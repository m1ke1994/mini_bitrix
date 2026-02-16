<template>
  <section class="page">
    <h1>Отчёт PDF</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">{{ success }}</p>

    <div class="form-card">
      <label>
        <input type="checkbox" v-model="form.enabled" @change="saveSettings" />
        Автоматический ежедневный отчёт
      </label>

      <label>Время отправки</label>
      <input type="time" v-model="form.daily_time" @change="saveSettings" />

      <label>Таймзона</label>
      <input type="text" v-model="form.timezone" @blur="saveSettings" placeholder="Europe/Moscow" />

      <hr />

      <label>
        <input type="checkbox" v-model="form.send_email" @change="saveSettings" />
        Отправлять на Email
      </label>

      <label>Email для отчётов</label>
      <input
        type="email"
        v-model="form.email_to"
        @blur="saveSettings"
        :disabled="!form.send_email"
        placeholder="owner@example.com"
      />

      <hr />

      <label>
        <input type="checkbox" v-model="form.send_telegram" @change="saveSettings" />
        Отправлять в Telegram
      </label>

      <p>
        <strong>Статус Telegram:</strong>
        <span v-if="form.telegram_is_connected">подключён</span>
        <span v-else>не подключён</span>
      </p>
      <p v-if="form.telegram_is_connected">
        <strong>Профиль:</strong>
        {{ form.telegram_username ? "@" + form.telegram_username : "без username" }}
        (chat_id: {{ form.telegram_chat_id }})
      </p>

      <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px">
        <button type="button" @click="connectTelegram">Подключить Telegram</button>
        <button type="button" @click="disconnectTelegramNow" :disabled="!form.telegram_is_connected">Отключить Telegram</button>
      </div>

      <p v-if="connectInfo.command">
        Откройте бота и нажмите Start, затем отправьте команду:
        <code>{{ connectInfo.command }}</code>
      </p>
      <p v-if="connectInfo.bot_link">
        Бот: <a :href="connectInfo.bot_link" target="_blank" rel="noopener noreferrer">{{ connectInfo.bot_link }}</a>
      </p>
      <p v-if="connectInfo.expires_at">Код действует до: {{ formatDateTime(connectInfo.expires_at) }}</p>

      <hr />

      <button type="button" :disabled="loading" @click="sendNow">Отправить сейчас</button>

      <hr />

      <p><strong>Последняя отправка:</strong> {{ formatDateTime(form.last_sent_at) }}</p>
      <p><strong>Статус:</strong> {{ form.last_status || "-" }}</p>
      <p v-if="form.last_error"><strong>Ошибка:</strong> {{ form.last_error }}</p>
      <p v-if="latestLog?.id">
        <strong>Лог:</strong> #{{ latestLog.id }} ({{ latestLog.status }})
        <span v-if="latestLog.delivery_channels">каналы: {{ latestLog.delivery_channels }}</span>
      </p>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import {
  disconnectTelegram,
  generateReportNow,
  getLatestReportLog,
  getReportSettings,
  startTelegramConnect,
  updateReportSettings,
} from "../services/reports";

const form = ref({
  enabled: false,
  daily_time: "09:00",
  timezone: "Europe/Moscow",
  send_email: true,
  email_to: "",
  send_telegram: false,
  telegram_chat_id: "",
  telegram_username: "",
  telegram_is_connected: false,
  last_sent_at: null,
  last_status: "idle",
  last_error: "",
});
const connectInfo = ref({
  command: "",
  bot_link: "",
  expires_at: null,
});
const latestLog = ref(null);
const loading = ref(false);
const error = ref("");
const success = ref("");

function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("ru-RU");
}

function applySettings(data) {
  form.value = {
    ...form.value,
    ...data,
    daily_time: (data.daily_time || form.value.daily_time || "09:00").slice(0, 5),
  };
}

async function loadPage() {
  error.value = "";
  success.value = "";
  try {
    const [settingsData, logData] = await Promise.all([getReportSettings(), getLatestReportLog()]);
    applySettings(settingsData);
    latestLog.value = logData?.id ? logData : null;
  } catch (err) {
    error.value = "Ошибка загрузки настроек отчётов.";
  }
}

async function saveSettings() {
  error.value = "";
  success.value = "";
  try {
    const payload = {
      enabled: !!form.value.enabled,
      daily_time: form.value.daily_time,
      timezone: (form.value.timezone || "Europe/Moscow").trim(),
      send_email: !!form.value.send_email,
      email_to: (form.value.email_to || "").trim() || null,
      send_telegram: !!form.value.send_telegram,
    };
    const data = await updateReportSettings(payload);
    applySettings(data);
    success.value = "Настройки сохранены.";
  } catch (err) {
    error.value =
      err?.response?.data?.email_to?.[0] ||
      err?.response?.data?.send_telegram?.[0] ||
      err?.response?.data?.enabled?.[0] ||
      "Не удалось сохранить настройки отчёта.";
  }
}

async function connectTelegram() {
  error.value = "";
  success.value = "";
  try {
    const data = await startTelegramConnect();
    connectInfo.value = {
      command: data.command || "",
      bot_link: data.bot_link || "",
      expires_at: data.expires_at || null,
    };
    success.value = "Код привязки создан. Отправьте команду боту.";
  } catch (err) {
    error.value = "Не удалось начать привязку Telegram.";
  }
}

async function disconnectTelegramNow() {
  error.value = "";
  success.value = "";
  try {
    await disconnectTelegram();
    form.value.send_telegram = false;
    form.value.telegram_is_connected = false;
    form.value.telegram_chat_id = "";
    form.value.telegram_username = "";
    success.value = "Telegram отключён.";
  } catch (err) {
    error.value = "Не удалось отключить Telegram.";
  }
}

async function sendNow() {
  loading.value = true;
  error.value = "";
  success.value = "";
  try {
    const response = await generateReportNow({});
    const blob = new Blob([response.data], { type: "application/pdf" });
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const fileName =
      response.headers["content-disposition"]
        ?.split("filename=")
        ?.pop()
        ?.replaceAll('"', "") || "tracknode-report.pdf";
    link.href = objectUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(objectUrl);

    const deliveryStatus = response.headers["x-report-delivery-status"] || "unknown";
    const channels = response.headers["x-report-delivery-channels"] || "-";
    success.value = `Отчёт сформирован и скачан. Статус доставки: ${deliveryStatus}. Каналы: ${channels}.`;
    await loadPage();
  } catch (err) {
    error.value = "Ошибка формирования отчёта.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadPage);
</script>
