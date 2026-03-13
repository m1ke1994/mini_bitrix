<template>
  <PublicFeaturePage />
</template>

<script setup>
import PublicFeaturePage from "~/views/PublicFeaturePage.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";
import { createFaqSchema, createServiceSchema, getCanonicalUrl } from "~/seo";

const otchetyFaqSchema = createFaqSchema(getPublicSeoContent("/otchety")?.faqItems || []);
const otchetyServiceSchema = createServiceSchema({
  name: "Отчеты TrackNode",
  description:
    "Ежедневные и периодические отчеты по заявкам, воронке и источникам трафика с экспортом в PDF.",
  path: "/otchety",
});

definePageMeta({
  publicPage: true,
  pageHeading: "Отчеты",
  pageText:
    "Формируйте ежедневные и периодические отчеты по заявкам, воронке и источникам трафика, чтобы принимать решения по бизнесу на основе фактических данных.",
  seo: {
    title: "Отчеты TrackNode: ежедневная аналитика и PDF по заявкам",
    description:
      "TrackNode формирует ежедневные и недельные отчеты по заявкам, источникам трафика и конверсии, а также PDF-сводки для руководителя, маркетинга и продаж.",
    keywords:
      "отчеты по заявкам, PDF отчет, аналитика сайта, учет заявок, источники трафика, конверсия",
    canonical: getCanonicalUrl("/otchety"),
    ogType: "website",
    schema: [otchetyServiceSchema, otchetyFaqSchema].filter(Boolean),
  },
});
</script>
