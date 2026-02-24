<template>
  <AuthPage />
</template>

<script setup>
import AuthPage from "~/views/AuthPage.vue";

definePageMeta({
  publicPage: true,
  noindex: true,
  seo: {
    title: "Авторизация | TrackNode",
    description: "Вход в личный кабинет TrackNode.",
    keywords: "tracknode login, авторизация",
  },
});
</script>
