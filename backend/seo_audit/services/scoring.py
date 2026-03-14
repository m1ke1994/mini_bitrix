# -*- coding: utf-8 -*-
from __future__ import annotations

from collections import defaultdict

from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit

SPEED_ISSUE_TYPES = {
    "slow_response",
    "large_page_size",
    "slow_ttfb",
    "large_html_size",
    "too_many_js",
    "too_many_css",
    "too_many_images",
    "heavy_js_payload",
    "heavy_css_payload",
    "heavy_images_payload",
    "heavy_page_payload",
}

INDEXING_ISSUE_TYPES = {
    "missing_robots_txt",
    "robots_disallow_all",
    "robots_missing_sitemap",
    "missing_sitemap",
    "bad_sitemap_status",
    "sitemap_mismatch",
    "missing_canonical",
    "invalid_canonical",
    "canonical_conflict",
    "page_noindex",
    "page_nofollow",
    "blocked_by_robots",
    "sitemap_page_missing",
    "missing_meta_robots",
}

CRITICAL_SCORE_ISSUE_TYPES = {
    "network_error",
    "bad_status",
    "robots_disallow_all",
    "missing_robots_txt",
    "missing_sitemap",
    "bad_sitemap_status",
    "blocked_by_robots",
    "slow_ttfb",
    "heavy_page_payload",
}

SCORE_COMPONENT_WEIGHTS = {
    "technical_accessibility": 0.32,
    "indexability": 0.24,
    "meta_structure": 0.20,
    "performance": 0.16,
    "issues_health": 0.08,
}


def _clamp_score(value: float) -> int:
    return int(max(0, min(100, round(float(value)))))


def _safe_ratio(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, float(part) / float(total))


def _average_int(values: list[int]) -> int:
    if not values:
        return 0
    return int(round(sum(values) / len(values)))


