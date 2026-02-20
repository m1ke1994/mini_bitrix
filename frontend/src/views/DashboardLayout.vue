<template>
  <section class="page dashboard-layout">
    <div v-if="loading" class="subscription-screen">
      <div class="subscription-card">
        <h2>Проверка подписки...</h2>
      </div>
    </div>

    <div v-else-if="isExpired" class="subscription-screen">
      <div class="subscription-card">
        <h2>Подписка не активна</h2>
        <p>Для продолжения работы оплатите подписку через YooKassa.</p>
        <button type="button" class="pay-btn" :disabled="payRedirectLoading" @click="goToPaymentCheckout">
          {{ payRedirectLoading ? "Переход..." : "Перейти к оплате" }}
        </button>
      </div>
    </div>

    <template v-else>
      <h1>Панель управления</h1>
      <div v-if="trialActive" class="trial-banner">
        Демо-доступ активен. Осталось: {{ trialDaysLeft }} дн.
        <div>
          <button type="button" class="pay-btn" :disabled="payRedirectLoading" @click="goToPaymentCheckout">
            {{ payRedirectLoading ? "Переход..." : "Оплатить сейчас" }}
          </button>
        </div>
      </div>
      <nav class="dashboard-subnav">
        <router-link to="/dashboard" exact-active-class="active">Обзор</router-link>
        <router-link to="/dashboard/dynamics" class="sub-item">Динамика по дням</router-link>
        <router-link to="/dashboard/unique" class="sub-item">Уникальные пользователи</router-link>
        <router-link to="/dashboard/engagement" class="sub-item">Вовлечённость</router-link>
        <router-link to="/dashboard/sources" class="sub-item">Топ источников</router-link>
        <router-link to="/dashboard/clicks" class="sub-item">Топ кликов</router-link>
        <router-link to="/dashboard/pages-conversion" class="sub-item">Конверсия по страницам</router-link>
        <router-link to="/dashboard/devices" class="sub-item">Устройства</router-link>
      </nav>
      <div class="dashboard-view">
        <router-view v-slot="{ Component }">
          <component :is="Component" ref="activeDashboardView" />
        </router-view>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { getSubscriptionStatus, redirectToYooKassaCheckout } from "../services/subscription";
import { useAuthStore } from "../stores/auth";

const loading = ref(true);
const status = ref("expired");
const isTrial = ref(false);
const paidUntil = ref(null);
const payRedirectLoading = ref(false);
const activeDashboardView = ref(null);

const auth = useAuthStore();
const isExpired = computed(() => status.value !== "active");
const trialActive = computed(() => status.value === "active" && isTrial.value === true);
const trialDaysLeft = computed(() => {
  if (!trialActive.value || !paidUntil.value) return 0;
  const ms = new Date(paidUntil.value).getTime() - Date.now();
  return Math.max(0, Math.ceil(ms / (1000 * 60 * 60 * 24)));
});

async function loadSubscription() {
  if (!auth.isAuthenticated) {
    loading.value = false;
    return;
  }

  loading.value = true;
  try {
    const statusResponse = await getSubscriptionStatus();
    status.value = statusResponse?.status || "expired";
    isTrial.value = Boolean(statusResponse?.is_trial);
    paidUntil.value = statusResponse?.paid_until ?? null;
  } catch (e) {
    status.value = "expired";
    isTrial.value = false;
    paidUntil.value = null;
  } finally {
    loading.value = false;
  }
}

async function goToPaymentCheckout() {
  if (payRedirectLoading.value) return;

  payRedirectLoading.value = true;
  try {
    await redirectToYooKassaCheckout();
  } catch (e) {
    if (e?.message === "NO_ACTIVE_PLANS") {
      alert("Нет активных тарифов для оплаты.");
    } else if (e?.message === "NO_CONFIRMATION_URL") {
      alert("Платеж создан, но ссылка на оплату не получена. Обратитесь в поддержку.");
    } else {
      alert("Не удалось начать оплату. Попробуйте снова.");
    }
  } finally {
    payRedirectLoading.value = false;
  }
}

async function refreshActiveDashboard(event) {
  const refreshFn = activeDashboardView.value?.manualRefresh;

  try {
    if (typeof refreshFn === "function") {
      await refreshFn();
    }
  } finally {
    if (typeof event?.detail?.done === "function") {
      event.detail.done();
    }
  }
}

onMounted(() => {
  loadSubscription();
  window.addEventListener("tracknode:manual-refresh", refreshActiveDashboard);
});

onBeforeUnmount(() => {
  window.removeEventListener("tracknode:manual-refresh", refreshActiveDashboard);
});
</script>

<style scoped>
.subscription-screen {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.subscription-card {
  width: min(38rem, 100%);
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 1rem;
  padding: 1.2rem;
  display: grid;
  gap: 0.8rem;
}

.trial-banner {
  margin: 0.6rem 0 1rem;
  padding: 0.7rem 0.9rem;
  border-radius: 0.6rem;
  background: #ecfeff;
  border: 1px solid #a5f3fc;
  color: #0f766e;
  font-weight: 600;
}

.pay-btn {
  border: 0;
  border-radius: 0.7rem;
  min-height: 2.6rem;
  background: linear-gradient(135deg, #2ba8d8, #4cc9f0);
  color: #fff;
  font-weight: 600;
}

.pay-btn:disabled {
  opacity: 0.65;
}
</style>
