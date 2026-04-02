<template>
  <aside class="crm-details" v-if="lead">
    <header class="crm-details-head">
      <div>
        <h2>{{ lead.name || "Unnamed lead" }}</h2>
        <p>#{{ lead.id }} · {{ lead.stage_name || "No stage" }}</p>
      </div>
      <button type="button" class="crm-close" @click="$emit('close')">Close</button>
    </header>

    <section class="crm-details-meta">
      <div><strong>Score:</strong> {{ Number(lead.score || 0) }}</div>
      <div><strong>Phone:</strong> {{ lead.phone || "-" }}</div>
      <div><strong>Email:</strong> {{ lead.email || "-" }}</div>
      <div><strong>Source:</strong> {{ lead.utm_source || lead.utm_medium || lead.source_url || "-" }}</div>
      <div><strong>Created:</strong> {{ formatDate(lead.created_at) }}</div>
      <div><strong>Next contact:</strong> {{ formatDate(lead.next_contact_at) || "-" }}</div>
      <div class="crm-message" v-if="lead.message"><strong>Message:</strong> {{ lead.message }}</div>
    </section>

    <section class="crm-action-block">
      <h3>Add note</h3>
      <textarea v-model="noteText" placeholder="Internal note" />
      <button type="button" @click="submitNote" :disabled="!noteText.trim()">Save note</button>
    </section>

    <section class="crm-action-block">
      <h3>Schedule contact</h3>
      <input v-model="scheduleAt" type="datetime-local" />
      <textarea v-model="scheduleNote" placeholder="Optional note"></textarea>
      <button type="button" @click="submitSchedule" :disabled="!scheduleAt">Schedule</button>
    </section>

    <section class="crm-activities">
      <header>
        <h3>Activity</h3>
        <button type="button" class="crm-refresh" @click="$emit('refresh')" :disabled="loading">Refresh</button>
      </header>
      <p v-if="loading" class="crm-muted">Loading activity...</p>
      <ul v-else-if="activities.length" class="crm-activity-list">
        <li v-for="item in activities" :key="item.id">
          <strong>{{ item.action_type }}</strong>
          <span>{{ formatDate(item.created_at) }}</span>
          <p>{{ item.description || "No description" }}</p>
        </li>
      </ul>
      <p v-else class="crm-muted">No activity yet.</p>
    </section>
  </aside>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  lead: {
    type: Object,
    default: null,
  },
  activities: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "refresh", "note", "schedule"]);

const noteText = ref("");
const scheduleAt = ref("");
const scheduleNote = ref("");

watch(
  () => props.lead?.id,
  () => {
    noteText.value = "";
    scheduleAt.value = "";
    scheduleNote.value = "";
  }
);

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("ru-RU");
}

function submitNote() {
  const payload = noteText.value.trim();
  if (!payload) return;
  emit("note", payload);
  noteText.value = "";
}

function submitSchedule() {
  if (!scheduleAt.value) return;
  const dateIso = new Date(scheduleAt.value).toISOString();
  emit("schedule", {
    nextContactAt: dateIso,
    note: scheduleNote.value.trim(),
  });
}
</script>

<style scoped>
.crm-details {
  width: min(420px, 100%);
  border-left: 1px solid #dbe2ea;
  background: #ffffff;
  padding: 16px;
  display: grid;
  align-content: start;
  gap: 14px;
  overflow-y: auto;
}

.crm-details-head {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}

.crm-details-head h2 {
  margin: 0;
  font-size: 18px;
}

.crm-details-head p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
}

.crm-close {
  min-height: 32px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #0f172a;
  box-shadow: none;
}

.crm-details-meta {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: #334155;
}

.crm-message {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px;
}

.crm-action-block {
  display: grid;
  gap: 8px;
}

.crm-action-block h3,
.crm-activities h3 {
  margin: 0;
  font-size: 14px;
}

.crm-action-block textarea,
.crm-action-block input {
  width: 100%;
}

.crm-activities {
  display: grid;
  gap: 8px;
}

.crm-activities header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.crm-refresh {
  min-height: 30px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #0f172a;
  box-shadow: none;
}

.crm-activity-list {
  list-style: none;
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
}

.crm-activity-list li {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px;
  display: grid;
  gap: 4px;
}

.crm-activity-list strong {
  text-transform: capitalize;
  font-size: 12px;
  color: #0f172a;
}

.crm-activity-list span {
  font-size: 11px;
  color: #64748b;
}

.crm-activity-list p {
  margin: 0;
  font-size: 12px;
  color: #334155;
}

.crm-muted {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 900px) {
  .crm-details {
    width: 100%;
    border-left: 0;
    border-top: 1px solid #dbe2ea;
  }
}
</style>