def _build_audit_score_snapshot(audit: SiteSEOAudit) -> dict[str, object]:
    pages = list(
        SEOPage.objects.filter(audit=audit).values(
            "id",
            "status_code",
            "ttfb_ms",
            "performance_score",
            "speed_status",
            "indexability_status",
            "blocked_by_robots",
            "in_sitemap",
            "title",
            "description",
            "h1",
            "h1_count",
            "word_count",
            "canonical_url",
        )
    )
    issues = list(SEOIssue.objects.filter(page__audit=audit).values("severity", "issue_type", "page_id"))

    severity_counts = {
        SEOIssue.Severity.HIGH: 0,
        SEOIssue.Severity.MEDIUM: 0,
        SEOIssue.Severity.LOW: 0,
    }
    issue_type_counts: dict[str, int] = defaultdict(int)
    issue_page_ids_by_type: dict[str, set[int]] = defaultdict(set)
    speed_issue_page_ids: set[int] = set()
    indexing_issue_page_ids: set[int] = set()

    for issue in issues:
        severity = str(issue.get("severity") or "").strip().lower()
        issue_type = str(issue.get("issue_type") or "").strip().lower()
        page_id = int(issue.get("page_id") or 0)
        if severity in severity_counts:
            severity_counts[severity] += 1
        if issue_type:
            issue_type_counts[issue_type] += 1
            if page_id > 0:
                issue_page_ids_by_type[issue_type].add(page_id)
            if issue_type in SPEED_ISSUE_TYPES and page_id > 0:
                speed_issue_page_ids.add(page_id)
            if issue_type in INDEXING_ISSUE_TYPES and page_id > 0:
                indexing_issue_page_ids.add(page_id)

    pages_count = len(pages)
    status_200_pages = [item for item in pages if int(item.get("status_code") or 0) == 200]
    status_200_ids = {int(item.get("id") or 0) for item in status_200_pages}
    status_200_count = len(status_200_pages)

    network_error_pages = sum(
        1
        for item in pages
        if int(item.get("status_code") or 0) == 0 or int(item.get("id") or 0) in issue_page_ids_by_type["network_error"]
    )
    non_200_pages = sum(1 for item in pages if int(item.get("status_code") or 0) != 200)
    http_error_pages = sum(1 for item in pages if int(item.get("status_code") or 0) >= 400)
    critical_ttfb_pages = sum(1 for item in pages if int(item.get("ttfb_ms") or 0) >= 3000)
    slow_ttfb_pages = sum(1 for item in pages if int(item.get("ttfb_ms") or 0) >= 1800)
    warning_ttfb_pages = sum(1 for item in pages if int(item.get("ttfb_ms") or 0) >= 900)

    critical_speed_pages = sum(
        1 for item in pages if str(item.get("speed_status") or "").strip().lower() == SEOPage.SpeedStatus.CRITICAL
    )
    warning_speed_pages = sum(
        1 for item in pages if str(item.get("speed_status") or "").strip().lower() == SEOPage.SpeedStatus.WARNING
    )
    unknown_speed_pages = sum(
        1 for item in pages if str(item.get("speed_status") or "").strip().lower() == SEOPage.SpeedStatus.UNKNOWN
    )

    index_unknown_pages = sum(
        1
        for item in pages
        if str(item.get("indexability_status") or "").strip().lower() == SEOPage.IndexabilityStatus.UNKNOWN
    )
    index_noindex_pages = sum(
        1
        for item in pages
        if str(item.get("indexability_status") or "").strip().lower() == SEOPage.IndexabilityStatus.NOINDEX
    )
    index_conflict_pages = sum(
        1
        for item in pages
        if str(item.get("indexability_status") or "").strip().lower() == SEOPage.IndexabilityStatus.CONFLICT
    )
    blocked_by_robots_pages = sum(1 for item in pages if bool(item.get("blocked_by_robots")))

    missing_title_pages = sum(1 for item in status_200_pages if not str(item.get("title") or "").strip())
    missing_description_pages = sum(1 for item in status_200_pages if not str(item.get("description") or "").strip())
    missing_h1_pages = sum(
        1
        for item in status_200_pages
        if int(item.get("h1_count") or 0) <= 0 or not str(item.get("h1") or "").strip()
    )
    multiple_h1_pages = sum(1 for item in status_200_pages if int(item.get("h1_count") or 0) > 1)
    low_word_count_pages = sum(1 for item in status_200_pages if int(item.get("word_count") or 0) < 300)
    missing_canonical_pages = sum(1 for item in status_200_pages if not str(item.get("canonical_url") or "").strip())
    invalid_canonical_pages = len(issue_page_ids_by_type["invalid_canonical"] & status_200_ids)
    missing_meta_robots_pages = len(issue_page_ids_by_type["missing_meta_robots"] & status_200_ids)
    not_in_sitemap_pages = sum(1 for item in status_200_pages if not bool(item.get("in_sitemap")))

    ttfb_values = [int(item.get("ttfb_ms") or 0) for item in pages if int(item.get("ttfb_ms") or 0) > 0]
    performance_values = [
        int(item.get("performance_score") or 0) for item in pages if int(item.get("performance_score") or 0) > 0
    ]
    avg_ttfb = _average_int(ttfb_values)
    avg_performance = _average_int(performance_values)

    network_error_ratio = _safe_ratio(network_error_pages, pages_count)
    non_200_ratio = _safe_ratio(non_200_pages, pages_count)
    http_error_ratio = _safe_ratio(http_error_pages, pages_count)
    critical_ttfb_ratio = _safe_ratio(critical_ttfb_pages, pages_count)
    slow_ttfb_ratio = _safe_ratio(slow_ttfb_pages, pages_count)
    warning_ttfb_ratio = _safe_ratio(warning_ttfb_pages, pages_count)
    critical_speed_ratio = _safe_ratio(critical_speed_pages, pages_count)
    warning_speed_ratio = _safe_ratio(warning_speed_pages, pages_count)
    unknown_speed_ratio = _safe_ratio(unknown_speed_pages, pages_count)
    index_unknown_ratio = _safe_ratio(index_unknown_pages, pages_count)
    index_noindex_ratio = _safe_ratio(index_noindex_pages, pages_count)
    index_conflict_ratio = _safe_ratio(index_conflict_pages, pages_count)
    blocked_by_robots_ratio = _safe_ratio(blocked_by_robots_pages, pages_count)

    if pages_count <= 0:
        technical_accessibility_score = 0
    else:
        technical_raw = 100.0
        technical_raw -= network_error_ratio * 70
        technical_raw -= http_error_ratio * 45
        technical_raw -= non_200_ratio * 20
        technical_raw -= critical_ttfb_ratio * 20
        technical_raw -= slow_ttfb_ratio * 10
        if network_error_pages > 0:
            technical_raw -= 15
        if status_200_count == 0:
            technical_raw -= 35
        technical_accessibility_score = _clamp_score(technical_raw)

    if pages_count <= 0:
        indexability_score = 0
    else:
        indexability_raw = 100.0
        if not bool(audit.has_robots_txt):
            indexability_raw -= 30
        if not bool(audit.has_sitemap_xml):
            indexability_raw -= 25
        if issue_type_counts.get("robots_disallow_all", 0) > 0:
            indexability_raw -= 30
        indexability_raw -= blocked_by_robots_ratio * 32
        indexability_raw -= index_unknown_ratio * 28
        indexability_raw -= index_noindex_ratio * 20
        indexability_raw -= index_conflict_ratio * 18
        if status_200_count > 0:
            indexability_raw -= _safe_ratio(missing_canonical_pages, status_200_count) * 18
            indexability_raw -= _safe_ratio(invalid_canonical_pages, status_200_count) * 16
            if bool(audit.has_sitemap_xml) and int(audit.sitemap_urls_count or 0) > 0:
                indexability_raw -= _safe_ratio(not_in_sitemap_pages, status_200_count) * 12
        else:
            indexability_raw -= 15
        if issue_type_counts.get("missing_sitemap", 0) > 0 and not bool(audit.has_sitemap_xml):
            indexability_raw -= 10
        indexability_score = _clamp_score(indexability_raw)

    if pages_count <= 0:
        meta_structure_score = 0
    elif status_200_count <= 0:
        meta_structure_score = 10 if network_error_pages > 0 else 20
    else:
        meta_raw = 100.0
        meta_raw -= _safe_ratio(missing_title_pages, status_200_count) * 35
        meta_raw -= _safe_ratio(missing_description_pages, status_200_count) * 25
        meta_raw -= _safe_ratio(missing_h1_pages, status_200_count) * 20
        meta_raw -= _safe_ratio(multiple_h1_pages, status_200_count) * 10
        meta_raw -= _safe_ratio(low_word_count_pages, status_200_count) * 10
        meta_raw -= _safe_ratio(missing_meta_robots_pages, status_200_count) * 8
        if status_200_count < pages_count:
            meta_raw -= 8
        meta_structure_score = _clamp_score(meta_raw)

    if pages_count <= 0:
        performance_group_score = 0
    else:
        performance_raw = float(avg_performance if avg_performance > 0 else 25)
        if avg_ttfb >= 3000:
            performance_raw -= 35
        elif avg_ttfb >= 2000:
            performance_raw -= 25
        elif avg_ttfb >= 1300:
            performance_raw -= 15
        elif avg_ttfb >= 900:
            performance_raw -= 8
        performance_raw -= critical_speed_ratio * 30
        performance_raw -= warning_speed_ratio * 12
        performance_raw -= network_error_ratio * 20
        if avg_performance <= 0:
            performance_raw -= 10
        if unknown_speed_ratio > 0.6:
            performance_raw -= 8
        performance_group_score = _clamp_score(performance_raw)

    critical_issue_instances = sum(issue_type_counts.get(issue_type, 0) for issue_type in CRITICAL_SCORE_ISSUE_TYPES)
    issues_penalty_points = (
        severity_counts[SEOIssue.Severity.HIGH] * 5
        + severity_counts[SEOIssue.Severity.MEDIUM] * 2
        + severity_counts[SEOIssue.Severity.LOW] * 0.75
        + critical_issue_instances * 2.5
    )
    if pages_count > 0:
        issues_penalty_points += _safe_ratio(critical_issue_instances, pages_count) * 8
    issues_health_score = _clamp_score(100 - min(85, issues_penalty_points))

    weighted_score = (
        technical_accessibility_score * SCORE_COMPONENT_WEIGHTS["technical_accessibility"]
        + indexability_score * SCORE_COMPONENT_WEIGHTS["indexability"]
        + meta_structure_score * SCORE_COMPONENT_WEIGHTS["meta_structure"]
        + performance_group_score * SCORE_COMPONENT_WEIGHTS["performance"]
        + issues_health_score * SCORE_COMPONENT_WEIGHTS["issues_health"]
    )
    score = _clamp_score(weighted_score)

    guardrails_applied = {
        "all_pages_unavailable": False,
        "high_network_error_ratio": False,
        "missing_robots_and_sitemap": False,
        "very_high_avg_ttfb": False,
        "unknown_indexability_all_pages": False,
        "critical_technical_and_indexability": False,
        "network_plus_missing_index_files": False,
    }
    if pages_count > 0:
        if status_200_count == 0:
            score = min(score, 35)
            guardrails_applied["all_pages_unavailable"] = True
        if network_error_ratio >= 0.5:
            score = min(score, 40)
            guardrails_applied["high_network_error_ratio"] = True
        if (not bool(audit.has_robots_txt)) and (not bool(audit.has_sitemap_xml)):
            score = min(score, 60)
            guardrails_applied["missing_robots_and_sitemap"] = True
        if avg_ttfb >= 3000:
            score = min(score, 55)
            guardrails_applied["very_high_avg_ttfb"] = True
        if index_unknown_pages == pages_count:
            score = min(score, 50)
            guardrails_applied["unknown_indexability_all_pages"] = True
        if technical_accessibility_score <= 25 and indexability_score <= 35:
            score = min(score, 42)
            guardrails_applied["critical_technical_and_indexability"] = True
        if issue_type_counts.get("network_error", 0) > 0 and (not bool(audit.has_robots_txt)) and (not bool(audit.has_sitemap_xml)):
            score = min(score, 35)
            guardrails_applied["network_plus_missing_index_files"] = True
    score = _clamp_score(score)

    return {
        "score": score,
        "severity_counts": severity_counts,
        "avg_ttfb_ms": avg_ttfb,
        "avg_performance_score": avg_performance,
        "pages_count": pages_count,
        "pages_with_speed_issues": len(speed_issue_page_ids),
        "pages_with_indexing_issues": len(indexing_issue_page_ids),
        "score_components": {
            "technical_accessibility_score": technical_accessibility_score,
            "indexability_score": indexability_score,
            "meta_structure_score": meta_structure_score,
            "performance_score": performance_group_score,
            "issues_health_score": issues_health_score,
            "weights": {name: int(round(weight * 100)) for name, weight in SCORE_COMPONENT_WEIGHTS.items()},
            "issues_penalty_points": round(float(issues_penalty_points), 2),
            "guardrails": guardrails_applied,
        },
        "score_inputs": {
            "pages_total": pages_count,
            "pages_http_200": status_200_count,
            "pages_network_error": network_error_pages,
            "pages_http_error": http_error_pages,
            "pages_non_200": non_200_pages,
            "pages_unknown_indexability": index_unknown_pages,
            "pages_blocked_by_robots": blocked_by_robots_pages,
            "pages_not_in_sitemap": not_in_sitemap_pages,
            "pages_missing_title": missing_title_pages,
            "pages_missing_description": missing_description_pages,
            "pages_missing_h1": missing_h1_pages,
            "pages_multiple_h1": multiple_h1_pages,
            "pages_low_word_count": low_word_count_pages,
            "pages_missing_canonical": missing_canonical_pages,
            "pages_invalid_canonical": invalid_canonical_pages,
            "pages_missing_meta_robots": missing_meta_robots_pages,
            "pages_critical_speed": critical_speed_pages,
            "pages_warning_speed": warning_speed_pages,
            "pages_unknown_speed": unknown_speed_pages,
            "avg_ttfb_ms": avg_ttfb,
            "avg_performance_score": avg_performance,
            "ratio_network_error": round(network_error_ratio, 4),
            "ratio_non_200": round(non_200_ratio, 4),
            "ratio_http_error": round(http_error_ratio, 4),
            "ratio_critical_ttfb": round(critical_ttfb_ratio, 4),
            "ratio_slow_ttfb": round(slow_ttfb_ratio, 4),
            "ratio_warning_ttfb": round(warning_ttfb_ratio, 4),
            "ratio_unknown_indexability": round(index_unknown_ratio, 4),
            "ratio_blocked_by_robots": round(blocked_by_robots_ratio, 4),
        },
    }


