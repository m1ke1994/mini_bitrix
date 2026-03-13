const TRACKER_SCRIPT_ID = "tracknode-tracker-script";
const LOG_PREFIX = "[TrackNode]";

function maskApiKey(value: string) {
  if (!value) return "(empty)";
  const clean = value.trim();
  if (!clean) return "(empty)";
  return `${clean.slice(0, 6)}...`;
}

export default defineNuxtPlugin((nuxtApp) => {
  const runtimeConfig = useRuntimeConfig();
  const trackerSrc = String(runtimeConfig.public.tracknodeTrackerSrc || "").trim();
  const apiKey = String(runtimeConfig.public.tracknodeApiKey || "").trim();

  console.info(`${LOG_PREFIX} plugin started`, {
    trackerSrc: trackerSrc || "(empty)",
    apiKeyPreview: maskApiKey(apiKey),
  });

  if (!trackerSrc || !apiKey) {
    console.warn(`${LOG_PREFIX} skipped: missing runtimeConfig values`, {
      hasTrackerSrc: Boolean(trackerSrc),
      hasApiKey: Boolean(apiKey),
    });
    return;
  }

  const ensureScript = () => {
    if (typeof document === "undefined") {
      console.warn(`${LOG_PREFIX} skipped: document is unavailable`);
      return;
    }
    if (!document.head) {
      console.warn(`${LOG_PREFIX} skipped: document.head is unavailable`);
      return;
    }

    const existing = document.getElementById(TRACKER_SCRIPT_ID);
    if (existing) {
      console.info(`${LOG_PREFIX} script already exists`, {
        id: TRACKER_SCRIPT_ID,
      });
      return;
    }

    const script = document.createElement("script");
    script.id = TRACKER_SCRIPT_ID;
    script.src = trackerSrc;
    script.async = true;
    script.setAttribute("data-api-key", apiKey);

    script.onload = () => {
      console.info(`${LOG_PREFIX} script loaded`, {
        src: trackerSrc,
      });
    };

    script.onerror = () => {
      console.warn(`${LOG_PREFIX} script failed to load`, {
        src: trackerSrc,
      });
    };

    document.head.appendChild(script);
    console.info(`${LOG_PREFIX} script appended`, {
      id: TRACKER_SCRIPT_ID,
      src: trackerSrc,
    });
  };

  if (typeof document === "undefined") {
    console.warn(`${LOG_PREFIX} skipped: document is unavailable before mount`);
    return;
  }

  if (document.readyState === "loading") {
    console.info(`${LOG_PREFIX} defer script insertion until app:mounted`);
    nuxtApp.hook("app:mounted", ensureScript);
    return;
  }

  ensureScript();
});
