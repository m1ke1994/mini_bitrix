from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
MAX_ITEMS = 7


def _seo_fallback(title: str, summary: str) -> dict[str, Any]:
    return {
        "success": False,
        "source": "fallback",
        "title": title,
        "summary": summary,
        "items": [],
        "priority": "medium",
        "generated_at": timezone.now().isoformat(),
        "cached": False,
    }


def _conversion_fallback(title: str, summary: str) -> dict[str, Any]:
    return {
        "success": False,
        "source": "fallback",
        "title": title,
        "summary": summary,
        "items": [],
        "priority": "medium",
        "generated_at": timezone.now().isoformat(),
        "cached": False,
    }


def _cache_get_safe(cache_key: str) -> dict[str, Any] | None:
    try:
        value = cache.get(cache_key)
        if isinstance(value, dict):
            return value
    except Exception:
        logger.warning("ai_recommendations cache.get failed", exc_info=True)
    return None


def _cache_set_safe(cache_key: str, payload: dict[str, Any], ttl_seconds: int) -> None:
    try:
        cache.set(cache_key, payload, timeout=ttl_seconds)
    except Exception:
        logger.warning("ai_recommendations cache.set failed", exc_info=True)


def _normalize_priority(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"high", "medium", "low"}:
        return normalized
    return "medium"


def _normalize_items(items: Any) -> list[str]:
    if not isinstance(items, (list, tuple)):
        return []
    normalized: list[str] = []
    for item in items:
        text = str(item or "").strip()
        if not text:
            continue
        normalized.append(text[:260])
        if len(normalized) >= MAX_ITEMS:
            break
    return normalized


