<template>
  <LandingPageShell :landing="landing" :hero="page.hero">
    <LandingCardSection title="Список кейсов" subtitle="Реальные проекты с измеримым результатом по трафику, конверсии и техническому качеству сайта.">
      <div class="cases-grid">
        <article
          v-for="caseItem in cases"
          :key="caseItem.slug"
          class="case-card"
        >
          <img :src="caseItem.previewImage" :alt="caseItem.title" class="case-card__image" loading="lazy" />

          <h2 class="case-card__title">{{ caseItem.title }}</h2>
          <p class="case-card__description">{{ caseItem.shortDescription }}</p>
          <p class="case-card__result">{{ caseItem.resultSummary }}</p>

          <NuxtLink :to="`/cases/${caseItem.slug}`" class="case-card__link">
            Смотреть кейс
          </NuxtLink>
        </article>
      </div>
    </LandingCardSection>
  </LandingPageShell>
</template>

<script setup>
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingCases, getLandingData } from "~/data/landing";

const landing = getLandingData();
const page = landing.seoPages?.cases;
const cases = getLandingCases();

definePageMeta({
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  ...page.seo,
  path: "/cases",
});
</script>

<style scoped>
.cases-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.case-card {
  border-radius: 20px;
  border: 1px solid rgba(227, 236, 250, 0.94);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.73) 0%,
      rgba(252, 255, 255, 0.58) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.88),
    0 13px 30px rgba(81, 111, 161, 0.11);
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.case-card__image {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(200, 217, 242, 0.9);
}

.case-card__title {
  margin: 0.9rem 0 0;
  color: #24314c;
  font-size: 1.04rem;
  line-height: 1.35;
  font-weight: 700;
}

.case-card__description {
  margin: 0.75rem 0 0;
  color: rgba(39, 50, 73, 0.78);
  font-size: 0.93rem;
  line-height: 1.5;
}

.case-card__result {
  margin: 0.8rem 0 0;
  color: #2f5fbb;
  font-size: 0.88rem;
  line-height: 1.45;
  font-weight: 700;
}

.case-card__link {
  margin-top: auto;
  min-height: 42px;
  border-radius: 11px;
  border: 1px solid rgba(164, 197, 243, 0.92);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.93) 0%,
      rgba(232, 243, 255, 0.96) 100%
    );
  color: #3d74c4;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.93rem;
  font-weight: 700;
  margin-top: 1rem;
}

@media (max-width: 1023px) {
  .cases-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .cases-grid {
    grid-template-columns: 1fr;
  }
}
</style>
