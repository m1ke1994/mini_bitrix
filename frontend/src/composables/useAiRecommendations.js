import { ref } from "vue";

import api from "../services/api";

function buildFallback({ title, summary }) {
  return {
    success: false,
    source: "fallback",
    fallback: true,
    title,
    summary,
    items: [],
    priority: "medium",
    user_message: summary,
    cached: false,
  };
}

function normalizePriority(value) {
  const normalized = String(value || "").trim().toLowerCase();
  if (normalized === "high" || normalized === "medium" || normalized === "low") {
    return normalized;
  }
  return "medium";
}

function normalizeItems(items) {
  if (!Array.isArray(items)) return [];
  return items
    .map((item) => String(item || "").trim())
    .filter((item) => Boolean(item))
    .slice(0, 7);
}

function normalizePayload(payload, fallback) {
  if (!payload || typeof payload !== "object") return fallback;
  const title = String(payload.title || "").trim() || fallback.title;
  const summary = String(payload.summary || "").trim() || fallback.summary;
  const items = normalizeItems(payload.items);
  const source = String(payload.source || fallback.source).trim().toLowerCase() || fallback.source;
  const fallbackMode = Boolean(payload.fallback) || source === "fallback";
  const userMessage = String(payload.user_message || "").trim();
  return {
    ...fallback,
    ...payload,
    title,
    summary,
    items,
    priority: normalizePriority(payload.priority),
    success: Boolean(payload.success),
    source,
    fallback: fallbackMode,
    user_message: userMessage || summary,
    cached: Boolean(payload.cached),
  };
}

export function useAiRecommendations(options = {}) {
  const {
    endpoint = "",
    fallbackTitle = "Рекомендации временно недоступны",
    fallbackSummary = "Не удалось получить AI-анализ. Попробуйте позже.",
  } = options;

  const fallback = buildFallback({ title: fallbackTitle, summary: fallbackSummary });
  const recommendations = ref(fallback);
  const loading = ref(false);
  const error = ref("");

  function resolveEndpoint() {
    return typeof endpoint === "function" ? endpoint() : endpoint;
  }

  function resetAiRecommendations() {
    recommendations.value = { ...fallback };
    error.value = "";
  }

  async function loadAiRecommendations({ force = false, params = {} } = {}) {
    const targetEndpoint = String(resolveEndpoint() || "").trim();
    if (!targetEndpoint) {
      resetAiRecommendations();
      return recommendations.value;
    }

    loading.value = true;
    error.value = "";
    try {
      const finalParams = { ...(params || {}) };
      if (force) finalParams.refresh = 1;
      const { data } = await api.get(targetEndpoint, { params: finalParams });
      recommendations.value = normalizePayload(data, fallback);
      return recommendations.value;
    } catch (e) {
      error.value = e?.response?.data?.detail || "Не удалось загрузить AI-рекомендации.";
      recommendations.value = { ...fallback };
      return recommendations.value;
    } finally {
      loading.value = false;
    }
  }

  return {
    recommendations,
    loading,
    error,
    loadAiRecommendations,
    resetAiRecommendations,
  };
}