def _extract_json_candidate(text: str) -> str:
    candidate = str(text or "").strip()
    if not candidate:
        return ""
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s*```$", "", candidate)
    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate
    match = re.search(r"\{.*\}", candidate, flags=re.DOTALL)
    if match:
        return match.group(0)
    return candidate


def _extract_output_text(response_data: dict[str, Any]) -> str:
    output_text = response_data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    chunks: list[str] = []
    for item in response_data.get("output") or []:
        if not isinstance(item, dict):
            continue
        content = item.get("content") or []
        for part in content:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
    return "\n".join(chunks).strip()


def _build_result_from_text(*, module: str, text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    lines = [line.strip(" -*•\t") for line in raw.splitlines() if line.strip()]
    if not lines and raw:
        lines = [part.strip() for part in raw.split(".") if part.strip()]

    items: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        items.append(line[:260])
        if len(items) >= MAX_ITEMS:
            break

    title = "Рекомендации по улучшению"
    if module == "seo":
        title = "AI-рекомендации по SEO"
    elif module == "conversion":
        title = "AI-рекомендации по повышению конверсии"

    summary = lines[0][:340] if lines else "Найдены точки роста, которые стоит проверить в первую очередь."
    return {
        "success": True,
        "source": "ai",
        "title": title,
        "summary": summary,
        "items": items[:MAX_ITEMS],
        "priority": "medium",
        "generated_at": timezone.now().isoformat(),
        "cached": False,
    }


def _normalize_ai_payload(*, module: str, raw_text: str) -> dict[str, Any]:
    candidate = _extract_json_candidate(raw_text)
    parsed: dict[str, Any] | None = None
    try:
        maybe = json.loads(candidate)
        if isinstance(maybe, dict):
            parsed = maybe
    except Exception:
        parsed = None

    if not parsed:
        return _build_result_from_text(module=module, text=raw_text)

    title = str(parsed.get("title") or "").strip()
    summary = str(parsed.get("summary") or "").strip()
    items = _normalize_items(parsed.get("items"))
    priority = _normalize_priority(parsed.get("priority"))

    if not title:
        title = "AI-рекомендации"
    if not summary:
        summary = "Найдены зоны роста, которые можно улучшить в первую очередь."
    if not items:
        fallback = _build_result_from_text(module=module, text=summary)
        items = fallback.get("items") or []

    return {
        "success": True,
        "source": "ai",
        "title": title[:160],
        "summary": summary[:520],
        "items": items[:MAX_ITEMS],
        "priority": priority,
        "generated_at": timezone.now().isoformat(),
        "cached": False,
    }


def _request_openai(*, model: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    body = {
        "model": model,
        "temperature": 0.2,
        "max_output_tokens": 500,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    timeout_seconds = float(getattr(settings, "AI_RECOMMENDATIONS_TIMEOUT_SECONDS", 20) or 20)
    response = requests.post(
        OPENAI_RESPONSES_URL,
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("OpenAI response is not a JSON object")
    return payload


def _cache_key(*, module: str, model: str, scope: str, payload: dict[str, Any]) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    return f"tracknode:ai-recommendations:{module}:{model}:{scope}:{digest}"


def _is_ai_enabled() -> bool:
    return bool(getattr(settings, "AI_RECOMMENDATIONS_ENABLED", False) and getattr(settings, "OPENAI_API_KEY", ""))


def _seo_prompt_payload(detail_payload: dict[str, Any]) -> dict[str, Any]:
    issue_groups = detail_payload.get("issue_groups") or []
    errors = detail_payload.get("errors") or []
    top_issues: list[dict[str, Any]] = []

    severity_order = {"high": 0, "medium": 1, "low": 2}
    sorted_groups = sorted(
        [group for group in issue_groups if isinstance(group, dict)],
        key=lambda group: (
            severity_order.get(str(group.get("severity") or "").lower(), 3),
            -int(group.get("pages_affected") or 0),
        ),
    )

    for group in sorted_groups[:10]:
        top_issues.append(
            {
                "issue_type": group.get("issue_type"),
                "title": group.get("title"),
                "severity": group.get("severity"),
                "pages_affected": int(group.get("pages_affected") or 0),
                "description": group.get("description"),
            }
        )

    def has_issue(issue_type: str) -> bool:
        return any(str(item.get("issue_type") or "").strip().lower() == issue_type for item in errors if isinstance(item, dict))

    breakdown = detail_payload.get("breakdown") or {}
    return {
        "domain": detail_payload.get("domain"),
        "seo_score": int(detail_payload.get("score") or detail_payload.get("seo_score") or 0),
        "critical_issues_count": int(breakdown.get("high_issues") or 0),
        "warning_issues_count": int(breakdown.get("medium_issues") or 0),
        "low_issues_count": int(breakdown.get("low_issues") or 0),
        "pages_count": int(detail_payload.get("pages_count") or 0),
        "title_status": "issues" if has_issue("missing_title") else "ok",
        "description_status": "issues" if has_issue("missing_description") else "ok",
        "h1_status": "issues" if has_issue("missing_h1") else "ok",
        "canonical_status": "issues" if has_issue("missing_canonical") else "ok",
        "robots_status": "ok" if detail_payload.get("has_robots_txt") else "missing",
        "indexing_status": "issues" if int(detail_payload.get("pages_with_indexing_issues") or 0) > 0 else "ok",
        "page_speed_status": "issues" if int(detail_payload.get("pages_with_speed_issues") or 0) > 0 else "ok",
        "content_length_status": "issues"
        if any(has_issue(name) for name in ("thin_content", "too_short_content", "low_word_count"))
        else "ok",
        "image_alt_status": "issues"
        if any(has_issue(name) for name in ("missing_alt", "missing_image_alt"))
        else "ok",
        "internal_links_status": "issues" if has_issue("low_internal_links") else "ok",
        "avg_ttfb_ms": int(detail_payload.get("avg_ttfb_ms") or 0),
        "avg_performance_score": int(detail_payload.get("avg_performance_score") or 0),
        "top_issues": top_issues,
    }


def _weakest_funnel_step(rows: list[dict[str, Any]]) -> str | None:
    if not rows:
        return None
    candidates: list[tuple[float, str]] = []
    for row in rows:
        stage = str(row.get("stage") or "").strip()
        if not stage:
            continue
        rate = float(row.get("next_step_rate_pct") or 0.0)
        candidates.append((rate, stage))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def _conversion_prompt_payload(summary_payload: dict[str, Any]) -> dict[str, Any]:
    ai_signals = summary_payload.get("ai_event_signals") or {}
    overview = ai_signals.get("overview") or {}
    scroll = ai_signals.get("scroll_depth") or {}
    funnel_rows = (ai_signals.get("form_funnel") or {}).get("rows") or []
    cta_rows = (ai_signals.get("cta_funnel") or {}).get("rows") or []
    field_rows = (ai_signals.get("field_analytics") or {}).get("rows") or []
    section_rows = (ai_signals.get("section_analytics") or {}).get("rows") or []
    source_rows = (ai_signals.get("source_segmentation") or {}).get("rows") or []
    device_rows = (ai_signals.get("device_segmentation") or {}).get("rows") or []
    micro_rows = (ai_signals.get("micro_conversions") or {}).get("rows") or []
    anomaly_rows = (ai_signals.get("anomalies") or {}).get("rows") or []

    sorted_cta_rows = sorted(
        [row for row in cta_rows if isinstance(row, dict)],
        key=lambda row: int(row.get("clicks") or 0),
        reverse=True,
    )[:5]
    sorted_field_rows = sorted(
        [row for row in field_rows if isinstance(row, dict)],
        key=lambda row: (int(row.get("drop_off") or 0), int(row.get("errors") or 0)),
        reverse=True,
    )[:5]
    best_sections = sorted(
        [row for row in section_rows if isinstance(row, dict)],
        key=lambda row: int(row.get("conversions_after_section") or 0),
        reverse=True,
    )[:3]
    weak_sections = sorted(
        [row for row in section_rows if isinstance(row, dict)],
        key=lambda row: float(row.get("exit_after_section_rate_pct") or 0.0),
        reverse=True,
    )[:3]

    return {
        "unique_users": int(overview.get("unique_users_total") or summary_payload.get("visitors_unique") or 0),
        "avg_scroll_depth": float(overview.get("avg_scroll_depth") or scroll.get("avg_scroll_depth") or 0.0),
        "form_start_count": int(overview.get("form_started_users") or 0),
        "form_submit_success_count": int(overview.get("form_submit_success_users") or 0),
        "important_button_clicks": int(overview.get("cta_click_users") or 0),
        "useful_actions_count": int(overview.get("micro_conversion_users") or 0),
        "funnel_steps": [
            {
                "stage": row.get("stage"),
                "users": int(row.get("users") or 0),
                "next_step_rate_pct": float(row.get("next_step_rate_pct") or 0.0),
            }
            for row in funnel_rows
            if isinstance(row, dict)
        ],
        "weakest_funnel_step": _weakest_funnel_step([row for row in funnel_rows if isinstance(row, dict)]),
        "top_button_stats": [
            {
                "cta_id": row.get("cta_id"),
                "cta_text": row.get("cta_text"),
                "clicks": int(row.get("clicks") or 0),
                "ctr_pct": float(row.get("ctr_pct") or 0.0),
                "click_to_conversion_rate_pct": float(row.get("click_to_conversion_rate_pct") or 0.0),
            }
            for row in sorted_cta_rows
        ],
        "worst_form_fields": [
            {
                "field": row.get("field_name") or row.get("field_key"),
                "drop_off": int(row.get("drop_off") or 0),
                "errors": int(row.get("errors") or 0),
                "completion_rate_pct": float(row.get("completion_rate_pct") or 0.0),
            }
            for row in sorted_field_rows
        ],
        "best_sections": [
            {
                "section": row.get("section_name") or row.get("section_id"),
                "views": int(row.get("views") or 0),
                "conversions_after_section": int(row.get("conversions_after_section") or 0),
            }
            for row in best_sections
        ],
        "weak_sections": [
            {
                "section": row.get("section_name") or row.get("section_id"),
                "views": int(row.get("views") or 0),
                "exit_after_section_rate_pct": float(row.get("exit_after_section_rate_pct") or 0.0),
            }
            for row in weak_sections
        ],
        "traffic_source_breakdown": [
            {
                "source": row.get("source"),
                "users": int(row.get("users") or 0),
                "users_share_pct": float(row.get("users_share_pct") or 0.0),
                "conversion_rate_pct": float(row.get("conversion_rate_pct") or 0.0),
            }
            for row in source_rows
            if isinstance(row, dict)
        ][:7],
        "device_breakdown": [
            {
                "device": row.get("device"),
                "users": int(row.get("users") or 0),
                "users_share_pct": float(row.get("users_share_pct") or 0.0),
                "form_conversion_rate_pct": float(row.get("form_conversion_rate_pct") or 0.0),
            }
            for row in device_rows
            if isinstance(row, dict)
        ][:7],
        "key_changes_vs_previous_period": [
            {
                "metric": row.get("metric"),
                "label": row.get("label"),
                "change_pct": float(row.get("change_pct") or 0.0),
                "status": row.get("status"),
            }
            for row in anomaly_rows
            if isinstance(row, dict)
        ][:6],
        "micro_actions": [
            {
                "event": row.get("event"),
                "label": row.get("label"),
                "count": int(row.get("count") or 0),
                "unique_users": int(row.get("unique_users") or 0),
            }
            for row in micro_rows
            if isinstance(row, dict)
        ][:10],
    }


def _generate_recommendations(
    *,
    module: str,
    model: str,
    cache_scope: str,
    payload_for_model: dict[str, Any],
    system_prompt: str,
    fallback_builder,
    force_refresh: bool,
) -> dict[str, Any]:
    if not _is_ai_enabled():
        return fallback_builder(
            "Рекомендации временно недоступны",
            "AI-анализ отключён в настройках окружения или не задан API-ключ.",
        )

    cache_key = _cache_key(module=module, model=model, scope=cache_scope, payload=payload_for_model)
    if not force_refresh:
        cached_payload = _cache_get_safe(cache_key)
        if cached_payload:
            cached_payload = dict(cached_payload)
            cached_payload["cached"] = True
            return cached_payload

    user_prompt = (
        "Проанализируй данные ниже и верни только JSON без markdown.\n"
        'Формат: {"title":"...","summary":"...","items":["..."],"priority":"high|medium|low"}\n'
        "Требования: 3-7 конкретных действий, деловой стиль, только на основе переданных данных.\n"
        f"Данные:\n{json.dumps(payload_for_model, ensure_ascii=False)}"
    )

    try:
        raw_response = _request_openai(model=model, system_prompt=system_prompt, user_prompt=user_prompt)
        output_text = _extract_output_text(raw_response)
        if not output_text:
            raise ValueError("OpenAI output is empty")
        result = _normalize_ai_payload(module=module, raw_text=output_text)
        _cache_set_safe(
            cache_key,
            result,
            ttl_seconds=int(getattr(settings, "AI_RECOMMENDATIONS_TTL_SECONDS", 10800) or 10800),
        )
        return result
    except Exception:
        logger.exception("ai_recommendations request failed: module=%s model=%s", module, model)
        return fallback_builder(
            "Рекомендации временно недоступны",
            "Не удалось получить AI-анализ. Попробуйте обновить рекомендации позже.",
        )


def get_seo_ai_recommendations(
    *,
    client_id: int,
    audit_id: int,
    audit_payload: dict[str, Any],
    force_refresh: bool = False,
) -> dict[str, Any]:
    seo_payload = _seo_prompt_payload(audit_payload)
    cache_scope = f"client:{client_id}:audit:{audit_id}"
    model = str(getattr(settings, "OPENAI_MODEL_SEO", "gpt-5-mini") or "gpt-5-mini")
    system_prompt = (
        "Ты SEO-аналитик. Анализируй только переданные данные SEO-аудита. "
        "Не придумывай факты и не давай общую теорию. "
        "Сначала перечисли критичные проблемы, потом быстрые улучшения. "
        "Рекомендации должны быть короткими, прикладными, на русском языке и полезными владельцу бизнеса."
    )
    return _generate_recommendations(
        module="seo",
        model=model,
        cache_scope=cache_scope,
        payload_for_model=seo_payload,
        system_prompt=system_prompt,
        fallback_builder=_seo_fallback,
        force_refresh=force_refresh,
    )


def get_conversion_ai_recommendations(
    *,
    client_id: int,
    period_from: datetime | str | None,
    period_to: datetime | str | None,
    summary_payload: dict[str, Any],
    force_refresh: bool = False,
) -> dict[str, Any]:
    conversion_payload = _conversion_prompt_payload(summary_payload)
    from_label = str(period_from or "")
    to_label = str(period_to or "")
    cache_scope = f"client:{client_id}:from:{from_label}:to:{to_label}"
    model = str(getattr(settings, "OPENAI_MODEL_CONVERSION", "gpt-5-mini") or "gpt-5-mini")
    system_prompt = (
        "Ты эксперт по CRO и лидогенерации. Анализируй только поведенческие данные пользователей на сайте. "
        "Определи, где теряется конверсия и какие действия повысят количество заявок. "
        "Не давай SEO-рекомендации. "
        "Отвечай на русском языке коротко и прикладно."
    )
    return _generate_recommendations(
        module="conversion",
        model=model,
        cache_scope=cache_scope,
        payload_for_model=conversion_payload,
        system_prompt=system_prompt,
        fallback_builder=_conversion_fallback,
        force_refresh=force_refresh,
    )
