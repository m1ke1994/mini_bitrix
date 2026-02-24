<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";

definePageMeta({
  publicPage: true,
  pageHeading: "Тарифы",
  pageText:
    "Подберите подходящий план для вашего бизнеса и начните работать с аналитикой сайта, отчетами и лидогенерацией в одном сервисе.",
  seo: {
    title: "Тарифы TrackNode — SaaS аналитика для малого и среднего бизнеса",
    description:
      "Выберите тариф TrackNode под ваш поток заявок: прозрачная цена, быстрый старт и инструменты аналитики без сложной настройки.",
    keywords: "тарифы аналитики сайта, цена saas, TrackNode тарифы",
    ogType: "website",
  },
});
</script>
