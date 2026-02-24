<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
const SITE_NAME = "TrackNode";
const BASE_URL = "https://tracknode.ru";
const DEFAULT_TITLE = "Аналитика сайтов и учет заявок — сервис отслеживания лидов | TrackNode";
const DEFAULT_DESCRIPTION =
  "Сервис аналитики сайтов и учета заявок. Отслеживайте лиды, конверсию и путь клиента. Аналитика воронки продаж и Telegram-уведомления в одном кабинете.";
const DEFAULT_KEYWORDS =
  "аналитика сайтов, сервис аналитики, учет заявок, аналитика воронки продаж, отслеживание конверсии, TrackNode";
const DEFAULT_IMAGE = `${BASE_URL}/og-preview.jpg`;
const DEFAULT_OG_IMAGE_ALT = "аналитика сайтов интерфейс";
const DEFAULT_TWITTER_IMAGE_ALT = "учет заявок дашборд";

const route = useRoute();

useHead(() => {
  const meta = route.meta || {};
  const seo = meta.seo || {};

  const title = seo.title || DEFAULT_TITLE;
  const description = seo.description || DEFAULT_DESCRIPTION;
  const keywords = seo.keywords || DEFAULT_KEYWORDS;
  const canonical = seo.canonical || `${BASE_URL}${route.path || "/"}`;
  const noindex = Boolean(meta.noindex || seo.noindex);
  const robots = noindex ? "noindex,nofollow" : "index,follow";
  const schema = seo.schema || null;

  const scripts = schema
    ? [
        {
          type: "application/ld+json",
          children: JSON.stringify(schema),
        },
      ]
    : [];

  return {
    title,
    meta: [
      { name: "description", content: description },
      { name: "keywords", content: keywords },
      { name: "robots", content: robots },
      { name: "application-name", content: SITE_NAME },
      { name: "apple-mobile-web-app-title", content: SITE_NAME },
      { property: "og:title", content: seo.ogTitle || title },
      { property: "og:description", content: seo.ogDescription || description },
      { property: "og:url", content: seo.ogUrl || canonical },
      { property: "og:type", content: seo.ogType || "website" },
      { property: "og:image", content: seo.ogImage || DEFAULT_IMAGE },
      {
        property: "og:image:alt",
        content: seo.ogImageAlt || DEFAULT_OG_IMAGE_ALT,
      },
      { name: "twitter:card", content: seo.twitterCard || "summary_large_image" },
      {
        name: "twitter:image:alt",
        content: seo.twitterImageAlt || DEFAULT_TWITTER_IMAGE_ALT,
      },
    ],
    link: [{ rel: "canonical", href: canonical }],
    script: scripts,
  };
});
</script>
