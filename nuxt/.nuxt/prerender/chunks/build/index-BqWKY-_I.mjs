globalThis.__timing__.logStart('Load chunks/build/index-BqWKY-_I');import { mergeProps, unref, createVNode, resolveDynamicComponent, ref, reactive, computed, h, useSSRContext } from 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/vue/index.mjs';
import { ssrRenderAttrs, ssrRenderComponent, ssrRenderList, ssrInterpolate, ssrRenderAttr, ssrRenderVNode, ssrRenderStyle, ssrRenderTeleport, ssrRenderClass } from 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/vue/server-renderer/index.mjs';
import { p as publicAssetsURL } from '../_/renderer.mjs';
import { _ as _export_sfc } from './server.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/vue-bundle-renderer/dist/runtime.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/h3/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/ufo/dist/index.mjs';
import '../_/nitro.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/destr/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/hookable/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/ofetch/dist/node.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/node-mock-http/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/unstorage/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/unstorage/drivers/fs.mjs';
import 'file:///C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/@nuxt/nitro-server/dist/runtime/utils/cache-driver.js';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/unstorage/drivers/fs-lite.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/ohash/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/klona/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/defu/dist/defu.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/scule/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/radix3/dist/index.mjs';
import 'node:fs';
import 'node:url';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/pathe/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/unhead/dist/server.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/devalue/index.js';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/unhead/dist/utils.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/unhead/dist/plugins.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/unctx/dist/index.mjs';
import 'file://C:/Users/Alex/Desktop/mini_bitrix/nuxt/node_modules/vue-router/vue-router.node.mjs';

