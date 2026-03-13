<template>
  <section class="auth-page">
    <div class="auth-card not-found-card">
      <h1>404</h1>
      <p class="muted">Страница не найдена</p>
      <router-link class="button" to="/">Вернуться на главную</router-link>
    </div>
  </section>
</template>

<style scoped>
.not-found-card {
  text-align: center;
  align-items: center;
}

.not-found-card h1 {
  margin: 0;
  font-size: 64px;
  line-height: 1;
}
</style>
