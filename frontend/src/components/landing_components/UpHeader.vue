<template>
  <header
    class="fixed inset-x-0 top-0 z-[120] border-b border-[#dce6f5]/85 bg-[rgba(244,249,255,0.72)] backdrop-blur-[14px]"
  >
    <div class="mx-auto w-full max-w-[1400px] px-3 py-2 sm:px-6 sm:py-2.5 lg:px-8">
      <div class="mx-auto flex w-full max-w-[1280px] items-center justify-between gap-2 rounded-[18px] border border-[#dee5f2] bg-white/95 px-3 py-2.5 shadow-[0_12px_36px_rgba(34,51,90,0.08)] backdrop-blur sm:px-4">
        <a href="#top" class="flex min-w-fit items-center gap-2.5 pr-2" @click.prevent="scrollTo('#top')">
          <img src="/brand/logo.svg" alt="TrackNode" class="h-8 w-8" />
          <span class="text-[22px] font-semibold tracking-[-0.02em] text-[#1f2738]">{{ brand.name }}</span>
        </a>

        <nav class="hidden items-center gap-8 lg:flex">
          <a
            v-for="item in nav"
            :key="item.href"
            :href="item.href"
            class="inline-flex items-center gap-1.5 text-[16px] font-medium text-[#2a3244] transition-colors hover:text-[#1d5fff]"
            @click.prevent="onNavClick(item)"
          >
            {{ item.label }}
          </a>
        </nav>

        <div class="flex items-center gap-2 sm:gap-2.5">
          <a
            :href="headerCta.href"
            :target="headerCta.target || null"
            :rel="headerCta.rel || null"
            class="btn-brand-gradient hidden min-h-10 items-center justify-center rounded-[11px] px-4 text-[15px] font-semibold text-white shadow-[0_10px_20px_rgba(47,106,255,0.35)] transition hover:brightness-105 sm:inline-flex sm:px-6 sm:text-[16px]"
          >
            {{ headerCta.label }}
          </a>

          <button
            type="button"
            aria-label="Menu"
            class="inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#d7dfee] bg-white text-[#2a3246] lg:hidden"
            @click="openMobileMenu"
          >
            <svg viewBox="0 0 20 20" class="h-[16px] w-[16px]" fill="none" aria-hidden="true">
              <path d="M4 6H16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
              <path d="M4 10H16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
              <path d="M4 14H16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div class="header-scroll-progress" aria-hidden="true">
      <span :style="{ transform: `scaleX(${scrollProgress})` }" />
    </div>

    <Teleport to="body">
      <div v-if="isMobileMenuOpen" class="mobile-menu-wrap lg:hidden">
        <button class="mobile-menu-overlay" type="button" aria-label="Закрыть меню" @click="closeMobileMenu" />

        <aside class="mobile-menu-sheet" role="dialog" aria-modal="true" aria-label="Мобильное меню">
          <div class="mobile-menu-head">
            <span>Меню</span>
            <button type="button" aria-label="Закрыть меню" @click="closeMobileMenu">
              <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
              </svg>
            </button>
          </div>

          <nav class="mobile-menu-nav">
            <a
              v-for="item in nav"
              :key="`mobile-${item.href}`"
              :href="item.href"
              @click.prevent="onNavClick(item, true)"
            >
              {{ item.label }}
            </a>
          </nav>

          <div class="mobile-menu-actions">
            <a href="https://tracknot.ru" target="_blank" rel="noopener" @click="closeMobileMenu">
              Войти
            </a>
            <a href="https://tracknot.ru" target="_blank" rel="noopener" @click="closeMobileMenu">
              Зарегистрироваться
            </a>
          </div>
        </aside>
      </div>
    </Teleport>
  </header>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

defineProps({
  brand: {
    type: Object,
    required: true,
  },
  nav: {
    type: Array,
    required: true,
  },
  headerCta: {
    type: Object,
    required: true,
  },
});

const isMobileMenuOpen = ref(false);
const scrollProgress = ref(0);

