# -*- coding: utf-8 -*-
import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Optional
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from django.db.models import Avg

from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.services.messages import get_issue_recommendation

logger = logging.getLogger(__name__)

MAX_PAGES_DEFAULT = 100
MAX_SITEMAP_URLS_DEFAULT = 200
REQUEST_TIMEOUT_SECONDS = 8
SLOW_RESPONSE_SECONDS = 2.0
MAX_PAGE_BYTES = 2 * 1024 * 1024
MAX_RESOURCE_FETCH_BUDGET = 600
SKIP_FILE_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".svg", ".zip", ".doc", ".docx", ".xls", ".xlsx")
HEADING_TAG_RE = re.compile(r"^h[1-6]$")
WORD_RE = re.compile(r"[A-Za-z0-9\u0400-\u04FF]+")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s\(\)]{7,}\d)")

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

CTA_TEXT_HINTS = (
    "оставить заявку",
    "оставить запрос",
    "заказать",
    "купить",
    "получить",
    "связаться",
    "отправить",
    "консульта",
    "перезвон",
    "записаться",
    "call",
    "contact",
    "request",
    "submit",
    "book",
    "buy",
    "order",
)
CTA_ATTR_HINTS = ("cta", "lead", "order", "buy", "request", "contact", "submit")
OFFER_HINTS = (
    "под ключ",
    "под заказ",
    "цена",
    "стоимость",
    "скидк",
    "выгода",
    "бесплатно",
    "гарант",
    "лучшее",
    "best",
    "offer",
    "solution",
)
BENEFITS_HINTS = ("преимущ", "почему мы", "why us", "benefit", "feature", "reason")
FAQ_HINTS = ("faq", "вопрос", "question", "часто задаваем")
MESSENGER_HINTS = ("wa.me", "whatsapp", "t.me", "telegram", "viber", "vk.me", "facebook.com/messages")


class AuditCancelledError(Exception):
    pass


@dataclass
class FetchResult:
    url: str
    response: Optional[requests.Response]
    error: Optional[str]
    elapsed_seconds: float
    ttfb_ms: int
    size_bytes: int


@dataclass
class SitemapURLResult:
    response_received: bool
    status_code: int
    is_xml: bool
    urls: list[str]


@dataclass
class RobotsRule:
    allow: bool
    path: str


@dataclass
class IndexingContext:
    anchor_page: SEOPage
    has_robots_txt: bool
    has_sitemap_xml: bool
    robots_disallow_all: bool
    robots_rules: list[RobotsRule]
    sitemap_urls: set[str]
    sitemap_response_received: bool
    sitemap_status_code: int
    sitemap_is_xml: bool


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


def _normalize_resource_url(raw_url: str, base_url: str) -> str:
    absolute = urljoin(base_url, str(raw_url or "").strip())
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""
    path = parsed.path or "/"
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))


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


def _extract_canonical_url(soup: Optional[BeautifulSoup], page_url: str) -> tuple[str, bool]:
    if not soup:
        return "", False
    tag = soup.find(
        "link",
        attrs={"rel": lambda v: "canonical" in [str(x).lower() for x in (v if isinstance(v, list) else [v])]},
    )
    if not tag:
        return "", False
    href = _extract_text(tag.get("href"))
    if not href:
        return "", False
    absolute = urljoin(page_url, href)
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return href, False
    return _normalize_url(absolute), True


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


def _extract_ttfb_ms(response: Optional[requests.Response], elapsed_seconds: float) -> int:
    if response is None:
        return int(max(0, round(elapsed_seconds * 1000)))
    elapsed = getattr(response, "elapsed", None)
    if elapsed is not None:
        try:
            return int(max(0, round(float(elapsed.total_seconds()) * 1000)))
        except Exception:
            pass
    return int(max(0, round(elapsed_seconds * 1000)))


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
            ttfb_ms=_extract_ttfb_ms(response, elapsed),
            size_bytes=_response_size_bytes(response),
        )
    except requests.RequestException as exc:
        elapsed = time.monotonic() - started
        return FetchResult(
            url=url,
            response=None,
            error=str(exc),
            elapsed_seconds=elapsed,
            ttfb_ms=int(max(0, round(elapsed * 1000))),
            size_bytes=0,
        )


def _response_content_type(response: Optional[requests.Response]) -> str:
    if response is None:
        return ""
    return str((getattr(response, "headers", {}) or {}).get("Content-Type") or "").lower()


def _is_xml_response(response: Optional[requests.Response]) -> bool:
    return "xml" in _response_content_type(response)


def _extract_loc_values_from_xml(xml_text: str) -> tuple[bool, list[str]]:
    soup = BeautifulSoup(xml_text or "", "xml")
    is_sitemap_index = bool(soup.find("sitemapindex"))
    loc_values: list[str] = []
    for loc_tag in soup.find_all("loc"):
        loc_text = _extract_text(loc_tag.get_text(" ", strip=True))
        if loc_text:
            loc_values.append(loc_text)
    return is_sitemap_index, loc_values


