<template>
  <AboutProject />
</template>

<script setup>
import AboutProject from "~/views/AboutProject.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";
import { createFaqSchema, getCanonicalUrl } from "~/seo";

const aboutFaqSchema = createFaqSchema(getPublicSeoContent("/about")?.faqItems || []);

definePageMeta({
  layout: "app",
  publicPage: true,
  seo: {
    title: "О TrackNode: сервис аналитики сайта и контроля заявок",
    description:
      "TrackNode объединяет аналитику сайта, отслеживание лидов, учет заявок и Telegram-уведомления, чтобы бизнес быстрее реагировал на обращения и повышал конверсию.",
    keywords:
      "о TrackNode, аналитика сайта, отслеживание лидов, учет заявок, SEO-оптимизация, уведомления в Telegram",
    canonical: getCanonicalUrl("/about"),
    ogType: "website",
    schema: [aboutFaqSchema].filter(Boolean),
  },
});
</script>
