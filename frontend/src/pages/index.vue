<template>
  <PublicHomePage />
</template>

<script setup>
import PublicHomePage from "~/views/PublicHomePage.vue";
import { homepageSoftwareSchema } from "~/seo";

definePageMeta({
  publicPage: true,
  seo: {
    title: "Аналитика сайтов и учет заявок — сервис отслеживания лидов | TrackNode",
    description:
      "Сервис аналитики сайтов и учета заявок. Отслеживайте лиды, конверсию и путь клиента. Аналитика воронки продаж и Telegram-уведомления в одном кабинете.",
    keywords:
      "аналитика сайтов, сервис аналитики, учет заявок, аналитика воронки продаж, отслеживание конверсии, TrackNode",
    ogType: "website",
    schema: homepageSoftwareSchema,
  },
});
</script>
