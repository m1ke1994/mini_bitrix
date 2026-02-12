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
  { path: "/login", name: "login", component: LoginPage, meta: { public: true } },
  { path: "/register", name: "register", component: RegisterPage, meta: { public: true } },
  { path: "/dashboard", name: "dashboard", component: DashboardPage },
  { path: "/dashboard/leads", name: "dashboard_leads", component: LeadsPage },
  { path: "/dashboard/settings", name: "dashboard_settings", component: SettingsPage },
  { path: "/dashboard/integration", name: "dashboard_integration", component: IntegrationPage },
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

export default router;
