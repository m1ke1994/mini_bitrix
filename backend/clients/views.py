import logging

from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from accounts.permissions import IsClientUser
from clients.serializers import ClientSettingsSerializer
from reports.models import ReportSettings

logger = logging.getLogger(__name__)


class ClientSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get_object(self):
        return self.request.client

    def _sanitize_payload(self, request) -> dict:
        raw_data = request.data if isinstance(request.data, dict) else {}
        # Hard whitelist for settings writes: ignore everything else.
        allowed_fields = {"send_to_telegram", "daily_pdf_enabled"}
        sanitized = {key: raw_data[key] for key in raw_data.keys() if key in allowed_fields}
        dropped = sorted(set(raw_data.keys()) - allowed_fields)
        if dropped:
            logger.info("Settings payload dropped read-only/unknown fields: %s", dropped)
        return sanitized

    def _build_response_data(self, instance, *, include_daily: bool = True) -> dict:
        data = dict(self.get_serializer(instance).data)
        if include_daily:
            report_settings, _ = ReportSettings.objects.get_or_create(client=instance)
            data["daily_pdf_enabled"] = report_settings.daily_pdf_enabled
        return data

    def _update_from_payload(self, request, *, partial: bool) -> Response:
        logger.info("=== SETTINGS REQUEST START ===")
        logger.info("METHOD: %s", request.method)
        logger.info("DATA: %s", request.data)
        instance = self.get_object()
        try:
            payload = self._sanitize_payload(request)

            client_updates = {}
            if "send_to_telegram" in payload:
                client_updates["send_to_telegram"] = payload["send_to_telegram"]

            if "daily_pdf_enabled" in payload:
                report_settings, _ = ReportSettings.objects.get_or_create(client=instance)
                report_settings.daily_pdf_enabled = bool(payload["daily_pdf_enabled"])
                report_settings.save(update_fields=["daily_pdf_enabled", "updated_at"])

            if not client_updates and "daily_pdf_enabled" not in payload:
                response_data = self._build_response_data(instance)
                logger.info("=== SETTINGS RESPONSE OK ===")
                logger.info("Settings response status about to return: %s", status.HTTP_200_OK)
                return Response(response_data, status=status.HTTP_200_OK)

            serializer = self.get_serializer(instance, data=client_updates, partial=partial)
            if not serializer.is_valid():
                logger.error("SETTINGS VALIDATION ERROR: %s", serializer.errors)
                response_data = self._build_response_data(instance)
                response_data["validation_errors"] = serializer.errors
                logger.info("=== SETTINGS RESPONSE OK ===")
                logger.info("Settings response status about to return: %s", status.HTTP_200_OK)
                return Response(response_data, status=status.HTTP_200_OK)

            self.perform_update(serializer)
            response_data = self._build_response_data(instance)
            logger.info("=== SETTINGS RESPONSE OK ===")
            logger.info("Settings response status about to return: %s", status.HTTP_200_OK)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("SETTINGS UNHANDLED ERROR")
            response_data = self._build_response_data(instance)
            response_data["settings_fallback"] = True
            logger.info("=== SETTINGS RESPONSE OK ===")
            logger.info("Settings response status about to return: %s", status.HTTP_200_OK)
            return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        return self._update_from_payload(request, partial=True)

    def put(self, request, *args, **kwargs):
        return self._update_from_payload(request, partial=False)

    def post(self, request, *args, **kwargs):
        return self._update_from_payload(request, partial=True)


