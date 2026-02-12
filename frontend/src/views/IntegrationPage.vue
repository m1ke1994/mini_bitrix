<template>
  <AppShell>
    <section class="page">
      <h1>Интеграция</h1>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="copied" class="success">Скрипт скопирован</p>

      <div class="form-card">
        <label>URL трекера</label>
        <input type="text" :value="settings.tracker_script_url" readonly />

        <label>Скрипт подключения</label>
        <textarea :value="settings.public_script_tag" rows="4" readonly />

        <button @click="copyScript">Скопировать</button>
      </div>
    </section>
  </AppShell>
</template>

<script setup>
import { onMounted, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import api from "../services/api";

const settings = ref({
  tracker_script_url: "",
  public_script_tag: "",
});
const error = ref("");
const copied = ref(false);

async function loadSettings() {
  error.value = "";
  try {
    const response = await api.get("/api/client/settings/");
    settings.value = response.data;
  } catch (_) {
    error.value = "Ошибка загрузки настроек интеграции.";
  }
}

async function copyScript() {
  copied.value = false;
  try {
    await navigator.clipboard.writeText(settings.value.public_script_tag || "");
    copied.value = true;
  } catch (_) {
    error.value = "Не удалось скопировать скрипт.";
  }
}

onMounted(loadSettings);
</script>
