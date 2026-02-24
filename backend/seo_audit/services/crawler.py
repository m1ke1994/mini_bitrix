import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Optional
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit

logger = logging.getLogger(__name__)

MAX_PAGES_DEFAULT = 100
REQUEST_TIMEOUT_SECONDS = 8
SLOW_RESPONSE_SECONDS = 2.0
MAX_PAGE_BYTES = 2 * 1024 * 1024
SKIP_FILE_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".svg")
HEADING_TAG_RE = re.compile(r"^h[1-6]$")
WORD_RE = re.compile(r"[A-Za-z0-9\u0400-\u04FF]+")


class AuditCancelledError(Exception):
    pass


@dataclass
class FetchResult:
    url: str
    response: Optional[requests.Response]
    error: Optional[str]
    elapsed_seconds: float
    size_bytes: int


def _check_cancelled(stop_check: Optional[Callable[[], bool]]) -> None:
    if stop_check and stop_check():
        raise AuditCancelledError()


def _normalized_host(hostname: str) -> str:
    host = str(hostname or "").strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _normalize_url(raw_url: str) -> str:
    parsed = urlparse(str(raw_url or "").strip())
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
        if not path:
            path = "/"
    return urlunparse((scheme, netloc, path, "", "", ""))


def _is_internal_url(url: str, root_host: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    return _normalized_host(parsed.hostname or "") == _normalized_host(root_host)


def _should_skip_url(url: str) -> bool:
    path = (urlparse(url).path or "").lower()
    return any(path.endswith(ext) for ext in SKIP_FILE_EXTENSIONS)


def _build_start_url(domain: str) -> str:
    raw = str(domain or "").strip()
    if not raw:
        return ""
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    host = (parsed.hostname or "").strip()
    scheme = parsed.scheme if parsed.scheme in ("http", "https") else "https"
    return f"{scheme}://{host}/"


def _extract_text(value) -> str:
    if not value:
        return ""
    return " ".join(str(value).split())


def _extract_title(soup: Optional[BeautifulSoup]) -> str:
    if not soup or not soup.title:
        return ""
    return _extract_text(soup.title.get_text(" ", strip=True))


def _extract_meta_content(soup: Optional[BeautifulSoup], name: str) -> str:
    if not soup:
        return ""
    target = str(name or "").strip().lower()
    if not target:
        return ""
    tag = soup.find("meta", attrs={"name": lambda v: str(v or "").strip().lower() == target})
    return _extract_text(tag.get("content")) if tag else ""


def _extract_h1_values(soup: Optional[BeautifulSoup]) -> list[str]:
    if not soup:
        return []
    return [_extract_text(tag.get_text(" ", strip=True)) for tag in soup.find_all("h1")]


def _count_words(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def _response_size_bytes(response: requests.Response) -> int:
    content = getattr(response, "content", None)
    if isinstance(content, (bytes, bytearray)):
        return len(content)
    text = getattr(response, "text", "") or ""
    encoding = getattr(response, "encoding", None) or "utf-8"
    try:
        return len(str(text).encode(encoding, errors="ignore"))
    except Exception:
        return len(str(text).encode("utf-8", errors="ignore"))


def _prepare_response_text(response: requests.Response) -> str:
    apparent = getattr(response, "apparent_encoding", None) or None
    encoding = apparent or getattr(response, "encoding", None) or "utf-8"
    try:
        response.encoding = encoding
    except Exception:
        pass
    try:
        return response.text or ""
    except Exception:
        content = getattr(response, "content", b"") or b""
        if isinstance(content, str):
            return content
        try:
            return bytes(content).decode(encoding or "utf-8", errors="replace")
        except Exception:
            return bytes(content).decode("utf-8", errors="replace")


def _fetch_url(session: requests.Session, url: str, stop_check: Optional[Callable[[], bool]]) -> FetchResult:
    _check_cancelled(stop_check)
    started = time.monotonic()
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True)
        elapsed = time.monotonic() - started
        return FetchResult(
            url=url,
            response=response,
            error=None,
            elapsed_seconds=elapsed,
            size_bytes=_response_size_bytes(response),
        )
    except requests.RequestException as exc:
        elapsed = time.monotonic() - started
        return FetchResult(url=url, response=None, error=str(exc), elapsed_seconds=elapsed, size_bytes=0)


def _create_issue(page: SEOPage, issue_type: str, severity: str, recommendation: str) -> None:
    SEOIssue.objects.create(
        page=page,
        issue_type=issue_type,
        severity=severity,
        recommendation=recommendation,
    )


def _get_anchor_page(audit: SiteSEOAudit, page_by_url: dict[str, SEOPage], start_url: str) -> SEOPage:
    start_key = _normalize_url(start_url)
    page = page_by_url.get(start_key)
    if page:
        return page
    page, _ = SEOPage.objects.get_or_create(
        audit=audit,
        url=start_key,
        defaults={
            "status_code": 0,
            "title": "",
            "title_length": 0,
            "description": "",
            "description_length": 0,
            "h1": "",
            "h1_count": 0,
            "word_count": 0,
        },
    )
    page_by_url[start_key] = page
    return page


def _extract_internal_links(soup: Optional[BeautifulSoup], page_url: str, root_host: str) -> list[str]:
    if not soup:
        return []
    links: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = str(tag.get("href") or "").strip()
        if not href or href.startswith("#"):
            continue
        if href.lower().startswith(("javascript:", "mailto:", "tel:")):
            continue
        absolute = _normalize_url(urljoin(page_url, href))
        if not absolute:
            continue
        if not _is_internal_url(absolute, root_host):
            continue
        if _should_skip_url(absolute):
            continue
        links.append(absolute)
    return links


def _has_meta_charset(soup: Optional[BeautifulSoup]) -> bool:
    if not soup:
        return False
    if soup.find("meta", attrs={"charset": True}):
        return True
    content_type_meta = soup.find(
        "meta",
        attrs={"http-equiv": lambda v: str(v or "").strip().lower() == "content-type"},
    )
    if not content_type_meta:
        return False
    content = str(content_type_meta.get("content") or "").lower()
    return "charset=" in content


def _has_canonical(soup: Optional[BeautifulSoup]) -> bool:
    if not soup:
        return False
    return bool(
        soup.find(
            "link",
            attrs={"rel": lambda v: "canonical" in [str(x).lower() for x in (v if isinstance(v, list) else [v])]},
        )
    )


def _heading_hierarchy_gap(soup: Optional[BeautifulSoup]) -> bool:
    if not soup:
        return False
    levels = []
    for tag in soup.find_all(HEADING_TAG_RE):
        try:
            levels.append(int(tag.name[1]))
        except Exception:
            continue
    for prev, current in zip(levels, levels[1:]):
        if current - prev > 1:
            return True
    return False


def _analyze_page_content(
    page: SEOPage,
    *,
    requested_url: str,
    final_url: str,
    status_code: int,
    elapsed_seconds: float,
    size_bytes: int,
    response: Optional[requests.Response],
    soup: Optional[BeautifulSoup],
) -> None:
    if status_code != 200:
        _create_issue(
            page,
            "bad_status",
            SEOIssue.Severity.HIGH,
            f"Page returned HTTP {status_code}. Fix server or routing response and ensure the page returns HTTP 200.",
        )

    history = list(getattr(response, "history", []) or []) if response is not None else []
    if history or (_normalize_url(final_url) and _normalize_url(final_url) != _normalize_url(requested_url)):
        _create_issue(
            page,
            "redirect",
            SEOIssue.Severity.LOW,
            "Page URL resolves through a redirect. Link directly to the final canonical URL to reduce crawl overhead.",
        )

    if elapsed_seconds > SLOW_RESPONSE_SECONDS:
        _create_issue(
            page,
            "slow_response",
            SEOIssue.Severity.MEDIUM,
            f"Page response time is {elapsed_seconds:.2f}s (>2s). Improve backend performance, caching, or CDN delivery.",
        )

    if size_bytes > MAX_PAGE_BYTES:
        size_mb = size_bytes / (1024 * 1024)
        _create_issue(
            page,
            "large_page_size",
            SEOIssue.Severity.MEDIUM,
            f"Page size is {size_mb:.2f}MB (>2MB). Compress assets and reduce HTML/JS payload size.",
        )

    if status_code != 200:
        return

    if not soup:
        return

    title = page.title or ""
    if not title:
        _create_issue(
            page,
            "missing_title",
            SEOIssue.Severity.HIGH,
            "Title tag is missing. Add a unique title around 50-60 characters with the main page intent.",
        )
    elif len(title) < 15:
        _create_issue(
            page,
            "title_too_short",
            SEOIssue.Severity.MEDIUM,
            "Title is too short (<15 chars). Expand it to describe the page topic with useful keywords.",
        )
    elif len(title) > 65:
        _create_issue(
            page,
            "title_too_long",
            SEOIssue.Severity.MEDIUM,
            "Title is too long (>65 chars). Shorten it so search engines can display it without truncation.",
        )

    description = page.description or ""
    if not description:
        _create_issue(
            page,
            "missing_description",
            SEOIssue.Severity.MEDIUM,
            "Meta description is missing. Add a unique 120-160 character summary to improve snippet quality.",
        )
    elif len(description) < 50:
        _create_issue(
            page,
            "description_too_short",
            SEOIssue.Severity.LOW,
            "Meta description is too short (<50 chars). Expand it with a concise summary and user benefit.",
        )
    elif len(description) > 160:
        _create_issue(
            page,
            "description_too_long",
            SEOIssue.Severity.LOW,
            "Meta description is too long (>160 chars). Shorten it to avoid truncation in search snippets.",
        )

    h1_values = _extract_h1_values(soup)
    if not h1_values:
        _create_issue(
            page,
            "missing_h1",
            SEOIssue.Severity.MEDIUM,
            "H1 heading is missing. Add one clear H1 that reflects the page topic.",
        )
    if len(h1_values) > 1:
        _create_issue(
            page,
            "multiple_h1",
            SEOIssue.Severity.MEDIUM,
            "More than one H1 was found. Keep a single H1 and use H2-H6 for the content structure.",
        )
    if any(len(h1) > 70 for h1 in h1_values):
        _create_issue(
            page,
            "long_h1",
            SEOIssue.Severity.LOW,
            "H1 is too long (>70 chars). Shorten the main heading so it stays readable and focused.",
        )

    if _heading_hierarchy_gap(soup):
        _create_issue(
            page,
            "heading_hierarchy_gap",
            SEOIssue.Severity.LOW,
            "Heading hierarchy skips levels (for example H1 to H3). Use sequential heading levels for structure.",
        )

    if page.word_count < 300 and status_code == 200:
        _create_issue(
            page,
            "low_word_count",
            SEOIssue.Severity.LOW,
            "Page has low text content (<300 words). Add more useful content to better cover the topic.",
        )

    missing_alt = 0
    empty_alt = 0
    for img in soup.find_all("img"):
        if not img.has_attr("alt"):
            missing_alt += 1
            continue
        if not _extract_text(img.get("alt")):
            empty_alt += 1
    if missing_alt:
        _create_issue(
            page,
            "image_missing_alt",
            SEOIssue.Severity.LOW,
            f"{missing_alt} image(s) have no alt attribute. Add descriptive alt text for informative images.",
        )
    if empty_alt:
        _create_issue(
            page,
            "image_empty_alt",
            SEOIssue.Severity.LOW,
            f"{empty_alt} image(s) have an empty alt attribute. Fill alt text unless the image is purely decorative.",
        )

    if not _has_canonical(soup):
        _create_issue(
            page,
            "missing_canonical",
            SEOIssue.Severity.LOW,
            "Canonical link tag is missing. Add a canonical URL to reduce duplicate-content ambiguity.",
        )

    if not _extract_meta_content(soup, "robots"):
        _create_issue(
            page,
            "missing_meta_robots",
            SEOIssue.Severity.LOW,
            "Meta robots tag is missing. Add a robots meta tag only if you need explicit index/follow directives.",
        )

    if not _extract_meta_content(soup, "viewport"):
        _create_issue(
            page,
            "missing_viewport",
            SEOIssue.Severity.LOW,
            "Viewport meta tag is missing. Add viewport settings for correct mobile rendering.",
        )

    if not _has_meta_charset(soup):
        _create_issue(
            page,
            "missing_charset",
            SEOIssue.Severity.LOW,
            "Charset meta tag is missing. Add <meta charset=\"utf-8\"> in the page head.",
        )


def _apply_duplicate_title_checks(audit: SiteSEOAudit) -> None:
    pages = SEOPage.objects.filter(audit=audit).exclude(title="").order_by("id")
    title_map: dict[str, list[SEOPage]] = defaultdict(list)
    for page in pages:
        normalized_title = _extract_text(page.title).lower()
        if not normalized_title:
            continue
        title_map[normalized_title].append(page)

    for duplicates in title_map.values():
        if len(duplicates) < 2:
            continue
        for page in duplicates:
            _create_issue(
                page,
                "duplicate_title",
                SEOIssue.Severity.MEDIUM,
                "Title duplicates another page title. Make each title unique for the page intent and target query.",
            )


def _analyze_robots_and_sitemap(
    audit: SiteSEOAudit,
    session: requests.Session,
    *,
    start_url: str,
    root_host: str,
    page_by_url: dict[str, SEOPage],
    crawled_urls: set[str],
    stop_check: Optional[Callable[[], bool]],
) -> None:
    _check_cancelled(stop_check)
    anchor_page = _get_anchor_page(audit, page_by_url, start_url)
    root_base = _normalize_url(start_url)

    robots_url = urljoin(root_base, "/robots.txt")
    robots_result = _fetch_url(session, robots_url, stop_check)
    sitemap_candidates: list[str] = []
    if not robots_result.response:
        _create_issue(
            anchor_page,
            "missing_robots_txt",
            SEOIssue.Severity.LOW,
            "robots.txt could not be fetched. Add a robots.txt file and declare sitemap location if available.",
        )
    else:
        robots_status = int(getattr(robots_result.response, "status_code", 0) or 0)
        if robots_status != 200:
            _create_issue(
                anchor_page,
                "missing_robots_txt",
                SEOIssue.Severity.LOW,
                f"robots.txt returned HTTP {robots_status}. Publish a valid robots.txt file at /robots.txt.",
            )
        else:
            robots_text = _prepare_response_text(robots_result.response)
            current_ua_is_all = False
            disallow_all = False
            for raw_line in robots_text.splitlines():
                line = raw_line.split("#", 1)[0].strip()
                if not line or ":" not in line:
                    continue
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == "user-agent":
                    current_ua_is_all = value.lower() == "*"
                elif key == "disallow" and current_ua_is_all and value == "/":
                    disallow_all = True
                elif key == "sitemap" and value:
                    sitemap_candidates.append(value)

            if disallow_all:
                _create_issue(
                    anchor_page,
                    "robots_disallow_all",
                    SEOIssue.Severity.HIGH,
                    "robots.txt blocks the whole site for User-agent: *. Remove 'Disallow: /' for public pages.",
                )
            if not sitemap_candidates:
                _create_issue(
                    anchor_page,
                    "robots_missing_sitemap",
                    SEOIssue.Severity.LOW,
                    "robots.txt does not declare a sitemap. Add a Sitemap directive with the sitemap.xml URL.",
                )

    if not sitemap_candidates:
        sitemap_candidates = [urljoin(root_base, "/sitemap.xml")]

    sitemap_url = None
    for candidate in sitemap_candidates:
        normalized = _normalize_url(urljoin(root_base, candidate))
        if _is_internal_url(normalized, root_host):
            sitemap_url = normalized
            break
    if not sitemap_url:
        sitemap_url = _normalize_url(urljoin(root_base, "/sitemap.xml"))

    _check_cancelled(stop_check)
    sitemap_result = _fetch_url(session, sitemap_url, stop_check)
    if not sitemap_result.response:
        _create_issue(
            anchor_page,
            "missing_sitemap",
            SEOIssue.Severity.MEDIUM,
            "sitemap.xml could not be fetched. Publish a sitemap.xml file with important page URLs.",
        )
        return

    sitemap_status = int(getattr(sitemap_result.response, "status_code", 0) or 0)
    if sitemap_status != 200:
        _create_issue(
            anchor_page,
            "bad_sitemap_status",
            SEOIssue.Severity.MEDIUM,
            f"sitemap.xml returned HTTP {sitemap_status}. Ensure sitemap.xml is publicly accessible with HTTP 200.",
        )
        return

    sitemap_text = _prepare_response_text(sitemap_result.response)
    sitemap_soup = BeautifulSoup(sitemap_text, "xml")
    loc_values: set[str] = set()
    for loc_tag in sitemap_soup.find_all("loc"):
        loc_text = _extract_text(loc_tag.get_text(" ", strip=True))
        if not loc_text:
            continue
        normalized = _normalize_url(loc_text)
        if normalized and _is_internal_url(normalized, root_host) and not _should_skip_url(normalized):
            loc_values.add(normalized)

    if not loc_values:
        _create_issue(
            anchor_page,
            "missing_sitemap",
            SEOIssue.Severity.MEDIUM,
            "sitemap.xml is empty or contains no internal URLs. Add page URLs to the sitemap.",
        )
        return

    if crawled_urls:
        overlap_count = len(crawled_urls & loc_values)
        if overlap_count < len(crawled_urls):
            _create_issue(
                anchor_page,
                "sitemap_mismatch",
                SEOIssue.Severity.LOW,
                (
                    f"Sitemap contains {len(loc_values)} URL(s), crawled {len(crawled_urls)} page(s), "
                    f"overlap is {overlap_count}. Align sitemap entries with real internal pages."
                ),
            )


def recalculate_audit_score(audit: SiteSEOAudit) -> dict[str, int]:
    severity_counts = {
        SEOIssue.Severity.HIGH: 0,
        SEOIssue.Severity.MEDIUM: 0,
        SEOIssue.Severity.LOW: 0,
    }

    issues = SEOIssue.objects.filter(page__audit=audit).values_list("severity", flat=True)
    for severity in issues:
        if severity in severity_counts:
            severity_counts[severity] += 1

    score = 100
    score -= severity_counts[SEOIssue.Severity.HIGH] * 7
    score -= severity_counts[SEOIssue.Severity.MEDIUM] * 3
    score -= severity_counts[SEOIssue.Severity.LOW] * 1
    score = max(0, score)

    audit.seo_score = score
    audit.pages_count = SEOPage.objects.filter(audit=audit).count()
    audit.save(update_fields=["seo_score", "pages_count"])

    return {
        "score": score,
        "high_issues": severity_counts[SEOIssue.Severity.HIGH],
        "medium_issues": severity_counts[SEOIssue.Severity.MEDIUM],
        "low_issues": severity_counts[SEOIssue.Severity.LOW],
    }


def crawl_site_audit(
    audit: SiteSEOAudit,
    *,
    session: Optional[requests.Session] = None,
    max_pages: Optional[int] = None,
    stop_check: Optional[Callable[[], bool]] = None,
) -> SiteSEOAudit:
    start_url = _build_start_url(audit.domain)
    if not start_url:
        raise ValueError("Audit domain is empty.")

    max_pages = max_pages or MAX_PAGES_DEFAULT
    root_host = urlparse(start_url).hostname or audit.domain
    local_session = session or requests.Session()
    local_session.headers.setdefault("User-Agent", "TrackNode SEO Audit/1.0 (+https://tracknode.local)")

    _check_cancelled(stop_check)

    # Re-running the same audit should replace previous crawl data, not append duplicate pages/issues.
    audit.pages.all().delete()

    queue: deque[str] = deque([_normalize_url(start_url)])
    queued: set[str] = {queue[0]}
    visited: set[str] = set()
    page_by_url: dict[str, SEOPage] = {}
    crawled_urls: set[str] = set()

    while queue and len(visited) < max_pages:
        _check_cancelled(stop_check)
        requested_url = queue.popleft()
        queued.discard(requested_url)
        if requested_url in visited:
            continue
        visited.add(requested_url)

        if not _is_internal_url(requested_url, root_host) or _should_skip_url(requested_url):
            continue

        fetch = _fetch_url(local_session, requested_url, stop_check)
        if not fetch.response:
            page, _ = SEOPage.objects.update_or_create(
                audit=audit,
                url=requested_url,
                defaults={
                    "status_code": 0,
                    "title": "",
                    "title_length": 0,
                    "description": "",
                    "description_length": 0,
                    "h1": "",
                    "h1_count": 0,
                    "word_count": 0,
                },
            )
            page_by_url[requested_url] = page
            _create_issue(
                page,
                "network_error",
                SEOIssue.Severity.HIGH,
                f"Page could not be fetched ({fetch.error or 'network error'}). Check DNS, SSL, firewall, or server availability.",
            )
            continue

        response = fetch.response
        final_url = _normalize_url(getattr(response, "url", "") or requested_url)
        if final_url and _is_internal_url(final_url, root_host):
            visited.add(final_url)
            target_url = final_url
        else:
            target_url = requested_url

        status_code = int(getattr(response, "status_code", 0) or 0)
        content_type = str((getattr(response, "headers", {}) or {}).get("Content-Type") or "").lower()
        is_html = ("html" in content_type) or (not content_type and status_code == 200)
        html_text = ""
        soup = None
        title = ""
        description = ""
        h1_values: list[str] = []
        page_text = ""
        word_count = 0

        if is_html:
            html_text = _prepare_response_text(response)
            soup = BeautifulSoup(html_text, "lxml")
            title = _extract_title(soup)
            description = _extract_meta_content(soup, "description")
            h1_values = _extract_h1_values(soup)
            page_text = _extract_text(soup.get_text(" ", strip=True))
            word_count = _count_words(page_text)

        page_defaults = {
            "status_code": status_code,
            "title": title,
            "title_length": len(title),
            "description": description,
            "description_length": len(description),
            "h1": h1_values[0] if h1_values else "",
            "h1_count": len(h1_values),
            "word_count": word_count,
        }
        page, _ = SEOPage.objects.update_or_create(audit=audit, url=target_url, defaults=page_defaults)
        page_by_url[target_url] = page
        if status_code == 200:
            crawled_urls.add(target_url)

        _analyze_page_content(
            page,
            requested_url=requested_url,
            final_url=target_url,
            status_code=status_code,
            elapsed_seconds=fetch.elapsed_seconds,
            size_bytes=fetch.size_bytes,
            response=response,
            soup=soup,
        )

        if soup and status_code == 200:
            for link in _extract_internal_links(soup, target_url, root_host):
                if link in visited or link in queued:
                    continue
                if len(visited) + len(queue) >= max_pages:
                    break
                queue.append(link)
                queued.add(link)

    _check_cancelled(stop_check)
    _apply_duplicate_title_checks(audit)
    _analyze_robots_and_sitemap(
        audit,
        local_session,
        start_url=start_url,
        root_host=root_host,
        page_by_url=page_by_url,
        crawled_urls=crawled_urls,
        stop_check=stop_check,
    )
    _check_cancelled(stop_check)
    recalculate_audit_score(audit)
    return audit
