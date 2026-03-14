<template>
  <section class="dashboard-section">
    <div class="chart-card">
      <div class="card-head ai-head">
        <h2>AI рекомендации</h2>
        <span class="badge">Этап 1</span>
      </div>
      <p class="muted">
        Раздел подготовлен под будущий модуль рекомендаций. Сейчас собираются события, которые станут входными данными для
        AI-аналитики.
      </p>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="stats">
      <article class="stat-card">
        <h3>Скролл-события</h3>
        <strong>{{ scrollEventsTotal }}</strong>
      </article>
      <article class="stat-card">
        <h3>Шаги формы</h3>
        <strong>{{ formStepsTotal }}</strong>
      </article>
      <article class="stat-card">
        <h3>Просмотры секций</h3>
        <strong>{{ sectionViewsTotal }}</strong>
      </article>
      <article class="stat-card">
        <h3>CTA-клики</h3>
        <strong>{{ ctaClicksTotal }}</strong>
      </article>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Скролл-глубина по порогам</h2>
      </div>
      <div class="thresholds-grid">
        <div class="threshold-item">25%: <strong>{{ scrollThreshold(25) }}</strong></div>
        <div class="threshold-item">50%: <strong>{{ scrollThreshold(50) }}</strong></div>
        <div class="threshold-item">75%: <strong>{{ scrollThreshold(75) }}</strong></div>
        <div class="threshold-item">100%: <strong>{{ scrollThreshold(100) }}</strong></div>
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
              <th>Количество</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Форма в зоне видимости</td>
              <td>{{ formSignals.form_view || 0 }}</td>
            </tr>
            <tr>
              <td>Старт взаимодействия</td>
              <td>{{ formSignals.form_start || 0 }}</td>
            </tr>
            <tr>
              <td>Первое заполненное поле</td>
              <td>{{ formSignals.form_first_field_filled || 0 }}</td>
            </tr>
            <tr>
              <td>Попытка отправки</td>
              <td>{{ formSignals.form_submit_attempt || 0 }}</td>
            </tr>
            <tr>
              <td>Успешная отправка</td>
              <td>{{ formSignals.form_submit_success || 0 }}</td>
            </tr>
            <tr>
              <td>Ошибка отправки</td>
              <td>{{ formSignals.form_submit_error || 0 }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="loading" class="muted">Обновление данных...</p>
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

const scrollEventsTotal = computed(() => Number(scrollSignals.value.events_total || 0));
const formStepsTotal = computed(() =>
  Number(formSignals.value.form_view || 0) +
  Number(formSignals.value.form_start || 0) +
  Number(formSignals.value.form_first_field_filled || 0) +
  Number(formSignals.value.form_submit_attempt || 0) +
  Number(formSignals.value.form_submit_success || 0) +
  Number(formSignals.value.form_submit_error || 0)
);
const sectionViewsTotal = computed(() => Number(aiSignals.value.section_views?.events_total || 0));
const ctaClicksTotal = computed(() => Number(aiSignals.value.cta_clicks?.events_total || 0));

function scrollThreshold(level) {
  return Number(scrollSignals.value.thresholds?.[String(level)] || scrollSignals.value.thresholds?.[level] || 0);
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

.thresholds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 0.6rem;
}

.threshold-item {
  border: 1px solid #d9e2ec;
  border-radius: 0.65rem;
  padding: 0.65rem 0.75rem;
  background: #f8fafc;
}
</style>
