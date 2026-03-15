<template>
  <LandingPageShell :landing="landing" :hero="page.hero">
    <LandingCardSection title="Последние статьи" subtitle="Материалы по SEO-аудиту, аналитике и росту конверсии сайта.">
      <div class="blog-grid">
        <article
          v-for="post in posts"
          :key="post.slug"
          class="blog-card"
        >
          <p class="blog-card__meta">{{ formatDate(post.date) }} · {{ post.category }}</p>
          <h2>{{ post.title }}</h2>
          <p>{{ post.excerpt }}</p>

          <NuxtLink :to="`/blog/${post.slug}`" class="blog-card__link">
            Читать статью
          </NuxtLink>
        </article>
      </div>
    </LandingCardSection>
  </LandingPageShell>
</template>

<script setup>
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingBlogPosts, getLandingData } from "~/data/landing";

const landing = getLandingData();
const page = landing.seoPages?.blog;
const posts = getLandingBlogPosts();

definePageMeta({
  layout: "landing",
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  ...page.seo,
  path: "/blog",
});

function formatDate(date) {
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString("ru-RU");
}
</script>

<style scoped>
.blog-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.blog-card {
  border-radius: 20px;
  border: 1px solid rgba(227, 236, 250, 0.94);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.73) 0%,
      rgba(252, 255, 255, 0.58) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.88),
    0 13px 30px rgba(81, 111, 161, 0.11);
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
}

.blog-card__meta {
  margin: 0;
  color: rgba(57, 86, 130, 0.82);
  font-size: 0.82rem;
  line-height: 1.2;
  font-weight: 700;
}

.blog-card h2 {
  margin: 0.75rem 0 0;
  color: #24314c;
  font-size: 1.08rem;
  line-height: 1.35;
  font-weight: 700;
}

.blog-card p {
  margin: 0.72rem 0 0;
  color: rgba(39, 50, 73, 0.78);
  font-size: 0.94rem;
  line-height: 1.5;
}

.blog-card__link {
  margin-top: auto;
  min-height: 42px;
  border-radius: 11px;
  border: 1px solid rgba(164, 197, 243, 0.92);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.93) 0%,
      rgba(232, 243, 255, 0.96) 100%
    );
  color: #3d74c4;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.93rem;
  font-weight: 700;
  margin-top: 1rem;
}

@media (max-width: 1023px) {
  .blog-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .blog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
