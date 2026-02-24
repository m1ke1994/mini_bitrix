<template>
  <main class="public-page">
    <section class="hero">
      <p class="label">TrackNode</p>
      <h1>Аналитика сайтов и учет заявок в одном сервисе</h1>
      <p class="lead">
        Сервис аналитики помогает отслеживать лиды, путь клиента и результат рекламы в одном кабинете.
        Подключение без сложной интеграции, отчеты и Telegram-уведомления в реальном времени.
      </p>
      <div class="actions">
        <router-link to="/login" class="btn primary">Войти</router-link>
        <router-link to="/register" class="btn ghost">Создать аккаунт</router-link>
      </div>

      <section class="seo-block" aria-label="Описание сервиса TrackNode">
        <h2>Что дает TrackNode бизнесу</h2>
        <p>
          TrackNode помогает бизнесу вести аналитику сайтов и учет заявок в одном интерфейсе без перегруженных CRM-модулей и сложной
          настройки. Сервис аналитики показывает, откуда пришел клиент, какие страницы он просмотрел, где оставил заявку и на каком этапе
          теряется интерес. Вы видите путь пользователя от первого визита до обращения, сравниваете источники трафика и контролируете
          качество лидов в ежедневной работе команды. Это удобно для собственников, маркетологов и менеджеров по продажам, которым нужна
          прозрачная аналитика воронки продаж и быстрые действия по данным, а не ручные отчеты в таблицах.
        </p>
        <p>
          Платформа подходит для малого и среднего бизнеса: помогает настроить отслеживание конверсии по ключевым страницам, оценить
          эффективность рекламы, вовремя реагировать на заявки и получать уведомления в Telegram. При этом данные остаются в одном кабинете,
          а отчеты читаются без технической подготовки. Если вам нужен инструмент, который объединяет аналитику сайтов, учет заявок и
          контроль результата по воронке, TrackNode закрывает эти задачи без смены текущих процессов.
        </p>
      </section>
    </section>
  </main>
</template>

<style scoped>
.public-page {
  min-height: 100vh;
  display: grid;
  justify-items: center;
  align-items: start;
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

.seo-block {
  margin: 2.5rem auto 0;
  max-width: 52rem;
  padding: 1.1rem 1.25rem;
  border: 1px solid rgba(37, 99, 235, 0.12);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.8);
  text-align: left;
}

.seo-block h2 {
  margin: 0;
  font-size: 1.05rem;
  color: #111827;
}

.seo-block p {
  margin: 0.85rem 0 0;
  color: #374151;
  line-height: 1.55;
}

@media (max-width: 640px) {
  .actions {
    width: 100%;
    display: grid;
  }

  .btn {
    text-align: center;
  }

  .seo-block {
    padding: 1rem;
  }
}
</style>
