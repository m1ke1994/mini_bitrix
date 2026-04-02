import api from "./api";

function unwrapEnvelope(data) {
  if (!data || typeof data !== "object") return data;
  if (Array.isArray(data)) return data;
  if (data.payload && typeof data.payload === "object") return data.payload;
  if (data.data && typeof data.data === "object") return data.data;
  return data;
}

function normalizeListResponse(data) {
  const payload = unwrapEnvelope(data);
  if (Array.isArray(payload)) {
    return {
      items: payload,
      next: "",
    };
  }

  const results = Array.isArray(payload?.results)
    ? payload.results
    : Array.isArray(payload?.items)
      ? payload.items
      : [];

  return {
    items: results,
    next: String(payload?.next || ""),
  };
}

function normalizeObjectResponse(data, fallback) {
  const payload = unwrapEnvelope(data);
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return fallback;
  return payload;
}

export async function fetchPipelines() {
  const response = await api.get("/api/pipelines/");
  const { items } = normalizeListResponse(response.data);
  return items;
}

export async function fetchLeads(params = {}) {
  const response = await api.get("/api/leads/", { params });
  const payload = unwrapEnvelope(response.data);

  if (Array.isArray(payload)) {
    return {
      count: payload.length,
      next: null,
      previous: null,
      results: payload,
    };
  }

  return normalizeObjectResponse(payload, { count: 0, next: null, previous: null, results: [] });
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

    const page = normalizeListResponse(response.data);
    items.push(...page.items);
    nextUrl = page.next;
    isFirstRequest = false;
  }

  return items;
}

export async function moveLead(leadId, stageId) {
  const response = await api.post(`/api/leads/${leadId}/move/`, { stage_id: stageId });
  return unwrapEnvelope(response.data) || {};
}

export async function fetchLeadActivities(leadId) {
  const response = await api.get(`/api/leads/${leadId}/activities/`);
  const payload = unwrapEnvelope(response.data);
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

export async function addLeadNote(leadId, note) {
  const response = await api.post(`/api/leads/${leadId}/note/`, { note });
  return unwrapEnvelope(response.data) || {};
}

export async function scheduleLead(leadId, nextContactAt, note = "") {
  const response = await api.post(`/api/leads/${leadId}/schedule/`, {
    next_contact_at: nextContactAt,
    note,
  });
  return unwrapEnvelope(response.data) || {};
}

export async function fetchWidgetVariants() {
  const response = await api.get("/api/widget-variants/");
  const payload = unwrapEnvelope(response.data);
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.items)) return payload.items;
  return [];
}

export async function fetchAnalyticsFunnel(params = {}) {
  const response = await api.get("/api/analytics/funnel/", { params });
  return normalizeObjectResponse(response.data, { total_leads: 0, stages: [] });
}

export async function fetchAnalyticsSources(params = {}) {
  const response = await api.get("/api/analytics/sources/", { params });
  return normalizeObjectResponse(response.data, { items: [], top_referrers: [] });
}

export async function fetchAnalyticsTimeline(params = {}) {
  const response = await api.get("/api/analytics/timeline/", { params });
  return normalizeObjectResponse(response.data, { items: [], granularity: "day" });
}

export async function fetchAnalyticsResponseTime(params = {}) {
  const response = await api.get("/api/analytics/response-time/", { params });
  return normalizeObjectResponse(response.data, { avg_first_response_seconds: 0, avg_first_response_hours: 0 });
}

export async function fetchAnalyticsConversionRate(params = {}) {
  const response = await api.get("/api/analytics/conversion-rate/", { params });
  return normalizeObjectResponse(response.data, { items: [] });
}

export async function fetchAnalyticsHeatmap(params = {}) {
  const response = await api.get("/api/analytics/heatmap/", { params });
  return normalizeObjectResponse(response.data, { items: [] });
}

export async function fetchAiAdvisor(params = {}) {
  const response = await api.get("/api/analytics/ai-advisor/", { params });
  return normalizeObjectResponse(response.data, { recommendations: [] });
}
