<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="stats">
      <article class="stat-card">
        <h3>Среднее время на странице</h3>
        <strong>{{ formatDuration(engagement.avg_time_on_page_seconds) }}</strong>
      </article>
      <article class="stat-card">
        <h3>Общее время за период</h3>
        <strong>{{ formatDuration(engagement.total_time_on_site_seconds) }}</strong>
      </article>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Вовлеченность по страницам</h2>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Страница</th>
              <th>Среднее время</th>
              <th>Общее время</th>
              <th>Кол-во посещений</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in sortedPages" :key="`engagement-${idx}`">
              <td>{{ row.pathname || "/" }}</td>
              <td>{{ formatDuration(row.avg_duration_seconds) }}</td>
              <td>{{ formatDuration(row.total_duration_seconds) }}</td>
              <td>{{ row.visits_count || 0 }}</td>
            </tr>
            <tr v-if="!sortedPages.length">
              <td colspan="4">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from "vue";

import { useAnalyticsEngagement } from "../composables/useAnalyticsEngagement";
import { formatDuration } from "../utils/duration";

const { engagement, error, loadEngagement } = useAnalyticsEngagement();

const sortedPages = computed(() => {
  const rows = [...(engagement.value.pages || [])];
  return rows.sort((a, b) => {
    const totalA = Number(a?.total_duration_seconds || 0);
    const totalB = Number(b?.total_duration_seconds || 0);
    return totalB - totalA;
  });
});

async function manualRefresh() {
  await loadEngagement();
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>
