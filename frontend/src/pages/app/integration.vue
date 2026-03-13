<template>
  <IntegrationPage />
</template>

<script setup>
import IntegrationPage from "~/views/IntegrationPage.vue";

definePageMeta({
  layout: "app",
  noindex: true,
  seo: {
    title: "Интеграции",
    description: "Личный кабинет TrackNode: настройки интеграции.",
  },
});
</script>
