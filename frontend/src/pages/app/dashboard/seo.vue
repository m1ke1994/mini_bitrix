<template>
  <DashboardSeoAudit />
</template>

<script setup>
import DashboardSeoAudit from "~/views/DashboardSeoAudit.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "SEO аудит",
    description: "Базовый SEO-аудит сайта в кабинете TrackNode.",
  },
});
</script>
