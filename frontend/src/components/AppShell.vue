<template>
  <div class="shell">
    <aside class="sidebar">
      <h2 class="logo">Mini SaaS</h2>
      <nav class="nav">
        <router-link to="/dashboard">Панель управления</router-link>
        <router-link to="/dashboard/leads">Заявки</router-link>
        <router-link to="/dashboard/integration">Интеграция</router-link>
        <router-link to="/dashboard/settings">Настройки</router-link>
      </nav>
      <button class="logout" @click="logout">Выйти</button>
    </aside>
    <main class="content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

async function logout() {
  await auth.logout();
  router.push("/login");
}
</script>
