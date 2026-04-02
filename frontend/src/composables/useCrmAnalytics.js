import { ref } from "vue";
import {
  fetchAiAdvisor,
  fetchAnalyticsConversionRate,
  fetchAnalyticsFunnel,
  fetchAnalyticsHeatmap,
  fetchAnalyticsResponseTime,
  fetchAnalyticsSources,
  fetchAnalyticsTimeline,
} from "~/services/crm";

function toParams(filters = {}) {
  const params = {};
  if (filters.dateFrom) params.date_from = filters.dateFrom;
  if (filters.dateTo) params.date_to = filters.dateTo;
  if (filters.granularity) params.granularity = filters.granularity;
  return params;
}

export function useCrmAnalytics() {
  const loading = ref(false);
  const error = ref("");

  const funnel = ref({ total_leads: 0, stages: [] });
  const sources = ref({ items: [], top_referrers: [] });
  const timeline = ref({ items: [], granularity: "day" });
  const responseTime = ref({ avg_first_response_seconds: 0, avg_first_response_hours: 0 });
  const conversionRate = ref({ items: [] });
  const heatmap = ref({ items: [] });
  const advisor = ref({ recommendations: [] });

  async function loadAnalytics(filters = {}) {
    loading.value = true;
    error.value = "";
    const params = toParams(filters);

    try {
      const [funnelPayload, sourcesPayload, timelinePayload, responsePayload, conversionPayload, heatmapPayload, advisorPayload] =
        await Promise.all([
          fetchAnalyticsFunnel(params),
          fetchAnalyticsSources(params),
          fetchAnalyticsTimeline(params),
          fetchAnalyticsResponseTime(params),
          fetchAnalyticsConversionRate(params),
          fetchAnalyticsHeatmap(params),
          fetchAiAdvisor(params),
        ]);

      funnel.value = funnelPayload || { total_leads: 0, stages: [] };
      sources.value = sourcesPayload || { items: [], top_referrers: [] };
      timeline.value = timelinePayload || { items: [], granularity: "day" };
      responseTime.value = responsePayload || { avg_first_response_seconds: 0, avg_first_response_hours: 0 };
      conversionRate.value = conversionPayload || { items: [] };
      heatmap.value = heatmapPayload || { items: [] };
      advisor.value = advisorPayload || { recommendations: [] };
    } catch (_error) {
      error.value = "Failed to load CRM analytics.";
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    funnel,
    sources,
    timeline,
    responseTime,
    conversionRate,
    heatmap,
    advisor,
    loadAnalytics,
  };
}
