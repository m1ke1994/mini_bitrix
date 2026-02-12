<template>
  <Line :data="chartData" :options="options" />
</template>

<script setup>
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { computed } from "vue";
import { Line } from "vue-chartjs";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

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

const labels = computed(() => {
  const days = new Set();
  [...props.visits, ...props.forms, ...props.leads].forEach((point) => days.add(String(point.day)));
  return Array.from(days).sort();
});

const chartData = computed(() => {
  const visitMap = toCountMap(props.visits);
  const formMap = toCountMap(props.forms);
  const leadMap = toCountMap(props.leads);

  return {
    labels: labels.value,
    datasets: [
      {
        label: "Визиты",
        data: labels.value.map((day) => visitMap[day] || 0),
        borderColor: "#1672f3",
        backgroundColor: "rgba(22, 114, 243, 0.2)",
        tension: 0.3,
      },
      {
        label: "Формы",
        data: labels.value.map((day) => formMap[day] || 0),
        borderColor: "#f39c12",
        backgroundColor: "rgba(243, 156, 18, 0.2)",
        tension: 0.3,
      },
      {
        label: "Заявки",
        data: labels.value.map((day) => leadMap[day] || 0),
        borderColor: "#2e8b57",
        backgroundColor: "rgba(46, 139, 87, 0.2)",
        tension: 0.3,
      },
    ],
  };
});

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: true } },
};
</script>
