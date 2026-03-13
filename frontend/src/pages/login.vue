<template>
  <AuthPage />
</template>

<script setup>
import AuthPage from "~/views/AuthPage.vue";

definePageMeta({
  publicPage: true,
  noindex: true,
  seo: {
    title: "Вход в TrackNode",
    description: "Вход в личный кабинет TrackNode для работы с аналитикой и заявками.",
    keywords: "вход tracknode, логин",
  },
});
</script>
