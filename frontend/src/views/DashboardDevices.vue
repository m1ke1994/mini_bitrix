<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="chart-card">
      <div class="card-head">
        <h2>Распределение по устройствам</h2>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Тип устройства</th>
              <th>Количество</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in deviceRows" :key="row.name">
              <td>{{ row.name }}</td>
              <td>{{ row.count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Распределение по ОС</h2>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>ОС</th>
              <th>Количество</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in osRows" :key="row.name">
              <td>{{ row.name }}</td>
              <td>{{ row.count }}</td>
            </tr>
            <tr v-if="!osRows.length">
              <td colspan="2">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>Распределение по браузерам</h2>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Браузер</th>
              <th>Количество</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in browserRows" :key="row.name">
              <td>{{ row.name }}</td>
              <td>{{ row.count }}</td>
            </tr>
            <tr v-if="!browserRows.length">
              <td colspan="2">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useAnalyticsDevices } from "../composables/useAnalyticsDevices";

const { devicesData, error, loadDevices } = useAnalyticsDevices();

const deviceRows = computed(() => [
  { name: "mobile", count: devicesData.value.devices.mobile || 0 },
  { name: "desktop", count: devicesData.value.devices.desktop || 0 },
  { name: "tablet", count: devicesData.value.devices.tablet || 0 },
]);

const osRows = computed(() =>
  Object.entries(devicesData.value.os || {})
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => (b.count || 0) - (a.count || 0))
);

const browserRows = computed(() =>
  Object.entries(devicesData.value.browsers || {})
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => (b.count || 0) - (a.count || 0))
);

onMounted(loadDevices);
</script>
