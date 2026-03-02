import { primeSubscriptionStatus } from "~/composables/useSubscriptionStatus";
import { useAuthStore } from "~/stores/auth";

const AUTH_PATHS = new Set(["/auth", "/login", "/register"]);

function normalizeAppPath(path) {
  const normalizedPath = String(path || "/");

  if (normalizedPath === "/app") {
    return "/";
  }

  if (normalizedPath.startsWith("/app/")) {
    return `/${normalizedPath.slice(5)}`;
  }

  return normalizedPath;
}

export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore();

  if (!auth.isInitialized || auth.isInitializing) {
    await auth.initializeAuth();
  }

  const normalizedToPath = normalizeAppPath(to.path);
  const isProtected = normalizedToPath.startsWith("/dashboard");
  const isAuthPage = AUTH_PATHS.has(normalizedToPath);

  if (isProtected && !auth.isAuthenticated) {
    return navigateTo("/login");
  }

  if (isAuthPage && auth.isAuthenticated) {
    return navigateTo("/dashboard");
  }

  if (import.meta.client && auth.isAuthenticated && normalizedToPath.startsWith("/dashboard")) {
    primeSubscriptionStatus();
  }
});
