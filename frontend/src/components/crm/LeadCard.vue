<template>
  <article class="crm-lead-card" @click="$emit('open', lead)">
    <header class="crm-lead-card-head">
      <strong class="crm-title">{{ lead.name || "Лид без имени" }}</strong>
      <span class="crm-score">{{ scoreLabel }}</span>
    </header>

    <p class="crm-meta">{{ sourceLabel }}</p>

    <p class="crm-contact">
      <span v-if="lead.phone">{{ lead.phone }}</span>
      <span v-if="lead.email">{{ lead.email }}</span>
      <span v-if="!lead.phone && !lead.email">Контакты не указаны</span>
    </p>

    <footer class="crm-footer">
      <span class="crm-created">{{ formattedCreatedAt }}</span>
      <span v-if="lead.next_contact_at" class="crm-next-contact">Следующий контакт: {{ formattedNextContactAt }}</span>
    </footer>
  </article>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  lead: {
    type: Object,
    required: true,
  },
});

defineEmits(["open"]);

const scoreLabel = computed(() => {
  return `Скоринг ${Number(props.lead.score || 0)}`;
});

const sourceLabel = computed(() => {
  return props.lead.utm_source || props.lead.utm_medium || props.lead.source_url || "Источник не указан";
});

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("ru-RU");
}

const formattedCreatedAt = computed(() => formatDate(props.lead.created_at));
const formattedNextContactAt = computed(() => formatDate(props.lead.next_contact_at));
</script>

<style scoped>
.crm-lead-card {
  border: 1px solid #dbe2ea;
  border-radius: 12px;
  padding: 10px;
  background: #fff;
  display: grid;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.crm-lead-card:hover {
  border-color: #93c5fd;
  transform: translateY(-1px);
}

.crm-lead-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.crm-title {
  font-size: 14px;
  color: #0f172a;
}

.crm-score {
  font-size: 11px;
  color: #1d4ed8;
  background: #dbeafe;
  border-radius: 999px;
  padding: 2px 8px;
  font-weight: 700;
}

.crm-meta,
.crm-contact,
.crm-created,
.crm-next-contact {
  margin: 0;
  font-size: 12px;
  color: #334155;
}

.crm-contact {
  display: grid;
  gap: 2px;
}

.crm-footer {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.crm-created {
  color: #64748b;
}

.crm-next-contact {
  color: #075985;
}
</style>
