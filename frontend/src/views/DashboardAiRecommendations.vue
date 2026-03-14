<template>
  <section class="dashboard-section">
    <div class="chart-card">
      <div class="card-head ai-head">
        <h2>AI рекомендации</h2>
        <span class="badge">Этап 1</span>
      </div>
      <p class="muted">
        Раздел подготовлен под будущий модуль рекомендаций. Сейчас собираются события, которые станут входными данными
        для AI-аналитики.
      </p>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

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
        Скролл-глубина по порогам — показывает, до какой глубины страницы доходили пользователи.
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
              <td>{{ formSignals.form_view || 0 }}</td>
            </tr>
            <tr>
              <td>Старт взаимодействия</td>
              <td class="muted">Пользователь начал работать с формой.</td>
              <td>{{ formSignals.form_start || 0 }}</td>
            </tr>
            <tr>
              <td>Первое заполненное поле</td>
              <td class="muted">Пользователь впервые ввёл данные в одно из полей.</td>
              <td>{{ formSignals.form_first_field_filled || 0 }}</td>
            </tr>
            <tr>
              <td>Попытка отправки</td>
              <td class="muted">Пользователь попытался отправить форму.</td>
              <td>{{ formSignals.form_submit_attempt || 0 }}</td>
            </tr>
            <tr>
              <td>Успешная отправка</td>
              <td class="muted">Форма была отправлена без ошибки.</td>
              <td>{{ formSignals.form_submit_success || 0 }}</td>
            </tr>
            <tr>
              <td>Ошибка отправки</td>
              <td class="muted">При отправке формы возникла ошибка.</td>
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
</style>
