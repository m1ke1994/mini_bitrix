import api from "./api";

export async function fetchPipelines() {
  const response = await api.get("/api/pipelines/");
  return Array.isArray(response.data) ? response.data : [];
}

export async function fetchLeads(params = {}) {
  const response = await api.get("/api/leads/", { params });
  return response.data || {};
}

export async function fetchAllLeads(params = {}) {
  const items = [];
  let nextUrl = "/api/leads/";
  let isFirstRequest = true;

  while (nextUrl) {
    const response =
      String(nextUrl).startsWith("http") || !isFirstRequest
        ? await api.get(nextUrl)
        : await api.get(nextUrl, { params });

    const payload = response.data || {};
    const pageItems = Array.isArray(payload.results) ? payload.results : [];
    items.push(...pageItems);

    nextUrl = payload.next || "";
    isFirstRequest = false;
  }

  return items;
}

export async function moveLead(leadId, stageId) {
  const response = await api.post(`/api/leads/${leadId}/move/`, { stage_id: stageId });
  return response.data;
}

export async function fetchLeadActivities(leadId) {
  const response = await api.get(`/api/leads/${leadId}/activities/`);
  return Array.isArray(response.data) ? response.data : [];
}

export async function addLeadNote(leadId, note) {
  const response = await api.post(`/api/leads/${leadId}/note/`, { note });
  return response.data;
}

export async function scheduleLead(leadId, nextContactAt, note = "") {
  const response = await api.post(`/api/leads/${leadId}/schedule/`, {
    next_contact_at: nextContactAt,
    note,
  });
  return response.data;
}

export async function fetchWidgetVariants() {
  const response = await api.get("/api/widget-variants/");
  const payload = response.data;
  if (Array.isArray(payload)) return payload;
  return Array.isArray(payload?.results) ? payload.results : [];
}

export async function fetchAnalyticsFunnel(params = {}) {
  const response = await api.get("/api/analytics/funnel/", { params });
  return response.data || {};
}

export async function fetchAnalyticsSources(params = {}) {
  const response = await api.get("/api/analytics/sources/", { params });
  return response.data || {};
}

export async function fetchAnalyticsTimeline(params = {}) {
  const response = await api.get("/api/analytics/timeline/", { params });
  return response.data || {};
}

export async function fetchAnalyticsResponseTime(params = {}) {
  const response = await api.get("/api/analytics/response-time/", { params });
  return response.data || {};
}

export async function fetchAnalyticsConversionRate(params = {}) {
  const response = await api.get("/api/analytics/conversion-rate/", { params });
  return response.data || {};
}

export async function fetchAnalyticsHeatmap(params = {}) {
  const response = await api.get("/api/analytics/heatmap/", { params });
  return response.data || {};
}

export async function fetchAiAdvisor(params = {}) {
  const response = await api.get("/api/analytics/ai-advisor/", { params });
  return response.data || {};
}
