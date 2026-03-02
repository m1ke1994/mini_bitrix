export default defineNuxtConfig({
  modules: ["@nuxtjs/tailwindcss"],
  css: ["~/assets/css/main.css"],
  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_URL || "",
    },
  },
  nitro: {
    output: {
      publicDir: "../frontend/landing_dist",
    },
    prerender: {
      crawlLinks: false,
      routes: ["/"],
    },
  },
  app: {
    buildAssetsDir: "/landing_assets/",
    head: {
      htmlAttrs: { lang: "ru" },
      title: "TrackNode",
      meta: [
        {
          name: "description",
          content: "Премиальная аналитика сайта и контроль заявок",
        },
      ],
    },
  },
});
