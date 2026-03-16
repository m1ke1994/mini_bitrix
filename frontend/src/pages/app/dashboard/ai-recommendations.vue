<template>
  <DashboardAiRecommendations />
</template>

<script setup>
import DashboardAiRecommendations from "~/views/DashboardAiRecommendations.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "Поведение пользователя на сайте",
    description: "Поведенческая аналитика: как посетители взаимодействуют с сайтом, формами и кнопками.",
  },
});
</script>
