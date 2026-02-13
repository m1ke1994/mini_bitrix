<template>
  <section class="page">
    <h1>Настройки</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="saved" class="success">Сохранено</p>

    <div class="form-card">
      <label>API ключ</label>
      <input type="text" :value="settings.api_key" readonly />

      <label>Статус Telegram</label>
      <input type="text" :value="settings.telegram_status === 'connected' ? 'Подключен' : 'Не подключен'" readonly />

      <label>Telegram Chat ID</label>
      <input type="text" :value="settings.telegram_chat_id || '-'" readonly />

      <a v-if="settings.telegram_connect_url" :href="settings.telegram_connect_url" target="_blank" rel="noopener">
        <button type="button">Подключить Telegram</button>
      </a>

      <label class="checkbox">
        <input v-model="settings.send_to_telegram" type="checkbox" />
        <span>Отправлять уведомления о заявках в Telegram</span>
      </label>

      <button @click="save">Сохранить</button>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../services/api";

const settings = ref({
  api_key: "",
  telegram_chat_id: "",
  telegram_status: "not_connected",
  telegram_connect_url: "",
  send_to_telegram: false,
});
const error = ref("");
const saved = ref(false);

async function loadSettings() {
  error.value = "";
  saved.value = false;
  try {
    const response = await api.get("/api/client/settings/");
    settings.value = response.data;
  } catch (_) {
    error.value = "Ошибка загрузки настроек.";
  }
}

async function save() {
  error.value = "";
  saved.value = false;
  try {
    const response = await api.patch("/api/client/settings/", {
      send_to_telegram: settings.value.send_to_telegram,
    });
    settings.value = response.data;
    saved.value = true;
  } catch (_) {
    error.value = "Ошибка сохранения настроек.";
  }
}

onMounted(loadSettings);
</script>
