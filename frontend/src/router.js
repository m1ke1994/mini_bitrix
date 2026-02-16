import { createRouter, createWebHistory } from "vue-router";
import MainLayout from "./views/MainLayout.vue";
import DashboardLayout from "./views/DashboardLayout.vue";
import DashboardOverview from "./views/DashboardOverview.vue";
import DashboardDynamics from "./views/DashboardDynamics.vue";
import DashboardSources from "./views/DashboardSources.vue";
import DashboardClicks from "./views/DashboardClicks.vue";
import DashboardPagesConversion from "./views/DashboardPagesConversion.vue";
import DashboardUniqueVisitors from "./views/DashboardUniqueVisitors.vue";
import IntegrationPage from "./views/IntegrationPage.vue";
import InstructionsPage from "./views/InstructionsPage.vue";
import LoginPage from "./views/LoginPage.vue";
import LeadsPage from "./views/LeadsPage.vue";
import RegisterPage from "./views/RegisterPage.vue";
import ReportsPage from "./views/ReportsPage.vue";
import SettingsPage from "./views/SettingsPage.vue";
import { useAuthStore } from "./stores/auth";

const routes = [
  { path: "/login", name: "login", component: LoginPage, meta: { public: true, title: "Вход" } },
  { path: "/register", name: "register", component: RegisterPage, meta: { public: true, title: "Регистрация" } },
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "", redirect: "/dashboard" },
      {
        path: "dashboard",
        component: DashboardLayout,
        children: [
          { path: "", name: "dashboard_overview", component: DashboardOverview, meta: { title: "Панель управления - Обзор" } },
          {
            path: "dynamics",
            name: "dashboard_dynamics",
            component: DashboardDynamics,
            meta: { title: "Панель управления - Динамика по дням" },
          },
          {
            path: "sources",
            name: "dashboard_sources",
            component: DashboardSources,
            meta: { title: "Панель управления - Топ источников" },
          },
          {
            path: "unique",
            name: "dashboard_unique",
            component: DashboardUniqueVisitors,
            meta: { title: "Панель управления - Уникальные пользователи" },
          },
          {
            path: "clicks",
            name: "dashboard_clicks",
            component: DashboardClicks,
            meta: { title: "Панель управления - Топ кликов" },
          },
          {
            path: "pages-conversion",
            name: "dashboard_pages_conversion",
            component: DashboardPagesConversion,
            meta: { title: "Панель управления - Конверсия по страницам" },
          },
        ],
      },
      { path: "leads", name: "leads", component: LeadsPage, meta: { title: "Заявки" } },
      { path: "settings", name: "settings", component: SettingsPage, meta: { title: "Настройки" } },
      { path: "integration", name: "integration", component: IntegrationPage, meta: { title: "Интеграции" } },
      { path: "reports", name: "reports", component: ReportsPage, meta: { title: "Отчёт PDF" } },
      { path: "instructions", name: "instructions", component: InstructionsPage, meta: { title: "Инструкция по подключению" } },
    ],
  },
  { path: "/dashboard/leads", redirect: "/leads" },
  { path: "/dashboard/settings", redirect: "/settings" },
  { path: "/dashboard/integration", redirect: "/integration" },
  { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: "login" };
  }
  if (to.meta.public && auth.isAuthenticated) {
    return { name: "dashboard_overview" };
  }
  return true;
});

router.afterEach((to) => {
  const pageTitle = to.meta?.title ? `${to.meta.title} | TrackNode Analytics` : "TrackNode Analytics";
  document.title = pageTitle;
});

export default router;
