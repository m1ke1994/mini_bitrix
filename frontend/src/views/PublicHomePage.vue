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

      <SeoContentBlock
        :section-title="seoContent.sectionTitle"
        :paragraphs="seoContent.paragraphs"
        :highlights-title="seoContent.highlightsTitle"
        :highlights="seoContent.highlights"
        :faq-title="seoContent.faqTitle"
        :faq-items="seoContent.faqItems"
        aria-label="Расширенное описание сервиса аналитики TrackNode"
      />
    </section>
  </main>
</template>

<script setup>
import SeoContentBlock from "~/components/SeoContentBlock.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";

const seoContent = getPublicSeoContent("/") || {
  sectionTitle: "",
  paragraphs: [],
  highlightsTitle: "",
  highlights: [],
  faqTitle: "",
  faqItems: [],
};
</script>

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

@media (max-width: 640px) {
  .actions {
    width: 100%;
    display: grid;
  }

  .btn {
    text-align: center;
  }
}
</style>
