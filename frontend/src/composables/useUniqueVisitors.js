import { ref } from "vue";
import api from "../services/api";

const unique = ref({
  total_unique: 0,
  daily: [],
  period: null,
});
const loading = ref(false);
const error = ref("");

async function loadUniqueDaily(params = {}) {
  loading.value = true;
  error.value = "";
  try {
    const response = await api.get("/api/analytics/unique-daily/", { params });
    unique.value = {
      total_unique: response.data?.total_unique || 0,
      daily: response.data?.daily || [],
      period: response.data?.period || null,
    };
  } catch (err) {
    error.value = "Ошибка загрузки уникальных пользователей.";
  } finally {
    loading.value = false;
  }
}

export function useUniqueVisitors() {
  return {
    unique,
    loading,
    error,
    loadUniqueDaily,
  };
}

