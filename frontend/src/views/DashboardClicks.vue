<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="chart-card">
      <p class="muted">Всего кликов: {{ summary.total_clicks || 0 }}</p>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Страница</th>
              <th>Элемент</th>
              <th>Клики</th>
              <th>% от всех кликов</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in summary.top_clicks || []" :key="`click-${index}`">
              <td>{{ item.page_pathname || "/" }}</td>
              <td>{{ item.element_text || item.element_id || item.element_class || "-" }}</td>
              <td>{{ item.count }}</td>
              <td>{{ (item.percent_of_total || 0).toFixed(2) }}%</td>
            </tr>
            <tr v-if="!(summary.top_clicks || []).length">
              <td colspan="4">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from "vue";
import { useAnalyticsSummary } from "../composables/useAnalyticsSummary";

const { summary, error, loadSummary } = useAnalyticsSummary();

async function manualRefresh() {
  await loadSummary();
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>
