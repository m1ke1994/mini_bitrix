<template>
  <PublicHomePage />
</template>

<script setup>
import PublicHomePage from "~/views/PublicHomePage.vue";

definePageMeta({
  layout: "app",
  publicPage: true,
});
</script>
