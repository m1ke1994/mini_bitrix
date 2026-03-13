<template>
  <SettingsPage />
</template>

<script setup>
import SettingsPage from "~/views/SettingsPage.vue";

definePageMeta({
  layout: "app",
  noindex: true,
  seo: {
    title: "Настройки",
    description: "Личный кабинет TrackNode: настройки аккаунта.",
  },
});
</script>
