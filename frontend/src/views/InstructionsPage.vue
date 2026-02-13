<template>
  <section class="page guide-page">
    <h1>Инструкция по подключению</h1>
    <p class="guide-intro">
      Здесь собраны простые шаги, которые помогут подключить аналитику и уведомления.
      Выполняйте шаги по порядку.
    </p>
    <div class="guide-actions">
      <router-link class="guide-action-btn" to="/integration">Открыть Интеграции</router-link>
      <router-link class="guide-action-btn secondary" to="/settings">Открыть Настройки</router-link>
    </div>

    <article class="guide-section">
      <h2>Как подключить аналитику к сайту</h2>
      <div class="guide-steps">
        <div class="guide-step" v-for="step in analyticsSteps" :key="step.number">
          <span class="guide-step-number">{{ step.number }}</span>
          <p>{{ step.text }}</p>
        </div>
      </div>
      <div class="guide-code">
        <p class="guide-code-title">Пример строки подключения:</p>
        <pre><code>&lt;script src="https://ваш-домен/tracker.js" data-api-key="ваш_публичный_ключ"&gt;&lt;/script&gt;</code></pre>
      </div>
    </article>

    <article class="guide-section">
      <h2>Как подключить Telegram-уведомления</h2>
      <div class="guide-steps">
        <div class="guide-step" v-for="step in telegramSteps" :key="step.number">
          <span class="guide-step-number">{{ step.number }}</span>
          <p>{{ step.text }}</p>
        </div>
      </div>
    </article>

    <article class="guide-section">
      <h2>Проверка работы</h2>
      <div class="guide-checks">
        <div class="guide-check" v-for="(item, index) in checks" :key="index">
          <span class="guide-check-mark">✓</span>
          <p>{{ item }}</p>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup>
const analyticsSteps = [
  { number: 1, text: "Откройте раздел «Интеграции» в левом меню." },
  { number: 2, text: "Скопируйте готовую строку подключения." },
  { number: 3, text: "Вставьте её на свой сайт перед закрывающим тегом </body>." },
  { number: 4, text: "Сохраните изменения на сайте." },
  { number: 5, text: "Откройте страницу сайта и отправьте тестовую заявку." },
  { number: 6, text: "Проверьте, что заявка появилась в разделе «Заявки»." },
];

const telegramSteps = [
  { number: 1, text: "Перейдите в раздел «Настройки»." },
  { number: 2, text: "Нажмите кнопку «Подключить Telegram»." },
  { number: 3, text: "Откроется бот. Нажмите кнопку «Старт»." },
  { number: 4, text: "Вернитесь в «Настройки» и проверьте статус. Он должен стать «Подключен»." },
  { number: 5, text: "Включите галочку «Отправлять уведомления»." },
  { number: 6, text: "Нажмите кнопку «Сохранить»." },
  { number: 7, text: "Отправьте тестовую заявку с сайта и проверьте получение сообщения." },
];

const checks = [
  "Показатели в панели управления постепенно увеличиваются.",
  "Заявки появляются в разделе «Заявки».",
  "Уведомления приходят в Telegram после отправки формы.",
];
</script>
