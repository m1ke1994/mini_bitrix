import { ref } from "vue";
import api from "../services/api";

const overview = ref({
  visits_total: 0,
  visitors_unique: 0,
  forms_total: 0,
  leads_total: 0,
  notifications_sent_total: 0,
  conversion: 0,
});
const loading = ref(false);
const error = ref("");

async function loadOverview(params = {}) {
  loading.value = true;
  error.value = "";
  try {
    const response = await api.get("/api/analytics/overview/", { params });
    console.log("[analytics] /api/analytics/overview response", response.data);
    overview.value = {
      ...overview.value,
      ...response.data,
    };
  } catch (err) {
    console.log("[analytics] /api/analytics/overview error", err?.response?.data || err);
    error.value = "Ошибка загрузки overview.";
  } finally {
    loading.value = false;
  }
}

export function useAnalyticsOverview() {
  return {
    overview,
    loading,
    error,
    loadOverview,
  };
}
