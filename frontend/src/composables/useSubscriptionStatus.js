import { computed, readonly, ref } from "vue";
import { getSubscriptionStatus } from "../services/subscription";
import { useAuthStore } from "../stores/auth";

const CACHE_KEY = "tracknode:subscription-status:v1";

const status = ref("unknown");
const isTrial = ref(false);
const paidUntil = ref(null);
const isLoading = ref(false);
const hasLoadedOnce = ref(false);
const lastUpdatedAt = ref(0);

let inflightRequest = null;

hydrateFromSession();

function hydrateFromSession() {
  if (typeof window === "undefined") return;

  try {
    const raw = window.sessionStorage.getItem(CACHE_KEY);
    if (!raw) return;

    const cached = JSON.parse(raw);
    if (!cached || typeof cached !== "object") return;

    status.value = cached.status === "active" ? "active" : "expired";
    isTrial.value = Boolean(cached.isTrial);
    paidUntil.value = cached.paidUntil || null;
    hasLoadedOnce.value = true;
    lastUpdatedAt.value = Number(cached.updatedAt) || 0;
  } catch {
    // Ignore malformed cache and continue with a network refresh.
  }
}

function persistToSession() {
  if (typeof window === "undefined") return;

  try {
    if (!hasLoadedOnce.value) {
      window.sessionStorage.removeItem(CACHE_KEY);
      return;
    }

    window.sessionStorage.setItem(
      CACHE_KEY,
      JSON.stringify({
        status: status.value,
        isTrial: isTrial.value,
        paidUntil: paidUntil.value,
        updatedAt: lastUpdatedAt.value,
      })
    );
  } catch {
    // Ignore storage quota / access errors.
  }
}

function clearSubscriptionStatus() {
  status.value = "unknown";
  isTrial.value = false;
  paidUntil.value = null;
  hasLoadedOnce.value = false;
  lastUpdatedAt.value = 0;
  persistToSession();
}

function applySubscriptionStatus(payload) {
  status.value = payload?.status === "active" ? "active" : "expired";
  isTrial.value = Boolean(payload?.is_trial);
  paidUntil.value = payload?.paid_until ?? null;
  hasLoadedOnce.value = true;
  lastUpdatedAt.value = Date.now();
  persistToSession();
}

function applyExpiredFallback() {
  status.value = "expired";
  isTrial.value = false;
  paidUntil.value = null;
  hasLoadedOnce.value = true;
  lastUpdatedAt.value = Date.now();
  persistToSession();
}

function getSnapshot() {
  return {
    status: status.value,
    isTrial: isTrial.value,
    paidUntil: paidUntil.value,
    hasLoadedOnce: hasLoadedOnce.value,
    isLoading: isLoading.value,
  };
}

export async function refreshSubscriptionStatus(options = {}) {
  const { force = false, maxAgeMs = 60_000 } = options;
  const auth = useAuthStore();

  if (!auth.isAuthenticated) {
    clearSubscriptionStatus();
    return getSnapshot();
  }

  const isFresh = hasLoadedOnce.value && Date.now() - lastUpdatedAt.value < maxAgeMs;
  if (!force && isFresh) {
    return getSnapshot();
  }

  if (!force && inflightRequest) {
    return inflightRequest;
  }

  isLoading.value = true;
  inflightRequest = (async () => {
    try {
      const payload = await getSubscriptionStatus();
      applySubscriptionStatus(payload);
    } catch {
      applyExpiredFallback();
    } finally {
      isLoading.value = false;
      inflightRequest = null;
    }

    return getSnapshot();
  })();

  return inflightRequest;
}

export function primeSubscriptionStatus(options) {
  void refreshSubscriptionStatus(options).catch(() => {});
}

export function useSubscriptionStatus() {
  return {
    status: readonly(status),
    isTrial: readonly(isTrial),
    paidUntil: readonly(paidUntil),
    isLoading: readonly(isLoading),
    hasLoadedOnce: readonly(hasLoadedOnce),
    isExpired: computed(() => hasLoadedOnce.value && status.value !== "active"),
    trialActive: computed(() => status.value === "active" && isTrial.value === true),
    refreshSubscriptionStatus,
    primeSubscriptionStatus,
  };
}
