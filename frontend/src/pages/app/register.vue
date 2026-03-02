<template>
  <AuthPage />
</template>

<script setup>
import AuthPage from "~/views/AuthPage.vue";

definePageMeta({
  publicPage: true,
  noindex: true,
  seo: {
    title: "Регистрация в TrackNode",
    description: "Создайте аккаунт TrackNode для доступа к аналитике сайта и воронке лидогенерации.",
    keywords: "регистрация tracknode, создать аккаунт",
  },
});
</script>
