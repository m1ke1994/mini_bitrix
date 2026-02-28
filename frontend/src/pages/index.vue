<template>
  <PublicHomePage />
</template>

<script setup>
import PublicHomePage from "~/views/PublicHomePage.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";
import { createFaqSchema, getCanonicalUrl, homepageSoftwareSchema } from "~/seo";

const homeFaqSchema = createFaqSchema(getPublicSeoContent("/")?.faqItems || []);

definePageMeta({
  publicPage: true,
  seo: {
    title: "TrackNode: аналитика сайта и учет заявок с Telegram",
    description:
      "TrackNode объединяет аналитику сайта, учет заявок и уведомления в Telegram, чтобы контролировать лиды, источники трафика и конверсию без потери обращений.",
    keywords:
      "анализ сайтов, аналитика сайта, SEO-оптимизация, отслеживание лидов, уведомления в Telegram, учет заявок, конверсия",
    canonical: getCanonicalUrl("/"),
    ogType: "website",
    schema: [...homepageSoftwareSchema, homeFaqSchema].filter(Boolean),
  },
});
</script>
