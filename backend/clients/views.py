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
    if (document.currentScript) {
      return document.currentScript;
    }
    var scripts = document.getElementsByTagName('script');
    return scripts && scripts.length ? scripts[scripts.length - 1] : null;
  }

  function createSessionId() {
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
  var token = scriptTag && scriptTag.dataset ? (scriptTag.dataset.token || scriptTag.dataset.apiKey || '') : '';
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

  var baseUrl = getBaseUrl(scriptTag);
  var visitorKey = 'saas_tracker_visitor_id';
  var sessionKey = 'saas_tracker_session_id';
  var startKey = 'saas_tracker_started_at';

  var visitorId = safeGet(window.localStorage, visitorKey);
  if (!visitorId) {
    visitorId = createSessionId();
    safeSet(window.localStorage, visitorKey, visitorId);
  }

  var sessionId = safeGet(window.sessionStorage, sessionKey);
  if (!sessionId) {
    sessionId = createSessionId();
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
      return fetch(url, {
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
          throw new Error('HTTP ' + response.status);
        }
        logDebug('success', endpoint, 'status', response.status);
        return response;
      }).catch(function (err) {
        logWarn('request failed', endpoint, 'attempt', attempt, err && err.message ? err.message : err);
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
    var fingerprint = window.location.pathname + window.location.search + '|' + (document.title || '');
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
        action: form.action || '',
        method: (form.method || 'GET').toUpperCase(),
        path: window.location.pathname
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
        setTimeout(trackPageView, 0);
        return result;
      };
      history.replaceState = function () {
        var result = originalReplace.apply(this, arguments);
        setTimeout(trackPageView, 0);
        return result;
      };
      window.addEventListener('popstate', function () {
        trackPageView();
      });
    } catch (err) {
      logError('history tracking failed', err);
    }
  }

  try {
    logDebug('init handlers');
    trackVisitStart();
    trackPageView();
    document.addEventListener('click', onClick, true);
    document.addEventListener('submit', onSubmit, true);
    window.addEventListener('beforeunload', trackVisitEnd);
    window.addEventListener('pagehide', trackVisitEnd);
    wrapHistory();
    logDebug('init complete');
  } catch (err) {
    logError('tracker init failed', err);
  }
})();
"""
    return HttpResponse(script, content_type="application/javascript; charset=utf-8")
