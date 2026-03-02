<template>
  <section id="capabilities" class="relative overflow-hidden py-16 scroll-mt-28 sm:py-20 lg:py-24 lg:scroll-mt-32">
    <div id="features" class="pointer-events-none absolute top-0 h-0 w-0" aria-hidden="true" />
    <div class="pointer-events-none absolute inset-0 bg-gradient-to-b from-[#f8fafe] via-[#edf3fd] to-[#e9eef9]" />
    <div
      class="pointer-events-none absolute -left-28 top-6 h-72 w-72 rounded-full bg-[radial-gradient(circle,rgba(154,198,255,0.38)_0%,rgba(154,198,255,0)_68%)] blur-3xl"
    />
    <div
      class="pointer-events-none absolute right-[-96px] top-10 h-80 w-80 rounded-full bg-[radial-gradient(circle,rgba(185,213,255,0.44)_0%,rgba(185,213,255,0)_70%)] blur-3xl"
    />
    <div
      class="pointer-events-none absolute bottom-[-130px] left-1/2 h-80 w-[620px] -translate-x-1/2 rounded-full bg-[radial-gradient(ellipse,rgba(206,224,255,0.34)_0%,rgba(206,224,255,0)_72%)] blur-3xl"
    />

    <div class="relative mx-auto w-full max-w-[1260px] px-4 sm:px-6 lg:px-8">
      <header class="mx-auto max-w-[800px] text-center">
        <h2 class="text-[34px] font-semibold leading-tight tracking-[-0.02em] text-slate-900 sm:text-[40px] lg:text-[44px]">
          {{ capabilities.title }}
        </h2>
        <p class="mx-auto mt-4 max-w-[760px] text-[20px] leading-[1.45] text-slate-600 sm:text-[22px] lg:text-[35px]">
          {{ capabilities.subtitle }}
        </p>
      </header>

      <div class="mt-9 grid grid-cols-1 gap-5 sm:mt-10 md:grid-cols-2 lg:mt-12 lg:grid-cols-3 lg:gap-6">
        <article
          v-for="item in capabilities.items"
          :key="item.id"
          class="flex h-full flex-col rounded-[20px] border border-white/55 bg-white/55 p-5 shadow-[0_16px_38px_rgba(35,55,92,0.12)] backdrop-blur-md transition-transform duration-300 hover:-translate-y-0.5"
        >
          <div
            class="inline-flex h-12 w-12 items-center justify-center rounded-xl border border-[#d2def2] bg-gradient-to-b from-white/90 to-[#ecf3ff] text-[#4c86d8] shadow-[0_6px_16px_rgba(63,118,201,0.14)]"
          >
            <component :is="iconMap[item.icon]" class="h-6 w-6" aria-hidden="true" />
          </div>

          <h3 class="mt-5 text-[28px] font-semibold leading-[1.28] tracking-[-0.01em] text-slate-900">
            {{ item.title }}
          </h3>

          <p class="mt-3 text-[14px] leading-[1.55] text-slate-600 sm:text-[15px]">
            {{ item.description }}
          </p>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { h } from "vue";
import { siteData } from "~/assets/data";

const capabilities = siteData.capabilities;

const iconMap = {
  telegram: () =>
    h(
      "svg",
      {
        viewBox: "0 0 24 24",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg",
      },
      [
        h("path", {
          d: "M21 4.65L17.93 19.11C17.73 20.06 17.2 20.28 16.38 19.82L11.92 16.53L9.76 18.61C9.53 18.85 9.35 19.03 8.9 19.03L9.22 14.5L17.47 7.04C17.83 6.72 17.39 6.54 16.92 6.86L6.72 13.3L2.32 11.93C1.36 11.62 1.34 10.96 2.52 10.5L19.55 3.93C20.34 3.63 21.03 4.12 21 4.65Z",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linejoin": "round",
        }),
      ],
    ),
  analytics: () =>
    h(
      "svg",
      {
        viewBox: "0 0 24 24",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg",
      },
      [
        h("path", {
          d: "M3 17.5H21",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
        }),
        h("path", {
          d: "M5 14.8L9 11.2L12.2 13.8L16 8.9L19 10.7",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
        }),
        h("path", {
          d: "M5.2 20.5V16.6M9 20.5V14.2M12.9 20.5V15.9M16.8 20.5V12.7",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
        }),
      ],
    ),
  cursor: () =>
    h(
      "svg",
      {
        viewBox: "0 0 24 24",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg",
      },
      [
        h("path", {
          d: "M4.5 3.8L17.4 10.2L11.6 12.1L9.7 17.9L4.5 3.8Z",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linejoin": "round",
        }),
        h("path", {
          d: "M15.9 4.4L16.9 2.8M19.6 8.1L21.2 7.1M16.2 8L18 8.2",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
        }),
      ],
    ),
  funnel: () =>
    h(
      "svg",
      {
        viewBox: "0 0 24 24",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg",
      },
      [
        h("path", {
          d: "M4 5.4H20L15.4 10.6H8.6L4 5.4Z",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linejoin": "round",
        }),
        h("path", {
          d: "M8.6 10.6H15.4L13.4 14.7H10.6L8.6 10.6Z",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linejoin": "round",
        }),
        h("path", {
          d: "M10.6 14.7H13.4L12.6 18.6H11.4L10.6 14.7Z",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linejoin": "round",
        }),
      ],
    ),
  seo: () =>
    h(
      "svg",
      {
        viewBox: "0 0 24 24",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg",
      },
      [
        h("path", {
          d: "M10.8 17.6C14.3346 17.6 17.2 14.7346 17.2 11.2C17.2 7.66538 14.3346 4.8 10.8 4.8C7.26538 4.8 4.4 7.66538 4.4 11.2C4.4 14.7346 7.26538 17.6 10.8 17.6Z",
          stroke: "currentColor",
          "stroke-width": "1.6",
        }),
        h("path", {
          d: "M15.5 15.8L20 20.2",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
        }),
        h("path", {
          d: "M8.1 11.6L10.1 13.6L13.8 9.7",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
        }),
      ],
    ),
  report: () =>
    h(
      "svg",
      {
        viewBox: "0 0 24 24",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg",
      },
      [
        h("path", {
          d: "M7.2 3.8H14.5L18.8 8.1V18.9C18.8 19.8 18.1 20.5 17.2 20.5H7.2C6.3 20.5 5.6 19.8 5.6 18.9V5.4C5.6 4.5 6.3 3.8 7.2 3.8Z",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linejoin": "round",
        }),
        h("path", {
          d: "M14.5 3.8V8.1H18.8",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linejoin": "round",
        }),
        h("path", {
          d: "M9 11.2H14.6M9 14.1H14.6",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
        }),
        h("path", {
          d: "M16.9 16.5V12.8M16.9 16.5L15.3 14.9M16.9 16.5L18.5 14.9",
          stroke: "currentColor",
          "stroke-width": "1.6",
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
        }),
      ],
    ),
};
</script>
