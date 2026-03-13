import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig(({ mode }) => {
  const plugins = [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      injectRegister: "auto",
      includeAssets: [
        "favicon.svg",
        "favicon.png",
        "apple-touch-icon.png",
        "safari-pinned-tab.svg",
        "manifest.webmanifest",
        "pwa-192x192.png",
        "pwa-512x512.png",
        "og-preview.jpg",
        "robots.txt",
        "sitemap.xml",
      ],
      manifest: false,
      workbox: {
        cleanupOutdatedCaches: true,
        clientsClaim: true,
        skipWaiting: true,
        navigationPreload: true,
        globIgnores: ["**/bundle-stats.html"],
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
  ];

  if (mode === "analyze") {
    plugins.push(
      visualizer({
        filename: "dist/bundle-stats.html",
        open: false,
        gzipSize: true,
        brotliSize: true,
      })
    );
  }

  return {
    plugins,
    server: {
      host: true,
      port: 9003,
      allowedHosts: ["tracknode.ru"],
    },
  };
});
