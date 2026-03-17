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

    top_level_output_text = response_data.get("output_text")
    normalized_top_level_text = _as_text(top_level_output_text)
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

            part_type = str(part.get("type") or "").strip()
            if part_type and part_type != "output_text":
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

    parsed: dict[str, Any] | None = None
    try:
        maybe = json.loads(candidate)
        if isinstance(maybe, dict):
            parsed = maybe
    except Exception:
        parsed = None

    if not parsed:
        parsed = _extract_json_like_payload(candidate)

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

    default_max_output_tokens = int(getattr(settings, "AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", 900) or 900)
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
    output_items = payload.get("output") if isinstance(payload.get("output"), list) else []

    logger.info(
        "ai_recommendations openai response: model=%s status=%s request_id=%s response_status=%s output_items=%s has_output_text=%s incomplete_details=%s",
        safe_model,
        response.status_code,
        request_id,
        payload_status,
        len(output_items),
        bool(payload.get("output_text")),
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
        return any(
            str(item.get("issue_type") or "").strip().lower() == issue_type
            for item in errors
            if isinstance(item, dict)
        )

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


def _build_user_prompt(*, module: str, payload_for_model: dict[str, Any]) -> str:
    if module == "seo":
        return (
            "Верни строго JSON без markdown и комментариев.\n"
            "Анализируй только переданные данные SEO-аудита, ничего не выдумывай.\n"
            "Все формулировки делай на русском, кратко и прикладно.\n"
            "Обязательная структура ответа:\n"
            "{\n"
            '  "title": "AI-рекомендации по SEO",\n'
            '  "summary": "Краткая оценка текущего состояния SEO сайта.",\n'
            '  "priority": "high|medium|low",\n'
            '  "overview": {\n'
            '    "seo_score_label": "...",\n'
            '    "pages_checked_label": "...",\n'
            '    "errors_label": "...",\n'
            '    "speed_label": "...",\n'
            '    "indexing_label": "..."\n'
            "  },\n"
            '  "highlights": ["..."],\n'
            '  "metrics_review": [\n'
            '    {"label":"...","value":"...","status":"good|warning|bad|info","comment":"..."}\n'
            "  ],\n"
            '  "problems": [\n'
            '    {"title":"...","severity":"high|medium|low","description":"..."}\n'
            "  ],\n"
            '  "fix_plan": [\n'
            '    {"step":1,"title":"...","details":"..."}\n'
            "  ],\n"
            '  "recommendations": ["..."]\n'
            "}\n"
            "Требования:\n"
            "- highlights: 3-5 пунктов.\n"
            "- metrics_review: 5-8 пунктов.\n"
            "- problems: 2-6 пунктов.\n"
            "- fix_plan: 3-7 шагов по приоритету.\n"
            "- recommendations: 3-7 конкретных действий.\n"
            "- В metrics_review обязательно оцени: SEO-оценку, число страниц, число ошибок, скорость, robots.txt и sitemap.xml (если данные есть).\n"
            "- Отмечай не только проблемы, но и сильные стороны.\n"
            f"Данные SEO-аудита:\n{json.dumps(payload_for_model, ensure_ascii=False)}"
        )

    return (
        "Analyze the data below and return JSON only without markdown.\n"
        'Format: {"title":"...","summary":"...","items":["..."],"priority":"high|medium|low"}\n'
        "Requirements: 3-7 concrete actions, practical style, based only on provided data.\n"
        "Important: response language must be Russian.\n"
        f"Data:\n{json.dumps(payload_for_model, ensure_ascii=False)}"
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

    payload_size = len(json.dumps(payload_for_model, ensure_ascii=False))
    logger.info(
        "ai_recommendations request start: module=%s model=%s endpoint=%s timeout=%s payload_size=%s force_refresh=%s",
        module,
        model,
        OPENAI_RESPONSES_URL,
        timeout_seconds,
        payload_size,
        force_refresh,
    )

    user_prompt = _build_user_prompt(module=module, payload_for_model=payload_for_model)

    try:
        raw_response = _request_openai(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        response_status = str(raw_response.get("status") or "").strip()
        incomplete_details = raw_response.get("incomplete_details")

        logger.info(
            "ai_recommendations response meta: module=%s model=%s status=%s incomplete_details=%s",
            module,
            model,
            response_status or "unknown",
            incomplete_details if isinstance(incomplete_details, dict) else None,
        )

        output_text = _extract_output_text(raw_response)

        logger.info(
            "ai_recommendations parsed output: module=%s model=%s output_items=%s extracted_text_len=%s",
            module,
            model,
            len(raw_response.get("output") or []) if isinstance(raw_response.get("output"), list) else 0,
            len(output_text),
        )

        if not output_text:
            incomplete_reason = ""
            if isinstance(incomplete_details, dict):
                incomplete_reason = str(incomplete_details.get("reason") or "").strip()

            if incomplete_reason == "max_output_tokens":
                retry_max = min(
                    int(getattr(settings, "AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", 900) or 900) * 2,
                    1800,
                )

                logger.warning(
                    "ai_recommendations retry due to incomplete output: module=%s model=%s reason=%s retry_max_output_tokens=%s",
                    module,
                    model,
                    incomplete_reason,
                    retry_max,
                )

                retry_response = _request_openai(
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_output_tokens_override=retry_max,
                )
                retry_text = _extract_output_text(retry_response)

                logger.info(
                    "ai_recommendations retry parsed output: module=%s model=%s output_items=%s extracted_text_len=%s",
                    module,
                    model,
                    len(retry_response.get("output") or []) if isinstance(retry_response.get("output"), list) else 0,
                    len(retry_text),
                )

                if retry_text:
                    result = _normalize_ai_payload(
                        module=module,
                        raw_text=retry_text,
                        payload_for_model=payload_for_model,
                    )
                    _cache_set_safe(
                        cache_key,
                        result,
                        ttl_seconds=int(getattr(settings, "AI_RECOMMENDATIONS_TTL_SECONDS", 10800) or 10800),
                    )
                    logger.info(
                        "ai_recommendations retry success: module=%s model=%s items=%s",
                        module,
                        model,
                        len(result.get("items") or []),
                    )
                    if period:
                        result["period"] = period
                    return result

            raise OpenAIRequestError(
                message="OpenAI returned empty output.",
                error_type="empty_output",
                error_code=incomplete_reason or None,
                response_status=response_status or None,
                incomplete_details=incomplete_details if isinstance(incomplete_details, dict) else None,
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
        "Ты senior SEO-аналитик продукта TrackNode. "
        "Анализируй только переданные данные SEO-аудита. "
        "Не выдумывай факты и не добавляй общую теорию. "
        "Сначала давай приоритетные проблемы, затем быстрые улучшения. "
        "Ответ всегда на русском и строго в JSON-структуре из запроса."
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
