from __future__ import annotations

import hashlib
import json
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


def _cache_key(*, client_id: int, period_from: str, period_to: str, payload: dict) -> str:
    serialized = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"ai_advisor:{client_id}:{period_from}:{period_to}:{digest}"


def _fallback_recommendations(payload: dict) -> list[dict]:
    recommendations = []
    stale_leads = int(payload.get("stale_leads") or 0)
    avg_response_time = float(payload.get("avg_response_time") or 0.0)
    top_utm = payload.get("top_converting_utm") or []
    leads_by_source = payload.get("leads_by_source") or []

    if stale_leads > 0:
        recommendations.append(
            {
                "priority": "high",
                "category": "operations",
                "recommendation": f"Разберите {stale_leads} лидов без активности и назначьте следующую точку контакта.",
                "expected_impact": "Снижение потерь лидов на позднем этапе.",
            }
        )

    if avg_response_time > 1800:
        recommendations.append(
            {
                "priority": "high",
                "category": "speed_to_lead",
                "recommendation": "Сократите время первого ответа: включите автоответ и уведомления ответственного.",
                "expected_impact": "Рост конверсии в квалификацию за счет более быстрого контакта.",
            }
        )

    if top_utm:
        best = top_utm[0]
        recommendations.append(
            {
                "priority": "medium",
                "category": "acquisition",
                "recommendation": (
                    f"Увеличьте трафик из канала {best.get('source') or best.get('utm_source') or 'top source'} "
                    "и масштабируйте успешные связки оффера."
                ),
                "expected_impact": "Рост количества качественных лидов без увеличения CPL.",
            }
        )

    if leads_by_source:
        worst = sorted(leads_by_source, key=lambda item: float(item.get("conversion_pct") or 0))[:1]
        if worst:
            source = worst[0].get("source") or "unknown"
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "optimization",
                    "recommendation": f"Перепроверьте посадочные страницы и УТП для источника {source}.",
                    "expected_impact": "Выравнивание конверсии между каналами и снижение доли некачественного трафика.",
                }
            )

    if len(recommendations) < 3:
        recommendations.append(
            {
                "priority": "low",
                "category": "process",
                "recommendation": "Запустите еженедельный разбор воронки по стадиям и причинам отказов.",
                "expected_impact": "Стабильный рост управляемости CRM-процесса.",
            }
        )

    return recommendations[:5]


def _extract_output_text(raw: dict) -> str:
    text = str(raw.get("output_text") or "").strip()
    if text:
        return text
    output = raw.get("output")
    if not isinstance(output, list):
        return ""
    for item in output:
        if not isinstance(item, dict):
            continue
        for content in item.get("content") or []:
            if not isinstance(content, dict):
                continue
            value = content.get("text")
            if isinstance(value, dict):
                value = value.get("value")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _normalize_recommendations(value) -> list[dict]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "priority": str(item.get("priority") or "medium").strip().lower() or "medium",
                "category": str(item.get("category") or "general").strip().lower() or "general",
                "recommendation": str(item.get("recommendation") or "").strip()[:400],
                "expected_impact": str(item.get("expected_impact") or "").strip()[:300],
            }
        )
        if len(result) >= 5:
            break
    return [item for item in result if item["recommendation"]]


def generate_ai_advisor_recommendations(
    *,
    client_id: int,
    period_from: str,
    period_to: str,
    payload: dict,
    force_refresh: bool = False,
) -> dict:
    cache_ttl = int(getattr(settings, "AI_RECOMMENDATIONS_TTL_SECONDS", 1800) or 1800)
    key = _cache_key(client_id=client_id, period_from=period_from, period_to=period_to, payload=payload)
    if not force_refresh:
        cached = cache.get(key)
        if isinstance(cached, dict):
            return cached

    api_key = str(getattr(settings, "OPENAI_API_KEY", "") or "").strip()
    model = str(getattr(settings, "OPENAI_MODEL_CONVERSION", "gpt-5-mini") or "gpt-5-mini")
    enabled = bool(api_key) and str(getattr(settings, "AI_RECOMMENDATIONS_ENABLED", "false")).lower() == "true"

    if not enabled:
        result = {
            "success": True,
            "source": "local",
            "recommendations": _fallback_recommendations(payload),
        }
        cache.set(key, result, timeout=cache_ttl)
        return result

    prompt_payload = json.dumps(payload, ensure_ascii=False)
    request_body = {
        "model": model,
        "instructions": (
            "Ты senior CRO advisor для SaaS CRM. "
            "Верни только JSON формата "
            '{"recommendations":[{"priority":"high|medium|low","category":"...","recommendation":"...","expected_impact":"..."}]} '
            "на русском языке, без markdown."
        ),
        "input": f"Данные:\n{prompt_payload}",
        "max_output_tokens": int(getattr(settings, "AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", 900) or 900),
    }

    try:
        response = requests.post(
            OPENAI_RESPONSES_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=request_body,
            timeout=float(getattr(settings, "AI_RECOMMENDATIONS_TIMEOUT_SECONDS", 20) or 20),
        )
        response.raise_for_status()
        raw = response.json()
        output_text = _extract_output_text(raw)
        parsed = json.loads(output_text) if output_text else {}
        recommendations = _normalize_recommendations(parsed.get("recommendations"))
        if not recommendations:
            raise ValueError("empty recommendations")
        result = {
            "success": True,
            "source": "openai",
            "recommendations": recommendations[:5],
        }
        cache.set(key, result, timeout=cache_ttl)
        return result
    except Exception:
        logger.exception("AI advisor request failed, fallback to local recommendations")
        result = {
            "success": True,
            "source": "local_fallback",
            "recommendations": _fallback_recommendations(payload),
        }
        cache.set(key, result, timeout=cache_ttl)
        return result

