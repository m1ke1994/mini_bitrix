const tracknodeTrackerSrc = process.env.NUXT_PUBLIC_TRACKNODE_TRACKER_SRC || "https://tracknode.ru/tracker.js";
const tracknodeApiKey = process.env.NUXT_PUBLIC_TRACKNODE_API_KEY || "";

export default defineNuxtConfig({
  srcDir: "src/",
  dir: {
    public: "../public",
  },
  ssr: true,
  devServer: {
    host: "0.0.0.0",
    port: 9003,
  },
  css: ["~/style.css"],
  modules: ["@pinia/nuxt"],
  runtimeConfig: {
    public: {
      apiBase: process.env.VITE_API_BASE || process.env.VITE_API_BASE_URL || "/",
      tracknodeTrackerSrc,
      tracknodeApiKey,
    },
  },
  nitro: {
    compressPublicAssets: true,
  },
  routeRules: {
    "/": {
      ssr: true,
      headers: {
        "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      },
    },
    "/about": {
      ssr: true,
      headers: {
        "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      },
    },
    "/analitika": {
      ssr: true,
      headers: {
        "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      },
    },
    "/otchety": {
      ssr: true,
      headers: {
        "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      },
    },
    "/tarify": {
      ssr: true,
      headers: {
        "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      },
    },
    "/telegram": {
      ssr: true,
      headers: {
        "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      },
    },
    "/dashboard": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/dashboard/**": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/app": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/app/**": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/settings": { ssr: false },
    "/account": { ssr: false },
    "/integration": { ssr: false },
    "/reports": { ssr: false },
    "/instructions": { ssr: false },
  },
  app: {
    head: {
      htmlAttrs: {
        lang: "ru",
      },
      viewport: "width=device-width, initial-scale=1",
      meta: [
        { name: "theme-color", content: "#2ba8d8" },
        { name: "tracknode-config-test", content: "nuxt-config-active" },
      ],
      link: [
        { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
        { rel: "icon", type: "image/png", href: "/favicon.png" },
        { rel: "apple-touch-icon", href: "/apple-touch-icon.png" },
        { rel: "manifest", href: "/manifest.webmanifest" },
        { rel: "mask-icon", href: "/safari-pinned-tab.svg", color: "#2ba8d8" },
      ],
      script: [
        {
          id: "tracknode-tracker-script",
          key: "tracknode-tracker-script",
          src: tracknodeTrackerSrc,
          async: true,
          "data-api-key": tracknodeApiKey,
        },
      ],
    },
  },
});
