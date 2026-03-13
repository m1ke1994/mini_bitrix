<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";
import { createFaqSchema, createServiceSchema, getCanonicalUrl } from "~/seo";

const telegramFaqSchema = createFaqSchema(getPublicSeoContent("/telegram")?.faqItems || []);
const telegramServiceSchema = createServiceSchema({
  name: "Telegram-уведомления TrackNode",
  description:
    "Мгновенные уведомления о заявках с указанием страницы отправки, времени и контекста для ускорения обработки лидов.",
  path: "/telegram",
});

definePageMeta({
  publicPage: true,
  pageHeading: "Telegram-уведомления",
  pageText:
    "Получайте мгновенные уведомления о заявках в Telegram с контекстом обращения, чтобы команда быстрее отвечала клиентам и не теряла лиды.",
  seo: {
    title: "Telegram-уведомления TrackNode для заявок и лидов сайта",
    description:
      "TrackNode отправляет Telegram-уведомления о каждой заявке с временем и страницей отправки формы, чтобы команда быстрее отвечала клиентам и не теряла лиды.",
    keywords:
      "уведомления в Telegram, отслеживание лидов, учет заявок, конверсия сайта, аналитика сайта, TrackNode",
    canonical: getCanonicalUrl("/telegram"),
    ogType: "website",
    schema: [telegramServiceSchema, telegramFaqSchema].filter(Boolean),
  },
});
</script>
