<template>
  <section class="page">
    <h1>Аккаунт</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">Пароль обновлён</p>

    <div class="form-card">
      <label for="current-password">Текущий пароль</label>
            <div class="password-field">
        <input
          id="current-password"
          v-model="currentPassword"
          :type="showCurrent ? 'text' : 'password'"
          autocomplete="current-password"
        />
        <button
          type="button"
          class="eye-toggle"
          :aria-label="showCurrent ? 'Hide password' : 'Show password'"
          @click="showCurrent = !showCurrent"
        >
          <svg v-if="!showCurrent" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M12 4.5C7 4.5 2.7 7.6 1 12c1.7 4.4 6 7.5 11 7.5s9.3-3.1 11-7.5c-1.7-4.4-6-7.5-11-7.5zm0 12.5a5 5 0 110-10 5 5 0 010 10z"
              fill="currentColor"
            />
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M3 5l17 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <path d="M12 6a6 6 0 016 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <label for="new-password">Новый пароль</label>
            <div class="password-field">
        <input
          id="new-password"
          v-model="newPassword"
          :type="showNew ? 'text' : 'password'"
          autocomplete="new-password"
        />
        <button
          type="button"
          class="eye-toggle"
          :aria-label="showNew ? 'Hide password' : 'Show password'"
          @click="showNew = !showNew"
        >
          <svg v-if="!showNew" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M12 4.5C7 4.5 2.7 7.6 1 12c1.7 4.4 6 7.5 11 7.5s9.3-3.1 11-7.5c-1.7-4.4-6-7.5-11-7.5zm0 12.5a5 5 0 110-10 5 5 0 010 10z"
              fill="currentColor"
            />
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M3 5l17 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <path d="M12 6a6 6 0 016 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <label for="confirm-password">Подтверждение нового пароля</label>
            <div class="password-field">
        <input
          id="confirm-password"
          v-model="confirmPassword"
          :type="showConfirm ? 'text' : 'password'"
          autocomplete="new-password"
        />
        <button
          type="button"
          class="eye-toggle"
          :aria-label="showConfirm ? 'Hide password' : 'Show password'"
          @click="showConfirm = !showConfirm"
        >
          <svg v-if="!showConfirm" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M12 4.5C7 4.5 2.7 7.6 1 12c1.7 4.4 6 7.5 11 7.5s9.3-3.1 11-7.5c-1.7-4.4-6-7.5-11-7.5zm0 12.5a5 5 0 110-10 5 5 0 010 10z"
              fill="currentColor"
            />
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M3 5l17 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <path d="M12 6a6 6 0 016 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
      </div>

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
const showCurrent = ref(false);
const showNew = ref(false);
const showConfirm = ref(false);
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
    error.value = "\u0417\u0430\u043F\u043E\u043B\u043D\u0438\u0442\u0435 \u0432\u0441\u0435 \u043F\u043E\u043B\u044F.";
    return;
  }
  if (newPassword.value.length < 8) {
    error.value = "\u041D\u043E\u0432\u044B\u0439 \u043F\u0430\u0440\u043E\u043B\u044C \u0434\u043E\u043B\u0436\u0435\u043D \u0441\u043E\u0434\u0435\u0440\u0436\u0430\u0442\u044C \u043C\u0438\u043D\u0438\u043C\u0443\u043C 8 \u0441\u0438\u043C\u0432\u043E\u043B\u043E\u0432.";
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
<style scoped>
.password-field {
  position: relative;
}

.password-field input {
  padding-right: 2.8rem;
}

.eye-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #888;
  padding: 0;
  min-height: 20px;
  min-width: 20px;
  box-shadow: none;
}

.eye-toggle:hover {
  filter: none;
  color: #59616d;
}
</style>
