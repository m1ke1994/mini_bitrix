<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";
import { createFaqSchema, getCanonicalUrl } from "~/seo";

const tarifyFaqSchema = createFaqSchema(getPublicSeoContent("/tarify")?.faqItems || []);

definePageMeta({
  publicPage: true,
  pageHeading: "Тарифы",
  pageText:
    "Подберите тариф TrackNode под ваш бизнес: от быстрого старта для малого проекта до расширенного плана для команды и агентства с несколькими сайтами.",
  seo: {
    title: "Тарифы TrackNode: SaaS-аналитика для малого и среднего бизнеса",
    description:
      "Выберите тариф TrackNode для анализа сайтов, отслеживания лидов и учета заявок: понятная стоимость, быстрый запуск и масштабирование под рост проекта.",
    keywords:
      "тарифы аналитики сайта, SaaS аналитика, учет заявок, отслеживание лидов, конверсия сайта, TrackNode",
    canonical: getCanonicalUrl("/tarify"),
    ogType: "website",
    schema: [tarifyFaqSchema].filter(Boolean),
  },
});
</script>
