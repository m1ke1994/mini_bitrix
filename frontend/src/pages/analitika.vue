<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";

definePageMeta({
  publicPage: true,
  pageHeading: "Аналитика сайтов",
  pageText:
    "Собирайте данные по визитам, источникам и событиям в одном интерфейсе. TrackNode помогает видеть реальную эффективность маркетинга и сайта.",
  seo: {
    title: "Аналитика сайтов TrackNode — контроль трафика, лидов и конверсии",
    description:
      "Аналитика TrackNode показывает источники трафика, динамику заявок и конверсию страниц, чтобы быстро находить точки роста.",
    keywords: "аналитика сайта, веб-аналитика, конверсия, лиды, TrackNode",
    ogType: "website",
  },
});
</script>
