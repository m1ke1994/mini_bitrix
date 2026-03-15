<template>
  <main id="top" class="public-home-main landing-page-main min-h-screen bg-[#eef1f8] px-3 pb-5 sm:px-6 sm:pb-8 lg:px-8">
    <div
      class="relative mx-auto w-full max-w-[1400px] overflow-hidden rounded-[30px] border border-white/70 bg-[#f7f9fe] px-4 pb-8 pt-4 shadow-[0_26px_60px_rgba(36,52,87,0.12)] sm:px-6 lg:px-9 lg:pb-12 lg:pt-6"
    >
      <div
        class="pointer-events-none absolute -left-[14%] bottom-[-14%] h-[430px] w-[430px] rounded-full bg-[radial-gradient(circle,rgba(203,218,255,0.5)_0%,rgba(203,218,255,0)_70%)] blur-2xl"
      />
      <div
        class="pointer-events-none absolute -right-[12%] top-[10%] h-[560px] w-[560px] rounded-full bg-[radial-gradient(circle,rgba(146,195,255,0.56)_0%,rgba(146,195,255,0)_72%)] blur-2xl"
      />

      <UpHeader
        :brand="landing.homepage.brand"
        :nav="landing.homepage.nav"
        :header-cta="landing.homepage.headerCta"
        :mobile-actions="landing.homepage.mobileActions"
      />

      <section class="landing-page-hero">
        <p v-if="hero.kicker" class="landing-page-hero__kicker">{{ hero.kicker }}</p>
        <h1 class="landing-page-hero__title">{{ hero.title }}</h1>
        <p class="landing-page-hero__description">{{ hero.description }}</p>

        <div v-if="hero.actions?.length" class="landing-page-hero__actions">
          <a
            v-for="action in hero.actions"
            :key="`${action.label}-${action.href}`"
            :href="action.href"
            :target="action.target || null"
            :rel="action.rel || null"
            :class="['landing-page-hero__action', { 'landing-page-hero__action--secondary': action.variant === 'secondary' }]"
          >
            {{ action.label }}
          </a>
        </div>
      </section>
    </div>

    <slot />

    <SiteFooter v-if="showFooter" :footer="landing.footer" />
  </main>
</template>

<script setup>
import SiteFooter from "~/components/landing_components/SiteFooter.vue";
import UpHeader from "~/components/landing_components/UpHeader.vue";

defineProps({
  landing: {
    type: Object,
    required: true,
  },
  hero: {
    type: Object,
    required: true,
  },
  showFooter: {
    type: Boolean,
    default: true,
  },
});
</script>

<style scoped>
.landing-page-main {
  padding-top: 90px !important;
}

.landing-page-hero {
  position: relative;
  z-index: 2;
  margin: 3.25rem auto 0;
  max-width: 980px;
  text-align: center;
}

.landing-page-hero__kicker {
  margin: 0;
  color: #3a71c6;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.landing-page-hero__title {
  margin: 0.9rem 0 0;
  color: #1f273a;
  font-size: clamp(2rem, 4.3vw, 3.5rem);
  line-height: 1.1;
  letter-spacing: -0.03em;
  font-weight: 650;
}

.landing-page-hero__description {
  margin: 1.2rem auto 0;
  max-width: 760px;
  color: rgba(49, 60, 84, 0.82);
  font-size: clamp(1rem, 1.45vw, 1.28rem);
  line-height: 1.55;
}

.landing-page-hero__actions {
  margin-top: 1.6rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.72rem;
}

.landing-page-hero__action {
  min-height: 44px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-size: 0.96rem;
  font-weight: 700;
  padding: 0 1.15rem;
  border: 1px solid rgba(66, 124, 232, 0.88);
  background-image: var(--brand-gradient);
  color: #fff;
  box-shadow: 0 10px 20px rgba(47, 106, 255, 0.26);
}

.landing-page-hero__action--secondary {
  border: 1px solid rgba(181, 206, 242, 0.95);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.92) 0%,
      rgba(233, 244, 255, 0.95) 100%
    );
  box-shadow: none;
  color: #3f73c0;
}

@media (min-width: 640px) {
  .landing-page-main {
    padding-top: 50px !important;
  }
}

@media (min-width: 1024px) {
  .landing-page-main {
    padding-top: 100px !important;
  }
}

@media (max-width: 767px) {
  .landing-page-hero {
    margin-top: 2.6rem;
    text-align: left;
  }

  .landing-page-hero__actions {
    justify-content: flex-start;
  }
}
</style>
