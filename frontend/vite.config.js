import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      injectRegister: "auto",
      includeAssets: ["favicon.svg", "favicon.png", "og-preview.jpg", "robots.txt", "sitemap.xml"],
      manifest: {
        name: "TrackNode",
        short_name: "TrackNode",
        description: "SaaS аналитика сайтов и система отслеживания заявок",
        start_url: "/",
        scope: "/",
        display: "standalone",
        background_color: "#ffffff",
        theme_color: "#1e3a8a",
        orientation: "portrait",
        icons: [
          {
            src: "/favicon.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable",
          },
          {
            src: "/favicon.svg",
            sizes: "any",
            type: "image/svg+xml",
            purpose: "any",
          },
        ],
      },
      workbox: {
        cleanupOutdatedCaches: true,
        clientsClaim: true,
        skipWaiting: true,
        navigateFallback: "/index.html",
        navigateFallbackDenylist: [/^\/api\//, /^\/dashboard(\/|$)/, /^\/settings(\/|$)/],
        runtimeCaching: [
          {
            urlPattern: ({ url }) => /\/api\//.test(url.pathname),
            handler: "NetworkOnly",
          },
          {
            urlPattern: ({ request, url }) =>
              request.destination === "document" &&
              !url.pathname.startsWith("/dashboard") &&
              !url.pathname.startsWith("/settings") &&
              !url.pathname.startsWith("/api/"),
            handler: "NetworkFirst",
            options: {
              cacheName: "html-pages",
              networkTimeoutSeconds: 5,
            },
          },
          {
            urlPattern: ({ request }) =>
              request.destination === "style" ||
              request.destination === "script" ||
              request.destination === "font" ||
              request.destination === "image",
            handler: "CacheFirst",
            options: {
              cacheName: "static-assets",
              expiration: {
                maxEntries: 120,
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
            },
          },
        ],
      },
      devOptions: {
        enabled: false,
      },
    }),
  ],
  server: {
    host: true,
    port: 9003,
    allowedHosts: ["tracknode.ru"],
  },
});
