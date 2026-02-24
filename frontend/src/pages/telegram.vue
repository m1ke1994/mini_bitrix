<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";

definePageMeta({
  publicPage: true,
  pageHeading: "Telegram-уведомления",
  pageText:
    "Настройте быстрые уведомления о событиях в Telegram, чтобы команда сразу реагировала на новые обращения и изменения статусов.",
  seo: {
    title: "Telegram-уведомления TrackNode — мгновенные оповещения по заявкам",
    description:
      "Подключите Telegram-уведомления в TrackNode и получайте сообщения о новых заявках, оплатах и статусах без задержек.",
    keywords: "telegram уведомления, уведомления о заявках, TrackNode",
    ogType: "website",
  },
});
</script>
