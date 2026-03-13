<template>
  <section class="dashboard-section seo-audit-page">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="chart-card">
      <div class="card-head">
        <h2>SEO аудит</h2>
      </div>
      <div class="seo-start-row">
        <label class="seo-field">
          <span class="seo-field-label">Домен</span>
          <input
            v-model.trim="domain"
            type="text"
            class="seo-input"
            placeholder="example.com"
            autocomplete="off"
          />
        </label>
        <button
          type="button"
          class="seo-start-btn"
          :class="{ 'is-busy': isInProgress }"
          :disabled="!canStartAudit"
          @click="startAudit"
        >
          {{ starting ? "Запуск..." : "Запустить аудит" }}
        </button>
        <button type="button" class="seo-stop-btn" :disabled="!canStopAudit" @click="stopAudit">
          {{ stopping ? "Остановка..." : "Остановить аудит" }}
        </button>
      </div>
      <p v-if="isInProgress" class="seo-running-indicator" role="status" aria-live="polite">
        <span class="seo-spinner" aria-hidden="true"></span>
        {{ runningHint }}
      </p>
      <p class="muted seo-hint">Аудит обходит до 100 внутренних страниц и выполняется в фоне через Celery.</p>
    </div>

    <div class="stats seo-stats">
      <article class="stat-card">
        <h3>Статус</h3>
        <strong :class="statusClass">{{ statusLabel }}</strong>
      </article>
      <article class="stat-card">
        <h3>SEO-оценка</h3>
        <strong :class="scoreClass">{{ scoreValue }}</strong>
      </article>
      <article class="stat-card">
        <h3>Страниц</h3>
        <strong>{{ audit?.pages_count ?? 0 }}</strong>
      </article>
      <article class="stat-card">
        <h3>Ошибок</h3>
        <strong>{{ errorsCount }}</strong>
      </article>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head">
        <h2>Разбивка ошибок</h2>
      </div>
      <div class="seo-breakdown-grid">
        <article class="seo-breakdown-card seo-breakdown-high">
          <span>Критичные</span>
          <strong>{{ breakdown.high_issues }}</strong>
        </article>
        <article class="seo-breakdown-card seo-breakdown-medium">
          <span>Средние</span>
          <strong>{{ breakdown.medium_issues }}</strong>
        </article>
        <article class="seo-breakdown-card seo-breakdown-low">
          <span>Низкие</span>
          <strong>{{ breakdown.low_issues }}</strong>
        </article>
      </div>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head">
        <h2>Страницы</h2>
        <span class="muted">Аудит #{{ auditId }}</span>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>URL</th>
              <th>Код ответа</th>
              <th>Title</th>
              <th>Длина Title</th>
              <th>Длина Description</th>
              <th>H1</th>
              <th>Количество H1</th>
              <th>Слов</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="page in pages" :key="page.id">
              <td class="url-cell">{{ page.url }}</td>
              <td>{{ page.status_code }}</td>
              <td>{{ page.title || "—" }}</td>
              <td>{{ page.title_length }}</td>
              <td>{{ page.description_length }}</td>
              <td>{{ page.h1 || "—" }}</td>
              <td>{{ page.h1_count }}</td>
              <td>{{ page.word_count }}</td>
            </tr>
            <tr v-if="!pages.length">
              <td colspan="8">Нет данных по страницам</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head">
        <h2>Ошибки</h2>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Страница</th>
              <th>Тип</th>
              <th>Уровень</th>
              <th>Рекомендация</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="issue in issues" :key="issue.id">
              <td class="url-cell">{{ issue.page_url }}</td>
              <td>{{ issueLabel(issue) }}</td>
              <td>
                <span class="severity-pill" :class="`severity-${issue.severity}`">
                  {{ severityLabel(issue.severity) }}
                </span>
              </td>
              <td>{{ issue.recommendation }}</td>
            </tr>
            <tr v-if="!issues.length">
              <td colspan="4">Ошибок не найдено</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import api from "../services/api";

const STORAGE_AUDIT_ID_KEY = "tracknode:seo:lastAuditId";
const STORAGE_DOMAIN_KEY = "tracknode:seo:lastDomain";
const POLL_INTERVAL_MS = 5000;

const auditId = ref(null);
const audit = ref(null);
const domain = ref("");
const error = ref("");
const loading = ref(false);
const starting = ref(false);
const stopping = ref(false);
const bootstrapping = ref(false);

let pollTimer = null;

