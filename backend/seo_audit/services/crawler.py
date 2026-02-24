import logging
import re
from collections import deque
from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from django.db.models import Count

from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit

logger = logging.getLogger(__name__)

MAX_PAGES_DEFAULT = 50
REQUEST_TIMEOUT_SECONDS = 10

_WORD_RE = re.compile(r"\w+", re.UNICODE)


class AuditCancelledError(Exception):
    pass


def crawl_site_audit(
    audit: SiteSEOAudit,
    max_pages: int = MAX_PAGES_DEFAULT,
    session: requests.Session | None = None,
    stop_check: Callable[[], bool] | None = None,
) -> SiteSEOAudit:
    start_url = _start_url_from_domain(audit.domain)
    root_host = _canonical_host(urlparse(start_url).hostname)
    queue: deque[str] = deque([start_url])
    visited: set[str] = set()
    title_to_page_ids: dict[str, list[int]] = {}
    http = session or requests.Session()

    # Safety for repeated runs on the same audit record.
    audit.pages.all().delete()

    while queue and len(visited) < max_pages:
        if stop_check and stop_check():
            raise AuditCancelledError("SEO audit was cancelled")
        current_url = _normalize_page_url(queue.popleft())
        if current_url in visited:
            continue
        visited.add(current_url)

        page_data = _fetch_page(http, current_url)
        seo_page = SEOPage.objects.create(
            audit=audit,
            url=current_url,
            status_code=max(0, int(page_data.get("status_code") or 0)),
            title=page_data.get("title") or "",
            title_length=int(page_data.get("title_length") or 0),
            description=page_data.get("description") or "",
            description_length=int(page_data.get("description_length") or 0),
            h1=page_data.get("h1") or "",
            h1_count=int(page_data.get("h1_count") or 0),
            word_count=int(page_data.get("word_count") or 0),
        )
        _create_page_issues(seo_page)

        title_key = ((seo_page.title or "").strip().lower())
        if title_key:
            title_to_page_ids.setdefault(title_key, []).append(seo_page.id)

        for next_url in page_data.get("internal_links") or []:
            if len(visited) + len(queue) >= max_pages and next_url not in visited:
                continue
            parsed_next = urlparse(next_url)
            if _canonical_host(parsed_next.hostname) != root_host:
                continue
            normalized_next = _normalize_page_url(next_url)
            if normalized_next not in visited:
                queue.append(normalized_next)

    _create_duplicate_title_issues(audit, title_to_page_ids)
    recalculate_audit_score(audit)
    return audit


def _fetch_page(http: requests.Session, url: str) -> dict:
    from bs4 import BeautifulSoup

    try:
        response = http.get(url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True)
    except requests.RequestException as exc:
        logger.warning("seo_audit.crawler request failed url=%s error=%s", url, exc)
        return {
            "status_code": 0,
            "title": "",
            "title_length": 0,
            "description": "",
            "description_length": 0,
            "h1": "",
            "h1_count": 0,
            "word_count": 0,
            "internal_links": [],
        }

    status_code = int(response.status_code or 0)
    content_type = (response.headers.get("Content-Type") or "").lower()
    is_html = "html" in content_type or not content_type
    if not is_html:
        return {
            "status_code": status_code,
            "title": "",
            "title_length": 0,
            "description": "",
            "description_length": 0,
            "h1": "",
            "h1_count": 0,
            "word_count": 0,
            "internal_links": [],
        }

    html = response.text or ""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    title = ""
    if soup.title:
        title = (soup.title.get_text(" ", strip=True) or "").strip()

    description = ""
    description_tag = soup.find("meta", attrs={"name": lambda value: str(value or "").lower() == "description"})
    if description_tag:
        description = (description_tag.get("content") or "").strip()

    h1_tags = soup.find_all("h1")
    h1_text = (h1_tags[0].get_text(" ", strip=True) if h1_tags else "") or ""
    visible_text = soup.get_text(" ", strip=True) if soup else ""
    word_count = len(_WORD_RE.findall(visible_text or ""))

    parsed_final = urlparse(str(response.url or url))
    internal_links = _extract_internal_links(soup=soup, base_url=url, root_host=_canonical_host(parsed_final.hostname))
    return {
        "status_code": status_code,
        "title": title,
        "title_length": len(title),
        "description": description,
        "description_length": len(description),
        "h1": h1_text,
        "h1_count": len(h1_tags),
        "word_count": word_count,
        "internal_links": sorted(internal_links),
    }


