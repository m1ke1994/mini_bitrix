<template>
  <DashboardSeoAudit />
</template>

<script setup>
import DashboardSeoAudit from "~/views/DashboardSeoAudit.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "SEO-аудит сайта: что чинить первым",
    description: "Продуктовый SEO-аудит: приоритетный план исправлений, сравнение аудитов, коммерческая готовность страниц и экспорт отчёта.",
  },
});
</script>
