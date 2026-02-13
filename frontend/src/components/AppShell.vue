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
        <button class="nav-toggle" type="button" @click="toggleDashboard">
          <span>Панель управления</span>
          <span class="nav-toggle-arrow">{{ isDashboardOpen ? "▾" : "▸" }}</span>
        </button>
        <div v-if="isDashboardOpen" class="nav-group">
          <router-link to="/dashboard" @click="isMenuOpen = false">Обзор</router-link>
          <router-link to="/dashboard/dynamics" @click="isMenuOpen = false">Динамика по дням</router-link>
          <router-link to="/dashboard/sources" @click="isMenuOpen = false">Топ источников</router-link>
          <router-link to="/dashboard/clicks" @click="isMenuOpen = false">Топ кликов</router-link>
          <router-link to="/dashboard/pages-conversion" @click="isMenuOpen = false">Конверсия по страницам</router-link>
        </div>
        <router-link to="/leads" @click="isMenuOpen = false">Заявки</router-link>
        <router-link to="/integration" @click="isMenuOpen = false">Интеграция</router-link>
        <router-link to="/settings" @click="isMenuOpen = false">Настройки</router-link>
      </nav>
      <div class="nav-secondary">
        <router-link to="/instructions" @click="isMenuOpen = false">Инструкция по подключению</router-link>
      </div>
      <button class="logout" @click="logout">Выйти</button>
    </aside>

    <main class="content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const isMenuOpen = ref(false);
const manualDashboardOpen = ref(true);
const isDashboardRoute = computed(() => route.path === "/dashboard" || route.path.startsWith("/dashboard/"));
const isDashboardOpen = computed(() => (isDashboardRoute.value ? true : manualDashboardOpen.value));

function toggleDashboard() {
  if (isDashboardRoute.value) {
    manualDashboardOpen.value = true;
    return;
  }
  manualDashboardOpen.value = !manualDashboardOpen.value;
}

async function logout() {
  await auth.logout();
  isMenuOpen.value = false;
  router.push("/login");
}
</script>
