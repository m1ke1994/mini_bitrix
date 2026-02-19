import { createRouter, createWebHistory } from "vue-router";
import MainLayout from "./views/MainLayout.vue";
import PublicHomePage from "./views/PublicHomePage.vue";
import PublicFeaturePage from "./views/PublicFeaturePage.vue";
import DashboardLayout from "./views/DashboardLayout.vue";
import DashboardOverview from "./views/DashboardOverview.vue";
import DashboardDynamics from "./views/DashboardDynamics.vue";
import DashboardSources from "./views/DashboardSources.vue";
import DashboardClicks from "./views/DashboardClicks.vue";
import DashboardPagesConversion from "./views/DashboardPagesConversion.vue";
import DashboardUniqueVisitors from "./views/DashboardUniqueVisitors.vue";
import DashboardDevices from "./views/DashboardDevices.vue";
import IntegrationPage from "./views/IntegrationPage.vue";
import InstructionsPage from "./views/InstructionsPage.vue";
import AuthPage from "./views/AuthPage.vue";
import LeadsPage from "./views/LeadsPage.vue";
import ReportsPage from "./views/ReportsPage.vue";
import SettingsPage from "./views/SettingsPage.vue";
import { useAuthStore } from "./stores/auth";
import { homepageSoftwareSchema, setSeoForRoute } from "./seo";

