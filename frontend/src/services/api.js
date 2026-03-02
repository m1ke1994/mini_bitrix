import { $fetch } from "ofetch";
import { useRuntimeConfig } from "#imports";
import { useAuthStore } from "../stores/auth";
import {
  buildAuthorizationHeader,
  debugAuth,
  getAccessToken,
  getRefreshToken,
  maskToken,
  normalizeToken,
} from "./authStorage";

const AUTH_ENDPOINTS = ["/api/auth/login/", "/api/auth/register/", "/api/auth/logout/", "/api/auth/refresh/"];
const CABINET_PATHS = ["/dashboard", "/settings", "/account", "/integration", "/reports", "/instructions"];

let refreshRequestPromise = null;

function isAuthEndpointRequest(config) {
  const url = String(config?.url || "");
  return AUTH_ENDPOINTS.some((endpoint) => url.includes(endpoint));
}

function setAuthorizationHeader(config, token) {
  const nextConfig = {
    ...config,
    headers: { ...(config?.headers || {}) },
  };

  const authorizationHeader = buildAuthorizationHeader(token);
  if (!authorizationHeader) {
    delete nextConfig.headers.Authorization;
    return nextConfig;
  }

  nextConfig.headers.Authorization = authorizationHeader;
  debugAuth("Authorization header attached", {
    url: String(nextConfig.url || ""),
    token: maskToken(token),
  });
  return nextConfig;
}

function isAbsoluteUrl(url) {
  return /^https?:\/\//i.test(String(url || ""));
}

function getApiBaseUrl() {
  try {
    const config = useRuntimeConfig();
    const runtimeBase = String(config?.public?.apiBase || "").trim();
    if (runtimeBase) return runtimeBase;
  } catch {
    // Runtime config is not available outside Nuxt app context; fall back to envs below.
  }

  try {
    const clientRuntimeBase = String(globalThis?.__NUXT__?.config?.public?.apiBase || "").trim();
    if (clientRuntimeBase) return clientRuntimeBase;
  } catch {
    // Ignore global lookup errors.
  }

  return process.env.VITE_API_BASE || process.env.VITE_API_BASE_URL || "http://localhost:9000";
}

function getAppBaseUrl() {
  try {
    const config = useRuntimeConfig();
    const runtimeBase = String(config?.app?.baseURL || "").trim();
    if (runtimeBase) return runtimeBase;
  } catch {
    // Runtime config is not available outside Nuxt app context; fall back to client config.
  }

  try {
    const clientRuntimeBase = String(globalThis?.__NUXT__?.config?.app?.baseURL || "").trim();
    if (clientRuntimeBase) return clientRuntimeBase;
  } catch {
    // Ignore global lookup errors.
  }

  return "/";
}

function getLoginRedirectPath() {
  const baseUrl = getAppBaseUrl();
  const normalizedBaseUrl = `/${String(baseUrl || "/").replace(/^\/+|\/+$/g, "")}`.replace(/\/$/, "");
  if (!normalizedBaseUrl || normalizedBaseUrl === "/") {
    return "/login";
  }
  return `${normalizedBaseUrl}/login`;
}

function getCurrentRoutePath() {
  if (!import.meta.client || typeof window === "undefined") return "server";
  return `${window.location.pathname}${window.location.search || ""}`;
}

function normalizeClientPath(path) {
  const normalizedPath = String(path || "/").trim();
  if (!normalizedPath) return "/";
  if (normalizedPath === "/") return "/";
  if (normalizedPath.endsWith("/")) return normalizedPath.slice(0, -1);
  return normalizedPath;
}

function isCabinetPath(path) {
  return CABINET_PATHS.some((basePath) => path === basePath || path.startsWith(`${basePath}/`));
}

function redirectToLogin() {
  if (!import.meta.client || typeof window === "undefined") return;

  const loginPath = getLoginRedirectPath();
  const normalizedCurrentPath = normalizeClientPath(window.location.pathname);
  const normalizedLoginPath = normalizeClientPath(loginPath);
  if (normalizedCurrentPath === normalizedLoginPath) return;
  if (!isCabinetPath(normalizedCurrentPath)) return;

  window.location.assign(loginPath);
}

