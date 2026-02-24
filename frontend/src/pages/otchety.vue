<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";

definePageMeta({
  publicPage: true,
  pageHeading: "Отчеты",
  pageText:
    "Формируйте регулярные отчеты по ключевым метрикам: заявкам, источникам и конверсии. Подходит для собственника, маркетолога и отдела продаж.",
  seo: {
    title: "Отчеты TrackNode — ежедневные и PDF-отчеты по заявкам и воронке",
    description:
      "Создавайте отчеты по заявкам и воронке продаж в TrackNode: ежедневная статистика, PDF-выгрузка и прозрачные показатели для бизнеса.",
    keywords: "отчеты по лидам, PDF отчет, отчеты аналитики, TrackNode",
    ogType: "website",
  },
});
</script>