function updateScrollProgress() {
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight;

  if (maxScroll <= 0) {
    scrollProgress.value = 0;
    return;
  }

  scrollProgress.value = Math.min(Math.max(window.scrollY / maxScroll, 0), 1);
}

function scrollTo(selector) {
  if (!selector || !selector.startsWith("#")) {
    return;
  }

  if (selector === "#top") {
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }

  const target = document.querySelector(selector);
  if (!target) {
    return;
  }

  target.scrollIntoView({ behavior: "smooth", block: "start" });
}

function onNavClick(item, closeAfter = false) {
  if (item?.href?.startsWith("#")) {
    scrollTo(item.href);
  } else if (item?.href) {
    if (item.target === "_blank") {
      window.open(item.href, "_blank", "noopener");
    } else {
      window.location.href = item.href;
    }
  }

  if (closeAfter) {
    closeMobileMenu();
  }
}

function openMobileMenu() {
  isMobileMenuOpen.value = true;
  document.body.style.overflow = "hidden";
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false;
  document.body.style.overflow = "";
}

function handleEscape(event) {
  if (event.key === "Escape" && isMobileMenuOpen.value) {
    closeMobileMenu();
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleEscape);
  window.addEventListener("scroll", updateScrollProgress, { passive: true });
  window.addEventListener("resize", updateScrollProgress, { passive: true });
  updateScrollProgress();
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleEscape);
  window.removeEventListener("scroll", updateScrollProgress);
  window.removeEventListener("resize", updateScrollProgress);
  document.body.style.overflow = "";
});
</script>

<style scoped>
.header-scroll-progress {
  height: 3px;
  width: 100%;
  background: rgba(210, 223, 243, 0.52);
  overflow: hidden;
}

.header-scroll-progress span {
  display: block;
  height: 100%;
  width: 100%;
  transform-origin: left center;
  transform: scaleX(0);
  background-image: var(--brand-gradient);
  box-shadow: 0 0 12px rgba(52, 124, 255, 0.35);
  transition: transform 0.14s linear;
}

.mobile-menu-wrap {
  position: fixed;
  inset: 0;
  z-index: 140;
}

.mobile-menu-overlay {
  position: absolute;
  inset: 0;
  border: 0;
  background: rgba(18, 29, 50, 0.38);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.mobile-menu-sheet {
  position: absolute;
  right: 12px;
  left: 12px;
  top: 12px;
  border-radius: 18px;
  border: 1px solid rgba(214, 227, 246, 0.95);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.94) 0%,
      rgba(247, 252, 255, 0.88) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 20px 40px rgba(34, 53, 90, 0.24);
  padding: 14px;
}

.mobile-menu-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #1f2a43;
  font-size: 1.02rem;
  font-weight: 700;
}

.mobile-menu-head button {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  border: 1px solid rgba(188, 208, 238, 0.9);
  background: rgba(249, 253, 255, 0.95);
  color: #4e79ba;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.mobile-menu-head svg {
  width: 15px;
  height: 15px;
}

.mobile-menu-nav {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mobile-menu-nav a {
  border-radius: 12px;
  border: 1px solid rgba(220, 232, 248, 0.95);
  background: rgba(255, 255, 255, 0.72);
  color: #2a3244;
  text-decoration: none;
  font-size: 0.96rem;
  font-weight: 600;
  line-height: 1.35;
  padding: 10px 12px;
}

.mobile-menu-actions {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-menu-actions a {
  min-height: 42px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 700;
}

.mobile-menu-actions a:first-child {
  border: 1px solid rgba(181, 206, 242, 0.95);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.92) 0%,
      rgba(233, 244, 255, 0.95) 100%
    );
  color: #3f73c0;
}

.mobile-menu-actions a:last-child {
  border: 1px solid rgba(66, 124, 232, 0.88);
  background-image: var(--brand-gradient);
  color: #fff;
  box-shadow: 0 10px 20px rgba(47, 106, 255, 0.28);
}
</style>
