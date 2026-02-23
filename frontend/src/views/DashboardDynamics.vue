<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

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
  </section>
</template>

<script setup>
import { onMounted } from "vue";
import LeadsChart from "../components/LeadsChart.vue";
import { useAnalyticsSummary } from "../composables/useAnalyticsSummary";

const { summary, error, loadSummary } = useAnalyticsSummary();

async function manualRefresh() {
  await loadSummary();
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>
