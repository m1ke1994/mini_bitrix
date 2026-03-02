<template>
  <section id="reviews" class="reviews-section">
    <div class="reviews-glow reviews-glow--left" aria-hidden="true" />
    <div class="reviews-glow reviews-glow--right" aria-hidden="true" />
    <div class="reviews-wave reviews-wave--one" aria-hidden="true" />

    <div class="reviews-content">
      <header class="reviews-header">
        <h2 class="reviews-title">{{ reviews.title }}</h2>
        <p class="reviews-subtitle">{{ reviews.subtitle }}</p>
      </header>

      <div class="reviews-grid">
        <article
          v-for="review in reviews.items"
          :key="review.company"
          class="review-card"
        >
          <div class="review-stars" aria-label="Рейтинг 5 из 5">
            <svg v-for="star in 5" :key="star" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path
                d="M8 1.3L9.73 4.84L13.6 5.4L10.8 8.12L11.46 12L8 10.18L4.54 12L5.2 8.12L2.4 5.4L6.27 4.84L8 1.3Z"
                fill="currentColor"
              />
            </svg>
          </div>

          <h3 class="review-project-title">{{ review.projectTitle }}</h3>

          <p class="review-company">{{ review.company }}</p>
          <p class="review-role">{{ review.description }}</p>
          <p class="review-date">Дата: {{ review.date }}</p>
          <p class="review-text">{{ review.text }}</p>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { siteData } from "~/assets/data";

const reviews = siteData.reviews;
</script>

<style scoped>
.reviews-section {
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
      115% 120% at 50% 103%,
      rgba(224, 233, 249, 0.88) 0%,
      rgba(238, 244, 255, 0.26) 56%,
      rgba(238, 244, 255, 0) 100%
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

.reviews-glow {
  position: absolute;
  z-index: -2;
  pointer-events: none;
  border-radius: 999px;
}

.reviews-glow--left {
  left: -13%;
  bottom: -14%;
  width: min(42vw, 600px);
  aspect-ratio: 1;
  background:
    radial-gradient(
      circle,
      rgba(171, 202, 246, 0.48) 0%,
      rgba(171, 202, 246, 0.16) 45%,
      rgba(171, 202, 246, 0) 72%
    );
}

.reviews-glow--right {
  right: -12%;
  top: -6%;
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

.reviews-wave {
  position: absolute;
  z-index: -1;
  pointer-events: none;
  left: -12%;
  right: -12%;
  border-radius: 999px;
}

.reviews-wave--one {
  bottom: -235px;
  height: 342px;
  background:
    radial-gradient(
      100% 198% at 50% 0%,
      rgba(255, 255, 255, 0.9) 0%,
      rgba(240, 246, 255, 0.72) 47%,
      rgba(240, 246, 255, 0) 72%
    );
}

.reviews-content {
  position: relative;
  margin: 0 auto;
  width: 100%;
  max-width: 1270px;
  padding: 58px 22px 70px;
}

.reviews-header {
  margin: 0 auto;
  text-align: center;
}

.reviews-title {
  margin: 0;
  color: #1f2942;
  font-size: clamp(2rem, 3.05vw, 3.2rem);
  line-height: 1.08;
  letter-spacing: -0.025em;
  font-weight: 600;
}

.reviews-subtitle {
  margin: 16px auto 0;
  max-width: 900px;
  color: rgba(42, 53, 77, 0.76);
  font-size: clamp(1rem, 1.33vw, 1.3rem);
  line-height: 1.42;
  font-weight: 500;
}

.reviews-grid {
  margin-top: 36px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.review-card {
  min-height: 336px;
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  border: 1px solid rgba(227, 236, 250, 0.94);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.73) 0%,
      rgba(252, 255, 255, 0.58) 100%
    );
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.88),
    inset 0 -1px 0 rgba(229, 237, 251, 0.7),
    0 13px 30px rgba(81, 111, 161, 0.12);
  padding: 16px 14px 14px;
}

.review-stars {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #62a0eb;
}

.review-stars svg {
  width: 15px;
  height: 15px;
}

.review-project-title {
  margin: 12px 0 0;
  color: #24314c;
  text-align: center;
  font-size: 1.02rem;
  line-height: 1.2;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.review-company {
  margin: 12px 0 0;
  color: #2e3c59;
  font-size: 0.95rem;
  line-height: 1.3;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.review-role {
  margin: 5px 0 0;
  color: rgba(47, 62, 89, 0.72);
  font-size: 0.88rem;
  line-height: 1.3;
  font-weight: 600;
}

.review-date {
  margin: 10px 0 0;
  color: rgba(67, 92, 132, 0.8);
  font-size: 0.82rem;
  line-height: 1.2;
  font-weight: 600;
}

.review-text {
  margin: 10px 0 0;
  color: rgba(35, 47, 71, 0.82);
  font-size: 0.95rem;
  line-height: 1.46;
}

@media (max-width: 1180px) {
  .reviews-content {
    padding: 50px 20px 62px;
  }

  .reviews-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 15px;
  }

  .review-card {
    min-height: 308px;
  }
}

@media (max-width: 767px) {
  .reviews-section {
    border-radius: 24px;
    scroll-margin-top: 96px;
  }

  .reviews-content {
    padding: 36px 14px 44px;
  }

  .reviews-subtitle {
    margin-top: 12px;
    font-size: 0.97rem;
    line-height: 1.44;
  }

  .reviews-grid {
    margin-top: 28px;
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .review-card {
    border-radius: 18px;
    min-height: 0;
    padding: 14px;
  }

  .review-role {
    margin-top: 4px;
  }

  .review-text {
    font-size: 0.93rem;
  }

  .review-date {
    margin-top: 8px;
  }

}
</style>
