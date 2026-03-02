<template>
  <div class="hero-demo">
    <div class="hero-demo__backlight" />

    <div class="hero-demo__frame">
      <div class="hero-demo__toolbar">
        <div class="hero-demo__dots" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <p class="hero-demo__toolbar-title">{{ resolvedDemo.title }}</p>
        <span class="hero-demo__badge">{{ resolvedDemo.badge }}</span>
      </div>

      <div class="hero-demo__screen">
        <img
          class="hero-demo__image"
          src="/landing_media/Hero/hero.gif"
          alt="TrackNode dashboard preview"
          loading="lazy"
        />
        <div class="hero-demo__shade" />

        <article class="hero-demo__card hero-demo__card--conversion" :class="{ 'is-pop': isAccented }">
          <div class="hero-demo__card-head">
            <p class="hero-demo__label">{{ resolvedDemo.conversion.title }}</p>
            <span class="hero-demo__trend">{{ resolvedDemo.conversion.growth }}</span>
          </div>

          <p class="hero-demo__value">{{ frame.conversion.toFixed(2) }}%</p>
          <p class="hero-demo__period">{{ resolvedDemo.conversion.period }}</p>

          <div class="hero-demo__chart-wrap">
            <svg viewBox="0 0 220 80" class="hero-demo__chart">
              <defs>
                <linearGradient id="hero-conversion-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#22c55e" stop-opacity="0.38" />
                  <stop offset="100%" stop-color="#22c55e" stop-opacity="0" />
                </linearGradient>
                <linearGradient id="hero-conversion-stroke" x1="10" y1="68" x2="210" y2="8" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#10b981" stop-opacity="0.74" />
                  <stop offset="100%" stop-color="#22c55e" stop-opacity="1" />
                </linearGradient>
              </defs>

              <g opacity="0.25" stroke="rgba(148,163,184,0.46)" stroke-width="1">
                <line x1="10" y1="68" x2="210" y2="68" />
                <line x1="10" y1="52" x2="210" y2="52" />
                <line x1="10" y1="36" x2="210" y2="36" />
                <line x1="10" y1="20" x2="210" y2="20" />
              </g>

              <path :d="CHART_AREA_PATH" fill="url(#hero-conversion-fill)" :opacity="areaOpacity" />

              <path
                ref="lineRef"
                :d="CHART_LINE_PATH"
                fill="none"
                stroke="url(#hero-conversion-stroke)"
                stroke-width="3"
                stroke-linecap="round"
                stroke-linejoin="round"
                :style="lineStyle"
              />

              <circle :cx="frame.marker.x" :cy="frame.marker.y" r="4.5" fill="#22c55e" />
              <circle
                :cx="frame.marker.x"
                :cy="frame.marker.y"
                r="8"
                fill="none"
                stroke="rgba(34,197,94,0.34)"
                stroke-width="2"
                class="hero-demo__ping"
              />
            </svg>
          </div>
        </article>

        <article class="hero-demo__card hero-demo__card--visits">
          <p class="hero-demo__label">{{ resolvedDemo.visits.title }}</p>
          <p class="hero-demo__metric">{{ (frame.visits / 1000).toFixed(1) }}K</p>

          <div class="hero-demo__meter">
            <span :style="{ width: `${visitsMeterWidth}%` }" />
          </div>
          <p class="hero-demo__metric-trend">{{ resolvedDemo.visits.growth }}</p>
        </article>

        <article class="hero-demo__card hero-demo__card--leads">
          <p class="hero-demo__label">{{ resolvedDemo.leads.title }}</p>
          <p class="hero-demo__metric">{{ frame.leads }}</p>

          <ul class="hero-demo__bars" aria-hidden="true">
            <li v-for="(height, index) in leadBars" :key="`lead-bar-${index}`">
              <span :style="{ height: `${height}%` }" />
            </li>
          </ul>
          <p class="hero-demo__metric-trend">{{ resolvedDemo.leads.growth }}</p>
        </article>
      </div>
    </div>

    <div class="hero-demo__base" />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";

const DEFAULT_DEMO = {
  title: "Dashboard preview",
  badge: "LIVE PREVIEW",
  conversion: {
    title: "Конверсия",
    period: "за последние 7 дней",
    growth: "+7.5%",
  },
  visits: {
    title: "Визиты",
    growth: "+3.2%",
  },
  leads: {
    title: "Заявки",
    growth: "+12%",
  },
};

const props = defineProps({
  demo: {
    type: Object,
    default: () => ({}),
  },
});

const resolvedDemo = computed(() => ({
  title: props.demo?.title || DEFAULT_DEMO.title,
  badge: props.demo?.badge || DEFAULT_DEMO.badge,
  conversion: {
    ...DEFAULT_DEMO.conversion,
    ...(props.demo?.conversion || {}),
  },
  visits: {
    ...DEFAULT_DEMO.visits,
    ...(props.demo?.visits || {}),
  },
  leads: {
    ...DEFAULT_DEMO.leads,
    ...(props.demo?.leads || {}),
  },
}));