def calculate_audit_score_breakdown(audit: SiteSEOAudit) -> dict[str, object]:
    snapshot = _build_audit_score_snapshot(audit)
    severity_counts = snapshot["severity_counts"]
    return {
        "score": int(snapshot["score"] or 0),
        "high_issues": int(severity_counts[SEOIssue.Severity.HIGH]),
        "medium_issues": int(severity_counts[SEOIssue.Severity.MEDIUM]),
        "low_issues": int(severity_counts[SEOIssue.Severity.LOW]),
        "score_components": snapshot["score_components"],
        "score_inputs": snapshot["score_inputs"],
    }


def recalculate_audit_score(audit: SiteSEOAudit) -> dict[str, object]:
    snapshot = _build_audit_score_snapshot(audit)
    severity_counts = snapshot["severity_counts"]

    audit.seo_score = int(snapshot["score"] or 0)
    audit.pages_count = int(snapshot["pages_count"] or 0)
    audit.avg_ttfb_ms = int(snapshot["avg_ttfb_ms"] or 0)
    audit.avg_performance_score = int(snapshot["avg_performance_score"] or 0)
    audit.pages_with_speed_issues = int(snapshot["pages_with_speed_issues"] or 0)
    audit.pages_with_indexing_issues = int(snapshot["pages_with_indexing_issues"] or 0)
    audit.save(
        update_fields=[
            "seo_score",
            "pages_count",
            "avg_ttfb_ms",
            "avg_performance_score",
            "pages_with_speed_issues",
            "pages_with_indexing_issues",
        ]
    )

    return {
        "score": int(snapshot["score"] or 0),
        "high_issues": int(severity_counts[SEOIssue.Severity.HIGH]),
        "medium_issues": int(severity_counts[SEOIssue.Severity.MEDIUM]),
        "low_issues": int(severity_counts[SEOIssue.Severity.LOW]),
        "score_components": snapshot["score_components"],
        "score_inputs": snapshot["score_inputs"],
    }
