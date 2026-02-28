<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";
import { createFaqSchema, createServiceSchema, getCanonicalUrl } from "~/seo";

const analitikaFaqSchema = createFaqSchema(getPublicSeoContent("/analitika")?.faqItems || []);
const analitikaServiceSchema = createServiceSchema({
  name: "Аналитика сайта TrackNode",
  description:
    "Сервис для контроля трафика, лидов, поведения пользователя на сайте и конверсии по ключевым страницам.",
  path: "/analitika",
});

definePageMeta({
  publicPage: true,
  pageHeading: "Аналитика сайтов",
  pageText:
    "TrackNode показывает источники трафика, путь пользователя, динамику заявок и конверсию, чтобы находить точки роста и вовремя усиливать эффективные каналы.",
  seo: {
    title: "Аналитика сайта TrackNode: трафик, лиды и конверсия",
    description:
      "Аналитика сайта в TrackNode помогает контролировать источники трафика, поведение на сайте, отслеживание лидов и конверсию страниц для роста заявок и продаж.",
    keywords:
      "аналитика сайта, анализ сайтов, отслеживание лидов, источники трафика, поведение пользователя на сайте, конверсия",
    canonical: getCanonicalUrl("/analitika"),
    ogType: "website",
    schema: [analitikaServiceSchema, analitikaFaqSchema].filter(Boolean),
  },
});
</script>