const START_CONVERSION = 8.03;
const END_CONVERSION = 8.61;
const START_VISITS = 18200;
const END_VISITS = 19640;
const START_LEADS = 124;
const END_LEADS = 142;

const ANIMATION_DURATION_MS = 2200;
const PAUSE_DURATION_MS = 2400;

const CHART_LINE_PATH =
  "M10 68 C40 61 65 58 90 50 C113 43 135 38 158 28 C178 21 192 14 210 9";
const CHART_AREA_PATH =
  "M10 68 C40 61 65 58 90 50 C113 43 135 38 158 28 C178 21 192 14 210 9 L210 76 L10 76 Z";
const INITIAL_MARKER = { x: 10, y: 68 };

const lineRef = ref(null);
const lineLength = ref(1);
const markerStart = ref({ ...INITIAL_MARKER });
const isAccented = ref(false);

const frame = reactive({
  conversion: START_CONVERSION,
  visits: START_VISITS,
  leads: START_LEADS,
  progress: 0,
  marker: { ...INITIAL_MARKER },
});

let frameId = 0;
let restartTimeout = 0;
let accentTimeout = 0;

function easeOutCubic(value) {
  return 1 - (1 - value) ** 3;
}

const lineStyle = computed(() => ({
  strokeDasharray: lineLength.value,
  strokeDashoffset: lineLength.value * (1 - frame.progress),
  filter: "drop-shadow(0 0 4px rgba(34,197,94,0.26))",
}));

const areaOpacity = computed(() => Math.max(0.18, Math.min(0.48, 0.18 + frame.progress * 0.36)));
const visitsMeterWidth = computed(() => Math.round(56 + frame.progress * 32));

const leadBars = computed(() => {
  const start = [30, 38, 48, 57, 66, 72];
  const end = [38, 49, 62, 74, 84, 92];
  return start.map((value, index) => Math.round(value + (end[index] - value) * frame.progress));
});

onMounted(() => {
  const pathElement = lineRef.value;

  if (pathElement) {
    const totalLength = pathElement.getTotalLength();
    lineLength.value = totalLength;

    const startPoint = pathElement.getPointAtLength(0);
    markerStart.value = { x: startPoint.x, y: startPoint.y };
    frame.marker = { x: startPoint.x, y: startPoint.y };
  }

  let animationStart = 0;

  const animate = (timestamp) => {
    if (!animationStart) {
      animationStart = timestamp;
    }

    const elapsed = timestamp - animationStart;
    const linearProgress = Math.min(elapsed / ANIMATION_DURATION_MS, 1);
    const easedProgress = easeOutCubic(linearProgress);

    frame.progress = easedProgress;
    frame.conversion = START_CONVERSION + (END_CONVERSION - START_CONVERSION) * easedProgress;
    frame.visits = Math.round(START_VISITS + (END_VISITS - START_VISITS) * easedProgress);
    frame.leads = Math.round(START_LEADS + (END_LEADS - START_LEADS) * easedProgress);

    if (pathElement && lineLength.value > 0) {
      const point = pathElement.getPointAtLength(lineLength.value * easedProgress);
      frame.marker = { x: point.x, y: point.y };
    }

    if (linearProgress < 1) {
      frameId = window.requestAnimationFrame(animate);
      return;
    }

    isAccented.value = true;

    accentTimeout = window.setTimeout(() => {
      isAccented.value = false;
    }, 420);

    restartTimeout = window.setTimeout(() => {
      animationStart = 0;
      frame.progress = 0;
      frame.conversion = START_CONVERSION;
      frame.visits = START_VISITS;
      frame.leads = START_LEADS;
      frame.marker = { ...markerStart.value };

      frameId = window.requestAnimationFrame(animate);
    }, PAUSE_DURATION_MS);
  };

  frameId = window.requestAnimationFrame(animate);
});

onBeforeUnmount(() => {
  window.cancelAnimationFrame(frameId);
  window.clearTimeout(restartTimeout);
  window.clearTimeout(accentTimeout);
});
</script>

<style scoped>
.hero-demo {
  position: relative;
  width: 100%;
}

.hero-demo__backlight {
  pointer-events: none;
  position: absolute;
  inset: -24px -28px 24px -18px;
  border-radius: 36px;
  background:
    radial-gradient(circle at 77% 20%, rgba(125, 211, 252, 0.48) 0%, rgba(125, 211, 252, 0) 58%),
    radial-gradient(circle at 16% 84%, rgba(147, 197, 253, 0.42) 0%, rgba(147, 197, 253, 0) 56%);
  filter: blur(32px);
}

.hero-demo__frame {
  position: relative;
  z-index: 1;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.85);
  overflow: hidden;
  box-shadow:
    0 32px 72px rgba(19, 41, 79, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  background: linear-gradient(180deg, #f3f8ff 0%, #eaf1fe 100%);
}

.hero-demo__toolbar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(203, 213, 225, 0.66);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
}

