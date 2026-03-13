export default defineNuxtPlugin(() => {
  const runtimeConfig = useRuntimeConfig();
  const trackerSrc = String(runtimeConfig.public.tracknodeTrackerSrc || "").trim();
  const apiKey = String(runtimeConfig.public.tracknodeApiKey || "").trim();

  if (!trackerSrc || !apiKey) return;
  if (typeof document === "undefined") return;
  if (document.getElementById("tracknode-tracker-script")) return;
  if (!document.head) return;

  const script = document.createElement("script");
  script.id = "tracknode-tracker-script";
  script.src = trackerSrc;
  script.async = true;
  script.setAttribute("data-api-key", apiKey);

  document.head.appendChild(script);
});
