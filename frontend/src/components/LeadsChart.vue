<template>
  <div class="trend-chart">
    <Line v-if="hasAnyData" :data="chartData" :options="options" />
    <div v-else class="empty-state">Нет данных для построения графика</div>
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
  visits: {
    type: Array,
    default: () => [],
  },
  forms: {
    type: Array,
    default: () => [],
  },
  leads: {
    type: Array,
    default: () => [],
  },
});

function toCountMap(points) {
  return points.reduce((acc, point) => {
    acc[String(point.day)] = point.count;
    return acc;
  }, {});
}

function lastNDates(days) {
  const result = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i -= 1) {
    const d = new Date(now);
    d.setDate(now.getDate() - i);
    result.push(d.toISOString().slice(0, 10));
  }
  return result;
}

const labels = computed(() => {
  const days = new Set();
  [...props.visits, ...props.forms, ...props.leads].forEach((point) => days.add(String(point.day).slice(0, 10)));
  const sorted = Array.from(days).sort();
  if (!sorted.length) {
    return lastNDates(14);
  }
  return sorted;
});

const visitMap = computed(() => toCountMap(props.visits));
const formMap = computed(() => toCountMap(props.forms));
const leadMap = computed(() => toCountMap(props.leads));

const hasAnyData = computed(() => {
  return [...props.visits, ...props.forms, ...props.leads].some((point) => Number(point.count || 0) > 0);
});

const chartData = computed(() => {
  return {
    labels: labels.value,
    datasets: [
      {
        label: "Визиты",
        data: labels.value.map((day) => Number(visitMap.value[day] || 0)),
        borderColor: "#0d6efd",
        backgroundColor: "rgba(13, 110, 253, 0.12)",
        fill: true,
        tension: 0.25,
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 5,
      },
      {
        label: "Формы",
        data: labels.value.map((day) => Number(formMap.value[day] || 0)),
        borderColor: "#6c757d",
        backgroundColor: "rgba(108, 117, 125, 0.1)",
        fill: true,
        tension: 0.25,
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 5,
      },
      {
        label: "Заявки",
        data: labels.value.map((day) => Number(leadMap.value[day] || 0)),
        borderColor: "#198754",
        backgroundColor: "rgba(25, 135, 84, 0.1)",
        fill: true,
        tension: 0.25,
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 5,
      },
    ],
  };
});

const options = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        position: "top",
        labels: {
          usePointStyle: true,
          boxWidth: 8,
        },
      },
      tooltip: {
        backgroundColor: "#2c3e50",
        padding: 10,
        callbacks: {
          label(context) {
            return `${context.dataset.label}: ${context.parsed.y}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 0,
          autoSkip: true,
        },
      },
      y: {
        beginAtZero: true,
        grace: "8%",
        ticks: {
          precision: 0,
          stepSize: undefined,
        },
        grid: {
          color: "rgba(221, 221, 221, 1)",
        },
      },
    },
  };
});
</script>

<style scoped>
.trend-chart {
  height: 100%;
  min-height: 220px;
}

.empty-state {
  height: 100%;
  min-height: 220px;
  display: grid;
  place-items: center;
  color: #6b7280;
  font-size: 14px;
  border: 1px dashed #dddddd;
  border-radius: 4px;
}
</style>
