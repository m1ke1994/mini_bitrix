import {
  AUTH_NOINDEX_PATHS,
  PRIVATE_EXACT_PATHS,
  PRIVATE_GLOB_PATHS,
  PUBLIC_DYNAMIC_ROUTE_GLOBS,
  PUBLIC_STATIC_SEO_PATHS,
  TECHNICAL_NOINDEX_PATHS,
  getPublicPrerenderPaths,
} from "./src/data/seo-routes.js";

const tracknodeTrackerSrc = process.env.NUXT_PUBLIC_TRACKNODE_TRACKER_SRC || "https://tracknode.ru/tracker.js";
const tracknodeApiKey = process.env.NUXT_PUBLIC_TRACKNODE_API_KEY || "";
const PRERENDER_SEO_ROUTES = getPublicPrerenderPaths();
const PUBLIC_CACHE_CONTROL = "public, s-maxage=900, stale-while-revalidate=3600";
const NOINDEX_HEADERS = {
  "Cache-Control": "no-store",
  "X-Robots-Tag": "noindex,nofollow",
};

const PUBLIC_ROUTE_RULES = Object.fromEntries(
  [...new Set([...PUBLIC_STATIC_SEO_PATHS, ...PUBLIC_DYNAMIC_ROUTE_GLOBS])].map((path) => [
    path,
    {
      ssr: true,
      prerender: true,
      headers: {
        "Cache-Control": PUBLIC_CACHE_CONTROL,
      },
    },
  ]),
);

const PRIVATE_ROUTE_RULES = Object.fromEntries(
  [...new Set([...PRIVATE_EXACT_PATHS, ...PRIVATE_GLOB_PATHS])].map((path) => [
    path,
    {
      ssr: false,
      headers: NOINDEX_HEADERS,
    },
  ]),
);

const AUTH_ROUTE_RULES = Object.fromEntries(
  AUTH_NOINDEX_PATHS.map((path) => [
    path,
    {
      ssr: true,
      headers: NOINDEX_HEADERS,
    },
  ]),
);

const TECHNICAL_ROUTE_RULES = Object.fromEntries(
  TECHNICAL_NOINDEX_PATHS.map((path) => [
    path,
    {
      headers: {
        "X-Robots-Tag": "noindex,nofollow",
      },
    },
  ]),
);

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
    prerender: {
      crawlLinks: false,
      routes: PRERENDER_SEO_ROUTES,
    },
  },
  routeRules: {
    ...PUBLIC_ROUTE_RULES,
    ...PRIVATE_ROUTE_RULES,
    ...AUTH_ROUTE_RULES,
    ...TECHNICAL_ROUTE_RULES,
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
