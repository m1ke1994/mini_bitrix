<template>
  <section class="relative z-10 mx-auto mt-12 w-full max-w-full overflow-hidden px-4 sm:max-w-[1280px] sm:px-0 lg:mt-14">
    <div class="grid items-center gap-7 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)] lg:gap-8">
      <div class="order-1 min-w-0">
        <h1 class="max-w-full text-[34px] font-semibold leading-[1.08] tracking-[-0.02em] text-[#1f273a] sm:max-w-[560px] sm:text-[49px] lg:text-[62px]">
          <span v-for="line in hero.titleLines" :key="line" class="block">{{ line }}</span>
        </h1>

        <p class="mt-6 max-w-full text-[18px] leading-[1.5] text-[#4c566d] sm:max-w-[560px] sm:text-[19px]">
          {{ hero.description }}
        </p>

        <div class="mt-8 flex flex-wrap gap-3">
          <a
            :href="hero.primaryCta.href"
            :target="hero.primaryCta.target || null"
            :rel="hero.primaryCta.rel || null"
            class="btn-brand-gradient inline-flex w-full min-h-12 items-center justify-center rounded-[12px] px-6 text-[18px] font-semibold text-white shadow-[0_12px_22px_rgba(47,107,255,0.35)] transition hover:brightness-105 sm:w-auto"
          >
            {{ hero.primaryCta.label }}
          </a>
          <a
            :href="hero.secondaryCta.href"
            :target="hero.secondaryCta.target || null"
            :rel="hero.secondaryCta.rel || null"
            class="inline-flex w-full min-h-12 items-center justify-center gap-2 rounded-[12px] border border-[#d5ddeb] bg-white/95 px-6 text-[18px] font-semibold text-[#374056] shadow-[0_8px_18px_rgba(34,50,86,0.08)] transition hover:border-[#c5d0e4] sm:w-auto"
          >
            {{ hero.secondaryCta.label }}
            <svg viewBox="0 0 16 16" class="h-4 w-4" fill="none" aria-hidden="true">
              <path d="M5 3L10 8L5 13" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </a>
        </div>
      </div>

      <div class="order-2 min-w-0 lg:pl-1">
        <div class="relative mx-auto w-full max-w-full overflow-hidden sm:max-w-[900px]">
          <div class="pointer-events-none absolute inset-x-0 -top-4 bottom-2 rounded-[28px] bg-[radial-gradient(circle_at_78%_36%,rgba(158,207,255,0.55)_0%,rgba(158,207,255,0)_62%),radial-gradient(circle_at_14%_72%,rgba(189,214,255,0.46)_0%,rgba(189,214,255,0)_58%)] blur-[22px] sm:-left-10 sm:-right-6 sm:-top-6 sm:inset-x-auto sm:rounded-[40px] sm:blur-[34px] lg:-left-14 lg:-right-8 lg:-top-7 lg:rounded-[46px] lg:blur-[36px]" />

          <HeroConversionDemo :demo="demo" />
        </div>
      </div>
    </div>

    <div class="mt-12 rounded-[20px] border border-[#e0e5ef] bg-white/72 px-5 py-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] backdrop-blur-sm sm:px-8">
      <p class="text-center text-[20px] font-medium text-[#364055]">{{ trust.title }}</p>
      <ul class="mt-5 flex flex-wrap items-center justify-center gap-x-5 gap-y-3 text-[15px] text-[#444d61] sm:gap-x-8 sm:text-[17px]">
        <li v-for="(item, index) in trust.items" :key="`${item}-${index}`" class="inline-flex items-center gap-2.5">
          <span class="inline-flex h-4 w-4 items-center justify-center rounded-full bg-[#d4dbea]">
            <span class="h-1.5 w-1.5 rounded-full bg-[#9ba7bf]" />
          </span>
          <span>{{ item }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import HeroConversionDemo from "./HeroConversionDemo.vue";

defineProps({
  hero: {
    type: Object,
    required: true,
  },
  trust: {
    type: Object,
    required: true,
  },
  demo: {
    type: Object,
    required: true,
  },
});
</script>
