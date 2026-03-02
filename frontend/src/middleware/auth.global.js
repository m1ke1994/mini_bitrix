import { primeSubscriptionStatus } from "~/composables/useSubscriptionStatus";
import { useAuthStore } from "~/stores/auth";

const AUTH_PATHS = new Set(["/auth", "/login", "/register"]);

export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore();

  if (!auth.isInitialized || auth.isInitializing) {
    await auth.initializeAuth();
  }

  const isPublic = to.matched.some((record) => record.meta?.publicPage === true);
  const isAuthPage = AUTH_PATHS.has(String(to.path || ""));

  if (!isPublic && !auth.isAuthenticated) {
    return navigateTo("/login");
  }

  if (isAuthPage && auth.isAuthenticated) {
    return navigateTo("/dashboard");
  }

  if (import.meta.client && auth.isAuthenticated && String(to.path || "").startsWith("/dashboard")) {
    primeSubscriptionStatus();
  }
});
