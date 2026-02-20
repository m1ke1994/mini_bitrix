<template>
  <section class="page">
    <h1>Аккаунт</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">Пароль обновлён</p>

    <div class="form-card">
      <label for="current-password">Текущий пароль</label>
      <input id="current-password" v-model="currentPassword" type="password" autocomplete="current-password" />

      <label for="new-password">Новый пароль</label>
      <input id="new-password" v-model="newPassword" type="password" autocomplete="new-password" />

      <label for="confirm-password">Подтверждение нового пароля</label>
      <input id="confirm-password" v-model="confirmPassword" type="password" autocomplete="new-password" />

      <button type="button" :disabled="loading" @click="changePassword">
        {{ loading ? "Обновление..." : "Обновить пароль" }}
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";
import api from "../services/api";

const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const error = ref("");
const success = ref(false);

function extractErrorMessage(err) {
  const data = err?.response?.data || {};
  if (typeof data.error === "string" && data.error) return data.error;
  const errors = data.errors || {};
  const firstField = Object.keys(errors)[0];
  if (firstField && Array.isArray(errors[firstField]) && errors[firstField][0]) {
    return String(errors[firstField][0]);
  }
  if (typeof data.detail === "string" && data.detail) return data.detail;
  return "Ошибка смены пароля.";
}

async function changePassword() {
  error.value = "";
  success.value = false;

  if (!currentPassword.value || !newPassword.value || !confirmPassword.value) {
    error.value = "Заполните все поля.";
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = "Подтверждение пароля не совпадает.";
    return;
  }

  loading.value = true;
  try {
    await api.post("/api/auth/change-password/", {
      current_password: currentPassword.value,
      new_password: newPassword.value,
    });
    success.value = true;
    currentPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  } catch (err) {
    error.value = extractErrorMessage(err);
  } finally {
    loading.value = false;
  }
}
</script>
