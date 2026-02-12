from accounts.permissions import IsClientUser
from clients.serializers import ClientSettingsSerializer
from django.http import HttpResponse
from rest_framework import generics, permissions


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

  function getUtms(url) {
    var params = new URL(url).searchParams;
    return {
      utm_source: params.get('utm_source') || null,
      utm_medium: params.get('utm_medium') || null,
      utm_campaign: params.get('utm_campaign') || null
    };
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

  function sendPayload(endpoint, payload) {
    var url = baseUrl + endpoint + '?api_key=' + encodeURIComponent(apiKey);
    var body = JSON.stringify(payload);

    if (navigator.sendBeacon) {
      try {
        var blob = new Blob([body], { type: 'application/json' });
        var beaconOk = navigator.sendBeacon(url, blob);
        if (beaconOk) {
          return;
        }
      } catch (error) {
        safeLogError('sendBeacon failed for ' + endpoint, error);
      }
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

  var nativeFetch = window.fetch ? window.fetch.bind(window) : null;
  if (!nativeFetch) {
    safeLogError('window.fetch is not available.');
    return;
  }

  function basePayload() {
    var url = window.location.href;
    return Object.assign(
      {
        source_url: url,
        page_url: url
      },
      getUtms(url)
    );
  }

  function sendVisit() {
    var payload = basePayload();
    payload.event_type = 'visit';
    sendPayload('/api/public/event/', payload);
  }

  function trackFormSubmit(event) {
    try {
      var form = event.target;
      if (!form || form.tagName !== 'FORM') {
        return;
      }
      var payload = basePayload();
      var nameValue = firstFieldValue(form, ['name', 'fullname', 'fio']);
      var phoneValue = firstFieldValue(form, ['phone', 'tel', 'mobile']);
      var emailValue = firstFieldValue(form, ['email', 'e-mail']);
      var messageValue = firstFieldValue(form, ['message', 'comment', 'text']);

      if (nameValue) { payload.name = nameValue; }
      if (phoneValue) { payload.phone = phoneValue; }
      if (emailValue) { payload.email = emailValue; }
      if (messageValue) { payload.message = messageValue; }

      sendPayload('/api/public/lead/', payload);
      sendPayload('/api/public/event/', {
        event_type: 'form_submit',
        page_url: payload.page_url,
        element_id: form.id || null
      });
    } catch (error) {
      safeLogError('Failed to process submit event.', error);
    }
  }

  function normalizeString(value) {
    if (typeof value !== 'string') {
      return null;
    }
    var trimmed = value.trim();
    return trimmed ? trimmed : null;
  }

  function pickFromObject(data, aliases) {
    if (!data || typeof data !== 'object') {
      return null;
    }
    var keys = Object.keys(data);
    for (var i = 0; i < aliases.length; i++) {
      var alias = aliases[i].toLowerCase();
      for (var j = 0; j < keys.length; j++) {
        var key = keys[j];
        var lowKey = key.toLowerCase();
        if (lowKey === alias || lowKey.indexOf(alias) !== -1) {
          var picked = data[key];
          if (typeof picked === 'number') {
            picked = String(picked);
          }
          var normalized = normalizeString(picked);
          if (normalized) {
            return normalized;
          }
        }
      }
    }
    return null;
  }

  function extractLeadFromObject(data) {
    if (!data || typeof data !== 'object') {
      return null;
    }
    var parsedPayload = basePayload();
    var nameValue = pickFromObject(data, ['name', 'fullname', 'fio']);
    var phoneValue = pickFromObject(data, ['phone', 'tel', 'mobile']);
    var emailValue = pickFromObject(data, ['email', 'e-mail']);
    var messageValue = pickFromObject(data, ['message', 'comment', 'text']);

    if (nameValue) { parsedPayload.name = nameValue; }
    if (phoneValue) { parsedPayload.phone = phoneValue; }
    if (emailValue) { parsedPayload.email = emailValue; }
    if (messageValue) { parsedPayload.message = messageValue; }

    if (!parsedPayload.name && !parsedPayload.phone && !parsedPayload.email && !parsedPayload.message) {
      return null;
    }
    return parsedPayload;
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
      console.log('Tracker intercepted lead:', leadPayload);
      sendPayload('/api/public/lead/', leadPayload);
      sendPayload('/api/public/event/', {
        event_type: 'form_submit',
        page_url: leadPayload.page_url,
        element_id: 'fetch_json'
      });
    } catch (error) {
      safeLogError('Failed to parse JSON fetch body.', error);
    }
  }

  function shouldSkipTrackedRequest(url) {
    return (
      typeof url === 'string' &&
      (url.indexOf('/api/public/lead/') !== -1 || url.indexOf('/api/public/event/') !== -1)
    );
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
                var headerPair = init.headers[i];
                if (headerPair && String(headerPair[0]).toLowerCase() === 'content-type') {
                  contentType = headerPair[1] || '';
                  break;
                }
              }
            } else {
              contentType = init.headers['Content-Type'] || init.headers['content-type'] || '';
            }
          }
          if (!contentType && input && input.headers && typeof input.headers.get === 'function') {
            contentType = input.headers.get('Content-Type') || '';
          }

          if (String(contentType).toLowerCase().indexOf('application/json') !== -1) {
            if (init && typeof init.body === 'string') {
              tryTrackJsonLead(init.body);
            } else if (input && typeof input.clone === 'function') {
              input.clone().text().then(function(textBody) {
                tryTrackJsonLead(textBody);
              }).catch(function(error) {
                safeLogError('Failed to read request body from clone().', error);
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

  try {
    sendVisit();
    document.addEventListener('submit', trackFormSubmit, true);
    interceptFetch();
  } catch (error) {
    safeLogError('Tracker initialization failed.', error);
  }
})();
"""
    return HttpResponse(script, content_type="application/javascript; charset=utf-8")