def _collect_urls_from_sitemap(
    session: requests.Session,
    *,
    sitemap_url: str,
    root_host: str,
    stop_check: Optional[Callable[[], bool]],
    max_urls: int = MAX_SITEMAP_URLS_DEFAULT,
) -> SitemapURLResult:
    normalized_root_sitemap = _normalize_url(sitemap_url)
    pending_sitemaps: deque[str] = deque([normalized_root_sitemap])
    visited_sitemaps: set[str] = set()
    collected_urls: set[str] = set()
    root_response_received = False
    root_status_code = 0
    root_is_xml = False

    while pending_sitemaps and len(collected_urls) < max_urls:
        _check_cancelled(stop_check)
        current_sitemap = pending_sitemaps.popleft()
        if current_sitemap in visited_sitemaps:
            continue
        visited_sitemaps.add(current_sitemap)

        if not _is_internal_url(current_sitemap, root_host):
            continue

        fetch = _fetch_url(session, current_sitemap, stop_check)
        response = fetch.response
        if current_sitemap == normalized_root_sitemap:
            root_response_received = bool(response)
            root_status_code = int(getattr(response, "status_code", 0) or 0) if response else 0
            root_is_xml = _is_xml_response(response)

        if not response:
            continue

        status_code = int(getattr(response, "status_code", 0) or 0)
        if status_code != 200:
            continue

        if not _is_xml_response(response):
            continue

        xml_text = _prepare_response_text(response)
        is_sitemap_index, loc_values = _extract_loc_values_from_xml(xml_text)

        if is_sitemap_index:
            for loc in loc_values:
                nested_sitemap = _normalize_url(loc)
                if not nested_sitemap:
                    continue
                if not _is_internal_url(nested_sitemap, root_host):
                    continue
                nested_path = (urlparse(nested_sitemap).path or "").lower()
                if not nested_path.endswith(".xml"):
                    continue
                if nested_sitemap not in visited_sitemaps:
                    pending_sitemaps.append(nested_sitemap)
            continue

        for loc in loc_values:
            candidate = _normalize_url(loc)
            if not candidate:
                continue
            if not _is_internal_url(candidate, root_host):
                continue
            if _should_skip_url(candidate):
                continue
            collected_urls.add(candidate)
            if len(collected_urls) >= max_urls:
                break

    return SitemapURLResult(
        response_received=root_response_received,
        status_code=root_status_code,
        is_xml=root_is_xml,
        urls=sorted(collected_urls),
    )


