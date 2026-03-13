<template>
  <InstructionsPage />
</template>

<script setup>
import InstructionsPage from "~/views/InstructionsPage.vue";

definePageMeta({
  layout: "app",
  noindex: true,
  seo: {
    title: "Инструкция по подключению",
    description: "Личный кабинет TrackNode: инструкции по подключению.",
  },
});
</script>
