<template>
  <section id="faq" class="faq-section">
    <div class="faq-glow faq-glow--left" aria-hidden="true" />
    <div class="faq-glow faq-glow--right" aria-hidden="true" />
    <div class="faq-wave" aria-hidden="true" />

    <div class="faq-content">
      <header class="faq-header">
        <h2 class="faq-title">{{ faq.title }}</h2>
      </header>

      <article class="faq-intro">
        <h3>{{ faq.introTitle }}</h3>
        <p v-for="(paragraph, idx) in faq.introParagraphs" :key="idx">
          {{ paragraph }}
        </p>
      </article>

      <h3 class="faq-list-title">Частые вопросы о сервисе</h3>

      <div class="faq-list" role="list">
        <article
          v-for="(item, index) in faq.items"
          :key="item.question"
          class="faq-item"
          :class="{ 'faq-item--open': openIndex === index }"
          role="listitem"
        >
          <button
            type="button"
            class="faq-trigger"
            :aria-expanded="openIndex === index"
            :aria-controls="`faq-panel-${index}`"
            @click="toggle(index)"
          >
            <span>{{ item.question }}</span>
            <span class="faq-plus" :class="{ 'faq-plus--open': openIndex === index }" aria-hidden="true" />
          </button>

          <div
            :id="`faq-panel-${index}`"
            class="faq-panel"
            :class="{ 'faq-panel--open': openIndex === index }"
          >
            <p>{{ item.answer }}</p>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { siteData } from "~/assets/data";

const faq = siteData.faq;
const openIndex = ref(0);

function toggle(index) {
  openIndex.value = openIndex.value === index ? -1 : index;
}
</script>

<style scoped>
.faq-section {
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

.faq-glow {
  position: absolute;
  z-index: -2;
  pointer-events: none;
  border-radius: 999px;
}

.faq-glow--left {
  left: -15%;
  bottom: -18%;
  width: min(42vw, 600px);
  aspect-ratio: 1;
  background:
    radial-gradient(
      circle,
      rgba(169, 200, 246, 0.5) 0%,
      rgba(169, 200, 246, 0.16) 45%,
      rgba(169, 200, 246, 0) 72%
    );
}

.faq-glow--right {
  right: -12%;
  top: -10%;
  width: min(40vw, 560px);
  aspect-ratio: 1;
  background:
    radial-gradient(
      circle,
      rgba(150, 191, 244, 0.43) 0%,
      rgba(150, 191, 244, 0.15) 44%,
      rgba(150, 191, 244, 0) 72%
    );
}

.faq-wave {
  position: absolute;
  z-index: -1;
  pointer-events: none;
  left: -12%;
  right: -12%;
  bottom: -238px;
  height: 344px;
  border-radius: 999px;
  background:
    radial-gradient(
      100% 198% at 50% 0%,
      rgba(255, 255, 255, 0.9) 0%,
      rgba(240, 246, 255, 0.72) 47%,
      rgba(240, 246, 255, 0) 72%
    );
}

.faq-content {
  position: relative;
  margin: 0 auto;
  width: 100%;
  max-width: 1120px;
  padding: 58px 22px 70px;
}

.faq-header {
  text-align: center;
}

.faq-title {
  margin: 0;
  color: #1f2942;
  font-size: clamp(2rem, 3.05vw, 3.2rem);
  line-height: 1.08;
  letter-spacing: -0.025em;
  font-weight: 600;
}

.faq-intro {
  margin: 28px auto 0;
  border-radius: 20px;
  border: 1px solid rgba(227, 236, 250, 0.94);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.72) 0%,
      rgba(252, 255, 255, 0.58) 100%
    );
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.88),
    inset 0 -1px 0 rgba(229, 237, 251, 0.68),
    0 13px 30px rgba(81, 111, 161, 0.12);
  padding: 24px 24px 20px;
}

.faq-intro h3 {
  margin: 0;
  color: #24314d;
  font-size: clamp(1.25rem, 2vw, 1.58rem);
  line-height: 1.22;
  font-weight: 700;
  letter-spacing: -0.015em;
}

.faq-intro p {
  margin: 12px 0 0;
  color: rgba(39, 50, 73, 0.8);
  font-size: 1rem;
  line-height: 1.52;
}

.faq-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.faq-list-title {
  margin: 22px 0 0;
  color: #24314d;
  font-size: clamp(1.16rem, 1.8vw, 1.4rem);
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: -0.012em;
}

.faq-item {
  border-radius: 16px;
  border: 1px solid rgba(226, 235, 249, 0.94);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.7) 0%,
      rgba(252, 255, 255, 0.54) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.84),
    0 10px 24px rgba(81, 111, 161, 0.1);
  overflow: hidden;
}

.faq-item--open {
  border-color: rgba(179, 208, 246, 0.95);
}

.faq-trigger {
  width: 100%;
  border: 0;
  background: transparent;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  cursor: pointer;
  color: #22304a;
  font-size: 1rem;
  line-height: 1.36;
  font-weight: 650;
  text-align: left;
}

.faq-plus {
  width: 20px;
  height: 20px;
  border-radius: 999px;
  border: 1px solid rgba(163, 198, 243, 0.92);
  background: rgba(235, 245, 255, 0.96);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.84);
  position: relative;
  flex-shrink: 0;
}

.faq-plus::before,
.faq-plus::after {
  content: "";
  position: absolute;
  background: #4f82c7;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.faq-plus::before {
  width: 10px;
  height: 2px;
  border-radius: 2px;
}

.faq-plus::after {
  width: 2px;
  height: 10px;
  border-radius: 2px;
}

.faq-plus--open::after {
  opacity: 0;
  transform: translate(-50%, -50%) scaleY(0.4);
}

.faq-panel {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 0.28s ease, opacity 0.24s ease, padding 0.24s ease;
  padding: 0 18px;
}

.faq-panel--open {
  max-height: 220px;
  opacity: 1;
  padding: 0 18px 16px;
}

.faq-panel p {
  margin: 0;
  color: rgba(39, 50, 73, 0.8);
  font-size: 0.96rem;
  line-height: 1.5;
}

@media (max-width: 767px) {
  .faq-section {
    border-radius: 24px;
    scroll-margin-top: 96px;
  }

  .faq-content {
    padding: 36px 14px 44px;
  }

  .faq-intro {
    margin-top: 20px;
    border-radius: 16px;
    padding: 16px 14px 14px;
  }

  .faq-intro p {
    font-size: 0.93rem;
    line-height: 1.48;
  }

  .faq-list {
    margin-top: 10px;
    gap: 8px;
  }

  .faq-list-title {
    margin-top: 16px;
    font-size: 1.05rem;
  }

  .faq-trigger {
    padding: 14px 12px;
    font-size: 0.93rem;
    line-height: 1.35;
  }

  .faq-panel {
    padding: 0 12px;
  }

  .faq-panel--open {
    padding: 0 12px 14px;
  }

  .faq-panel p {
    font-size: 0.9rem;
    line-height: 1.44;
  }
}
</style>
