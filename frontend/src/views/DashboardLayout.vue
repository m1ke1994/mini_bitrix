<template>
  <AppShell>
    <section class="page dashboard-layout">
      <h1>Панель управления</h1>
      <nav class="dashboard-subnav">
        <router-link to="/dashboard" exact-active-class="active">Обзор</router-link>
        <router-link to="/dashboard/dynamics" class="sub-item">Динамика по дням</router-link>
        <router-link to="/dashboard/sources" class="sub-item">Топ источников</router-link>
        <router-link to="/dashboard/clicks" class="sub-item">Топ кликов</router-link>
        <router-link to="/dashboard/pages-conversion" class="sub-item">Конверсия по страницам</router-link>
      </nav>
      <div class="dashboard-view">
        <router-view />
      </div>
    </section>
  </AppShell>
</template>

<script setup>
import AppShell from "../components/AppShell.vue";
</script>
