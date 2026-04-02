<template>
  <div class="crm-chart">
    <Line v-if="hasData" :data="chartData" :options="options" />
    <div v-else class="crm-chart-empty">Нет данных по динамике</div>
  </div>
</template>

<script setup>
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";
import { computed } from "vue";
import { Line } from "vue-chartjs";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
});

const hasData = computed(() => props.items.some((item) => Number(item.leads_count || 0) > 0));

const chartData = computed(() => {
  const labels = props.items.map((item) => String(item.period || ""));
  return {
    labels,
    datasets: [
      {
        label: "Лиды",
        data: props.items.map((item) => Number(item.leads_count || 0)),
        borderColor: "#2563eb",
        backgroundColor: "rgba(37,99,235,0.15)",
        fill: true,
        tension: 0.22,
      },
      {
        label: "Сделки",
        data: props.items.map((item) => Number(item.deals_count || 0)),
        borderColor: "#16a34a",
        backgroundColor: "rgba(22,163,74,0.12)",
        fill: true,
        tension: 0.22,
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
