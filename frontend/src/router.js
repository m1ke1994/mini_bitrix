import { createRouter, createWebHistory } from "vue-router";
import DashboardPage from "./views/DashboardPage.vue";
import IntegrationPage from "./views/IntegrationPage.vue";
import LoginPage from "./views/LoginPage.vue";
import LeadsPage from "./views/LeadsPage.vue";
import RegisterPage from "./views/RegisterPage.vue";
import SettingsPage from "./views/SettingsPage.vue";
import { useAuthStore } from "./stores/auth";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/login", name: "login", component: LoginPage, meta: { public: true, title: "Вход" } },
  { path: "/register", name: "register", component: RegisterPage, meta: { public: true, title: "Регистрация" } },
  { path: "/dashboard", name: "dashboard", component: DashboardPage, meta: { title: "Панель управления" } },
  { path: "/dashboard/leads", name: "dashboard_leads", component: LeadsPage, meta: { title: "Заявки" } },
  { path: "/dashboard/settings", name: "dashboard_settings", component: SettingsPage, meta: { title: "Настройки" } },
  { path: "/dashboard/integration", name: "dashboard_integration", component: IntegrationPage, meta: { title: "Интеграция" } },
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
    return { name: "dashboard" };
  }
  return true;
});

router.afterEach((to) => {
  const pageTitle = to.meta?.title ? `${to.meta.title} | TrackNode Analytics` : "TrackNode Analytics";
  document.title = pageTitle;
});

export default router;
