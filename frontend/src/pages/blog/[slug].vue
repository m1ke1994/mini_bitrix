<template>
  <LandingPageShell :landing="landing" :hero="hero">
    <LandingCardSection :title="post.title" :subtitle="`${formatDate(post.date)} · ${post.category}`">
      <article class="article-content">
        <p class="article-lead">{{ post.description }}</p>

        <section v-for="section in post.body" :key="section.heading">
          <h2>{{ section.heading }}</h2>
          <p v-for="paragraph in section.paragraphs" :key="paragraph">{{ paragraph }}</p>

          <ul v-if="section.list?.length">
            <li v-for="item in section.list" :key="item">{{ item }}</li>
          </ul>
        </section>
      </article>
    </LandingCardSection>
  </LandingPageShell>
</template>

<script setup>
import LandingCardSection from "~/components/landing_components/LandingCardSection.vue";
import LandingPageShell from "~/components/landing_components/LandingPageShell.vue";
import { useLandingSeoPage } from "~/composables/useLandingSeoPage";
import { getLandingBlogPostBySlug, getLandingData } from "~/data/landing";

const landing = getLandingData();
const route = useRoute();
const slug = String(route.params.slug || "");
const post = getLandingBlogPostBySlug(slug);

if (!post) {
  throw createError({
    statusCode: 404,
    statusMessage: "Статья не найдена",
  });
}

const hero = {
  kicker: "Статья",
  title: post.title,
  description: post.excerpt,
  actions: [
    { label: "Все статьи", href: "/blog", variant: "secondary" },
    { label: "Связаться", href: "/contacts" },
  ],
};

const articleSchema = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: post.title,
  description: post.description,
  datePublished: post.date,
  author: {
    "@type": "Organization",
    name: "TrackNode",
  },
  mainEntityOfPage: `https://tracknode.ru/blog/${post.slug}`,
};

definePageMeta({
  layout: "landing",
  publicPage: true,
  disableGlobalSeo: true,
});

useLandingSeoPage({
  title: `${post.title} | Блог TrackNode`,
  description: post.description,
  keywords: `${post.category}, блог tracknode, seo, аналитика сайта, конверсия`,
  path: `/blog/${post.slug}`,
  ogType: "article",
  schema: [articleSchema],
});

function formatDate(date) {
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString("ru-RU");
}
</script>

<style scoped>
.article-content {
  color: rgba(35, 47, 71, 0.86);
  max-width: 860px;
}

.article-lead {
  margin: 0;
  font-size: 1.04rem;
  line-height: 1.62;
}

.article-content section + section {
  margin-top: 1.5rem;
}

.article-content h2 {
  margin: 0;
  color: #24314c;
  font-size: 1.28rem;
  line-height: 1.32;
  letter-spacing: -0.01em;
  font-weight: 700;
}

.article-content p {
  margin: 0.75rem 0 0;
  font-size: 1rem;
  line-height: 1.62;
}

.article-content ul {
  margin: 0.85rem 0 0;
  padding-left: 1rem;
  font-size: 0.98rem;
  line-height: 1.58;
}

.article-content li + li {
  margin-top: 0.4rem;
}

@media (max-width: 767px) {
  .article-content h2 {
    font-size: 1.16rem;
  }

  .article-content p,
  .article-lead {
    font-size: 0.95rem;
    line-height: 1.56;
  }

  .article-content ul {
    font-size: 0.93rem;
  }
}
</style>
