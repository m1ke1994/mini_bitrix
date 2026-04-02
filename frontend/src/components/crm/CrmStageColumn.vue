<template>
  <section class="crm-stage-column">
    <header class="crm-stage-header">
      <div class="crm-stage-badge" :style="badgeStyle"></div>
      <div>
        <h3>{{ stage.name }}</h3>
        <p>{{ leadsCountLabel }}</p>
      </div>
    </header>

    <draggable
      class="crm-stage-list"
      :list="mutableLeads"
      item-key="id"
      group="crm-leads"
      :animation="180"
      ghost-class="crm-ghost"
      drag-class="crm-drag"
      @change="onListChange"
    >
      <template #item="{ element }">
        <LeadCard :lead="element" @open="$emit('open', $event)" />
      </template>
      <template #footer>
        <div v-if="!mutableLeads.length" class="crm-stage-empty">No leads in this stage</div>
      </template>
    </draggable>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import draggable from "vuedraggable";
import LeadCard from "~/components/crm/LeadCard.vue";

const props = defineProps({
  stage: {
    type: Object,
    required: true,
  },
  leads: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["move", "open"]);

const mutableLeads = ref([]);

watch(
  () => props.leads,
  (next) => {
    mutableLeads.value = Array.isArray(next) ? [...next] : [];
  },
  { immediate: true, deep: true }
);

const leadsCountLabel = computed(() => {
  return `${mutableLeads.value.length} lead${mutableLeads.value.length === 1 ? "" : "s"}`;
});

const badgeStyle = computed(() => {
  return {
    background: props.stage?.color || "#3B82F6",
  };
});

function onListChange(eventPayload) {
  const movedLead = eventPayload?.added?.element;
  if (!movedLead || !movedLead.id) return;

  emit("move", {
    leadId: Number(movedLead.id),
    toStageId: Number(props.stage.id),
  });
}
</script>

<style scoped>
.crm-stage-column {
  min-width: 280px;
  max-width: 320px;
  display: grid;
  gap: 12px;
  background: #f8fafc;
  border: 1px solid #dbe2ea;
  border-radius: 14px;
  padding: 10px;
  max-height: calc(100vh - 240px);
}

.crm-stage-header {
  display: flex;
  gap: 10px;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 8px;
}

.crm-stage-badge {
  width: 10px;
  height: 36px;
  border-radius: 99px;
}

.crm-stage-header h3 {
  margin: 0;
  font-size: 15px;
}

.crm-stage-header p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #64748b;
}

.crm-stage-list {
  display: grid;
  gap: 8px;
  overflow-y: auto;
  min-height: 48px;
  padding-right: 3px;
}

.crm-stage-empty {
  border: 1px dashed #cbd5e1;
  color: #64748b;
  border-radius: 10px;
  font-size: 12px;
  padding: 10px;
  text-align: center;
}

.crm-ghost {
  opacity: 0.4;
}

.crm-drag {
  transform: rotate(1deg);
}
</style>
