<template>
  <div class="auth-page">
    <form class="auth-card" @submit.prevent="onSubmit">
      <h1>Вход</h1>
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Пароль" required />
      <button type="submit" :disabled="loading">{{ loading ? "Загрузка..." : "Войти" }}</button>
      <p v-if="error" class="error">{{ error }}</p>
      <router-link to="/register">Создать аккаунт</router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function onSubmit() {
  loading.value = true;
  error.value = "";
  try {
    await auth.login(email.value, password.value);
    router.push("/dashboard");
  } catch (_) {
    error.value = auth.error || "Ошибка входа.";
  } finally {
    loading.value = false;
  }
}
</script>