const routes = [
  {
    path: "/",
    name: "home",
    component: PublicHomePage,
    meta: {
      public: true,
      title: "TrackNode вЂ” SaaS Р°РЅР°Р»РёС‚РёРєР° СЃР°Р№С‚РѕРІ Рё РІРѕСЂРѕРЅРєР° Р»РёРґРѕРіРµРЅРµСЂР°С†РёРё",
      description:
        "TrackNode вЂ” РїР»Р°С‚С„РѕСЂРјР° Р°РЅР°Р»РёС‚РёРєРё СЃР°Р№С‚РѕРІ РґР»СЏ РјР°Р»РѕРіРѕ Р±РёР·РЅРµСЃР°. РћС‚СЃР»РµР¶РёРІР°РЅРёРµ Р·Р°СЏРІРѕРє, РІРѕСЂРѕРЅРєР° Р»РёРґРѕРІ, РѕС‚С‡С‘С‚С‹ Рё Telegram-СѓРІРµРґРѕРјР»РµРЅРёСЏ РІ РѕРґРЅРѕРј СЃРµСЂРІРёСЃРµ.",
      keywords: "Р°РЅР°Р»РёС‚РёРєР° СЃР°Р№С‚Р°, SaaS Р°РЅР°Р»РёС‚РёРєР°, TrackNode, РІРѕСЂРѕРЅРєР° Р»РёРґРѕРіРµРЅРµСЂР°С†РёРё, РѕС‚СЃР»РµР¶РёРІР°РЅРёРµ Р·Р°СЏРІРѕРє",
      ogType: "website",
      schema: homepageSoftwareSchema,
    },
  },
  {
    path: "/analitika",
    name: "analitika",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "РђРЅР°Р»РёС‚РёРєР° СЃР°Р№С‚РѕРІ TrackNode вЂ” РєРѕРЅС‚СЂРѕР»СЊ С‚СЂР°С„РёРєР°, Р»РёРґРѕРІ Рё РєРѕРЅРІРµСЂСЃРёРё",
      description:
        "РђРЅР°Р»РёС‚РёРєР° TrackNode РїРѕРєР°Р·С‹РІР°РµС‚ РёСЃС‚РѕС‡РЅРёРєРё С‚СЂР°С„РёРєР°, РґРёРЅР°РјРёРєСѓ Р·Р°СЏРІРѕРє Рё РєРѕРЅРІРµСЂСЃРёСЋ СЃС‚СЂР°РЅРёС†, С‡С‚РѕР±С‹ Р±С‹СЃС‚СЂРѕ РЅР°С…РѕРґРёС‚СЊ С‚РѕС‡РєРё СЂРѕСЃС‚Р°.",
      keywords: "Р°РЅР°Р»РёС‚РёРєР° СЃР°Р№С‚Р°, РІРµР±-Р°РЅР°Р»РёС‚РёРєР°, РєРѕРЅРІРµСЂСЃРёСЏ, Р»РёРґС‹, TrackNode",
      pageHeading: "РђРЅР°Р»РёС‚РёРєР° СЃР°Р№С‚РѕРІ",
      pageText:
        "РЎРѕР±РёСЂР°Р№С‚Рµ РґР°РЅРЅС‹Рµ РїРѕ РІРёР·РёС‚Р°Рј, РёСЃС‚РѕС‡РЅРёРєР°Рј Рё СЃРѕР±С‹С‚РёСЏРј РІ РѕРґРЅРѕРј РёРЅС‚РµСЂС„РµР№СЃРµ. TrackNode РїРѕРјРѕРіР°РµС‚ РІРёРґРµС‚СЊ СЂРµР°Р»СЊРЅСѓСЋ СЌС„С„РµРєС‚РёРІРЅРѕСЃС‚СЊ РјР°СЂРєРµС‚РёРЅРіР° Рё СЃР°Р№С‚Р°.",
      ogType: "website",
    },
  },
  {
    path: "/otchety",
    name: "otchety",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "РћС‚С‡С‘С‚С‹ TrackNode вЂ” РµР¶РµРґРЅРµРІРЅС‹Рµ Рё PDF-РѕС‚С‡С‘С‚С‹ РїРѕ Р·Р°СЏРІРєР°Рј Рё РІРѕСЂРѕРЅРєРµ",
      description:
        "РЎРѕР·РґР°РІР°Р№С‚Рµ РѕС‚С‡С‘С‚С‹ РїРѕ Р·Р°СЏРІРєР°Рј Рё РІРѕСЂРѕРЅРєРµ РїСЂРѕРґР°Р¶ РІ TrackNode: РµР¶РµРґРЅРµРІРЅР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°, PDF-РІС‹РіСЂСѓР·РєР° Рё РїСЂРѕР·СЂР°С‡РЅС‹Рµ РїРѕРєР°Р·Р°С‚РµР»Рё РґР»СЏ Р±РёР·РЅРµСЃР°.",
      keywords: "РѕС‚С‡С‘С‚С‹ РїРѕ Р»РёРґР°Рј, PDF РѕС‚С‡С‘С‚, РѕС‚С‡С‘С‚С‹ Р°РЅР°Р»РёС‚РёРєРё, TrackNode",
      pageHeading: "РћС‚С‡С‘С‚С‹",
      pageText:
        "Р¤РѕСЂРјРёСЂСѓР№С‚Рµ СЂРµРіСѓР»СЏСЂРЅС‹Рµ РѕС‚С‡С‘С‚С‹ РїРѕ РєР»СЋС‡РµРІС‹Рј РјРµС‚СЂРёРєР°Рј: Р·Р°СЏРІРєР°Рј, РёСЃС‚РѕС‡РЅРёРєР°Рј Рё РєРѕРЅРІРµСЂСЃРёРё. РџРѕРґС…РѕРґРёС‚ РґР»СЏ СЃРѕР±СЃС‚РІРµРЅРЅРёРєР°, РјР°СЂРєРµС‚РѕР»РѕРіР° Рё РѕС‚РґРµР»Р° РїСЂРѕРґР°Р¶.",
      ogType: "website",
    },
  },
  {
    path: "/telegram",
    name: "telegram",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "Telegram-СѓРІРµРґРѕРјР»РµРЅРёСЏ TrackNode вЂ” РјРіРЅРѕРІРµРЅРЅС‹Рµ РѕРїРѕРІРµС‰РµРЅРёСЏ РїРѕ Р·Р°СЏРІРєР°Рј",
      description:
        "РџРѕРґРєР»СЋС‡РёС‚Рµ Telegram-СѓРІРµРґРѕРјР»РµРЅРёСЏ РІ TrackNode Рё РїРѕР»СѓС‡Р°Р№С‚Рµ СЃРѕРѕР±С‰РµРЅРёСЏ Рѕ РЅРѕРІС‹С… Р·Р°СЏРІРєР°С…, РѕРїР»Р°С‚Р°С… Рё СЃС‚Р°С‚СѓСЃР°С… Р±РµР· Р·Р°РґРµСЂР¶РµРє.",
      keywords: "telegram СѓРІРµРґРѕРјР»РµРЅРёСЏ, СѓРІРµРґРѕРјР»РµРЅРёСЏ Рѕ Р·Р°СЏРІРєР°С…, TrackNode",
      pageHeading: "Telegram-СѓРІРµРґРѕРјР»РµРЅРёСЏ",
      pageText:
        "РќР°СЃС‚СЂРѕР№С‚Рµ Р±С‹СЃС‚СЂС‹Рµ СѓРІРµРґРѕРјР»РµРЅРёСЏ Рѕ СЃРѕР±С‹С‚РёСЏС… РІ Telegram, С‡С‚РѕР±С‹ РєРѕРјР°РЅРґР° СЃСЂР°Р·Сѓ СЂРµР°РіРёСЂРѕРІР°Р»Р° РЅР° РЅРѕРІС‹Рµ РѕР±СЂР°С‰РµРЅРёСЏ Рё РёР·РјРµРЅРµРЅРёСЏ СЃС‚Р°С‚СѓСЃРѕРІ.",
      ogType: "website",
    },
  },
  {
    path: "/tarify",
    name: "tarify",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "РўР°СЂРёС„С‹ TrackNode вЂ” SaaS Р°РЅР°Р»РёС‚РёРєР° РґР»СЏ РјР°Р»РѕРіРѕ Рё СЃСЂРµРґРЅРµРіРѕ Р±РёР·РЅРµСЃР°",
      description:
        "Р’С‹Р±РµСЂРёС‚Рµ С‚Р°СЂРёС„ TrackNode РїРѕРґ РІР°С€ РїРѕС‚РѕРє Р·Р°СЏРІРѕРє: РїСЂРѕР·СЂР°С‡РЅР°СЏ С†РµРЅР°, Р±С‹СЃС‚СЂС‹Р№ СЃС‚Р°СЂС‚ Рё РёРЅСЃС‚СЂСѓРјРµРЅС‚С‹ Р°РЅР°Р»РёС‚РёРєРё Р±РµР· СЃР»РѕР¶РЅРѕР№ РЅР°СЃС‚СЂРѕР№РєРё.",
      keywords: "С‚Р°СЂРёС„С‹ Р°РЅР°Р»РёС‚РёРєРё СЃР°Р№С‚Р°, С†РµРЅР° saas, TrackNode С‚Р°СЂРёС„С‹",
      pageHeading: "РўР°СЂРёС„С‹",
      pageText:
        "РџРѕРґР±РµСЂРёС‚Рµ РїРѕРґС…РѕРґСЏС‰РёР№ РїР»Р°РЅ РґР»СЏ РІР°С€РµРіРѕ Р±РёР·РЅРµСЃР° Рё РЅР°С‡РЅРёС‚Рµ СЂР°Р±РѕС‚Р°С‚СЊ СЃ Р°РЅР°Р»РёС‚РёРєРѕР№ СЃР°Р№С‚Р°, РѕС‚С‡С‘С‚Р°РјРё Рё Р»РёРґРѕРіРµРЅРµСЂР°С†РёРµР№ РІ РѕРґРЅРѕРј СЃРµСЂРІРёСЃРµ.",
      ogType: "website",
    },
  },
  {
    path: "/auth",
    name: "auth",
    component: AuthPage,
    meta: {
      public: true,
      noindex: true,
      title: "РђРІС‚РѕСЂРёР·Р°С†РёСЏ | TrackNode",
      description: "Р’С…РѕРґ РІ Р»РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode.",
      keywords: "tracknode login, Р°РІС‚РѕСЂРёР·Р°С†РёСЏ",
    },
  },
  {
    path: "/login",
    name: "login",
    component: AuthPage,
    meta: {
      public: true,
      noindex: true,
      title: "Р’С…РѕРґ РІ TrackNode",
      description: "Р’С…РѕРґ РІ Р»РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ Р°РЅР°Р»РёС‚РёРєРѕР№ Рё Р·Р°СЏРІРєР°РјРё.",
      keywords: "РІС…РѕРґ tracknode, Р»РѕРіРёРЅ",
    },
  },
  {
    path: "/register",
    name: "register",
    component: AuthPage,
    meta: {
      public: true,
      noindex: true,
      title: "Р РµРіРёСЃС‚СЂР°С†РёСЏ РІ TrackNode",
      description: "РЎРѕР·РґР°Р№С‚Рµ Р°РєРєР°СѓРЅС‚ TrackNode РґР»СЏ РґРѕСЃС‚СѓРїР° Рє Р°РЅР°Р»РёС‚РёРєРµ СЃР°Р№С‚Р° Рё РІРѕСЂРѕРЅРєРµ Р»РёРґРѕРіРµРЅРµСЂР°С†РёРё.",
      keywords: "СЂРµРіРёСЃС‚СЂР°С†РёСЏ tracknode, СЃРѕР·РґР°С‚СЊ Р°РєРєР°СѓРЅС‚",
    },
  },
  {
    path: "/",
    component: MainLayout,
    meta: { noindex: true },
    children: [
      {
        path: "/dashboard",
        component: DashboardLayout,
        meta: { noindex: true },
        children: [
          {
            path: "",
            name: "dashboard_overview",
            component: DashboardOverview,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - РћР±Р·РѕСЂ",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РѕР±Р·РѕСЂ РєР»СЋС‡РµРІС‹С… РјРµС‚СЂРёРє.",
            },
          },
          {
            path: "dynamics",
            name: "dashboard_dynamics",
            component: DashboardDynamics,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - Р”РёРЅР°РјРёРєР° РїРѕ РґРЅСЏРј",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РґРёРЅР°РјРёРєР° РјРµС‚СЂРёРє РїРѕ РґРЅСЏРј.",
            },
          },
          {
            path: "sources",
            name: "dashboard_sources",
            component: DashboardSources,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - РўРѕРї РёСЃС‚РѕС‡РЅРёРєРѕРІ",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: С‚РѕРї РёСЃС‚РѕС‡РЅРёРєРѕРІ С‚СЂР°С„РёРєР°.",
            },
          },
          {
            path: "unique",
            name: "dashboard_unique",
            component: DashboardUniqueVisitors,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - РЈРЅРёРєР°Р»СЊРЅС‹Рµ РїРѕР»СЊР·РѕРІР°С‚РµР»Рё",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: СѓРЅРёРєР°Р»СЊРЅС‹Рµ РїРѕР»СЊР·РѕРІР°С‚РµР»Рё.",
            },
          },
          {
            path: "clicks",
            name: "dashboard_clicks",
            component: DashboardClicks,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - РўРѕРї РєР»РёРєРѕРІ",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РѕС‚С‡С‘С‚ РїРѕ РєР»РёРєР°Рј.",
            },
          },
          {
            path: "pages-conversion",
            name: "dashboard_pages_conversion",
            component: DashboardPagesConversion,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - РљРѕРЅРІРµСЂСЃРёСЏ РїРѕ СЃС‚СЂР°РЅРёС†Р°Рј",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РєРѕРЅРІРµСЂСЃРёСЏ СЃС‚СЂР°РЅРёС†.",
            },
          },
          {
            path: "devices",
            name: "dashboard_devices",
            component: DashboardDevices,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - РЈСЃС‚СЂРѕР№СЃС‚РІР°",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: СЃС‚Р°С‚РёСЃС‚РёРєР° СѓСЃС‚СЂРѕР№СЃС‚РІ.",
            },
          },
        ],
      },
      {
        path: "/leads",
        name: "leads",
        component: LeadsPage,
        meta: { noindex: true, title: "Р—Р°СЏРІРєРё", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: СЂР°Р±РѕС‚Р° СЃ Р·Р°СЏРІРєР°РјРё." },
      },
      {
        path: "/settings",
        name: "settings",
        component: SettingsPage,
        meta: { noindex: true, title: "РќР°СЃС‚СЂРѕР№РєРё", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РЅР°СЃС‚СЂРѕР№РєРё Р°РєРєР°СѓРЅС‚Р°." },
      },
      {
        path: "/integration",
        name: "integration",
        component: IntegrationPage,
        meta: { noindex: true, title: "РРЅС‚РµРіСЂР°С†РёРё", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РЅР°СЃС‚СЂРѕР№РєРё РёРЅС‚РµРіСЂР°С†РёРё." },
      },
      {
        path: "/reports",
        name: "reports",
        component: ReportsPage,
        meta: { noindex: true, title: "РћС‚С‡С‘С‚ PDF", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: PDF-РѕС‚С‡С‘С‚С‹." },
      },
      {
        path: "/about",
        name: "AboutProject",
        component: () => import("./views/AboutProject.vue"),
        meta: {
          noindex: true,
          title: "О проекте TrackNode — платформа аналитики сайтов",
          description: "TrackNode — система аналитики сайтов и управления заявками для малого и среднего бизнеса.",
          keywords: "TrackNode, аналитика сайта, SaaS аналитика, управление заявками, воронка лидогенерации",
          ogType: "website",
        },
      },
      {
        path: "/instructions",
        name: "instructions",
        component: InstructionsPage,
        meta: { noindex: true, title: "РРЅСЃС‚СЂСѓРєС†РёСЏ РїРѕ РїРѕРґРєР»СЋС‡РµРЅРёСЋ", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РёРЅСЃС‚СЂСѓРєС†РёРё." },
      },
    ],
  },
  { path: "/dashboard/leads", redirect: "/leads" },
  { path: "/dashboard/settings", redirect: "/settings" },
  { path: "/dashboard/integration", redirect: "/integration" },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  const isPublic = to.matched.some((record) => record.meta?.public === true);
  const isAuthPage = ["auth", "login", "register"].includes(String(to.name || ""));

  if (!isPublic && !auth.isAuthenticated) {
    return { name: "login" };
  }
  if (isAuthPage && auth.isAuthenticated) {
    return { name: "dashboard_overview" };
  }
  return true;
});

router.afterEach((to) => {
  setSeoForRoute(to);
});

export default router;
