<template>
  <section class="page reports-page">
    <h1>PDF Отчет</h1>
    <p class="muted">
      Отчет формируется по текущей аналитике клиента и отправляется в Telegram, подключенный в настройках клиента.
    </p>

    <div class="form-card reports-card">
      <button type="button" :disabled="loadingNow || loadingToggle || isSendCooldownActive" @click="handleSendNow">
        {{
          loadingNow
            ? "Формирование..."
            : isSendCooldownActive
              ? "Доступно раз в 5 часов"
              : "Сформировать и отправить сейчас"
        }}
      </button>
      <p v-if="isSendCooldownActive" class="muted">Следующая отправка: {{ cooldownUntilText }}</p>

      <button type="button" :disabled="loadingNow || loadingToggle" @click="handleToggleDaily">
        {{
          loadingToggle
            ? "Сохранение..."
            : dailyEnabled
              ? "Отключить ежедневный отчет в 20:00 (МСК)"
              : "Включить ежедневный отчет в 20:00 (МСК)"
        }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { getDailyPdfStatus, sendPdfNow, toggleDailyPdf } from "../services/reports";

const dailyEnabled = ref(false);
const loadingNow = ref(false);
const loadingToggle = ref(false);
const error = ref("");
const success = ref("");

const SEND_COOLDOWN_MS = 5 * 60 * 60 * 1000;
const SEND_COOLDOWN_KEY = "reports_send_now_cooldown_until";
const cooldownUntil = ref(0);

const isSendCooldownActive = computed(() => Date.now() < cooldownUntil.value);
const cooldownUntilText = computed(() => {
  if (!cooldownUntil.value) {
    return "-";
  }
  return new Date(cooldownUntil.value).toLocaleString();
});

async function handleSendNow() {
  if (isSendCooldownActive.value) {
    error.value = `Отправка доступна раз в 5 часов. Следующая попытка: ${cooldownUntilText.value}.`;
    success.value = "";
    return;
  }

  loadingNow.value = true;
  error.value = "";
  success.value = "";
  try {
    await sendPdfNow();
    cooldownUntil.value = Date.now() + SEND_COOLDOWN_MS;
    localStorage.setItem(SEND_COOLDOWN_KEY, String(cooldownUntil.value));
    success.value = "PDF отчет сформирован и отправлен в Telegram.";
  } catch (err) {
    error.value = err?.response?.data?.detail || "Не удалось сформировать и отправить PDF отчет.";
  } finally {
    loadingNow.value = false;
  }
}

async function handleToggleDaily() {
  loadingToggle.value = true;
  error.value = "";
  success.value = "";
  try {
    const nextEnabled = !dailyEnabled.value;
    const response = await toggleDailyPdf(nextEnabled);
    dailyEnabled.value = !!response.daily_pdf_enabled;
    success.value = dailyEnabled.value
      ? "Ежедневный PDF отчет включен на 20:00 (МСК)."
      : "Ежедневный PDF отчет отключен.";
  } catch (err) {
    error.value = err?.response?.data?.detail || "Не удалось обновить режим ежедневного отчета.";
  } finally {
    loadingToggle.value = false;
  }
}

onMounted(async () => {
  const storedCooldownUntil = Number(localStorage.getItem(SEND_COOLDOWN_KEY) || 0);
  cooldownUntil.value = Number.isFinite(storedCooldownUntil) ? storedCooldownUntil : 0;

  try {
    const response = await getDailyPdfStatus();
    dailyEnabled.value = !!response.daily_pdf_enabled;
  } catch (_) {
    // Leave default state when status loading fails.
  }
});
</script>

<style scoped>
.reports-page {
  max-width: 52rem;
}

.reports-card {
  gap: 0.9rem;
}
</style>