def tracker_js_view(request):
    script = r"""
(function () {
  'use strict';

  function safeConsole(method, args) {
    try {
      if (window.console && typeof window.console[method] === 'function') {
        window.console[method].apply(window.console, args);
      }
    } catch (_) {}
  }

  function logError(message, err) {
    safeConsole('error', ['[SaaS Tracker] ' + message, err || '']);
  }

  function logDebug() {
    if (!debug) {
      return;
    }
    var args = Array.prototype.slice.call(arguments);
    args.unshift('[SaaS Tracker]');
    safeConsole('log', args);
  }

  function logWarn() {
    var args = Array.prototype.slice.call(arguments);
    args.unshift('[SaaS Tracker]');
    safeConsole('warn', args);
  }

  function asBool(value) {
    try {
      return String(value).toLowerCase() === 'true' || String(value) === '1';
    } catch (_) {
      return false;
    }
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function safeGet(storage, key) {
    try {
      return storage.getItem(key);
    } catch (_) {
      return null;
    }
  }

  function safeSet(storage, key, value) {
    try {
      storage.setItem(key, value);
    } catch (_) {}
  }

  function getScript() {
    var current = document.currentScript || null;
    try {
      if (current && current.src && current.src.indexOf('/tracker.js') !== -1) {
        return current;
      }
    } catch (_) {}

    var scripts = document.getElementsByTagName('script');
    if (!scripts || !scripts.length) {
      return current;
    }

    // Prefer tracker.js script with explicit tracker token on it.
    for (var i = scripts.length - 1; i >= 0; i--) {
      var script = scripts[i];
      if (!script || !script.src || script.src.indexOf('/tracker.js') === -1) {
        continue;
      }
      if (script.dataset && (script.dataset.token || script.dataset.apiKey)) {
        return script;
      }
    }

    // Fallback to any tracker.js script.
    for (var j = scripts.length - 1; j >= 0; j--) {
      var fallback = scripts[j];
      if (fallback && fallback.src && fallback.src.indexOf('/tracker.js') !== -1) {
        return fallback;
      }
    }

    return current || scripts[scripts.length - 1] || null;
  }

  function createUuid() {
    try {
      if (window.crypto && typeof window.crypto.randomUUID === 'function') {
        return window.crypto.randomUUID();
      }
    } catch (_) {}
    return 'sid-' + Date.now() + '-' + Math.random().toString(16).slice(2);
  }

  function getBaseUrl(scriptTag) {
    try {
      if (scriptTag && scriptTag.src) {
        return new URL(scriptTag.src).origin;
      }
    } catch (err) {
      logError('Cannot parse script src.', err);
    }
    return window.location.origin;
  }

  var scriptTag = getScript();
  var token = '';
  try {
    token = String(scriptTag && scriptTag.dataset ? (scriptTag.dataset.token || scriptTag.dataset.apiKey || '') : '').trim();
  } catch (_) {
    token = '';
  }
  var debug = false;
  try {
    debug = (
      (scriptTag && scriptTag.dataset && asBool(scriptTag.dataset.debug)) ||
      asBool(safeGet(window.localStorage, 'saas_tracker_debug')) ||
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1'
    );
  } catch (_) {
    debug = false;
  }

  logDebug('init start');

  if (!token) {
    logError('Missing tracker token. Use data-token or data-api-key.');
    return;
  }

  if (window.__saasTrackerInitializedToken === token) {
    logDebug('skip duplicate tracker init for token', token);
    return;
  }
  window.__saasTrackerInitializedToken = token;

  var baseUrl = getBaseUrl(scriptTag);
  var trackerOrigin = baseUrl;
  var originalFetch = (typeof window.fetch === 'function') ? window.fetch.bind(window) : null;
  var visitorKey = 'saas_tracker_visitor_id';
  var sessionKey = 'saas_tracker_session_id';
  var startKey = 'saas_tracker_started_at';

  var visitorId = safeGet(window.localStorage, visitorKey);
  if (!visitorId) {
    visitorId = createUuid();
    safeSet(window.localStorage, visitorKey, visitorId);
  }

  var sessionId = safeGet(window.sessionStorage, sessionKey);
  if (!sessionId) {
    sessionId = createUuid();
    safeSet(window.sessionStorage, sessionKey, sessionId);
  }
  logDebug('visitor/session ready', visitorId, sessionId);

  var startedAt = safeGet(window.sessionStorage, startKey);
  if (!startedAt) {
    startedAt = nowIso();
    safeSet(window.sessionStorage, startKey, startedAt);
  }
  logDebug('visit started_at', startedAt);

  var sentPageviewFingerprint = '';
  var pageTrackPath = '/';
  var pageTrackStartedAt = Date.now();
  var pageTrackSent = false;
  var pageTrackRouteFingerprint = '';

  function toAbsoluteUrl(input) {
    if (!input) {
      return '';
    }
    try {
      return new URL(String(input), window.location.href).toString();
    } catch (_) {
      return '';
    }
  }

  function requestMethodOrDefault(method) {
    return ((method || 'GET') + '').toUpperCase();
  }

  function shouldTrackApiRequest(urlValue, method) {
    var absolute = toAbsoluteUrl(urlValue);
    if (!absolute) {
      return false;
    }
    try {
      var parsed = new URL(absolute);
      var pathname = parsed.pathname || '';
      if (pathname.indexOf('/api/') === -1) {
        return false;
      }
      if (parsed.origin === trackerOrigin && pathname.indexOf('/api/track/') === 0) {
        return false;
      }
      return requestMethodOrDefault(method) !== 'OPTIONS';
    } catch (_) {
      return false;
    }
  }

  function extractFetchUrl(input) {
    if (!input) {
      return '';
    }
    if (typeof input === 'string') {
      return toAbsoluteUrl(input);
    }
    try {
      if (input.url) {
        return toAbsoluteUrl(input.url);
      }
      if (input.href) {
        return toAbsoluteUrl(input.href);
      }
    } catch (_) {}
    return '';
  }

  function extractFetchMethod(input, init) {
    try {
      if (init && init.method) {
        return requestMethodOrDefault(init.method);
      }
      if (input && input.method) {
        return requestMethodOrDefault(input.method);
      }
    } catch (_) {}
    return 'GET';
  }

  function extractSafeFormFields(form) {
    if (!form || !form.elements) {
      return [];
    }
    var fields = [];
    var seen = {};
    var sensitiveNamePattern = /(pass|password|pwd|token|secret|key|card|cvv|cvc|iban|email|phone|tel|cookie|session)/i;
    for (var i = 0; i < form.elements.length; i++) {
      var field = form.elements[i];
      if (!field || field.disabled) {
        continue;
      }
      var fieldType = ((field.type || field.tagName || '') + '').toLowerCase();
      if (fieldType === 'password' || fieldType === 'hidden' || fieldType === 'file') {
        continue;
      }
      var rawName = (field.name || field.id || '').trim();
      if (!rawName) {
        continue;
      }
      if (sensitiveNamePattern.test(rawName)) {
        continue;
      }
      var key = (rawName + '|' + fieldType).toLowerCase();
      if (seen[key]) {
        continue;
      }
      seen[key] = true;
      fields.push({
        name: rawName.slice(0, 64),
        type: fieldType.slice(0, 32),
        checked: !!field.checked
      });
      if (fields.length >= 25) {
        break;
      }
    }
    return fields;
  }

  function buildPayload(extra) {
    var payload = {
      token: token,
      visitor_id: visitorId,
      session_id: sessionId,
      timestamp: nowIso()
    };
    if (extra && typeof extra === 'object') {
      var keys = Object.keys(extra);
      for (var i = 0; i < keys.length; i++) {
        payload[keys[i]] = extra[keys[i]];
      }
    }
    return payload;
  }

  function postWithRetry(endpoint, payload, opts) {
    var maxAttempts = (opts && opts.maxAttempts) || 3;
    var attempt = 0;
    var url = baseUrl + endpoint;

    function runAttempt() {
      attempt += 1;
      logDebug('sending', endpoint, 'attempt', attempt, payload);
      if (!originalFetch) {
        logWarn('window.fetch is unavailable, skip tracker request', endpoint);
        return Promise.resolve(null);
      }
      return originalFetch(url, {
        method: 'POST',
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
        keepalive: true
      }).then(function (response) {
        if (!response.ok) {
          var httpError = new Error('HTTP ' + response.status);
          httpError.status = response.status;
          throw httpError;
        }
        logDebug('success', endpoint, 'status', response.status);
        return response;
      }).catch(function (err) {
        logWarn('request failed', endpoint, 'attempt', attempt, err && err.message ? err.message : err);
        var statusCode = err && typeof err.status === 'number' ? err.status : 0;
        if (statusCode >= 400 && statusCode < 500 && statusCode !== 429) {
          logError('request rejected without retry: ' + endpoint, err);
          return null;
        }
        if (attempt >= maxAttempts) {
          logError('request permanently failed: ' + endpoint, err);
          return null;
        }
        return new Promise(function (resolve) {
          setTimeout(resolve, 250 * attempt);
        }).then(runAttempt);
      });
    }

    try {
      return runAttempt();
    } catch (err) {
      logError('Request init failed: ' + endpoint, err);
      return Promise.resolve();
    }
  }

  function trackVisitStart() {
    return postWithRetry('/api/track/visit-start/', buildPayload({
      type: 'visit',
      started_at: startedAt,
      referrer: document.referrer || ''
    }));
  }

  function trackPageView() {
    var fingerprint = window.location.pathname + window.location.search;
    if (fingerprint === sentPageviewFingerprint) {
      logDebug('skip duplicate pageview', fingerprint);
      return Promise.resolve();
    }
    sentPageviewFingerprint = fingerprint;
    return postWithRetry('/api/track/pageview/', buildPayload({
      url: window.location.href,
      title: document.title || '',
      timestamp: nowIso()
    }));
  }

  function trackEvent(type, payload) {
    return postWithRetry('/api/track/event/', buildPayload({
      type: type,
      payload: payload || {},
      timestamp: nowIso()
    }));
  }

  function routeFingerprint() {
    return (window.location.pathname || '/') + (window.location.search || '');
  }

  function resetPageTimer(pathname) {
    pageTrackPath = (pathname || window.location.pathname || '/');
    pageTrackStartedAt = Date.now();
    pageTrackSent = false;
    pageTrackRouteFingerprint = routeFingerprint();
    logDebug('page timer reset', pageTrackPath, pageTrackRouteFingerprint);
  }

  function buildEventPayload(type, payload) {
    return buildPayload({
      type: type,
      payload: payload || {},
      timestamp: nowIso()
    });
  }

  function sendEventPayload(payload, preferBeacon) {
    if (preferBeacon && navigator.sendBeacon) {
      try {
        var data = JSON.stringify(payload);
        var blob = new Blob([data], { type: 'application/json' });
        var ok = navigator.sendBeacon(baseUrl + '/api/track/event/', blob);
        logDebug('sendBeacon event', payload && payload.type, ok);
        if (ok) {
          return;
        }
      } catch (err) {
        logWarn('sendBeacon event failed', err && err.message ? err.message : err);
      }
    }
    postWithRetry('/api/track/event/', payload, { maxAttempts: 2 });
  }

  function flushTimeOnPage(reason, opts) {
    var options = opts || {};
    if (pageTrackSent) {
      return;
    }
    var durationSeconds = 0;
    try {
      durationSeconds = Math.floor((Date.now() - pageTrackStartedAt) / 1000);
    } catch (_) {
      durationSeconds = 0;
    }
    pageTrackSent = true;
    if (durationSeconds <= 1) {
      logDebug('skip short time_on_page', durationSeconds, pageTrackPath, reason || '');
      return;
    }
    sendEventPayload(buildEventPayload('time_on_page', {
      page: pageTrackPath || '/',
      duration_seconds: durationSeconds
    }), !!options.preferBeacon);
  }

  function handleRouteChange() {
    var nextFingerprint = routeFingerprint();
    if (nextFingerprint === pageTrackRouteFingerprint) {
      return;
    }
    flushTimeOnPage('spa_route_change');
    resetPageTimer(window.location.pathname || '/');
    setTimeout(trackPageView, 0);
  }

  function trackApiRequest(payload) {
    if (!payload || !payload.url) {
      return;
    }
    if (!shouldTrackApiRequest(payload.url, payload.method)) {
      return;
    }
    trackEvent('api_post', {
      url: payload.url,
      method: requestMethodOrDefault(payload.method),
      status: payload.status || 0,
      transport: payload.transport || 'fetch',
      page_url: window.location.href,
      path: window.location.pathname,
      domain: window.location.hostname
    });
  }

  function trackVisitEnd() {
    try {
      var endedAt = nowIso();
      var duration = 0;
      try {
        duration = Math.max(0, Math.round((Date.now() - new Date(startedAt).getTime()) / 1000));
      } catch (_) {
        duration = 0;
      }
      var payload = buildPayload({
        ended_at: endedAt,
        duration: duration
      });
      var data = JSON.stringify(payload);
      if (navigator.sendBeacon) {
        var blob = new Blob([data], { type: 'application/json' });
        var ok = navigator.sendBeacon(baseUrl + '/api/track/visit-end/', blob);
        logDebug('sendBeacon visit-end', ok);
        if (ok) {
          return;
        }
      }
      postWithRetry('/api/track/visit-end/', payload, { maxAttempts: 2 });
    } catch (err) {
      logError('visit-end failed', err);
    }
  }

  function onVisibilityChange() {
    try {
      if (document.visibilityState === 'hidden') {
        flushTimeOnPage('visibility_hidden', { preferBeacon: true });
        return;
      }
      if (document.visibilityState === 'visible') {
        resetPageTimer(window.location.pathname || '/');
      }
    } catch (err) {
      logError('visibility tracking failed', err);
    }
  }

  function onPageClose() {
    flushTimeOnPage('page_close', { preferBeacon: true });
    trackVisitEnd();
  }

  function onClick(event) {
    try {
      var node = event.target && event.target.closest ? event.target.closest('button, a, [role="button"], [data-track]') : null;
      if (!node) {
        return;
      }
      trackEvent('click', {
        tag: node.tagName || '',
        id: node.id || '',
        text: ((node.innerText || node.textContent || '') + '').trim().slice(0, 120),
        path: window.location.pathname
      });
    } catch (err) {
      logError('click tracking failed', err);
    }
  }

  function onSubmit(event) {
    try {
      var form = event.target;
      if (!form || form.tagName !== 'FORM') {
        return;
      }
      trackEvent('form_submit', {
        id: form.id || '',
        name: form.getAttribute('name') || '',
        page_url: window.location.href,
        url: window.location.href,
        domain: window.location.hostname,
        action: form.action || '',
        action_path: (function () {
          try {
            return new URL(form.action || '', window.location.href).pathname || '';
          } catch (_) {
            return '';
          }
        })(),
        method: (form.method || 'GET').toUpperCase(),
        path: window.location.pathname,
        fields: extractSafeFormFields(form),
        field_count: (form.elements && form.elements.length) ? form.elements.length : 0
      });
    } catch (err) {
      logError('submit tracking failed', err);
    }
  }

  function wrapHistory() {
    try {
      var originalPush = history.pushState;
      var originalReplace = history.replaceState;
      history.pushState = function () {
        var result = originalPush.apply(this, arguments);
        setTimeout(handleRouteChange, 0);
        return result;
      };
      history.replaceState = function () {
        var result = originalReplace.apply(this, arguments);
        setTimeout(handleRouteChange, 0);
        return result;
      };
      window.addEventListener('popstate', function () {
        handleRouteChange();
      });
    } catch (err) {
      logError('history tracking failed', err);
    }
  }

  function installFetchInterceptor() {
    if (!originalFetch) {
      return;
    }
    window.fetch = function (input, init) {
      var requestUrl = extractFetchUrl(input);
      var requestMethod = extractFetchMethod(input, init);
      return originalFetch.apply(this, arguments)
        .then(function (response) {
          trackApiRequest({
            url: requestUrl,
            method: requestMethod,
            status: response && typeof response.status === 'number' ? response.status : 0,
            transport: 'fetch'
          });
          return response;
        })
        .catch(function (error) {
          trackApiRequest({
            url: requestUrl,
            method: requestMethod,
            status: 0,
            transport: 'fetch'
          });
          throw error;
        });
    };
  }

  function installXhrInterceptor() {
    if (!window.XMLHttpRequest || !window.XMLHttpRequest.prototype) {
      return;
    }
    var proto = window.XMLHttpRequest.prototype;
    var originalOpen = proto.open;
    var originalSend = proto.send;
    if (!originalOpen || !originalSend) {
      return;
    }

    proto.open = function (method, url) {
      try {
        this.__saasTrackerMethod = requestMethodOrDefault(method);
        this.__saasTrackerUrl = toAbsoluteUrl(url);
      } catch (_) {
        this.__saasTrackerMethod = 'GET';
        this.__saasTrackerUrl = '';
      }
      return originalOpen.apply(this, arguments);
    };

    proto.send = function () {
      var xhr = this;
      function onDone() {
        try {
          xhr.removeEventListener('loadend', onDone);
        } catch (_) {}
        trackApiRequest({
          url: xhr.__saasTrackerUrl || '',
          method: xhr.__saasTrackerMethod || 'GET',
          status: typeof xhr.status === 'number' ? xhr.status : 0,
          transport: 'xhr'
        });
      }
      try {
        xhr.addEventListener('loadend', onDone);
      } catch (_) {}
      return originalSend.apply(this, arguments);
    };
  }

  try {
    logDebug('init handlers');
    resetPageTimer(window.location.pathname || '/');
    trackVisitStart()
      .then(function () {
        return trackPageView();
      })
      .catch(function () {
        return trackPageView();
      });
    installFetchInterceptor();
    installXhrInterceptor();
    document.addEventListener('click', onClick, true);
    document.addEventListener('submit', onSubmit, true);
    document.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('beforeunload', onPageClose);
    window.addEventListener('pagehide', onPageClose);
    wrapHistory();
    logDebug('init complete');
  } catch (err) {
    try {
      if (window.__saasTrackerInitializedToken === token) {
        window.__saasTrackerInitializedToken = '';
      }
    } catch (_) {}
    logError('tracker init failed', err);
  }
})();
"""
    return HttpResponse(script, content_type="application/javascript; charset=utf-8")
