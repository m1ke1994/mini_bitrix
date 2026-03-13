<template>
  <DashboardClicks />
</template>

<script setup>
import DashboardClicks from "~/views/DashboardClicks.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Топ кликов",
    description: "Личный кабинет TrackNode: отчет по кликам.",
  },
});
</script>
