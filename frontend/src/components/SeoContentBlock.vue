<template>
  <section class="seo-content" :aria-label="ariaLabel">
    <h2 class="seo-title">{{ sectionTitle }}</h2>

    <p v-for="paragraph in paragraphs" :key="paragraph" class="seo-paragraph">
      {{ paragraph }}
    </p>

    <h3 v-if="highlights.length" class="seo-subtitle">{{ highlightsTitle }}</h3>
    <ul v-if="highlights.length" class="seo-list">
      <li v-for="item in highlights" :key="item">{{ item }}</li>
    </ul>

    <section v-if="faqItems.length" class="seo-faq" aria-label="Часто задаваемые вопросы">
      <h2 class="seo-title faq-title">{{ faqTitle }}</h2>
      <article v-for="item in faqItems" :key="item.question" class="faq-item">
        <h3 class="faq-question">{{ item.question }}</h3>
        <p class="faq-answer">{{ item.answer }}</p>
      </article>
    </section>
  </section>
</template>

<script setup>
defineProps({
  sectionTitle: {
    type: String,
    required: true,
  },
  ariaLabel: {
    type: String,
    default: "SEO-контент",
  },
  paragraphs: {
    type: Array,
    default: () => [],
  },
  highlightsTitle: {
    type: String,
    default: "Ключевые преимущества",
  },
  highlights: {
    type: Array,
    default: () => [],
  },
  faqTitle: {
    type: String,
    default: "Частые вопросы",
  },
  faqItems: {
    type: Array,
    default: () => [],
  },
});
</script>

<style scoped>
.seo-content {
  margin: 2.5rem auto 0;
  max-width: 52rem;
  padding: 1.1rem 1.25rem;
  border: 1px solid rgba(37, 99, 235, 0.12);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.86);
  text-align: left;
}

.seo-title {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.35;
  color: #111827;
}

.seo-subtitle {
  margin: 1.1rem 0 0;
  font-size: 1rem;
  color: #111827;
}

.seo-paragraph {
  margin: 0.9rem 0 0;
  line-height: 1.62;
  color: #374151;
}

.seo-list {
  margin: 0.75rem 0 0;
  padding-left: 1.1rem;
  color: #1f2937;
}

.seo-list li {
  margin-top: 0.4rem;
  line-height: 1.5;
}

.seo-faq {
  margin-top: 1.5rem;
}

.faq-title {
  margin-top: 0;
}

.faq-item + .faq-item {
  margin-top: 0.9rem;
}

.faq-question {
  margin: 0;
  font-size: 1rem;
  color: #111827;
}

.faq-answer {
  margin: 0.45rem 0 0;
  line-height: 1.58;
  color: #374151;
}

@media (max-width: 640px) {
  .seo-content {
    padding: 1rem;
  }
}
</style>
