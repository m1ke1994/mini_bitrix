(function () {
  "use strict";

  function getCurrentScript() {
    if (document.currentScript) return document.currentScript;
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var s = scripts[i];
      if (s && s.src && s.src.indexOf("/widget.js") !== -1) return s;
    }
    return null;
  }

  var script = getCurrentScript();
  if (!script || window.__tracknodeWidgetInitialized) return;

  var apiKey = (script.getAttribute("data-key") || script.getAttribute("data-api-key") || "").trim();
  if (!apiKey) return;
  window.__tracknodeWidgetInitialized = true;

  function boolAttr(name, defaultValue) {
    var raw = (script.getAttribute(name) || "").trim().toLowerCase();
    if (!raw) return defaultValue;
    return !(raw === "0" || raw === "false" || raw === "no");
  }

  var config = {
    position: (script.getAttribute("data-position") || "bottom-right").trim(),
    color: (script.getAttribute("data-color") || "#3B82F6").trim(),
    title: (script.getAttribute("data-title") || "Оставьте заявку").trim(),
    submitText: (script.getAttribute("data-submit-text") || "Отправить").trim(),
    callbackText: (script.getAttribute("data-callback-text") || "Перезвоните мне").trim(),
    delayMs: parseInt(script.getAttribute("data-delay-ms") || "15000", 10),
    exitIntent: boolAttr("data-exit-intent", true),
  };

  if (!isFinite(config.delayMs) || config.delayMs < 0) config.delayMs = 15000;

  var src = script.src || "";
  var baseOrigin = "";
  try {
    baseOrigin = new URL(src, window.location.href).origin;
  } catch (_) {
    baseOrigin = window.location.origin;
  }

  var visitorIdKey = "tracknode_widget_visitor_id";
  var sessionIdKey = "tracknode_widget_session_id";
  function createId() {
    try {
      if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
    } catch (_) {}
    return "wid-" + Date.now() + "-" + Math.random().toString(16).slice(2);
  }
  function getStorage(storage, key) {
    try {
      return storage.getItem(key) || "";
    } catch (_) {
      return "";
    }
  }
  function setStorage(storage, key, value) {
    try {
      storage.setItem(key, value);
    } catch (_) {}
  }

  var visitorId = getStorage(window.localStorage, visitorIdKey);
  if (!visitorId) {
    visitorId = createId();
    setStorage(window.localStorage, visitorIdKey, visitorId);
  }
  var sessionId = getStorage(window.sessionStorage, sessionIdKey);
  if (!sessionId) {
    sessionId = createId();
    setStorage(window.sessionStorage, sessionIdKey, sessionId);
  }

  function safeFetch(path, opts) {
    var url = baseOrigin + path;
    var request = opts || {};
    request.headers = Object.assign(
      {
        "Content-Type": "application/json",
        "X-API-KEY": apiKey,
      },
      request.headers || {}
    );
    return fetch(url, request);
  }

  function collectUtm() {
    var data = {
      utm_source: null,
      utm_medium: null,
      utm_campaign: null,
      source_url: window.location.href,
      referrer: document.referrer || "",
    };
    try {
      var p = new URLSearchParams(window.location.search || "");
      data.utm_source = p.get("utm_source");
      data.utm_medium = p.get("utm_medium");
      data.utm_campaign = p.get("utm_campaign");
    } catch (_) {}
    return data;
  }

  var selectedVariantId = null;
  function applyVariant(variant) {
    if (!variant || !variant.config) return;
    selectedVariantId = variant.id || null;
    var cfg = variant.config || {};
    if (cfg.title) config.title = String(cfg.title).slice(0, 120);
    if (cfg.color) config.color = String(cfg.color).slice(0, 20);
    if (cfg.submitText) config.submitText = String(cfg.submitText).slice(0, 40);
    if (cfg.position) config.position = String(cfg.position).slice(0, 30);
  }

  render();
  safeFetch(
    "/api/public/widget/variant/?session_id=" +
      encodeURIComponent(sessionId) +
      "&visitor_id=" +
      encodeURIComponent(visitorId)
  )
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (json) {
      if (!json || !json.variant) return;
      applyVariant(json.variant);
      var titleNode = shadow && shadow.getElementById("tnwTitle");
      var submitNode = shadow && shadow.getElementById("tnwSubmit");
      var wrapNode = shadow && shadow.querySelector(".tnw-wrap");
      if (titleNode) titleNode.textContent = config.title;
      if (submitNode) submitNode.textContent = config.submitText;
      if (wrapNode) wrapNode.style.setProperty("--tnw-color", config.color);
    })
    .catch(function () {});

  var rootNode = null;
  var shadow = null;
  var isOpen = false;
  var hasShown = false;
  var hasSubmitted = false;

  function render() {
    if (rootNode) return;

    rootNode = document.createElement("div");
    rootNode.setAttribute("id", "tracknode-widget-root");
    shadow = rootNode.attachShadow({ mode: "open" });
    document.body.appendChild(rootNode);

    var side = config.position.indexOf("left") !== -1 ? "left" : "right";
    var style = [
      ":host { all: initial; }",
      ".tnw-wrap { --tnw-color: " + config.color + "; position: fixed; bottom: 20px; " + side + ": 20px; z-index: 2147483000; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif; }",
      ".tnw-btn { width: 58px; height: 58px; border-radius: 999px; border: 0; color: #fff; background: var(--tnw-color); cursor: pointer; box-shadow: 0 10px 24px rgba(0,0,0,.2); font-size: 22px; }",
      ".tnw-panel { width: min(360px, calc(100vw - 30px)); background: #fff; border-radius: 16px; box-shadow: 0 18px 42px rgba(2, 6, 23, .24); overflow: hidden; margin-bottom: 10px; display: none; border: 1px solid #e2e8f0; }",
      ".tnw-panel.open { display: block; animation: tnwSlide .2s ease-out; }",
      ".tnw-head { padding: 14px 16px; background: #0f172a; color: #fff; display: flex; align-items: center; justify-content: space-between; gap: 12px; }",
      ".tnw-title { font-size: 16px; font-weight: 700; margin: 0; line-height: 1.2; }",
      ".tnw-close { border: 0; background: transparent; color: #cbd5e1; cursor: pointer; font-size: 18px; }",
      ".tnw-body { padding: 14px 16px 16px; display: grid; gap: 10px; }",
      ".tnw-input,.tnw-textarea { width: 100%; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 12px; font-size: 14px; }",
      ".tnw-input:focus,.tnw-textarea:focus { outline: none; border-color: var(--tnw-color); box-shadow: 0 0 0 3px rgba(59,130,246,.14); }",
      ".tnw-textarea { min-height: 88px; resize: vertical; }",
      ".tnw-submit,.tnw-callback { border: 0; border-radius: 10px; min-height: 40px; cursor: pointer; font-size: 14px; font-weight: 600; }",
      ".tnw-submit { background: var(--tnw-color); color: #fff; }",
      ".tnw-callback { background: #eef2ff; color: #1e293b; }",
      ".tnw-status { min-height: 20px; font-size: 13px; color: #334155; }",
      ".tnw-status.error { color: #b91c1c; }",
      ".tnw-status.success { color: #15803d; }",
      "@keyframes tnwSlide { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }",
    ].join("");

    var html = [
      '<style>' + style + "</style>",
      '<div class="tnw-wrap">',
      '  <div class="tnw-panel" id="tnwPanel">',
      '    <div class="tnw-head">',
      '      <h3 class="tnw-title" id="tnwTitle"></h3>',
      '      <button type="button" class="tnw-close" id="tnwClose" aria-label="Закрыть">✕</button>',
      "    </div>",
      '    <form class="tnw-body" id="tnwForm" novalidate>',
      '      <input class="tnw-input" name="name" placeholder="Ваше имя" autocomplete="name" />',
      '      <input class="tnw-input" name="phone" placeholder="Телефон" autocomplete="tel" />',
      '      <input class="tnw-input" name="email" placeholder="Email" autocomplete="email" />',
      '      <textarea class="tnw-textarea" name="message" placeholder="Сообщение"></textarea>',
      '      <button type="submit" class="tnw-submit" id="tnwSubmit"></button>',
      '      <button type="button" class="tnw-callback" id="tnwCallback"></button>',
      '      <div class="tnw-status" id="tnwStatus"></div>',
      "    </form>",
      "  </div>",
      '  <button type="button" class="tnw-btn" id="tnwLauncher" aria-label="Открыть форму">✉</button>',
      "</div>",
    ].join("");
    shadow.innerHTML = html;

    shadow.getElementById("tnwTitle").textContent = config.title;
    shadow.getElementById("tnwSubmit").textContent = config.submitText;
    shadow.getElementById("tnwCallback").textContent = config.callbackText;

    shadow.getElementById("tnwLauncher").addEventListener("click", function () {
      toggleOpen(!isOpen);
    });
    shadow.getElementById("tnwClose").addEventListener("click", function () {
      toggleOpen(false);
    });
    shadow.getElementById("tnwCallback").addEventListener("click", function () {
      var msg = shadow.querySelector('textarea[name="message"]');
      if (msg && !msg.value) msg.value = "Перезвоните мне, пожалуйста";
      var phone = shadow.querySelector('input[name="phone"]');
      if (phone) phone.focus();
    });
    shadow.getElementById("tnwForm").addEventListener("submit", handleSubmit);

    window.setTimeout(function () {
      if (!hasShown && !hasSubmitted) {
        toggleOpen(true);
      }
    }, config.delayMs);

    if (config.exitIntent) {
      document.addEventListener("mouseout", function (e) {
        if (hasShown || hasSubmitted) return;
        var to = e.relatedTarget || e.toElement;
        if (!to && e.clientY <= 0) toggleOpen(true);
      });
    }
  }

  function toggleOpen(next) {
    if (!shadow) return;
    isOpen = !!next;
    if (isOpen) hasShown = true;
    var panel = shadow.getElementById("tnwPanel");
    if (panel) panel.classList.toggle("open", isOpen);
  }

  function setStatus(text, kind) {
    if (!shadow) return;
    var node = shadow.getElementById("tnwStatus");
    if (!node) return;
    node.textContent = text || "";
    node.className = "tnw-status" + (kind ? " " + kind : "");
  }

  function valueOf(name) {
    if (!shadow) return "";
    var el = shadow.querySelector('[name="' + name + '"]');
    return el ? String(el.value || "").trim() : "";
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (hasSubmitted) return;

    var name = valueOf("name");
    var phone = valueOf("phone");
    var email = valueOf("email");
    var message = valueOf("message");
    if (!phone && !email && !message) {
      setStatus("Укажите телефон, email или сообщение.", "error");
      return;
    }

    hasSubmitted = true;
    setStatus("Отправляем...", "");

    var utm = collectUtm();
    var body = {
      name: name,
      phone: phone,
      email: email,
      message: message,
      source_url: utm.source_url,
      utm_source: utm.utm_source,
      utm_medium: utm.utm_medium,
      utm_campaign: utm.utm_campaign,
      session_id: sessionId,
      visitor_id: visitorId,
      variant_id: selectedVariantId,
    };

    safeFetch("/api/public/lead/", {
      method: "POST",
      body: JSON.stringify(body),
      keepalive: true,
    })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP_" + res.status);
        return res.json();
      })
      .then(function () {
        setStatus("Спасибо! Заявка отправлена.", "success");
        window.setTimeout(function () {
          toggleOpen(false);
        }, 1200);
      })
      .catch(function () {
        hasSubmitted = false;
        setStatus("Не удалось отправить. Попробуйте ещё раз.", "error");
      });
  }

})();
