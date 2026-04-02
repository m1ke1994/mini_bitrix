<template>
  <section class="crm-kanban-page">
    <header class="crm-page-head">
      <div>
        <h1>CRM Kanban</h1>
        <p>Pipeline-based lead workflow with live updates.</p>
      </div>
      <div class="crm-page-actions">
        <span class="crm-ws" :class="{ online: isConnected }">{{ isConnected ? "Live" : "Offline" }}</span>
        <button type="button" @click="manualRefresh" :disabled="crm.loading">Refresh</button>
      </div>
    </header>

    <p v-if="crm.error" class="error">{{ crm.error }}</p>

    <div v-if="crm.loading" class="crm-loading">Loading CRM board...</div>

    <div v-else class="crm-board-layout">
      <div class="crm-board" v-if="crm.stages.length">
        <CrmStageColumn
          v-for="stage in crm.stages"
          :key="stage.id"
          :stage="stage"
          :leads="crm.leadsByStage[String(stage.id)] || []"
          @move="onLeadMove"
          @open="openLead"
        />
      </div>
      <div v-else class="crm-loading">No stages configured.</div>

      <LeadDetailsPanel
        v-if="crm.selectedLead"
        :lead="crm.selectedLead"
        :activities="crm.selectedActivities"
        :loading="crm.loadingActivities"
        @close="crm.selectedLeadId = null"
        @refresh="refreshSelectedLeadActivities"
        @note="createNote"
        @schedule="createSchedule"
      />
      <aside v-else class="crm-empty-panel">Select a lead card to open details.</aside>
    </div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from "vue";
import CrmStageColumn from "~/components/crm/CrmStageColumn.vue";
import LeadDetailsPanel from "~/components/crm/LeadDetailsPanel.vue";
import { useLeadsRealtime } from "~/composables/useLeadsRealtime";
import { useCrmStore } from "~/stores/crm";

const crm = useCrmStore();
const { connect, disconnect, isConnected } = useLeadsRealtime();

function handleLeadEvent(eventPayload) {
  crm.applyRealtimePayload(eventPayload);
}

async function manualRefresh() {
  await crm.loadCrm();
  if (crm.selectedLeadId) {
    await crm.loadActivities(crm.selectedLeadId);
  }
}

defineExpose({ manualRefresh });

function handleManualRefreshEvent(event) {
  manualRefresh().finally(() => {
    if (typeof event?.detail?.done === "function") {
      event.detail.done();
    }
  });
}

async function onLeadMove({ leadId, toStageId }) {
  const lead = crm.leads.find((item) => Number(item.id) === Number(leadId));
  if (!lead) return;
  if (Number(lead.stage_id || lead.stage) === Number(toStageId)) return;

  try {
    await crm.moveLeadWithOptimistic(leadId, toStageId);
    if (crm.selectedLeadId && Number(crm.selectedLeadId) === Number(leadId)) {
      await crm.loadActivities(leadId);
    }
  } catch (_error) {
    crm.error = "Failed to move lead.";
  }
}

async function openLead(lead) {
  if (!lead?.id) return;
  await crm.selectLead(lead.id);
}

async function createNote(note) {
  if (!crm.selectedLeadId) return;
  try {
    await crm.createNote(crm.selectedLeadId, note);
  } catch (_error) {
    crm.error = "Failed to save note.";
  }
}

async function createSchedule(payload) {
  if (!crm.selectedLeadId) return;
  try {
    await crm.createSchedule(crm.selectedLeadId, payload.nextContactAt, payload.note || "");
  } catch (_error) {
    crm.error = "Failed to schedule contact.";
  }
}

async function refreshSelectedLeadActivities() {
  if (!crm.selectedLeadId) return;
  await crm.loadActivities(crm.selectedLeadId);
}

onMounted(async () => {
  await crm.loadCrm();
  connect(handleLeadEvent);
  window.addEventListener("tracknode:manual-refresh", handleManualRefreshEvent);
});

onBeforeUnmount(() => {
  window.removeEventListener("tracknode:manual-refresh", handleManualRefreshEvent);
  disconnect();
});
</script>

<style scoped>
.crm-kanban-page {
  min-height: 100%;
  display: grid;
  align-content: start;
  gap: 12px;
}

.crm-page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.crm-page-head h1 {
  margin: 0;
  font-size: 24px;
}

.crm-page-head p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.crm-page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.crm-ws {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  border-radius: 999px;
  padding: 0 10px;
  border: 1px solid #cbd5e1;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
}

.crm-ws.online {
  border-color: #86efac;
  background: #f0fdf4;
  color: #15803d;
}

.crm-loading {
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  color: #64748b;
}

.crm-board-layout {
  display: grid;
  grid-template-columns: 1fr minmax(320px, 420px);
  border: 1px solid #dbe2ea;
  border-radius: 14px;
  overflow: hidden;
  min-height: calc(100vh - 220px);
  background: #ffffff;
}

.crm-board {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  overflow-x: auto;
  padding: 12px;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.crm-empty-panel {
  border-left: 1px solid #dbe2ea;
  background: #ffffff;
  color: #64748b;
  display: grid;
  place-items: center;
  font-size: 13px;
  padding: 16px;
}

@media (max-width: 1180px) {
  .crm-board-layout {
    grid-template-columns: 1fr;
  }
}
</style>
