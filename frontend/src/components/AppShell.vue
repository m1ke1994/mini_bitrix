<template>
  <div class="shell">
    <header class="mobile-header">
      <button class="burger" type="button" @click="isMenuOpen = !isMenuOpen" aria-label="Открыть меню">
        ☰
      </button>
      <h2 class="mobile-logo">TrackNode Analytics</h2>
      <button class="logout compact" @click="logout">Выйти</button>
    </header>

    <div v-if="isMenuOpen" class="mobile-overlay" @click="isMenuOpen = false"></div>

    <aside class="sidebar" :class="{ open: isMenuOpen }">
      <h2 class="logo">TrackNode Analytics</h2>
      <nav class="nav">
        <router-link to="/dashboard" @click="isMenuOpen = false">Панель управления</router-link>
        <router-link to="/dashboard/leads" @click="isMenuOpen = false">Заявки</router-link>
        <router-link to="/dashboard/integration" @click="isMenuOpen = false">Интеграция</router-link>
        <router-link to="/dashboard/settings" @click="isMenuOpen = false">Настройки</router-link>
      </nav>
      <button class="logout" @click="logout">Выйти</button>
    </aside>

    <main class="content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const isMenuOpen = ref(false);

async function logout() {
  await auth.logout();
  isMenuOpen.value = false;
  router.push("/login");
}
</script>
