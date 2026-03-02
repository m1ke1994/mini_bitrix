import { primeSubscriptionStatus } from "~/composables/useSubscriptionStatus";
import { useAuthStore } from "~/stores/auth";

const AUTH_PATHS = new Set(["/auth", "/login", "/register"]);
const CABINET_PATHS = ["/dashboard", "/settings", "/account", "/integration", "/reports", "/instructions"];

function normalizeAppPath(path) {
  const rawPath = String(path || "/").trim();
  const normalizedPath = rawPath.startsWith("/") ? rawPath : `/${rawPath}`;

  if (normalizedPath === "/app") {
    return "/";
  }

  if (normalizedPath.startsWith("/app/")) {
    return `/${normalizedPath.slice(5)}`;
  }

  if (normalizedPath.length > 1 && normalizedPath.endsWith("/")) {
    return normalizedPath.slice(0, -1);
  }

  return normalizedPath;
}

function isPathWithin(path, basePath) {
  return path === basePath || path.startsWith(`${basePath}/`);
}

export default defineNuxtRouteMiddleware(async (to) => {
  const normalizedToPath = normalizeAppPath(to.path);
  const isProtected = CABINET_PATHS.some((path) => isPathWithin(normalizedToPath, path));
  const isAuthPage = AUTH_PATHS.has(normalizedToPath);
  const isDashboardRoute = isPathWithin(normalizedToPath, "/dashboard");

  if (!isProtected && !isAuthPage) {
    return;
  }

  const auth = useAuthStore();
  if (!auth.isInitialized || auth.isInitializing) {
    await auth.initializeAuth();
  }

  if (isProtected && !auth.isAuthenticated) {
    return navigateTo("/login");
  }

  if (isAuthPage && auth.isAuthenticated) {
    return navigateTo("/dashboard");
  }

  if (import.meta.client && auth.isAuthenticated && isDashboardRoute) {
    primeSubscriptionStatus();
  }
});
