from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
MAX_ITEMS = 7
MODEL_WITHOUT_TEMPERATURE_PREFIXES = ("gpt-5",)


@dataclass
class OpenAIRequestError(Exception):
    message: str
    status_code: int | None = None
    error_type: str | None = None
    error_param: str | None = None
    error_code: str | None = None

    def __str__(self) -> str:
        return self.message


def _seo_fallback(title: str, summary: str) -> dict[str, Any]:
    return {
        "success": False,
        "source": "fallback",
        "title": title,
        "summary": summary,
        "items": [],
        "priority": "medium",
        "debug": None,
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
        "debug": None,
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
    def _as_text(value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            if isinstance(value.get("value"), str):
                return str(value.get("value") or "").strip()
            if isinstance(value.get("text"), str):
                return str(value.get("text") or "").strip()
        if isinstance(value, list):
            chunks = [_as_text(item) for item in value]
            return "\n".join([chunk for chunk in chunks if chunk]).strip()
        return ""

    output_text = response_data.get("output_text")
    normalized_top_level_text = _as_text(output_text)
    if normalized_top_level_text:
        return normalized_top_level_text

    chunks: list[str] = []
    for item in response_data.get("output") or []:
        if not isinstance(item, dict):
            continue
        content = item.get("content") or []
        for part in content:
            if not isinstance(part, dict):
                continue
            part_text = _as_text(part.get("text"))
            if part_text:
                chunks.append(part_text)
    return "\n".join(chunks).strip()


def _build_result_from_text(*, module: str, text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    lines: list[str] = []
    for line in raw.splitlines():
        normalized_line = str(line or "").strip()
        if not normalized_line:
            continue
        normalized_line = re.sub(r"^[\s\-\*\u2022]+", "", normalized_line)
        lines.append(normalized_line)
    if not lines and raw:
        lines = [part.strip() for part in raw.split(".") if part.strip()]

    items: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        items.append(line[:260])
        if len(items) >= MAX_ITEMS:
            break

    title = "\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u043f\u043e \u0443\u043b\u0443\u0447\u0448\u0435\u043d\u0438\u044e"
    if module == "seo":
        title = "AI-\u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u043f\u043e SEO"
    elif module == "conversion":
        title = "AI-\u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u043f\u043e \u043f\u043e\u0432\u044b\u0448\u0435\u043d\u0438\u044e \u043a\u043e\u043d\u0432\u0435\u0440\u0441\u0438\u0438"

    summary = lines[0][:340] if lines else "\u041d\u0430\u0439\u0434\u0435\u043d\u044b \u0442\u043e\u0447\u043a\u0438 \u0440\u043e\u0441\u0442\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u0441\u0442\u043e\u0438\u0442 \u043f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u0432 \u043f\u0435\u0440\u0432\u0443\u044e \u043e\u0447\u0435\u0440\u0435\u0434\u044c."
    return {
        "success": True,
        "source": "ai",
        "title": title,
        "summary": summary,
        "items": items[:MAX_ITEMS],
        "priority": "medium",
        "debug": None,
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
        title = "AI-\u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438"
    if not summary:
        summary = "\u041d\u0430\u0439\u0434\u0435\u043d\u044b \u0437\u043e\u043d\u044b \u0440\u043e\u0441\u0442\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u043c\u043e\u0436\u043d\u043e \u0443\u043b\u0443\u0447\u0448\u0438\u0442\u044c \u0432 \u043f\u0435\u0440\u0432\u0443\u044e \u043e\u0447\u0435\u0440\u0435\u0434\u044c."
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
        "debug": None,
        "generated_at": timezone.now().isoformat(),
        "cached": False,
    }


def _request_openai(*, model: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    safe_model = str(model or "").strip()
    if not safe_model:
        raise OpenAIRequestError("Model name is empty.", error_type="configuration_error")

    max_output_tokens = int(getattr(settings, "AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", 900) or 900)
    body: dict[str, Any] = {
        "model": safe_model,
        "max_output_tokens": max_output_tokens,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    # GPT-5 models reject temperature and are more stable with low reasoning effort for concise JSON output.
    if safe_model.startswith(MODEL_WITHOUT_TEMPERATURE_PREFIXES):
        body["reasoning"] = {"effort": "minimal"}
        body["text"] = {"verbosity": "low"}
    else:
        body["temperature"] = 0.2

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

    if response.status_code >= 400:
        payload: dict[str, Any] = {}
        try:
            payload = response.json() or {}
        except Exception:
            payload = {}
        error_payload = payload.get("error") if isinstance(payload, dict) else {}
        if not isinstance(error_payload, dict):
            error_payload = {}

        message = str(error_payload.get("message") or f"OpenAI request failed with status {response.status_code}.")
        raise OpenAIRequestError(
            message=message,
            status_code=response.status_code,
            error_type=str(error_payload.get("type") or ""),
            error_param=str(error_payload.get("param") or ""),
            error_code=str(error_payload.get("code") or ""),
        )

    try:
        payload = response.json()
    except Exception as exc:
        raise OpenAIRequestError(f"Failed to parse OpenAI JSON: {exc}", status_code=response.status_code) from exc

    if not isinstance(payload, dict):
        raise OpenAIRequestError("OpenAI response is not a JSON object", status_code=response.status_code)
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
    enabled = bool(getattr(settings, "AI_RECOMMENDATIONS_ENABLED", False))
    has_key = bool(getattr(settings, "OPENAI_API_KEY", ""))
    timeout_seconds = float(getattr(settings, "AI_RECOMMENDATIONS_TIMEOUT_SECONDS", 20) or 20)

    if not _is_ai_enabled():
        logger.warning(
            "ai_recommendations disabled: module=%s enabled=%s has_key=%s",
            module,
            enabled,
            has_key,
        )
        return fallback_builder(
            "\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b",
            "AI-\u0430\u043d\u0430\u043b\u0438\u0437 \u043e\u0442\u043a\u043b\u044e\u0447\u0451\u043d \u0432 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u0445 \u043e\u043a\u0440\u0443\u0436\u0435\u043d\u0438\u044f \u0438\u043b\u0438 \u043d\u0435 \u0437\u0430\u0434\u0430\u043d API-\u043a\u043b\u044e\u0447.",
        )

    cache_key = _cache_key(module=module, model=model, scope=cache_scope, payload=payload_for_model)
    if not force_refresh:
        cached_payload = _cache_get_safe(cache_key)
        if cached_payload:
            cached_success = bool(cached_payload.get("success"))
            cached_source = str(cached_payload.get("source") or "").strip().lower()
            if cached_success and cached_source == "ai":
                cached_payload = dict(cached_payload)
                cached_payload["cached"] = True
                return cached_payload
            logger.info(
                "ai_recommendations skip stale cache: module=%s model=%s cached_success=%s cached_source=%s",
                module,
                model,
                cached_success,
                cached_source or "unknown",
            )

    payload_size = len(json.dumps(payload_for_model, ensure_ascii=False))
    logger.info(
        "ai_recommendations request start: module=%s model=%s timeout=%s payload_size=%s force_refresh=%s",
        module,
        model,
        timeout_seconds,
        payload_size,
        force_refresh,
    )

    user_prompt = (
        "Analyze the data below and return JSON only without markdown.\\n"
        'Format: {"title":"...","summary":"...","items":["..."],"priority":"high|medium|low"}\\n'
        "Requirements: 3-7 concrete actions, practical style, based only on provided data.\\n"
        "Important: response language must be Russian.\\n"
        f"Data:\\n{json.dumps(payload_for_model, ensure_ascii=False)}"
    )

    try:
        raw_response = _request_openai(model=model, system_prompt=system_prompt, user_prompt=user_prompt)
        output_text = _extract_output_text(raw_response)
        if not output_text:
            response_status = str(raw_response.get("status") or "").strip()
            incomplete_reason = ""
            incomplete_details = raw_response.get("incomplete_details")
            if isinstance(incomplete_details, dict):
                incomplete_reason = str(incomplete_details.get("reason") or "").strip()
            details = []
            if response_status:
                details.append(f"status={response_status}")
            if incomplete_reason:
                details.append(f"reason={incomplete_reason}")
            suffix = f" ({', '.join(details)})" if details else ""
            raise OpenAIRequestError(
                f"OpenAI output is empty{suffix}",
                error_type="empty_output",
                error_code=incomplete_reason or None,
            )

        result = _normalize_ai_payload(module=module, raw_text=output_text)
        _cache_set_safe(
            cache_key,
            result,
            ttl_seconds=int(getattr(settings, "AI_RECOMMENDATIONS_TTL_SECONDS", 10800) or 10800),
        )
        logger.info(
            "ai_recommendations request success: module=%s model=%s items=%s",
            module,
            model,
            len(result.get("items") or []),
        )
        return result
    except OpenAIRequestError as exc:
        logger.error(
            "ai_recommendations openai error: module=%s model=%s status=%s type=%s param=%s code=%s message=%s",
            module,
            model,
            exc.status_code,
            exc.error_type,
            exc.error_param,
            exc.error_code,
            exc.message,
        )
        return fallback_builder(
            "\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b",
            "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c AI-\u0430\u043d\u0430\u043b\u0438\u0437. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043e\u0431\u043d\u043e\u0432\u0438\u0442\u044c \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u043f\u043e\u0437\u0436\u0435.",
        )
    except Exception as exc:
        logger.exception(
            "ai_recommendations unexpected error: module=%s model=%s error=%s",
            module,
            model,
            exc,
        )
        return fallback_builder(
            "\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b",
            "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c AI-\u0430\u043d\u0430\u043b\u0438\u0437. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043e\u0431\u043d\u043e\u0432\u0438\u0442\u044c \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u043f\u043e\u0437\u0436\u0435.",
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
        "You are a senior SEO analyst. Analyze only provided SEO audit data. "
        "Do not invent facts and avoid generic theory. "
        "List the most critical issues first, then quick wins. "
        "Keep recommendations concise, practical, and in Russian."
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
        "You are a CRO and lead-generation expert. Analyze only user behavior analytics data. "
        "Find where users drop off and what actions can increase leads. "
        "Do not give SEO advice. Keep recommendations concise, practical, and in Russian."
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
