<template>
  <LandingPageShell :landing="landing" :hero="page.hero">
    <LandingCardSection :title="page.blocks.definition.title">
      <p class="landing-text">{{ page.blocks.definition.text }}</p>
    </LandingCardSection>

    <LandingCardSection :title="page.blocks.problems.title">
      <div class="landing-grid landing-grid--3">
        <article
          v-for="item in page.blocks.problems.items"
          :key="item.title"
          class="landing-card"
        >
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </LandingCardSection>

    <LandingCardSection :title="page.blocks.errorTypes.title">
      <div class="landing-grid landing-grid--3">
        <article
          v-for="item in page.blocks.errorTypes.items"
          :key="item.title"
          class="landing-card"
        >
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </LandingCardSection>

    <LandingCardSection :title="page.blocks.businessValue.title">
      <ul class="landing-list">
        <li v-for="item in page.blocks.businessValue.items" :key="item">{{ item }}</li>
      </ul>
    </LandingCardSection>

    <LandingCardSection :title="page.blocks.advantages.title">
      <ul class="landing-list">
        <li v-for="item in page.blocks.advantages.items" :key="item">{{ item }}</li>
      </ul>
    </LandingCardSection>

    <LandingCardSection :title="page.blocks.cta.title" :subtitle="page.blocks.cta.text">
      <a :href="page.blocks.cta.action.href" class="landing-cta">{{ page.blocks.cta.action.label }}</a>
    </LandingCardSection>
  </LandingPageShell>
</template>

<script setup>
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingData } from "~/data/landing";
import { createServiceSchema } from "~/seo";

const landing = getLandingData();
const page = landing.seoPages?.seoAudit;

const serviceSchema = createServiceSchema({
  name: "SEO-аудит сайта TrackNode",
  description: page?.seo?.description || "",
  path: "/seo-audit",
});

definePageMeta({
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  ...page.seo,
  path: "/seo-audit",
  schema: [serviceSchema],
});
</script>

<style scoped>
.landing-text {
  margin: 0;
  color: rgba(34, 47, 71, 0.82);
  font-size: 1.04rem;
  line-height: 1.58;
}

.landing-grid {
  display: grid;
  gap: 14px;
}

.landing-grid--3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.landing-card {
  border-radius: 18px;
  border: 1px solid rgba(227, 236, 250, 0.94);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.73) 0%,
      rgba(252, 255, 255, 0.58) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.88),
    0 13px 30px rgba(81, 111, 161, 0.1);
  padding: 18px 16px;
}

.landing-card h3 {
  margin: 0;
  color: #24314c;
  font-size: 1.08rem;
  line-height: 1.3;
  font-weight: 700;
}

.landing-card p {
  margin: 0.7rem 0 0;
  color: rgba(39, 50, 73, 0.78);
  font-size: 0.95rem;
  line-height: 1.5;
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
  .landing-grid--3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .landing-grid--3 {
    grid-template-columns: 1fr;
  }
}
</style>
