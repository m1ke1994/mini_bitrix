<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="chart-card">
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Страница</th>
              <th>Визиты</th>
              <th>Заявки</th>
              <th>Конверсия (%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in sortedRows" :key="`row-${index}`">
              <td>{{ item.pathname }}</td>
              <td>{{ item.visits }}</td>
              <td>{{ item.leads }}</td>
              <td>{{ item.conversion_pct.toFixed(2) }}</td>
            </tr>
            <tr v-if="!sortedRows.length">
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
import { useAnalyticsSummary } from "../composables/useAnalyticsSummary";

const { summary, error, loadSummary } = useAnalyticsSummary();

const sortedRows = computed(() => {
  const rows = [...(summary.value.conversion_by_pages || [])];
  return rows.sort((a, b) => {
    const leadsDelta = (b.leads || 0) - (a.leads || 0);
    if (leadsDelta !== 0) {
      return leadsDelta;
    }
    return (b.visits || 0) - (a.visits || 0);
  });
});

async function manualRefresh() {
  await loadSummary();
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>
