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
MAX_HIGHLIGHTS = 5
MAX_METRICS_REVIEW = 8
MAX_PROBLEMS = 8
MAX_FIX_PLAN = 7
MAX_OUTPUT_DIAGNOSTIC_ITEMS = 12
MAX_TEXT_DIAGNOSTIC_PATHS = 20
MAX_LOG_TEXT_PREVIEW = 200


@dataclass
class OpenAIRequestError(Exception):
    message: str
    status_code: int | None = None
    error_type: str | None = None
    error_param: str | None = None
    error_code: str | None = None
    request_id: str | None = None
    response_status: str | None = None
    incomplete_details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


@dataclass
class OutputTextExtraction:
    text: str
    path: str
    candidate_paths: list[str]


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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0.0)
    except Exception:
        return default


def _safe_int_setting(name: str, default: int) -> int:
    try:
        return int(getattr(settings, name, default) or default)
    except Exception:
        return default


def _resolve_max_output_tokens(module: str) -> int:
    fallback = _safe_int_setting("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", 900)
    module_key = str(module or "").strip().lower()
    if module_key == "seo":
        return max(256, _safe_int_setting("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_SEO", max(fallback, 2200)))
    if module_key == "conversion":
        return max(
            256,
            _safe_int_setting("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_CONVERSION", fallback),
        )
    return max(256, fallback)


def _resolve_retry_max_output_tokens(module: str, base_tokens: int) -> int:
    base = max(256, int(base_tokens or 0))
    default_cap = 3200 if str(module or "").strip().lower() == "seo" else 2000
    retry_cap = max(base, _safe_int_setting("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_RETRY_CAP", default_cap))
    retry_candidate = max(base + 300, int(base * 1.5))
    return min(retry_candidate, retry_cap)


def _truncate_for_log(value: Any, *, limit: int = MAX_LOG_TEXT_PREVIEW) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


def _normalize_text_list(value: Any, *, max_items: int, max_len: int = 260) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    items: list[str] = []
    for raw in value:
        text = str(raw or "").strip()
        if not text:
            continue
        items.append(text[:max_len])
        if len(items) >= max_items:
            break
    return items


def _normalize_metric_status(value: Any) -> str:
    key = str(value or "").strip().lower()
    if key in {"good", "warning", "bad", "info"}:
        return key
    return "info"


def _severity_key(value: Any) -> str:
    key = str(value or "").strip().lower()
    if key in {"high", "medium", "low"}:
        return key
    return "medium"


def _severity_label(value: Any) -> str:
    key = _severity_key(value)
    if key == "high":
        return "критичная"
    if key == "low":
        return "низкая"
    return "средняя"


def _metric_row(*, label: str, value: str, status: str, comment: str) -> dict[str, str]:
    return {
        "label": str(label).strip()[:120],
        "value": str(value).strip()[:120],
        "status": _normalize_metric_status(status),
        "comment": str(comment).strip()[:260],
    }


def _build_seo_default_overview(payload: dict[str, Any]) -> dict[str, str]:
    score = _safe_int(payload.get("seo_score"))
    pages_count = _safe_int(payload.get("pages_count"))
    critical = _safe_int(payload.get("critical_issues_count"))
    warning = _safe_int(payload.get("warning_issues_count"))
    low = _safe_int(payload.get("low_issues_count"))
    page_speed_status = str(payload.get("page_speed_status") or "").strip().lower()
    indexing_status = str(payload.get("indexing_status") or "").strip().lower()
    robots_status = str(payload.get("robots_status") or "").strip().lower()
    sitemap_status = str(payload.get("sitemap_status") or "").strip().lower()

    if score >= 80:
        score_label = "хорошо"
    elif score >= 60:
        score_label = "есть точки роста"
    else:
        score_label = "требует доработки"

    if pages_count >= 10:
        pages_label = "достаточно данных"
    elif pages_count >= 3:
        pages_label = "данных достаточно для базового вывода"
    else:
        pages_label = "данных пока мало"

    if critical > 0:
        errors_label = "есть критичные ошибки"
    elif warning + low > 0:
        errors_label = "есть предупреждения и ошибки"
    else:
        errors_label = "критичных ошибок не найдено"

    if page_speed_status == "issues":
        speed_label = "ниже нормы"
    else:
        speed_label = "в пределах нормы"

    indexing_is_ok = indexing_status == "ok" and robots_status == "ok" and sitemap_status == "ok"
    if indexing_is_ok:
        indexing_label = "в целом нормально"
    elif indexing_status == "issues":
        indexing_label = "есть риски индексации"
    else:
        indexing_label = "нужна дополнительная проверка"

    return {
        "seo_score_label": score_label,
        "pages_checked_label": pages_label,
        "errors_label": errors_label,
        "speed_label": speed_label,
        "indexing_label": indexing_label,
    }


def _build_seo_default_highlights(payload: dict[str, Any]) -> list[str]:
    score = _safe_int(payload.get("seo_score"))
    critical = _safe_int(payload.get("critical_issues_count"))
    warning = _safe_int(payload.get("warning_issues_count"))
    top_issues = payload.get("top_issues") or []
    issue_titles: list[str] = []
    for item in top_issues:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("issue_type") or "").strip()
        if title:
            issue_titles.append(title)
        if len(issue_titles) >= 2:
            break

    highlights: list[str] = []
    if critical > 0:
        highlights.append(f"Найдены критичные ошибки: {critical}. Их нужно закрыть в первую очередь.")
    elif warning > 0:
        highlights.append("Критичных проблем нет, но есть предупреждения, влияющие на рост SEO.")
    else:
        highlights.append("Критичных проблем не обнаружено, можно работать над точками роста.")

    if issue_titles:
        highlights.append(f"Основные зоны внимания: {', '.join(issue_titles)}.")

    if score >= 80:
        highlights.append("Общий SEO-уровень хороший, но остаются задачи для дальнейшего роста.")
    elif score >= 60:
        highlights.append("SEO в рабочем состоянии, но есть заметные резервы для улучшения.")
    else:
        highlights.append("Текущее SEO-состояние требует приоритетных доработок.")
    return highlights[:MAX_HIGHLIGHTS]


