<template>
  <section id="pricing" class="pricing-section">
    <div class="pricing-glow pricing-glow--left" aria-hidden="true" />
    <div class="pricing-glow pricing-glow--right" aria-hidden="true" />
    <div class="pricing-wave pricing-wave--one" aria-hidden="true" />

    <div class="pricing-content">
      <header class="pricing-header">
        <h2 class="pricing-title">{{ pricing.title }}</h2>
        <p class="pricing-subtitle">{{ pricing.subtitle }}</p>
      </header>

      <div class="pricing-grid">
        <article
          v-for="plan in pricing.plans"
          :key="plan.name"
          class="pricing-card"
          :class="{ 'pricing-card--featured': plan.featured }"
        >
          <span v-if="plan.featured" class="pricing-badge">Рекомендуем</span>

          <h3 class="pricing-card-title">{{ plan.name }}</h3>
          <p class="pricing-card-price">{{ plan.price }}</p>
          <p class="pricing-card-description">{{ plan.description }}</p>

          <ul class="pricing-features">
            <li v-for="feature in plan.features" :key="feature" class="pricing-feature">
              <span class="pricing-feature-icon" aria-hidden="true">
                <svg viewBox="0 0 16 16" fill="none">
                  <path
                    d="M3.4 8.3L6.5 11.3L12.6 5.2"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
              <span>{{ feature }}</span>
            </li>
          </ul>

          <a href="https://t.me/M1ke994" target="_blank" rel="noopener" class="pricing-cta">Связаться</a>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { siteData } from "~/assets/data";

const pricing = siteData.pricing;
</script>

<style scoped>
.pricing-section {
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
      115% 120% at 50% 98%,
      rgba(225, 234, 249, 0.88) 0%,
      rgba(236, 243, 255, 0.25) 54%,
      rgba(236, 243, 255, 0) 100%
    ),
    linear-gradient(
      180deg,
      rgba(246, 250, 255, 0.95) 0%,
      rgba(238, 244, 254, 0.88) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 22px 52px rgba(53, 79, 122, 0.11);
  scroll-margin-top: 112px;
}

.pricing-glow {
  position: absolute;
  z-index: -2;
  pointer-events: none;
  border-radius: 999px;
}

.pricing-glow--left {
  left: -12%;
  top: 10%;
  width: min(40vw, 540px);
  aspect-ratio: 1;
  background:
    radial-gradient(
      circle,
      rgba(182, 209, 246, 0.5) 0%,
      rgba(182, 209, 246, 0.14) 45%,
      rgba(182, 209, 246, 0) 74%
    );
}

.pricing-glow--right {
  right: -10%;
  bottom: -6%;
  width: min(44vw, 620px);
  aspect-ratio: 1;
  background:
    radial-gradient(
      circle,
      rgba(154, 191, 245, 0.45) 0%,
      rgba(154, 191, 245, 0.16) 46%,
      rgba(154, 191, 245, 0) 72%
    );
}

.pricing-wave {
  position: absolute;
  z-index: -1;
  pointer-events: none;
  left: -10%;
  right: -10%;
  border-radius: 999px;
}

.pricing-wave--one {
  bottom: -226px;
  height: 336px;
  background:
    radial-gradient(
      100% 198% at 50% 0%,
      rgba(255, 255, 255, 0.9) 0%,
      rgba(240, 246, 255, 0.72) 47%,
      rgba(240, 246, 255, 0) 72%
    );
}

.pricing-content {
  position: relative;
  margin: 0 auto;
  width: 100%;
  max-width: 1270px;
  padding: 58px 28px 72px;
}

.pricing-header {
  margin: 0 auto;
  text-align: center;
}

.pricing-title {
  margin: 0;
  color: #1e2740;
  font-size: clamp(2rem, 3.05vw, 3.2rem);
  line-height: 1.08;
  letter-spacing: -0.025em;
  font-weight: 600;
}

