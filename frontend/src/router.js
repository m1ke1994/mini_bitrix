import { createRouter, createWebHistory } from "vue-router";
import PublicHomePage from "./views/PublicHomePage.vue";
import { primeSubscriptionStatus } from "./composables/useSubscriptionStatus";
import { useAuthStore } from "./stores/auth";
import { homepageSoftwareSchema, setSeoForRoute } from "./seo";

const MainLayout = () => import("./views/MainLayout.vue");
const PublicFeaturePage = () => import("./views/PublicFeaturePage.vue");
const DashboardLayout = () => import("./views/DashboardLayout.vue");
const DashboardOverview = () => import("./views/DashboardOverview.vue");
const DashboardDynamics = () => import("./views/DashboardDynamics.vue");
const DashboardEngagement = () => import("./views/DashboardEngagement.vue");
const DashboardSources = () => import("./views/DashboardSources.vue");
const DashboardClicks = () => import("./views/DashboardClicks.vue");
const DashboardPagesConversion = () => import("./views/DashboardPagesConversion.vue");
const DashboardUniqueVisitors = () => import("./views/DashboardUniqueVisitors.vue");
const DashboardDevices = () => import("./views/DashboardDevices.vue");
const DashboardSeoAudit = () => import("./views/DashboardSeoAudit.vue");
const DashboardAiRecommendations = () => import("./views/DashboardAiRecommendations.vue");
const IntegrationPage = () => import("./views/IntegrationPage.vue");
const InstructionsPage = () => import("./views/InstructionsPage.vue");
const AuthPage = () => import("./views/AuthPage.vue");
const ReportsPage = () => import("./views/ReportsPage.vue");
const SettingsPage = () => import("./views/SettingsPage.vue");
const AccountView = () => import("./views/AccountView.vue");

