<template>
  <DashboardOverview />
</template>

<script setup>
import DashboardOverview from "~/views/DashboardOverview.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Обзор",
    description: "Личный кабинет TrackNode: обзор ключевых метрик.",
  },
});
</script>
