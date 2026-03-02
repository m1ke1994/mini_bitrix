<template>
  <section id="how" class="how-section">
    <div class="how-bg how-bg--left" aria-hidden="true" />
    <div class="how-bg how-bg--right" aria-hidden="true" />
    <div class="how-bg how-bg--top" aria-hidden="true" />
    <div class="how-wave how-wave--one" aria-hidden="true" />
    <div class="how-wave how-wave--two" aria-hidden="true" />

    <div class="how-content">
      <header class="how-header">
        <h2 class="how-title">Как это работает</h2>
        <p class="how-subtitle">
          Внесите сайт в два простых шага и получите аналитику и уведомления.
        </p>
      </header>

      <div class="how-grid">
        <article
          v-for="step in steps"
          :key="step.id"
          class="how-card how-card--interactive"
          role="button"
          tabindex="0"
          :aria-label="`Открыть инструкцию: ${step.title}`"
          @click="openModal(step.id)"
          @keydown.enter.prevent="openModal(step.id)"
          @keydown.space.prevent="openModal(step.id)"
        >
          <span class="how-badge">{{ step.number }}</span>
          <div class="how-media">
            <img :src="step.image" :alt="step.alt" loading="lazy" decoding="async" />
          </div>
          <h3 class="how-card-title">{{ step.title }}</h3>
          <p class="how-card-description">{{ step.description }}</p>
        </article>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="activeModal && currentModal"
        class="how-modal-overlay"
        @click.self="closeModal"
      >
        <article class="how-modal" role="dialog" aria-modal="true" :aria-labelledby="`how-modal-title-${activeModal}`">
          <button type="button" class="how-modal-close" aria-label="Закрыть" @click="closeModal">
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
          </button>

          <h3 :id="`how-modal-title-${activeModal}`" class="how-modal-title">
            {{ currentModal.title }}
          </h3>

          <template v-if="currentModal.type === 'example'">
            <img
              src="/Hero/hero.gif"
              alt="Пример аналитики TrackNode"
              class="how-modal-gif"
            />
            <p class="how-modal-text">
              TrackNode показывает ключевые метрики в одном интерфейсе: посещения, источники, события и заявки.
              Команда сразу видит, где растёт конверсия, а где нужны доработки, и быстрее принимает решения.
            </p>
          </template>

          <template v-else>
            <ol class="how-modal-steps">
              <li v-for="item in currentModal.steps" :key="item">{{ item }}</li>
            </ol>
          </template>
        </article>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

const steps = [
  {
    id: "step-1",
    number: "1",
    title: "Добавляете сайт",
    description: "Введите адрес сайта и создайте проект в TrackNode.",
    image: "/how/step-1.png",
    alt: "Добавление сайта",
  },
  {
    id: "step-2",
    number: "2",
    title: "Устанавливаете код",
    description: "Установите линейный код отслеживания или интеграцию.",
    image: "/how/step-2.png",
    alt: "Установка кода отслеживания",
  },
  {
    id: "step-3",
    number: "3",
    title: "Смотрите аналитику",
    description: "Отслеживайте посещения и уведомления о заявках.",
    image: "/how/step-3.png",
    alt: "Просмотр аналитики",
  },
];

const modalData = {
  "step-1": {
    type: "steps",
    title: "Добавляете сайт",
    steps: [
      "Откройте TrackNode и нажмите «Создать проект».",
      "Укажите домен сайта и рабочий часовой пояс.",
      "Выберите Telegram-канал для уведомлений о заявках.",
      "Проверьте параметры проекта и сохраните настройки.",
    ],
  },
  "step-2": {
    type: "steps",
    title: "Устанавливаете код",
    steps: [
      "Скопируйте трекинг-код из карточки проекта.",
      "Добавьте код перед закрывающим тегом </head> на сайте.",
      "Если используете CMS, подключите код через шаблон или модуль.",
      "Опубликуйте изменения и выполните тестовый визит.",
      "Убедитесь, что данные начали поступать в дашборд.",
    ],
  },
  "step-3": {
    type: "example",
    title: "Пример",
  },
};

const activeModal = ref("");
const currentModal = computed(() => (activeModal.value ? modalData[activeModal.value] : null));

function openModal(id) {
  activeModal.value = id;
  document.body.style.overflow = "hidden";
}

function closeModal() {
  activeModal.value = "";
  document.body.style.overflow = "";
}

function handleEscape(event) {
  if (event.key === "Escape" && activeModal.value) {
    closeModal();
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleEscape);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleEscape);
  document.body.style.overflow = "";
});
</script>

