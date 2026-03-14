<template>
  <DashboardAiRecommendations />
</template>

<script setup>
import DashboardAiRecommendations from "~/views/DashboardAiRecommendations.vue";

definePageMeta({
  noindex: true,
  seo: {
    title: "AI рекомендации",
    description: "Раздел заготовки для будущих AI-рекомендаций на базе поведенческой аналитики.",
  },
});
</script>