const pages = computed(() => (Array.isArray(audit.value?.pages) ? audit.value.pages : []));
const groupedErrors = computed(() => {
  const grouped = audit.value?.grouped_errors || {};
  return {
    high: Array.isArray(grouped.high) ? grouped.high : [],
    medium: Array.isArray(grouped.medium) ? grouped.medium : [],
    low: Array.isArray(grouped.low) ? grouped.low : [],
  };
});
const issues = computed(() => {
  if (Array.isArray(audit.value?.errors)) return audit.value.errors;
  return [...groupedErrors.value.high, ...groupedErrors.value.medium, ...groupedErrors.value.low];
});
const breakdown = computed(() => {
  const payload = audit.value?.breakdown;
  if (payload && typeof payload === "object") {
    return {
      score: Number(payload.score ?? audit.value?.score ?? 0) || 0,
      high_issues: Number(payload.high_issues ?? 0) || 0,
      medium_issues: Number(payload.medium_issues ?? 0) || 0,
      low_issues: Number(payload.low_issues ?? 0) || 0,
    };
  }
  let high = 0;
  let medium = 0;
  let low = 0;
  for (const issue of issues.value) {
    const severity = String(issue?.severity || "").toLowerCase();
    if (severity === "high") high += 1;
    if (severity === "medium") medium += 1;
    if (severity === "low") low += 1;
  }
  return {
    score: Number(audit.value?.score ?? audit.value?.seo_score ?? 0) || 0,
    high_issues: high,
    medium_issues: medium,
    low_issues: low,
  };
});
const scoreValue = computed(() => Number(audit.value?.score ?? audit.value?.seo_score ?? 0) || 0);
const errorsCount = computed(
  () => breakdown.value.high_issues + breakdown.value.medium_issues + breakdown.value.low_issues,
);
const rawStatus = computed(() => String(audit.value?.status || "idle").trim().toLowerCase());
const isInProgress = computed(() => rawStatus.value === "pending" || rawStatus.value === "running");
const canStartAudit = computed(
  () =>
    Boolean(domain.value) &&
    !starting.value &&
    !stopping.value &&
    !loading.value &&
    !bootstrapping.value &&
    !isInProgress.value,
);
const canStopAudit = computed(
  () => Boolean(auditId.value) && !starting.value && !stopping.value && !bootstrapping.value && isInProgress.value,
);
const runningHint = computed(() => (rawStatus.value === "pending" ? "Аудит в очереди..." : "Аудит выполняется..."));
const scoreClass = computed(() => {
  const score = scoreValue.value;
  if (score <= 40) return "seo-score-bad";
  if (score <= 70) return "seo-score-warn";
  return "seo-score-good";
});

const statusLabel = computed(() => {
  const labels = {
    idle: "Не запускался",
    pending: "В очереди",
    running: "Выполняется",
    done: "Готово",
    error: "Ошибка",
    stopped: "Остановлено",
  };
  return labels[rawStatus.value] || rawStatus.value;
});

const statusClass = computed(() => {
  if (rawStatus.value === "done") return "status-done";
  if (rawStatus.value === "error") return "status-error";
  if (rawStatus.value === "stopped") return "status-stopped";
  if (rawStatus.value === "pending" || rawStatus.value === "running") return "status-running";
  return "status-idle";
});

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function severityLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "high") return "Критичный";
  if (key === "medium") return "Средний";
  if (key === "low") return "Низкий";
  return "—";
}

function issueLabel(issue) {
  return String(issue?.issue_title || "").trim() || "SEO-ошибка";
}

function persistState() {
  if (!canUseStorage()) return;
  try {
    if (auditId.value) {
      window.localStorage.setItem(STORAGE_AUDIT_ID_KEY, String(auditId.value));
    }
    window.localStorage.setItem(STORAGE_DOMAIN_KEY, String(domain.value || ""));
  } catch {
    // Ignore localStorage errors.
  }
}

function restoreState() {
  if (!canUseStorage()) return;
  try {
    const storedId = String(window.localStorage.getItem(STORAGE_AUDIT_ID_KEY) || "").trim();
    const storedDomain = String(window.localStorage.getItem(STORAGE_DOMAIN_KEY) || "").trim();
    if (storedDomain) {
      domain.value = storedDomain;
    }
    if (/^\d+$/.test(storedId)) {
      auditId.value = Number(storedId);
    }
  } catch {
    // Ignore localStorage errors.
  }
}

function stopPolling() {
  if (pollTimer) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
}

function schedulePollingIfNeeded() {
  stopPolling();
  if (!auditId.value) return;
  if (!isInProgress.value) return;
  pollTimer = setTimeout(() => {
    void loadAudit({ silent: true });
  }, POLL_INTERVAL_MS);
}

async function startAudit() {
  if (!canStartAudit.value) return;
  error.value = "";
  starting.value = true;
  stopPolling();
  try {
    const { data } = await api.post("/api/seo/start/", { domain: domain.value });
    auditId.value = Number(data?.audit_id || 0) || null;
    if (data?.domain) {
      domain.value = String(data.domain);
    }
    persistState();
    await loadAudit();
  } catch (e) {
    error.value =
      e?.response?.data?.detail ||
      (Array.isArray(e?.response?.data?.domain) ? e.response.data.domain[0] : "") ||
      "Не удалось запустить аудит.";
  } finally {
    starting.value = false;
  }
}

async function loadAudit({ silent = false } = {}) {
  if (!auditId.value) return;
  if (!silent) loading.value = true;
  error.value = "";
  try {
    const { data } = await api.get(`/api/seo/${auditId.value}/`);
    audit.value = data || null;
    if (data?.domain && !domain.value) {
      domain.value = String(data.domain);
    }
    persistState();
  } catch (e) {
    error.value = e?.response?.data?.detail || "Не удалось загрузить результат аудита.";
  } finally {
    if (!silent) loading.value = false;
    schedulePollingIfNeeded();
  }
}

