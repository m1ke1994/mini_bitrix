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

      <div class="stats secondary">
        <article class="stat-card">
          <h3>Среднее время на сайте</h3>
          <strong>{{ summary.avg_time_on_site.toFixed(1) }} сек</strong>
        </article>
        <article class="stat-card">
          <h3>Средняя длительность сессии</h3>
          <strong>{{ summary.avg_session_duration.toFixed(1) }} сек</strong>
        </article>
        <article class="stat-card">
          <h3>Средняя глубина просмотра</h3>
          <strong>{{ summary.avg_scroll_depth.toFixed(1) }}%</strong>
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

      <div class="two-col-grid">
        <div class="chart-card">
          <h2>Топ источников</h2>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Источник</th>
                  <th>Визиты</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in summary.top_sources" :key="`source-${index}`">
                  <td>{{ item.source }}</td>
                  <td>{{ item.count }}</td>
                </tr>
                <tr v-if="!summary.top_sources.length">
                  <td colspan="2">Нет данных</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="chart-card">
          <h2>Топ кликов</h2>
          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Страница</th>
                  <th>Элемент</th>
                  <th>Клики</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in summary.top_clicks" :key="`click-${index}`">
                  <td>{{ item.page_pathname || "/" }}</td>
                  <td>{{ item.element_text || item.element_id || item.element_class || "-" }}</td>
                  <td>{{ item.count }}</td>
                </tr>
                <tr v-if="!summary.top_clicks.length">
                  <td colspan="3">Нет данных</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h2>Конверсия по страницам</h2>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Страница</th>
                <th>Визиты</th>
                <th>Заявки</th>
                <th>Конверсия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in summary.conversion_by_pages" :key="`page-${index}`">
                <td>{{ item.pathname }}</td>
                <td>{{ item.visits }}</td>
                <td>{{ item.leads }}</td>
                <td>{{ item.conversion_pct.toFixed(2) }}%</td>
              </tr>
              <tr v-if="!summary.conversion_by_pages.length">
                <td colspan="4">Нет данных</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="chart-card">
        <h2>Последние 10 заявок</h2>
        <div class="table-wrap">
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
              <tr v-for="lead in summary.latest_leads || []" :key="lead.id">
                <td>{{ lead.id }}</td>
                <td>{{ lead.name || "-" }}</td>
                <td>{{ lead.phone || "-" }}</td>
                <td>{{ lead.email || "-" }}</td>
                <td>{{ lead.status }}</td>
                <td>{{ lead.created_at }}</td>
              </tr>
              <tr v-if="!(summary.latest_leads || []).length">
                <td colspan="6">Нет данных</td>
              </tr>
            </tbody>
          </table>
        </div>
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
  avg_time_on_site: 0,
  avg_session_duration: 0,
  avg_scroll_depth: 0,
  top_sources: [],
  conversion_by_pages: [],
  top_clicks: [],
});
const error = ref("");

async function loadSummary() {
  try {
    const response = await api.get("/api/analytics/summary/");
    summary.value = {
      ...summary.value,
      ...response.data,
      top_sources: response.data.top_sources || [],
      conversion_by_pages: response.data.conversion_by_pages || [],
      top_clicks: response.data.top_clicks || [],
    };
  } catch (_) {
    error.value = "Ошибка загрузки аналитики.";
  }
}

onMounted(loadSummary);
</script>
