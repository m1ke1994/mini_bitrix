<template>
  <main class="about-page">
    <article class="about-content">
      <header>
        <p class="about-kicker">TrackNode</p>
        <h1>О проекте TrackNode</h1>
        <p>
          TrackNode создан как практичная платформа для компаний, которым важно ежедневно видеть реальные цифры по трафику,
          заявкам и эффективности маркетинга. Сервис объединяет аналитику сайта, отслеживание лидов и учет заявок, чтобы
          руководитель, маркетолог и отдел продаж работали с единым источником данных.
        </p>
      </header>

      <section>
        <h2>Миссия сервиса</h2>
        <p>
          Наша задача — сделать анализ сайтов прикладным и понятным для бизнеса. Вместо сложной BI-инфраструктуры TrackNode
          показывает ключевые показатели, которые действительно влияют на выручку: источники трафика, конверсию страниц,
          динамику заявок и поведение пользователя на сайте. Мы помогаем компаниям принимать решения не по ощущениям, а по
          подтвержденным данным.
        </p>
      </section>

      <section>
        <h2>Как работает TrackNode</h2>
        <p>
          После подключения скрипта система фиксирует важные действия пользователей: визиты, переходы, отправки форм и другие
          события воронки. Эти данные связываются с заявками, поэтому команда видит полный путь клиента — от первого касания до
          обращения. Дополнительно уведомления в Telegram помогают быстро реагировать на лиды и не терять горячие заявки в
          моменты высокой нагрузки.
        </p>
      </section>

      <section>
        <h2>Кому подходит платформа</h2>
        <p>
          TrackNode подходит малому и среднему бизнесу, агентствам и продуктовым командам, которым нужен прозрачный контроль
          маркетинга и продаж. Сервис полезен там, где важно быстро оценить эффективность рекламного канала, понять причины
          просадки конверсии и выстроить стабильный процесс обработки обращений.
        </p>
      </section>

      <section>
        <h2>Безопасность и практичность</h2>
        <p>
          Мы делаем акцент на рабочем процессе: данные должны быть доступны, структурированы и понятны без лишней технической
          сложности. В интерфейсе остается только то, что помогает управлять результатом: отчеты, динамика, источники трафика,
          точки потерь и скорость реакции на обращения. Это позволяет запускать аналитику быстро и использовать ее ежедневно.
        </p>
      </section>

      <section>
        <h2>Что получает бизнес на практике</h2>
        <p>
          В результате компания получает единый контур для SEO-оптимизации, отслеживания лидов и учета заявок. Маркетинг видит,
          где растет эффективность, продажи быстрее реагируют на новые обращения, а руководитель принимает решения на основании
          прозрачной статистики. Такой формат снижает потери воронки и помогает системно увеличивать конверсию.
        </p>
      </section>

      <SeoContentBlock
        :section-title="seoContent.sectionTitle"
        :paragraphs="seoContent.paragraphs"
        :highlights-title="seoContent.highlightsTitle"
        :highlights="seoContent.highlights"
        :faq-title="seoContent.faqTitle"
        :faq-items="seoContent.faqItems"
        aria-label="FAQ и подробное описание TrackNode"
      />
    </article>
  </main>
</template>

<script setup>
import SeoContentBlock from "~/components/SeoContentBlock.vue";
import { getPublicSeoContent } from "~/content/publicSeoContent";

const seoContent = getPublicSeoContent("/about") || {
  sectionTitle: "",
  paragraphs: [],
  highlightsTitle: "",
  highlights: [],
  faqTitle: "",
  faqItems: [],
};
</script>

<style scoped>
.about-page {
  padding: 0;
}

.about-content {
  max-width: none;
  margin: 0;
  background: transparent;
  border-radius: 0;
  padding: 0;
}

.about-kicker {
  margin: 0;
  color: #1d4ed8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  font-size: 0.78rem;
}

h1 {
  margin: 0.35rem 0 1rem;
  color: #0f172a;
  line-height: 1.2;
}

h2 {
  margin: 2rem 0 0.8rem;
  color: #0f172a;
  line-height: 1.3;
}

p {
  margin: 0 0 0.95rem;
  color: #1f2937;
  line-height: 1.75;
}

@media (max-width: 768px) {
  .about-content {
    padding: 0;
  }
}
</style>
