import { defineStore } from "pinia";
import api from "../services/api";
import {
  AUTH_STORAGE_KEY_LIST,
  clearAuthStorage,
  getRefreshToken,
  normalizeToken,
  readAuthStorage,
  writeAuthStorage,
} from "../services/authStorage";

const SUBSCRIPTION_CACHE_KEY = "tracknode:subscription-status:v1";
const JWT_EXP_LEEWAY_MS = 30_000;

let authInitPromise = null;
let storageSyncAttached = false;

function clearSubscriptionCache() {
  if (typeof window === "undefined" || typeof window.sessionStorage === "undefined") return;
  try {
    window.sessionStorage.removeItem(SUBSCRIPTION_CACHE_KEY);
  } catch {
    // Ignore storage cleanup errors.
  }
}

function decodeJwtPayload(token) {
  if (!token || typeof token !== "string") return null;

  const parts = token.split(".");
  if (parts.length < 2) return null;

  const payloadPart = parts[1].replace(/-/g, "+").replace(/_/g, "/");
  const paddedPayload = payloadPart.padEnd(payloadPart.length + ((4 - (payloadPart.length % 4)) % 4), "=");

  try {
    const binary = atob(paddedPayload);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
    const json = new TextDecoder().decode(bytes);
    const payload = JSON.parse(json);
    return payload && typeof payload === "object" ? payload : null;
  } catch {
    return null;
  }
}

function isJwtExpired(token) {
  const payload = decodeJwtPayload(token);
  const exp = Number(payload?.exp || 0);
  if (!exp) return true;
  return exp * 1000 <= Date.now() + JWT_EXP_LEEWAY_MS;
}

function buildUserStateFromToken(token, fallback = {}) {
  const payload = decodeJwtPayload(token);
  return {
    userEmail: String(payload?.email || fallback.userEmail || ""),
    clientId: payload?.client_id ? String(payload.client_id) : String(fallback.clientId || ""),
  };
}

