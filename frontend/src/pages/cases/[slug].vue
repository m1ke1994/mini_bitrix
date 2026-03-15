<template>
  <LandingPageShell :landing="landing" :hero="hero">
    <LandingCardSection title="Кратко о проекте">
      <p class="landing-text">{{ currentCase.shortDescription }}</p>
    </LandingCardSection>

    <LandingCardSection title="Было / Стало">
      <div class="case-compare">
        <figure>
          <img :src="currentCase.beforeImage" :alt="`До: ${currentCase.title}`" loading="lazy" />
          <figcaption>До внедрения</figcaption>
        </figure>
        <figure>
          <img :src="currentCase.afterImage" :alt="`После: ${currentCase.title}`" loading="lazy" />
          <figcaption>После внедрения</figcaption>
        </figure>
      </div>
    </LandingCardSection>

    <LandingCardSection title="С какими проблемами пришел проект">
      <ul class="landing-list">
        <li v-for="item in currentCase.issues" :key="item">{{ item }}</li>
      </ul>
    </LandingCardSection>

    <LandingCardSection title="Что было исправлено">
      <ul class="landing-list">
        <li v-for="item in currentCase.fixes" :key="item">{{ item }}</li>
      </ul>
    </LandingCardSection>

    <LandingCardSection title="Какие результаты получены">
      <ul class="landing-list">
        <li v-for="item in currentCase.results" :key="item">{{ item }}</li>
      </ul>
    </LandingCardSection>

    <LandingCardSection title="Ключевые показатели">
      <div class="metrics-table-wrap">
        <table class="metrics-table">
          <thead>
            <tr>
              <th>Показатель</th>
              <th>Было</th>
              <th>Стало</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="metric in currentCase.metrics" :key="metric.label">
              <td>{{ metric.label }}</td>
              <td>{{ metric.before }}</td>
              <td>{{ metric.after }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </LandingCardSection>
  </LandingPageShell>
</template>

<script setup>
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingCaseBySlug, getLandingData } from "~/data/landing";

const landing = getLandingData();
const route = useRoute();
const slug = String(route.params.slug || "");
const currentCase = getLandingCaseBySlug(slug);

if (!currentCase) {
  throw createError({
    statusCode: 404,
    statusMessage: "Кейс не найден",
  });
}

const hero = {
  kicker: "Кейс",
  title: currentCase.title,
  description: currentCase.resultSummary,
  actions: [
    { label: "Все кейсы", href: "/cases", variant: "secondary" },
    { label: "Обсудить проект", href: "/contacts" },
  ],
};

const caseSchema = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: currentCase.title,
  description: currentCase.shortDescription,
  mainEntityOfPage: `https://tracknode.ru/cases/${currentCase.slug}`,
};

definePageMeta({
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  title: `${currentCase.title} | Кейс TrackNode`,
  description: currentCase.shortDescription,
  keywords: "seo кейс, аналитика сайта кейс, рост конверсии, технический аудит",
  path: `/cases/${currentCase.slug}`,
  ogType: "article",
  schema: [caseSchema],
});
</script>

<style scoped>
.landing-text {
  margin: 0;
  color: rgba(34, 47, 71, 0.82);
  font-size: 1.04rem;
  line-height: 1.58;
}

.case-compare {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.case-compare figure {
  margin: 0;
  border-radius: 16px;
  border: 1px solid rgba(214, 228, 248, 0.92);
  background: rgba(255, 255, 255, 0.75);
  padding: 10px;
}

.case-compare img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid rgba(197, 215, 240, 0.92);
}

.case-compare figcaption {
  margin-top: 0.6rem;
  color: rgba(37, 51, 77, 0.8);
  font-size: 0.88rem;
  line-height: 1.3;
  font-weight: 700;
}

.landing-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.landing-list li {
  border-radius: 14px;
  border: 1px solid rgba(226, 235, 249, 0.94);
  background: rgba(255, 255, 255, 0.74);
  color: rgba(35, 47, 71, 0.86);
  font-size: 0.98rem;
  line-height: 1.46;
  padding: 12px 14px;
}

.metrics-table-wrap {
  overflow-x: auto;
  border-radius: 16px;
  border: 1px solid rgba(215, 229, 248, 0.94);
  background: rgba(255, 255, 255, 0.8);
}

.metrics-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 520px;
}

.metrics-table th {
  color: rgba(42, 54, 79, 0.82);
  font-size: 0.86rem;
  line-height: 1.2;
  font-weight: 700;
  text-align: left;
  background: rgba(236, 245, 255, 0.82);
}

.metrics-table th,
.metrics-table td {
  border-bottom: 1px solid rgba(215, 229, 248, 0.9);
  padding: 11px 13px;
}

.metrics-table td {
  color: rgba(35, 47, 71, 0.86);
  font-size: 0.93rem;
  line-height: 1.35;
}

.metrics-table tbody tr:last-child td {
  border-bottom: none;
}

@media (max-width: 767px) {
  .case-compare {
    grid-template-columns: 1fr;
  }
}
</style>