.pricing-subtitle {
  margin: 16px auto 0;
  max-width: 900px;
  color: rgba(41, 52, 77, 0.78);
  font-size: clamp(1.03rem, 1.35vw, 1.32rem);
  line-height: 1.42;
  font-weight: 500;
}

.pricing-grid {
  margin-top: 38px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.pricing-card {
  position: relative;
  min-height: 438px;
  display: flex;
  flex-direction: column;
  border-radius: 22px;
  border: 1px solid rgba(227, 236, 250, 0.95);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.73) 0%,
      rgba(251, 255, 255, 0.58) 100%
    );
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    inset 0 -1px 0 rgba(228, 236, 250, 0.7),
    0 14px 34px rgba(78, 108, 160, 0.12);
  padding: 24px 22px 22px;
}

.pricing-card--featured {
  border-color: rgba(174, 205, 247, 0.95);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.92),
    0 20px 42px rgba(75, 119, 191, 0.2),
    0 0 0 1px rgba(188, 215, 250, 0.66);
}

.pricing-badge {
  position: absolute;
  top: 14px;
  right: 16px;
  border-radius: 999px;
  border: 1px solid rgba(152, 193, 245, 0.85);
  background: rgba(240, 248, 255, 0.88);
  color: #4f82c6;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  padding: 6px 10px;
}

.pricing-card-title {
  margin: 0;
  color: #1f2a43;
  font-size: clamp(1.46rem, 1.9vw, 1.86rem);
  line-height: 1.15;
  letter-spacing: -0.015em;
  font-weight: 700;
}

.pricing-card-price {
  margin: 13px 0 0;
  color: #2f5fbb;
  font-size: clamp(1.48rem, 2vw, 2rem);
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.pricing-card-description {
  margin: 10px 0 0;
  color: rgba(39, 50, 73, 0.72);
  font-size: 0.97rem;
  line-height: 1.38;
}

.pricing-features {
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pricing-feature {
  display: grid;
  grid-template-columns: 22px 1fr;
  gap: 8px;
  color: rgba(34, 46, 70, 0.86);
  font-size: 0.98rem;
  line-height: 1.4;
}

.pricing-feature-icon {
  margin-top: 2px;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(168, 201, 242, 0.9);
  background: rgba(234, 245, 255, 0.95);
  color: #4d86d2;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
}

.pricing-feature-icon svg {
  width: 12px;
  height: 12px;
}

.pricing-cta {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(165, 198, 244, 0.9);
  background:
    linear-gradient(
      180deg,
      rgba(253, 255, 255, 0.95) 0%,
      rgba(229, 242, 255, 0.96) 100%
    );
  color: #3d74c4;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1;
  text-decoration: none;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 8px 16px rgba(79, 122, 186, 0.18);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.pricing-cta:hover {
  transform: translateY(-1px);
  border-color: rgba(138, 183, 239, 0.96);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 11px 20px rgba(79, 122, 186, 0.23);
}

@media (max-width: 1130px) {
  .pricing-content {
    padding: 50px 22px 62px;
  }

  .pricing-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .pricing-card {
    min-height: 410px;
  }
}

@media (max-width: 767px) {
  .pricing-section {
    border-radius: 24px;
    scroll-margin-top: 96px;
  }

  .pricing-content {
    padding: 36px 14px 44px;
  }

  .pricing-subtitle {
    margin-top: 12px;
    font-size: 0.98rem;
    line-height: 1.45;
  }

  .pricing-grid {
    margin-top: 28px;
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .pricing-card {
    min-height: 0;
    border-radius: 18px;
    padding: 18px 14px 16px;
  }

  .pricing-badge {
    top: 12px;
    right: 12px;
  }

  .pricing-card-price {
    margin-top: 10px;
  }

  .pricing-features {
    margin-top: 14px;
    gap: 9px;
  }

  .pricing-feature {
    font-size: 0.94rem;
  }

  .pricing-cta {
    margin-top: 18px;
    min-height: 44px;
  }
}
</style>
