<template>
  <section class="dashboard-section">
    <p v-if="error || overviewError" class="error">{{ error || overviewError }}</p>

    <div class="stats">
      <article class="stat-card">
        <h3>Визиты</h3>
        <strong>{{ overview.visits_total }}</strong>
      </article>
      <article class="stat-card">
        <h3>Уникальные</h3>
        <strong>{{ overview.visitors_unique }}</strong>
      </article>
      <article class="stat-card">
        <h3>Заявки</h3>
        <strong>{{ overview.leads_total }}</strong>
      </article>
      <article class="stat-card">
        <h3>Формы</h3>
        <strong>{{ overview.forms_total }}</strong>
      </article>
      <article class="stat-card">
        <h3>Конверсия</h3>
        <strong>{{ (overview.conversion * 100).toFixed(2) }}%</strong>
      </article>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Последние 10 заявок</h2>
        <button class="sort-btn" type="button" @click="toggleDateSort">
          Сортировка: {{ dateSortAsc ? "старые -> новые" : "новые -> старые" }}
        </button>
      </div>
      <div class="table-wrap sticky-head">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Телефон</th>
              <th>Email</th>
              <th>Статус</th>
              <th>Создано</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lead in sortedLeads" :key="lead.id">
              <td>{{ lead.id }}</td>
              <td>{{ lead.name || "-" }}</td>
              <td>{{ lead.phone || "-" }}</td>
              <td>{{ lead.email || "-" }}</td>
              <td>{{ lead.status }}</td>
              <td>{{ formatDateTime(lead.created_at) }}</td>
            </tr>
            <tr v-if="!sortedLeads.length">
              <td colspan="6">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useAnalyticsOverview } from "../composables/useAnalyticsOverview";
import { useAnalyticsSummary } from "../composables/useAnalyticsSummary";

const { overview, error: overviewError, loadOverview } = useAnalyticsOverview();
const { summary, error, loadSummary } = useAnalyticsSummary();
const dateSortAsc = ref(false);

const sortedLeads = computed(() => {
  const leads = [...(summary.value.latest_leads || [])];
  return leads.sort((a, b) => {
    const aDate = new Date(a.created_at).getTime();
    const bDate = new Date(b.created_at).getTime();
    return dateSortAsc.value ? aDate - bDate : bDate - aDate;
  });
});

function toggleDateSort() {
  dateSortAsc.value = !dateSortAsc.value;
}

function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

onMounted(async () => {
  await Promise.all([loadOverview(), loadSummary()]);
});
</script>
