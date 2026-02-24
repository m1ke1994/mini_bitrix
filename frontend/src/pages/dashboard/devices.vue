<template>
  <DashboardDevices />
</template>

<script setup>
import DashboardDevices from "~/views/DashboardDevices.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Панель управления - Устройства",
    description: "Личный кабинет TrackNode: статистика устройств.",
  },
});
</script>