async function stopAudit() {
  if (!canStopAudit.value) return;
  stopping.value = true;
  error.value = "";
  stopPolling();
  try {
    const { data } = await api.post(`/api/seo/${auditId.value}/stop/`);
    audit.value = {
      ...(audit.value || {}),
      id: auditId.value,
      status: String(data?.status || "stopped"),
      finished_at: data?.finished_at ?? audit.value?.finished_at ?? null,
      pages: Array.isArray(audit.value?.pages) ? audit.value.pages : [],
      errors: Array.isArray(audit.value?.errors) ? audit.value.errors : [],
      grouped_errors:
        audit.value?.grouped_errors && typeof audit.value.grouped_errors === "object"
          ? audit.value.grouped_errors
          : { high: [], medium: [], low: [] },
      breakdown:
        audit.value?.breakdown && typeof audit.value.breakdown === "object"
          ? audit.value.breakdown
          : {
              score: Number(audit.value?.score ?? audit.value?.seo_score ?? 0) || 0,
              high_issues: 0,
              medium_issues: 0,
              low_issues: 0,
            },
    };
    await loadAudit({ silent: true });
  } catch (e) {
    error.value = e?.response?.data?.detail || "Не удалось остановить аудит.";
  } finally {
    stopping.value = false;
  }
}

async function manualRefresh() {
  await loadAudit();
}

defineExpose({ manualRefresh });

onMounted(() => {
  restoreState();
  if (!auditId.value) return;
  bootstrapping.value = true;
  void loadAudit({ silent: true }).finally(() => {
    bootstrapping.value = false;
  });
});

onBeforeUnmount(() => {
  stopPolling();
});
</script>

<style scoped>
.seo-start-row {
  display: grid;
  grid-template-columns: minmax(16rem, 30rem) auto auto;
  gap: 0.75rem;
  align-items: end;
}

.seo-field {
  display: grid;
  gap: 0.35rem;
}

.seo-field-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-muted);
}

.seo-input {
  min-height: 2.6rem;
  border-radius: 0.65rem;
  border: 1px solid var(--color-border);
  padding: 0.5rem 0.75rem;
  font: inherit;
}

.seo-start-btn,
.seo-stop-btn {
  min-height: 2.6rem;
  border-radius: 0.65rem;
  border: 1px solid var(--color-border);
  padding: 0 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.seo-start-btn {
  border-color: transparent;
  color: #fff;
  background: linear-gradient(135deg, #0284c7, #2563eb);
}

.seo-start-btn.is-busy {
  background: linear-gradient(135deg, #64748b, #334155);
}

.seo-stop-btn {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
  font-weight: 700;
}

.seo-start-btn:disabled,
.seo-stop-btn:disabled {
  opacity: 0.65;
  cursor: default;
}

.seo-running-indicator {
  margin: 0.7rem 0 0;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #1d4ed8;
  font-weight: 600;
}

.seo-spinner {
  width: 0.95rem;
  height: 0.95rem;
  border-radius: 999px;
  border: 2px solid #bfdbfe;
  border-top-color: #1d4ed8;
  animation: seo-spin 0.9s linear infinite;
}

.seo-hint {
  margin: 0.7rem 0 0;
}

.seo-stats {
  margin-top: 16px;
}

.seo-breakdown-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.seo-breakdown-card {
  border: 1px solid var(--color-border);
  border-radius: 0.8rem;
  padding: 0.85rem;
  display: grid;
  gap: 0.35rem;
}

.seo-breakdown-card span {
  font-size: 0.82rem;
  color: var(--color-muted);
  font-weight: 600;
}

.seo-breakdown-card strong {
  font-size: 1.35rem;
}

.seo-breakdown-high {
  background: #fff7f7;
}

.seo-breakdown-medium {
  background: #fffaf0;
}

.seo-breakdown-low {
  background: #f5fbf6;
}

.url-cell {
  max-width: 20rem;
  word-break: break-word;
}

.severity-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 4.8rem;
  border-radius: 999px;
  padding: 0.15rem 0.5rem;
  font-size: 0.78rem;
  font-weight: 700;
}

.severity-high {
  color: #991b1b;
  background: #fee2e2;
}

.severity-medium {
  color: #92400e;
  background: #fef3c7;
}

.severity-low {
  color: #166534;
  background: #dcfce7;
}

.status-done {
  color: #15803d;
}

.status-error {
  color: #b91c1c;
}

.status-running {
  color: #1d4ed8;
}

.status-stopped {
  color: #b45309;
}

.status-idle {
  color: #6b7280;
}

.seo-score-bad {
  color: #b91c1c;
}

.seo-score-warn {
  color: #b45309;
}

.seo-score-good {
  color: #15803d;
}

@keyframes seo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .seo-start-row {
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .seo-breakdown-grid {
    grid-template-columns: 1fr;
  }
}
</style>
