<template>
  <DashboardUniqueVisitors />
</template>

<script setup>
import DashboardUniqueVisitors from "~/views/DashboardUniqueVisitors.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Уникальные пользователи",
    description: "Личный кабинет TrackNode: уникальные пользователи.",
  },
});
</script>
