<template>
  <main id="top" class="public-home-main min-h-screen bg-[#eef1f8] px-3 pb-5 sm:px-6 sm:pb-8 lg:px-8">
    <div class="relative mx-auto w-full max-w-[1400px] overflow-hidden rounded-[30px] border border-white/70 bg-[#f7f9fe] px-4 pb-10 pt-4 shadow-[0_26px_60px_rgba(36,52,87,0.12)] sm:px-6 lg:px-9 lg:pb-14 lg:pt-6">
      <div class="pointer-events-none absolute -left-[14%] bottom-[-14%] h-[430px] w-[430px] rounded-full bg-[radial-gradient(circle,rgba(203,218,255,0.5)_0%,rgba(203,218,255,0)_70%)] blur-2xl" />
      <div class="pointer-events-none absolute -right-[12%] top-[10%] h-[560px] w-[560px] rounded-full bg-[radial-gradient(circle,rgba(146,195,255,0.56)_0%,rgba(146,195,255,0)_72%)] blur-2xl" />
      <UpHeader
        :brand="landing.homepage.brand"
        :nav="landing.homepage.nav"
        :header-cta="landing.homepage.headerCta"
        :mobile-actions="landing.homepage.mobileActions"
      />
      <Hero :hero="landing.homepage.hero" :trust="landing.homepage.trust" :demo="landing.heroDemo" />
    </div>

    <div class="mx-auto mt-5 w-full max-w-[1400px] overflow-hidden rounded-[30px] border border-white/70 bg-[#f4f7fd] shadow-[0_22px_52px_rgba(36,52,87,0.1)]">
      <CapabilitiesSection :capabilities="landing.site.capabilities" />
    </div>

    <HowItWorksSection :how="landing.how" />

    <PricingSection :pricing="landing.site.pricing" />
    <ReviewsSection :reviews="landing.site.reviews" />
    <FAQSection :faq="landing.site.faq" />

    <SiteFooter :footer="landing.footer" />
  </main>
</template>

<script setup>
import UpHeader from "~/components/landing_components/UpHeader.vue";
import Hero from "~/components/landing_components/Hero.vue";
import CapabilitiesSection from "~/components/landing_components/sections/CapabilitiesSection.vue";
import HowItWorksSection from "~/components/landing_components/HowItWorksSection.vue";
import PricingSection from "~/components/landing_components/PricingSection.vue";
import ReviewsSection from "~/components/landing_components/ReviewsSection.vue";
import FAQSection from "~/components/landing_components/FAQSection.vue";
import SiteFooter from "~/components/landing_components/SiteFooter.vue";
import { getLandingData } from "~/data/landing";

const landing = getLandingData();
</script>

<style scoped>
.public-home-main {
  padding-top: 90px !important;
}

@media (min-width: 640px) {
  .public-home-main {
    padding-top: 50px !important;
  }
}

@media (min-width: 1024px) {
  .public-home-main {
    padding-top: 100px !important;
  }
}
</style>
