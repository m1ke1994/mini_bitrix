from django.http import HttpResponse
from rest_framework import generics, permissions

from accounts.permissions import IsClientUser
from clients.serializers import ClientSettingsSerializer


class ClientSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientUser]

    def get_object(self):
        return self.request.client


def tracker_js_view(request):
    script = r"""
(function () {
  'use strict';

  function safeLogError(message, error) {
    try {
      console.error('[SaaS Tracker] ' + message, error || '');
    } catch (_) {}
  }

  function safeStorageGet(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (_) {
      return null;
    }
  }

  function safeStorageSet(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_) {}
  }

  function getScriptTag() {
    if (document.currentScript) {
      return document.currentScript;
    }
    var scripts = document.getElementsByTagName('script');
    if (!scripts || !scripts.length) {
      return null;
    }
    return scripts[scripts.length - 1];
  }

  function createSessionId() {
    try {
      if (window.crypto && window.crypto.randomUUID) {
        return window.crypto.randomUUID();
      }
    } catch (_) {}
    return 'sid-' + Date.now() + '-' + Math.random().toString(16).slice(2);
  }

  function isEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i.test(value);
  }

  function isIsoDate(value) {
    return /^\d{4}-\d{2}-\d{2}$/.test(String(value).trim());
  }

  function normalizePhone(value) {
    var raw = String(value || '').trim();
    if (!raw || isIsoDate(raw)) {
      return null;
    }
    if (!/^\+?[0-9\s\-()]{7,20}$/.test(raw)) {
      return null;
    }
    var digits = raw.replace(/\D/g, '');
    if (digits.length < 7) {
      return null;
    }
    return raw;
  }

  function hasPhoneHint(key) {
    var normalized = String(key || '').toLowerCase();
    return normalized.indexOf('phone') !== -1 || normalized.indexOf('tel') !== -1;
  }

  function hasEmailHint(key) {
    var normalized = String(key || '').toLowerCase();
    return normalized.indexOf('email') !== -1 || normalized.indexOf('mail') !== -1;
  }

  function getUtms(url) {
    var params = new URL(url).searchParams;
    return {
      utm_source: params.get('utm_source') || null,
      utm_medium: params.get('utm_medium') || null,
      utm_campaign: params.get('utm_campaign') || null,
      utm_term: params.get('utm_term') || null,
      utm_content: params.get('utm_content') || null
    };
  }

  function collectFormFields(form) {
    var fields = [];
    var nodes = form.querySelectorAll('input, textarea, select');
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (!node) { continue; }
      var key = (node.name || node.id || '').trim();
      var fieldType = ((node.type || '') + '').toLowerCase();
      var rawValue = typeof node.value === 'string' ? node.value.trim() : '';
      if (!rawValue) { continue; }
      fields.push({ key: key, value: rawValue, fieldType: fieldType });
    }
    return fields;
  }

  function collectObjectFields(payload) {
    var fields = [];
    function walk(data, path) {
      if (data === null || data === undefined) {
        return;
      }
      if (typeof data === 'string' || typeof data === 'number') {
        var value = String(data).trim();
        if (value) {
          fields.push({ key: path || '', value: value, fieldType: '' });
        }
        return;
      }
      if (Array.isArray(data)) {
        for (var i = 0; i < data.length; i++) {
          walk(data[i], path);
        }
        return;
      }
      if (typeof data === 'object') {
        var keys = Object.keys(data);
        for (var j = 0; j < keys.length; j++) {
          var key = keys[j];
          walk(data[key], key);
        }
      }
    }
    walk(payload, '');
    return fields;
  }

  function assignLeadFromFields(fields, payload) {
    var extracted = {
      name: null,
      email: null,
      phone: null,
      message: null
    };

    function setIfMissing(field, value) {
      if (!extracted[field] && value) {
        extracted[field] = value;
      }
    }

    for (var i = 0; i < fields.length; i++) {
      var item = fields[i];
      var key = (item.key || '').toLowerCase();
      var value = item.value;
      var fieldType = (item.fieldType || '').toLowerCase();
      if (!value) { continue; }

      if (key.indexOf('name') !== -1 || key.indexOf('fullname') !== -1 || key.indexOf('fio') !== -1) {
        setIfMissing('name', value);
      }
      if (key.indexOf('message') !== -1 || key.indexOf('comment') !== -1 || key.indexOf('text') !== -1) {
        setIfMissing('message', value);
      }

      if (fieldType === 'email' || key === 'email' || hasEmailHint(key)) {
        if (isEmail(value)) {
          setIfMissing('email', value);
        }
      }

      if (fieldType === 'tel' || hasPhoneHint(key) || key.indexOf('contact') !== -1) {
        if (isEmail(value) && key.indexOf('contact') !== -1) {
          setIfMissing('email', value);
        } else {
          var normalizedPhone = normalizePhone(value);
          if (normalizedPhone) {
            setIfMissing('phone', normalizedPhone);
          }
        }
      }
    }

    for (var j = 0; j < fields.length; j++) {
      var candidate = fields[j].value;
      var candidateKey = (fields[j].key || '').toLowerCase();
      if (!candidate) { continue; }
      if (!extracted.email && (hasEmailHint(candidateKey) || candidate.indexOf('@') !== -1) && isEmail(candidate)) {
        extracted.email = candidate;
      }
      if (!extracted.phone && (hasPhoneHint(candidateKey) || candidateKey.indexOf('contact') !== -1)) {
        var fallbackPhone = normalizePhone(candidate);
        if (fallbackPhone) {
          extracted.phone = fallbackPhone;
        }
      }
    }

    if (extracted.name) { payload.name = extracted.name; }
    if (extracted.email) { payload.email = extracted.email; }
    if (extracted.phone) { payload.phone = extracted.phone; }
    if (extracted.message) { payload.message = extracted.message; }
  }

  function getElementText(el) {
    if (!el) { return ''; }
    var text = (el.innerText || el.textContent || el.value || '').trim();
    return text.slice(0, 100);
  }

  var scriptTag = getScriptTag();
  var apiKey = scriptTag && scriptTag.dataset ? scriptTag.dataset.apiKey : '';
  if (!apiKey) {
    safeLogError('Missing data-api-key attribute.');
    return;
  }

  var baseUrl = window.location.origin;
  try {
    if (scriptTag && scriptTag.src) {
      baseUrl = new URL(scriptTag.src).origin;
    }
  } catch (error) {
    safeLogError('Failed to resolve tracker base URL.', error);
  }

  var nativeFetch = window.fetch ? window.fetch.bind(window) : null;
  if (!nativeFetch) {
    safeLogError('window.fetch is not available.');
    return;
  }

  var sessionKey = 'saas_tracker_session_id';
  var sessionId = safeStorageGet(sessionKey);
  if (!sessionId) {
    sessionId = createSessionId();
    safeStorageSet(sessionKey, sessionId);
  }
  var sourceKey = 'saas_tracker_session_source_' + sessionId;
  var sessionSourceRaw = safeStorageGet(sourceKey);
  var sessionSource = null;
  if (sessionSourceRaw) {
    try {
      sessionSource = JSON.parse(sessionSourceRaw);
    } catch (_) {
      sessionSource = null;
    }
  }
  if (!sessionSource) {
    var initialHref = window.location.href;
    var initialLoc = window.location;
    sessionSource = Object.assign(
      {
        source_url: initialHref,
        first_url: initialHref,
        first_pathname: initialLoc.pathname || '/',
        first_query_string: initialLoc.search || '',
        referrer: document.referrer || null
      },
      getUtms(initialHref)
    );
    safeStorageSet(sourceKey, JSON.stringify(sessionSource));
  }

  var pageStartTs = Date.now();
  var maxScrollDepth = 0;
  var sentClickFingerprints = {};

  function basePayload() {
    var href = window.location.href;
    var locationObj = window.location;
    var sourceFields = sessionSource || {};
    return Object.assign(
      {
        session_id: sessionId,
        source_url: sourceFields.source_url || href,
        page_url: href,
        url: href,
        pathname: locationObj.pathname || '/',
        query_string: locationObj.search || '',
        referrer: sourceFields.referrer || null,
        timestamp: new Date().toISOString()
      },
      {
        utm_source: sourceFields.utm_source || null,
        utm_medium: sourceFields.utm_medium || null,
        utm_campaign: sourceFields.utm_campaign || null,
        utm_term: sourceFields.utm_term || null,
        utm_content: sourceFields.utm_content || null
      }
    );
  }

  function requestWithFallback(endpoint, payload) {
    var url = baseUrl + endpoint + '?api_key=' + encodeURIComponent(apiKey);
    var body = JSON.stringify(payload);
    if (navigator.sendBeacon) {
      try {
        var blob = new Blob([body], { type: 'application/json' });
        if (navigator.sendBeacon(url, blob)) {
          return;
        }
      } catch (_) {}
    }

    nativeFetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': apiKey
      },
      body: body,
      keepalive: true,
      credentials: 'omit'
    }).catch(function (error) {
      safeLogError('Request failed for ' + endpoint, error);
    });
  }

  function sendPublicEvent(eventType, elementId) {
    var payload = basePayload();
    payload.event_type = eventType;
    payload.element_id = elementId || null;
    requestWithFallback('/api/public/event/', payload);
  }

  function sendPublicLead(payload) {
    requestWithFallback('/api/public/lead/', payload);
  }

  function sendAnalyticsEvent(eventType, payloadOverrides) {
    var payload = basePayload();
    payload.event_type = eventType;
    if (payloadOverrides && typeof payloadOverrides === 'object') {
      var keys = Object.keys(payloadOverrides);
      for (var i = 0; i < keys.length; i++) {
        payload[keys[i]] = payloadOverrides[keys[i]];
      }
    }
    requestWithFallback('/api/analytics/event/', payload);
  }

  function maybeSendVisitOnce() {
    var marker = 'saas_tracker_visit_sent_' + sessionId;
    if (safeStorageGet(marker) === '1') {
      return;
    }
    sendPublicEvent('visit', null);
    safeStorageSet(marker, '1');
  }

  function sendPageView() {
    sendAnalyticsEvent('page_view', { max_scroll_depth: maxScrollDepth });
  }

  function firstFieldValue(form, aliases) {
    for (var i = 0; i < aliases.length; i++) {
      var selector = '[name="' + aliases[i] + '"], [name*="' + aliases[i] + '" i], #' + aliases[i];
      var field = form.querySelector(selector);
      if (!field || typeof field.value !== 'string') {
        continue;
      }
      var value = field.value.trim();
      if (value) {
        return value;
      }
    }
    return null;
  }

  function extractLeadPayloadFromForm(form) {
    var payload = basePayload();
    payload.session_id = sessionId;
    var fields = collectFormFields(form);
    assignLeadFromFields(fields, payload);
    if (!payload.name) {
      payload.name = firstFieldValue(form, ['name', 'fullname', 'fio']);
    }
    if (!payload.message) {
      payload.message = firstFieldValue(form, ['message', 'comment', 'text']);
    }
    return payload;
  }

  function trackFormSubmit(event) {
    try {
      var form = event.target;
      if (!form || form.tagName !== 'FORM') {
        return;
      }
      var leadPayload = extractLeadPayloadFromForm(form);
      sendPublicLead(leadPayload);
      sendPublicEvent('form_submit', form.id || null);
      sendAnalyticsEvent('lead_submit', { pathname: window.location.pathname });
    } catch (error) {
      safeLogError('Failed to process submit event.', error);
    }
  }

  function shouldSkipTrackedRequest(url) {
    return (
      typeof url === 'string' &&
      (
        url.indexOf('/api/public/lead/') !== -1 ||
        url.indexOf('/api/public/event/') !== -1 ||
        url.indexOf('/api/analytics/event/') !== -1
      )
    );
  }

  function extractLeadFromObject(data) {
    if (!data || typeof data !== 'object') {
      return null;
    }
    var payload = basePayload();
    payload.session_id = sessionId;
    var fields = collectObjectFields(data);
    assignLeadFromFields(fields, payload);
    if (!payload.name && typeof data.name === 'string') {
      payload.name = data.name.trim();
    }
    if (!payload.message && typeof data.message === 'string') {
      payload.message = data.message.trim();
    }
    if (!payload.name && !payload.phone && !payload.email && !payload.message) {
      return null;
    }
    return payload;
  }

  function tryTrackJsonLead(rawBody) {
    if (typeof rawBody !== 'string' || !rawBody.trim()) {
      return;
    }
    try {
      var parsed = JSON.parse(rawBody);
      var leadPayload = extractLeadFromObject(parsed);
      if (!leadPayload) {
        return;
      }
      sendPublicLead(leadPayload);
      sendPublicEvent('form_submit', 'fetch_json');
      sendAnalyticsEvent('lead_submit', { pathname: window.location.pathname });
    } catch (error) {
      safeLogError('Failed to parse JSON fetch body.', error);
    }
  }

  function interceptFetch() {
    window.fetch = function(input, init) {
      try {
        var method = (init && init.method) || (input && input.method) || 'GET';
        var upperMethod = String(method).toUpperCase();
        var url = typeof input === 'string' ? input : (input && input.url ? input.url : '');

        if (upperMethod === 'POST' && !shouldSkipTrackedRequest(url)) {
          var contentType = '';
          if (init && init.headers) {
            if (typeof init.headers.get === 'function') {
              contentType = init.headers.get('Content-Type') || '';
            } else if (Array.isArray(init.headers)) {
              for (var i = 0; i < init.headers.length; i++) {
                var pair = init.headers[i];
                if (pair && String(pair[0]).toLowerCase() === 'content-type') {
                  contentType = pair[1] || '';
                  break;
                }
              }
            } else {
              contentType = init.headers['Content-Type'] || init.headers['content-type'] || '';
            }
          }
          if (String(contentType).toLowerCase().indexOf('application/json') !== -1) {
            if (init && typeof init.body === 'string') {
              tryTrackJsonLead(init.body);
            } else if (input && typeof input.clone === 'function') {
              input.clone().text().then(function(textBody) {
                tryTrackJsonLead(textBody);
              }).catch(function(error) {
                safeLogError('Failed to read request body from fetch clone.', error);
              });
            }
          }
        }
      } catch (error) {
        safeLogError('Fetch interception failed.', error);
      }
      return nativeFetch(input, init);
    };
  }

  function updateScrollDepth() {
    try {
      var doc = document.documentElement || document.body;
      var scrollTop = window.pageYOffset || doc.scrollTop || 0;
      var viewportHeight = window.innerHeight || doc.clientHeight || 0;
      var fullHeight = Math.max(
        doc.scrollHeight || 0,
        document.body ? document.body.scrollHeight : 0
      );
      if (fullHeight <= 0) {
        return;
      }
      var percent = Math.floor(((scrollTop + viewportHeight) / fullHeight) * 100);
      var milestones = [25, 50, 75, 100];
      for (var i = milestones.length - 1; i >= 0; i--) {
        if (percent >= milestones[i]) {
          if (milestones[i] > maxScrollDepth) {
            maxScrollDepth = milestones[i];
          }
          break;
        }
      }
    } catch (_) {}
  }

  function trackClick(event) {
    try {
      var target = event.target;
      if (!target) {
        return;
      }
      var clickable = target.closest('button, a, input[type="submit"], [data-track]');
      if (!clickable) {
        return;
      }

      var elementText = getElementText(clickable);
      var elementId = (clickable.id || '').slice(0, 255);
      var elementClass = ((clickable.className || '') + '').trim().slice(0, 255);
      var fingerprint = window.location.pathname + '|' + elementId + '|' + elementText;
      if (sentClickFingerprints[fingerprint]) {
        return;
      }
      sentClickFingerprints[fingerprint] = true;

      sendAnalyticsEvent('click_event', {
        pathname: window.location.pathname,
        element_text: elementText,
        element_id: elementId,
        element_class: elementClass
      });
    } catch (error) {
      safeLogError('Failed to process click event.', error);
    }
  }

  function sendSessionEnd() {
    var durationSeconds = Math.max(0, Math.round((Date.now() - pageStartTs) / 1000));
    sendAnalyticsEvent('session_end', {
      duration_seconds: durationSeconds,
      max_scroll_depth: maxScrollDepth,
      pathname: window.location.pathname
    });
  }

  try {
    maybeSendVisitOnce();
    sendPageView();
    document.addEventListener('submit', trackFormSubmit, true);
    document.addEventListener('click', trackClick, true);
    window.addEventListener('scroll', updateScrollDepth, { passive: true });
    window.addEventListener('beforeunload', sendSessionEnd);
    interceptFetch();
    updateScrollDepth();
  } catch (error) {
    safeLogError('Tracker initialization failed.', error);
  }
})();
"""
    return HttpResponse(script, content_type="application/javascript; charset=utf-8")