def _build_seo_default_metrics_review(payload: dict[str, Any]) -> list[dict[str, str]]:
    score = _safe_int(payload.get("seo_score"))
    pages_count = _safe_int(payload.get("pages_count"))
    critical = _safe_int(payload.get("critical_issues_count"))
    warning = _safe_int(payload.get("warning_issues_count"))
    low = _safe_int(payload.get("low_issues_count"))
    ttfb = _safe_int(payload.get("avg_ttfb_ms"))
    robots_status = str(payload.get("robots_status") or "").strip().lower()
    sitemap_status = str(payload.get("sitemap_status") or "").strip().lower()

    if score >= 80:
        score_status, score_comment = "good", "Общий уровень хороший, но остаются точки роста."
    elif score >= 60:
        score_status, score_comment = "warning", "Уровень средний: нужно закрыть ключевые проблемы."
    else:
        score_status, score_comment = "bad", "Низкий уровень: начните с критичных технических ошибок."

    if pages_count >= 10:
        pages_comment = "Данных достаточно для уверенных выводов."
    elif pages_count >= 3:
        pages_comment = "Данных достаточно для базового анализа."
    else:
        pages_comment = "Пока мало данных, выводы предварительные."

    total_errors = critical + warning + low
    if critical > 0:
        errors_status, errors_comment = "bad", "Есть критичные ошибки, влияющие на SEO-трафик."
    elif warning + low > 0:
        errors_status, errors_comment = "warning", "Есть ошибки и предупреждения, их стоит закрыть планово."
    else:
        errors_status, errors_comment = "good", "Существенных ошибок не обнаружено."

    if ttfb <= 0:
        ttfb_value, ttfb_status, ttfb_comment = "нет данных", "info", "Недостаточно данных для оценки отклика."
    elif ttfb <= 450:
        ttfb_value, ttfb_status, ttfb_comment = f"{ttfb} мс", "good", "Отклик сервера в хорошем диапазоне."
    elif ttfb <= 800:
        ttfb_value, ttfb_status, ttfb_comment = f"{ttfb} мс", "warning", "Отклик приемлемый, но можно ускорить."
    else:
        ttfb_value, ttfb_status, ttfb_comment = f"{ttfb} мс", "bad", "Отклик высокий, это может вредить SEO и UX."

    robots_value = "Найден" if robots_status == "ok" else "Не найден"
    sitemap_value = "Найден" if sitemap_status == "ok" else "Не найден"

    return [
        _metric_row(label="SEO-оценка", value=str(score), status=score_status, comment=score_comment),
        _metric_row(label="Страниц проверено", value=str(pages_count), status="info", comment=pages_comment),
        _metric_row(label="Всего ошибок", value=str(total_errors), status=errors_status, comment=errors_comment),
        _metric_row(label="Средний отклик", value=ttfb_value, status=ttfb_status, comment=ttfb_comment),
        _metric_row(
            label="robots.txt",
            value=robots_value,
            status="good" if robots_status == "ok" else "bad",
            comment="Файл robots.txt помогает корректному обходу сайта поисковыми системами.",
        ),
        _metric_row(
            label="sitemap.xml",
            value=sitemap_value,
            status="good" if sitemap_status == "ok" else "warning",
            comment="Карта сайта упрощает индексацию важных страниц.",
        ),
    ][:MAX_METRICS_REVIEW]


def _default_recommendation_for_issue(issue_type: str, title: str) -> str:
    issue_key = str(issue_type or "").strip().lower()
    mapping = {
        "missing_title": "Добавьте уникальные title на приоритетные страницы с коммерческим трафиком.",
        "missing_description": "Заполните meta description с понятным оффером и релевантными ключевыми фразами.",
        "missing_h1": "Добавьте уникальный H1, отражающий основной поисковый интент страницы.",
        "missing_canonical": "Укажите canonical на страницах с риском дублей, чтобы консолидировать индекс.",
        "low_word_count": "Усилите контент: добавьте полезные блоки и ответы на вопросы пользователя.",
        "thin_content": "Расширьте слабый контент, чтобы покрыть интент и повысить релевантность страницы.",
        "missing_alt": "Добавьте alt-теги к изображениям с коротким описанием содержания.",
        "slow_ttfb": "Проверьте серверный отклик и настройте кеширование/CDN для снижения задержки.",
        "slow_response": "Оптимизируйте ресурсы страницы и устраните тяжёлые скрипты для ускорения загрузки.",
    }
    if issue_key in mapping:
        return mapping[issue_key]
    if title:
        return f"Разберите проблему «{title}» и исправьте её сначала на ключевых посадочных страницах."
    return "Закройте эту проблему на ключевых страницах и перепроверьте аудит после правок."


def _build_seo_default_problems(payload: dict[str, Any]) -> list[dict[str, str]]:
    top_issues = payload.get("top_issues") or []
    problems: list[dict[str, str]] = []
    for item in top_issues:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("issue_type") or "SEO-проблема").strip()
        severity = _severity_key(item.get("severity"))
        pages = _safe_int(item.get("pages_affected"))
        description = str(item.get("description") or "").strip()
        if pages > 0:
            pages_text = f" Затронуто страниц: {pages}."
        else:
            pages_text = ""
        if not description:
            description = f"Нужно устранить эту проблему на приоритетных страницах.{pages_text}"
        else:
            description = f"{description[:220]}{pages_text}"
        problems.append({"title": title[:140], "severity": severity, "description": description[:260]})
        if len(problems) >= MAX_PROBLEMS:
            break

    if problems:
        return problems

    generated: list[dict[str, str]] = []
    status_checks = [
        ("title_status", "Проблемы с title"),
        ("description_status", "Проблемы с description"),
        ("h1_status", "Проблемы с H1"),
        ("canonical_status", "Проблемы с canonical"),
        ("indexing_status", "Риски индексации"),
        ("page_speed_status", "Проблемы скорости страниц"),
        ("content_length_status", "Слабый контент"),
        ("image_alt_status", "Отсутствуют alt у изображений"),
        ("internal_links_status", "Слабая внутренняя перелинковка"),
    ]
    for key, title in status_checks:
        if str(payload.get(key) or "").strip().lower() != "issues":
            continue
        generated.append(
            {
                "title": title,
                "severity": "medium",
                "description": "Эта зона требует доработки для стабильного роста видимости и трафика.",
            }
        )
        if len(generated) >= MAX_PROBLEMS:
            break
    return generated


