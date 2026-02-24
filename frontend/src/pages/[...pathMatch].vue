<template>
  <NotFoundPage />
</template>

<script setup>
import NotFoundPage from "~/views/NotFoundPage.vue";

definePageMeta({
  publicPage: true,
  noindex: true,
  seo: {
    title: "404 - Страница не найдена | TrackNode",
    description: "Страница не найдена.",
  },
});
</script>
