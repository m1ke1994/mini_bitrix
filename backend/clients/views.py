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

  function isEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i.test(value);
  }

  function isPhone(value) {
    var normalized = String(value).replace(/[^\d+]/g, '');
    var digits = normalized.replace(/\D/g, '');
    return digits.length >= 7;
  }

  function collectFormFields(form) {
    var fields = [];
    var nodes = form.querySelectorAll('input, textarea, select');
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (!node) { continue; }
      var key = (node.name || node.id || '').trim();
      var rawValue = typeof node.value === 'string' ? node.value.trim() : '';
      if (!rawValue) { continue; }
      fields.push({ key: key, value: rawValue });
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
          fields.push({ key: path || '', value: value });
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

    function setNameIfMissing(value) {
      if (!extracted.name && value) { extracted.name = value; }
    }
    function setEmailIfMissing(value) {
      if (!extracted.email && value) { extracted.email = value; }
    }
    function setPhoneIfMissing(value) {
      if (!extracted.phone && value) { extracted.phone = value; }
    }
    function setMessageIfMissing(value) {
      if (!extracted.message && value) { extracted.message = value; }
    }

    for (var i = 0; i < fields.length; i++) {
      var item = fields[i];
      var key = (item.key || '').toLowerCase();
      var value = item.value;
      if (!value) { continue; }

      if (key.indexOf('name') !== -1 || key.indexOf('fullname') !== -1 || key.indexOf('fio') !== -1) {
        setNameIfMissing(value);
      }
      if (key.indexOf('message') !== -1 || key.indexOf('comment') !== -1 || key.indexOf('text') !== -1) {
        setMessageIfMissing(value);
      }

      if (key === 'contact' || key.indexOf('contact') !== -1 || key.indexOf('user_contact') !== -1) {
        if (isEmail(value)) {
          setEmailIfMissing(value);
        } else if (isPhone(value)) {
          setPhoneIfMissing(value);
        }
      }

      if (
        key === 'email' ||
        key === 'email_address' ||
        key.indexOf('mail') !== -1
      ) {
        if (isEmail(value)) {
          setEmailIfMissing(value);
        }
      }

      if (
        key === 'phone' ||
        key === 'phone_number' ||
        key === 'tel' ||
        key.indexOf('phone') !== -1 ||
        key.indexOf('tel') !== -1
      ) {
        if (isPhone(value)) {
          setPhoneIfMissing(value);
        }
      }
    }

    for (var j = 0; j < fields.length; j++) {
      var candidate = fields[j].value;
      if (!candidate) { continue; }
      if (!extracted.email && isEmail(candidate)) {
        extracted.email = candidate;
      }
      if (!extracted.phone && isPhone(candidate)) {
        extracted.phone = candidate;
      }
    }

    if (extracted.name) { payload.name = extracted.name; }
    if (extracted.email) { payload.email = extracted.email; }
    if (extracted.phone) { payload.phone = extracted.phone; }
    if (extracted.message) { payload.message = extracted.message; }

    return extracted;
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
      var fields = collectFormFields(form);
      var extracted = assignLeadFromFields(fields, payload);
      if (!payload.name) {
        payload.name = firstFieldValue(form, ['name', 'fullname', 'fio']);
      }
      if (!payload.message) {
        payload.message = firstFieldValue(form, ['message', 'comment', 'text']);
      }
      console.log('Tracker extracted lead:', {
        name: extracted.name || payload.name || null,
        email: extracted.email || payload.email || null,
        phone: extracted.phone || payload.phone || null
      });

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
    var payload = basePayload();
    var fields = collectObjectFields(data);
    var extracted = assignLeadFromFields(fields, payload);

    if (!payload.name) {
      payload.name = pickFromObject(data, ['name', 'fullname', 'fio']);
    }
    if (!payload.message) {
      payload.message = pickFromObject(data, ['message', 'comment', 'text']);
    }

    if (!payload.name && !payload.phone && !payload.email && !payload.message) {
      return null;
    }
    console.log('Tracker extracted lead:', {
      name: extracted.name || payload.name || null,
      email: extracted.email || payload.email || null,
      phone: extracted.phone || payload.phone || null
    });
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
