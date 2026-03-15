import { ref } from "vue";
import api from "../services/api";

const summary = ref({
  visit_count: 0,
  visitors_unique: 0,
  form_submit_count: 0,
  leads_count: 0,
  conversion: 0,
  visits_by_day: [],
  unique_by_day: [],
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
  total_time_on_site_seconds: 0,
  avg_visit_duration_seconds: 0,
  engagement_pages: [],
  ai_event_signals: {
    scroll_depth: {
      events_total: 0,
      thresholds: { 25: 0, 50: 0, 75: 0, 100: 0 },
    },
    forms: {
      form_view: 0,
      form_start: 0,
      form_first_field_filled: 0,
      form_submit_attempt: 0,
      form_submit_success: 0,
      form_submit_error: 0,
      form_visible: 0,
      form_started: 0,
      form_first_field_completed: 0,
    },
    section_views: { events_total: 0 },
    cta_clicks: { events_total: 0 },
    form_funnel: {
      has_data: false,
      insufficient_data: true,
      rows: [],
    },
    field_analytics: {
      has_data: false,
      insufficient_data: true,
      rows: [],
      first_field_starts: [],
      top_drop_off_field: null,
      top_error_field: null,
      top_revisit_field: null,
    },
    cta_funnel: {
      has_data: false,
      insufficient_data: true,
      rows: [],
    },
    section_analytics: {
      has_data: false,
      insufficient_data: true,
      rows: [],
    },
    device_segmentation: {
      has_data: false,
      insufficient_data: true,
      rows: [],
    },
    source_segmentation: {
      has_data: false,
      insufficient_data: true,
      rows: [],
    },
    micro_conversions: {
      has_data: false,
      insufficient_data: true,
      rows: [],
    },
    anomalies: {
      has_data: false,
      rows: [],
      key_sections: [],
      period: null,
    },
  },
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
      engagement_pages: response.data.engagement_pages || [],
    };
  } catch (err) {
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

