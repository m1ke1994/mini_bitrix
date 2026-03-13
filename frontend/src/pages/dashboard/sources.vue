<template>
  <DashboardSources />
</template>

<script setup>
import DashboardSources from "~/views/DashboardSources.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Топ источников",
    description: "Личный кабинет TrackNode: топ источников трафика.",
  },
});
</script>
