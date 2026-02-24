<template>
  <DashboardEngagement />
</template>

<script setup>
import DashboardEngagement from "~/views/DashboardEngagement.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Вовлеченность",
    description: "Личный кабинет TrackNode: вовлеченность пользователей по страницам.",
  },
});
</script>
