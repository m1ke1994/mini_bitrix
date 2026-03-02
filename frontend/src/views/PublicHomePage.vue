<template>
  <main id="top" class="min-h-screen bg-[#eef1f8] px-3 pb-5 pt-[92px] sm:px-6 sm:pb-8 sm:pt-[102px] lg:px-8 lg:pt-[112px]">
    <div class="relative mx-auto w-full max-w-[1400px] overflow-hidden rounded-[30px] border border-white/70 bg-[#f7f9fe] px-4 pb-10 pt-4 shadow-[0_26px_60px_rgba(36,52,87,0.12)] sm:px-6 lg:px-9 lg:pb-14 lg:pt-6">
      <div class="pointer-events-none absolute -left-[14%] bottom-[-14%] h-[430px] w-[430px] rounded-full bg-[radial-gradient(circle,rgba(203,218,255,0.5)_0%,rgba(203,218,255,0)_70%)] blur-2xl" />
      <div class="pointer-events-none absolute -right-[12%] top-[10%] h-[560px] w-[560px] rounded-full bg-[radial-gradient(circle,rgba(146,195,255,0.56)_0%,rgba(146,195,255,0)_72%)] blur-2xl" />
      <UpHeader :brand="homepageData.brand" :nav="homepageData.nav" :header-cta="homepageData.headerCta" />
      <Hero :hero="homepageData.hero" :trust="homepageData.trust" />
    </div>

    <div class="mx-auto mt-5 w-full max-w-[1400px] overflow-hidden rounded-[30px] border border-white/70 bg-[#f4f7fd] shadow-[0_22px_52px_rgba(36,52,87,0.1)]">
      <CapabilitiesSection />
    </div>

    <HowItWorksSection />

    <PricingSection />
    <ReviewsSection />
    <FAQSection />

    <SiteFooter />
  </main>
</template>

<script setup>
import { homepageData } from "~/data/homepage";
import CapabilitiesSection from "~/components/sections/CapabilitiesSection.vue";
import HowItWorksSection from "~/components/HowItWorksSection.vue";
import PricingSection from "~/components/PricingSection.vue";
import ReviewsSection from "~/components/ReviewsSection.vue";
import FAQSection from "~/components/FAQSection.vue";
import SiteFooter from "~/components/SiteFooter.vue";
</script>
