<template>
  <AccountView />
</template>

<script setup>
import AccountView from "~/views/AccountView.vue";

definePageMeta({
  layout: "app",
  noindex: true,
  seo: {
    title: "Аккаунт",
    description: "Личный кабинет TrackNode: смена пароля.",
  },
});
</script>