<style scoped>
.how-section {
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
      80% 120% at 50% 105%,
      rgba(224, 233, 250, 0.92) 0%,
      rgba(239, 244, 254, 0.28) 56%,
      rgba(244, 248, 255, 0) 100%
    ),
    linear-gradient(
      180deg,
      rgba(246, 249, 255, 0.95) 0%,
      rgba(237, 243, 253, 0.86) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 24px 56px rgba(53, 79, 122, 0.12);
  scroll-margin-top: 112px;
}

.how-bg {
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
  filter: blur(0.5px);
  z-index: -2;
}

.how-bg--left {
  left: -17%;
  bottom: -16%;
  width: min(58vw, 700px);
  aspect-ratio: 1;
  background:
    radial-gradient(
      circle,
      rgba(195, 212, 242, 0.62) 0%,
      rgba(195, 212, 242, 0.24) 42%,
      rgba(195, 212, 242, 0) 72%
    );
}

.how-bg--right {
  right: -19%;
  top: -3%;
  width: min(56vw, 700px);
  aspect-ratio: 1;
  background:
    radial-gradient(
      circle,
      rgba(145, 182, 238, 0.5) 0%,
      rgba(158, 196, 248, 0.2) 40%,
      rgba(158, 196, 248, 0) 72%
    );
}

.how-bg--top {
  left: 24%;
  top: -30%;
  width: min(53vw, 720px);
  aspect-ratio: 1.25;
  background:
    radial-gradient(
      ellipse,
      rgba(255, 255, 255, 0.5) 0%,
      rgba(227, 238, 255, 0.2) 44%,
      rgba(227, 238, 255, 0) 70%
    );
}

.how-wave {
  position: absolute;
  pointer-events: none;
  left: -16%;
  right: -16%;
  border-radius: 999px;
  z-index: -1;
}

.how-wave--one {
  bottom: -182px;
  height: 332px;
  background:
    radial-gradient(
      100% 188% at 50% 0%,
      rgba(255, 255, 255, 0.95) 0%,
      rgba(240, 246, 255, 0.86) 48%,
      rgba(240, 246, 255, 0) 74%
    );
}

.how-wave--two {
  bottom: -220px;
  height: 350px;
  background:
    radial-gradient(
      100% 205% at 50% 0%,
      rgba(235, 242, 253, 0.8) 0%,
      rgba(235, 242, 253, 0.36) 46%,
      rgba(235, 242, 253, 0) 76%
    );
}

.how-content {
  position: relative;
  width: 100%;
  max-width: 1270px;
  margin: 0 auto;
  padding: 62px 30px 72px;
}

.how-header {
  margin: 0 auto;
  text-align: center;
}

.how-title {
  margin: 0;
  color: #1d2740;
  font-size: clamp(2rem, 3.2vw, 3.5rem);
  line-height: 1.08;
  letter-spacing: -0.03em;
  font-weight: 600;
}

.how-subtitle {
  margin: 18px auto 0;
  max-width: 940px;
  color: rgba(44, 55, 82, 0.82);
  font-size: clamp(1.06rem, 1.75vw, 2.02rem);
  line-height: 1.36;
  letter-spacing: -0.01em;
  font-weight: 500;
}

.how-grid {
  margin-top: 46px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.how-card {
  position: relative;
  min-height: 420px;
  border-radius: 20px;
  border: 1px solid rgba(232, 239, 252, 0.92);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.66) 0%,
      rgba(252, 255, 255, 0.56) 100%
    );
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    inset 0 -1px 0 rgba(229, 237, 251, 0.72),
    0 14px 30px rgba(92, 121, 170, 0.12);
  padding: 18px 28px 24px;
  display: flex;
  flex-direction: column;
}

.how-card--interactive {
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.how-card--interactive:hover,
.how-card--interactive:focus-visible {
  transform: translateY(-2px);
  border-color: rgba(198, 218, 246, 0.96);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.92),
    inset 0 -1px 0 rgba(229, 237, 251, 0.74),
    0 18px 34px rgba(86, 121, 177, 0.16);
  outline: none;
}

.how-badge {
  width: 60px;
  height: 60px;
  border-radius: 999px;
  border: 1px solid rgba(191, 212, 240, 0.84);
  background:
    radial-gradient(
      circle at 34% 28%,
      rgba(246, 252, 255, 0.96) 0%,
      rgba(224, 238, 252, 0.94) 62%,
      rgba(213, 228, 245, 0.95) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.85),
    0 6px 14px rgba(113, 144, 194, 0.2);
  color: #5f96d1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 50px;
  line-height: 1;
  letter-spacing: -0.02em;
  font-weight: 500;
}

.how-media {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 206px;
}

.how-media img {
  display: block;
  width: 100%;
  max-width: 338px;
  max-height: 196px;
  object-fit: contain;
  filter: drop-shadow(0 10px 16px rgba(130, 162, 210, 0.18));
}

