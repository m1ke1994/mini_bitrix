<template>
  <div class="auth-page">
    <form class="auth-card" @submit.prevent="onSubmit">
      <h1>Регистрация</h1>
      <input v-model="companyName" type="text" placeholder="Название компании" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" minlength="8" placeholder="Пароль" required />
      <button type="submit" :disabled="loading">{{ loading ? "Загрузка..." : "Создать аккаунт" }}</button>
      <p v-if="error" class="error">{{ error }}</p>
      <router-link to="/login">Уже есть аккаунт?</router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const companyName = ref("");
const email = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function onSubmit() {
  loading.value = true;
  error.value = "";
  try {
    await auth.register(email.value, password.value, companyName.value);
    router.push("/dashboard");
  } catch (_) {
    error.value = auth.error || "Ошибка регистрации.";
  } finally {
    loading.value = false;
  }
}
</script>
