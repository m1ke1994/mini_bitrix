import { ref } from "vue";
import api from "../services/api";

const engagement = ref({
  period: null,
  avg_time_on_page_seconds: 0,
  total_time_on_site_seconds: 0,
  pages: [],
});
const loading = ref(false);
const error = ref("");

async function loadEngagement(params = {}) {
  loading.value = true;
  error.value = "";
  try {
    const response = await api.get("/api/analytics/engagement/", { params });
    engagement.value = {
      period: response.data?.period || null,
      avg_time_on_page_seconds: response.data?.avg_time_on_page_seconds || 0,
      total_time_on_site_seconds: response.data?.total_time_on_site_seconds || 0,
      pages: response.data?.pages || [],
    };
  } catch (err) {
    error.value = "РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё РІРѕРІР»РµС‡РµРЅРЅРѕСЃС‚Рё.";
  } finally {
    loading.value = false;
  }
}

export function useAnalyticsEngagement() {
  return {
    engagement,
    loading,
    error,
    loadEngagement,
  };
}