.how-card-title {
  margin: 4px 0 0;
  color: #1e273f;
  font-size: clamp(1.9rem, 2.2vw, 2.8rem);
  line-height: 1.18;
  letter-spacing: -0.02em;
  font-weight: 600;
}

.how-card-description {
  margin: 16px 0 0;
  color: rgba(39, 49, 73, 0.74);
  font-size: clamp(1.2rem, 1.28vw, 1.84rem);
  line-height: 1.42;
  letter-spacing: -0.005em;
  font-weight: 500;
  max-width: 28ch;
}

.how-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 160;
  background: rgba(19, 30, 52, 0.34);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.how-modal {
  width: min(100%, 760px);
  max-height: min(88vh, 840px);
  overflow: auto;
  position: relative;
  border-radius: 22px;
  border: 1px solid rgba(212, 227, 248, 0.96);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.88) 0%,
      rgba(247, 252, 255, 0.82) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.94),
    0 26px 48px rgba(35, 58, 99, 0.2);
  padding: 24px 24px 22px;
}

.how-modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(189, 209, 240, 0.9);
  background: rgba(248, 252, 255, 0.95);
  color: #537dbd;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.how-modal-close:hover {
  border-color: rgba(150, 186, 236, 0.95);
  transform: translateY(-1px);
}

.how-modal-close svg {
  width: 16px;
  height: 16px;
}

.how-modal-title {
  margin: 0;
  padding-right: 38px;
  color: #23304b;
  font-size: clamp(1.3rem, 2.2vw, 1.8rem);
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: -0.015em;
}

.how-modal-steps {
  margin: 16px 0 0;
  padding: 0 0 0 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.how-modal-steps li {
  color: rgba(34, 45, 68, 0.86);
  font-size: 1rem;
  line-height: 1.45;
}

.how-modal-gif {
  margin-top: 16px;
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(188, 211, 245, 0.92);
  display: block;
  object-fit: cover;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.86),
    0 12px 22px rgba(79, 120, 182, 0.16);
}

.how-modal-text {
  margin: 14px 0 0;
  color: rgba(37, 48, 72, 0.82);
  font-size: 0.98rem;
  line-height: 1.48;
}

@media (max-width: 1279px) {
  .how-content {
    padding: 54px 26px 66px;
  }

  .how-grid {
    gap: 14px;
  }

  .how-card {
    min-height: 390px;
    padding: 16px 22px 22px;
  }

  .how-badge {
    width: 52px;
    height: 52px;
    font-size: 42px;
  }

  .how-media {
    min-height: 172px;
  }

  .how-media img {
    max-width: 288px;
    max-height: 168px;
  }

  .how-card-title {
    font-size: clamp(1.55rem, 2.35vw, 2.2rem);
  }

  .how-card-description {
    margin-top: 12px;
    font-size: clamp(1rem, 1.38vw, 1.28rem);
  }
}

@media (max-width: 1023px) {
  .how-content {
    padding: 48px 22px 60px;
  }

  .how-title {
    font-size: clamp(2rem, 5.2vw, 3rem);
  }

  .how-subtitle {
    margin-top: 14px;
    max-width: 740px;
    font-size: clamp(1rem, 2.5vw, 1.55rem);
  }

  .how-grid {
    margin-top: 38px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }

  .how-card {
    min-height: 360px;
  }
}

@media (max-width: 767px) {
  .how-section {
    border-radius: 24px;
    scroll-margin-top: 96px;
  }

  .how-content {
    padding: 38px 16px 44px;
  }

  .how-title {
    font-size: clamp(1.7rem, 8vw, 2.2rem);
  }

  .how-subtitle {
    margin-top: 12px;
    font-size: clamp(1rem, 4.5vw, 1.16rem);
    line-height: 1.45;
  }

  .how-grid {
    margin-top: 28px;
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .how-card {
    min-height: 336px;
    border-radius: 18px;
    padding: 14px 16px 18px;
  }

  .how-badge {
    width: 46px;
    height: 46px;
    font-size: 34px;
  }

  .how-media {
    margin-top: 12px;
    min-height: 146px;
  }

  .how-media img {
    max-width: 264px;
    max-height: 152px;
  }

  .how-card-title {
    margin-top: 2px;
    font-size: 1.6rem;
  }

  .how-card-description {
    margin-top: 9px;
    font-size: 1rem;
    line-height: 1.4;
    max-width: 32ch;
  }

  .how-modal-overlay {
    padding: 10px;
  }

  .how-modal {
    border-radius: 18px;
    padding: 16px 14px 14px;
  }

  .how-modal-title {
    font-size: 1.24rem;
  }

  .how-modal-steps li {
    font-size: 0.93rem;
    line-height: 1.4;
  }

  .how-modal-text {
    font-size: 0.92rem;
    line-height: 1.42;
  }
}
</style>
