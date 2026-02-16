<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="stats">
      <article class="stat-card">
        <h3>Уникальные за период</h3>
        <strong>{{ unique.total_unique }}</strong>
      </article>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Динамика уникальных пользователей по дням</h2>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Дата</th>
              <th>Уникальные пользователи</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in unique.daily" :key="`u-${idx}`">
              <td>{{ formatDay(row.day) }}</td>
              <td>{{ row.count }}</td>
            </tr>
            <tr v-if="!unique.daily.length">
              <td colspan="2">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from "vue";
import { useUniqueVisitors } from "../composables/useUniqueVisitors";

const { unique, error, loadUniqueDaily } = useUniqueVisitors();

function formatDay(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("ru-RU");
}

onMounted(() => {
  loadUniqueDaily();
});
</script>
