import { defineStore } from "pinia";
import {
  addLeadNote,
  fetchAllLeads,
  fetchLeadActivities,
  fetchPipelines,
  fetchWidgetVariants,
  moveLead,
  scheduleLead,
} from "~/services/crm";

function cloneLead(lead) {
  return { ...(lead || {}) };
}

function extractLeadPayload(payload) {
  if (!payload || typeof payload !== "object") return null;
  return payload.payload || payload.lead || payload.data || payload;
}

function normalizeLead(lead) {
  const raw = cloneLead(lead);

  const stageIdCandidate = raw.stage_id ?? raw.stage ?? raw.stageId ?? null;
  const parsedStageId = Number(stageIdCandidate);

  if (Number.isFinite(parsedStageId) && parsedStageId > 0) {
    raw.stage = parsedStageId;
    raw.stage_id = parsedStageId;
  } else {
    raw.stage = null;
    raw.stage_id = null;
  }

  if (!raw.stage_name && typeof raw.stageName === "string") {
    raw.stage_name = raw.stageName;
  }

  raw.id = Number(raw.id);
  raw.score = Number(raw.score || 0);

  return raw;
}

export const useCrmStore = defineStore("crm", {
  state: () => ({
    pipelines: [],
    leads: [],
    leadsByStage: {},
    activitiesByLead: {},
    selectedLeadId: null,
    widgetVariants: [],
    loading: false,
    loadingActivities: false,
    error: "",
  }),
  getters: {
    stages(state) {
      const first = state.pipelines[0] || {};
      const stages = Array.isArray(first.stages) ? first.stages : [];
      return stages
        .map((item) => ({ ...item, id: Number(item.id) }))
        .sort((a, b) => Number(a.order || 0) - Number(b.order || 0));
    },
    selectedLead(state) {
      return state.leads.find((lead) => Number(lead.id) === Number(state.selectedLeadId)) || null;
    },
    selectedActivities(state) {
      const key = String(state.selectedLeadId || "");
      return state.activitiesByLead[key] || [];
    },
  },
  actions: {
    _rebuildBoard() {
      const nextMap = {};
      const fallbackStage = this.stages[0] || null;
      this.stages.forEach((stage) => {
        nextMap[String(stage.id)] = [];
      });

      this.leads.forEach((lead) => {
        const normalized = normalizeLead(lead);
        const effectiveStageId = normalized.stage_id || fallbackStage?.id || null;
        if (effectiveStageId && !normalized.stage_id) {
          normalized.stage_id = Number(effectiveStageId);
          normalized.stage = Number(effectiveStageId);
          if (!normalized.stage_name && fallbackStage?.name) {
            normalized.stage_name = fallbackStage.name;
            normalized.stage_color = fallbackStage.color || normalized.stage_color;
          }
        }
        const key = String(effectiveStageId || "");
        if (!nextMap[key]) nextMap[key] = [];
        nextMap[key].push(normalized);
      });

      Object.keys(nextMap).forEach((key) => {
        nextMap[key].sort((a, b) => Number(b.score || 0) - Number(a.score || 0));
      });
      this.leadsByStage = nextMap;
    },

    upsertLead(lead) {
      const next = normalizeLead(lead);
      if (!Number.isFinite(next.id) || next.id <= 0) {
        return;
      }

      const idx = this.leads.findIndex((item) => Number(item.id) === Number(next.id));
      if (idx === -1) {
        this.leads.unshift(next);
      } else {
        this.leads.splice(idx, 1, { ...this.leads[idx], ...next });
      }
      this._rebuildBoard();
    },

    async loadCrm() {
      this.loading = true;
      this.error = "";
      try {
        const [pipelines, leads, variants] = await Promise.all([
          fetchPipelines(),
          fetchAllLeads(),
          fetchWidgetVariants(),
        ]);
        this.pipelines = pipelines;
        this.leads = Array.isArray(leads) ? leads.map(normalizeLead) : [];
        this.widgetVariants = variants;
        this._rebuildBoard();
      } catch (_error) {
        this.error = "Не удалось загрузить данные CRM.";
      } finally {
        this.loading = false;
      }
    },

    async moveLeadWithOptimistic(leadId, stageId) {
      const current = this.leads.find((lead) => Number(lead.id) === Number(leadId));
      if (!current) return;
      const previous = cloneLead(current);
      const stage = this.stages.find((item) => Number(item.id) === Number(stageId));
      this.upsertLead({
        ...current,
        stage: Number(stageId),
        stage_id: Number(stageId),
        stage_name: stage?.name || current.stage_name,
        stage_color: stage?.color || current.stage_color,
      });

      try {
        const updated = await moveLead(leadId, stageId);
        this.upsertLead(updated);
      } catch (error) {
        this.upsertLead(previous);
        throw error;
      }
    },

    async selectLead(leadId) {
      this.selectedLeadId = Number(leadId);
      await this.loadActivities(leadId);
    },

    async loadActivities(leadId) {
      this.loadingActivities = true;
      try {
        const items = await fetchLeadActivities(leadId);
        this.activitiesByLead[String(leadId)] = items;
      } finally {
        this.loadingActivities = false;
      }
    },

    async createNote(leadId, note) {
      const updatedLead = await addLeadNote(leadId, note);
      this.upsertLead(updatedLead);
      await this.loadActivities(leadId);
    },

    async createSchedule(leadId, nextContactAt, note) {
      const updatedLead = await scheduleLead(leadId, nextContactAt, note);
      this.upsertLead(updatedLead);
      await this.loadActivities(leadId);
    },

    applyRealtimePayload(payload) {
      const lead = extractLeadPayload(payload);
      if (!lead || !lead.id) return;
      this.upsertLead(lead);
    },
  },
});
