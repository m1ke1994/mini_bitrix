<template>
  <LandingPageShell :landing="landing" :hero="page.hero">
    <LandingCardSection title="Способы связи" subtitle="Выберите удобный канал, чтобы обсудить задачи по SEO-аудиту и аналитике сайта.">
      <div class="contacts-grid">
        <article
          v-for="channel in page.channels"
          :key="`${channel.label}-${channel.value}`"
          class="contact-card"
        >
          <p class="contact-card__label">{{ channel.label }}</p>
          <a v-if="channel.href" :href="channel.href">{{ channel.value }}</a>
          <p v-else class="contact-card__value">{{ channel.value }}</p>
        </article>
      </div>

      <p class="contacts-note">{{ page.note }}</p>
    </LandingCardSection>

    <LandingCardSection :title="page.cta.title" :subtitle="page.cta.text">
      <a
        :href="page.cta.action.href"
        :target="page.cta.action.target || null"
        :rel="page.cta.action.rel || null"
        class="landing-cta"
      >
        {{ page.cta.action.label }}
      </a>
    </LandingCardSection>
  </LandingPageShell>
</template>

<script setup>
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingData } from "~/data/landing";

const landing = getLandingData();
const page = landing.seoPages?.contacts;

definePageMeta({
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  ...page.seo,
  path: "/contacts",
});
</script>

<style scoped>
.contacts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.contact-card {
  border-radius: 16px;
  border: 1px solid rgba(226, 235, 249, 0.94);
  background: rgba(255, 255, 255, 0.74);
  padding: 12px 14px;
}

.contact-card__label {
  margin: 0;
  color: rgba(69, 94, 132, 0.82);
  font-size: 0.78rem;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.contact-card a,
.contact-card__value {
  margin: 0.45rem 0 0;
  color: rgba(35, 47, 71, 0.86);
  text-decoration: none;
  font-size: 1.02rem;
  line-height: 1.45;
  font-weight: 600;
}

.contacts-note {
  margin: 1rem 0 0;
  color: rgba(39, 50, 73, 0.8);
  font-size: 0.95rem;
  line-height: 1.54;
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

@media (max-width: 767px) {
  .contacts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
