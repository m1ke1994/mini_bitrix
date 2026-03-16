<template>
  <LandingPageShell :landing="landing" :hero="page.hero">
    <PricingSection :pricing="pricingSection" />

    <LandingCardSection title="Преимущества сервиса">
      <ul class="landing-list">
        <li v-for="item in page.advantages" :key="item">{{ item }}</li>
      </ul>
    </LandingCardSection>

    <LandingCardSection title="Что входит">
      <ul class="landing-list">
        <li v-for="item in page.included" :key="item">{{ item }}</li>
      </ul>
    </LandingCardSection>

    <LandingCardSection :title="page.cta.title" :subtitle="page.cta.text">
      <a :href="page.cta.action.href" class="landing-cta">{{ page.cta.action.label }}</a>
    </LandingCardSection>
  </LandingPageShell>
</template>

<script setup>
import { computed } from "vue";
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import PricingSection from "~/components/landing_components/PricingSection.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingData } from "~/data/landing";

const landing = getLandingData();
const page = landing.seoPages?.pricing;

const pricingSection = computed(() => ({
  ...landing.site?.pricing,
  title: "Тарифы",
  subtitle: page?.hero?.description || landing.site?.pricing?.subtitle || "",
  plans: page?.plans || [],
  contactCta:
    page?.cta?.action ||
    landing.site?.pricing?.contactCta || {
      href: "/contacts",
      label: "Связаться",
    },
}));

definePageMeta({
  layout: "landing",
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  ...page.seo,
  path: "/pricing",
});
</script>

<style scoped>
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

.landing-cta {
  min-height: 46px;
  border-radius: 12px;
  border: 1px solid rgba(66, 124, 232, 0.88);
  background-image: var(--brand-gradient);
  color: #fff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 1.2rem;
  font-size: 0.98rem;
  font-weight: 700;
  box-shadow: 0 10px 20px rgba(47, 106, 255, 0.26);
}
</style>

