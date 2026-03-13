<template>
  <ReportsPage />
</template>

<script setup>
import ReportsPage from "~/views/ReportsPage.vue";

definePageMeta({
  layout: "app",
  noindex: true,
  seo: {
    title: "Отчет PDF",
    description: "Личный кабинет TrackNode: PDF-отчеты.",
  },
});
</script>
