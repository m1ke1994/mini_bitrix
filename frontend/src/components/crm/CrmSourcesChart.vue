<template>
  <div class="crm-chart">
    <Bar v-if="hasData" :data="chartData" :options="options" />
    <div v-else class="crm-chart-empty">No source data</div>
  </div>
</template>

<script setup>
import { Bar } from "vue-chartjs";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { computed } from "vue";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  top: {
    type: Number,
    default: 8,
  },
});

const topItems = computed(() => {
  return [...props.items]
    .sort((a, b) => Number(b.leads || 0) - Number(a.leads || 0))
    .slice(0, props.top);
});

const hasData = computed(() => topItems.value.length > 0);

const chartData = computed(() => {
  return {
    labels: topItems.value.map((item) => String(item.source || "unknown").slice(0, 32)),
    datasets: [
      {
        label: "Leads",
        data: topItems.value.map((item) => Number(item.leads || 0)),
        backgroundColor: "#0ea5e9",
      },
      {
        label: "Deals",
        data: topItems.value.map((item) => Number(item.deals || 0)),
        backgroundColor: "#22c55e",
      },
    ],
  };
});

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top",
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0,
      },
    },
  },
};
</script>

<style scoped>
.crm-chart {
  min-height: 260px;
  height: 300px;
}

.crm-chart-empty {
  min-height: 240px;
  display: grid;
  place-items: center;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  color: #64748b;
  font-size: 13px;
}
</style>
