<template>
  <AboutProject />
</template>

<script setup>
import AboutProject from "~/views/AboutProject.vue";

definePageMeta({
  layout: "app",
  noindex: true,
  seo: {
    title: "О проекте TrackNode",
    description: "TrackNode — система аналитики сайтов и управления заявками.",
    keywords: "TrackNode, аналитика сайта, SaaS аналитика",
    ogType: "website",
  },
});
</script>
