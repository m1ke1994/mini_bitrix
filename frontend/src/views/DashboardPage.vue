<template>
  <AppShell>
    <section class="page">
      <h1>Панель управления</h1>
      <p v-if="error" class="error">{{ error }}</p>

      <div class="stats">
        <article class="stat-card">
          <h3>Визиты</h3>
          <strong>{{ summary.visit_count }}</strong>
        </article>
        <article class="stat-card">
          <h3>Заявки</h3>
          <strong>{{ summary.leads_count }}</strong>
        </article>
        <article class="stat-card">
          <h3>Формы</h3>
          <strong>{{ summary.form_submit_count }}</strong>
        </article>
        <article class="stat-card">
          <h3>Конверсия</h3>
          <strong>{{ (summary.conversion * 100).toFixed(2) }}%</strong>
        </article>
      </div>

      <div class="chart-card">
        <h2>Динамика по дням</h2>
        <div class="chart-wrap">
          <LeadsChart
            :visits="summary.visits_by_day || []"
            :forms="summary.forms_by_day || []"
            :leads="summary.leads_by_day || []"
          />
        </div>
      </div>

      <div class="chart-card">
        <h2>Последние 10 заявок</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Телефон</th>
              <th>Статус</th>
              <th>Создано</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lead in summary.latest_leads || []" :key="lead.id">
              <td>{{ lead.id }}</td>
              <td>{{ lead.name }}</td>
              <td>{{ lead.phone }}</td>
              <td>{{ lead.status }}</td>
              <td>{{ lead.created_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </AppShell>
</template>

<script setup>
import { onMounted, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import LeadsChart from "../components/LeadsChart.vue";
import api from "../services/api";

const summary = ref({
  visit_count: 0,
  form_submit_count: 0,
  leads_count: 0,
  conversion: 0,
  visits_by_day: [],
  forms_by_day: [],
  leads_by_day: [],
  latest_leads: [],
});
const error = ref("");

async function loadSummary() {
  try {
    const response = await api.get("/api/analytics/summary/");
    summary.value = response.data;
  } catch (_) {
    error.value = "Ошибка загрузки аналитики.";
  }
}

onMounted(loadSummary);
</script>
