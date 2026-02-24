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
  routeRules: {
    "/dashboard": { ssr: false },
    "/dashboard/**": { ssr: false },
    "/settings": { ssr: false },
    "/account": { ssr: false },
    "/integration": { ssr: false },
    "/reports": { ssr: false },
    "/about": { ssr: false },
    "/instructions": { ssr: false },
  },
  app: {
    head: {
      htmlAttrs: {
        lang: "ru",
      },
      viewport: "width=device-width, initial-scale=1",
      link: [
        { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
        { rel: "icon", type: "image/png", href: "/favicon.png" },
      ],
    },
  },
});
