<template>
  <main class="public-page">
    <section class="hero">
      <p class="label">TrackNode</p>
      <h1>SaaS аналитика сайтов и воронка лидогенерации</h1>
      <p class="lead">
        Отслеживайте заявки, путь клиента и результат рекламы в одном кабинете. Подключение без сложной интеграции,
        отчёты и Telegram-уведомления в реальном времени.
      </p>
      <div class="actions">
        <router-link to="/login" class="btn primary">Войти</router-link>
        <router-link to="/register" class="btn ghost">Создать аккаунт</router-link>
      </div>
    </section>
  </main>
</template>

<style scoped>
.public-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 2rem 1rem;
  background: radial-gradient(circle at top right, #f5f9ff 0%, #ffffff 40%, #eff6ff 100%);
}

.hero {
  width: 100%;
  max-width: 60rem;
  text-align: center;
}

.label {
  margin: 0 0 0.5rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #1e40af;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 6vw, 3.5rem);
  line-height: 1.1;
  color: #111827;
}

.lead {
  margin: 1.25rem auto 0;
  max-width: 44rem;
  color: #374151;
  font-size: 1.05rem;
}

.actions {
  margin-top: 1.8rem;
  display: inline-flex;
  gap: 0.8rem;
}

.btn {
  text-decoration: none;
  border-radius: 999px;
  padding: 0.72rem 1.1rem;
  font-weight: 700;
}

.btn.primary {
  background: #2563eb;
  color: #ffffff;
}

.btn.ghost {
  border: 1px solid #2563eb;
  color: #1e40af;
}
</style>
