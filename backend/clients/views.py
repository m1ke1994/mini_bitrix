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
  var SCROLL_THRESHOLDS = [25, 50, 75, 100];
  var scrollThresholdState = {};
  var maxScrollDepth = 0;
  var scrollEvaluationScheduled = false;
  var formVisibilityObserver = null;
  var sectionVisibilityObserver = null;
  var pendingFormSubmissions = {};
  var sectionSeenState = {};
  var sectionObservedState = {};

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

  function normalizeString(value, maxLen) {
    var normalized = ((value || '') + '').trim();
    if (typeof maxLen === 'number' && maxLen > 0) {
      return normalized.slice(0, maxLen);
    }
    return normalized;
  }

  function normalizeText(value, maxLen) {
    var normalized = ((value || '') + '').replace(/\s+/g, ' ').trim();
    if (typeof maxLen === 'number' && maxLen > 0) {
      return normalized.slice(0, maxLen);
    }
    return normalized;
  }

  function mergeObjects(base, extension) {
    var target = {};
    var key;
    if (base && typeof base === 'object') {
      for (key in base) {
        if (Object.prototype.hasOwnProperty.call(base, key)) {
          target[key] = base[key];
        }
      }
    }
    if (extension && typeof extension === 'object') {
      for (key in extension) {
        if (Object.prototype.hasOwnProperty.call(extension, key)) {
          target[key] = extension[key];
        }
      }
    }
    return target;
  }

  function parseUrlPathname(urlValue) {
    var absolute = toAbsoluteUrl(urlValue);
    if (!absolute) {
      return '';
    }
    try {
      return normalizeString(new URL(absolute).pathname || '', 512);
    } catch (_) {
      return '';
    }
  }

  function isTrackerInternalRequest(urlValue) {
    var absolute = toAbsoluteUrl(urlValue);
    if (!absolute) {
      return false;
    }
    try {
      var parsed = new URL(absolute);
      return parsed.origin === trackerOrigin && (parsed.pathname || '').indexOf('/api/track/') === 0;
    } catch (_) {
      return false;
    }
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

  function getCurrentRouteKey() {
    return (window.location.pathname || '/') + (window.location.search || '');
  }

  function getCurrentPathname() {
    return normalizeString(window.location.pathname || '/', 512) || '/';
  }

  function getFormDomIndex(form) {
    try {
      var forms = document.getElementsByTagName('form');
      for (var i = 0; i < forms.length; i++) {
        if (forms[i] === form) {
          return i + 1;
        }
      }
    } catch (_) {}
    return 0;
  }

  function getFormIdentifier(form) {
    if (!form) {
      return '';
    }
    var explicit = normalizeString(form.getAttribute('data-track-form'), 120);
    if (explicit) {
      return explicit;
    }
    if (form.id) {
      return normalizeString('id:' + form.id, 120);
    }
    var formName = normalizeString(form.getAttribute('name'), 100);
    if (formName) {
      return normalizeString('name:' + formName, 120);
    }
    var actionPath = parseUrlPathname(form.action || window.location.href);
    if (actionPath) {
      return normalizeString('action:' + actionPath + '#' + getFormDomIndex(form), 120);
    }
    return normalizeString('form#' + getFormDomIndex(form), 120);
  }

  function getFormMeta(form) {
    var actionUrl = toAbsoluteUrl(form && form.action ? form.action : window.location.href) || window.location.href;
    return {
      id: normalizeString(form && form.id ? form.id : '', 255),
      name: normalizeString(form && form.getAttribute ? form.getAttribute('name') : '', 255),
      form_key: getFormIdentifier(form),
      action: normalizeString(actionUrl, 1000),
      action_path: parseUrlPathname(actionUrl),
      method: requestMethodOrDefault(form && form.method ? form.method : 'GET'),
      page_url: normalizeString(window.location.href, 1000),
      path: getCurrentPathname(),
      field_count: (form && form.elements && form.elements.length) ? form.elements.length : 0
    };
  }

  function getFormState(form) {
    if (!form || form.tagName !== 'FORM') {
      return null;
    }
    var currentRouteKey = getCurrentRouteKey();
    if (!form.__saasTrackerState || form.__saasTrackerState.routeKey !== currentRouteKey) {
      form.__saasTrackerState = {
        routeKey: currentRouteKey,
        viewed: false,
        started: false,
        firstFieldFilled: false,
        submitAttempted: false,
      };
    }
    return form.__saasTrackerState;
  }

  function trackFormStep(stepType, form, extraPayload) {
    var payload = mergeObjects(getFormMeta(form), extraPayload || {});
    trackEvent(stepType, payload);
  }

  function createPendingFormSubmission(form) {
    var submissionId = createUuid();
    var meta = getFormMeta(form);
    pendingFormSubmissions[submissionId] = {
      id: submissionId,
      createdAt: Date.now(),
      resolved: false,
      resolvedAt: 0,
      method: requestMethodOrDefault(meta.method || 'POST'),
      actionUrl: toAbsoluteUrl(meta.action || window.location.href),
      actionPath: normalizeString(meta.action_path, 512),
      routePath: normalizeString(meta.path || window.location.pathname || '/', 512),
      formMeta: meta
    };
    return pendingFormSubmissions[submissionId];
  }

  function cleanupPendingFormSubmissions(force) {
    var now = Date.now();
    var keys = Object.keys(pendingFormSubmissions || {});
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      var item = pendingFormSubmissions[key];
      if (!item) {
        delete pendingFormSubmissions[key];
        continue;
      }
      if (force) {
        delete pendingFormSubmissions[key];
        continue;
      }
      if (item.resolved && (now - (item.resolvedAt || now) > 5000)) {
        delete pendingFormSubmissions[key];
        continue;
      }
      if (!item.resolved && (now - (item.createdAt || now) > 15000)) {
        delete pendingFormSubmissions[key];
      }
    }
  }

  function isWriteRequestMethod(method) {
    var normalized = requestMethodOrDefault(method);
    return normalized === 'POST' || normalized === 'PUT' || normalized === 'PATCH' || normalized === 'DELETE';
  }

  function detectBodyKind(body) {
    if (typeof body === 'undefined' || body === null) {
      return '';
    }
    try {
      if (typeof FormData !== 'undefined' && body instanceof FormData) {
        return 'formdata';
      }
    } catch (_) {}
    try {
      if (typeof URLSearchParams !== 'undefined' && body instanceof URLSearchParams) {
        return 'urlencoded';
      }
    } catch (_) {}
    try {
      if (typeof Blob !== 'undefined' && body instanceof Blob) {
        return 'blob';
      }
    } catch (_) {}
    if (typeof body === 'string') {
      return body ? 'text' : '';
    }
    if (typeof body === 'object') {
      return 'json';
    }
    return 'unknown';
  }

  function buildRequestMetaFromFetchArgs(input, init) {
    var bodyValue = null;
    try {
      if (init && Object.prototype.hasOwnProperty.call(init, 'body')) {
        bodyValue = init.body;
      } else if (input && typeof input === 'object' && Object.prototype.hasOwnProperty.call(input, 'body')) {
        bodyValue = input.body;
      }
    } catch (_) {
      bodyValue = null;
    }
    return {
      hasBody: !(typeof bodyValue === 'undefined' || bodyValue === null),
      bodyKind: detectBodyKind(bodyValue),
      requestFailed: false
    };
  }

  function matchPendingFormSubmissionScore(item, requestUrl, requestMethod, requestMeta) {
    if (!item || item.resolved) {
      return -1;
    }
    if (isTrackerInternalRequest(requestUrl)) {
      return -1;
    }
    if ((Date.now() - (item.createdAt || Date.now())) > 20000) {
      return -1;
    }

    var normalizedMethod = requestMethodOrDefault(requestMethod);
    var methodScore = 0;
    if (item.method && normalizedMethod && item.method === normalizedMethod) {
      methodScore = 30;
    } else if (isWriteRequestMethod(item.method) && isWriteRequestMethod(normalizedMethod)) {
      methodScore = 15;
    } else if (item.method === 'GET' && normalizedMethod === 'GET') {
      methodScore = 20;
    } else if (!isWriteRequestMethod(normalizedMethod)) {
      return -1;
    }

    var absoluteRequestUrl = toAbsoluteUrl(requestUrl);
    var requestPath = parseUrlPathname(absoluteRequestUrl || '');
    if (!absoluteRequestUrl && !requestPath) {
      return -1;
    }

    var score = methodScore;
    if (item.actionUrl && absoluteRequestUrl.indexOf(item.actionUrl) === 0) {
      score += 120;
    }
    if (requestPath && item.actionPath && requestPath === item.actionPath) {
      score += 100;
    } else if (requestPath && item.actionPath && item.actionPath !== '/' && requestPath.indexOf(item.actionPath) === 0) {
      score += 70;
    }
    if (requestPath && /^\/api\//.test(requestPath)) {
      score += 35;
    }
    if (requestPath && /(lead|form|contact|submit|request|feedback|callback)/i.test(requestPath)) {
      score += 25;
    }
    if (requestPath && item.routePath && requestPath === item.routePath) {
      score += 10;
    }
    if ((Date.now() - (item.createdAt || Date.now())) <= 5000) {
      score += 15;
    }
    if (requestMeta && requestMeta.hasBody) {
      score += 20;
      if (requestMeta.bodyKind === 'formdata') {
        score += 15;
      } else if (requestMeta.bodyKind === 'json' || requestMeta.bodyKind === 'urlencoded') {
        score += 10;
      }
    }
    return score;
  }

  function resolvePendingFormSubmission(requestUrl, requestMethod, requestMeta) {
    cleanupPendingFormSubmissions(false);
    var keys = Object.keys(pendingFormSubmissions || {});
    var matched = null;
    var matchedScore = -1;
    var unresolvedCount = 0;
    var unresolvedCandidate = null;
    for (var i = 0; i < keys.length; i++) {
      var item = pendingFormSubmissions[keys[i]];
      if (!item || item.resolved) {
        continue;
      }
      unresolvedCount += 1;
      unresolvedCandidate = item;
      var score = matchPendingFormSubmissionScore(item, requestUrl, requestMethod, requestMeta);
      if (score < 0) {
        continue;
      }
      if (!matched || score > matchedScore || (score === matchedScore && (item.createdAt || 0) > (matched.createdAt || 0))) {
        matched = item;
        matchedScore = score;
      }
    }
    if (matched && matchedScore >= 45) {
      return matched;
    }
    if (matched && matchedScore >= 30 && requestMeta && requestMeta.hasBody) {
      return matched;
    }
    if (
      unresolvedCount === 1 &&
      unresolvedCandidate &&
      isWriteRequestMethod(requestMethod) &&
      (Date.now() - (unresolvedCandidate.createdAt || Date.now())) <= 7000
    ) {
      return unresolvedCandidate;
    }
    return null;
  }

  function finalizePendingFormSubmission(requestUrl, requestMethod, statusCode, transport, requestMeta) {
    var normalizedMeta = requestMeta || {};
    var pending = resolvePendingFormSubmission(requestUrl, requestMethod, normalizedMeta);
    if (!pending) {
      return;
    }
    pending.resolved = true;
    pending.resolvedAt = Date.now();
    var normalizedStatus = Number(statusCode || 0) || 0;
    var failedByTransport = !!normalizedMeta.requestFailed;
    var isSuccessStatus = normalizedStatus >= 200 && normalizedStatus < 400;
    var isBestEffortSuccess = !failedByTransport && normalizedStatus === 0;
    var eventType = (isSuccessStatus || isBestEffortSuccess) ? 'form_submit_success' : 'form_submit_error';
    trackFormStep(eventType, null, mergeObjects(pending.formMeta || {}, {
      submission_id: pending.id,
      status: normalizedStatus,
      transport: normalizeString(transport || '', 32),
      body_kind: normalizeString(normalizedMeta.bodyKind || '', 32),
      request_failed: failedByTransport,
      request_url: normalizeString(requestUrl || '', 1000)
    }));
    cleanupPendingFormSubmissions(false);
  }

  function isFilledField(target) {
    if (!target) {
      return false;
    }
    var type = ((target.type || '') + '').toLowerCase();
    if (type === 'checkbox' || type === 'radio') {
      return !!target.checked;
    }
    if (type === 'file') {
      return !!(target.files && target.files.length);
    }
    return normalizeString(target.value, 1000).length > 0;
  }

  function onFormFocusIn(event) {
    try {
      var field = event.target;
      var form = field && field.form ? field.form : null;
      if (!form || form.tagName !== 'FORM') {
        return;
      }
      var state = getFormState(form);
      if (!state || state.started) {
        return;
      }
      state.started = true;
      trackFormStep('form_start', form, { trigger: 'focus' });
    } catch (err) {
      logError('form focus tracking failed', err);
    }
  }

  function onFormInputOrChange(event) {
    try {
      var field = event.target;
      var form = field && field.form ? field.form : null;
      if (!form || form.tagName !== 'FORM') {
        return;
      }
      var state = getFormState(form);
      if (!state) {
        return;
      }
      if (!state.started) {
        state.started = true;
        trackFormStep('form_start', form, { trigger: 'input' });
      }
      if (!state.firstFieldFilled && isFilledField(field)) {
        state.firstFieldFilled = true;
        trackFormStep('form_first_field_filled', form, {
          field_name: normalizeString(field.name || field.id || '', 64),
          field_type: normalizeString(field.type || field.tagName || '', 32),
        });
      }
    } catch (err) {
      logError('form input tracking failed', err);
    }
  }

  function onFormVisibility(entries) {
    for (var i = 0; i < entries.length; i++) {
      var entry = entries[i];
      var form = entry && entry.target ? entry.target : null;
      if (!form || form.tagName !== 'FORM') {
        continue;
      }
      if (!entry.isIntersecting || entry.intersectionRatio < 0.35) {
        continue;
      }
      var state = getFormState(form);
      if (!state || state.viewed) {
        continue;
      }
      state.viewed = true;
      trackFormStep('form_view', form, { trigger: 'intersection' });
      if (formVisibilityObserver) {
        try {
          formVisibilityObserver.unobserve(form);
        } catch (_) {}
      }
    }
  }

  function refreshFormVisibilityObserver() {
    try {
      if (formVisibilityObserver) {
        formVisibilityObserver.disconnect();
      }
      if (!window.IntersectionObserver) {
        return;
      }
      formVisibilityObserver = new IntersectionObserver(onFormVisibility, {
        threshold: [0.35, 0.6]
      });
      var forms = document.getElementsByTagName('form');
      for (var i = 0; i < forms.length; i++) {
        var form = forms[i];
        var state = getFormState(form);
        if (!state || state.viewed) {
          continue;
        }
        formVisibilityObserver.observe(form);
      }
    } catch (err) {
      logError('form visibility observer failed', err);
    }
  }

  function normalizeSectionKey(value) {
    return normalizeString(value, 64).toLowerCase().replace(/[^a-z0-9_-]+/g, '_').replace(/^_+|_+$/g, '');
  }

  function detectSectionKey(element) {
    if (!element || element.nodeType !== 1) {
      return '';
    }
    var explicit = normalizeSectionKey(element.getAttribute ? element.getAttribute('data-track-section') : '');
    if (explicit) {
      return explicit;
    }

    var tagName = normalizeString(element.tagName || '', 32).toLowerCase();
    if (tagName === 'form') {
      return 'form';
    }

    var idValue = normalizeString(element.id || '', 100).toLowerCase();
    var classValue = '';
    try {
      classValue = normalizeString(typeof element.className === 'string' ? element.className : '', 255).toLowerCase();
    } catch (_) {
      classValue = '';
    }
    var signature = idValue + ' ' + classValue;

    if (!signature) {
      return '';
    }
    if (/hero/.test(signature)) {
      return 'hero';
    }
    if (/(benefit|advantage|capabilit|feature)/.test(signature)) {
      return 'benefits';
    }
    if (/(case|portfolio|project|example)/.test(signature)) {
      return 'cases';
    }
    if (/(review|testimonial)/.test(signature)) {
      return 'reviews';
    }
    if (/(faq|question)/.test(signature)) {
      return 'faq';
    }
    if (/(pricing|tarif|plan|price)/.test(signature)) {
      return 'pricing';
    }
    if (/(contact|footer|telegram|whatsapp|email|phone)/.test(signature)) {
      return 'contacts';
    }
    return '';
  }

  function collectSectionCandidates() {
    var selector = [
      '[data-track-section]',
      'form',
      'section',
      '[id*="hero"]',
      '[id*="benefit"]',
      '[id*="advantage"]',
      '[id*="case"]',
      '[id*="review"]',
      '[id*="faq"]',
      '[id*="pricing"]',
      '[id*="tarif"]',
      '[id*="contact"]',
      '[class*="hero"]',
      '[class*="benefit"]',
      '[class*="advantage"]',
      '[class*="case"]',
      '[class*="review"]',
      '[class*="faq"]',
      '[class*="pricing"]',
      '[class*="tarif"]',
      '[class*="contact"]'
    ].join(',');
    try {
      return document.querySelectorAll(selector);
    } catch (_) {
      return [];
    }
  }

  function onSectionVisibility(entries) {
    for (var i = 0; i < entries.length; i++) {
      var entry = entries[i];
      var section = entry && entry.target ? entry.target : null;
      if (!section || !entry.isIntersecting || entry.intersectionRatio < 0.35) {
        continue;
      }
      var sectionKey = normalizeString(section.__saasSectionKey, 64);
      if (!sectionKey || sectionSeenState[sectionKey]) {
        continue;
      }
      sectionSeenState[sectionKey] = true;
      trackEvent('section_view', {
        section_key: sectionKey,
        page_url: normalizeString(window.location.href, 1000),
        path: getCurrentPathname()
      });
      if (sectionVisibilityObserver) {
        try {
          sectionVisibilityObserver.unobserve(section);
        } catch (_) {}
      }
    }
  }

  function refreshSectionVisibilityObserver() {
    try {
      if (sectionVisibilityObserver) {
        sectionVisibilityObserver.disconnect();
      }
      sectionObservedState = {};
      if (!window.IntersectionObserver) {
        return;
      }
      sectionVisibilityObserver = new IntersectionObserver(onSectionVisibility, {
        threshold: [0.35, 0.6]
      });
      var candidates = collectSectionCandidates();
      for (var i = 0; i < candidates.length; i++) {
        var section = candidates[i];
        var sectionKey = detectSectionKey(section);
        if (!sectionKey || sectionSeenState[sectionKey] || sectionObservedState[sectionKey]) {
          continue;
        }
        sectionObservedState[sectionKey] = true;
        section.__saasSectionKey = sectionKey;
        sectionVisibilityObserver.observe(section);
      }
    } catch (err) {
      logError('section visibility observer failed', err);
    }
  }

  function getScrollDepthPercent() {
    var doc = document.documentElement || {};
    var body = document.body || {};
    var scrollTop = window.pageYOffset || doc.scrollTop || body.scrollTop || 0;
    var viewportHeight = window.innerHeight || doc.clientHeight || 0;
    var scrollHeight = Math.max(
      doc.scrollHeight || 0,
      body.scrollHeight || 0,
      doc.offsetHeight || 0,
      body.offsetHeight || 0
    );

    if (scrollHeight <= 0 || viewportHeight <= 0) {
      return 0;
    }
    if (scrollHeight <= viewportHeight) {
      return 100;
    }
    var depth = Math.round(((scrollTop + viewportHeight) / scrollHeight) * 100);
    if (depth < 0) {
      return 0;
    }
    if (depth > 100) {
      return 100;
    }
    return depth;
  }

  function evaluateScrollDepth() {
    var depth = getScrollDepthPercent();
    if (depth > maxScrollDepth) {
      maxScrollDepth = depth;
    }
    for (var i = 0; i < SCROLL_THRESHOLDS.length; i++) {
      var threshold = SCROLL_THRESHOLDS[i];
      if (depth < threshold || scrollThresholdState[threshold]) {
        continue;
      }
      scrollThresholdState[threshold] = true;
      trackEvent('scroll_depth', {
        depth: threshold,
        current_depth: depth,
        path: getCurrentPathname(),
        page_url: normalizeString(window.location.href, 1000)
      });
    }
  }

  function scheduleScrollDepthEvaluation() {
    if (scrollEvaluationScheduled) {
      return;
    }
    scrollEvaluationScheduled = true;
    var scheduler = window.requestAnimationFrame || function (callback) {
      return setTimeout(callback, 50);
    };
    scheduler(function () {
      scrollEvaluationScheduled = false;
      evaluateScrollDepth();
    });
  }

  function resetPageAnalyticsSignals() {
    scrollThresholdState = {};
    maxScrollDepth = 0;
    sectionSeenState = {};
    cleanupPendingFormSubmissions(false);
    scheduleScrollDepthEvaluation();
    setTimeout(function () {
      refreshFormVisibilityObserver();
      refreshSectionVisibilityObserver();
      scheduleScrollDepthEvaluation();
    }, 120);
  }

  function readDatasetValue(node, attrName) {
    if (!node || !node.getAttribute) {
      return '';
    }
    return normalizeString(node.getAttribute(attrName), 120);
  }

  function detectCtaType(node, text, href, className) {
    var lowerText = normalizeText(text, 200).toLowerCase();
    var lowerHref = normalizeString(href, 1000).toLowerCase();
    var lowerClass = normalizeString(className, 255).toLowerCase();
    var explicitType = readDatasetValue(node, 'data-cta-type') || readDatasetValue(node, 'data-track-cta-type');
    if (explicitType) {
      return normalizeSectionKey(explicitType) || 'generic';
    }
    if (lowerHref.indexOf('t.me') !== -1 || lowerHref.indexOf('telegram.me') !== -1) {
      return 'telegram';
    }
    if (lowerHref.indexOf('wa.me') !== -1 || lowerHref.indexOf('whatsapp') !== -1) {
      return 'whatsapp';
    }
    if (lowerHref.indexOf('mailto:') === 0) {
      return 'email';
    }
    if (lowerHref.indexOf('tel:') === 0) {
      return 'phone';
    }
    if (/(pricing|tarif|plan|price)/.test(lowerClass) || /(тариф|цена|оплат|купить|buy|pricing|plan|price)/.test(lowerText)) {
      return 'pricing';
    }
    if (/(hero|banner)/.test(lowerClass)) {
      return 'hero';
    }
    if (/(submit|form|send|request|оставить|заявк|подпис|запис)/.test(lowerClass + ' ' + lowerText)) {
      return 'form';
    }
    return 'generic';
  }

  function getCtaMeta(node) {
    if (!node) {
      return null;
    }
    var explicit = readDatasetValue(node, 'data-track-cta') || readDatasetValue(node, 'data-cta');
    var text = normalizeText((node.innerText || node.textContent || ''), 120);
    var href = normalizeString(node.getAttribute ? (node.getAttribute('href') || '') : '', 1000);
    var className = normalizeString(typeof node.className === 'string' ? node.className : '', 255);
    var lowerText = text.toLowerCase();
    var lowerHref = href.toLowerCase();
    var lowerClass = className.toLowerCase();
    var isCta = !!explicit;

    if (!isCta && (lowerHref.indexOf('t.me') !== -1 || lowerHref.indexOf('telegram.me') !== -1 || lowerHref.indexOf('wa.me') !== -1 || lowerHref.indexOf('whatsapp') !== -1 || lowerHref.indexOf('mailto:') === 0 || lowerHref.indexOf('tel:') === 0)) {
      isCta = true;
    }
    if (!isCta && (lowerClass.indexOf('cta') !== -1 || lowerClass.indexOf('btn-primary') !== -1 || lowerClass.indexOf('button-primary') !== -1 || lowerClass.indexOf('hero') !== -1)) {
      isCta = true;
    }
    if (!isCta && /(оставить|заявк|подключ|начать|попроб|демо|demo|trial|register|signup|sign up|buy|contact|call|write|telegram|whatsapp|связат|заказать|получить)/.test(lowerText)) {
      isCta = true;
    }
    if (!isCta) {
      return null;
    }

    var ctaType = detectCtaType(node, text, href, className);
    var ctaKeySource = explicit || node.id || href || text;
    var ctaKey = normalizeSectionKey(ctaKeySource) || 'cta';

    return {
      cta_type: normalizeString(ctaType, 48),
      cta_key: normalizeString(ctaKey, 120),
      href: href,
      text: text
    };
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
    resetPageAnalyticsSignals();
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
        resetPageAnalyticsSignals();
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
      var clickPayload = {
        tag: node.tagName || '',
        id: node.id || '',
        class: normalizeString(typeof node.className === 'string' ? node.className : '', 255),
        text: ((node.innerText || node.textContent || '') + '').trim().slice(0, 120),
        href: normalizeString(node.getAttribute ? (node.getAttribute('href') || '') : '', 1000),
        path: window.location.pathname
      };
      trackEvent('click', clickPayload);

      var ctaMeta = getCtaMeta(node);
      if (ctaMeta) {
        trackEvent('cta_click', mergeObjects(clickPayload, ctaMeta));
      }
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
      var state = getFormState(form);
      if (state) {
        state.submitAttempted = true;
        if (!state.started) {
          state.started = true;
          trackFormStep('form_start', form, { trigger: 'submit' });
        }
      }
      var pending = createPendingFormSubmission(form);
      var formPayloadBase = mergeObjects(getFormMeta(form), {
        url: normalizeString(window.location.href, 1000),
        domain: normalizeString(window.location.hostname, 255),
        fields: extractSafeFormFields(form),
        submission_id: pending.id
      });
      trackEvent('form_submit_attempt', formPayloadBase);
      trackEvent('form_submit', formPayloadBase);
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
      var requestMeta = buildRequestMetaFromFetchArgs(input, init);
      return originalFetch.apply(this, arguments)
        .then(function (response) {
          var statusCode = response && typeof response.status === 'number' ? response.status : 0;
          trackApiRequest({
            url: requestUrl,
            method: requestMethod,
            status: statusCode,
            transport: 'fetch'
          });
          finalizePendingFormSubmission(
            requestUrl,
            requestMethod,
            statusCode,
            'fetch',
            mergeObjects(requestMeta, { requestFailed: false })
          );
          return response;
        })
        .catch(function (error) {
          trackApiRequest({
            url: requestUrl,
            method: requestMethod,
            status: 0,
            transport: 'fetch'
          });
          finalizePendingFormSubmission(
            requestUrl,
            requestMethod,
            0,
            'fetch',
            mergeObjects(requestMeta, { requestFailed: true })
          );
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
        this.__saasTrackerHasBody = false;
        this.__saasTrackerBodyKind = '';
        this.__saasTrackerFailed = false;
      } catch (_) {
        this.__saasTrackerMethod = 'GET';
        this.__saasTrackerUrl = '';
        this.__saasTrackerHasBody = false;
        this.__saasTrackerBodyKind = '';
        this.__saasTrackerFailed = false;
      }
      return originalOpen.apply(this, arguments);
    };

    proto.send = function (body) {
      var xhr = this;
      try {
        xhr.__saasTrackerHasBody = !(typeof body === 'undefined' || body === null);
        xhr.__saasTrackerBodyKind = detectBodyKind(body);
      } catch (_) {
        xhr.__saasTrackerHasBody = false;
        xhr.__saasTrackerBodyKind = '';
      }
      function onRequestFailed() {
        xhr.__saasTrackerFailed = true;
      }
      function onDone() {
        try {
          xhr.removeEventListener('loadend', onDone);
          xhr.removeEventListener('error', onRequestFailed);
          xhr.removeEventListener('timeout', onRequestFailed);
          xhr.removeEventListener('abort', onRequestFailed);
        } catch (_) {}
        var xhrStatus = typeof xhr.status === 'number' ? xhr.status : 0;
        trackApiRequest({
          url: xhr.__saasTrackerUrl || '',
          method: xhr.__saasTrackerMethod || 'GET',
          status: xhrStatus,
          transport: 'xhr'
        });
        finalizePendingFormSubmission(
          xhr.__saasTrackerUrl || '',
          xhr.__saasTrackerMethod || 'GET',
          xhrStatus,
          'xhr',
          {
            hasBody: !!xhr.__saasTrackerHasBody,
            bodyKind: xhr.__saasTrackerBodyKind || '',
            requestFailed: !!xhr.__saasTrackerFailed
          }
        );
      }
      try {
        xhr.addEventListener('loadend', onDone);
        xhr.addEventListener('error', onRequestFailed);
        xhr.addEventListener('timeout', onRequestFailed);
        xhr.addEventListener('abort', onRequestFailed);
      } catch (_) {}
      return originalSend.apply(this, arguments);
    };
  }

  try {
    logDebug('init handlers');
    resetPageTimer(window.location.pathname || '/');
    resetPageAnalyticsSignals();
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
    document.addEventListener('focusin', onFormFocusIn, true);
    document.addEventListener('input', onFormInputOrChange, true);
    document.addEventListener('change', onFormInputOrChange, true);
    document.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('scroll', scheduleScrollDepthEvaluation, { passive: true });
    window.addEventListener('resize', scheduleScrollDepthEvaluation);
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
