import { defineStore } from "pinia";
import api from "../services/api";

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
    accessToken: localStorage.getItem("accessToken") || "",
    refreshToken: localStorage.getItem("refreshToken") || "",
    userEmail: localStorage.getItem("userEmail") || "",
    error: "",
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
  },
  actions: {
    applyAuth(access, refresh, email) {
      this.accessToken = access || "";
      this.refreshToken = refresh || "";
      this.userEmail = email || "";
      localStorage.setItem("accessToken", this.accessToken);
      localStorage.setItem("refreshToken", this.refreshToken);
      localStorage.setItem("userEmail", this.userEmail);
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
        this.applyAuth(tokens.access, tokens.refresh, email);
      } catch (error) {
        this.error = extractErrorMessage(error, "Ошибка регистрации.");
        throw error;
      }
    },
    async login(email, password) {
      this.error = "";
      try {
        const response = await api.post("/api/auth/login/", { email, password });
        this.applyAuth(response.data.access, response.data.refresh, email);
      } catch (error) {
        this.error = extractErrorMessage(error, "Ошибка входа.");
        throw error;
      }
    },
    async logout() {
      try {
        if (this.accessToken) {
          await api.post("/api/auth/logout/");
        }
      } catch (_) {
        // Stateless logout on frontend side.
      } finally {
        this.accessToken = "";
        this.refreshToken = "";
        this.userEmail = "";
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("userEmail");
      }
    },
  },
});
