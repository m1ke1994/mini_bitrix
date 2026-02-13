import { ref } from "vue";
import api from "../services/api";

const summary = ref({
  visit_count: 0,
  form_submit_count: 0,
  leads_count: 0,
  conversion: 0,
  visits_by_day: [],
  forms_by_day: [],
  leads_by_day: [],
  latest_leads: [],
  avg_time_on_site: 0,
  avg_session_duration: 0,
  avg_scroll_depth: 0,
  total_sessions: 0,
  avg_page_views_per_session: 0,
  top_sources: [],
  source_performance: [],
  conversion_by_pages: [],
  top_clicks: [],
  total_clicks: 0,
});
const loading = ref(false);
const error = ref("");

async function loadSummary() {
  loading.value = true;
  error.value = "";
  try {
    const response = await api.get("/api/analytics/summary/");
    summary.value = {
      ...summary.value,
      ...response.data,
      top_sources: response.data.top_sources || [],
      source_performance: response.data.source_performance || [],
      conversion_by_pages: response.data.conversion_by_pages || [],
      top_clicks: response.data.top_clicks || [],
      latest_leads: response.data.latest_leads || [],
    };
  } catch (_) {
    error.value = "Ошибка загрузки аналитики.";
  } finally {
    loading.value = false;
  }
}

export function useAnalyticsSummary() {
  return {
    summary,
    loading,
    error,
    loadSummary,
  };
}
