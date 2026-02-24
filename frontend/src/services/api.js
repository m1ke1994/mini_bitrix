import axios from "axios";
import { useAuthStore } from "../stores/auth";

const AUTH_ENDPOINTS = ["/api/auth/login/", "/api/auth/register/", "/api/auth/logout/", "/api/auth/refresh/"];

let refreshRequestPromise = null;

function canUseWebStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function getStoredAccessToken() {
  if (!canUseWebStorage()) return "";
  try {
    return String(window.localStorage.getItem("accessToken") || "");
  } catch {
    return "";
  }
}

function hasRefreshTokenInStorage() {
  if (!canUseWebStorage()) return false;
  try {
    return Boolean(window.localStorage.getItem("refreshToken"));
  } catch {
    return false;
  }
}

function isAuthEndpointRequest(config) {
  const url = String(config?.url || "");
  return AUTH_ENDPOINTS.some((endpoint) => url.includes(endpoint));
}

function setAuthorizationHeader(config, token) {
  if (!token) return config;

  const nextConfig = config;
  nextConfig.headers = nextConfig.headers || {};
  nextConfig.headers.Authorization = `Bearer ${token}`;
  return nextConfig;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:9000",
});

api.interceptors.request.use((config) => {
  const auth = useAuthStore();
  const token = auth.accessToken || getStoredAccessToken();
  return setAuthorizationHeader(config, token);
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status;
    const originalRequest = error?.config || {};

    if (status !== 401) {
      return Promise.reject(error);
    }

    if (originalRequest._skipUnauthorizedLogout) {
      return Promise.reject(error);
    }

    const auth = useAuthStore();
    const isAuthEndpoint = isAuthEndpointRequest(originalRequest);
    const canRetryWithRefresh =
      !isAuthEndpoint &&
      !originalRequest._retry &&
      !originalRequest._skipAuthRetry &&
      Boolean(auth.refreshToken || hasRefreshTokenInStorage());

    if (canRetryWithRefresh) {
      originalRequest._retry = true;

      try {
        refreshRequestPromise ||= auth.refreshAccessToken();
        await refreshRequestPromise;

        const nextToken = auth.accessToken || getStoredAccessToken();
        if (nextToken) {
          setAuthorizationHeader(originalRequest, nextToken);
          return api(originalRequest);
        }
      } catch (_) {
        // Fall through to local cleanup.
      } finally {
        refreshRequestPromise = null;
      }
    }

    if (!isAuthEndpoint) {
      auth.clearAuth();
      auth.isInitialized = true;
    }

    return Promise.reject(error);
  }
);

export default api;
