<template>
  <main class="feature-page">
    <section class="wrap">
      <h1>{{ heading }}</h1>
      <p>{{ text }}</p>
      <router-link to="/register" class="cta">Попробовать TrackNode</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const heading = computed(() => route.meta.pageHeading || "TrackNode");
const text = computed(
  () =>
    route.meta.pageText ||
    "TrackNode помогает бизнесу анализировать трафик, заявки и конверсию в единой SaaS-платформе.",
);
</script>

<style scoped>
.feature-page {
  min-height: 100vh;
  padding: 2.5rem 1rem;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.wrap {
  max-width: 56rem;
  margin: 0 auto;
}

h1 {
  margin: 0;
  color: #0f172a;
  font-size: clamp(2rem, 5vw, 3rem);
}

p {
  margin-top: 1rem;
  max-width: 42rem;
  color: #334155;
  line-height: 1.7;
}

.cta {
  display: inline-block;
  margin-top: 1.4rem;
  text-decoration: none;
  color: #ffffff;
  background: #2563eb;
  padding: 0.72rem 1.1rem;
  border-radius: 999px;
  font-weight: 700;
}
</style>
