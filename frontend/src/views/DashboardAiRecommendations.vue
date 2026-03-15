<template>
  <section class="dashboard-section">
    <div class="chart-card">
      <div class="card-head ai-head">
        <h2>AI рекомендации</h2>
        <span class="badge">Этап 1+</span>
      </div>
      <p class="muted">
        Раздел подготовлен под будущий модуль рекомендаций. Сейчас собираются события, которые станут входными данными
        для AI-аналитики.
      </p>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted loading-note">Обновление данных...</p>

    <div class="stats">
      <article class="stat-card">
        <h3>Скролл-события</h3>
        <p class="muted metric-help">
          Скролл-события — сколько раз пользователи достигали порогов прокрутки страницы.
        </p>
        <strong>{{ scrollEventsTotal }}</strong>
      </article>
      <article class="stat-card">
        <h3>Шаги формы</h3>
        <p class="muted metric-help">
          Шаги формы — этапы взаимодействия с формой: от просмотра до отправки.
        </p>
        <strong>{{ formStepsTotal }}</strong>
      </article>
      <article class="stat-card">
        <h3>Просмотры секций</h3>
        <p class="muted metric-help">
          Просмотры секций — сколько раз ключевые блоки страницы попадали в видимую область.
        </p>
        <strong>{{ sectionViewsTotal }}</strong>
      </article>
      <article class="stat-card">
        <h3>CTA-клики</h3>
        <p class="muted metric-help">
          CTA-клики — клики по целевым кнопкам и важным действиям на странице.
        </p>
        <strong>{{ ctaClicksTotal }}</strong>
      </article>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Скролл-глубина по порогам</h2>
      </div>
      <p class="muted block-help">
        Скролл-глубина показывает, до какого процента страницы обычно доходят пользователи.
      </p>
      <div class="thresholds-grid">
        <div class="threshold-item">
          <span class="threshold-title">25%</span>
          <span class="muted threshold-help">Дошли до четверти страницы</span>
          <strong>{{ scrollThreshold(25) }}</strong>
        </div>
        <div class="threshold-item">
          <span class="threshold-title">50%</span>
          <span class="muted threshold-help">Дошли до середины страницы</span>
          <strong>{{ scrollThreshold(50) }}</strong>
        </div>
        <div class="threshold-item">
          <span class="threshold-title">75%</span>
          <span class="muted threshold-help">Дошли до трёх четвертей страницы</span>
          <strong>{{ scrollThreshold(75) }}</strong>
        </div>
        <div class="threshold-item">
          <span class="threshold-title">100%</span>
          <span class="muted threshold-help">Дошли до конца страницы</span>
          <strong>{{ scrollThreshold(100) }}</strong>
        </div>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>События форм</h2>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Событие</th>
              <th>Что означает</th>
              <th>Количество</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Форма в зоне видимости</td>
              <td class="muted">Форма была показана пользователю на экране.</td>
              <td>{{ formVisibleCount }}</td>
            </tr>
            <tr>
              <td>Старт взаимодействия</td>
              <td class="muted">Пользователь начал работать с формой.</td>
              <td>{{ formStartedCount }}</td>
            </tr>
            <tr>
              <td>Первое заполненное поле</td>
              <td class="muted">Пользователь впервые ввёл данные в поле формы.</td>
              <td>{{ formFirstFieldCompletedCount }}</td>
            </tr>
            <tr>
              <td>Попытка отправки</td>
              <td class="muted">Пользователь попытался отправить форму.</td>
              <td>{{ formSubmitAttemptCount }}</td>
            </tr>
            <tr>
              <td>Успешная отправка</td>
              <td class="muted">Форма была отправлена без ошибки.</td>
              <td>{{ formSubmitSuccessCount }}</td>
            </tr>
            <tr>
              <td>Ошибка отправки</td>
              <td class="muted">При отправке формы возникла ошибка.</td>
              <td>{{ formSubmitErrorCount }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Воронка формы</h2>
      </div>
      <p v-if="showFormFunnelEmpty" class="muted">Недостаточно данных</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Этап</th>
              <th>Пользователи</th>
              <th>Переход к следующему шагу</th>
              <th>От первого шага</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in formFunnelRows" :key="row.stage">
              <td>{{ formStageLabel(row.stage) }}</td>
              <td>{{ row.users || 0 }}</td>
              <td>{{ formatPercent(row.next_step_rate_pct) }}</td>
              <td>{{ formatPercent(row.from_first_step_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Аналитика полей формы</h2>
      </div>
      <p v-if="showFieldAnalyticsEmpty" class="muted">Недостаточно данных</p>
      <template v-else>
        <div class="field-highlights">
          <span class="muted">Первое поле старта: <strong>{{ firstFieldStartedLabel }}</strong></span>
          <span class="muted">Чаще отваливаются на: <strong>{{ topDropOffLabel }}</strong></span>
          <span class="muted">Больше ошибок на: <strong>{{ topErrorLabel }}</strong></span>
          <span class="muted">Чаще возвращаются к: <strong>{{ topRevisitLabel }}</strong></span>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Поле</th>
                <th>Начали ввод</th>
                <th>Завершили</th>
                <th>Ошибки</th>
                <th>Повторные возвраты</th>
                <th>Completion rate</th>
                <th>Drop-off (упрощ.)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in fieldRows" :key="row.field_key">
                <td>{{ fieldLabel(row) }}</td>
                <td>{{ row.started || 0 }}</td>
                <td>{{ row.completed || 0 }}</td>
                <td>{{ row.errors || 0 }}</td>
                <td>{{ row.revisits || 0 }}</td>
                <td>{{ formatPercent(row.completion_rate_pct) }}</td>
                <td>{{ row.drop_off || 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>CTA-воронка</h2>
      </div>
      <p v-if="showCtaFunnelEmpty" class="muted">Недостаточно данных</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>CTA</th>
              <th>Показы</th>
              <th>Клики</th>
              <th>Reach target</th>
              <th>Конверсии</th>
              <th>CTR</th>
              <th>Click-to-conversion</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in ctaRows" :key="row.cta_id">
              <td>{{ ctaLabel(row) }}</td>
              <td>{{ row.shows || 0 }}</td>
              <td>{{ row.clicks || 0 }}</td>
              <td>{{ row.target_reached || 0 }}</td>
              <td>{{ row.conversions || 0 }}</td>
              <td>{{ formatPercent(row.ctr_pct) }}</td>
              <td>{{ formatPercent(row.click_to_conversion_rate_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Аналитика секций</h2>
      </div>
      <p v-if="showSectionAnalyticsEmpty" class="muted">Недостаточно данных</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Секция</th>
              <th>Просмотры</th>
              <th>Среднее время</th>
              <th>CTA после секции</th>
              <th>Старт формы после секции</th>
              <th>Конверсии после секции</th>
              <th>Exit after section</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sectionRows" :key="row.section_id">
              <td>{{ row.section_name || row.section_id }}</td>
              <td>{{ row.views || 0 }}</td>
              <td>{{ formatSeconds(row.avg_time_spent_seconds) }}</td>
              <td>{{ row.cta_after_section || 0 }}</td>
              <td>{{ row.form_start_after_section || 0 }}</td>
              <td>{{ row.conversions_after_section || 0 }}</td>
              <td>{{ formatPercent(row.exit_after_section_rate_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Сегментация по устройствам</h2>
      </div>
      <p v-if="showDeviceSegmentationEmpty" class="muted">Недостаточно данных</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Устройство</th>
              <th>Сессии</th>
              <th>Скролл-события</th>
              <th>CTA-клики</th>
              <th>Старт формы</th>
              <th>Успешные отправки</th>
              <th>Конверсия формы</th>
              <th>Средняя глубина скролла</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in deviceRows" :key="row.device">
              <td>{{ row.device }}</td>
              <td>{{ row.sessions || 0 }}</td>
              <td>{{ row.scroll_events || 0 }}</td>
              <td>{{ row.cta_clicks || 0 }}</td>
              <td>{{ row.form_starts || 0 }}</td>
              <td>{{ row.form_submit_success || 0 }}</td>
              <td>{{ formatPercent(row.form_conversion_rate_pct) }}</td>
              <td>{{ formatPercent(row.avg_scroll_depth) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Сегментация по источникам</h2>
      </div>
      <p v-if="showSourceSegmentationEmpty" class="muted">Недостаточно данных</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Источник</th>
              <th>Сессии</th>
              <th>Средняя глубина скролла</th>
              <th>CTA CTR</th>
              <th>Начало формы</th>
              <th>Успешные отправки</th>
              <th>Conversion rate</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sourceRows" :key="row.source">
              <td>{{ row.source }}</td>
              <td>{{ row.sessions || 0 }}</td>
              <td>{{ formatPercent(row.avg_scroll_depth) }}</td>
              <td>{{ formatPercent(row.cta_ctr_pct) }}</td>
              <td>{{ row.form_starts || 0 }}</td>
              <td>{{ row.form_submit_success || 0 }}</td>
              <td>{{ formatPercent(row.conversion_rate_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Микроконверсии</h2>
      </div>
      <p v-if="showMicroConversionsEmpty" class="muted">Недостаточно данных</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Событие</th>
              <th>Количество</th>
              <th>Уникальные пользователи</th>
              <th>Связанная страница</th>
              <th>Связанная секция</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in microRows" :key="row.event">
              <td>{{ row.event }}</td>
              <td>{{ row.count || 0 }}</td>
              <td>{{ row.unique_users || 0 }}</td>
              <td>{{ row.page || '—' }}</td>
              <td>{{ row.section || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Аномалии</h2>
      </div>
      <p v-if="showAnomaliesEmpty" class="muted">Недостаточно данных</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Метрика</th>
              <th>Текущее</th>
              <th>Предыдущее</th>
              <th>Изменение</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in anomalyRows" :key="row.metric">
              <td>{{ row.label || row.metric }}</td>
              <td>{{ row.current_value ?? 0 }}</td>
              <td>{{ row.previous_value ?? 0 }}</td>
              <td>{{ formatSignedPercent(row.change_pct) }}</td>
              <td>
                <span class="status-badge" :class="anomalyStatusClass(row.status)">
                  {{ anomalyStatusLabel(row.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from "vue";

import { useAnalyticsSummary } from "../composables/useAnalyticsSummary";

const { summary, error, loading, loadSummary } = useAnalyticsSummary();

const aiSignals = computed(() => summary.value.ai_event_signals || {});
const scrollSignals = computed(() => aiSignals.value.scroll_depth || {});
const formSignals = computed(() => aiSignals.value.forms || {});

const formVisibleCount = computed(() => Number(formSignals.value.form_visible || formSignals.value.form_view || 0));
const formStartedCount = computed(() => Number(formSignals.value.form_started || formSignals.value.form_start || 0));
const formFirstFieldCompletedCount = computed(() =>
  Number(formSignals.value.form_first_field_completed || formSignals.value.form_first_field_filled || 0)
);
const formSubmitAttemptCount = computed(() => Number(formSignals.value.form_submit_attempt || 0));
const formSubmitSuccessCount = computed(() => Number(formSignals.value.form_submit_success || 0));
const formSubmitErrorCount = computed(() => Number(formSignals.value.form_submit_error || 0));

const formFunnel = computed(() => aiSignals.value.form_funnel || { has_data: false, rows: [] });
const fieldAnalytics = computed(() => aiSignals.value.field_analytics || { has_data: false, rows: [] });
const ctaFunnel = computed(() => aiSignals.value.cta_funnel || { has_data: false, rows: [] });
const sectionAnalytics = computed(() => aiSignals.value.section_analytics || { has_data: false, rows: [] });
const deviceSegmentation = computed(() => aiSignals.value.device_segmentation || { has_data: false, rows: [] });
const sourceSegmentation = computed(() => aiSignals.value.source_segmentation || { has_data: false, rows: [] });
const microConversions = computed(() => aiSignals.value.micro_conversions || { has_data: false, rows: [] });
const anomalies = computed(() => aiSignals.value.anomalies || { has_data: false, rows: [] });

const formFunnelRows = computed(() => formFunnel.value.rows || []);
const fieldRows = computed(() => fieldAnalytics.value.rows || []);
const ctaRows = computed(() => ctaFunnel.value.rows || []);
const sectionRows = computed(() => sectionAnalytics.value.rows || []);
const deviceRows = computed(() => deviceSegmentation.value.rows || []);
const sourceRows = computed(() => sourceSegmentation.value.rows || []);
const microRows = computed(() => microConversions.value.rows || []);
const anomalyRows = computed(() => anomalies.value.rows || []);

const showFormFunnelEmpty = computed(() => !loading.value && (!formFunnel.value.has_data || !formFunnelRows.value.length));
const showFieldAnalyticsEmpty = computed(() => !loading.value && (!fieldAnalytics.value.has_data || !fieldRows.value.length));
const showCtaFunnelEmpty = computed(() => !loading.value && (!ctaFunnel.value.has_data || !ctaRows.value.length));
const showSectionAnalyticsEmpty = computed(() =>
  !loading.value && (!sectionAnalytics.value.has_data || !sectionRows.value.length)
);
const showDeviceSegmentationEmpty = computed(() =>
  !loading.value && (!deviceSegmentation.value.has_data || !deviceRows.value.length)
);
const showSourceSegmentationEmpty = computed(() =>
  !loading.value && (!sourceSegmentation.value.has_data || !sourceRows.value.length)
);
const showMicroConversionsEmpty = computed(() =>
  !loading.value && (!microConversions.value.has_data || !microRows.value.length)
);
const showAnomaliesEmpty = computed(() => !loading.value && (!anomalies.value.has_data || !anomalyRows.value.length));

const scrollEventsTotal = computed(() => Number(scrollSignals.value.events_total || 0));
const formStepsTotal = computed(() =>
  formVisibleCount.value +
  formStartedCount.value +
  formFirstFieldCompletedCount.value +
  formSubmitAttemptCount.value +
  formSubmitSuccessCount.value +
  formSubmitErrorCount.value
);
const sectionViewsTotal = computed(() => Number(aiSignals.value.section_views?.events_total || 0));
const ctaClicksTotal = computed(() => Number(aiSignals.value.cta_clicks?.events_total || 0));

const firstFieldStartedLabel = computed(() => {
  const item = fieldAnalytics.value.first_field_starts?.[0];
  if (!item) return "—";
  return `${item.field_name || "поле"}${item.form_id ? ` (${item.form_id})` : ""}`;
});

const topDropOffLabel = computed(() => {
  const item = fieldAnalytics.value.top_drop_off_field;
  if (!item) return "—";
  return `${item.field_name || "поле"} (${item.count || 0})`;
});

const topErrorLabel = computed(() => {
  const item = fieldAnalytics.value.top_error_field;
  if (!item) return "—";
  return `${item.field_name || "поле"} (${item.count || 0})`;
});

const topRevisitLabel = computed(() => {
  const item = fieldAnalytics.value.top_revisit_field;
  if (!item) return "—";
  return `${item.field_name || "поле"} (${item.count || 0})`;
});

function scrollThreshold(level) {
  return Number(scrollSignals.value.thresholds?.[String(level)] || scrollSignals.value.thresholds?.[level] || 0);
}

function formStageLabel(stage) {
  const labels = {
    form_visible: "Увидели форму",
    form_started: "Начали заполнение",
    form_first_field_completed: "Заполнили первое поле",
    form_submit_attempt: "Попытались отправить",
    form_submit_success: "Успешно отправили",
    form_submit_error: "Ошибка отправки",
  };
  return labels[stage] || stage;
}

function fieldLabel(row) {
  if (!row) return "—";
  const name = row.field_name || "поле";
  const type = row.field_type || "unknown";
  const formId = row.form_id || "form";
  return `${name} (${type}, ${formId})`;
}

function ctaLabel(row) {
  if (!row) return "—";
  if (row.cta_text) {
    return `${row.cta_text}${row.cta_type ? ` (${row.cta_type})` : ""}`;
  }
  return `${row.cta_id || "cta"}${row.cta_type ? ` (${row.cta_type})` : ""}`;
}

function formatPercent(value) {
  const normalized = Number(value || 0);
  return `${normalized.toFixed(2)}%`;
}

function formatSignedPercent(value) {
  const normalized = Number(value || 0);
  const sign = normalized > 0 ? "+" : "";
  return `${sign}${normalized.toFixed(2)}%`;
}

function formatSeconds(value) {
  const normalized = Number(value || 0);
  return `${normalized.toFixed(1)} c`;
}

function anomalyStatusLabel(status) {
  const map = {
    anomaly: "аномалия",
    growth: "рост",
    decline: "падение",
    stable: "стабильно",
    insufficient: "недостаточно данных",
  };
  return map[status] || "статус не определён";
}

function anomalyStatusClass(status) {
  return `status-${status || "unknown"}`;
}

async function manualRefresh() {
  await loadSummary();
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>

<style scoped>
.ai-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.8rem;
  padding: 0 0.7rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #075985;
  background: #e0f2fe;
  border: 1px solid #bae6fd;
}

.loading-note {
  margin-top: 0.75rem;
}

.thresholds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 0.6rem;
}

.threshold-item {
  display: grid;
  gap: 0.25rem;
  border: 1px solid #d9e2ec;
  border-radius: 0.65rem;
  padding: 0.65rem 0.75rem;
  background: #f8fafc;
}

.metric-help {
  font-size: 0.75rem;
  line-height: 1.35;
  margin: 0 0 0.2rem;
}

.block-help {
  margin: 0 0 0.65rem;
}

.threshold-title {
  font-weight: 700;
}

.threshold-help {
  font-size: 0.75rem;
}

.field-highlights {
  display: grid;
  gap: 0.35rem;
  margin-bottom: 0.7rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.45rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: lowercase;
  border: 1px solid transparent;
}

.status-anomaly {
  color: #b91c1c;
  background: #fee2e2;
  border-color: #fecaca;
}

.status-growth {
  color: #166534;
  background: #dcfce7;
  border-color: #bbf7d0;
}

.status-decline {
  color: #9a3412;
  background: #ffedd5;
  border-color: #fed7aa;
}

.status-stable {
  color: #1d4ed8;
  background: #dbeafe;
  border-color: #bfdbfe;
}

.status-insufficient,
.status-unknown {
  color: #374151;
  background: #f3f4f6;
  border-color: #d1d5db;
}
</style>
