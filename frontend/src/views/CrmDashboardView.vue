<template>
  <section class="crm-analytics-page">
    <header class="crm-analytics-head">
      <div>
        <h1>Панель CRM</h1>
        <p>Воронка, источники, скорость реакции и конверсия.</p>
      </div>
      <button type="button" @click="manualRefresh" :disabled="loading">Обновить</button>
    </header>

    <form class="crm-filters" @submit.prevent="manualRefresh">
      <label>
        С
        <input v-model="dateFrom" type="date" />
      </label>
      <label>
        По
        <input v-model="dateTo" type="date" />
      </label>
      <label>
        Шаг графика
        <select v-model="granularity">
          <option value="day">По дням</option>
          <option value="week">По неделям</option>
        </select>
      </label>
      <button type="submit" :disabled="loading">Применить</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="crm-metrics-grid">
      <CrmMetricCard title="Всего лидов" :value="funnel.total_leads || 0" hint="За выбранный период" />
      <CrmMetricCard
        title="Средний первый ответ"
        :value="`${Number(responseTime.avg_first_response_hours || 0).toFixed(2)} ч`"
        hint="По активности в карточках лидов"
      />
      <CrmMetricCard title="Лучший источник" :value="topSourceName" :hint="topSourceHint" />
      <CrmMetricCard title="Лучшая конверсия канала" :value="topConversionValue" :hint="topConversionHint" />
    </div>

    <div class="crm-chart-grid">
      <article class="chart-card">
        <h2>Динамика лидов</h2>
        <CrmTimelineChart :items="timeline.items || []" />
      </article>
      <article class="chart-card">
        <h2>Эффективность источников</h2>
        <CrmSourcesChart :items="sources.items || []" :top="8" />
      </article>
    </div>

    <div class="crm-table-grid">
      <article class="chart-card">
        <h2>Воронка</h2>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Стадия</th>
                <th>Лиды</th>
                <th>Конв. с прошлой стадии</th>
                <th>Конв. с первой стадии</th>
                <th>Оценочная сумма</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in funnel.stages || []" :key="row.stage_id">
                <td>{{ row.stage }}</td>
                <td>{{ row.count }}</td>
                <td>{{ Number(row.conversion_from_previous_pct || 0).toFixed(2) }}%</td>
                <td>{{ Number(row.conversion_from_first_pct || 0).toFixed(2) }}%</td>
                <td>{{ formatMoney(row.estimated_value_total) }}</td>
              </tr>
              <tr v-if="!(funnel.stages || []).length">
                <td colspan="5">Нет данных</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="chart-card">
        <h2>Конверсия по каналам</h2>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Канал</th>
                <th>Лиды</th>
                <th>Сделки</th>
                <th>Конверсия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in conversionRate.items || []" :key="`${row.channel}-${row.utm_source}-${row.utm_medium}`">
                <td>{{ row.channel }}</td>
                <td>{{ row.leads }}</td>
                <td>{{ row.deals }}</td>
                <td>{{ Number(row.conversion_pct || 0).toFixed(2) }}%</td>
              </tr>
              <tr v-if="!(conversionRate.items || []).length">
                <td colspan="4">Нет данных</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </div>

    <div class="crm-table-grid">
      <article class="chart-card">
        <h2>Пики активности (heatmap)</h2>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>День недели</th>
                <th>Час</th>
                <th>Активность</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in topHeatmapRows" :key="`${row.weekday}-${row.hour}`">
                <td>{{ weekdayLabel(row.weekday) }}</td>
                <td>{{ String(row.hour).padStart(2, "0") }}:00</td>
                <td>{{ row.count }}</td>
              </tr>
              <tr v-if="!topHeatmapRows.length">
                <td colspan="3">Нет данных</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="chart-card">
        <h2>AI-рекомендации</h2>
        <p class="muted">Источник: {{ advisor.source || "-" }}</p>
        <ul class="crm-advisor-list" v-if="(advisor.recommendations || []).length">
          <li v-for="(item, idx) in advisor.recommendations" :key="`${item.category}-${idx}`">
            <div class="crm-advisor-top">
              <strong>{{ item.priority }}</strong>
              <span>{{ item.category }}</span>
            </div>
            <p>{{ item.recommendation }}</p>
            <small>{{ item.expected_impact }}</small>
          </li>
        </ul>
        <p v-else class="muted">Рекомендаций пока нет.</p>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import CrmMetricCard from "~/components/crm/CrmMetricCard.vue";
