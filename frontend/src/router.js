import { createRouter, createWebHistory } from "vue-router";
import MainLayout from "./views/MainLayout.vue";
import PublicHomePage from "./views/PublicHomePage.vue";
import PublicFeaturePage from "./views/PublicFeaturePage.vue";
import DashboardLayout from "./views/DashboardLayout.vue";
import DashboardOverview from "./views/DashboardOverview.vue";
import DashboardDynamics from "./views/DashboardDynamics.vue";
import DashboardEngagement from "./views/DashboardEngagement.vue";
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
      title: "TrackNode - SaaS аналитика сайтов и воронка лидогенерации",
      description:
        "TrackNode - платформа аналитики сайтов для малого бизнеса. Отслеживание заявок, воронка лидов, отчеты и Telegram-уведомления в одном сервисе.",
      keywords: "аналитика сайта, SaaS аналитика, TrackNode, воронка лидогенерации, отслеживание заявок",
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
      title: "Аналитика сайтов TrackNode - контроль трафика, лидов и конверсии",
      description:
        "Аналитика TrackNode показывает источники трафика, динамику заявок и конверсию страниц, чтобы быстро находить точки роста.",
      keywords: "аналитика сайта, веб-аналитика, конверсия, лиды, TrackNode",
      pageHeading: "Аналитика сайтов",
      pageText:
        "Собирайте данные по визитам, источникам и событиям в одном интерфейсе. TrackNode помогает видеть реальную эффективность маркетинга и сайта.",
      ogType: "website",
    },
  },
  {
    path: "/otchety",
    name: "otchety",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "Отчеты TrackNode - ежедневные и PDF-отчеты по заявкам и воронке",
      description:
        "Создавайте отчеты по заявкам и воронке продаж в TrackNode: ежедневная статистика, PDF-выгрузка и прозрачные показатели для бизнеса.",
      keywords: "отчеты по лидам, PDF отчет, отчеты аналитики, TrackNode",
      pageHeading: "Отчеты",
      pageText:
        "Формируйте регулярные отчеты по ключевым метрикам: заявкам, источникам и конверсии. Подходит для собственника, маркетолога и отдела продаж.",
      ogType: "website",
    },
  },
  {
    path: "/telegram",
    name: "telegram",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "Telegram-уведомления TrackNode - мгновенные оповещения по заявкам",
      description:
        "Подключите Telegram-уведомления в TrackNode и получайте сообщения о новых заявках, оплатах и статусах без задержек.",
      keywords: "telegram уведомления, уведомления о заявках, TrackNode",
      pageHeading: "Telegram-уведомления",
      pageText:
        "Настройте быстрые уведомления о событиях в Telegram, чтобы команда сразу реагировала на новые обращения и изменения статусов.",
      ogType: "website",
    },
  },
  {
    path: "/tarify",
    name: "tarify",
    component: PublicFeaturePage,
    meta: {
      public: true,
      title: "Тарифы TrackNode - SaaS аналитика для малого и среднего бизнеса",
      description:
        "Выберите тариф TrackNode под ваш поток заявок: прозрачная цена, быстрый старт и инструменты аналитики без сложной настройки.",
      keywords: "тарифы аналитики сайта, цена saas, TrackNode тарифы",
      pageHeading: "Тарифы",
      pageText:
        "Подберите подходящий план для вашего бизнеса и начните работать с аналитикой сайта, отчетами и лидогенерацией в одном сервисе.",
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
      title: "Авторизация | TrackNode",
      description: "Вход в личный кабинет TrackNode.",
      keywords: "tracknode login, авторизация",
    },
  },
  {
    path: "/login",
    name: "login",
    component: AuthPage,
    meta: {
      public: true,
      noindex: true,
      title: "Вход в TrackNode",
      description: "Вход в личный кабинет TrackNode для работы с аналитикой и заявками.",
      keywords: "вход tracknode, логин",
    },
  },
  {
    path: "/register",
    name: "register",
    component: AuthPage,
    meta: {
      public: true,
      noindex: true,
      title: "Регистрация в TrackNode",
      description: "Создайте аккаунт TrackNode для доступа к аналитике сайта и воронке лидогенерации.",
      keywords: "регистрация tracknode, создать аккаунт",
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
              title: "Панель управления - Обзор",
              description: "Личный кабинет TrackNode: обзор ключевых метрик.",
            },
          },
          {
            path: "dynamics",
            name: "dashboard_dynamics",
            component: DashboardDynamics,
            meta: {
              noindex: true,
              title: "Панель управления - Динамика по дням",
              description: "Личный кабинет TrackNode: динамика метрик по дням.",
            },
          },
          {
            path: "sources",
            name: "dashboard_sources",
            component: DashboardSources,
            meta: {
              noindex: true,
              title: "Панель управления - Топ источников",
              description: "Личный кабинет TrackNode: топ источников трафика.",
            },
          },
          {
            path: "unique",
            name: "dashboard_unique",
            component: DashboardUniqueVisitors,
            meta: {
              noindex: true,
              title: "Панель управления - Уникальные пользователи",
              description: "Личный кабинет TrackNode: уникальные пользователи.",
            },
          },
          {
            path: "engagement",
            name: "dashboard_engagement",
            component: DashboardEngagement,
            meta: {
              noindex: true,
              title: "Панель управления - Вовлечённость",
              description: "Личный кабинет TrackNode: вовлечённость пользователей по времени на страницах.",
            },
          },
          {
            path: "clicks",
            name: "dashboard_clicks",
            component: DashboardClicks,
            meta: {
              noindex: true,
              title: "Панель управления - Топ кликов",
              description: "Личный кабинет TrackNode: отчет по кликам.",
            },
          },
          {
            path: "pages-conversion",
            name: "dashboard_pages_conversion",
            component: DashboardPagesConversion,
            meta: {
              noindex: true,
              title: "Панель управления - Конверсия по страницам",
              description: "Личный кабинет TrackNode: конверсия страниц.",
            },
          },
          {
            path: "devices",
            name: "dashboard_devices",
            component: DashboardDevices,
            meta: {
              noindex: true,
              title: "Панель управления - Устройства",
              description: "Личный кабинет TrackNode: статистика устройств.",
            },
          },
        ],
      },
      {
        path: "/leads",
        name: "leads",
        component: LeadsPage,
        meta: { noindex: true, title: "Заявки", description: "Личный кабинет TrackNode: работа с заявками." },
      },
      {
        path: "/settings",
        name: "settings",
        component: SettingsPage,
        meta: { noindex: true, title: "Настройки", description: "Личный кабинет TrackNode: настройки аккаунта." },
      },
      {
        path: "/integration",
        name: "integration",
        component: IntegrationPage,
        meta: { noindex: true, title: "Интеграции", description: "Личный кабинет TrackNode: настройки интеграции." },
      },
      {
        path: "/reports",
        name: "reports",
        component: ReportsPage,
        meta: { noindex: true, title: "Отчет PDF", description: "Личный кабинет TrackNode: PDF-отчеты." },
      },
      {
        path: "/about",
        name: "AboutProject",
        component: () => import("./views/AboutProject.vue"),
        meta: {
          noindex: true,
          title: "О проекте TrackNode - платформа аналитики сайтов",
          description: "TrackNode - система аналитики сайтов и управления заявками для малого и среднего бизнеса.",
          keywords: "TrackNode, аналитика сайта, SaaS аналитика, управление заявками, воронка лидогенерации",
          ogType: "website",
        },
      },
      {
        path: "/instructions",
        name: "instructions",
        component: InstructionsPage,
        meta: { noindex: true, title: "Инструкция по подключению", description: "Личный кабинет TrackNode: инструкции." },
      },
    ],
  },
  { path: "/dashboard/leads", redirect: "/leads" },
  { path: "/dashboard/settings", redirect: "/settings" },
  { path: "/dashboard/integration", redirect: "/integration" },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("./views/NotFoundPage.vue"),
    meta: {
      public: true,
      noindex: true,
      title: "404 - Страница не найдена | TrackNode",
      description: "Страница не найдена.",
    },
  },
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
