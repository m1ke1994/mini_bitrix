<template>
  <section class="dashboard-section">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="chart-card">
      <div class="card-head card-head-with-filter">
        <h2>Распределение по устройствам</h2>
        <label class="traffic-filter" aria-label="Фильтр трафика для устройств и браузеров">
          <span class="traffic-filter-label">Трафик</span>
          <select v-model="selectedFilter" class="traffic-filter-select">
            <option value="all">Все</option>
            <option value="users">Пользователи</option>
            <option value="bots">Боты</option>
          </select>
        </label>
      </div>
      <p v-if="selectedFilter !== 'all'" class="muted traffic-filter-note">
        Для блока устройств API возвращает только агрегированные counts по типам устройств. Фильтр применяется к спискам ОС и браузеров ниже без изменения исходных данных.
      </p>
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
            <tr v-for="row in filteredOsRows" :key="row.name">
              <td>{{ row.name }}</td>
              <td>{{ row.count }}</td>
            </tr>
            <tr v-if="!filteredOsRows.length">
              <td colspan="2">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="chart-card">
      <div class="card-head card-head-with-filter">
        <h2>Распределение по браузерам</h2>
        <label class="traffic-filter" aria-label="Фильтр трафика для браузеров">
          <span class="traffic-filter-label">Трафик</span>
          <select v-model="selectedFilter" class="traffic-filter-select">
            <option value="all">Все</option>
            <option value="users">Пользователи</option>
            <option value="bots">Боты</option>
          </select>
        </label>
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
            <tr v-for="row in filteredBrowserRows" :key="row.name">
              <td>{{ row.name }}</td>
              <td>{{ row.count }}</td>
            </tr>
            <tr v-if="!filteredBrowserRows.length">
              <td colspan="2">Нет данных</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useAnalyticsDevices } from "../composables/useAnalyticsDevices";

const CRAWLER_PATTERNS = [
  /bot/i,
  /crawler/i,
  /spider/i,
  /headlesschrome/i,
  /googlebot/i,
  /applebot/i,
  /bingbot/i,
  /yandex/i,
  /duckduckbot/i,
  /baiduspider/i,
  /semrushbot/i,
  /ahrefsbot/i,
  /mj12bot/i,
  /slurp/i,
  /facebookexternalhit/i,
  /meta-externalagent/i,
  /slackbot/i,
  /discordbot/i,
  /telegrambot/i,
  /preview/i,
];

const { devicesData, error, loadDevices } = useAnalyticsDevices();
const selectedFilter = ref("all");

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

function isCrawlerAgentName(name) {
  const value = String(name || "").trim();
  if (!value) return false;
  return CRAWLER_PATTERNS.some((pattern) => pattern.test(value));
}

function filterTrafficRows(rows, mode) {
  const safeRows = Array.isArray(rows) ? [...rows] : [];

  if (mode === "users") {
    return safeRows.filter((row) => !isCrawlerAgentName(row.name));
  }
  if (mode === "bots") {
    return safeRows.filter((row) => isCrawlerAgentName(row.name));
  }
  return safeRows;
}

const filteredOsRows = computed(() => filterTrafficRows(osRows.value, selectedFilter.value));
const filteredBrowserRows = computed(() => filterTrafficRows(browserRows.value, selectedFilter.value));

async function manualRefresh() {
  await loadDevices();
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>

<style scoped>
.card-head-with-filter {
  align-items: flex-start;
}

.traffic-filter {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.traffic-filter-label {
  font-size: 0.8rem;
  color: var(--color-muted);
  font-weight: 600;
}

.traffic-filter-select {
  min-height: 2rem;
  padding: 0.25rem 0.55rem;
  border-radius: 0.55rem;
  border: 1px solid var(--color-border);
  background: #fff;
  font-size: 0.85rem;
  min-width: 9rem;
}

.traffic-filter-note {
  margin: -0.2rem 0 0.75rem;
  font-size: 0.85rem;
}

@media (max-width: 900px) {
  .card-head-with-filter {
    align-items: stretch;
  }

  .traffic-filter {
    width: 100%;
    justify-content: space-between;
  }

  .traffic-filter-select {
    min-width: 0;
    width: 100%;
    max-width: 12rem;
  }
}
</style>