const routes = [
  {
    path: "/",
    name: "home",
    component: PublicHomePage,
    meta: {
      public: true,
      title:
        "РђРЅР°Р»РёС‚РёРєР° СЃР°Р№С‚РѕРІ Рё СѓС‡РµС‚ Р·Р°СЏРІРѕРє вЂ” СЃРµСЂРІРёСЃ РѕС‚СЃР»РµР¶РёРІР°РЅРёСЏ Р»РёРґРѕРІ | TrackNode",
      description:
        "РЎРµСЂРІРёСЃ Р°РЅР°Р»РёС‚РёРєРё СЃР°Р№С‚РѕРІ Рё СѓС‡РµС‚Р° Р·Р°СЏРІРѕРє. РћС‚СЃР»РµР¶РёРІР°Р№С‚Рµ Р»РёРґС‹, РєРѕРЅРІРµСЂСЃРёСЋ Рё РїСѓС‚СЊ РєР»РёРµРЅС‚Р°. РђРЅР°Р»РёС‚РёРєР° РІРѕСЂРѕРЅРєРё РїСЂРѕРґР°Р¶ Рё Telegram-СѓРІРµРґРѕРјР»РµРЅРёСЏ РІ РѕРґРЅРѕРј РєР°Р±РёРЅРµС‚Рµ.",
      keywords:
        "Р°РЅР°Р»РёС‚РёРєР° СЃР°Р№С‚РѕРІ, СЃРµСЂРІРёСЃ Р°РЅР°Р»РёС‚РёРєРё, СѓС‡РµС‚ Р·Р°СЏРІРѕРє, Р°РЅР°Р»РёС‚РёРєР° РІРѕСЂРѕРЅРєРё РїСЂРѕРґР°Р¶, РѕС‚СЃР»РµР¶РёРІР°РЅРёРµ РєРѕРЅРІРµСЂСЃРёРё, TrackNode",
      ogImageAlt: "Р°РЅР°Р»РёС‚РёРєР° СЃР°Р№С‚РѕРІ РёРЅС‚РµСЂС„РµР№СЃ",
      twitterImageAlt: "СѓС‡РµС‚ Р·Р°СЏРІРѕРє РґР°С€Р±РѕСЂРґ",
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
      title: "РђРЅР°Р»РёС‚РёРєР° СЃР°Р№С‚РѕРІ TrackNode - РєРѕРЅС‚СЂРѕР»СЊ С‚СЂР°С„РёРєР°, Р»РёРґРѕРІ Рё РєРѕРЅРІРµСЂСЃРёРё",
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
      title: "РћС‚С‡РµС‚С‹ TrackNode - РµР¶РµРґРЅРµРІРЅС‹Рµ Рё PDF-РѕС‚С‡РµС‚С‹ РїРѕ Р·Р°СЏРІРєР°Рј Рё РІРѕСЂРѕРЅРєРµ",
      description:
        "РЎРѕР·РґР°РІР°Р№С‚Рµ РѕС‚С‡РµС‚С‹ РїРѕ Р·Р°СЏРІРєР°Рј Рё РІРѕСЂРѕРЅРєРµ РїСЂРѕРґР°Р¶ РІ TrackNode: РµР¶РµРґРЅРµРІРЅР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°, PDF-РІС‹РіСЂСѓР·РєР° Рё РїСЂРѕР·СЂР°С‡РЅС‹Рµ РїРѕРєР°Р·Р°С‚РµР»Рё РґР»СЏ Р±РёР·РЅРµСЃР°.",
      keywords: "РѕС‚С‡РµС‚С‹ РїРѕ Р»РёРґР°Рј, PDF РѕС‚С‡РµС‚, РѕС‚С‡РµС‚С‹ Р°РЅР°Р»РёС‚РёРєРё, TrackNode",
      pageHeading: "РћС‚С‡РµС‚С‹",
      pageText:
        "Р¤РѕСЂРјРёСЂСѓР№С‚Рµ СЂРµРіСѓР»СЏСЂРЅС‹Рµ РѕС‚С‡РµС‚С‹ РїРѕ РєР»СЋС‡РµРІС‹Рј РјРµС‚СЂРёРєР°Рј: Р·Р°СЏРІРєР°Рј, РёСЃС‚РѕС‡РЅРёРєР°Рј Рё РєРѕРЅРІРµСЂСЃРёРё. РџРѕРґС…РѕРґРёС‚ РґР»СЏ СЃРѕР±СЃС‚РІРµРЅРЅРёРєР°, РјР°СЂРєРµС‚РѕР»РѕРіР° Рё РѕС‚РґРµР»Р° РїСЂРѕРґР°Р¶.",
      ogType: "website",
    },
  },
  {
    path: "/telegram",
    name: "telegram",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "Telegram-СѓРІРµРґРѕРјР»РµРЅРёСЏ TrackNode - РјРіРЅРѕРІРµРЅРЅС‹Рµ РѕРїРѕРІРµС‰РµРЅРёСЏ РїРѕ Р·Р°СЏРІРєР°Рј",
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
      title: "РўР°СЂРёС„С‹ TrackNode - SaaS Р°РЅР°Р»РёС‚РёРєР° РґР»СЏ РјР°Р»РѕРіРѕ Рё СЃСЂРµРґРЅРµРіРѕ Р±РёР·РЅРµСЃР°",
      description:
        "Р’С‹Р±РµСЂРёС‚Рµ С‚Р°СЂРёС„ TrackNode РїРѕРґ РІР°С€ РїРѕС‚РѕРє Р·Р°СЏРІРѕРє: РїСЂРѕР·СЂР°С‡РЅР°СЏ С†РµРЅР°, Р±С‹СЃС‚СЂС‹Р№ СЃС‚Р°СЂС‚ Рё РёРЅСЃС‚СЂСѓРјРµРЅС‚С‹ Р°РЅР°Р»РёС‚РёРєРё Р±РµР· СЃР»РѕР¶РЅРѕР№ РЅР°СЃС‚СЂРѕР№РєРё.",
      keywords: "С‚Р°СЂРёС„С‹ Р°РЅР°Р»РёС‚РёРєРё СЃР°Р№С‚Р°, С†РµРЅР° saas, TrackNode С‚Р°СЂРёС„С‹",
      pageHeading: "РўР°СЂРёС„С‹",
      pageText:
        "РџРѕРґР±РµСЂРёС‚Рµ РїРѕРґС…РѕРґСЏС‰РёР№ РїР»Р°РЅ РґР»СЏ РІР°С€РµРіРѕ Р±РёР·РЅРµСЃР° Рё РЅР°С‡РЅРёС‚Рµ СЂР°Р±РѕС‚Р°С‚СЊ СЃ Р°РЅР°Р»РёС‚РёРєРѕР№ СЃР°Р№С‚Р°, РѕС‚С‡РµС‚Р°РјРё Рё Р»РёРґРѕРіРµРЅРµСЂР°С†РёРµР№ РІ РѕРґРЅРѕРј СЃРµСЂРІРёСЃРµ.",
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
            path: "engagement",
            name: "dashboard_engagement",
            component: DashboardEngagement,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - Р’РѕРІР»РµС‡С‘РЅРЅРѕСЃС‚СЊ",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РІРѕРІР»РµС‡С‘РЅРЅРѕСЃС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№ РїРѕ РІСЂРµРјРµРЅРё РЅР° СЃС‚СЂР°РЅРёС†Р°С….",
            },
          },
          {
            path: "clicks",
            name: "dashboard_clicks",
            component: DashboardClicks,
            meta: {
              noindex: true,
              title: "РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ - РўРѕРї РєР»РёРєРѕРІ",
              description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РѕС‚С‡РµС‚ РїРѕ РєР»РёРєР°Рј.",
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
            path: "seo",
            name: "dashboard_seo",
            component: DashboardSeoAudit,
            meta: {
              noindex: true,
              title: "SEO Р°СѓРґРёС‚",
              description: "Р‘Р°Р·РѕРІС‹Р№ SEO-Р°СѓРґРёС‚ СЃР°Р№С‚Р° РІ РєР°Р±РёРЅРµС‚Рµ TrackNode.",
            },
          },
          {
            path: "ai-recommendations",
            name: "dashboard_ai_recommendations",
            component: DashboardAiRecommendations,
            meta: {
              noindex: true,
              title: "Поведение пользователя на сайте",
              description: "Поведенческая аналитика для бизнеса: глубина просмотра, формы, кнопки и ключевые действия пользователей.",
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
        path: "/settings",
        name: "settings",
        component: SettingsPage,
        meta: { noindex: true, title: "РќР°СЃС‚СЂРѕР№РєРё", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: РЅР°СЃС‚СЂРѕР№РєРё Р°РєРєР°СѓРЅС‚Р°." },
      },
      {
        path: "/account",
        name: "account",
        component: AccountView,
        meta: { noindex: true, title: "РђРєРєР°СѓРЅС‚", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: СЃРјРµРЅР° РїР°СЂРѕР»СЏ." },
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
        meta: { noindex: true, title: "РћС‚С‡РµС‚ PDF", description: "Р›РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ TrackNode: PDF-РѕС‚С‡РµС‚С‹." },
      },
      {
        path: "/about",
        name: "AboutProject",
        component: () => import("./views/AboutProject.vue"),
        meta: {
          noindex: true,
          title: "Рћ РїСЂРѕРµРєС‚Рµ TrackNode - РїР»Р°С‚С„РѕСЂРјР° Р°РЅР°Р»РёС‚РёРєРё СЃР°Р№С‚РѕРІ",
          description: "TrackNode - СЃРёСЃС‚РµРјР° Р°РЅР°Р»РёС‚РёРєРё СЃР°Р№С‚РѕРІ Рё СѓРїСЂР°РІР»РµРЅРёСЏ Р·Р°СЏРІРєР°РјРё РґР»СЏ РјР°Р»РѕРіРѕ Рё СЃСЂРµРґРЅРµРіРѕ Р±РёР·РЅРµСЃР°.",
          keywords: "TrackNode, Р°РЅР°Р»РёС‚РёРєР° СЃР°Р№С‚Р°, SaaS Р°РЅР°Р»РёС‚РёРєР°, СѓРїСЂР°РІР»РµРЅРёРµ Р·Р°СЏРІРєР°РјРё, РІРѕСЂРѕРЅРєР° Р»РёРґРѕРіРµРЅРµСЂР°С†РёРё",
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
  { path: "/dashboard/settings", redirect: "/settings" },
  { path: "/dashboard/integration", redirect: "/integration" },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("./views/NotFoundPage.vue"),
    meta: {
      public: true,
      noindex: true,
      title: "404 - РЎС‚СЂР°РЅРёС†Р° РЅРµ РЅР°Р№РґРµРЅР° | TrackNode",
      description: "РЎС‚СЂР°РЅРёС†Р° РЅРµ РЅР°Р№РґРµРЅР°.",
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.isInitialized || auth.isInitializing) {
    await auth.initializeAuth();
  }
  const isPublic = to.matched.some((record) => record.meta?.public === true);
  const isAuthPage = ["auth", "login", "register"].includes(String(to.name || ""));

  if (!isPublic && !auth.isAuthenticated) {
    return { name: "login" };
  }
  if (isAuthPage && auth.isAuthenticated) {
    return { name: "dashboard_overview" };
  }

  if (auth.isAuthenticated && to.path.startsWith("/dashboard")) {
    primeSubscriptionStatus();
  }

  return true;
});

router.afterEach((to) => {
  setSeoForRoute(to);
});

export default router;