function extractErrorMessage(error, fallback) {
  const data = error?.response?.data || {};
  const errors = data.errors || {};
  const firstField = Object.keys(errors)[0];
  if (firstField && Array.isArray(errors[firstField]) && errors[firstField][0]) {
    return String(errors[firstField][0]);
  }
  if (typeof data.detail === "string" && data.detail) {
    return data.detail;
  }
  return fallback;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: "",
    refreshToken: "",
    userEmail: "",
    clientId: "",
    error: "",
    isInitialized: false,
    isInitializing: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
  },
  actions: {
    hydrateFromStorage() {
      const stored = readAuthStorage();
      this.accessToken = normalizeToken(stored.accessToken);
      this.refreshToken = normalizeToken(stored.refreshToken);
      this.userEmail = stored.userEmail;
      this.clientId = stored.clientId;

      if (this.accessToken && (!this.userEmail || !this.clientId)) {
        const restored = buildUserStateFromToken(this.accessToken, stored);
        this.userEmail = restored.userEmail;
        this.clientId = restored.clientId;
        writeAuthStorage({
          accessToken: this.accessToken,
          refreshToken: this.refreshToken,
          userEmail: this.userEmail,
          clientId: this.clientId,
        });
      }
    },

    setAuthState({ accessToken = "", refreshToken = "", userEmail = "", clientId = "" } = {}) {
      this.accessToken = normalizeToken(accessToken);
      this.refreshToken = normalizeToken(refreshToken);
      this.userEmail = userEmail ? String(userEmail) : "";
      this.clientId = clientId ? String(clientId) : "";

      writeAuthStorage({
        accessToken: this.accessToken,
        refreshToken: this.refreshToken,
        userEmail: this.userEmail,
        clientId: this.clientId,
      });
    },

    clearAuth() {
      this.accessToken = "";
      this.refreshToken = "";
      this.userEmail = "";
      this.clientId = "";
      clearAuthStorage();
      clearSubscriptionCache();
    },

    applyAuth(access, refresh, email, clientId = "") {
      const normalizedAccessToken = normalizeToken(access);
      const normalizedRefreshToken = normalizeToken(refresh);
      const restoredFromToken = buildUserStateFromToken(normalizedAccessToken, {
        userEmail: email,
        clientId,
      });

      this.setAuthState({
        accessToken: normalizedAccessToken,
        refreshToken: normalizedRefreshToken,
        userEmail: restoredFromToken.userEmail,
        clientId: restoredFromToken.clientId,
      });
      this.isInitialized = true;
    },

    async refreshAccessToken() {
      const refreshToken = normalizeToken(this.refreshToken || getRefreshToken());
      if (!refreshToken) {
        throw new Error("NO_REFRESH_TOKEN");
      }

      this.refreshToken = refreshToken;

      const response = await api.post(
        "/api/auth/refresh/",
        { refresh: refreshToken },
        {
          _skipAuthRetry: true,
          _skipUnauthorizedLogout: true,
        }
      );

      const nextAccessToken = normalizeToken(response.data?.access || "");
      if (!nextAccessToken) {
        throw new Error("NO_ACCESS_TOKEN_IN_REFRESH_RESPONSE");
      }

      this.applyAuth(nextAccessToken, refreshToken, this.userEmail, this.clientId);
      return nextAccessToken;
    },

    async initializeAuth() {
      if (this.isInitialized && !this.isInitializing) {
        return this.isAuthenticated;
      }

      if (authInitPromise) {
        await authInitPromise;
        return this.isAuthenticated;
      }

      authInitPromise = (async () => {
        this.isInitializing = true;
        this.hydrateFromStorage();

        if (!this.accessToken) {
          if (this.refreshToken) {
            try {
              await this.refreshAccessToken();
            } catch {
              this.clearAuth();
            }
          }

          this.isInitialized = true;
          return;
        }

        if (isJwtExpired(this.accessToken)) {
          if (this.refreshToken) {
            try {
              await this.refreshAccessToken();
            } catch {
              this.clearAuth();
            }
          } else {
            this.clearAuth();
          }
        } else {
          const restored = buildUserStateFromToken(this.accessToken, {
            userEmail: this.userEmail,
            clientId: this.clientId,
          });
          this.setAuthState({
            accessToken: this.accessToken,
            refreshToken: this.refreshToken,
            userEmail: restored.userEmail,
            clientId: restored.clientId,
          });
        }

        this.isInitialized = true;
      })();

      try {
        await authInitPromise;
      } finally {
        this.isInitializing = false;
        authInitPromise = null;
      }

      return this.isAuthenticated;
    },

    bindStorageSync() {
      if (storageSyncAttached || typeof window === "undefined") return;

      window.addEventListener("storage", (event) => {
        if (event.storageArea !== window.localStorage) return;
        if (event.key && !AUTH_STORAGE_KEY_LIST.includes(String(event.key))) return;

        this.hydrateFromStorage();
        this.isInitialized = true;
        if (!this.accessToken && !this.refreshToken) {
          clearSubscriptionCache();
        }
      });

      storageSyncAttached = true;
    },

    async register(email, password, companyName) {
      this.error = "";
      try {
        const response = await api.post("/api/auth/register/", {
          company_name: companyName,
          email,
          password,
        });
        const tokens = response.data?.tokens || {};
        this.applyAuth(tokens.access, tokens.refresh, email, response.data?.user?.client_id || "");
      } catch (error) {
        this.error = extractErrorMessage(error, "Ошибка регистрации.");
        throw error;
      }
    },

    async login(email, password) {
      this.error = "";
      try {
        const response = await api.post("/api/auth/login/", { email, password });
        this.applyAuth(response.data.access, response.data.refresh, email, response.data?.client_id || "");
      } catch (error) {
        this.error = extractErrorMessage(error, "Ошибка входа.");
        throw error;
      }
    },

    async logout(options = {}) {
      const { skipRequest = false } = options;
      try {
        if (!skipRequest && this.accessToken) {
          await api.post(
            "/api/auth/logout/",
            {},
            {
              _skipAuthRetry: true,
              _skipUnauthorizedLogout: true,
            }
          );
        }
      } catch (_) {
        // Stateless logout on frontend side.
      } finally {
        this.clearAuth();
        this.isInitialized = true;
      }
    },
  },
});
