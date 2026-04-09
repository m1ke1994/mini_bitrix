<template>
  <article class="crm-metric-card">
    <h3>{{ title }}</h3>
    <strong>{{ value }}</strong>
    <p v-if="hint">{{ hint }}</p>
  </article>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
  hint: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.crm-metric-card {
  background: #fff;
  border: 1px solid #dbe2ea;
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 6px;
}

.crm-metric-card h3 {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.crm-metric-card strong {
  font-size: 24px;
  color: #0f172a;
}

.crm-metric-card p {
  margin: 0;
  font-size: 12px;
  color: #475569;
}
</style>