def _create_issue(page: SEOPage, issue_type: str, severity: str, recommendation: Optional[str] = None) -> None:
    SEOIssue.objects.create(
        page=page,
        issue_type=issue_type,
        severity=severity,
        recommendation=_extract_text(recommendation) or get_issue_recommendation(issue_type),
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
            "ttfb_ms": 0,
            "html_size_bytes": 0,
            "js_files_count": 0,
            "css_files_count": 0,
            "images_count": 0,
            "total_js_bytes": 0,
            "total_css_bytes": 0,
            "total_image_bytes": 0,
            "performance_score": 0,
            "speed_status": SEOPage.SpeedStatus.UNKNOWN,
            "title": "",
            "title_length": 0,
            "description": "",
            "description_length": 0,
            "h1": "",
            "h1_count": 0,
            "word_count": 0,
            "meta_robots": "",
            "canonical_url": "",
            "indexability_status": SEOPage.IndexabilityStatus.UNKNOWN,
            "in_sitemap": False,
            "blocked_by_robots": False,
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


def _extract_resource_urls(soup: Optional[BeautifulSoup], page_url: str) -> tuple[list[str], list[str], list[str]]:
    if not soup:
        return [], [], []

    js_urls: list[str] = []
    css_urls: list[str] = []
    image_urls: list[str] = []

    for tag in soup.find_all("script", src=True):
        src = _normalize_resource_url(tag.get("src"), page_url)
        if src:
            js_urls.append(src)

    for tag in soup.find_all("link", href=True):
        rel_values = tag.get("rel")
        rel_list = [str(item).strip().lower() for item in (rel_values if isinstance(rel_values, list) else [rel_values])]
        if "stylesheet" not in rel_list:
            continue
        href = _normalize_resource_url(tag.get("href"), page_url)
        if href:
            css_urls.append(href)

    for tag in soup.find_all("img"):
        src = _normalize_resource_url(tag.get("src"), page_url)
        if src:
            image_urls.append(src)
        srcset = _extract_text(tag.get("srcset"))
        if not srcset:
            continue
        for part in srcset.split(","):
            url_part = _extract_text(part.split(" ", 1)[0])
            candidate = _normalize_resource_url(url_part, page_url)
            if candidate:
                image_urls.append(candidate)

    return sorted(set(js_urls)), sorted(set(css_urls)), sorted(set(image_urls))


def _safe_content_length(headers: dict) -> Optional[int]:
    value = str((headers or {}).get("Content-Length") or "").strip()
    if not value.isdigit():
        return None
    try:
        parsed = int(value)
    except Exception:
        return None
    return max(0, parsed)


def _fetch_resource_size_bytes(
    session: requests.Session,
    resource_url: str,
    *,
    resource_size_cache: dict[str, Optional[int]],
    resource_fetch_state: dict[str, int],
    stop_check: Optional[Callable[[], bool]],
) -> Optional[int]:
    if resource_url in resource_size_cache:
        return resource_size_cache[resource_url]

    if resource_fetch_state.get("remaining", 0) <= 0:
        resource_size_cache[resource_url] = None
        return None

    _check_cancelled(stop_check)
    size: Optional[int] = None

    try:
        resource_fetch_state["remaining"] = max(0, resource_fetch_state["remaining"] - 1)
        head_response = session.head(resource_url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True)
        if int(getattr(head_response, "status_code", 0) or 0) < 400:
            size = _safe_content_length(getattr(head_response, "headers", {}) or {})
    except requests.RequestException:
        size = None

    if size is None and resource_fetch_state.get("remaining", 0) > 0:
        try:
            _check_cancelled(stop_check)
            resource_fetch_state["remaining"] = max(0, resource_fetch_state["remaining"] - 1)
            response = session.get(resource_url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True)
            if int(getattr(response, "status_code", 0) or 0) < 400:
                size = _response_size_bytes(response)
        except requests.RequestException:
            size = None

    resource_size_cache[resource_url] = size
    return size


def _collect_resource_metrics(
    session: requests.Session,
    *,
    soup: Optional[BeautifulSoup],
    page_url: str,
    resource_size_cache: dict[str, Optional[int]],
    resource_fetch_state: dict[str, int],
    stop_check: Optional[Callable[[], bool]],
) -> dict[str, int]:
    js_urls, css_urls, image_urls = _extract_resource_urls(soup, page_url)
    total_js_bytes = 0
    total_css_bytes = 0
    total_image_bytes = 0

    for url in js_urls:
        size = _fetch_resource_size_bytes(
            session,
            url,
            resource_size_cache=resource_size_cache,
            resource_fetch_state=resource_fetch_state,
            stop_check=stop_check,
        )
        if size is not None:
            total_js_bytes += max(0, int(size))

    for url in css_urls:
        size = _fetch_resource_size_bytes(
            session,
            url,
            resource_size_cache=resource_size_cache,
            resource_fetch_state=resource_fetch_state,
            stop_check=stop_check,
        )
        if size is not None:
            total_css_bytes += max(0, int(size))

    for url in image_urls:
        size = _fetch_resource_size_bytes(
            session,
            url,
            resource_size_cache=resource_size_cache,
            resource_fetch_state=resource_fetch_state,
            stop_check=stop_check,
        )
        if size is not None:
            total_image_bytes += max(0, int(size))

    return {
        "js_files_count": len(js_urls),
        "css_files_count": len(css_urls),
        "images_count": len(image_urls),
        "total_js_bytes": total_js_bytes,
        "total_css_bytes": total_css_bytes,
        "total_image_bytes": total_image_bytes,
    }


def _calculate_speed_score(
    *,
    ttfb_ms: int,
    html_size_bytes: int,
    js_files_count: int,
    css_files_count: int,
    images_count: int,
    total_js_bytes: int,
    total_css_bytes: int,
    total_image_bytes: int,
) -> tuple[int, str]:
    total_page_payload = html_size_bytes + total_js_bytes + total_css_bytes + total_image_bytes
    penalty = 0

    if ttfb_ms >= 1800:
        penalty += 25
    elif ttfb_ms >= 900:
        penalty += 12

    if html_size_bytes >= 700 * 1024:
        penalty += 18
    elif html_size_bytes >= 250 * 1024:
        penalty += 8

    if js_files_count >= 20:
        penalty += 16
    elif js_files_count >= 12:
        penalty += 8

    if css_files_count >= 12:
        penalty += 12
    elif css_files_count >= 6:
        penalty += 6

    if images_count >= 60:
        penalty += 12
    elif images_count >= 30:
        penalty += 6

    if total_js_bytes >= 1800 * 1024:
        penalty += 16
    elif total_js_bytes >= 900 * 1024:
        penalty += 8

    if total_css_bytes >= 700 * 1024:
        penalty += 12
    elif total_css_bytes >= 300 * 1024:
        penalty += 6

    if total_image_bytes >= 5 * 1024 * 1024:
        penalty += 16
    elif total_image_bytes >= int(2.5 * 1024 * 1024):
        penalty += 8

    if total_page_payload >= 6 * 1024 * 1024:
        penalty += 20
    elif total_page_payload >= 3 * 1024 * 1024:
        penalty += 10

    score = max(0, 100 - penalty)
    if score >= 75:
        return score, SEOPage.SpeedStatus.GOOD
    if score >= 45:
        return score, SEOPage.SpeedStatus.WARNING
    return score, SEOPage.SpeedStatus.CRITICAL


def _normalize_text(value: str) -> str:
    return _extract_text(value).strip().lower()


def _tag_attr_probe(tag) -> str:
    if tag is None:
        return ""
    parts: list[str] = []
    for key in ("id", "class", "name", "role"):
        raw = tag.get(key)
        if isinstance(raw, list):
            parts.extend(str(item) for item in raw if item)
        elif raw:
            parts.append(str(raw))
    return _normalize_text(" ".join(parts))


def _contains_any(text: str, hints: tuple[str, ...]) -> bool:
    probe = _normalize_text(text)
    if not probe:
        return False
    return any(item in probe for item in hints)


def _collect_commercial_signals(soup: Optional[BeautifulSoup]) -> dict[str, bool]:
    if not soup:
        return {
            "has_form": False,
            "has_cta": False,
            "has_phone_or_contact": False,
            "has_messenger": False,
            "has_offer_like_heading": False,
            "has_benefits_block": False,
            "has_faq": False,
        }

    text_body = _normalize_text(soup.get_text(" ", strip=True))
    has_form = bool(soup.find("form"))
    has_submit = bool(soup.find("button", attrs={"type": lambda v: str(v or "").strip().lower() == "submit"}))
    has_submit = has_submit or bool(soup.find("input", attrs={"type": lambda v: str(v or "").strip().lower() == "submit"}))
    if has_submit:
        has_form = True

    has_cta = False
    for tag in soup.find_all(["a", "button", "input"]):
        tag_text = ""
        if tag.name == "input":
            tag_text = str(tag.get("value") or "")
        else:
            tag_text = str(tag.get_text(" ", strip=True) or "")
        if _contains_any(tag_text, CTA_TEXT_HINTS) or _contains_any(_tag_attr_probe(tag), CTA_ATTR_HINTS):
            has_cta = True
            break

    has_phone_or_contact = bool(soup.find("a", href=lambda v: str(v or "").strip().lower().startswith("tel:")))
    has_phone_or_contact = has_phone_or_contact or bool(
        soup.find("a", href=lambda v: str(v or "").strip().lower().startswith("mailto:"))
    )
    has_phone_or_contact = has_phone_or_contact or bool(PHONE_RE.search(text_body))
    has_phone_or_contact = has_phone_or_contact or _contains_any(text_body, ("контакт", "contact", "связаться"))

    has_messenger = bool(
        soup.find("a", href=lambda v: _contains_any(str(v or ""), MESSENGER_HINTS))
    )

    heading_texts = []
    for tag in soup.find_all(["h1", "h2"])[:4]:
        heading_texts.append(str(tag.get_text(" ", strip=True) or ""))
    has_offer_like_heading = _contains_any(" ".join(heading_texts), OFFER_HINTS)

    has_benefits_block = False
    for tag in soup.find_all(["section", "div", "ul", "ol"]):
        probe = f"{_tag_attr_probe(tag)} {_normalize_text(tag.get_text(' ', strip=True))}"
        if _contains_any(probe, BENEFITS_HINTS):
            has_benefits_block = True
            break
    if not has_benefits_block:
        list_items = soup.find_all("li")
        if len(list_items) >= 4:
            has_benefits_block = True

    has_faq = False
    for tag in soup.find_all(["section", "div", "details", "summary", "h2", "h3"]):
        probe = f"{_tag_attr_probe(tag)} {_normalize_text(tag.get_text(' ', strip=True))}"
        if _contains_any(probe, FAQ_HINTS):
            has_faq = True
            break

    return {
        "has_form": has_form,
        "has_cta": has_cta,
        "has_phone_or_contact": has_phone_or_contact,
        "has_messenger": has_messenger,
        "has_offer_like_heading": has_offer_like_heading,
        "has_benefits_block": has_benefits_block,
        "has_faq": has_faq,
    }


def _score_commercial_signals(signals: dict[str, bool]) -> tuple[int, str]:
    score = 0
    score += 28 if signals.get("has_form") else 0
    score += 20 if signals.get("has_cta") else 0
    score += 16 if signals.get("has_phone_or_contact") else 0
    score += 8 if signals.get("has_messenger") else 0
    score += 12 if signals.get("has_offer_like_heading") else 0
    score += 10 if signals.get("has_benefits_block") else 0
    score += 6 if signals.get("has_faq") else 0
    score = max(0, min(100, int(score)))
    if score >= 70:
        return score, SEOPage.CommercialStatus.GOOD
    if score >= 40:
        return score, SEOPage.CommercialStatus.WARNING
    return score, SEOPage.CommercialStatus.CRITICAL


def _update_page_commercial_fields(page: SEOPage, signals: dict[str, bool], score: int, status: str) -> None:
    page.has_form = bool(signals.get("has_form"))
    page.has_cta = bool(signals.get("has_cta"))
    page.has_phone_or_contact = bool(signals.get("has_phone_or_contact"))
    page.has_messenger = bool(signals.get("has_messenger"))
    page.has_offer_like_heading = bool(signals.get("has_offer_like_heading"))
    page.has_benefits_block = bool(signals.get("has_benefits_block"))
    page.has_faq = bool(signals.get("has_faq"))
    page.commercial_readiness_score = int(score or 0)
    page.commercial_status = str(status or SEOPage.CommercialStatus.WARNING)
    page.save(
        update_fields=[
            "has_form",
            "has_cta",
            "has_phone_or_contact",
            "has_messenger",
            "has_offer_like_heading",
            "has_benefits_block",
            "has_faq",
            "commercial_readiness_score",
            "commercial_status",
        ]
    )


def _analyze_page_content(
    page: SEOPage,
    *,
    requested_url: str,
    final_url: str,
    status_code: int,
    elapsed_seconds: float,
    size_bytes: int,
    ttfb_ms: int,
    response: Optional[requests.Response],
    soup: Optional[BeautifulSoup],
) -> None:
    commercial_signals = _collect_commercial_signals(soup if status_code == 200 else None)
    commercial_score, commercial_status = _score_commercial_signals(commercial_signals)
    _update_page_commercial_fields(page, commercial_signals, commercial_score, commercial_status)

    if status_code != 200:
        _create_issue(page, "bad_status", SEOIssue.Severity.HIGH)

    history = list(getattr(response, "history", []) or []) if response is not None else []
    if history or (_normalize_url(final_url) and _normalize_url(final_url) != _normalize_url(requested_url)):
        _create_issue(page, "redirect", SEOIssue.Severity.LOW)

    if elapsed_seconds > SLOW_RESPONSE_SECONDS:
        _create_issue(page, "slow_response", SEOIssue.Severity.MEDIUM)

    if size_bytes > MAX_PAGE_BYTES:
        _create_issue(page, "large_page_size", SEOIssue.Severity.MEDIUM)

    if ttfb_ms >= 1800:
        _create_issue(page, "slow_ttfb", SEOIssue.Severity.HIGH)
    elif ttfb_ms >= 900:
        _create_issue(page, "slow_ttfb", SEOIssue.Severity.MEDIUM)

    if page.html_size_bytes >= 700 * 1024:
        _create_issue(page, "large_html_size", SEOIssue.Severity.MEDIUM)
    elif page.html_size_bytes >= 250 * 1024:
        _create_issue(page, "large_html_size", SEOIssue.Severity.LOW)

    if page.js_files_count >= 20:
        _create_issue(page, "too_many_js", SEOIssue.Severity.MEDIUM)
    elif page.js_files_count >= 12:
        _create_issue(page, "too_many_js", SEOIssue.Severity.LOW)

    if page.css_files_count >= 12:
        _create_issue(page, "too_many_css", SEOIssue.Severity.MEDIUM)
    elif page.css_files_count >= 6:
        _create_issue(page, "too_many_css", SEOIssue.Severity.LOW)

    if page.images_count >= 60:
        _create_issue(page, "too_many_images", SEOIssue.Severity.MEDIUM)
    elif page.images_count >= 30:
        _create_issue(page, "too_many_images", SEOIssue.Severity.LOW)

    if page.total_js_bytes >= 1800 * 1024:
        _create_issue(page, "heavy_js_payload", SEOIssue.Severity.HIGH)
    elif page.total_js_bytes >= 900 * 1024:
        _create_issue(page, "heavy_js_payload", SEOIssue.Severity.MEDIUM)

    if page.total_css_bytes >= 700 * 1024:
        _create_issue(page, "heavy_css_payload", SEOIssue.Severity.MEDIUM)
    elif page.total_css_bytes >= 300 * 1024:
        _create_issue(page, "heavy_css_payload", SEOIssue.Severity.LOW)

    if page.total_image_bytes >= 5 * 1024 * 1024:
        _create_issue(page, "heavy_images_payload", SEOIssue.Severity.MEDIUM)
    elif page.total_image_bytes >= int(2.5 * 1024 * 1024):
        _create_issue(page, "heavy_images_payload", SEOIssue.Severity.LOW)

    total_payload = page.html_size_bytes + page.total_js_bytes + page.total_css_bytes + page.total_image_bytes
    if total_payload >= 6 * 1024 * 1024:
        _create_issue(page, "heavy_page_payload", SEOIssue.Severity.HIGH)
    elif total_payload >= 3 * 1024 * 1024:
        _create_issue(page, "heavy_page_payload", SEOIssue.Severity.MEDIUM)

    if status_code != 200:
        return
    if not soup:
        return

    title = page.title or ""
    if not title:
        _create_issue(page, "missing_title", SEOIssue.Severity.HIGH)
    elif len(title) < 15:
        _create_issue(page, "title_too_short", SEOIssue.Severity.MEDIUM)
    elif len(title) > 65:
        _create_issue(page, "title_too_long", SEOIssue.Severity.MEDIUM)

    description = page.description or ""
    if not description:
        _create_issue(page, "missing_description", SEOIssue.Severity.MEDIUM)
    elif len(description) < 50:
        _create_issue(page, "description_too_short", SEOIssue.Severity.LOW)
    elif len(description) > 160:
        _create_issue(page, "description_too_long", SEOIssue.Severity.LOW)

    h1_values = _extract_h1_values(soup)
    if not h1_values:
        _create_issue(page, "missing_h1", SEOIssue.Severity.MEDIUM)
    if len(h1_values) > 1:
        _create_issue(page, "multiple_h1", SEOIssue.Severity.MEDIUM)
    if any(len(h1) > 70 for h1 in h1_values):
        _create_issue(page, "long_h1", SEOIssue.Severity.LOW)

    if _heading_hierarchy_gap(soup):
        _create_issue(page, "heading_hierarchy_gap", SEOIssue.Severity.LOW)

    if page.word_count < 300:
        _create_issue(page, "low_word_count", SEOIssue.Severity.LOW)

    missing_alt = 0
    empty_alt = 0
    for img in soup.find_all("img"):
        if not img.has_attr("alt"):
            missing_alt += 1
            continue
        if not _extract_text(img.get("alt")):
            empty_alt += 1
    if missing_alt:
        _create_issue(page, "image_missing_alt", SEOIssue.Severity.LOW)
    if empty_alt:
        _create_issue(page, "image_empty_alt", SEOIssue.Severity.LOW)

    if not page.meta_robots:
        _create_issue(page, "missing_meta_robots", SEOIssue.Severity.LOW)

    if not _extract_meta_content(soup, "viewport"):
        _create_issue(page, "missing_viewport", SEOIssue.Severity.LOW)

    if not _has_meta_charset(soup):
        _create_issue(page, "missing_charset", SEOIssue.Severity.LOW)


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
            _create_issue(page, "duplicate_title", SEOIssue.Severity.MEDIUM)


def _parse_robots_txt(robots_text: str) -> tuple[list[RobotsRule], bool, list[str]]:
    rules: list[RobotsRule] = []
    disallow_all = False
    sitemap_urls: list[str] = []
    current_ua_is_all = False

    for raw_line in str(robots_text or "").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "user-agent":
            current_ua_is_all = value.lower() == "*"
            continue

        if key == "sitemap" and value:
            sitemap_urls.append(value)
            continue

        if not current_ua_is_all:
            continue

        if key not in ("allow", "disallow"):
            continue
        if key == "disallow" and not value:
            continue
        normalized = value.split("*", 1)[0].strip() or "/"
        if normalized and not normalized.startswith("/"):
            normalized = f"/{normalized}"
        allow_rule = key == "allow"
        rules.append(RobotsRule(allow=allow_rule, path=normalized))
        if (not allow_rule) and normalized == "/":
            disallow_all = True

    return rules, disallow_all, sitemap_urls


def _is_blocked_by_robots(url: str, rules: list[RobotsRule]) -> bool:
    if not rules:
        return False
    path = urlparse(url).path or "/"
    matched: Optional[RobotsRule] = None
    for rule in rules:
        rule_path = str(rule.path or "").strip()
        if not rule_path:
            continue
        if not path.startswith(rule_path):
            continue
        if matched is None or len(rule_path) > len(matched.path):
            matched = rule
        elif matched and len(rule_path) == len(matched.path) and rule.allow:
            matched = rule
    if matched is None:
        return False
    return not bool(matched.allow)


def _build_indexing_context(
    audit: SiteSEOAudit,
    session: requests.Session,
    *,
    start_url: str,
    root_host: str,
    page_by_url: dict[str, SEOPage],
    stop_check: Optional[Callable[[], bool]],
) -> IndexingContext:
    _check_cancelled(stop_check)
    anchor_page = _get_anchor_page(audit, page_by_url, start_url)
    root_base = _normalize_url(start_url)
    robots_url = urljoin(root_base, "/robots.txt")

    has_robots_txt = False
    robots_disallow_all = False
    robots_rules: list[RobotsRule] = []
    sitemap_candidates: list[str] = []

    robots_result = _fetch_url(session, robots_url, stop_check)
    robots_response = robots_result.response
    if not robots_response or int(getattr(robots_response, "status_code", 0) or 0) != 200:
        _create_issue(anchor_page, "missing_robots_txt", SEOIssue.Severity.LOW)
    else:
        has_robots_txt = True
        robots_text = _prepare_response_text(robots_response)
        robots_rules, robots_disallow_all, sitemap_candidates = _parse_robots_txt(robots_text)
        if robots_disallow_all:
            _create_issue(anchor_page, "robots_disallow_all", SEOIssue.Severity.HIGH)
        if not sitemap_candidates:
            _create_issue(anchor_page, "robots_missing_sitemap", SEOIssue.Severity.LOW)

    if not sitemap_candidates:
        sitemap_candidates = [urljoin(root_base, "/sitemap.xml")]

    sitemap_url = ""
    for candidate in sitemap_candidates:
        normalized = _normalize_url(urljoin(root_base, candidate))
        if _is_internal_url(normalized, root_host):
            sitemap_url = normalized
            break
    if not sitemap_url:
        sitemap_url = _normalize_url(urljoin(root_base, "/sitemap.xml"))

    _check_cancelled(stop_check)
    sitemap_result = _collect_urls_from_sitemap(
        session,
        sitemap_url=sitemap_url,
        root_host=root_host,
        stop_check=stop_check,
        max_urls=MAX_SITEMAP_URLS_DEFAULT,
    )
    has_sitemap_xml = bool(
        sitemap_result.response_received and sitemap_result.status_code == 200 and sitemap_result.is_xml
    )

    if not sitemap_result.response_received:
        _create_issue(anchor_page, "missing_sitemap", SEOIssue.Severity.MEDIUM)
    elif sitemap_result.status_code != 200:
        _create_issue(anchor_page, "bad_sitemap_status", SEOIssue.Severity.MEDIUM)
    elif not sitemap_result.is_xml or not sitemap_result.urls:
        _create_issue(anchor_page, "missing_sitemap", SEOIssue.Severity.MEDIUM)

    sitemap_urls = set(sitemap_result.urls if has_sitemap_xml else [])

    return IndexingContext(
        anchor_page=anchor_page,
        has_robots_txt=has_robots_txt,
        has_sitemap_xml=has_sitemap_xml,
        robots_disallow_all=robots_disallow_all,
        robots_rules=robots_rules,
        sitemap_urls=sitemap_urls,
        sitemap_response_received=sitemap_result.response_received,
        sitemap_status_code=sitemap_result.status_code,
        sitemap_is_xml=sitemap_result.is_xml,
    )


def _is_valid_canonical_url(canonical_url: str) -> bool:
    parsed = urlparse(str(canonical_url or "").strip())
    return parsed.scheme in ("http", "https") and bool(parsed.hostname)


def _apply_indexing_page_checks(
    audit: SiteSEOAudit,
    *,
    context: IndexingContext,
    crawled_urls: set[str],
) -> None:
    pages = SEOPage.objects.filter(audit=audit).order_by("id")
    normalized_crawled_urls = {_normalize_url(url) for url in crawled_urls if url}

    if context.has_sitemap_xml and context.sitemap_urls and normalized_crawled_urls:
        overlap_count = len(normalized_crawled_urls & context.sitemap_urls)
        if overlap_count < len(normalized_crawled_urls):
            _create_issue(context.anchor_page, "sitemap_mismatch", SEOIssue.Severity.LOW)

    for page in pages:
        normalized_page_url = _normalize_url(page.url)
        in_sitemap = bool(context.has_sitemap_xml and context.sitemap_urls and normalized_page_url in context.sitemap_urls)
        blocked_by_robots = bool(context.has_robots_txt and _is_blocked_by_robots(page.url, context.robots_rules))
        meta_robots = str(page.meta_robots or "").strip().lower()
        tokens = {token.strip() for token in meta_robots.split(",") if token.strip()}
        has_noindex = "noindex" in tokens or "none" in tokens
        has_nofollow = "nofollow" in tokens or "none" in tokens

        canonical_url = str(page.canonical_url or "").strip()
        has_canonical = bool(canonical_url)
        canonical_valid = bool(has_canonical and _is_valid_canonical_url(canonical_url))
        canonical_conflict = bool(
            has_noindex and canonical_valid and _normalize_url(canonical_url) != normalized_page_url
        )

        if page.status_code == 200:
            if has_noindex:
                _create_issue(page, "page_noindex", SEOIssue.Severity.MEDIUM)
            if has_nofollow:
                _create_issue(page, "page_nofollow", SEOIssue.Severity.LOW)

            if not has_canonical:
                _create_issue(page, "missing_canonical", SEOIssue.Severity.LOW)
            elif not canonical_valid:
                _create_issue(page, "invalid_canonical", SEOIssue.Severity.MEDIUM)

            if canonical_conflict:
                _create_issue(page, "canonical_conflict", SEOIssue.Severity.MEDIUM)

            if blocked_by_robots:
                _create_issue(page, "blocked_by_robots", SEOIssue.Severity.HIGH)

            if context.has_sitemap_xml and context.sitemap_urls and not in_sitemap:
                _create_issue(page, "sitemap_page_missing", SEOIssue.Severity.LOW)

        if blocked_by_robots:
            indexability_status = SEOPage.IndexabilityStatus.BLOCKED
        elif canonical_conflict:
            indexability_status = SEOPage.IndexabilityStatus.CONFLICT
        elif has_noindex:
            indexability_status = SEOPage.IndexabilityStatus.NOINDEX
        elif page.status_code == 200:
            indexability_status = SEOPage.IndexabilityStatus.INDEXABLE
        else:
            indexability_status = SEOPage.IndexabilityStatus.UNKNOWN

        page.in_sitemap = in_sitemap
        page.blocked_by_robots = blocked_by_robots
        page.indexability_status = indexability_status
        page.save(update_fields=["in_sitemap", "blocked_by_robots", "indexability_status"])


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

    pages_qs = SEOPage.objects.filter(audit=audit)
    avg_ttfb = pages_qs.filter(ttfb_ms__gt=0).aggregate(value=Avg("ttfb_ms")).get("value") or 0
    avg_performance = pages_qs.filter(performance_score__gt=0).aggregate(value=Avg("performance_score")).get("value") or 0

    pages_with_speed_issues = (
        SEOIssue.objects.filter(page__audit=audit, issue_type__in=SPEED_ISSUE_TYPES)
        .values("page_id")
        .distinct()
        .count()
    )
    pages_with_indexing_issues = (
        SEOIssue.objects.filter(page__audit=audit, issue_type__in=INDEXING_ISSUE_TYPES)
        .values("page_id")
        .distinct()
        .count()
    )

    audit.seo_score = score
    audit.pages_count = pages_qs.count()
    audit.avg_ttfb_ms = int(round(avg_ttfb)) if avg_ttfb else 0
    audit.avg_performance_score = int(round(avg_performance)) if avg_performance else 0
    audit.pages_with_speed_issues = int(pages_with_speed_issues or 0)
    audit.pages_with_indexing_issues = int(pages_with_indexing_issues or 0)
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
        raise ValueError("Не указан домен для SEO-аудита.")

    link_crawl_limit = max_pages or MAX_PAGES_DEFAULT
    sitemap_crawl_limit = min(max_pages or MAX_SITEMAP_URLS_DEFAULT, MAX_SITEMAP_URLS_DEFAULT)
    root_host = urlparse(start_url).hostname or audit.domain
    local_session = session or requests.Session()
    local_session.headers.setdefault("User-Agent", "TrackNode SEO Audit/1.0 (+https://tracknode.local)")

    _check_cancelled(stop_check)

    # Повторный запуск аудита должен заменять старые результаты, а не дублировать страницы и ошибки.
    audit.pages.all().delete()
    audit.used_sitemap = False
    audit.sitemap_urls_count = 0
    audit.has_robots_txt = False
    audit.has_sitemap_xml = False
    audit.avg_ttfb_ms = 0
    audit.avg_performance_score = 0
    audit.pages_with_speed_issues = 0
    audit.pages_with_indexing_issues = 0
    audit.save(
        update_fields=[
            "used_sitemap",
            "sitemap_urls_count",
            "has_robots_txt",
            "has_sitemap_xml",
            "avg_ttfb_ms",
            "avg_performance_score",
            "pages_with_speed_issues",
            "pages_with_indexing_issues",
        ]
    )

    page_by_url: dict[str, SEOPage] = {}
    indexing_context = _build_indexing_context(
        audit,
        local_session,
        start_url=start_url,
        root_host=root_host,
        page_by_url=page_by_url,
        stop_check=stop_check,
    )

    crawl_uses_sitemap = bool(indexing_context.has_sitemap_xml and indexing_context.sitemap_urls)
    if crawl_uses_sitemap:
        queue: deque[str] = deque(sorted(indexing_context.sitemap_urls)[:sitemap_crawl_limit])
        crawl_limit = sitemap_crawl_limit
        audit.used_sitemap = True
    else:
        queue = deque([_normalize_url(start_url)])
        crawl_limit = link_crawl_limit

    audit.has_robots_txt = bool(indexing_context.has_robots_txt)
    audit.has_sitemap_xml = bool(indexing_context.has_sitemap_xml)
    audit.sitemap_urls_count = len(indexing_context.sitemap_urls)
    audit.save(update_fields=["used_sitemap", "has_robots_txt", "has_sitemap_xml", "sitemap_urls_count"])

    queued: set[str] = set(queue)
    visited: set[str] = set()
    crawled_urls: set[str] = set()
    resource_size_cache: dict[str, Optional[int]] = {}
    resource_fetch_state = {"remaining": MAX_RESOURCE_FETCH_BUDGET}

    while queue and len(visited) < crawl_limit:
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
                    "ttfb_ms": fetch.ttfb_ms,
                    "html_size_bytes": 0,
                    "js_files_count": 0,
                    "css_files_count": 0,
                    "images_count": 0,
                    "total_js_bytes": 0,
                    "total_css_bytes": 0,
                    "total_image_bytes": 0,
                    "performance_score": 0,
                    "speed_status": SEOPage.SpeedStatus.CRITICAL,
                    "title": "",
                    "title_length": 0,
                    "description": "",
                    "description_length": 0,
                    "h1": "",
                    "h1_count": 0,
                    "word_count": 0,
                    "meta_robots": "",
                    "canonical_url": "",
                    "indexability_status": SEOPage.IndexabilityStatus.UNKNOWN,
                    "in_sitemap": bool(indexing_context.sitemap_urls and requested_url in indexing_context.sitemap_urls),
                    "blocked_by_robots": bool(
                        indexing_context.has_robots_txt and _is_blocked_by_robots(requested_url, indexing_context.robots_rules)
                    ),
                },
            )
            page_by_url[requested_url] = page
            _create_issue(page, "network_error", SEOIssue.Severity.HIGH)
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
        soup = None
        title = ""
        description = ""
        h1_values: list[str] = []
        word_count = 0
        meta_robots = ""
        canonical_url = ""
        canonical_valid = False

        if is_html:
            html_text = _prepare_response_text(response)
            soup = BeautifulSoup(html_text, "lxml")
            title = _extract_title(soup)
            description = _extract_meta_content(soup, "description")
            h1_values = _extract_h1_values(soup)
            page_text = _extract_text(soup.get_text(" ", strip=True))
            word_count = _count_words(page_text)
            meta_robots = _extract_meta_content(soup, "robots")
            canonical_url, canonical_valid = _extract_canonical_url(soup, target_url)
            if canonical_url and not canonical_valid:
                canonical_url = _extract_text(canonical_url)

        resource_metrics = _collect_resource_metrics(
            local_session,
            soup=soup if status_code == 200 else None,
            page_url=target_url,
            resource_size_cache=resource_size_cache,
            resource_fetch_state=resource_fetch_state,
            stop_check=stop_check,
        )
        performance_score, speed_status = _calculate_speed_score(
            ttfb_ms=fetch.ttfb_ms,
            html_size_bytes=fetch.size_bytes,
            js_files_count=resource_metrics["js_files_count"],
            css_files_count=resource_metrics["css_files_count"],
            images_count=resource_metrics["images_count"],
            total_js_bytes=resource_metrics["total_js_bytes"],
            total_css_bytes=resource_metrics["total_css_bytes"],
            total_image_bytes=resource_metrics["total_image_bytes"],
        )

        page_defaults = {
            "status_code": status_code,
            "ttfb_ms": fetch.ttfb_ms,
            "html_size_bytes": fetch.size_bytes,
            "js_files_count": resource_metrics["js_files_count"],
            "css_files_count": resource_metrics["css_files_count"],
            "images_count": resource_metrics["images_count"],
            "total_js_bytes": resource_metrics["total_js_bytes"],
            "total_css_bytes": resource_metrics["total_css_bytes"],
            "total_image_bytes": resource_metrics["total_image_bytes"],
            "performance_score": performance_score,
            "speed_status": speed_status,
            "title": title,
            "title_length": len(title),
            "description": description,
            "description_length": len(description),
            "h1": h1_values[0] if h1_values else "",
            "h1_count": len(h1_values),
            "word_count": word_count,
            "meta_robots": meta_robots,
            "canonical_url": canonical_url,
            "indexability_status": SEOPage.IndexabilityStatus.UNKNOWN,
            "in_sitemap": bool(indexing_context.sitemap_urls and target_url in indexing_context.sitemap_urls),
            "blocked_by_robots": bool(
                indexing_context.has_robots_txt and _is_blocked_by_robots(target_url, indexing_context.robots_rules)
            ),
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
            ttfb_ms=fetch.ttfb_ms,
            response=response,
            soup=soup,
        )

        if (not crawl_uses_sitemap) and soup and status_code == 200:
            for link in _extract_internal_links(soup, target_url, root_host):
                if link in visited or link in queued:
                    continue
                if len(visited) + len(queue) >= crawl_limit:
                    break
                queue.append(link)
                queued.add(link)

    _check_cancelled(stop_check)
    _apply_duplicate_title_checks(audit)
    _apply_indexing_page_checks(audit, context=indexing_context, crawled_urls=crawled_urls)
    _check_cancelled(stop_check)
    recalculate_audit_score(audit)
    return audit
