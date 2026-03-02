<template>
  <DashboardDynamics />
</template>

<script setup>
import DashboardDynamics from "~/views/DashboardDynamics.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Динамика по дням",
    description: "Личный кабинет TrackNode: динамика метрик по дням.",
  },
});
</script>