def _extract_internal_links(*, soup: Any, base_url: str, root_host: str) -> set[str]:
    links: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href") or "").strip()
        if not href:
            continue
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)
        if parsed.scheme not in ("http", "https"):
            continue
        if _canonical_host(parsed.hostname) != root_host:
            continue
        links.add(_normalize_page_url(absolute_url))
    return links


def _create_page_issues(page: SEOPage) -> None:
    if page.status_code != 200:
        _create_issue(
            page=page,
            issue_type=SEOIssue.IssueType.BAD_STATUS,
            severity=SEOIssue.Severity.HIGH,
            recommendation=f"Проверьте URL и исправьте HTTP-статус (сейчас {page.status_code}).",
        )

    title = (page.title or "").strip()
    if not title:
        _create_issue(
            page=page,
            issue_type=SEOIssue.IssueType.MISSING_TITLE,
            severity=SEOIssue.Severity.HIGH,
            recommendation="Добавьте уникальный тег <title> длиной 10-70 символов.",
        )
    elif page.title_length < 10 or page.title_length > 70:
        _create_issue(
            page=page,
            issue_type=SEOIssue.IssueType.BAD_TITLE_LENGTH,
            severity=SEOIssue.Severity.MEDIUM,
            recommendation="Скорректируйте длину <title> до диапазона 10-70 символов.",
        )

    if not (page.description or "").strip():
        _create_issue(
            page=page,
            issue_type=SEOIssue.IssueType.MISSING_DESCRIPTION,
            severity=SEOIssue.Severity.MEDIUM,
            recommendation="Добавьте meta description с описанием страницы.",
        )

    if page.h1_count == 0:
        _create_issue(
            page=page,
            issue_type=SEOIssue.IssueType.MISSING_H1,
            severity=SEOIssue.Severity.MEDIUM,
            recommendation="Добавьте один релевантный заголовок H1.",
        )
    elif page.h1_count > 1:
        _create_issue(
            page=page,
            issue_type=SEOIssue.IssueType.MULTIPLE_H1,
            severity=SEOIssue.Severity.MEDIUM,
            recommendation="Оставьте один основной H1 на странице.",
        )


def _create_duplicate_title_issues(audit: SiteSEOAudit, title_to_page_ids: dict[str, list[int]]) -> None:
    duplicate_page_ids: set[int] = set()
    for _title_key, page_ids in title_to_page_ids.items():
        if len(page_ids) > 1:
            duplicate_page_ids.update(page_ids)
    if not duplicate_page_ids:
        return

    for page in SEOPage.objects.filter(audit=audit, id__in=duplicate_page_ids):
        _create_issue(
            page=page,
            issue_type=SEOIssue.IssueType.DUPLICATE_TITLE,
            severity=SEOIssue.Severity.MEDIUM,
            recommendation="Сделайте <title> уникальным для этой страницы.",
        )


def _create_issue(*, page: SEOPage, issue_type: str, severity: str, recommendation: str) -> SEOIssue:
    return SEOIssue.objects.create(
        page=page,
        issue_type=issue_type,
        severity=severity,
        recommendation=recommendation,
    )


def _recalculate_audit_score(audit: SiteSEOAudit) -> None:
    severity_counts = {
        row["severity"]: int(row["count"] or 0)
        for row in (
            SEOIssue.objects.filter(page__audit=audit)
            .values("severity")
            .annotate(count=Count("id"))
        )
    }
    high_count = severity_counts.get(SEOIssue.Severity.HIGH, 0)
    medium_count = severity_counts.get(SEOIssue.Severity.MEDIUM, 0)
    score = max(0, 100 - (high_count * 5) - (medium_count * 2))
    pages_count = audit.pages.count()
    audit.seo_score = score
    audit.pages_count = pages_count
    audit.save(update_fields=["seo_score", "pages_count"])


def recalculate_audit_score(audit: SiteSEOAudit) -> None:
    _recalculate_audit_score(audit)


def _start_url_from_domain(domain: str) -> str:
    normalized = normalize_domain(domain)
    return f"https://{normalized}/"


def normalize_domain(domain: str) -> str:
    raw = (domain or "").strip()
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise ValueError("Invalid domain")
    return host


def _normalize_page_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower() or "https"
    host = (parsed.hostname or "").strip().lower()
    if not host:
        return url
    netloc = host
    if parsed.port and not ((scheme == "http" and parsed.port == 80) or (scheme == "https" and parsed.port == 443)):
        netloc = f"{host}:{parsed.port}"
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", "", ""))


def _canonical_host(hostname: str | None) -> str:
    host = (hostname or "").strip().lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host
