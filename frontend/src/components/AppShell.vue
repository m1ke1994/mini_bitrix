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
        <router-link
          v-for="item in mainNavItems"
          :key="item.to"
          :to="item.to"
          active-class=""
          exact-active-class="router-link-active"
          @click="isMenuOpen = false"
        >
          {{ item.label }}
        </router-link>
      </nav>

      <div class="nav-secondary">
        <router-link to="/instructions" active-class="" exact-active-class="router-link-active" @click="isMenuOpen = false">
          Инструкции по подключению
        </router-link>
        <router-link to="/about" active-class="" exact-active-class="router-link-active" @click="isMenuOpen = false">
          О проекте
        </router-link>
        <a href="https://t.me/M1ke994" target="_blank" rel="noopener noreferrer" @click="isMenuOpen = false">
          Telegram
        </a>
      </div>

      <button class="logout" @click="logout">Выйти</button>
    </aside>

    <section class="content">
      <header class="content-header">
        <div class="content-title">TrackNode Analytics</div>
        <div class="content-user">{{ userLabel }}</div>
      </header>
      <main class="content-body">
        <slot />
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const isMenuOpen = ref(false);

const userLabel = computed(() => auth.userEmail || "Пользователь");

const mainNavItems = [
  { to: "/dashboard", label: "Обзор" },
  { to: "/dashboard/dynamics", label: "Динамика по дням" },
  { to: "/dashboard/sources", label: "Топ источников" },
  { to: "/dashboard/unique", label: "Уникальные пользователи" },
  { to: "/dashboard/clicks", label: "Топ кликов" },
  { to: "/dashboard/pages-conversion", label: "Конверсия по страницам" },
  { to: "/dashboard/devices", label: "Устройства" },
  { to: "/reports", label: "Отчёт PDF" },
  { to: "/leads", label: "Заявки" },
  { to: "/integration", label: "Интеграции" },
  { to: "/settings", label: "Настройки" },
];

async function logout() {
  await auth.logout();
  isMenuOpen.value = false;
  router.push("/auth");
}
</script>
