import { computed, onBeforeUnmount, ref } from "vue";
import { useRuntimeConfig } from "#imports";
import { useAuthStore } from "~/stores/auth";

function resolveWsBase() {
  const runtime = useRuntimeConfig();
  const configured = String(runtime?.public?.wsBase || "").trim();
  if (configured) return configured.replace(/\/$/, "");

  const apiBase = String(runtime?.public?.apiBase || "").trim();
  if (/^https?:\/\//i.test(apiBase)) {
    return apiBase.replace(/^http/i, "ws").replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const origin = window.location.origin.replace(/^http/i, "ws");
    return origin;
  }
  return "";
}

export function useLeadsRealtime() {
  const auth = useAuthStore();
  const ws = ref(null);
  const isConnected = ref(false);
  const lastEvent = ref(null);
  const wsBase = computed(() => resolveWsBase());

  function disconnect() {
    if (ws.value) {
      try {
        ws.value.close();
      } catch (_) {}
    }
    ws.value = null;
    isConnected.value = false;
  }

  function connect(onLeadEvent) {
    if (typeof window === "undefined") return;
    const token = String(auth.accessToken || "").trim();
    if (!token) return;

    const base = wsBase.value;
    if (!base) return;

    disconnect();
    const url = `${base}/ws/leads/?token=${encodeURIComponent(token)}`;
    const socket = new WebSocket(url);
    ws.value = socket;

    socket.onopen = () => {
      isConnected.value = true;
    };
    socket.onclose = () => {
      isConnected.value = false;
    };
    socket.onerror = () => {
      isConnected.value = false;
    };
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(String(event.data || "{}"));
        lastEvent.value = payload;
        if (payload?.type === "lead_event" && typeof onLeadEvent === "function") {
          onLeadEvent(payload);
        }
      } catch (_) {}
    };
  }

  onBeforeUnmount(() => {
    disconnect();
  });

  return {
    connect,
    disconnect,
    isConnected,
    lastEvent,
  };
}

