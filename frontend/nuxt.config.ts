// nuxt.config.ts
export default defineNuxtConfig({
  srcDir: "src/",
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
    },
  },

  nitro: {
    compressPublicAssets: true,
    /**
     * ⚠️ ВАЖНО:
     * publicAssets с baseURL "/" будет раздавать файлы из landing_dist прямо из корня.
     * Если в landing_dist есть index.html, он может перебивать SSR-страницу "/".
     *
     * Так как лендинг у нас должен быть SSR для SEO — не раздаём landing_dist в "/".
     * Оставляем папку доступной по отдельному префиксу, чтобы не было конфликтов.
     */
    publicAssets: [
      {
        dir: "landing_dist",
        baseURL: "/landing_dist",
      },
    ],
  },

  routeRules: {
    // ✅ Лендинг/SEO-страницы — SSR
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

    // ✅ Дашборд и кабинет — SPA (SSR выключен)
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

    // Если это тоже разделы кабинета — оставляем SPA
    "/settings": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/account": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/integration": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/reports": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
    "/instructions": {
      ssr: false,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
  },

  app: {
    head: {
      htmlAttrs: {
        lang: "ru",
      },
      viewport: "width=device-width, initial-scale=1",

      meta: [{ name: "theme-color", content: "#2ba8d8" }],

      link: [
        { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
        { rel: "icon", type: "image/png", href: "/favicon.png" },
        { rel: "apple-touch-icon", href: "/apple-touch-icon.png" },
        { rel: "manifest", href: "/manifest.webmanifest" },
        { rel: "mask-icon", href: "/safari-pinned-tab.svg", color: "#2ba8d8" },
      ],

      // ✅ Встраиваем ваш трекер TrackNode
      script: [
        {
          src: "https://tracknode.ru/tracker.js",
          "data-api-key": "obo5CDD4lMSLT_afuLT3QtuD_34u2bdF_sEfTFp5Zyk",
          defer: true,
        },
      ],
    },
  },
});