.hero-demo__dots {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.hero-demo__dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.hero-demo__dots span:nth-child(1) {
  background: #fca5a5;
}

.hero-demo__dots span:nth-child(2) {
  background: #fcd34d;
}

.hero-demo__dots span:nth-child(3) {
  background: #86efac;
}

.hero-demo__toolbar-title {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

.hero-demo__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid rgba(191, 219, 254, 0.9);
  background: rgba(239, 246, 255, 0.96);
  padding: 4px 9px;
  font-size: 10px;
  font-weight: 700;
  color: #1d4ed8;
  letter-spacing: 0.08em;
}

.hero-demo__screen {
  position: relative;
  min-height: 306px;
  aspect-ratio: 16 / 10;
  overflow: hidden;
}

.hero-demo__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  filter: saturate(1.04) contrast(1.03);
}

.hero-demo__shade {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(248, 251, 255, 0.2) 0%, rgba(248, 251, 255, 0.55) 100%),
    linear-gradient(92deg, rgba(15, 23, 42, 0.12) 0%, rgba(15, 23, 42, 0.02) 46%, rgba(15, 23, 42, 0.16) 100%);
}

.hero-demo__card {
  position: absolute;
  border: 1px solid rgba(255, 255, 255, 0.88);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 26px rgba(15, 23, 42, 0.16);
  backdrop-filter: blur(9px);
}

.hero-demo__card--conversion {
  left: 16px;
  top: 16px;
  width: min(58%, 290px);
  padding: 12px 12px 10px;
  transition:
    transform 0.28s ease,
    box-shadow 0.28s ease;
}

.hero-demo__card--conversion.is-pop {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 18px 30px rgba(21, 128, 61, 0.22);
}

.hero-demo__card--visits {
  left: 16px;
  bottom: 16px;
  width: 180px;
  padding: 10px;
}

.hero-demo__card--leads {
  right: 16px;
  bottom: 16px;
  width: 170px;
  padding: 10px;
}

.hero-demo__card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.hero-demo__label {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.hero-demo__trend {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 2px 7px;
  font-size: 11px;
  font-weight: 700;
  color: #15803d;
  background: rgba(220, 252, 231, 0.9);
}

.hero-demo__value {
  margin: 6px 0 2px;
  font-size: 30px;
  line-height: 1;
  letter-spacing: -0.02em;
  font-weight: 700;
  color: #0f172a;
}

.hero-demo__period {
  margin: 0 0 6px;
  font-size: 11px;
  color: #64748b;
}

.hero-demo__chart-wrap {
  height: 86px;
}

.hero-demo__chart {
  width: 100%;
  height: 100%;
}

.hero-demo__ping {
  animation: hero-ping 2.4s ease-out infinite;
}

.hero-demo__metric {
  margin: 4px 0;
  font-size: 26px;
  line-height: 1;
  letter-spacing: -0.02em;
  font-weight: 700;
  color: #0f172a;
}

.hero-demo__meter {
  width: 100%;
  height: 7px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.hero-demo__meter span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #34d399 0%, #16a34a 100%);
  transition: width 0.28s ease;
}

.hero-demo__metric-trend {
  margin: 6px 0 0;
  font-size: 11px;
  font-weight: 700;
  color: #15803d;
}

.hero-demo__bars {
  list-style: none;
  margin: 6px 0 0;
  padding: 0;
  height: 44px;
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  align-items: end;
  gap: 4px;
}

.hero-demo__bars li {
  display: flex;
  align-items: end;
  height: 100%;
}

.hero-demo__bars span {
  width: 100%;
  border-radius: 5px 5px 3px 3px;
  background: linear-gradient(180deg, #93c5fd 0%, #2563eb 100%);
  transition: height 0.24s ease;
}

.hero-demo__base {
  width: 90%;
  height: 11px;
  margin: 2px auto 0;
  border-radius: 0 0 20px 20px;
  background: linear-gradient(180deg, #dae4f5 0%, #bccbe3 100%);
  box-shadow: 0 10px 18px rgba(31, 57, 98, 0.25);
}

@keyframes hero-ping {
  0% {
    opacity: 0.75;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(1.65);
  }
}

@media (max-width: 900px) {
  .hero-demo__screen {
    min-height: 280px;
  }

  .hero-demo__card--conversion {
    width: min(64%, 280px);
  }
}

@media (max-width: 640px) {
  .hero-demo__toolbar {
    padding: 10px 12px;
  }

  .hero-demo__badge {
    display: none;
  }

  .hero-demo__screen {
    min-height: 260px;
  }

  .hero-demo__card--conversion {
    left: 10px;
    top: 10px;
    width: calc(100% - 20px);
    max-width: none;
  }

  .hero-demo__card--visits {
    left: 10px;
    bottom: 10px;
    width: 46%;
    min-width: 126px;
  }

  .hero-demo__card--leads {
    right: 10px;
    bottom: 10px;
    width: 46%;
    min-width: 122px;
  }
}
</style>