const _imports_0$1 = publicAssetsURL("/brand/logo.svg");
const _sfc_main$9 = {
  __name: "UpHeader",
  __ssrInlineRender: true,
  props: {
    brand: {
      type: Object,
      required: true
    },
    nav: {
      type: Array,
      required: true
    },
    headerCta: {
      type: Object,
      required: true
    }
  },
  setup(__props) {
    const isMobileMenuOpen = ref(false);
    const scrollProgress = ref(0);
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<header${ssrRenderAttrs(mergeProps({ class: "fixed inset-x-0 top-0 z-[120] border-b border-[#dce6f5]/85 bg-[rgba(244,249,255,0.72)] backdrop-blur-[14px]" }, _attrs))} data-v-9bd3b53a><div class="mx-auto w-full max-w-[1400px] px-3 py-2 sm:px-6 sm:py-2.5 lg:px-8" data-v-9bd3b53a><div class="mx-auto flex w-full max-w-[1280px] items-center justify-between gap-2 rounded-[18px] border border-[#dee5f2] bg-white/95 px-3 py-2.5 shadow-[0_12px_36px_rgba(34,51,90,0.08)] backdrop-blur sm:px-4" data-v-9bd3b53a><a href="#top" class="flex min-w-fit items-center gap-2.5 pr-2" data-v-9bd3b53a><img${ssrRenderAttr("src", _imports_0$1)} alt="TrackNode" class="h-8 w-8" data-v-9bd3b53a><span class="text-[22px] font-semibold tracking-[-0.02em] text-[#1f2738]" data-v-9bd3b53a>${ssrInterpolate(__props.brand.name)}</span></a><nav class="hidden items-center gap-8 lg:flex" data-v-9bd3b53a><!--[-->`);
      ssrRenderList(__props.nav, (item) => {
        _push(`<a${ssrRenderAttr("href", item.href)} class="inline-flex items-center gap-1.5 text-[16px] font-medium text-[#2a3244] transition-colors hover:text-[#1d5fff]" data-v-9bd3b53a>${ssrInterpolate(item.label)}</a>`);
      });
      _push(`<!--]--></nav><div class="flex items-center gap-2 sm:gap-2.5" data-v-9bd3b53a><a${ssrRenderAttr("href", __props.headerCta.href)}${ssrRenderAttr("target", __props.headerCta.target || null)}${ssrRenderAttr("rel", __props.headerCta.rel || null)} class="btn-brand-gradient hidden min-h-10 items-center justify-center rounded-[11px] px-4 text-[15px] font-semibold text-white shadow-[0_10px_20px_rgba(47,106,255,0.35)] transition hover:brightness-105 sm:inline-flex sm:px-6 sm:text-[16px]" data-v-9bd3b53a>${ssrInterpolate(__props.headerCta.label)}</a><button type="button" aria-label="Menu" class="inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#d7dfee] bg-white text-[#2a3246] lg:hidden" data-v-9bd3b53a><svg viewBox="0 0 20 20" class="h-[16px] w-[16px]" fill="none" aria-hidden="true" data-v-9bd3b53a><path d="M4 6H16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" data-v-9bd3b53a></path><path d="M4 10H16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" data-v-9bd3b53a></path><path d="M4 14H16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" data-v-9bd3b53a></path></svg></button></div></div></div><div class="header-scroll-progress" aria-hidden="true" data-v-9bd3b53a><span style="${ssrRenderStyle({ transform: `scaleX(${scrollProgress.value})` })}" data-v-9bd3b53a></span></div>`);
      ssrRenderTeleport(_push, (_push2) => {
        if (isMobileMenuOpen.value) {
          _push2(`<div class="mobile-menu-wrap lg:hidden" data-v-9bd3b53a><button class="mobile-menu-overlay" type="button" aria-label="\u0420\u2014\u0420\xB0\u0420\u0454\u0421\u0402\u0421\u2039\u0421\u201A\u0421\u040A \u0420\u0458\u0420\xB5\u0420\u0405\u0421\u040B" data-v-9bd3b53a></button><aside class="mobile-menu-sheet" role="dialog" aria-modal="true" aria-label="\u0420\u045A\u0420\u0455\u0420\xB1\u0420\u0451\u0420\xBB\u0421\u040A\u0420\u0405\u0420\u0455\u0420\xB5 \u0420\u0458\u0420\xB5\u0420\u0405\u0421\u040B" data-v-9bd3b53a><div class="mobile-menu-head" data-v-9bd3b53a><span data-v-9bd3b53a>\u0420\u045A\u0420\xB5\u0420\u0405\u0421\u040B</span><button type="button" aria-label="\u0420\u2014\u0420\xB0\u0420\u0454\u0421\u0402\u0421\u2039\u0421\u201A\u0421\u040A \u0420\u0458\u0420\xB5\u0420\u0405\u0421\u040B" data-v-9bd3b53a><svg viewBox="0 0 20 20" fill="none" aria-hidden="true" data-v-9bd3b53a><path d="M5 5L15 15M15 5L5 15" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" data-v-9bd3b53a></path></svg></button></div><nav class="mobile-menu-nav" data-v-9bd3b53a><!--[-->`);
          ssrRenderList(__props.nav, (item) => {
            _push2(`<a${ssrRenderAttr("href", item.href)} data-v-9bd3b53a>${ssrInterpolate(item.label)}</a>`);
          });
          _push2(`<!--]--></nav><div class="mobile-menu-actions" data-v-9bd3b53a><a href="/login" data-v-9bd3b53a> \u0420\u2019\u0420\u0455\u0420\u2116\u0421\u201A\u0420\u0451 </a><a href="/register" data-v-9bd3b53a> \u0420\u2014\u0420\xB0\u0421\u0402\u0420\xB5\u0420\u0456\u0420\u0451\u0421\u0403\u0421\u201A\u0421\u0402\u0420\u0451\u0421\u0402\u0420\u0455\u0420\u0406\u0420\xB0\u0421\u201A\u0421\u040A\u0421\u0403\u0421\u040F </a></div></aside></div>`);
        } else {
          _push2(`<!---->`);
        }
      }, "body", false, _parent);
      _push(`</header>`);
    };
  }
};
const _sfc_setup$9 = _sfc_main$9.setup;
_sfc_main$9.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/UpHeader.vue");
  return _sfc_setup$9 ? _sfc_setup$9(props, ctx) : void 0;
};
const __nuxt_component_0 = /* @__PURE__ */ _export_sfc(_sfc_main$9, [["__scopeId", "data-v-9bd3b53a"]]);
const START_CONVERSION = 8;
const CHART_LINE_PATH = "M20 122 C58 118 89 109 118 98 C148 86 177 76 205 61 C229 49 251 38 280 24";
const CHART_AREA_PATH = "M20 122 C58 118 89 109 118 98 C148 86 177 76 205 61 C229 49 251 38 280 24 L280 134 L20 134 Z";
const _sfc_main$8 = {
  __name: "HeroConversionDemo",
  __ssrInlineRender: true,
  setup(__props) {
    const INITIAL_MARKER = { x: 20, y: 122 };
    ref(null);
    const lineLength = ref(1);
    ref({ ...INITIAL_MARKER });
    const isAccented = ref(false);
    const frame = reactive({
      conversion: START_CONVERSION,
      progress: 0,
      visits: 18200,
      leads: 124,
      marker: { ...INITIAL_MARKER }
    });
    const areaOpacity = computed(() => Math.max(0, Math.min(0.46, frame.progress * 0.52)));
    const lineStyle = computed(() => ({
      strokeDasharray: lineLength.value,
      strokeDashoffset: lineLength.value * (1 - frame.progress),
      filter: "drop-shadow(0 0 5px rgba(34,197,94,0.28))"
    }));
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<div${ssrRenderAttrs(mergeProps({ class: "relative aspect-[16/10] min-h-[300px] w-full max-w-full overflow-hidden rounded-[24px] border border-white/70 bg-[#edf3ff] shadow-[0_30px_80px_rgba(2,6,23,0.16)] sm:min-h-[360px] sm:rounded-[30px] lg:min-h-[420px]" }, _attrs))}><div class="absolute inset-[1px] overflow-hidden rounded-[28px] bg-gradient-to-b from-white/70 to-slate-50/60"><div class="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(191,219,254,0.55)_0%,rgba(191,219,254,0)_48%),radial-gradient(circle_at_12%_88%,rgba(186,230,253,0.4)_0%,rgba(186,230,253,0)_55%)]"></div><div class="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(to_right,rgba(148,163,184,0.18)_1px,transparent_1px),linear-gradient(to_bottom,rgba(148,163,184,0.18)_1px,transparent_1px)] [background-size:34px_34px]"></div><div class="relative z-10 flex h-full min-w-0 flex-col gap-3 p-3.5 sm:p-5"><div class="flex min-w-0 flex-wrap items-center justify-between gap-2"><p class="min-w-0 max-w-full break-words text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500 sm:text-[12px]">Dashboard preview</p><span class="shrink-0 rounded-full bg-white/75 px-3 py-1 text-[11px] font-medium text-slate-700 backdrop-blur">LIVE PREVIEW</span></div><div class="grid min-w-0 flex-1 auto-rows-[minmax(0,1fr)] grid-cols-12 gap-3"><section class="${ssrRenderClass([isAccented.value ? "ring-1 ring-emerald-300/80 shadow-[0_0_0_1px_rgba(134,239,172,0.55),0_18px_36px_rgba(21,128,61,0.18)]" : "", "col-span-12 min-w-0 rounded-2xl border border-white/80 bg-white/70 p-3.5 shadow-[0_16px_30px_rgba(15,23,42,0.09)] backdrop-blur-sm transition-all duration-500 sm:p-4 lg:col-span-8 lg:row-span-2"])}"><div class="flex min-w-0 items-start justify-between gap-3"><div class="min-w-0"><p class="text-[14px] font-semibold text-slate-700">\u041A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u044F</p><p class="mt-1 text-[30px] font-bold tracking-[-0.02em] text-slate-900 sm:text-[38px]">${ssrInterpolate(frame.conversion.toFixed(2))}%</p><p class="mt-1 text-[12px] text-slate-500">\u0437\u0430 \u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 7 \u0434\u043D\u0435\u0439</p></div><span class="shrink-0 rounded-full border border-emerald-200/90 bg-emerald-50/95 px-2.5 py-1 text-[12px] font-semibold text-emerald-700">+7.5%</span></div><div class="mt-3 h-[136px] sm:h-[150px]"><svg viewBox="0 0 300 140" class="h-full w-full"><defs><linearGradient id="conversion-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#22c55e" stop-opacity="0.42"></stop><stop offset="100%" stop-color="#22c55e" stop-opacity="0"></stop></linearGradient><linearGradient id="conversion-stroke" x1="20" y1="120" x2="280" y2="20" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#16a34a" stop-opacity="0.7"></stop><stop offset="100%" stop-color="#22c55e" stop-opacity="1"></stop></linearGradient></defs><g opacity="0.25" stroke="rgba(148,163,184,0.5)" stroke-width="1"><line x1="20" y1="120" x2="280" y2="120"></line><line x1="20" y1="94" x2="280" y2="94"></line><line x1="20" y1="68" x2="280" y2="68"></line><line x1="20" y1="42" x2="280" y2="42"></line></g><path${ssrRenderAttr("d", CHART_AREA_PATH)} fill="url(#conversion-fill)"${ssrRenderAttr("opacity", areaOpacity.value)}></path><path${ssrRenderAttr("d", CHART_LINE_PATH)} fill="none" stroke="url(#conversion-stroke)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="${ssrRenderStyle(lineStyle.value)}"></path><circle${ssrRenderAttr("cx", frame.marker.x)}${ssrRenderAttr("cy", frame.marker.y)} r="4.8" fill="#22c55e"></circle><circle${ssrRenderAttr("cx", frame.marker.x)}${ssrRenderAttr("cy", frame.marker.y)} r="9" fill="none" stroke="rgba(34,197,94,0.35)" stroke-width="2" class="animate-[ping_2.4s_ease-out_infinite]"></circle></svg></div></section><section class="col-span-6 min-w-0 rounded-2xl border border-white/80 bg-white/70 p-3 shadow-[0_10px_22px_rgba(15,23,42,0.08)] backdrop-blur-sm lg:col-span-4"><p class="text-[12px] font-medium text-slate-500">\u0412\u0438\u0437\u0438\u0442\u044B</p><p class="mt-2 text-[24px] font-bold tracking-[-0.02em] text-slate-900">${ssrInterpolate((frame.visits / 1e3).toFixed(1))}K</p><p class="mt-1 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 animate-[pulse_5.8s_ease-in-out_infinite]"><span aria-hidden="true">\u2197</span> +3.2% </p></section><section class="col-span-6 min-w-0 rounded-2xl border border-white/80 bg-white/70 p-3 shadow-[0_10px_22px_rgba(15,23,42,0.08)] backdrop-blur-sm lg:col-span-4"><p class="text-[12px] font-medium text-slate-500">\u0417\u0430\u044F\u0432\u043A\u0438</p><p class="mt-2 text-[24px] font-bold tracking-[-0.02em] text-slate-900">${ssrInterpolate(frame.leads)}</p><p class="mt-1 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 animate-[pulse_6.1s_ease-in-out_infinite]"><span aria-hidden="true">\u2197</span> +12% </p></section></div></div></div></div>`);
    };
  }
};
const _sfc_setup$8 = _sfc_main$8.setup;
_sfc_main$8.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/HeroConversionDemo.vue");
  return _sfc_setup$8 ? _sfc_setup$8(props, ctx) : void 0;
};
const _sfc_main$7 = {
  __name: "Hero",
  __ssrInlineRender: true,
  props: {
    hero: {
      type: Object,
      required: true
    },
    trust: {
      type: Object,
      required: true
    }
  },
  setup(__props) {
    return (_ctx, _push, _parent, _attrs) => {
      const _component_HeroConversionDemo = _sfc_main$8;
      _push(`<section${ssrRenderAttrs(mergeProps({ class: "relative z-10 mx-auto mt-8 w-full max-w-full overflow-hidden px-4 sm:max-w-[1280px] sm:px-0 lg:mt-9" }, _attrs))}><div class="grid items-center gap-7 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)] lg:gap-8"><div class="order-1 min-w-0"><h1 class="max-w-full text-[34px] font-semibold leading-[1.08] tracking-[-0.02em] text-[#1f273a] sm:max-w-[560px] sm:text-[49px] lg:text-[62px]"><!--[-->`);
      ssrRenderList(__props.hero.titleLines, (line) => {
        _push(`<span class="block">${ssrInterpolate(line)}</span>`);
      });
      _push(`<!--]--></h1><p class="mt-6 max-w-full text-[18px] leading-[1.5] text-[#4c566d] sm:max-w-[560px] sm:text-[19px]">${ssrInterpolate(__props.hero.description)}</p><div class="mt-8 flex flex-wrap gap-3"><a${ssrRenderAttr("href", __props.hero.primaryCta.href)}${ssrRenderAttr("target", __props.hero.primaryCta.target || null)}${ssrRenderAttr("rel", __props.hero.primaryCta.rel || null)} class="btn-brand-gradient inline-flex w-full min-h-12 items-center justify-center rounded-[12px] px-6 text-[18px] font-semibold text-white shadow-[0_12px_22px_rgba(47,107,255,0.35)] transition hover:brightness-105 sm:w-auto">${ssrInterpolate(__props.hero.primaryCta.label)}</a><a${ssrRenderAttr("href", __props.hero.secondaryCta.href)}${ssrRenderAttr("target", __props.hero.secondaryCta.target || null)}${ssrRenderAttr("rel", __props.hero.secondaryCta.rel || null)} class="inline-flex w-full min-h-12 items-center justify-center gap-2 rounded-[12px] border border-[#d5ddeb] bg-white/95 px-6 text-[18px] font-semibold text-[#374056] shadow-[0_8px_18px_rgba(34,50,86,0.08)] transition hover:border-[#c5d0e4] sm:w-auto">${ssrInterpolate(__props.hero.secondaryCta.label)} <svg viewBox="0 0 16 16" class="h-4 w-4" fill="none" aria-hidden="true"><path d="M5 3L10 8L5 13" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path></svg></a></div></div><div class="order-2 min-w-0 lg:pl-1"><div class="relative mx-auto w-full max-w-full overflow-hidden sm:max-w-[900px]"><div class="pointer-events-none absolute inset-x-0 -top-4 bottom-2 rounded-[28px] bg-[radial-gradient(circle_at_78%_36%,rgba(158,207,255,0.55)_0%,rgba(158,207,255,0)_62%),radial-gradient(circle_at_14%_72%,rgba(189,214,255,0.46)_0%,rgba(189,214,255,0)_58%)] blur-[22px] sm:-left-10 sm:-right-6 sm:-top-6 sm:inset-x-auto sm:rounded-[40px] sm:blur-[34px] lg:-left-14 lg:-right-8 lg:-top-7 lg:rounded-[46px] lg:blur-[36px]"></div>`);
      _push(ssrRenderComponent(_component_HeroConversionDemo, null, null, _parent));
      _push(`<div class="mx-auto mt-2 h-[9px] w-[90%] rounded-b-[18px] bg-gradient-to-b from-[#dbe4f3] to-[#b8c7df] shadow-[0_10px_20px_rgba(41,61,98,0.25)]"></div></div></div></div><div class="mt-12 rounded-[20px] border border-[#e0e5ef] bg-white/72 px-5 py-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] backdrop-blur-sm sm:px-8"><p class="text-center text-[20px] font-medium text-[#364055]">${ssrInterpolate(__props.trust.title)}</p><ul class="mt-5 flex flex-wrap items-center justify-center gap-x-5 gap-y-3 text-[15px] text-[#444d61] sm:gap-x-8 sm:text-[17px]"><!--[-->`);
      ssrRenderList(__props.trust.items, (item, index) => {
        _push(`<li class="inline-flex items-center gap-2.5"><span class="inline-flex h-4 w-4 items-center justify-center rounded-full bg-[#d4dbea]"><span class="h-1.5 w-1.5 rounded-full bg-[#9ba7bf]"></span></span><span>${ssrInterpolate(item)}</span></li>`);
      });
      _push(`<!--]--></ul></div></section>`);
    };
  }
};
const _sfc_setup$7 = _sfc_main$7.setup;
_sfc_main$7.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/Hero.vue");
  return _sfc_setup$7 ? _sfc_setup$7(props, ctx) : void 0;
};
const homepageData = {
  brand: { name: "TrackNode" },
  nav: [
    { label: "\u0420\u2019\u0420\u0455\u0420\xB7\u0420\u0458\u0420\u0455\u0420\xB6\u0420\u0405\u0420\u0455\u0421\u0403\u0421\u201A\u0420\u0451", href: "#capabilities" },
    { label: "\u0420\u0459\u0420\xB0\u0420\u0454 \u0421\u0402\u0420\xB0\u0420\xB1\u0420\u0455\u0421\u201A\u0420\xB0\u0420\xB5\u0421\u201A", href: "#how" },
    { label: "\u0420\u045E\u0420\xB0\u0421\u0402\u0420\u0451\u0421\u201E\u0421\u2039", href: "#pricing" },
    { label: "\u0420\u045B\u0421\u201A\u0420\xB7\u0421\u2039\u0420\u0406\u0421\u2039", href: "#reviews" },
    { label: "FAQ", href: "#faq" },
    { label: "\u0420\u0459\u0420\u0455\u0420\u0405\u0421\u201A\u0420\xB0\u0420\u0454\u0421\u201A\u0421\u2039", href: "#footer" }
  ],
  headerCta: { label: "\u0420\u2019\u0420\u0455\u0420\u2116\u0421\u201A\u0420\u0451", href: "/login" },
  hero: {
    titleLines: [
      "\u0420\u0452\u0420\u0405\u0420\xB0\u0420\xBB\u0420\u0451\u0421\u201A\u0420\u0451\u0420\u0454\u0420\xB0 \u0421\u0403\u0420\xB0\u0420\u2116\u0421\u201A\u0420\xB0,",
      "\u0421\u0453\u0420\u0406\u0420\xB5\u0420\u0491\u0420\u0455\u0420\u0458\u0420\xBB\u0420\xB5\u0420\u0405\u0420\u0451\u0421\u040F \u0420\u0455 \u0420\xB7\u0420\xB0\u0421\u040F\u0420\u0406\u0420\u0454\u0420\xB0\u0421\u2026",
      "\u0420\u0406 Telegram \u0420\u0451 SEO-\u0420\xB0\u0421\u0453\u0420\u0491\u0420\u0451\u0421\u201A \u0432\u0402\u201D",
      "\u0420\u0406 \u0420\u0455\u0420\u0491\u0420\u0405\u0420\u0455\u0420\u0458 \u0421\u0403\u0420\xB5\u0421\u0402\u0420\u0406\u0420\u0451\u0421\u0403\u0420\xB5"
    ],
    description: "TrackNode \u0421\u201E\u0420\u0451\u0420\u0454\u0421\u0403\u0420\u0451\u0421\u0402\u0421\u0453\u0420\xB5\u0421\u201A \u0420\u0405\u0420\u0455\u0420\u0406\u0421\u2039\u0420\xB5 \u0420\xB7\u0420\xB0\u0421\u040F\u0420\u0406\u0420\u0454\u0420\u0451 \u0420\u0451 \u0420\xBB\u0420\u0451\u0420\u0491\u0421\u2039 \u0421\u0403 \u0421\u0403\u0420\xB0\u0420\u2116\u0421\u201A\u0420\xB0 \u0420\u0451 \u0420\u0458\u0420\u0456\u0420\u0405\u0420\u0455\u0420\u0406\u0420\xB5\u0420\u0405\u0420\u0405\u0420\u0455 \u0420\u0455\u0421\u201A\u0420\u0457\u0421\u0402\u0420\xB0\u0420\u0406\u0420\xBB\u0421\u040F\u0420\xB5\u0421\u201A \u0421\u0453\u0420\u0406\u0420\xB5\u0420\u0491\u0420\u0455\u0420\u0458\u0420\xBB\u0420\xB5\u0420\u0405\u0420\u0451\u0421\u040F \u0420\u0406 Telegram. \u0420\u201D\u0420\u0455\u0420\u0457\u0420\u0455\u0420\xBB\u0420\u0405\u0420\u0451\u0421\u201A\u0420\xB5\u0420\xBB\u0421\u040A\u0420\u0405\u0420\u0455 \u0420\u0457\u0420\u0455\u0420\u0454\u0420\xB0\u0420\xB7\u0421\u2039\u0420\u0406\u0420\xB0\u0420\xB5\u0421\u201A \u0420\xB0\u0420\u0405\u0420\xB0\u0420\xBB\u0420\u0451\u0421\u201A\u0420\u0451\u0420\u0454\u0421\u0453 \u0420\u0457\u0420\u0455\u0421\u0403\u0420\xB5\u0421\u2030\u0420\xB5\u0420\u0405\u0420\u0451\u0420\u2116 \u0420\u0451 \u0420\u0451\u0421\u0403\u0421\u201A\u0420\u0455\u0421\u2021\u0420\u0405\u0420\u0451\u0420\u0454\u0420\u0455\u0420\u0406 \u0421\u201A\u0421\u0402\u0420\xB0\u0421\u201E\u0420\u0451\u0420\u0454\u0420\xB0 \u0420\u0451 \u0420\u0457\u0420\u0455\u0420\u0458\u0420\u0455\u0420\u0456\u0420\xB0\u0420\xB5\u0421\u201A \u0420\u0405\u0420\xB0\u0421\u2026\u0420\u0455\u0420\u0491\u0420\u0451\u0421\u201A\u0421\u040A SEO \u0420\u0451 \u0421\u201A\u0420\xB5\u0421\u2026\u0420\u0405\u0420\u0451\u0421\u2021\u0420\xB5\u0421\u0403\u0420\u0454\u0420\u0451\u0420\xB5 \u0420\u0455\u0421\u20AC\u0420\u0451\u0420\xB1\u0420\u0454\u0420\u0451.",
    primaryCta: { label: "\u0420\u2014\u0420\xB0\u0421\u0402\u0420\xB5\u0420\u0456\u0420\u0451\u0421\u0403\u0421\u201A\u0421\u0402\u0420\u0451\u0421\u0402\u0420\u0455\u0420\u0406\u0420\xB0\u0421\u201A\u0421\u040A\u0421\u0403\u0421\u040F", href: "/register" },
    secondaryCta: { label: "\u0420\u045F\u0420\u0455\u0420\u0491\u0420\u0454\u0420\xBB\u0421\u040B\u0421\u2021\u0420\u0451\u0421\u201A\u0421\u040A \u0421\u0403\u0420\xB0\u0420\u2116\u0421\u201A", href: "#how" }
  },
  trust: {
    title: "\u0420\x98\u0421\u0403\u0420\u0457\u0420\u0455\u0420\xBB\u0421\u040A\u0420\xB7\u0421\u0453\u0421\u040B\u0421\u201A \u0420\u0491\u0420\xBB\u0421\u040F \u0420\u0454\u0420\u0455\u0420\u0405\u0421\u201A\u0421\u0402\u0420\u0455\u0420\xBB\u0421\u040F \u0420\xB7\u0420\xB0\u0421\u040F\u0420\u0406\u0420\u0455\u0420\u0454 \u0420\u0451 \u0421\u0402\u0420\u0455\u0421\u0403\u0421\u201A\u0420\xB0 \u0420\u0454\u0420\u0455\u0420\u0405\u0420\u0406\u0420\xB5\u0421\u0402\u0421\u0403\u0420\u0451\u0420\u0451",
    items: ["Company", "Brand", "Studio", "Agency", "Startup", "Business", "Business"]
  }
};
const siteData = {
  capabilities: {
    title: "\u0412\u043E\u0437\u043C\u043E\u0436\u043D\u043E\u0441\u0442\u0438 TrackNode",
    subtitle: "\u041A\u043E\u043D\u0442\u0440\u043E\u043B\u0438\u0440\u0443\u0439\u0442\u0435 \u0437\u0430\u044F\u0432\u043A\u0438, \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u044F, \u043F\u043E\u0432\u0435\u0434\u0435\u043D\u0438\u0435, SEO \u0438 \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u043E\u0435 \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u0441\u0430\u0439\u0442\u0430.",
    items: [
      {
        id: "tg-leads",
        title: "\u0423\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u043E \u0437\u0430\u044F\u0432\u043A\u0430\u0445 \u0432 Telegram",
        description: "\u041F\u043E\u043B\u0443\u0447\u0430\u0439\u0442\u0435 \u043C\u0433\u043D\u043E\u0432\u0435\u043D\u043D\u044B\u0435 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u043E \u043D\u043E\u0432\u044B\u0445 \u0437\u0430\u044F\u0432\u043A\u0430\u0445 \u043F\u0440\u044F\u043C\u043E \u0432 Telegram, \u0447\u0442\u043E\u0431\u044B \u0431\u044B\u0441\u0442\u0440\u043E \u0440\u0435\u0430\u0433\u0438\u0440\u043E\u0432\u0430\u0442\u044C.",
        icon: "telegram"
      },
      {
        id: "traffic-analytics",
        title: "\u0410\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0430 \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u0439 \u0438 \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u043E\u0432 \u0442\u0440\u0430\u0444\u0438\u043A\u0430",
        description: "\u041E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u0439\u0442\u0435 \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u044F, \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u044B, \u043A\u0430\u043D\u0430\u043B\u044B, \u0437\u0430\u0438\u043D\u0442\u0435\u0440\u0435\u0441\u043E\u0432\u0430\u043D\u043D\u043E\u0441\u0442\u044C \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0435\u0439 \u0438 \u0430\u043D\u0430\u043B\u0438\u0437\u0438\u0440\u0443\u0439\u0442\u0435 \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0438 \u0442\u0440\u0430\u0444\u0438\u043A\u0430.",
        icon: "analytics"
      },
      {
        id: "user-behavior",
        title: "\u041F\u043E\u0432\u0435\u0434\u0435\u043D\u0438\u0435 \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044F",
        description: "\u0417\u0430\u043F\u0438\u0441\u044B\u0432\u0430\u0439\u0442\u0435 \u043A\u043B\u0438\u043A\u0438, \u043F\u0435\u0440\u0435\u0445\u043E\u0434\u044B, \u043F\u0435\u0440\u0435\u043C\u0435\u0449\u0435\u043D\u0438\u044F \u0438 \u0441\u0442\u0440\u043E\u0439\u0442\u0435 \u043A\u0430\u0440\u0442\u044B \u043A\u043B\u0438\u043A\u043E\u0432, \u0447\u0442\u043E\u0431\u044B \u0432\u0438\u0434\u0435\u0442\u044C \u0432\u0435\u0441\u044C \u043F\u0443\u0442\u044C \u043A\u043B\u0438\u0435\u043D\u0442\u0430.",
        icon: "cursor"
      },
      {
        id: "funnels",
        title: "\u0412\u043E\u0440\u043E\u043D\u043A\u0438 \u0438 \u043A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u044F",
        description: "\u0421\u043E\u0437\u0434\u0430\u0432\u0430\u0439\u0442\u0435 \u0432\u043E\u0440\u043E\u043D\u043A\u0438 \u043F\u0440\u043E\u0434\u0430\u0436, \u0440\u0430\u0437\u0431\u0438\u0432\u0430\u0439\u0442\u0435 \u0438\u0445 \u043D\u0430 \u044D\u0442\u0430\u043F\u044B, \u0430\u043D\u0430\u043B\u0438\u0437\u0438\u0440\u0443\u0439\u0442\u0435, \u0433\u0434\u0435 \u0442\u0435\u0440\u044F\u044E\u0442\u0441\u044F \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0438 \u0438 \u0437\u0430\u044F\u0432\u043A\u0438.",
        icon: "funnel"
      },
      {
        id: "seo-audit",
        title: "SEO-\u0430\u0443\u0434\u0438\u0442 \u0438 \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u0438\u0435 \u043E\u0448\u0438\u0431\u043A\u0438",
        description: "\u041D\u0430\u0445\u043E\u0434\u0438\u0442\u0435 \u043E\u0448\u0438\u0431\u043A\u0438, \u0432\u043B\u0438\u044F\u044E\u0449\u0438\u0435 \u043D\u0430 \u043F\u0440\u043E\u0434\u0432\u0438\u0436\u0435\u043D\u0438\u0435 \u0441\u0430\u0439\u0442\u0430, \u0443\u043B\u0443\u0447\u0448\u0430\u0439\u0442\u0435 SEO-\u043F\u043E\u043A\u0430\u0437\u0430\u0442\u0435\u043B\u0438 \u0438 \u043F\u043E\u043B\u0443\u0447\u0430\u0439\u0442\u0435 \u0441\u043E\u0432\u0435\u0442\u044B \u043F\u043E \u0443\u043B\u0443\u0447\u0448\u0435\u043D\u0438\u044E.",
        icon: "seo"
      },
      {
        id: "reports",
        title: "\u041E\u0442\u0447\u0451\u0442\u044B \u0438 \u044D\u043A\u0441\u043F\u043E\u0440\u0442",
        description: "\u041F\u043E\u043B\u0443\u0447\u0430\u0439\u0442\u0435 \u0433\u043E\u0442\u043E\u0432\u044B\u0439 \u043E\u0442\u0447\u0451\u0442 \u0432 PDF \u043F\u043E \u043A\u043B\u044E\u0447\u0435\u0432\u044B\u043C \u043C\u0435\u0442\u0440\u0438\u043A\u0430\u043C \u0438 \u044D\u043A\u0441\u043F\u043E\u0440\u0442\u0438\u0440\u0443\u0439\u0442\u0435 \u0434\u0430\u043D\u043D\u044B\u0435 \u0432 \u0443\u0434\u043E\u0431\u043D\u043E\u043C \u0444\u043E\u0440\u043C\u0430\u0442\u0435.",
        icon: "report"
      }
    ]
  },
  pricing: {
    title: "\u0422\u0430\u0440\u0438\u0444\u044B",
    subtitle: "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0443\u0434\u043E\u0431\u043D\u044B\u0439 \u043F\u043B\u0430\u043D \u0438 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0430\u0439\u0442\u0435 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0443, \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u0438 SEO-\u043A\u043E\u043D\u0442\u0440\u043E\u043B\u044C \u0432 \u043E\u0434\u043D\u043E\u043C \u0438\u043D\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u0435.",
    plans: [
      {
        name: "\u0421\u0442\u0430\u0440\u0442",
        price: "1 990 \u20BD/\u043C\u0435\u0441",
        description: "\u0414\u043B\u044F \u043D\u0435\u0431\u043E\u043B\u044C\u0448\u0438\u0445 \u043F\u0440\u043E\u0435\u043A\u0442\u043E\u0432 \u0438 \u0431\u044B\u0441\u0442\u0440\u043E\u0433\u043E \u0441\u0442\u0430\u0440\u0442\u0430.",
        features: [
          "\u0411\u0430\u0437\u043E\u0432\u0430\u044F \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0430 \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u0439",
          "Telegram-\u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u043E \u0437\u0430\u044F\u0432\u043A\u0430\u0445",
          "\u041E\u0442\u0447\u0451\u0442\u044B \u043F\u043E \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0430\u043C \u0442\u0440\u0430\u0444\u0438\u043A\u0430",
          "SEO-\u0430\u0443\u0434\u0438\u0442 \u0434\u043E 100 \u0441\u0442\u0440\u0430\u043D\u0438\u0446"
        ]
      },
      {
        name: "\u0411\u0438\u0437\u043D\u0435\u0441",
        price: "3 990 \u20BD/\u043C\u0435\u0441",
        description: "\u041E\u043F\u0442\u0438\u043C\u0430\u043B\u044C\u043D\u044B\u0439 \u043F\u043B\u0430\u043D \u0434\u043B\u044F \u0440\u043E\u0441\u0442\u0430 \u043A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u0438.",
        features: [
          "\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043D\u043D\u0430\u044F \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0430 \u0438 \u0432\u043E\u0440\u043E\u043D\u043A\u0438",
          "\u041F\u0440\u0438\u043E\u0440\u0438\u0442\u0435\u0442\u043D\u044B\u0435 Telegram-\u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F",
          "\u041F\u043E\u0432\u0435\u0434\u0435\u043D\u0447\u0435\u0441\u043A\u0438\u0435 \u043E\u0442\u0447\u0451\u0442\u044B \u0438 \u0441\u0435\u0433\u043C\u0435\u043D\u0442\u044B",
          "SEO-\u0430\u0443\u0434\u0438\u0442 \u0434\u043E 300 \u0441\u0442\u0440\u0430\u043D\u0438\u0446",
          "\u0421\u0440\u0430\u0432\u043D\u0435\u043D\u0438\u0435 \u043F\u0435\u0440\u0438\u043E\u0434\u043E\u0432 \u0438 \u044D\u043A\u0441\u043F\u043E\u0440\u0442"
        ],
        featured: true
      },
      {
        name: "\u041F\u0440\u043E\u0444\u0438",
        price: "6 990 \u20BD/\u043C\u0435\u0441",
        description: "\u0414\u043B\u044F \u043A\u043E\u043C\u0430\u043D\u0434 \u0441 \u0431\u043E\u043B\u044C\u0448\u0438\u043C \u0442\u0440\u0430\u0444\u0438\u043A\u043E\u043C \u0438 \u0441\u043B\u043E\u0436\u043D\u043E\u0439 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u043E\u0439.",
        features: [
          "\u041C\u0443\u043B\u044C\u0442\u0438\u043F\u0440\u043E\u0435\u043A\u0442\u044B \u0438 \u043A\u043E\u043C\u0430\u043D\u0434\u043D\u044B\u0439 \u0434\u043E\u0441\u0442\u0443\u043F",
          "\u0413\u0438\u0431\u043A\u0438\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u044F \u0438 \u043A\u0430\u0441\u0442\u043E\u043C\u043D\u044B\u0435 \u0446\u0435\u043B\u0438",
          "\u0410\u0432\u0442\u043E\u043E\u0442\u0447\u0451\u0442\u044B \u0438 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043D\u043D\u044B\u0439 \u044D\u043A\u0441\u043F\u043E\u0440\u0442",
          "SEO-\u0430\u0443\u0434\u0438\u0442 \u0434\u043E 1000 \u0441\u0442\u0440\u0430\u043D\u0438\u0446",
          "\u041F\u0435\u0440\u0441\u043E\u043D\u0430\u043B\u044C\u043D\u0430\u044F \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0430 \u043C\u043E\u043D\u0438\u0442\u043E\u0440\u0438\u043D\u0433\u0430"
        ]
      }
    ]
  },
  reviews: {
    title: "\u041E\u0442\u0437\u044B\u0432\u044B",
    subtitle: "\u0420\u0435\u0430\u043B\u044C\u043D\u044B\u0435 \u043F\u0440\u043E\u0435\u043A\u0442\u044B TrackNode: \u0447\u0442\u043E \u0438\u0437\u043C\u0435\u043D\u0438\u043B\u043E\u0441\u044C \u043F\u043E\u0441\u043B\u0435 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0438 \u0438 Telegram-\u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u0439.",
    items: [
      {
        projectTitle: "\u041F\u0440\u043E\u0435\u043A\u0442 AI-\u043F\u0440\u043E\u0434\u0430\u0436",
        description: "business",
        date: "14.02.2026",
        text: "\u0423\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u0432 Telegram \u0441\u043F\u0430\u0441\u0430\u044E\u0442 \u0432\u0440\u0435\u043C\u044F: \u043B\u0438\u0434\u044B \u043D\u0435 \u0442\u0435\u0440\u044F\u044E\u0442\u0441\u044F, \u0430 \u043F\u043E \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0435 \u0441\u0442\u0430\u043B\u043E \u043F\u043E\u043D\u044F\u0442\u043D\u043E, \u0433\u0434\u0435 \u043F\u0440\u043E\u0441\u0435\u0434\u0430\u0435\u0442 \u043A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u044F."
      },
      {
        projectTitle: "\u0422\u0443\u0440\u0438\u0441\u0442\u0438\u0447\u0435\u0441\u043A\u0438\u0439 \u043F\u0440\u043E\u0435\u043A\u0442",
        description: "tourism project",
        date: "03.02.2026",
        text: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u043B\u0438 \u0437\u0430 \u043F\u0430\u0440\u0443 \u043C\u0438\u043D\u0443\u0442. \u0422\u0435\u043F\u0435\u0440\u044C \u0432\u0438\u0434\u0438\u043C \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0438 \u0442\u0440\u0430\u0444\u0438\u043A\u0430 \u0438 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044F \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0435\u0439, \u0430 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F \u043F\u0440\u0438\u0445\u043E\u0434\u044F\u0442 \u0441\u0440\u0430\u0437\u0443."
      },
      {
        projectTitle: "\u0418\u043D\u0442\u0435\u0440\u043D\u0435\u0442-\u043C\u0430\u0433\u0430\u0437\u0438\u043D",
        description: "start-up",
        date: "20.01.2026",
        text: "\u041D\u0430\u043A\u043E\u043D\u0435\u0446-\u0442\u043E \u043F\u0440\u043E\u0437\u0440\u0430\u0447\u043D\u0430\u044F \u043A\u0430\u0440\u0442\u0438\u043D\u0430 \u043F\u043E \u043F\u043E\u0432\u0435\u0434\u0435\u043D\u0438\u044E: \u043A\u043B\u0438\u043A\u0438, \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u044B, \u043E\u0442\u043A\u0430\u0437\u044B. \u041F\u043B\u044E\u0441 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u2014 \u043E\u0447\u0435\u043D\u044C \u0443\u0434\u043E\u0431\u043D\u043E."
      },
      {
        projectTitle: "\u041C\u0435\u0434\u0438\u0430 \u0438 \u0444\u0438\u043D\u0430\u043D\u0441\u044B",
        description: "agency",
        date: "08.01.2026",
        text: "\u041E\u0442\u0447\u0451\u0442\u044B \u0438 \u043F\u043E\u043D\u044F\u0442\u043D\u0430\u044F \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0430 \u043F\u043E\u043C\u043E\u0433\u0430\u044E\u0442 \u0434\u0435\u0440\u0436\u0430\u0442\u044C \u0440\u0443\u043A\u0443 \u043D\u0430 \u043F\u0443\u043B\u044C\u0441\u0435. Telegram-\u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u2014 \u0442\u043E\u043F."
      }
    ]
  },
  faq: {
    title: "FAQ",
    introTitle: "\u041A\u0430\u043A TrackNode \u043F\u043E\u043C\u043E\u0433\u0430\u0435\u0442 \u0440\u0430\u0441\u0442\u0438 \u0431\u0435\u0437 \u043F\u043E\u0442\u0435\u0440\u0438 \u0437\u0430\u044F\u0432\u043E\u043A",
    introParagraphs: [
      "TrackNode \u043E\u0431\u044A\u0435\u0434\u0438\u043D\u044F\u0435\u0442 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0443 \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u0439, \u043A\u043E\u043D\u0442\u0440\u043E\u043B\u044C \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u043E\u0432 \u0442\u0440\u0430\u0444\u0438\u043A\u0430 \u0438 \u043C\u0433\u043D\u043E\u0432\u0435\u043D\u043D\u044B\u0435 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u043E \u0437\u0430\u044F\u0432\u043A\u0430\u0445 \u0432 Telegram. \u041A\u043E\u043C\u0430\u043D\u0434\u0430 \u0432\u0438\u0434\u0438\u0442, \u043E\u0442\u043A\u0443\u0434\u0430 \u043F\u0440\u0438\u0448\u0451\u043B \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C, \u043A\u0430\u043A \u043E\u043D \u0432\u0451\u043B \u0441\u0435\u0431\u044F \u043D\u0430 \u0441\u0430\u0439\u0442\u0435 \u0438 \u0432 \u043A\u0430\u043A\u043E\u0439 \u043C\u043E\u043C\u0435\u043D\u0442 \u043E\u0441\u0442\u0430\u0432\u0438\u043B \u0437\u0430\u044F\u0432\u043A\u0443.",
      "\u0421\u0435\u0440\u0432\u0438\u0441 \u043F\u043E\u043C\u043E\u0433\u0430\u0435\u0442 \u0431\u044B\u0441\u0442\u0440\u043E \u043D\u0430\u0445\u043E\u0434\u0438\u0442\u044C \u0443\u0437\u043A\u0438\u0435 \u043C\u0435\u0441\u0442\u0430 \u0432 \u0432\u043E\u0440\u043E\u043D\u043A\u0435, \u043F\u0440\u043E\u0432\u0435\u0440\u044F\u0442\u044C \u043A\u0430\u0447\u0435\u0441\u0442\u0432\u043E \u0442\u0440\u0430\u0444\u0438\u043A\u0430, \u0443\u043B\u0443\u0447\u0448\u0430\u0442\u044C \u043A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u044E \u0438 \u0434\u0435\u0440\u0436\u0430\u0442\u044C \u043F\u043E\u0434 \u043A\u043E\u043D\u0442\u0440\u043E\u043B\u0435\u043C SEO \u0438 \u0442\u0435\u0445\u043D\u0438\u0447\u0435\u0441\u043A\u043E\u0435 \u0441\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u0441\u0430\u0439\u0442\u0430 \u0431\u0435\u0437 \u043B\u0438\u0448\u043D\u0438\u0445 \u0441\u043B\u043E\u0436\u043D\u043E\u0441\u0442\u0435\u0439 \u0432 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0435."
    ],
    items: [
      {
        question: "\u041A\u0430\u043A TrackNode \u043F\u043E\u043C\u043E\u0433\u0430\u0435\u0442 \u043D\u0435 \u0442\u0435\u0440\u044F\u0442\u044C \u0437\u0430\u044F\u0432\u043A\u0438?",
        answer: "\u041D\u043E\u0432\u044B\u0435 \u0437\u0430\u044F\u0432\u043A\u0438 \u0438 \u043B\u0438\u0434\u044B \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u044E\u0442\u0441\u044F \u0432 Telegram \u0441\u0440\u0430\u0437\u0443 \u043F\u043E\u0441\u043B\u0435 \u0441\u043E\u0431\u044B\u0442\u0438\u044F, \u043F\u043E\u044D\u0442\u043E\u043C\u0443 \u043C\u0435\u043D\u0435\u0434\u0436\u0435\u0440\u044B \u0440\u0435\u0430\u0433\u0438\u0440\u0443\u044E\u0442 \u0431\u044B\u0441\u0442\u0440\u0435\u0435 \u0438 \u043D\u0435 \u043F\u0440\u043E\u043F\u0443\u0441\u043A\u0430\u044E\u0442 \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044F \u0434\u0430\u0436\u0435 \u0432 \u043F\u0438\u043A\u043E\u0432\u044B\u0435 \u043F\u0435\u0440\u0438\u043E\u0434\u044B."
      },
      {
        question: "\u0427\u0442\u043E \u0438\u043C\u0435\u043D\u043D\u043E \u043E\u0442\u043F\u0440\u0430\u0432\u043B\u044F\u0435\u0442\u0441\u044F \u0432 Telegram?",
        answer: "\u0412 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F\u0445 \u043C\u043E\u0436\u043D\u043E \u043F\u043E\u043B\u0443\u0447\u0430\u0442\u044C \u043A\u043B\u044E\u0447\u0435\u0432\u0443\u044E \u0438\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u044E \u043F\u043E \u043E\u0431\u0440\u0430\u0449\u0435\u043D\u0438\u044E: \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A \u0442\u0440\u0430\u0444\u0438\u043A\u0430, \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u0443, \u0442\u0438\u043F \u0437\u0430\u044F\u0432\u043A\u0438 \u0438 \u0432\u0440\u0435\u043C\u044F \u0441\u043E\u0431\u044B\u0442\u0438\u044F, \u0447\u0442\u043E\u0431\u044B \u0441\u0440\u0430\u0437\u0443 \u0432\u0438\u0434\u0435\u0442\u044C \u043A\u043E\u043D\u0442\u0435\u043A\u0441\u0442 \u043B\u0438\u0434\u0430."
      },
      {
        question: "\u0421\u043A\u043E\u043B\u044C\u043A\u043E \u0432\u0440\u0435\u043C\u0435\u043D\u0438 \u0437\u0430\u043D\u0438\u043C\u0430\u0435\u0442 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435?",
        answer: "\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u0435 \u0437\u0430\u043D\u0438\u043C\u0430\u0435\u0442 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u043E \u043C\u0438\u043D\u0443\u0442: \u0434\u043E\u0431\u0430\u0432\u043B\u044F\u0435\u0442\u0435 \u0441\u0430\u0439\u0442, \u0443\u0441\u0442\u0430\u043D\u0430\u0432\u043B\u0438\u0432\u0430\u0435\u0442\u0435 \u043A\u043E\u0434 \u043E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u043D\u0438\u044F \u0438\u043B\u0438 \u0438\u043D\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u044E, \u043F\u043E\u0441\u043B\u0435 \u0447\u0435\u0433\u043E \u0434\u0430\u043D\u043D\u044B\u0435 \u043D\u0430\u0447\u0438\u043D\u0430\u044E\u0442 \u043F\u043E\u0441\u0442\u0443\u043F\u0430\u0442\u044C \u0432 \u0438\u043D\u0442\u0435\u0440\u0444\u0435\u0439\u0441."
      },
      {
        question: "\u041C\u043E\u0436\u043D\u043E \u043B\u0438 \u043E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u0442\u044C \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0438 \u0442\u0440\u0430\u0444\u0438\u043A\u0430?",
        answer: "\u0414\u0430, \u0441\u0435\u0440\u0432\u0438\u0441 \u043F\u043E\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u0442 \u043A\u0430\u043D\u0430\u043B\u044B \u0438 \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0438 \u0442\u0440\u0430\u0444\u0438\u043A\u0430, \u043F\u043E\u0432\u0435\u0434\u0435\u043D\u0438\u0435 \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0435\u0439 \u043F\u043E \u0441\u0442\u0440\u0430\u043D\u0438\u0446\u0430\u043C \u0438 \u043A\u043B\u044E\u0447\u0435\u0432\u044B\u0435 \u043F\u043E\u043A\u0430\u0437\u0430\u0442\u0435\u043B\u0438 \u0432\u043E\u0432\u043B\u0435\u0447\u0451\u043D\u043D\u043E\u0441\u0442\u0438 \u0434\u043B\u044F \u043E\u0446\u0435\u043D\u043A\u0438 \u044D\u0444\u0444\u0435\u043A\u0442\u0438\u0432\u043D\u043E\u0441\u0442\u0438 \u0440\u0435\u043A\u043B\u0430\u043C\u044B \u0438 \u043A\u043E\u043D\u0442\u0435\u043D\u0442\u0430."
      },
      {
        question: "\u0415\u0441\u0442\u044C \u043B\u0438 \u043E\u0442\u0447\u0435\u0442\u044B \u0432 PDF \u0438 \u0447\u0442\u043E \u0432 \u043D\u0438\u0445?",
        answer: "TrackNode \u0444\u043E\u0440\u043C\u0438\u0440\u0443\u0435\u0442 \u043E\u0442\u0447\u0451\u0442\u044B \u0438 \u043F\u043E\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442 \u044D\u043A\u0441\u043F\u043E\u0440\u0442. \u0412 \u043E\u0442\u0447\u0451\u0442\u0430\u0445 \u0434\u043E\u0441\u0442\u0443\u043F\u043D\u044B \u043E\u0441\u043D\u043E\u0432\u043D\u044B\u0435 \u043C\u0435\u0442\u0440\u0438\u043A\u0438 \u043F\u043E \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u044F\u043C, \u0437\u0430\u044F\u0432\u043A\u0430\u043C, \u043A\u0430\u043D\u0430\u043B\u0430\u043C \u0442\u0440\u0430\u0444\u0438\u043A\u0430 \u0438 \u0434\u0438\u043D\u0430\u043C\u0438\u043A\u0435 \u043A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u0438."
      },
      {
        question: "\u0427\u0435\u043C TrackNode \u043E\u0442\u043B\u0438\u0447\u0430\u0435\u0442\u0441\u044F \u043E\u0442 \u043E\u0431\u044B\u0447\u043D\u044B\u0445 \u0441\u0447\u0435\u0442\u0447\u0438\u043A\u043E\u0432?",
        answer: "\u041F\u043E\u043C\u0438\u043C\u043E \u0431\u0430\u0437\u043E\u0432\u043E\u0439 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043A\u0438, \u0441\u0435\u0440\u0432\u0438\u0441 \u043E\u0431\u044A\u0435\u0434\u0438\u043D\u044F\u0435\u0442 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0443, \u043A\u043E\u043D\u0442\u0440\u043E\u043B\u044C \u0432\u043E\u0440\u043E\u043D\u043A\u0438, \u043F\u043E\u0432\u0435\u0434\u0435\u043D\u0438\u0435 \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0435\u0439, SEO-\u043F\u0440\u043E\u0432\u0435\u0440\u043A\u0438 \u0438 \u043E\u043F\u0435\u0440\u0430\u0442\u0438\u0432\u043D\u044B\u0435 Telegram-\u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u0432 \u043E\u0434\u043D\u043E\u043C \u0440\u0430\u0431\u043E\u0447\u0435\u043C \u043A\u043E\u043D\u0442\u0443\u0440\u0435."
      },
      {
        question: "\u041F\u043E\u043C\u043E\u0433\u0430\u0435\u0442 \u043B\u0438 \u0441\u0435\u0440\u0432\u0438\u0441 \u0443\u043B\u0443\u0447\u0448\u0438\u0442\u044C \u043A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u044E \u0441\u0430\u0439\u0442\u0430?",
        answer: "\u0414\u0430, TrackNode \u043F\u043E\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u0442, \u043D\u0430 \u043A\u0430\u043A\u0438\u0445 \u044D\u0442\u0430\u043F\u0430\u0445 \u0442\u0435\u0440\u044F\u044E\u0442\u0441\u044F \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u0438, \u0438 \u043F\u043E\u0437\u0432\u043E\u043B\u044F\u0435\u0442 \u0431\u044B\u0441\u0442\u0440\u043E \u043F\u0440\u0438\u043D\u0438\u043C\u0430\u0442\u044C \u0440\u0435\u0448\u0435\u043D\u0438\u044F \u043F\u043E \u0443\u043B\u0443\u0447\u0448\u0435\u043D\u0438\u044E \u0441\u0442\u0440\u0430\u043D\u0438\u0446, \u0444\u043E\u0440\u043C \u0438 \u0441\u0446\u0435\u043D\u0430\u0440\u0438\u0435\u0432 \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u043A\u0438 \u0437\u0430\u044F\u0432\u043E\u043A."
      },
      {
        question: "\u041F\u043E\u0434\u0445\u043E\u0434\u0438\u0442 \u043B\u0438 TrackNode \u0434\u043B\u044F \u0430\u0433\u0435\u043D\u0442\u0441\u0442\u0432 \u0438 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u0438\u0445 \u0441\u0430\u0439\u0442\u043E\u0432?",
        answer: "\u0421\u0435\u0440\u0432\u0438\u0441 \u043F\u043E\u0434\u0445\u043E\u0434\u0438\u0442 \u0434\u043B\u044F \u0430\u0433\u0435\u043D\u0442\u0441\u0442\u0432 \u0438 \u043A\u043E\u043C\u0430\u043D\u0434 \u0441 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u0438\u043C\u0438 \u043F\u0440\u043E\u0435\u043A\u0442\u0430\u043C\u0438: \u043C\u043E\u0436\u043D\u043E \u0446\u0435\u043D\u0442\u0440\u0430\u043B\u0438\u0437\u043E\u0432\u0430\u043D\u043D\u043E \u043E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u0442\u044C \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0443 \u0438 \u0437\u0430\u044F\u0432\u043A\u0438 \u043F\u043E \u0440\u0430\u0437\u043D\u044B\u043C \u0441\u0430\u0439\u0442\u0430\u043C \u0438 \u0441\u0440\u0430\u0432\u043D\u0438\u0432\u0430\u0442\u044C \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u044B."
      }
    ]
  }
};
const _sfc_main$6 = {
  __name: "CapabilitiesSection",
  __ssrInlineRender: true,
  setup(__props) {
    const capabilities = siteData.capabilities;
    const iconMap = {
      telegram: () => h(
        "svg",
        {
          viewBox: "0 0 24 24",
          fill: "none",
          xmlns: "http://www.w3.org/2000/svg"
        },
        [
          h("path", {
            d: "M21 4.65L17.93 19.11C17.73 20.06 17.2 20.28 16.38 19.82L11.92 16.53L9.76 18.61C9.53 18.85 9.35 19.03 8.9 19.03L9.22 14.5L17.47 7.04C17.83 6.72 17.39 6.54 16.92 6.86L6.72 13.3L2.32 11.93C1.36 11.62 1.34 10.96 2.52 10.5L19.55 3.93C20.34 3.63 21.03 4.12 21 4.65Z",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linejoin": "round"
          })
        ]
      ),
      analytics: () => h(
        "svg",
        {
          viewBox: "0 0 24 24",
          fill: "none",
          xmlns: "http://www.w3.org/2000/svg"
        },
        [
          h("path", {
            d: "M3 17.5H21",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round"
          }),
          h("path", {
            d: "M5 14.8L9 11.2L12.2 13.8L16 8.9L19 10.7",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round",
            "stroke-linejoin": "round"
          }),
          h("path", {
            d: "M5.2 20.5V16.6M9 20.5V14.2M12.9 20.5V15.9M16.8 20.5V12.7",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round"
          })
        ]
      ),
      cursor: () => h(
        "svg",
        {
          viewBox: "0 0 24 24",
          fill: "none",
          xmlns: "http://www.w3.org/2000/svg"
        },
        [
          h("path", {
            d: "M4.5 3.8L17.4 10.2L11.6 12.1L9.7 17.9L4.5 3.8Z",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linejoin": "round"
          }),
          h("path", {
            d: "M15.9 4.4L16.9 2.8M19.6 8.1L21.2 7.1M16.2 8L18 8.2",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round"
          })
        ]
      ),
      funnel: () => h(
        "svg",
        {
          viewBox: "0 0 24 24",
          fill: "none",
          xmlns: "http://www.w3.org/2000/svg"
        },
        [
          h("path", {
            d: "M4 5.4H20L15.4 10.6H8.6L4 5.4Z",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linejoin": "round"
          }),
          h("path", {
            d: "M8.6 10.6H15.4L13.4 14.7H10.6L8.6 10.6Z",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linejoin": "round"
          }),
          h("path", {
            d: "M10.6 14.7H13.4L12.6 18.6H11.4L10.6 14.7Z",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linejoin": "round"
          })
        ]
      ),
      seo: () => h(
        "svg",
        {
          viewBox: "0 0 24 24",
          fill: "none",
          xmlns: "http://www.w3.org/2000/svg"
        },
        [
          h("path", {
            d: "M10.8 17.6C14.3346 17.6 17.2 14.7346 17.2 11.2C17.2 7.66538 14.3346 4.8 10.8 4.8C7.26538 4.8 4.4 7.66538 4.4 11.2C4.4 14.7346 7.26538 17.6 10.8 17.6Z",
            stroke: "currentColor",
            "stroke-width": "1.6"
          }),
          h("path", {
            d: "M15.5 15.8L20 20.2",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round"
          }),
          h("path", {
            d: "M8.1 11.6L10.1 13.6L13.8 9.7",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round",
            "stroke-linejoin": "round"
          })
        ]
      ),
      report: () => h(
        "svg",
        {
          viewBox: "0 0 24 24",
          fill: "none",
          xmlns: "http://www.w3.org/2000/svg"
        },
        [
          h("path", {
            d: "M7.2 3.8H14.5L18.8 8.1V18.9C18.8 19.8 18.1 20.5 17.2 20.5H7.2C6.3 20.5 5.6 19.8 5.6 18.9V5.4C5.6 4.5 6.3 3.8 7.2 3.8Z",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linejoin": "round"
          }),
          h("path", {
            d: "M14.5 3.8V8.1H18.8",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linejoin": "round"
          }),
          h("path", {
            d: "M9 11.2H14.6M9 14.1H14.6",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round"
          }),
          h("path", {
            d: "M16.9 16.5V12.8M16.9 16.5L15.3 14.9M16.9 16.5L18.5 14.9",
            stroke: "currentColor",
            "stroke-width": "1.6",
            "stroke-linecap": "round",
            "stroke-linejoin": "round"
          })
        ]
      )
    };
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<section${ssrRenderAttrs(mergeProps({
        id: "capabilities",
        class: "relative overflow-hidden py-16 scroll-mt-28 sm:py-20 lg:py-24 lg:scroll-mt-32"
      }, _attrs))}><div id="features" class="pointer-events-none absolute top-0 h-0 w-0" aria-hidden="true"></div><div class="pointer-events-none absolute inset-0 bg-gradient-to-b from-[#f8fafe] via-[#edf3fd] to-[#e9eef9]"></div><div class="pointer-events-none absolute -left-28 top-6 h-72 w-72 rounded-full bg-[radial-gradient(circle,rgba(154,198,255,0.38)_0%,rgba(154,198,255,0)_68%)] blur-3xl"></div><div class="pointer-events-none absolute right-[-96px] top-10 h-80 w-80 rounded-full bg-[radial-gradient(circle,rgba(185,213,255,0.44)_0%,rgba(185,213,255,0)_70%)] blur-3xl"></div><div class="pointer-events-none absolute bottom-[-130px] left-1/2 h-80 w-[620px] -translate-x-1/2 rounded-full bg-[radial-gradient(ellipse,rgba(206,224,255,0.34)_0%,rgba(206,224,255,0)_72%)] blur-3xl"></div><div class="relative mx-auto w-full max-w-[1260px] px-4 sm:px-6 lg:px-8"><header class="mx-auto max-w-[800px] text-center"><h2 class="text-[34px] font-semibold leading-tight tracking-[-0.02em] text-slate-900 sm:text-[40px] lg:text-[44px]">${ssrInterpolate(unref(capabilities).title)}</h2><p class="mx-auto mt-4 max-w-[760px] text-[20px] leading-[1.45] text-slate-600 sm:text-[22px] lg:text-[35px]">${ssrInterpolate(unref(capabilities).subtitle)}</p></header><div class="mt-9 grid grid-cols-1 gap-5 sm:mt-10 md:grid-cols-2 lg:mt-12 lg:grid-cols-3 lg:gap-6"><!--[-->`);
      ssrRenderList(unref(capabilities).items, (item) => {
        _push(`<article class="flex h-full flex-col rounded-[20px] border border-white/55 bg-white/55 p-5 shadow-[0_16px_38px_rgba(35,55,92,0.12)] backdrop-blur-md transition-transform duration-300 hover:-translate-y-0.5"><div class="inline-flex h-12 w-12 items-center justify-center rounded-xl border border-[#d2def2] bg-gradient-to-b from-white/90 to-[#ecf3ff] text-[#4c86d8] shadow-[0_6px_16px_rgba(63,118,201,0.14)]">`);
        ssrRenderVNode(_push, createVNode(resolveDynamicComponent(iconMap[item.icon]), {
          class: "h-6 w-6",
          "aria-hidden": "true"
        }, null), _parent);
        _push(`</div><h3 class="mt-5 text-[28px] font-semibold leading-[1.28] tracking-[-0.01em] text-slate-900">${ssrInterpolate(item.title)}</h3><p class="mt-3 text-[14px] leading-[1.55] text-slate-600 sm:text-[15px]">${ssrInterpolate(item.description)}</p></article>`);
      });
      _push(`<!--]--></div></div></section>`);
    };
  }
};
const _sfc_setup$6 = _sfc_main$6.setup;
_sfc_main$6.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/sections/CapabilitiesSection.vue");
  return _sfc_setup$6 ? _sfc_setup$6(props, ctx) : void 0;
};
const _imports_0 = publicAssetsURL("/Hero/hero.gif");
const _sfc_main$5 = {
  __name: "HowItWorksSection",
  __ssrInlineRender: true,
  setup(__props) {
    const steps = [
      {
        id: "step-1",
        number: "1",
        title: "\u0414\u043E\u0431\u0430\u0432\u043B\u044F\u0435\u0442\u0435 \u0441\u0430\u0439\u0442",
        description: "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0430\u0434\u0440\u0435\u0441 \u0441\u0430\u0439\u0442\u0430 \u0438 \u0441\u043E\u0437\u0434\u0430\u0439\u0442\u0435 \u043F\u0440\u043E\u0435\u043A\u0442 \u0432 TrackNode.",
        image: "/how/step-1.png",
        alt: "\u0414\u043E\u0431\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u0441\u0430\u0439\u0442\u0430"
      },
      {
        id: "step-2",
        number: "2",
        title: "\u0423\u0441\u0442\u0430\u043D\u0430\u0432\u043B\u0438\u0432\u0430\u0435\u0442\u0435 \u043A\u043E\u0434",
        description: "\u0423\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u0435 \u043B\u0438\u043D\u0435\u0439\u043D\u044B\u0439 \u043A\u043E\u0434 \u043E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u043D\u0438\u044F \u0438\u043B\u0438 \u0438\u043D\u0442\u0435\u0433\u0440\u0430\u0446\u0438\u044E.",
        image: "/how/step-2.png",
        alt: "\u0423\u0441\u0442\u0430\u043D\u043E\u0432\u043A\u0430 \u043A\u043E\u0434\u0430 \u043E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u043D\u0438\u044F"
      },
      {
        id: "step-3",
        number: "3",
        title: "\u0421\u043C\u043E\u0442\u0440\u0438\u0442\u0435 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0443",
        description: "\u041E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u0439\u0442\u0435 \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u044F \u0438 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F \u043E \u0437\u0430\u044F\u0432\u043A\u0430\u0445.",
        image: "/how/step-3.png",
        alt: "\u041F\u0440\u043E\u0441\u043C\u043E\u0442\u0440 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0438"
      }
    ];
    const modalData = {
      "step-1": {
        type: "steps",
        title: "\u0414\u043E\u0431\u0430\u0432\u043B\u044F\u0435\u0442\u0435 \u0441\u0430\u0439\u0442",
        steps: [
          "\u041E\u0442\u043A\u0440\u043E\u0439\u0442\u0435 TrackNode \u0438 \u043D\u0430\u0436\u043C\u0438\u0442\u0435 \xAB\u0421\u043E\u0437\u0434\u0430\u0442\u044C \u043F\u0440\u043E\u0435\u043A\u0442\xBB.",
          "\u0423\u043A\u0430\u0436\u0438\u0442\u0435 \u0434\u043E\u043C\u0435\u043D \u0441\u0430\u0439\u0442\u0430 \u0438 \u0440\u0430\u0431\u043E\u0447\u0438\u0439 \u0447\u0430\u0441\u043E\u0432\u043E\u0439 \u043F\u043E\u044F\u0441.",
          "\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 Telegram-\u043A\u0430\u043D\u0430\u043B \u0434\u043B\u044F \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u0439 \u043E \u0437\u0430\u044F\u0432\u043A\u0430\u0445.",
          "\u041F\u0440\u043E\u0432\u0435\u0440\u044C\u0442\u0435 \u043F\u0430\u0440\u0430\u043C\u0435\u0442\u0440\u044B \u043F\u0440\u043E\u0435\u043A\u0442\u0430 \u0438 \u0441\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u0435 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438."
        ]
      },
      "step-2": {
        type: "steps",
        title: "\u0423\u0441\u0442\u0430\u043D\u0430\u0432\u043B\u0438\u0432\u0430\u0435\u0442\u0435 \u043A\u043E\u0434",
        steps: [
          "\u0421\u043A\u043E\u043F\u0438\u0440\u0443\u0439\u0442\u0435 \u0442\u0440\u0435\u043A\u0438\u043D\u0433-\u043A\u043E\u0434 \u0438\u0437 \u043A\u0430\u0440\u0442\u043E\u0447\u043A\u0438 \u043F\u0440\u043E\u0435\u043A\u0442\u0430.",
          "\u0414\u043E\u0431\u0430\u0432\u044C\u0442\u0435 \u043A\u043E\u0434 \u043F\u0435\u0440\u0435\u0434 \u0437\u0430\u043A\u0440\u044B\u0432\u0430\u044E\u0449\u0438\u043C \u0442\u0435\u0433\u043E\u043C </head> \u043D\u0430 \u0441\u0430\u0439\u0442\u0435.",
          "\u0415\u0441\u043B\u0438 \u0438\u0441\u043F\u043E\u043B\u044C\u0437\u0443\u0435\u0442\u0435 CMS, \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u0435 \u043A\u043E\u0434 \u0447\u0435\u0440\u0435\u0437 \u0448\u0430\u0431\u043B\u043E\u043D \u0438\u043B\u0438 \u043C\u043E\u0434\u0443\u043B\u044C.",
          "\u041E\u043F\u0443\u0431\u043B\u0438\u043A\u0443\u0439\u0442\u0435 \u0438\u0437\u043C\u0435\u043D\u0435\u043D\u0438\u044F \u0438 \u0432\u044B\u043F\u043E\u043B\u043D\u0438\u0442\u0435 \u0442\u0435\u0441\u0442\u043E\u0432\u044B\u0439 \u0432\u0438\u0437\u0438\u0442.",
          "\u0423\u0431\u0435\u0434\u0438\u0442\u0435\u0441\u044C, \u0447\u0442\u043E \u0434\u0430\u043D\u043D\u044B\u0435 \u043D\u0430\u0447\u0430\u043B\u0438 \u043F\u043E\u0441\u0442\u0443\u043F\u0430\u0442\u044C \u0432 \u0434\u0430\u0448\u0431\u043E\u0440\u0434."
        ]
      },
      "step-3": {
        type: "example",
        title: "\u041F\u0440\u0438\u043C\u0435\u0440"
      }
    };
    const activeModal = ref("");
    const currentModal = computed(() => activeModal.value ? modalData[activeModal.value] : null);
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<section${ssrRenderAttrs(mergeProps({
        id: "how",
        class: "how-section"
      }, _attrs))} data-v-a60d7549><div class="how-bg how-bg--left" aria-hidden="true" data-v-a60d7549></div><div class="how-bg how-bg--right" aria-hidden="true" data-v-a60d7549></div><div class="how-bg how-bg--top" aria-hidden="true" data-v-a60d7549></div><div class="how-wave how-wave--one" aria-hidden="true" data-v-a60d7549></div><div class="how-wave how-wave--two" aria-hidden="true" data-v-a60d7549></div><div class="how-content" data-v-a60d7549><header class="how-header" data-v-a60d7549><h2 class="how-title" data-v-a60d7549>\u041A\u0430\u043A \u044D\u0442\u043E \u0440\u0430\u0431\u043E\u0442\u0430\u0435\u0442</h2><p class="how-subtitle" data-v-a60d7549> \u0412\u043D\u0435\u0441\u0438\u0442\u0435 \u0441\u0430\u0439\u0442 \u0432 \u0434\u0432\u0430 \u043F\u0440\u043E\u0441\u0442\u044B\u0445 \u0448\u0430\u0433\u0430 \u0438 \u043F\u043E\u043B\u0443\u0447\u0438\u0442\u0435 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0443 \u0438 \u0443\u0432\u0435\u0434\u043E\u043C\u043B\u0435\u043D\u0438\u044F. </p></header><div class="how-grid" data-v-a60d7549><!--[-->`);
      ssrRenderList(steps, (step) => {
        _push(`<article class="how-card how-card--interactive" role="button" tabindex="0"${ssrRenderAttr("aria-label", `\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0438\u043D\u0441\u0442\u0440\u0443\u043A\u0446\u0438\u044E: ${step.title}`)} data-v-a60d7549><span class="how-badge" data-v-a60d7549>${ssrInterpolate(step.number)}</span><div class="how-media" data-v-a60d7549><img${ssrRenderAttr("src", step.image)}${ssrRenderAttr("alt", step.alt)} loading="lazy" decoding="async" data-v-a60d7549></div><h3 class="how-card-title" data-v-a60d7549>${ssrInterpolate(step.title)}</h3><p class="how-card-description" data-v-a60d7549>${ssrInterpolate(step.description)}</p></article>`);
      });
      _push(`<!--]--></div></div>`);
      ssrRenderTeleport(_push, (_push2) => {
        if (activeModal.value && currentModal.value) {
          _push2(`<div class="how-modal-overlay" data-v-a60d7549><article class="how-modal" role="dialog" aria-modal="true"${ssrRenderAttr("aria-labelledby", `how-modal-title-${activeModal.value}`)} data-v-a60d7549><button type="button" class="how-modal-close" aria-label="\u0417\u0430\u043A\u0440\u044B\u0442\u044C" data-v-a60d7549><svg viewBox="0 0 20 20" fill="none" aria-hidden="true" data-v-a60d7549><path d="M5 5L15 15M15 5L5 15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" data-v-a60d7549></path></svg></button><h3${ssrRenderAttr("id", `how-modal-title-${activeModal.value}`)} class="how-modal-title" data-v-a60d7549>${ssrInterpolate(currentModal.value.title)}</h3>`);
          if (currentModal.value.type === "example") {
            _push2(`<!--[--><img${ssrRenderAttr("src", _imports_0)} alt="\u041F\u0440\u0438\u043C\u0435\u0440 \u0430\u043D\u0430\u043B\u0438\u0442\u0438\u043A\u0438 TrackNode" class="how-modal-gif" data-v-a60d7549><p class="how-modal-text" data-v-a60d7549> TrackNode \u043F\u043E\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u0442 \u043A\u043B\u044E\u0447\u0435\u0432\u044B\u0435 \u043C\u0435\u0442\u0440\u0438\u043A\u0438 \u0432 \u043E\u0434\u043D\u043E\u043C \u0438\u043D\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u0435: \u043F\u043E\u0441\u0435\u0449\u0435\u043D\u0438\u044F, \u0438\u0441\u0442\u043E\u0447\u043D\u0438\u043A\u0438, \u0441\u043E\u0431\u044B\u0442\u0438\u044F \u0438 \u0437\u0430\u044F\u0432\u043A\u0438. \u041A\u043E\u043C\u0430\u043D\u0434\u0430 \u0441\u0440\u0430\u0437\u0443 \u0432\u0438\u0434\u0438\u0442, \u0433\u0434\u0435 \u0440\u0430\u0441\u0442\u0451\u0442 \u043A\u043E\u043D\u0432\u0435\u0440\u0441\u0438\u044F, \u0430 \u0433\u0434\u0435 \u043D\u0443\u0436\u043D\u044B \u0434\u043E\u0440\u0430\u0431\u043E\u0442\u043A\u0438, \u0438 \u0431\u044B\u0441\u0442\u0440\u0435\u0435 \u043F\u0440\u0438\u043D\u0438\u043C\u0430\u0435\u0442 \u0440\u0435\u0448\u0435\u043D\u0438\u044F. </p><!--]-->`);
          } else {
            _push2(`<ol class="how-modal-steps" data-v-a60d7549><!--[-->`);
            ssrRenderList(currentModal.value.steps, (item) => {
              _push2(`<li data-v-a60d7549>${ssrInterpolate(item)}</li>`);
            });
            _push2(`<!--]--></ol>`);
          }
          _push2(`</article></div>`);
        } else {
          _push2(`<!---->`);
        }
      }, "body", false, _parent);
      _push(`</section>`);
    };
  }
};
const _sfc_setup$5 = _sfc_main$5.setup;
_sfc_main$5.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/HowItWorksSection.vue");
  return _sfc_setup$5 ? _sfc_setup$5(props, ctx) : void 0;
};
const HowItWorksSection = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["__scopeId", "data-v-a60d7549"]]);
const _sfc_main$4 = {
  __name: "PricingSection",
  __ssrInlineRender: true,
  setup(__props) {
    const pricing = siteData.pricing;
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<section${ssrRenderAttrs(mergeProps({
        id: "pricing",
        class: "pricing-section"
      }, _attrs))} data-v-c5132970><div class="pricing-glow pricing-glow--left" aria-hidden="true" data-v-c5132970></div><div class="pricing-glow pricing-glow--right" aria-hidden="true" data-v-c5132970></div><div class="pricing-wave pricing-wave--one" aria-hidden="true" data-v-c5132970></div><div class="pricing-content" data-v-c5132970><header class="pricing-header" data-v-c5132970><h2 class="pricing-title" data-v-c5132970>${ssrInterpolate(unref(pricing).title)}</h2><p class="pricing-subtitle" data-v-c5132970>${ssrInterpolate(unref(pricing).subtitle)}</p></header><div class="pricing-grid" data-v-c5132970><!--[-->`);
      ssrRenderList(unref(pricing).plans, (plan) => {
        _push(`<article class="${ssrRenderClass([{ "pricing-card--featured": plan.featured }, "pricing-card"])}" data-v-c5132970>`);
        if (plan.featured) {
          _push(`<span class="pricing-badge" data-v-c5132970>\u0420\u0435\u043A\u043E\u043C\u0435\u043D\u0434\u0443\u0435\u043C</span>`);
        } else {
          _push(`<!---->`);
        }
        _push(`<h3 class="pricing-card-title" data-v-c5132970>${ssrInterpolate(plan.name)}</h3><p class="pricing-card-price" data-v-c5132970>${ssrInterpolate(plan.price)}</p><p class="pricing-card-description" data-v-c5132970>${ssrInterpolate(plan.description)}</p><ul class="pricing-features" data-v-c5132970><!--[-->`);
        ssrRenderList(plan.features, (feature) => {
          _push(`<li class="pricing-feature" data-v-c5132970><span class="pricing-feature-icon" aria-hidden="true" data-v-c5132970><svg viewBox="0 0 16 16" fill="none" data-v-c5132970><path d="M3.4 8.3L6.5 11.3L12.6 5.2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" data-v-c5132970></path></svg></span><span data-v-c5132970>${ssrInterpolate(feature)}</span></li>`);
        });
        _push(`<!--]--></ul><a href="https://t.me/M1ke994" target="_blank" rel="noopener" class="pricing-cta" data-v-c5132970>\u0421\u0432\u044F\u0437\u0430\u0442\u044C\u0441\u044F</a></article>`);
      });
      _push(`<!--]--></div></div></section>`);
    };
  }
};
const _sfc_setup$4 = _sfc_main$4.setup;
_sfc_main$4.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/PricingSection.vue");
  return _sfc_setup$4 ? _sfc_setup$4(props, ctx) : void 0;
};
const PricingSection = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-c5132970"]]);
const _sfc_main$3 = {
  __name: "ReviewsSection",
  __ssrInlineRender: true,
  setup(__props) {
    const reviews = siteData.reviews;
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<section${ssrRenderAttrs(mergeProps({
        id: "reviews",
        class: "reviews-section"
      }, _attrs))} data-v-f236a512><div class="reviews-glow reviews-glow--left" aria-hidden="true" data-v-f236a512></div><div class="reviews-glow reviews-glow--right" aria-hidden="true" data-v-f236a512></div><div class="reviews-wave reviews-wave--one" aria-hidden="true" data-v-f236a512></div><div class="reviews-content" data-v-f236a512><header class="reviews-header" data-v-f236a512><h2 class="reviews-title" data-v-f236a512>${ssrInterpolate(unref(reviews).title)}</h2><p class="reviews-subtitle" data-v-f236a512>${ssrInterpolate(unref(reviews).subtitle)}</p></header><div class="reviews-grid" data-v-f236a512><!--[-->`);
      ssrRenderList(unref(reviews).items, (review) => {
        _push(`<article class="review-card" data-v-f236a512><div class="review-stars" aria-label="\u0420\u0435\u0439\u0442\u0438\u043D\u0433 5 \u0438\u0437 5" data-v-f236a512><!--[-->`);
        ssrRenderList(5, (star) => {
          _push(`<svg viewBox="0 0 16 16" fill="none" aria-hidden="true" data-v-f236a512><path d="M8 1.3L9.73 4.84L13.6 5.4L10.8 8.12L11.46 12L8 10.18L4.54 12L5.2 8.12L2.4 5.4L6.27 4.84L8 1.3Z" fill="currentColor" data-v-f236a512></path></svg>`);
        });
        _push(`<!--]--></div><h3 class="review-project-title" data-v-f236a512>${ssrInterpolate(review.projectTitle)}</h3><p class="review-company" data-v-f236a512>${ssrInterpolate(review.company)}</p><p class="review-role" data-v-f236a512>${ssrInterpolate(review.description)}</p><p class="review-date" data-v-f236a512>\u0414\u0430\u0442\u0430: ${ssrInterpolate(review.date)}</p><p class="review-text" data-v-f236a512>${ssrInterpolate(review.text)}</p></article>`);
      });
      _push(`<!--]--></div></div></section>`);
    };
  }
};
const _sfc_setup$3 = _sfc_main$3.setup;
_sfc_main$3.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/ReviewsSection.vue");
  return _sfc_setup$3 ? _sfc_setup$3(props, ctx) : void 0;
};
const ReviewsSection = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-f236a512"]]);
const _sfc_main$2 = {
  __name: "FAQSection",
  __ssrInlineRender: true,
  setup(__props) {
    const faq = siteData.faq;
    const openIndex = ref(0);
    return (_ctx, _push, _parent, _attrs) => {
      _push(`<section${ssrRenderAttrs(mergeProps({
        id: "faq",
        class: "faq-section"
      }, _attrs))} data-v-2c6737c1><div class="faq-glow faq-glow--left" aria-hidden="true" data-v-2c6737c1></div><div class="faq-glow faq-glow--right" aria-hidden="true" data-v-2c6737c1></div><div class="faq-wave" aria-hidden="true" data-v-2c6737c1></div><div class="faq-content" data-v-2c6737c1><header class="faq-header" data-v-2c6737c1><h2 class="faq-title" data-v-2c6737c1>${ssrInterpolate(unref(faq).title)}</h2></header><article class="faq-intro" data-v-2c6737c1><h3 data-v-2c6737c1>${ssrInterpolate(unref(faq).introTitle)}</h3><!--[-->`);
      ssrRenderList(unref(faq).introParagraphs, (paragraph, idx) => {
        _push(`<p data-v-2c6737c1>${ssrInterpolate(paragraph)}</p>`);
      });
      _push(`<!--]--></article><h3 class="faq-list-title" data-v-2c6737c1>\u0427\u0430\u0441\u0442\u044B\u0435 \u0432\u043E\u043F\u0440\u043E\u0441\u044B \u043E \u0441\u0435\u0440\u0432\u0438\u0441\u0435</h3><div class="faq-list" role="list" data-v-2c6737c1><!--[-->`);
      ssrRenderList(unref(faq).items, (item, index) => {
        _push(`<article class="${ssrRenderClass([{ "faq-item--open": openIndex.value === index }, "faq-item"])}" role="listitem" data-v-2c6737c1><button type="button" class="faq-trigger"${ssrRenderAttr("aria-expanded", openIndex.value === index)}${ssrRenderAttr("aria-controls", `faq-panel-${index}`)} data-v-2c6737c1><span data-v-2c6737c1>${ssrInterpolate(item.question)}</span><span class="${ssrRenderClass([{ "faq-plus--open": openIndex.value === index }, "faq-plus"])}" aria-hidden="true" data-v-2c6737c1></span></button><div${ssrRenderAttr("id", `faq-panel-${index}`)} class="${ssrRenderClass([{ "faq-panel--open": openIndex.value === index }, "faq-panel"])}" data-v-2c6737c1><p data-v-2c6737c1>${ssrInterpolate(item.answer)}</p></div></article>`);
      });
      _push(`<!--]--></div></div></section>`);
    };
  }
};
const _sfc_setup$2 = _sfc_main$2.setup;
_sfc_main$2.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/FAQSection.vue");
  return _sfc_setup$2 ? _sfc_setup$2(props, ctx) : void 0;
};
const FAQSection = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-2c6737c1"]]);
const _sfc_main$1 = {};
function _sfc_ssrRender(_ctx, _push, _parent, _attrs) {
  _push(`<footer${ssrRenderAttrs(mergeProps({
    id: "footer",
    class: "site-footer"
  }, _attrs))} data-v-34babacb><div class="footer-glow footer-glow--left" aria-hidden="true" data-v-34babacb></div><div class="footer-glow footer-glow--right" aria-hidden="true" data-v-34babacb></div><div class="footer-content" data-v-34babacb><div id="contacts" class="footer-anchor" aria-hidden="true" data-v-34babacb></div><div id="footer-contacts" class="footer-anchor" aria-hidden="true" data-v-34babacb></div><div class="footer-top" data-v-34babacb><section class="footer-brand" data-v-34babacb><a href="/" class="footer-logo" data-v-34babacb><img${ssrRenderAttr("src", _imports_0$1)} alt="TrackNode" data-v-34babacb><span data-v-34babacb>TrackNode</span></a><p class="footer-copy" data-v-34babacb>\u0412\xA9 2026 TrackNode. \u0420\u2019\u0421\u0403\u0420\xB5 \u0420\u0457\u0421\u0402\u0420\xB0\u0420\u0406\u0420\xB0 \u0420\xB7\u0420\xB0\u0421\u2030\u0420\u0451\u0421\u2030\u0420\xB5\u0420\u0405\u0421\u2039.</p><p class="footer-legal" data-v-34babacb><a href="#" data-v-34babacb>\u0420\u045F\u0420\u0455\u0420\xBB\u0420\u0451\u0421\u201A\u0420\u0451\u0420\u0454\u0420\xB0 \u0420\u0454\u0420\u0455\u0420\u0405\u0421\u201E\u0420\u0451\u0420\u0491\u0420\xB5\u0420\u0405\u0421\u2020\u0420\u0451\u0420\xB0\u0420\xBB\u0421\u040A\u0420\u0405\u0420\u0455\u0421\u0403\u0421\u201A\u0420\u0451</a><span data-v-34babacb>|</span><a href="#" data-v-34babacb>\u0420\u0408\u0421\u0403\u0420\xBB\u0420\u0455\u0420\u0406\u0420\u0451\u0421\u040F \u0420\u0457\u0420\u0455\u0420\xBB\u0421\u040A\u0420\xB7\u0420\u0455\u0420\u0406\u0420\xB0\u0420\u0405\u0420\u0451\u0421\u040F</a></p></section><section class="footer-menus" aria-label="\u0420\u045C\u0420\xB0\u0420\u0406\u0420\u0451\u0420\u0456\u0420\xB0\u0421\u2020\u0420\u0451\u0421\u040F \u0421\u201E\u0421\u0453\u0421\u201A\u0420\xB5\u0421\u0402\u0420\xB0" data-v-34babacb><div class="footer-column" data-v-34babacb><h3 data-v-34babacb>\u0420\u045F\u0421\u0402\u0420\u0455\u0420\u0491\u0421\u0453\u0420\u0454\u0421\u201A</h3><ul data-v-34babacb><li data-v-34babacb><a href="#features" data-v-34babacb>\u0420\u2019\u0420\u0455\u0420\xB7\u0420\u0458\u0420\u0455\u0420\xB6\u0420\u0405\u0420\u0455\u0421\u0403\u0421\u201A\u0420\u0451</a></li><li data-v-34babacb><a href="#how" data-v-34babacb>\u0420\u0459\u0420\xB0\u0420\u0454 \u0421\u040C\u0421\u201A\u0420\u0455 \u0421\u0402\u0420\xB0\u0420\xB1\u0420\u0455\u0421\u201A\u0420\xB0\u0420\xB5\u0421\u201A</a></li><li data-v-34babacb><a href="#pricing" data-v-34babacb>\u0420\u045E\u0420\xB0\u0421\u0402\u0420\u0451\u0421\u201E\u0421\u2039</a></li><li data-v-34babacb><a href="/login" data-v-34babacb> \u0420\u045B\u0421\u201A\u0420\u0454\u0421\u0402\u0421\u2039\u0421\u201A\u0421\u040A \u0420\u0457\u0421\u0402\u0420\u0451\u0420\xBB\u0420\u0455\u0420\xB6\u0420\xB5\u0420\u0405\u0420\u0451\u0420\xB5 </a></li></ul></div><div class="footer-column" data-v-34babacb><h3 data-v-34babacb>\u0420\xA0\u0420\xB5\u0421\u0403\u0421\u0453\u0421\u0402\u0421\u0403\u0421\u2039</h3><ul data-v-34babacb><li data-v-34babacb><a href="#reviews" data-v-34babacb>\u0420\u045B\u0421\u201A\u0420\xB7\u0421\u2039\u0420\u0406\u0421\u2039</a></li><li data-v-34babacb><a href="#faq" data-v-34babacb>FAQ</a></li><li data-v-34babacb><a href="#footer-contacts" data-v-34babacb>\u0420\u045F\u0420\u0455\u0420\u0491\u0420\u0491\u0420\xB5\u0421\u0402\u0420\xB6\u0420\u0454\u0420\xB0</a></li><li data-v-34babacb><a href="#footer-contacts" data-v-34babacb>\u0420\u201D\u0420\u0455\u0420\u0454\u0421\u0453\u0420\u0458\u0420\xB5\u0420\u0405\u0421\u201A\u0420\xB0\u0421\u2020\u0420\u0451\u0421\u040F</a></li></ul></div><div class="footer-column" data-v-34babacb><h3 data-v-34babacb>\u0420\u0459\u0420\u0455\u0420\u0458\u0420\u0457\u0420\xB0\u0420\u0405\u0420\u0451\u0421\u040F</h3><ul data-v-34babacb><li data-v-34babacb><a href="#footer-contacts" data-v-34babacb>\u0420\u0459\u0420\u0455\u0420\u0405\u0421\u201A\u0420\xB0\u0420\u0454\u0421\u201A\u0421\u2039</a></li><li data-v-34babacb><a href="#footer-contacts" data-v-34babacb>\u0420\u045F\u0420\xB0\u0421\u0402\u0421\u201A\u0420\u0405\u0421\u2018\u0421\u0402\u0420\xB0\u0420\u0458</a></li><li data-v-34babacb><a href="#footer-contacts" data-v-34babacb>\u0420\u2019\u0420\xB0\u0420\u0454\u0420\xB0\u0420\u0405\u0421\u0403\u0420\u0451\u0420\u0451</a></li><li data-v-34babacb><a href="#footer-contacts" data-v-34babacb>\u0420\u045B \u0420\u0405\u0420\xB0\u0421\u0403</a></li></ul></div></section><section class="footer-contacts" aria-label="\u0420\u0459\u0420\u0455\u0420\u0405\u0421\u201A\u0420\xB0\u0420\u0454\u0421\u201A\u0421\u2039" data-v-34babacb><h3 data-v-34babacb>\u0420\u0459\u0420\u0455\u0420\u0405\u0421\u201A\u0420\xB0\u0420\u0454\u0421\u201A\u0421\u2039</h3><ul data-v-34babacb><li data-v-34babacb><span class="footer-contact-label" data-v-34babacb>Telegram</span><a href="https://t.me/M1ke994" target="_blank" rel="noopener" data-v-34babacb>@M1ke994</a></li><li data-v-34babacb><span class="footer-contact-label" data-v-34babacb>Email</span><a href="mailto:tishechkin1994@gmail.com" data-v-34babacb>tishechkin1994@gmail.com</a></li><li data-v-34babacb><span class="footer-contact-label" data-v-34babacb>\u0420\u045E\u0420\xB5\u0420\xBB\u0420\xB5\u0421\u201E\u0420\u0455\u0420\u0405</span><a href="tel:+79017800504" data-v-34babacb>+7-901-780-05-04</a></li><li data-v-34babacb><span class="footer-contact-label" data-v-34babacb>\u0420\u0452\u0420\u0491\u0421\u0402\u0420\xB5\u0421\u0403</span><span data-v-34babacb>\u0420\xA0\u0420\u0455\u0421\u0403\u0421\u0403\u0420\u0451\u0421\u040F, \u0420\u045A\u0420\u0455\u0421\u0403\u0420\u0454\u0420\u0406\u0420\xB0, \u0421\u0453\u0420\xBB. \u0420\u203A\u0420\xB5\u0420\u0405\u0420\u0451\u0420\u0405\u0420\u0456\u0421\u0402\u0420\xB0\u0420\u0491\u0421\u0403\u0420\u0454\u0420\xB0\u0421\u040F, 15</span></li></ul><div class="footer-socials" aria-label="\u0420\u040E\u0420\u0455\u0421\u2020\u0420\u0451\u0420\xB0\u0420\xBB\u0421\u040A\u0420\u0405\u0421\u2039\u0420\xB5 \u0421\u0403\u0420\xB5\u0421\u201A\u0420\u0451" data-v-34babacb><a href="https://t.me/M1ke994" target="_blank" rel="noopener" aria-label="Telegram" data-v-34babacb><svg viewBox="0 0 20 20" fill="none" data-v-34babacb><path d="M17.5 3.7L15.1 15.2C14.95 15.9 14.55 16.08 13.95 15.74L10.45 13.16L8.72 14.83C8.54 15.02 8.39 15.16 8.04 15.16L8.3 11.52L14.88 5.56C15.17 5.31 14.82 5.16 14.45 5.42L6.31 10.56L2.8 9.47C2.04 9.22 2.02 8.7 2.96 8.34L16.55 3.1C17.18 2.86 17.73 3.24 17.5 3.7Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" data-v-34babacb></path></svg></a><a href="https://example.com" target="_blank" rel="noopener" aria-label="VK" data-v-34babacb><svg viewBox="0 0 20 20" fill="none" data-v-34babacb><path d="M3.9 6.2H6.1C6.22 6.2 6.34 6.3 6.37 6.42C6.61 7.54 7.08 8.6 7.77 9.53C8.6 10.66 9.53 11.34 10.06 11.45C10.2 11.48 10.33 11.37 10.33 11.23V6.58C10.33 6.37 10.5 6.2 10.71 6.2H12.55C12.76 6.2 12.93 6.37 12.93 6.58V9.02C12.93 9.19 13.14 9.27 13.26 9.15C14.08 8.31 14.68 7.28 15 6.16C15.03 6.05 15.14 5.97 15.26 5.97H17.08C17.35 5.97 17.55 6.23 17.46 6.49C16.98 7.88 16.23 9.16 15.24 10.25C15.16 10.34 15.16 10.48 15.24 10.56C16.26 11.61 17.06 12.85 17.59 14.22C17.69 14.49 17.49 14.78 17.2 14.78H15.31C15.2 14.78 15.09 14.72 15.04 14.62C14.54 13.58 13.84 12.65 12.99 11.87C12.87 11.76 12.67 11.84 12.67 12V14.36C12.67 14.57 12.5 14.74 12.29 14.74H11.18C7.3 14.74 4.41 12.14 3.58 6.59C3.55 6.37 3.72 6.2 3.9 6.2Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" data-v-34babacb></path></svg></a><a href="https://example.com" target="_blank" rel="noopener" aria-label="YouTube" data-v-34babacb><svg viewBox="0 0 20 20" fill="none" data-v-34babacb><rect x="2.7" y="5.4" width="14.6" height="9.2" rx="2.5" stroke="currentColor" stroke-width="1.3" data-v-34babacb></rect><path d="M8.4 8.1L12.8 10L8.4 11.9V8.1Z" fill="currentColor" data-v-34babacb></path></svg></a></div></section></div><div class="footer-bottom" data-v-34babacb><p data-v-34babacb>\u0412\xA9 2026 TrackNode. \u0420\u2019\u0421\u0403\u0420\xB5 \u0420\u0457\u0421\u0402\u0420\xB0\u0420\u0406\u0420\xB0 \u0420\xB7\u0420\xB0\u0421\u2030\u0420\u0451\u0421\u2030\u0420\xB5\u0420\u0405\u0421\u2039.</p><p data-v-34babacb><a href="#" data-v-34babacb>\u0420\u045F\u0420\u0455\u0420\xBB\u0420\u0451\u0421\u201A\u0420\u0451\u0420\u0454\u0420\xB0 \u0420\u0454\u0420\u0455\u0420\u0405\u0421\u201E\u0420\u0451\u0420\u0491\u0420\xB5\u0420\u0405\u0421\u2020\u0420\u0451\u0420\xB0\u0420\xBB\u0421\u040A\u0420\u0405\u0420\u0455\u0421\u0403\u0421\u201A\u0420\u0451</a><span data-v-34babacb>|</span><a href="#" data-v-34babacb>\u0420\u0408\u0421\u0403\u0420\xBB\u0420\u0455\u0420\u0406\u0420\u0451\u0421\u040F \u0420\u0457\u0420\u0455\u0420\xBB\u0421\u040A\u0420\xB7\u0420\u0455\u0420\u0406\u0420\xB0\u0420\u0405\u0420\u0451\u0421\u040F</a></p></div></div></footer>`);
}
const _sfc_setup$1 = _sfc_main$1.setup;
_sfc_main$1.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("components/SiteFooter.vue");
  return _sfc_setup$1 ? _sfc_setup$1(props, ctx) : void 0;
};
const SiteFooter = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["ssrRender", _sfc_ssrRender], ["__scopeId", "data-v-34babacb"]]);
const _sfc_main = {
  __name: "index",
  __ssrInlineRender: true,
  setup(__props) {
    return (_ctx, _push, _parent, _attrs) => {
      const _component_UpHeader = __nuxt_component_0;
      const _component_Hero = _sfc_main$7;
      _push(`<main${ssrRenderAttrs(mergeProps({
        id: "top",
        class: "min-h-screen bg-[#eef1f8] px-3 pb-5 pt-[92px] sm:px-6 sm:pb-8 sm:pt-[102px] lg:px-8 lg:pt-[112px]"
      }, _attrs))}><div class="relative mx-auto w-full max-w-[1400px] overflow-hidden rounded-[30px] border border-white/70 bg-[#f7f9fe] px-4 pb-10 pt-4 shadow-[0_26px_60px_rgba(36,52,87,0.12)] sm:px-6 lg:px-9 lg:pb-14 lg:pt-6"><div class="pointer-events-none absolute -left-[14%] bottom-[-14%] h-[430px] w-[430px] rounded-full bg-[radial-gradient(circle,rgba(203,218,255,0.5)_0%,rgba(203,218,255,0)_70%)] blur-2xl"></div><div class="pointer-events-none absolute -right-[12%] top-[10%] h-[560px] w-[560px] rounded-full bg-[radial-gradient(circle,rgba(146,195,255,0.56)_0%,rgba(146,195,255,0)_72%)] blur-2xl"></div>`);
      _push(ssrRenderComponent(_component_UpHeader, {
        brand: unref(homepageData).brand,
        nav: unref(homepageData).nav,
        "header-cta": unref(homepageData).headerCta
      }, null, _parent));
      _push(ssrRenderComponent(_component_Hero, {
        hero: unref(homepageData).hero,
        trust: unref(homepageData).trust
      }, null, _parent));
      _push(`</div><div class="mx-auto mt-5 w-full max-w-[1400px] overflow-hidden rounded-[30px] border border-white/70 bg-[#f4f7fd] shadow-[0_22px_52px_rgba(36,52,87,0.1)]">`);
      _push(ssrRenderComponent(_sfc_main$6, null, null, _parent));
      _push(`</div>`);
      _push(ssrRenderComponent(HowItWorksSection, null, null, _parent));
      _push(ssrRenderComponent(PricingSection, null, null, _parent));
      _push(ssrRenderComponent(ReviewsSection, null, null, _parent));
      _push(ssrRenderComponent(FAQSection, null, null, _parent));
      _push(ssrRenderComponent(SiteFooter, null, null, _parent));
      _push(`</main>`);
    };
  }
};
const _sfc_setup = _sfc_main.setup;
_sfc_main.setup = (props, ctx) => {
  const ssrContext = useSSRContext();
  (ssrContext.modules || (ssrContext.modules = /* @__PURE__ */ new Set())).add("pages/index.vue");
  return _sfc_setup ? _sfc_setup(props, ctx) : void 0;
};

export { _sfc_main as default };;globalThis.__timing__.logEnd('Load chunks/build/index-BqWKY-_I');
//# sourceMappingURL=index-BqWKY-_I.mjs.map
