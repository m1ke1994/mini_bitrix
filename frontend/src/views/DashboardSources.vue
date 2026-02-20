<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="chart-card">
      <div class="card-head">
        <h2>Топ источников</h2>
        <button class="sort-btn" type="button" @click="toggleSort">
          Сортировка: {{ sortFieldLabel }}
        </button>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Источник</th>
              <th>Визиты</th>
              <th>Заявки</th>
              <th>Конверсия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in sortedSources" :key="`source-${index}`">
              <td>{{ item.source }}</td>
              <td>{{ item.visits }}</td>
              <td>{{ item.leads }}</td>
              <td>{{ item.conversion_pct.toFixed(2) }}%</td>
            </tr>
            <tr v-if="!sortedSources.length">
              <td colspan="4">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useAnalyticsSummary } from "../composables/useAnalyticsSummary";

const { summary, error, loadSummary } = useAnalyticsSummary();

const sortMode = ref("visits");
const sortFieldLabel = computed(() => {
  if (sortMode.value === "visits") return "по визитам";
  if (sortMode.value === "leads") return "по заявкам";
  return "по конверсии";
});

const sortedSources = computed(() => {
  const rows = [...(summary.value.source_performance || [])];
  return rows.sort((a, b) => {
    if (sortMode.value === "visits") return (b.visits || 0) - (a.visits || 0);
    if (sortMode.value === "leads") return (b.leads || 0) - (a.leads || 0);
    return (b.conversion_pct || 0) - (a.conversion_pct || 0);
  });
});

function toggleSort() {
  if (sortMode.value === "visits") {
    sortMode.value = "leads";
  } else if (sortMode.value === "leads") {
    sortMode.value = "conversion";
  } else {
    sortMode.value = "visits";
  }
}

async function manualRefresh() {
  await loadSummary();
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>