import CrmSourcesChart from "~/components/crm/CrmSourcesChart.vue";
import CrmTimelineChart from "~/components/crm/CrmTimelineChart.vue";
import { useCrmAnalytics } from "~/composables/useCrmAnalytics";

const {
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
} = useCrmAnalytics();

function toDateString(date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

const now = new Date();
const monthAgo = new Date(now);
monthAgo.setDate(now.getDate() - 30);

const dateFrom = ref(toDateString(monthAgo));
const dateTo = ref(toDateString(now));
const granularity = ref("day");

const topSource = computed(() => {
  const rows = Array.isArray(sources.value.items) ? sources.value.items : [];
  if (!rows.length) return null;
  return [...rows].sort((a, b) => Number(b.leads || 0) - Number(a.leads || 0))[0] || null;
});

const topSourceName = computed(() => topSource.value?.source || "-");
const topSourceHint = computed(() => {
  if (!topSource.value) return "Нет данных по источникам";
  return `${Number(topSource.value.leads || 0)} лидов / ${Number(topSource.value.deals || 0)} сделок`;
});

const topConversion = computed(() => {
  const rows = Array.isArray(conversionRate.value.items) ? conversionRate.value.items : [];
  if (!rows.length) return null;
  return [...rows].sort((a, b) => Number(b.conversion_pct || 0) - Number(a.conversion_pct || 0))[0] || null;
});

const topConversionValue = computed(() => {
  if (!topConversion.value) return "-";
  return `${Number(topConversion.value.conversion_pct || 0).toFixed(2)}%`;
});

const topConversionHint = computed(() => {
  if (!topConversion.value) return "Нет данных по конверсии";
  return String(topConversion.value.channel || "неизвестно");
});

const topHeatmapRows = computed(() => {
  const rows = Array.isArray(heatmap.value.items) ? heatmap.value.items : [];
  return [...rows].sort((a, b) => Number(b.count || 0) - Number(a.count || 0)).slice(0, 12);
});

function weekdayLabel(value) {
  const map = {
    1: "Воскресенье",
    2: "Понедельник",
    3: "Вторник",
    4: "Среда",
    5: "Четверг",
    6: "Пятница",
    7: "Суббота",
  };
  return map[Number(value)] || "-";
}

function formatMoney(value) {
  const numeric = Number(value || 0);
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(numeric);
}

async function manualRefresh() {
  await loadAnalytics({
    dateFrom: dateFrom.value,
    dateTo: dateTo.value,
    granularity: granularity.value,
  });
}

defineExpose({ manualRefresh });

function handleManualRefreshEvent(event) {
  manualRefresh().finally(() => {
    if (typeof event?.detail?.done === "function") {
      event.detail.done();
    }
  });
}

onMounted(() => {
  manualRefresh();
  window.addEventListener("tracknode:manual-refresh", handleManualRefreshEvent);
});

onBeforeUnmount(() => {
  window.removeEventListener("tracknode:manual-refresh", handleManualRefreshEvent);
});
</script>

<style scoped>
.crm-analytics-page {
  min-height: 100%;
  display: grid;
  align-content: start;
  gap: 12px;
}

.crm-analytics-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.crm-analytics-head h1 {
  margin: 0;
  font-size: 24px;
}

.crm-analytics-head p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #64748b;
}

.crm-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: end;
}

.crm-filters label {
  display: grid;
  gap: 4px;
  font-size: 12px;
  color: #475569;
  min-width: 150px;
}

.crm-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.crm-chart-grid,
.crm-table-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.crm-advisor-list {
  list-style: none;
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
}

.crm-advisor-list li {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px;
  display: grid;
  gap: 4px;
}

.crm-advisor-top {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.crm-advisor-list p {
  margin: 0;
  font-size: 13px;
}

.crm-advisor-list small {
  color: #475569;
  font-size: 12px;
}

@media (max-width: 1180px) {
  .crm-metrics-grid,
  .crm-chart-grid,
  .crm-table-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .crm-metrics-grid,
  .crm-chart-grid,
  .crm-table-grid {
    grid-template-columns: 1fr;
  }

  .crm-analytics-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
