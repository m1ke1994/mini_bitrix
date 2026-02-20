<template>
  <div class="shell">
    <header class="mobile-header">
      <button class="burger" type="button" @click="isMenuOpen = !isMenuOpen" aria-label="Открыть меню">
        ☰
      </button>
      <h2 class="mobile-logo">TrackNode Analytics</h2>
      <button
        v-if="isDashboardRoute"
        class="refresh-icon-btn"
        type="button"
        :disabled="isRefreshing"
        aria-label="Обновить данные"
        @click="manualRefresh"
      >
        <svg class="refresh-icon" :class="{ spin: isRefreshing }" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M17.65 6.35A7.95 7.95 0 0012 4V1L7 6l5 5V7a5 5 0 11-5 5H5a7 7 0 107-7c1.61 0 3.09.59 4.24 1.56l1.41-1.41z"
            fill="currentColor"
          />
        </svg>
      </button>
      <button v-else class="logout compact" @click="logout">Выйти</button>
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
        <div class="content-actions">
          <button
            v-if="isDashboardRoute"
            class="refresh-btn"
            type="button"
            :disabled="isRefreshing"
            @click="manualRefresh"
          >
            <svg class="refresh-icon" :class="{ spin: isRefreshing }" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M17.65 6.35A7.95 7.95 0 0012 4V1L7 6l5 5V7a5 5 0 11-5 5H5a7 7 0 107-7c1.61 0 3.09.59 4.24 1.56l1.41-1.41z"
                fill="currentColor"
              />
            </svg>
            <span>{{ isRefreshing ? "Обновление..." : "Обновить" }}</span>
          </button>
          <div class="content-user">{{ userLabel }}</div>
        </div>
      </header>
      <main class="content-body">
        <slot />
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const isMenuOpen = ref(false);
const isRefreshing = ref(false);

const userLabel = computed(() => auth.userEmail || "Пользователь");
const isDashboardRoute = computed(() => String(route.path || "").startsWith("/dashboard"));

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
  { to: "/account", label: "Аккаунт" },
];

async function logout() {
  await auth.logout();
  isMenuOpen.value = false;
  router.push("/auth");
}

async function manualRefresh() {
  if (isRefreshing.value || !isDashboardRoute.value) return;

  isRefreshing.value = true;
  try {
    await new Promise((resolve) => {
      let settled = false;
      const done = () => {
        if (settled) return;
        settled = true;
        resolve();
      };

      window.dispatchEvent(new CustomEvent("tracknode:manual-refresh", { detail: { done } }));
      window.setTimeout(done, 8000);
    });
  } finally {
    isRefreshing.value = false;
  }
}
</script>
