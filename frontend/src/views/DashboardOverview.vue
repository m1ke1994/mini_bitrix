<template>
  <section class="dashboard-section">
    <p v-if="overviewError" class="error">{{ overviewError }}</p>

    <div class="stats">
      <article class="stat-card">
        <h3>Визиты</h3>
        <strong>{{ overview.visits_total }}</strong>
      </article>
      <article class="stat-card">
        <h3>Уникальные</h3>
        <strong>{{ overview.visitors_unique }}</strong>
      </article>
      <article class="stat-card">
        <h3>Формы</h3>
        <strong>{{ overview.forms_total }}</strong>
      </article>
      <article class="stat-card">
        <h3>Конверсия</h3>
        <strong>{{ Number(overview.conversion || 0).toFixed(2) }}%</strong>
      </article>
      <article class="stat-card">
        <h3>Уведомления</h3>
        <strong>{{ overview.notifications_sent_total }}</strong>
      </article>
    </div>

    <div class="chart-card">
      <div class="card-head">
        <h2>📨 Уведомления о заявках</h2>
      </div>
      <p v-if="Number(overview.notifications_sent_total || 0) > 0" class="notifications-text">
        Отправлено в Telegram: <strong>{{ overview.notifications_sent_total }}</strong>
      </p>
      <p v-else class="notifications-text">Пока нет отправленных заявок.</p>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from "vue";

import { useAnalyticsOverview } from "../composables/useAnalyticsOverview";

const { overview, error: overviewError, loadOverview } = useAnalyticsOverview();

onMounted(loadOverview);
</script>
