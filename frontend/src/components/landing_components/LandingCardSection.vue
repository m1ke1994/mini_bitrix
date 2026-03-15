<template>
  <section :id="id || null" class="landing-card-section">
    <div class="landing-card-section__content">
      <header v-if="title || subtitle" class="landing-card-section__header">
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="subtitle">{{ subtitle }}</p>
      </header>

      <div class="landing-card-section__body">
        <slot />
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  id: {
    type: String,
    default: "",
  },
  title: {
    type: String,
    default: "",
  },
  subtitle: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.landing-card-section {
  position: relative;
  isolation: isolate;
  margin: 1.25rem auto 0;
  width: 100%;
  max-width: 1400px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 30px;
  background:
    radial-gradient(
      120% 120% at 50% 104%,
      rgba(224, 233, 249, 0.9) 0%,
      rgba(239, 244, 255, 0.28) 56%,
      rgba(239, 244, 255, 0) 100%
    ),
    linear-gradient(
      180deg,
      rgba(246, 250, 255, 0.95) 0%,
      rgba(238, 244, 254, 0.9) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 22px 52px rgba(53, 79, 122, 0.11);
  scroll-margin-top: 112px;
}

.landing-card-section__content {
  position: relative;
  margin: 0 auto;
  width: 100%;
  max-width: 1260px;
  padding: 52px 22px 62px;
}

.landing-card-section__header {
  text-align: center;
}

.landing-card-section__header h2 {
  margin: 0;
  color: #1f2942;
  font-size: clamp(1.8rem, 2.9vw, 3rem);
  line-height: 1.12;
  letter-spacing: -0.025em;
  font-weight: 620;
}

.landing-card-section__header p {
  margin: 0.95rem auto 0;
  max-width: 900px;
  color: rgba(42, 53, 77, 0.78);
  font-size: clamp(1rem, 1.3vw, 1.24rem);
  line-height: 1.5;
}

.landing-card-section__body {
  margin-top: 1.8rem;
}

@media (max-width: 767px) {
  .landing-card-section {
    border-radius: 24px;
    scroll-margin-top: 96px;
  }

  .landing-card-section__content {
    padding: 34px 14px 42px;
  }

  .landing-card-section__header {
    text-align: left;
  }

  .landing-card-section__body {
    margin-top: 1.3rem;
  }
}
</style>