function normalizeError(error, requestConfig) {
  const normalized = error || new Error("API_REQUEST_FAILED");
  const status = Number(normalized?.status || normalized?.response?.status || 0) || undefined;
  const data =
    normalized?.data ??
    normalized?.response?._data ??
    normalized?.response?.data ??
    null;

  if (!normalized.response) {
    normalized.response = {};
  }

  if (status && !normalized.response.status) {
    normalized.response.status = status;
  }

  if (data !== null && typeof normalized.response.data === "undefined") {
    normalized.response.data = data;
  }

  if (requestConfig && !normalized.config) {
    normalized.config = requestConfig;
  }

  return normalized;
}

function buildRequestConfig(method, url, dataOrConfig, config) {
  if (method === "get" || method === "delete") {
    return {
      method,
      url,
      ...(dataOrConfig || {}),
    };
  }

  return {
    method,
    url,
    data: dataOrConfig,
    ...(config || {}),
  };
}

async function executeRawRequest(requestConfig) {
  const method = String(requestConfig.method || "get").toUpperCase();
  const url = String(requestConfig.url || "");
  const baseURL = getApiBaseUrl();
  const useBaseURL = !isAbsoluteUrl(url);

  const response = await $fetch.raw(url, {
    method,
    baseURL: useBaseURL ? baseURL : undefined,
    params: requestConfig.params,
    headers: requestConfig.headers,
    body: typeof requestConfig.data === "undefined" ? undefined : requestConfig.data,
  });

  return {
    data: response._data,
    status: response.status,
    headers: response.headers,
    config: requestConfig,
  };
}

async function dispatchRequest(initialConfig) {
  const auth = useAuthStore();
  const token = normalizeToken(auth.accessToken || getAccessToken());
  const requestConfig = setAuthorizationHeader(initialConfig, token);

  try {
    return await executeRawRequest(requestConfig);
  } catch (rawError) {
    const error = normalizeError(rawError, requestConfig);
    const status = Number(error?.response?.status || 0);
    const isUnauthorizedStatus = status === 401 || status === 403;

    if (!isUnauthorizedStatus) {
      return Promise.reject(error);
    }

    debugAuth("Unauthorized API response", {
      status,
      url: String(requestConfig.url || ""),
      route: getCurrentRoutePath(),
    });

    if (requestConfig._skipUnauthorizedLogout) {
      return Promise.reject(error);
    }

    const isAuthEndpoint = isAuthEndpointRequest(requestConfig);
    const refreshToken = normalizeToken(auth.refreshToken || getRefreshToken());
    const canRetryWithRefresh =
      !isAuthEndpoint &&
      !requestConfig._retry &&
      !requestConfig._skipAuthRetry &&
      Boolean(refreshToken);

    if (canRetryWithRefresh) {
      try {
        if (!auth.refreshToken && refreshToken) {
          auth.refreshToken = refreshToken;
        }

        refreshRequestPromise ||= auth.refreshAccessToken();
        await refreshRequestPromise;

        const nextToken = normalizeToken(auth.accessToken || getAccessToken());
        if (nextToken) {
          return await dispatchRequest({
            ...requestConfig,
            _retry: true,
            headers: {
              ...(requestConfig.headers || {}),
              Authorization: buildAuthorizationHeader(nextToken),
            },
          });
        }
      } catch (_) {
        debugAuth("Refresh flow failed", {
          status,
          url: String(requestConfig.url || ""),
          route: getCurrentRoutePath(),
        });
      } finally {
        refreshRequestPromise = null;
      }
    }

    if (!isAuthEndpoint) {
      auth.clearAuth();
      auth.isInitialized = true;
      redirectToLogin();
    }

    return Promise.reject(error);
  }
}

const api = {
  get(url, config) {
    return dispatchRequest(buildRequestConfig("get", url, config));
  },

  delete(url, config) {
    return dispatchRequest(buildRequestConfig("delete", url, config));
  },

  post(url, data, config) {
    return dispatchRequest(buildRequestConfig("post", url, data, config));
  },

  put(url, data, config) {
    return dispatchRequest(buildRequestConfig("put", url, data, config));
  },

  patch(url, data, config) {
    return dispatchRequest(buildRequestConfig("patch", url, data, config));
  },
};

export default api;
