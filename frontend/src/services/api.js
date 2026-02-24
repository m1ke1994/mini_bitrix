import { $fetch } from "ofetch";
import { useRuntimeConfig } from "#imports";
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
  nextConfig.headers = { ...(nextConfig.headers || {}) };
  nextConfig.headers.Authorization = `Bearer ${token}`;
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
  const token = auth.accessToken || getStoredAccessToken();
  const requestConfig = setAuthorizationHeader(
    {
      ...initialConfig,
      headers: { ...(initialConfig?.headers || {}) },
    },
    token
  );

  try {
    return await executeRawRequest(requestConfig);
  } catch (rawError) {
    const error = normalizeError(rawError, requestConfig);
    const status = error?.response?.status;

    if (status !== 401) {
      return Promise.reject(error);
    }

    if (requestConfig._skipUnauthorizedLogout) {
      return Promise.reject(error);
    }

    const isAuthEndpoint = isAuthEndpointRequest(requestConfig);
    const canRetryWithRefresh =
      !isAuthEndpoint &&
      !requestConfig._retry &&
      !requestConfig._skipAuthRetry &&
      Boolean(auth.refreshToken || hasRefreshTokenInStorage());

    if (canRetryWithRefresh) {
      try {
        refreshRequestPromise ||= auth.refreshAccessToken();
        await refreshRequestPromise;

        const nextToken = auth.accessToken || getStoredAccessToken();
        if (nextToken) {
          return await dispatchRequest({
            ...requestConfig,
            _retry: true,
            headers: {
              ...(requestConfig.headers || {}),
              Authorization: `Bearer ${nextToken}`,
            },
          });
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