def _build_seo_default_fix_plan(problems: list[dict[str, str]]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for idx, problem in enumerate(problems[:MAX_FIX_PLAN], start=1):
        title = str(problem.get("title") or "SEO-задача").strip()
        severity = _severity_key(problem.get("severity"))
        if severity == "high":
            details = "Сделайте это в первую очередь на страницах с ключевым трафиком и конверсиями."
        elif severity == "medium":
            details = "Выполните после критичных проблем и проверьте изменения повторным аудитом."
        else:
            details = "Запланируйте как доработку качества после закрытия основных рисков."
        steps.append({"step": idx, "title": title[:140], "details": details})
    return steps


def _build_seo_default_recommendations(payload: dict[str, Any], problems: list[dict[str, str]]) -> list[str]:
    top_issues = payload.get("top_issues") or []
    recommendations: list[str] = []
    for item in top_issues:
        if not isinstance(item, dict):
            continue
        issue_type = str(item.get("issue_type") or "").strip().lower()
        title = str(item.get("title") or "").strip()
        recommendation = _default_recommendation_for_issue(issue_type, title)
        if recommendation and recommendation not in recommendations:
            recommendations.append(recommendation)
        if len(recommendations) >= MAX_ITEMS:
            break

    if not recommendations:
        for problem in problems:
            title = str(problem.get("title") or "").strip()
            recommendation = _default_recommendation_for_issue("", title)
            if recommendation and recommendation not in recommendations:
                recommendations.append(recommendation)
            if len(recommendations) >= MAX_ITEMS:
                break

    if not recommendations:
        recommendations = [
            "Закройте критичные ошибки и перепроверьте SEO-аудит после внедрения правок.",
            "Усилите мета-теги и контент на страницах с приоритетным трафиком.",
            "Оптимизируйте скорость и индексацию, чтобы закрепить рост видимости в поиске.",
        ]
    return recommendations[:MAX_ITEMS]


def _normalize_metrics_review(items: Any, default_items: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(items, (list, tuple)):
        return default_items
    result: list[dict[str, str]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        label = str(raw.get("label") or "").strip()
        value = str(raw.get("value") or "").strip()
        comment = str(raw.get("comment") or "").strip()
        if not (label and value):
            continue
        result.append(
            _metric_row(
                label=label,
                value=value,
                status=_normalize_metric_status(raw.get("status")),
                comment=comment or "Показатель учтён в общей оценке.",
            )
        )
        if len(result) >= MAX_METRICS_REVIEW:
            break
    return result or default_items


def _normalize_problems(items: Any, default_items: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(items, (list, tuple)):
        return default_items
    result: list[dict[str, str]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or "").strip()
        if not title:
            continue
        result.append(
            {
                "title": title[:140],
                "severity": _severity_key(raw.get("severity")),
                "description": str(raw.get("description") or "Проблема требует проверки и исправления.").strip()[:260],
            }
        )
        if len(result) >= MAX_PROBLEMS:
            break
    return result or default_items


def _normalize_fix_plan(items: Any, default_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(items, (list, tuple)):
        return default_items
    result: list[dict[str, Any]] = []
    for idx, raw in enumerate(items, start=1):
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or "").strip()
        details = str(raw.get("details") or "").strip()
        if not title:
            continue
        step = _safe_int(raw.get("step"), idx)
        if step <= 0:
            step = idx
        result.append(
            {
                "step": step,
                "title": title[:140],
                "details": (details or "Выполните этот шаг и перепроверьте результат аудитом.")[:260],
            }
        )
        if len(result) >= MAX_FIX_PLAN:
            break
    return result or default_items


def _normalize_overview(items: Any, default_item: dict[str, str]) -> dict[str, str]:
    if not isinstance(items, dict):
        return default_item
    result = dict(default_item)
    for key in ("seo_score_label", "pages_checked_label", "errors_label", "speed_label", "indexing_label"):
        value = str(items.get(key) or "").strip()
        if value:
            result[key] = value[:140]
    return result


def _build_seo_structured_result(
    *,
    parsed: dict[str, Any] | None,
    payload_for_model: dict[str, Any],
    fallback_text: str,
) -> dict[str, Any]:
    parsed = parsed or {}
    title = str(parsed.get("title") or "").strip() or "AI-рекомендации по SEO"
    summary = str(parsed.get("summary") or "").strip()
    priority = _normalize_priority(parsed.get("priority"))

    default_overview = _build_seo_default_overview(payload_for_model)
    default_highlights = _build_seo_default_highlights(payload_for_model)
    default_metrics = _build_seo_default_metrics_review(payload_for_model)
    default_problems = _build_seo_default_problems(payload_for_model)
    default_fix_plan = _build_seo_default_fix_plan(default_problems)
    default_recommendations = _build_seo_default_recommendations(payload_for_model, default_problems)

    overview = _normalize_overview(parsed.get("overview"), default_overview)
    highlights = _normalize_text_list(parsed.get("highlights"), max_items=MAX_HIGHLIGHTS, max_len=220) or default_highlights
    metrics_review = _normalize_metrics_review(parsed.get("metrics_review"), default_metrics)
    problems = _normalize_problems(parsed.get("problems"), default_problems)
    fix_plan = _normalize_fix_plan(parsed.get("fix_plan"), default_fix_plan)

    recommendations = _normalize_text_list(parsed.get("recommendations"), max_items=MAX_ITEMS, max_len=300)
    parsed_items = _normalize_items(parsed.get("items"))
    if not recommendations and parsed_items:
        recommendations = parsed_items
    if not recommendations:
        recommendations = default_recommendations

    if not summary:
        fallback_result = _build_result_from_text(module="seo", text=fallback_text)
        summary = str(fallback_result.get("summary") or "").strip() or (
            "Есть точки роста по техническому SEO. Начните с критичных проблем и приоритетных страниц."
        )

    return {
        "success": True,
        "source": "ai",
        "fallback": False,
        "title": title[:160],
        "summary": summary[:520],
        "priority": priority,
        "overview": overview,
        "highlights": highlights[:MAX_HIGHLIGHTS],
        "metrics_review": metrics_review[:MAX_METRICS_REVIEW],
        "problems": problems[:MAX_PROBLEMS],
        "fix_plan": fix_plan[:MAX_FIX_PLAN],
        "recommendations": recommendations[:MAX_ITEMS],
        # backward compatibility for existing UI/composables
        "items": recommendations[:MAX_ITEMS],
        "debug": None,
        "generated_at": timezone.now().isoformat(),
        "cached": False,
    }


def _decode_json_string(raw: str) -> str:
    text = str(raw or "")
    if not text:
        return ""
    try:
        return json.loads(f'"{text}"')
    except Exception:
        return text.replace('\\"', '"').replace("\\n", "\n").strip()


def _extract_json_like_payload(text: str) -> dict[str, Any] | None:
    raw = str(text or "").strip()
    if not raw:
        return None

    title_match = re.search(r'"title"\s*:\s*"((?:\\.|[^"\\])*)"', raw, flags=re.DOTALL)
    summary_match = re.search(r'"summary"\s*:\s*"((?:\\.|[^"\\])*)"', raw, flags=re.DOTALL)
    priority_match = re.search(r'"priority"\s*:\s*"((?:\\.|[^"\\])*)"', raw, flags=re.DOTALL)
    items_match = re.search(r'"items"\s*:\s*\[(.*?)\]', raw, flags=re.DOTALL)

    if not any([title_match, summary_match, priority_match, items_match]):
        return None

    items: list[str] = []
    if items_match:
        items_block = str(items_match.group(1) or "")
        item_matches = re.findall(r'"((?:\\.|[^"\\])*)"', items_block, flags=re.DOTALL)
        for chunk in item_matches:
            decoded = _decode_json_string(chunk).strip()
            if decoded:
                items.append(decoded)
            if len(items) >= MAX_ITEMS:
                break

    payload: dict[str, Any] = {}
    if title_match:
        payload["title"] = _decode_json_string(title_match.group(1)).strip()
    if summary_match:
        payload["summary"] = _decode_json_string(summary_match.group(1)).strip()
    if priority_match:
        payload["priority"] = _decode_json_string(priority_match.group(1)).strip().lower()
    if items:
        payload["items"] = items

    return payload


def _extract_json_candidate(text: str) -> str:
    candidate = str(text or "").strip()
    if not candidate:
        return ""

    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s*```$", "", candidate)

    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate

    balanced = _extract_first_balanced_json_object(candidate)
    if balanced:
        return balanced

    return candidate


def _extract_first_balanced_json_object(text: str) -> str:
    raw = str(text or "")
    if not raw:
        return ""

    start = raw.find("{")
    if start < 0:
        return ""

    depth = 0
    in_string = False
    escaped = False
    for idx in range(start, len(raw)):
        char = raw[idx]

        if in_string:
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
            continue
        if char == "}":
            depth -= 1
            if depth == 0:
                return raw[start : idx + 1]

    return ""


def _try_parse_json_object(candidate: str) -> dict[str, Any] | None:
    raw = str(candidate or "").strip()
    if not raw:
        return None

    attempts: list[str] = []
    for variant in (raw, _extract_json_candidate(raw), _extract_first_balanced_json_object(raw)):
        normalized = str(variant or "").strip()
        if normalized and normalized not in attempts:
            attempts.append(normalized)

    for variant in attempts:
        try:
            parsed = json.loads(variant)
        except Exception:
            continue

        if isinstance(parsed, dict):
            return parsed

        # Some models return a JSON object wrapped as a string.
        if isinstance(parsed, str):
            nested = str(parsed or "").strip()
            if nested and nested != variant:
                nested_parsed = _try_parse_json_object(nested)
                if isinstance(nested_parsed, dict):
                    return nested_parsed

    return None


def _dedupe_non_empty(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _as_text_value(value: Any, *, _depth: int = 0) -> str:
    if _depth > 8:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float, bool)):
        return str(value).strip()

    if isinstance(value, dict):
        preferred = (
            "text",
            "output_text",
            "value",
            "content",
            "message",
            "result",
            "arguments",
            "summary",
            "response",
        )
        chunks: list[str] = []
        for key in preferred:
            if key not in value:
                continue
            chunk = _as_text_value(value.get(key), _depth=_depth + 1)
            if chunk:
                chunks.append(chunk)
        if chunks:
            return "\n".join(_dedupe_non_empty(chunks)).strip()
        if len(value) == 1:
            only_value = next(iter(value.values()))
            return _as_text_value(only_value, _depth=_depth + 1)
        return ""

    if isinstance(value, list):
        chunks = [_as_text_value(item, _depth=_depth + 1) for item in value]
        return "\n".join(_dedupe_non_empty(chunks)).strip()

    return ""


def _collect_text_candidates(
    value: Any,
    *,
    path: str,
    out: list[tuple[str, str]],
    max_items: int = MAX_TEXT_DIAGNOSTIC_PATHS,
    _depth: int = 0,
) -> None:
    if len(out) >= max_items or _depth > 10:
        return

    if isinstance(value, str):
        text = value.strip()
        if text:
            out.append((path, text))
        return

    if isinstance(value, list):
        for index, item in enumerate(value):
            if len(out) >= max_items:
                return
            _collect_text_candidates(
                item,
                path=f"{path}[{index}]",
                out=out,
                max_items=max_items,
                _depth=_depth + 1,
            )
        return

    if isinstance(value, dict):
        for key, item in value.items():
            if len(out) >= max_items:
                return
            safe_key = str(key or "").strip()
            child = f"{path}.{safe_key}" if safe_key else path
            _collect_text_candidates(item, path=child, out=out, max_items=max_items, _depth=_depth + 1)


def _is_known_output_text_path(path: str) -> bool:
    normalized = str(path or "").strip()
    if not normalized:
        return False
    patterns = (
        r"^response\.output_text$",
        r"^response\.output\[\d+\]\.text$",
        r"^response\.output\[\d+\]\.output_text$",
        r"^response\.output\[\d+\]\.content\[\d+\]\.text$",
        r"^response\.output\[\d+\]\.content\[\d+\]\.output_text$",
        r"^response\.output\[\d+\]\.content\[\d+\]\.value$",
        r"^response\.output\[\d+\]\.content\[\d+\]\.text\.value$",
    )
    return any(re.match(pattern, normalized) for pattern in patterns)


def _is_useful_text_candidate(path: str, text: str) -> bool:
    normalized_path = str(path or "").strip().lower()
    normalized_text = str(text or "").strip()
    if not normalized_text:
        return False

    if normalized_path.endswith((".id", ".model", ".status", ".type", ".role", ".object", ".reason", ".code")):
        return False
    if "usage" in normalized_path:
        return False
    if not any(marker in normalized_path for marker in ("output", "content", "message", "response", "result")):
        return False

    if normalized_text.startswith("{") or normalized_text.startswith("["):
        return True
    if "\n" in normalized_text:
        return True
    if len(normalized_text) >= 12:
        return True
    return False


def _output_item_diagnostics(output_items: list[Any]) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    for idx, item in enumerate(output_items[:MAX_OUTPUT_DIAGNOSTIC_ITEMS]):
        if not isinstance(item, dict):
            diagnostics.append(
                {
                    "index": idx,
                    "type": type(item).__name__,
                    "has_content": False,
                    "content_types": [],
                    "text_len": len(_as_text_value(item)),
                    "content_parts": [],
                }
            )
            continue

        content = item.get("content")
        content_parts = content if isinstance(content, list) else []
        content_types: list[str] = []
        part_meta: list[dict[str, Any]] = []
        for part_idx, part in enumerate(content_parts[:MAX_OUTPUT_DIAGNOSTIC_ITEMS]):
            if isinstance(part, dict):
                part_type = str(part.get("type") or "").strip() or "unknown"
                content_types.append(part_type)
                part_meta.append(
                    {
                        "index": part_idx,
                        "type": part_type,
                        "text_len": len(_as_text_value(part.get("text"))),
                        "output_text_len": len(_as_text_value(part.get("output_text"))),
                        "value_len": len(_as_text_value(part.get("value"))),
                    }
                )
            else:
                part_meta.append(
                    {
                        "index": part_idx,
                        "type": type(part).__name__,
                        "text_len": len(_as_text_value(part)),
                        "output_text_len": 0,
                        "value_len": 0,
                    }
                )

        diagnostics.append(
            {
                "index": idx,
                "type": str(item.get("type") or "").strip() or "unknown",
                "has_content": bool(content_parts),
                "content_types": content_types,
                "text_len": len(_as_text_value(item.get("text"))),
                "output_text_len": len(_as_text_value(item.get("output_text"))),
                "content_parts": part_meta,
            }
        )
    return diagnostics


def _build_openai_response_diagnostics(response_data: dict[str, Any]) -> dict[str, Any]:
    output_items = response_data.get("output") if isinstance(response_data.get("output"), list) else []

    text_candidates: list[tuple[str, str]] = []
    _collect_text_candidates(response_data, path="response", out=text_candidates)
    unexpected_text_paths = [
        {"path": path, "length": len(text)}
        for path, text in text_candidates
        if _is_useful_text_candidate(path, text) and not _is_known_output_text_path(path)
    ][:MAX_TEXT_DIAGNOSTIC_PATHS]

    output_types = []
    for item in output_items:
        if isinstance(item, dict):
            output_types.append(str(item.get("type") or "").strip() or "unknown")
        else:
            output_types.append(type(item).__name__)

    return {
        "response_id": response_data.get("id"),
        "response_status": str(response_data.get("status") or "").strip() or "unknown",
        "incomplete_details": response_data.get("incomplete_details")
        if isinstance(response_data.get("incomplete_details"), dict)
        else None,
        "output_items_count": len(output_items),
        "output_types": output_types[:MAX_OUTPUT_DIAGNOSTIC_ITEMS],
        "top_level_output_text_present": bool(_as_text_value(response_data.get("output_text"))),
        "top_level_output_text_len": len(_as_text_value(response_data.get("output_text"))),
        "output_items": _output_item_diagnostics(output_items),
        "unexpected_text_paths": unexpected_text_paths,
    }


def _extract_output_text_details(response_data: dict[str, Any]) -> OutputTextExtraction:
    candidate_paths: list[str] = []

    top_level_output_text = _as_text_value(response_data.get("output_text"))
    if top_level_output_text:
        return OutputTextExtraction(
            text=top_level_output_text,
            path="output_text",
            candidate_paths=["output_text"],
        )

    output = response_data.get("output")
    output_items = output if isinstance(output, list) else []

    content_chunks: list[str] = []
    for item_idx, item in enumerate(output_items):
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part_idx, part in enumerate(content):
            if isinstance(part, dict):
                for key in ("text", "output_text"):
                    chunk = _as_text_value(part.get(key))
                    if chunk:
                        content_chunks.append(chunk)
                        candidate_paths.append(f"output[{item_idx}].content[{part_idx}].{key}")
            else:
                chunk = _as_text_value(part)
                if chunk:
                    content_chunks.append(chunk)
                    candidate_paths.append(f"output[{item_idx}].content[{part_idx}]")

    content_chunks = _dedupe_non_empty(content_chunks)
    if content_chunks:
        return OutputTextExtraction(
            text="\n".join(content_chunks).strip(),
            path="output[*].content[*].text|output_text",
            candidate_paths=_dedupe_non_empty(candidate_paths),
        )

    direct_chunks: list[str] = []
    for item_idx, item in enumerate(output_items):
        if not isinstance(item, dict):
            continue
        for key in ("text", "output_text"):
            chunk = _as_text_value(item.get(key))
            if chunk:
                direct_chunks.append(chunk)
                candidate_paths.append(f"output[{item_idx}].{key}")

    direct_chunks = _dedupe_non_empty(direct_chunks)
    if direct_chunks:
        return OutputTextExtraction(
            text="\n".join(direct_chunks).strip(),
            path="output[*].text|output_text",
            candidate_paths=_dedupe_non_empty(candidate_paths),
        )

    nested_candidates: list[tuple[str, str]] = []
    for item_idx, item in enumerate(output_items):
        _collect_text_candidates(item, path=f"response.output[{item_idx}]", out=nested_candidates)
    nested_text_chunks = [
        text
        for path, text in nested_candidates
        if _is_useful_text_candidate(path, text) and not _is_known_output_text_path(path)
    ]
    nested_text_chunks = _dedupe_non_empty(nested_text_chunks)
    if nested_text_chunks:
        for path, text in nested_candidates:
            if _is_useful_text_candidate(path, text) and not _is_known_output_text_path(path):
                candidate_paths.append(path.replace("response.", "", 1))
        return OutputTextExtraction(
            text="\n".join(nested_text_chunks).strip(),
            path="output[*].<nested_text_fields>",
            candidate_paths=_dedupe_non_empty(candidate_paths),
        )

    top_level_candidates: list[tuple[str, str]] = []
    _collect_text_candidates(response_data, path="response", out=top_level_candidates)
    top_level_chunks = [
        text
        for path, text in top_level_candidates
        if _is_useful_text_candidate(path, text) and not _is_known_output_text_path(path)
    ]
    top_level_chunks = _dedupe_non_empty(top_level_chunks)
    if top_level_chunks:
        for path, text in top_level_candidates:
            if _is_useful_text_candidate(path, text) and not _is_known_output_text_path(path):
                candidate_paths.append(path.replace("response.", "", 1))
        return OutputTextExtraction(
            text="\n".join(top_level_chunks).strip(),
            path="response.<nested_text_fields>",
            candidate_paths=_dedupe_non_empty(candidate_paths),
        )

    return OutputTextExtraction(text="", path="none", candidate_paths=_dedupe_non_empty(candidate_paths))


def _extract_output_text(response_data: dict[str, Any]) -> str:
    return _extract_output_text_details(response_data).text


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

    title = "Рекомендации по улучшению"
    if module == "seo":
        title = "AI-рекомендации по SEO"
    elif module == "conversion":
        title = "AI-рекомендации по повышению конверсии"

    summary = (
        lines[0][:340]
        if lines
        else "Найдены точки роста, которые стоит проверить в первую очередь."
    )

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


def _normalize_ai_payload(
    *,
    module: str,
    raw_text: str,
    payload_for_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate = _extract_json_candidate(raw_text)

    parsed: dict[str, Any] | None = _try_parse_json_object(candidate)
    if not parsed:
        parsed = _try_parse_json_object(raw_text)

    if not parsed:
        parsed = _extract_json_like_payload(candidate)

    if not parsed:
        parsed = _extract_json_like_payload(raw_text)

    if module == "seo":
        return _build_seo_structured_result(
            parsed=parsed,
            payload_for_model=payload_for_model or {},
            fallback_text=raw_text,
        )

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
        fallback_from_text = _build_result_from_text(module=module, text=summary)
        items = fallback_from_text.get("items") or []

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


def _build_error_response(
    *,
    module: str,
    model: str,
    cache_scope: str,
    payload_for_model: dict[str, Any],
    exc: Exception,
    period: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload_size = len(json.dumps(payload_for_model, ensure_ascii=False))

    if isinstance(exc, OpenAIRequestError):
        debug = {
            "message": exc.message,
            "status_code": exc.status_code,
            "error_type": exc.error_type,
            "error_param": exc.error_param,
            "error_code": exc.error_code,
            "request_id": exc.request_id,
            "response_status": exc.response_status,
            "incomplete_details": exc.incomplete_details,
        }
    else:
        debug = {
            "message": str(exc),
            "status_code": None,
            "error_type": exc.__class__.__name__,
            "error_param": None,
            "error_code": None,
            "request_id": None,
            "response_status": None,
            "incomplete_details": None,
        }

    result = {
        "success": False,
        "source": "openai_error",
        "title": "Ошибка получения AI-ответа",
        "summary": "OpenAI не вернул валидный ответ. Смотрите поле debug.",
        "items": [],
        "priority": "medium",
        "debug": debug,
        "debug_context": {
            "module": module,
            "model": model,
            "endpoint": OPENAI_RESPONSES_URL,
            "cache_scope": cache_scope,
            "payload_size": payload_size,
            "enabled": bool(getattr(settings, "AI_RECOMMENDATIONS_ENABLED", False)),
            "has_key": bool(getattr(settings, "OPENAI_API_KEY", "")),
            "timeout_seconds": float(getattr(settings, "AI_RECOMMENDATIONS_TIMEOUT_SECONDS", 20) or 20),
        },
        "generated_at": timezone.now().isoformat(),
        "cached": False,
    }

    if period:
        result["period"] = period

    return result


def _extract_error_type(exc: Exception) -> str:
    if isinstance(exc, OpenAIRequestError):
        error_type = str(exc.error_type or exc.error_code or "").strip().lower()
        if error_type:
            return error_type
        if exc.status_code:
            return f"http_{int(exc.status_code)}"
        return "openai_error"

    return str(exc.__class__.__name__ or "unexpected_error").strip().lower() or "unexpected_error"


def _build_seo_fallback_result(
    *,
    model: str,
    cache_scope: str,
    payload_for_model: dict[str, Any],
    exc: Exception,
    period: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error_payload = _build_error_response(
        module="seo",
        model=model,
        cache_scope=cache_scope,
        payload_for_model=payload_for_model,
        exc=exc,
        period=period,
    )

    overview = _build_seo_default_overview(payload_for_model)
    highlights = _build_seo_default_highlights(payload_for_model)
    metrics_review = _build_seo_default_metrics_review(payload_for_model)
    problems = _build_seo_default_problems(payload_for_model)
    fix_plan = _build_seo_default_fix_plan(problems)
    recommendations = _build_seo_default_recommendations(payload_for_model, problems)

    result = {
        "success": True,
        "source": "fallback",
        "fallback": True,
        "title": "Рекомендации по SEO временно недоступны",
        "summary": "Сейчас AI-анализ временно недоступен. Ниже показаны базовые рекомендации на основе данных последнего SEO-аудита.",
        "user_message": "AI-анализ временно недоступен. Показаны базовые рекомендации по данным последнего аудита.",
        "priority": "medium",
        "overview": overview,
        "highlights": highlights[:MAX_HIGHLIGHTS],
        "metrics_review": metrics_review[:MAX_METRICS_REVIEW],
        "problems": problems[:MAX_PROBLEMS],
        "fix_plan": fix_plan[:MAX_FIX_PLAN],
        "recommendations": recommendations[:MAX_ITEMS],
        # backward compatibility for existing UI/composables
        "items": recommendations[:MAX_ITEMS],
        "debug": error_payload.get("debug"),
        "debug_context": error_payload.get("debug_context"),
        "generated_at": error_payload.get("generated_at") or timezone.now().isoformat(),
        "cached": False,
    }

    if period:
        result["period"] = period

    return result


def _request_openai(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_output_tokens_override: int | None = None,
) -> dict[str, Any]:
    safe_model = str(model or "").strip()
    if not safe_model:
        raise OpenAIRequestError(
            "Model name is empty.",
            error_type="configuration_error",
        )

    api_key = str(getattr(settings, "OPENAI_API_KEY", "") or "").strip()
    if not api_key:
        raise OpenAIRequestError(
            "OPENAI_API_KEY is empty.",
            error_type="configuration_error",
        )

    default_max_output_tokens = _safe_int_setting("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", 900)
    max_output_tokens = int(max_output_tokens_override or default_max_output_tokens)

    body: dict[str, Any] = {
        "model": safe_model,
        "instructions": system_prompt,
        "input": user_prompt,
        "max_output_tokens": max_output_tokens,
    }

    timeout_seconds = float(getattr(settings, "AI_RECOMMENDATIONS_TIMEOUT_SECONDS", 20) or 20)

    logger.info(
        "ai_recommendations openai request: endpoint=%s model=%s timeout=%s max_output_tokens=%s input_len=%s instructions_len=%s",
        OPENAI_RESPONSES_URL,
        safe_model,
        timeout_seconds,
        max_output_tokens,
        len(str(user_prompt or "")),
        len(str(system_prompt or "")),
    )

    response: requests.Response | None = None
    current_timeout = timeout_seconds

    for attempt in (1, 2):
        try:
            response = requests.post(
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=current_timeout,
            )
            break

        except requests.exceptions.ReadTimeout as exc:
            logger.warning(
                "ai_recommendations openai timeout: model=%s attempt=%s timeout=%s error=%s",
                safe_model,
                attempt,
                current_timeout,
                exc,
            )
            if attempt == 1:
                current_timeout = max(timeout_seconds * 2, timeout_seconds + 10)
                continue

            raise OpenAIRequestError(
                f"OpenAI request timed out after retry: {exc}",
                error_type="network_timeout",
            ) from exc

        except requests.exceptions.RequestException as exc:
            logger.warning(
                "ai_recommendations openai network error: model=%s attempt=%s error=%s",
                safe_model,
                attempt,
                exc,
            )
            if attempt == 1:
                continue

            raise OpenAIRequestError(
                f"OpenAI request failed: {exc}",
                error_type="network_error",
            ) from exc

    if response is None:
        raise OpenAIRequestError(
            "OpenAI request failed before receiving response.",
            error_type="network_error",
        )

    response_headers = getattr(response, "headers", {}) or {}
    if not hasattr(response_headers, "get"):
        response_headers = {}
    request_id = response_headers.get("x-request-id") or response_headers.get("openai-request-id")

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

        logger.error(
            "ai_recommendations openai http error: model=%s status=%s request_id=%s error_type=%s error_param=%s error_code=%s message=%s",
            safe_model,
            response.status_code,
            request_id,
            error_payload.get("type"),
            error_payload.get("param"),
            error_payload.get("code"),
            message,
        )

        raise OpenAIRequestError(
            message=message,
            status_code=response.status_code,
            error_type=str(error_payload.get("type") or ""),
            error_param=str(error_payload.get("param") or ""),
            error_code=str(error_payload.get("code") or ""),
            request_id=str(request_id or ""),
        )

    try:
        payload = response.json()
    except Exception as exc:
        raise OpenAIRequestError(
            f"Failed to parse OpenAI JSON: {exc}",
            status_code=response.status_code,
            request_id=str(request_id or ""),
        ) from exc

    if not isinstance(payload, dict):
        raise OpenAIRequestError(
            "OpenAI response is not a JSON object.",
            status_code=response.status_code,
            request_id=str(request_id or ""),
        )

    payload_status = str(payload.get("status") or "").strip() or "unknown"
    incomplete_details = payload.get("incomplete_details")
    response_diagnostics = _build_openai_response_diagnostics(payload)
    extracted_probe = _extract_output_text_details(payload)

    logger.info(
        "openai response received: model=%s status=%s request_id=%s response_id=%s response_status=%s incomplete_details=%s output_items=%s output_types=%s has_output_text=%s has_top_level_output_text=%s",
        safe_model,
        response.status_code,
        request_id,
        response_diagnostics.get("response_id"),
        payload_status,
        incomplete_details if isinstance(incomplete_details, dict) else None,
        response_diagnostics.get("output_items_count"),
        response_diagnostics.get("output_types"),
        bool(extracted_probe.text),
        bool(response_diagnostics.get("top_level_output_text_present")),
    )
    logger.info(
        "openai response diagnostics: model=%s request_id=%s top_level_output_text_len=%s extraction_probe_path=%s extraction_probe_text_len=%s output_items_meta=%s unexpected_text_paths=%s",
        safe_model,
        request_id,
        response_diagnostics.get("top_level_output_text_len"),
        extracted_probe.path,
        len(extracted_probe.text),
        response_diagnostics.get("output_items"),
        response_diagnostics.get("unexpected_text_paths"),
    )
    if extracted_probe.text:
        logger.info(
            "openai response text preview: model=%s request_id=%s text_preview=%s",
            safe_model,
            request_id,
            _truncate_for_log(extracted_probe.text),
        )
    if extracted_probe.candidate_paths:
        logger.info(
            "openai response candidate text paths: model=%s request_id=%s paths=%s",
            safe_model,
            request_id,
            extracted_probe.candidate_paths,
        )

    logger.info(
        "ai_recommendations openai response: model=%s status=%s request_id=%s response_status=%s output_items=%s has_output_text=%s incomplete_details=%s",
        safe_model,
        response.status_code,
        request_id,
        payload_status,
        response_diagnostics.get("output_items_count"),
        bool(extracted_probe.text),
        incomplete_details if isinstance(incomplete_details, dict) else None,
    )

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

    for group in sorted_groups[:6]:
        title = str(group.get("title") or group.get("issue_type") or "").strip()
        top_issues.append(
            {
                "issue_type": group.get("issue_type"),
                "title": title[:120],
                "severity": group.get("severity"),
                "pages_affected": int(group.get("pages_affected") or 0),
            }
        )

    def has_issue(issue_type: str) -> bool:
        return any(
            str(item.get("issue_type") or "").strip().lower() == issue_type
            for item in errors
            if isinstance(item, dict)
        )

    breakdown = detail_payload.get("breakdown") or {}
    issue_type_counts: dict[str, int] = {}
    for item in errors:
        if not isinstance(item, dict):
            continue
        issue_key = str(item.get("issue_type") or "").strip().lower()
        if not issue_key:
            continue
        issue_type_counts[issue_key] = issue_type_counts.get(issue_key, 0) + 1

    issue_type_counts_sorted = sorted(issue_type_counts.items(), key=lambda pair: pair[1], reverse=True)[:8]

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
        "sitemap_status": "ok" if detail_payload.get("has_sitemap_xml") else "missing",
        "indexing_status": "issues" if int(detail_payload.get("pages_with_indexing_issues") or 0) > 0 else "ok",
        "page_speed_status": "issues" if int(detail_payload.get("pages_with_speed_issues") or 0) > 0 else "ok",
        "pages_with_speed_issues": int(detail_payload.get("pages_with_speed_issues") or 0),
        "pages_with_indexing_issues": int(detail_payload.get("pages_with_indexing_issues") or 0),
        "content_length_status": (
            "issues"
            if any(has_issue(name) for name in ("thin_content", "too_short_content", "low_word_count"))
            else "ok"
        ),
        "image_alt_status": (
            "issues"
            if any(has_issue(name) for name in ("missing_alt", "missing_image_alt"))
            else "ok"
        ),
        "internal_links_status": "issues" if has_issue("low_internal_links") else "ok",
        "avg_ttfb_ms": int(detail_payload.get("avg_ttfb_ms") or 0),
        "avg_performance_score": int(detail_payload.get("avg_performance_score") or 0),
        "issue_type_counts": [
            {"issue_type": issue_type, "count": count}
            for issue_type, count in issue_type_counts_sorted
        ],
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


def _build_user_prompt(*, module: str, payload_for_model: dict[str, Any], retry_mode: bool = False) -> str:
    payload_json = json.dumps(payload_for_model, ensure_ascii=False)

    if module == "seo":
        if retry_mode:
            return (
                "Return valid JSON only (no markdown).\n"
                "Language: Russian.\n"
                "Use only provided SEO audit data and keep output compact.\n"
                'Required keys: {"title","summary","priority","problems","recommendations","fix_plan"}.\n'
                "Limits: summary 1-2 short sentences; problems 3; recommendations 3; fix_plan up to 4 steps.\n"
                'Each problem item: {"title","severity","description"}.\n'
                'Each fix_plan item: {"step","title","details"}.\n'
                f"SEO audit data:\n{payload_json}"
            )

        return (
            "Return valid JSON only (no markdown).\n"
            "Language: Russian.\n"
            "Analyze only provided SEO audit data. No assumptions outside data.\n"
            "Required keys:\n"
            "{\n"
            '  "title": "...",\n'
            '  "summary": "...",\n'
            '  "priority": "high|medium|low",\n'
            '  "problems": [{"title":"...","severity":"high|medium|low","description":"..."}],\n'
            '  "recommendations": ["..."],\n'
            '  "fix_plan": [{"step":1,"title":"...","details":"..."}]\n'
            "}\n"
            'Optional keys: "overview", "highlights", "metrics_review".\n'
            "Limits: summary 1-2 short sentences; problems 3-5; recommendations 3-5; fix_plan up to 5 steps; "
            "highlights up to 4; metrics_review up to 6.\n"
            f"SEO audit data:\n{payload_json}"
        )

    if retry_mode:
        return (
            "Return JSON only without markdown.\n"
            'Format: {"title":"...","summary":"...","items":["..."],"priority":"high|medium|low"}\n'
            "Language: Russian. Keep concise: summary 1 sentence, items 3-5.\n"
            f"Data:\n{payload_json}"
        )

    return (
        "Analyze the data below and return JSON only without markdown.\n"
        'Format: {"title":"...","summary":"...","items":["..."],"priority":"high|medium|low"}\n'
        "Requirements: 3-7 concrete actions, practical style, based only on provided data.\n"
        "Important: response language must be Russian.\n"
        f"Data:\n{payload_json}"
    )


def _generate_recommendations(
    *,
    module: str,
    model: str,
    cache_scope: str,
    payload_for_model: dict[str, Any],
    system_prompt: str,
    force_refresh: bool,
    period: dict[str, Any] | None = None,
) -> dict[str, Any]:
    timeout_seconds = float(getattr(settings, "AI_RECOMMENDATIONS_TIMEOUT_SECONDS", 20) or 20)

    if not _is_ai_enabled():
        disabled_error = OpenAIRequestError(
            message="AI recommendations are disabled or OPENAI_API_KEY is missing.",
            error_type="configuration_error",
        )
        if module == "seo":
            fallback_reason = _extract_error_type(disabled_error)
            logger.warning("seo ai fallback activated")
            logger.warning("seo ai fallback reason=%s", fallback_reason)
            logger.warning("openai fallback activated: reason=%s", fallback_reason)
            return _build_seo_fallback_result(
                model=model,
                cache_scope=cache_scope,
                payload_for_model=payload_for_model,
                exc=disabled_error,
                period=period,
            )

        return _build_error_response(
            module=module,
            model=model,
            cache_scope=cache_scope,
            payload_for_model=payload_for_model,
            exc=disabled_error,
            period=period,
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
                "ai_recommendations skip cached non-ai payload: module=%s model=%s cached_success=%s cached_source=%s",
                module,
                model,
                cached_success,
                cached_source or "unknown",
            )

    initial_max_tokens = _resolve_max_output_tokens(module)
    payload_size = len(json.dumps(payload_for_model, ensure_ascii=False))
    logger.info(
        "ai_recommendations request start: module=%s model=%s endpoint=%s timeout=%s payload_size=%s max_output_tokens=%s force_refresh=%s",
        module,
        model,
        OPENAI_RESPONSES_URL,
        timeout_seconds,
        payload_size,
        initial_max_tokens,
        force_refresh,
    )

    user_prompt = _build_user_prompt(module=module, payload_for_model=payload_for_model, retry_mode=False)

    try:
        raw_response = _request_openai(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_output_tokens_override=initial_max_tokens,
        )

        response_status = str(raw_response.get("status") or "").strip()
        incomplete_details = raw_response.get("incomplete_details")
        incomplete_reason = (
            str(incomplete_details.get("reason") or "").strip()
            if isinstance(incomplete_details, dict)
            else ""
        )

        logger.info(
            "ai_recommendations response meta: module=%s model=%s status=%s incomplete_details=%s",
            module,
            model,
            response_status or "unknown",
            incomplete_details if isinstance(incomplete_details, dict) else None,
        )

        extraction = _extract_output_text_details(raw_response)
        output_text = extraction.text

        logger.info(
            "ai_recommendations parsed output: module=%s model=%s output_items=%s extracted_text_len=%s extraction_path=%s candidate_paths=%s",
            module,
            model,
            len(raw_response.get("output") or []) if isinstance(raw_response.get("output"), list) else 0,
            len(output_text),
            extraction.path,
            extraction.candidate_paths,
        )
        logger.info(
            "openai extraction path used: module=%s model=%s path=%s extracted_text_len=%s",
            module,
            model,
            extraction.path,
            len(output_text),
        )

        if output_text and response_status == "incomplete":
            logger.info(
                "openai partial text accepted despite incomplete status: module=%s model=%s reason=%s extracted_text_len=%s",
                module,
                model,
                incomplete_reason or "unknown",
                len(output_text),
            )

        if not output_text:
            retry_max = _resolve_retry_max_output_tokens(module, initial_max_tokens)
            retry_prompt = _build_user_prompt(module=module, payload_for_model=payload_for_model, retry_mode=True)
            logger.warning(
                "openai retry triggered due to missing usable text: module=%s model=%s response_status=%s incomplete_reason=%s retry_max_output_tokens=%s",
                module,
                model,
                response_status or "unknown",
                incomplete_reason or "unknown",
                retry_max,
            )

            retry_response = _request_openai(
                model=model,
                system_prompt=system_prompt,
                user_prompt=retry_prompt,
                max_output_tokens_override=retry_max,
            )
            retry_status = str(retry_response.get("status") or "").strip()
            retry_incomplete_details = retry_response.get("incomplete_details")
            retry_reason = (
                str(retry_incomplete_details.get("reason") or "").strip()
                if isinstance(retry_incomplete_details, dict)
                else ""
            )
            retry_extraction = _extract_output_text_details(retry_response)

            logger.info(
                "ai_recommendations retry parsed output: module=%s model=%s status=%s output_items=%s extracted_text_len=%s extraction_path=%s candidate_paths=%s",
                module,
                model,
                retry_status or "unknown",
                len(retry_response.get("output") or []) if isinstance(retry_response.get("output"), list) else 0,
                len(retry_extraction.text),
                retry_extraction.path,
                retry_extraction.candidate_paths,
            )
            logger.info(
                "openai extraction path used: module=%s model=%s path=%s extracted_text_len=%s",
                module,
                model,
                retry_extraction.path,
                len(retry_extraction.text),
            )

            if retry_extraction.text:
                output_text = retry_extraction.text
                response_status = retry_status
                incomplete_details = retry_incomplete_details
                incomplete_reason = retry_reason
                if retry_status == "incomplete":
                    logger.info(
                        "openai partial text accepted despite incomplete status: module=%s model=%s reason=%s extracted_text_len=%s",
                        module,
                        model,
                        retry_reason or "unknown",
                        len(output_text),
                    )
                logger.info(
                    "ai_recommendations retry success: module=%s model=%s extracted_text_len=%s",
                    module,
                    model,
                    len(output_text),
                )
            else:
                raise OpenAIRequestError(
                    message="OpenAI returned empty output.",
                    error_type="empty_output",
                    error_code=retry_reason or incomplete_reason or "missing_usable_text",
                    response_status=retry_status or response_status or None,
                    incomplete_details=(
                        retry_incomplete_details
                        if isinstance(retry_incomplete_details, dict)
                        else (incomplete_details if isinstance(incomplete_details, dict) else None)
                    ),
                )

        result = _normalize_ai_payload(
            module=module,
            raw_text=output_text,
            payload_for_model=payload_for_model,
        )
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
        if module == "seo":
            logger.info("seo ai success: model=%s source=%s", model, result.get("source"))

        if period:
            result["period"] = period

        return result

    except Exception as exc:
        logger.exception(
            "ai_recommendations failure: module=%s model=%s error=%s",
            module,
            model,
            exc,
        )
        if module == "seo":
            fallback_reason = _extract_error_type(exc)
            logger.warning("seo ai fallback activated")
            logger.warning("seo ai fallback reason=%s", fallback_reason)
            logger.warning("openai fallback activated: reason=%s", fallback_reason)
            try:
                return _build_seo_fallback_result(
                    model=model,
                    cache_scope=cache_scope,
                    payload_for_model=payload_for_model,
                    exc=exc,
                    period=period,
                )
            except Exception as fallback_exc:
                logger.exception(
                    "seo ai hard failure: fallback builder failed: model=%s error=%s",
                    model,
                    fallback_exc,
                )
                exc = fallback_exc

        return _build_error_response(
            module=module,
            model=model,
            cache_scope=cache_scope,
            payload_for_model=payload_for_model,
            exc=exc,
            period=period,
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
        "You are a senior SEO analyst for TrackNode. "
        "Analyze only the provided SEO audit payload. "
        "Do not hallucinate missing facts. "
        "Return concise and practical recommendations in Russian JSON."
    )

    return _generate_recommendations(
        module="seo",
        model=model,
        cache_scope=cache_scope,
        payload_for_model=seo_payload,
        system_prompt=system_prompt,
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
        "You are a CRO and lead-generation expert. "
        "Analyze only user behavior analytics data. "
        "Find where users drop off and what actions can increase leads. "
        "Do not give SEO advice. "
        "Keep recommendations concise, practical, and in Russian."
    )

    return _generate_recommendations(
        module="conversion",
        model=model,
        cache_scope=cache_scope,
        payload_for_model=conversion_payload,
        system_prompt=system_prompt,
        force_refresh=force_refresh,
        period={
            "date_from": from_label,
            "date_to": to_label,
        },
    )


def run_ai_connectivity_check(model: str | None = None) -> dict[str, Any]:
    selected_model = str(
        model or getattr(settings, "OPENAI_MODEL_SEO", "gpt-5-mini") or "gpt-5-mini"
    ).strip()

    try:
        raw = _request_openai(
            model=selected_model,
            system_prompt="Ответь строго одной короткой фразой на русском.",
            user_prompt="Скажи: API работает.",
        )
        text = _extract_output_text(raw)

        return {
            "success": bool(text),
            "source": "openai",
            "model": raw.get("model") or selected_model,
            "status": raw.get("status"),
            "incomplete_details": raw.get("incomplete_details"),
            "output_items": len(raw.get("output") or []) if isinstance(raw.get("output"), list) else 0,
            "text": (text or "").strip(),
            "debug": None,
            "generated_at": timezone.now().isoformat(),
        }

    except Exception as exc:
        return {
            "success": False,
            "source": "openai_error",
            "model": selected_model,
            "status": None,
            "incomplete_details": None,
            "output_items": 0,
            "text": "",
            "debug": _build_error_response(
                module="connectivity_check",
                model=selected_model,
                cache_scope="connectivity-check",
                payload_for_model={"ping": True},
                exc=exc,
            )["debug"],
            "generated_at": timezone.now().isoformat(),
        }
