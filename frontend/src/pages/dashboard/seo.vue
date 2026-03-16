<template>
  <DashboardSeoAudit />
</template>

<script setup>
import DashboardSeoAudit from "~/views/DashboardSeoAudit.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "SEO-аудит сайта: что чинить первым",
    description: "SEO-аудит сайта: приоритетный план исправлений, группировка проблем, сравнение аудитов и экспорт отчёта.",
  },
});
</script>
