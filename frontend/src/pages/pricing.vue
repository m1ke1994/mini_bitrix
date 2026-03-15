<template>
  <LandingPageShell :landing="landing" :hero="page.hero">
    <LandingCardSection title="Тарифы">
      <div class="pricing-grid">
        <article
          v-for="plan in page.plans"
          :key="plan.name"
          class="pricing-card"
          :class="{ 'pricing-card--featured': plan.featured }"
        >
          <span v-if="plan.featured" class="pricing-badge">Рекомендуем</span>
          <h2>{{ plan.name }}</h2>
          <p class="pricing-price">{{ plan.price }}</p>
          <p class="pricing-description">{{ plan.description }}</p>

          <ul>
            <li v-for="feature in plan.features" :key="feature">{{ feature }}</li>
          </ul>
        </article>
      </div>
    </LandingCardSection>

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
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingData } from "~/data/landing";

const landing = getLandingData();
const page = landing.seoPages?.pricing;

definePageMeta({
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  ...page.seo,
  path: "/pricing",
});
</script>

<style scoped>
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.pricing-card {
  position: relative;
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
  padding: 17px 14px;
}

.pricing-card--featured {
  border-color: rgba(174, 205, 247, 0.95);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.92),
    0 20px 42px rgba(75, 119, 191, 0.18),
    0 0 0 1px rgba(188, 215, 250, 0.66);
}

.pricing-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  border-radius: 999px;
  border: 1px solid rgba(152, 193, 245, 0.85);
  background: rgba(240, 248, 255, 0.88);
  color: #4f82c6;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 5px 9px;
}

.pricing-card h2 {
  margin: 0;
  color: #1f2a43;
  font-size: 1.26rem;
  line-height: 1.2;
  font-weight: 700;
}

.pricing-price {
  margin: 0.8rem 0 0;
  color: #2f5fbb;
  font-size: 1.34rem;
  line-height: 1.1;
  font-weight: 700;
}

.pricing-description {
  margin: 0.6rem 0 0;
  color: rgba(39, 50, 73, 0.72);
  font-size: 0.94rem;
  line-height: 1.45;
}

.pricing-card ul {
  margin: 0.8rem 0 0;
  padding-left: 1rem;
  color: rgba(34, 46, 70, 0.86);
  font-size: 0.92rem;
  line-height: 1.45;
}

.pricing-card li + li {
  margin-top: 0.4rem;
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

@media (max-width: 1023px) {
  .pricing-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .pricing-grid {
    grid-template-columns: 1fr;
  }
}
</style>
