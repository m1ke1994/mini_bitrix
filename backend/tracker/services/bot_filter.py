import re
import time
from dataclasses import dataclass, field
from functools import lru_cache
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache


_LONG_RANDOM_SEGMENT_RE = re.compile(r"^[A-Za-z0-9]{21,}$")
_BOT_UA_SUBSTRINGS = (
    "googlebot",
    "applebot",
    "bingbot",
    "headlesschrome",
    "curl",
    "python-requests",
    "wget",
)

# Keep in sync with frontend/src/router.js real pages (excluding catch-all 404 route).
_KNOWN_FRONTEND_PATHS = frozenset(
    {
        "/",
        "/analitika",
        "/otchety",
        "/telegram",
        "/tarify",
        "/auth",
        "/login",
        "/register",
        "/dashboard",
        "/dashboard/dynamics",
        "/dashboard/sources",
        "/dashboard/unique",
        "/dashboard/engagement",
        "/dashboard/clicks",
        "/dashboard/pages-conversion",
        "/dashboard/devices",
        "/dashboard/settings",
        "/dashboard/integration",
        "/settings",
        "/account",
        "/integration",
        "/reports",
        "/about",
        "/instructions",
    }
)
_DEFAULT_FRONTEND_HOSTS = frozenset({"tracknode.ru", "www.tracknode.ru", "localhost", "127.0.0.1", "tracker.local"})


@dataclass
class BotCheckResult:
    is_bot: bool = False
    reasons: list[str] = field(default_factory=list)
    request_count_5s: int | None = None
    unique_urls_10s: int | None = None

    def add_reason(self, reason: str) -> None:
        if reason not in self.reasons:
            self.reasons.append(reason)
            self.is_bot = True


def detect_bot_visit(*, site_id: int, ip_address: str | None, user_agent: str | None, tracked_url: str | None = None) -> BotCheckResult:
    result = BotCheckResult()
    ua = (user_agent or "").strip()

    if not ua:
        result.add_reason("empty_user_agent")
    else:
        ua_lower = ua.lower()
        for token in _BOT_UA_SUBSTRINGS:
            if token in ua_lower:
                result.add_reason(f"user_agent:{token}")

    now_ts = time.time()
    if ip_address:
        request_count_5s = _record_request_and_count(site_id=site_id, ip_address=ip_address, now_ts=now_ts)
        result.request_count_5s = request_count_5s
        if request_count_5s is not None and request_count_5s > 10:
            result.add_reason("request_rate_over_10_in_5s")

    parsed = _parse_tracked_url(tracked_url)
    if parsed is not None:
        path = _normalize_path(parsed.path or "/")
        if _path_has_random_long_segment(path):
            result.add_reason("path_random_segment_gt20")
        if _should_validate_against_frontend_routes(parsed) and not _path_exists_in_frontend_routes(path):
            result.add_reason("path_not_in_frontend_routes")

        if ip_address:
            normalized_url = _normalize_url_for_uniques(parsed)
            unique_urls_10s = _record_unique_url_and_count(
                site_id=site_id,
                ip_address=ip_address,
                normalized_url=normalized_url,
                now_ts=now_ts,
            )
            result.unique_urls_10s = unique_urls_10s
            if unique_urls_10s is not None and unique_urls_10s > 5:
                result.add_reason("unique_urls_over_5_in_10s")

    return result


def _parse_tracked_url(tracked_url: str | None):
    raw = (tracked_url or "").strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    if parsed.scheme and parsed.netloc:
        return parsed
    if raw.startswith("/"):
        # Relative paths can belong to arbitrary tracked sites, so route validation is skipped for them.
        return urlparse(f"https://relative.local{raw}")
    return None


def _normalize_path(path: str) -> str:
    raw = (path or "").strip() or "/"
    if not raw.startswith("/"):
        raw = f"/{raw}"
    raw = re.sub(r"/{2,}", "/", raw)
    if raw != "/" and raw.endswith("/"):
        raw = raw.rstrip("/")
    return raw or "/"


def _path_has_random_long_segment(path: str) -> bool:
    for segment in (segment for segment in (path or "").split("/") if segment):
        base = segment.split(".", 1)[0]
        if _LONG_RANDOM_SEGMENT_RE.match(base or ""):
            return True
    return False


def _path_exists_in_frontend_routes(path: str) -> bool:
    normalized = _normalize_path(path)
    return normalized in _KNOWN_FRONTEND_PATHS


def _normalize_url_for_uniques(parsed_url) -> str:
    path = _normalize_path(parsed_url.path or "/")
    query = (parsed_url.query or "").strip()
    return f"{path}?{query}" if query else path


def _cache_key(prefix: str, site_id: int, ip_address: str) -> str:
    return f"tracker:bot:{prefix}:site:{site_id}:ip:{ip_address}"


def _record_request_and_count(*, site_id: int, ip_address: str, now_ts: float) -> int | None:
    key = _cache_key("req", site_id, ip_address)
    try:
        timestamps = cache.get(key) or []
        window_start = now_ts - 5
        timestamps = [ts for ts in timestamps if ts >= window_start]
        timestamps.append(now_ts)
        cache.set(key, timestamps, timeout=30)
        return len(timestamps)
    except Exception:
        return None


def _record_unique_url_and_count(*, site_id: int, ip_address: str, normalized_url: str, now_ts: float) -> int | None:
    key = _cache_key("uniq-url", site_id, ip_address)
    try:
        items = cache.get(key) or {}
        window_start = now_ts - 10
        items = {
            str(url): float(ts)
            for url, ts in items.items()
            if isinstance(ts, (int, float)) and float(ts) >= window_start
        }
        items[normalized_url[:1024]] = now_ts
        cache.set(key, items, timeout=60)
        return len(items)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _frontend_route_hosts() -> set[str]:
    hosts = set(_DEFAULT_FRONTEND_HOSTS)
    for setting_name in ("FRONTEND_URL", "PUBLIC_BASE_URL"):
        raw = (getattr(settings, setting_name, "") or "").strip()
        if not raw:
            continue
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
        host = (parsed.hostname or "").strip().lower()
        if host:
            hosts.add(host)
    return hosts


def _should_validate_against_frontend_routes(parsed_url) -> bool:
    host = (parsed_url.hostname or "").strip().lower()
    if not host:
        return True
    return host in _frontend_route_hosts()
