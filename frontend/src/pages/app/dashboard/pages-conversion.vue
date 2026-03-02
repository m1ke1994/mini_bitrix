<template>
  <DashboardPagesConversion />
</template>

<script setup>
import DashboardPagesConversion from "~/views/DashboardPagesConversion.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Конверсия по страницам",
    description: "Личный кабинет TrackNode: конверсия по страницам сайта.",
  },
});
</script>
