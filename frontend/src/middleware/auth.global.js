import { primeSubscriptionStatus } from "~/composables/useSubscriptionStatus";
import { useAuthStore } from "~/stores/auth";

const AUTH_PATHS = new Set(["/auth", "/login", "/register"]);
const APP_AUTH_PATHS = new Set(["/app/auth", "/app/login", "/app/register"]);

export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore();

  if (!auth.isInitialized || auth.isInitializing) {
    await auth.initializeAuth();
  }

  const isPublic = to.matched.some((record) => record.meta?.publicPage === true);
  const toPath = String(to.path || "");
  const isAuthPage = AUTH_PATHS.has(toPath) || APP_AUTH_PATHS.has(toPath);
  const isDashboardPage =
    toPath.startsWith("/app/dashboard") ||
    toPath.startsWith("/dashboard") ||
    toPath.startsWith("/app/crm");

  if (!isPublic && !auth.isAuthenticated) {
    return navigateTo("/app/login");
  }

  if (isAuthPage && auth.isAuthenticated) {
    return navigateTo("/app/dashboard");
  }

  if (import.meta.client && auth.isAuthenticated && isDashboardPage) {
    primeSubscriptionStatus();
  }
});
