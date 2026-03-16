<template>
  <header
    class="landing-header fixed inset-x-0 top-0 z-[120] border-b border-[#dce6f5]/85 bg-[rgba(244,249,255,0.72)] backdrop-blur-[14px]"
  >
    <div class="landing-header__outer mx-auto w-full max-w-[1400px] px-3 py-2 sm:px-6 sm:py-2.5 lg:px-8">
      <div
        class="landing-header__inner mx-auto flex w-full max-w-[1280px] items-center justify-between gap-2 rounded-[18px] border border-[#dee5f2] bg-white/95 px-3 py-2.5 shadow-[0_12px_36px_rgba(34,51,90,0.08)] backdrop-blur sm:px-4"
      >
        <a href="/" class="landing-header__brand flex min-w-fit items-center gap-2.5 pr-2" @click.prevent="onBrandClick">
          <img :src="brand.logoSrc || '/landing_media/brand/logo.svg'" :alt="brand.name" class="landing-header__logo h-8 w-8" />
          <span class="landing-header__brand-name text-[22px] font-semibold tracking-[-0.02em] text-[#1f2738]">{{ brand.name }}</span>
        </a>

        <nav class="landing-header__desktop-nav hidden items-center gap-7 lg:flex" aria-label="Main navigation">
          <div
            v-for="item in nav"
            :key="`${item.label}-${item.href}`"
            class="desktop-nav-item"
            @mouseenter="item.children?.length ? openDesktopDropdown(item.label) : null"
            @mouseleave="item.children?.length ? scheduleDesktopDropdownClose() : null"
            @focusin="item.children?.length ? openDesktopDropdown(item.label) : null"
            @focusout="item.children?.length ? scheduleDesktopDropdownClose() : null"
          >
            <a
              :href="item.href"
              class="desktop-nav-link"
              :class="{ 'desktop-nav-link--active': isItemActive(item) }"
              @click.prevent="onNavClick(item)"
            >
              <span>{{ item.label }}</span>
              <svg
                v-if="item.children?.length"
                viewBox="0 0 16 16"
                fill="none"
                class="desktop-nav-caret"
                :class="{ 'desktop-nav-caret--open': activeDesktopDropdown === item.label }"
                aria-hidden="true"
              >
                <path
                  d="M4 6.5L8 10L12 6.5"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </a>

            <div
              v-if="item.children?.length"
              class="desktop-dropdown"
              :class="{ 'desktop-dropdown--open': activeDesktopDropdown === item.label }"
            >
              <a
                v-for="child in item.children"
                :key="`${item.label}-${child.label}-${child.href}`"
                :href="child.href"
                class="desktop-dropdown__link"
                @click.prevent="onNavChildClick(item, child)"
              >
                {{ child.label }}
              </a>
            </div>
          </div>
        </nav>

        <div class="landing-header__actions flex items-center gap-2 sm:gap-2.5">
          <a
            :href="headerCta.href"
            :target="headerCta.target || null"
            :rel="headerCta.rel || null"
            class="landing-header__cta btn-brand-gradient hidden min-h-10 items-center justify-center rounded-[11px] px-4 text-[15px] font-semibold text-white shadow-[0_10px_20px_rgba(47,106,255,0.35)] transition hover:brightness-105 sm:inline-flex sm:px-6 sm:text-[16px]"
          >
            {{ headerCta.label }}
          </a>

          <button
            type="button"
            aria-label="Menu"
            class="landing-header__burger inline-flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#d7dfee] bg-white text-[#2a3246] lg:hidden"
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
      <Transition name="mobile-menu-fade">
        <div v-if="isMobileMenuOpen" class="mobile-menu-wrap lg:hidden">
          <button class="mobile-menu-overlay" type="button" aria-label="Close menu" @click="closeMobileMenu" />

          <aside class="mobile-menu-sheet" role="dialog" aria-modal="true" aria-label="Mobile menu">
            <div class="mobile-menu-head">
              <button type="button" class="mobile-menu-head__brand" @click="onMobileBrandClick">
                <img :src="brand.logoSrc || '/landing_media/brand/logo.svg'" :alt="brand.name" class="mobile-menu-head__logo" />
                <span class="mobile-menu-head__title">{{ brand.name }}</span>
              </button>

              <button type="button" class="mobile-menu-close" aria-label="Close menu" @click="closeMobileMenu">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" />
                </svg>
              </button>
            </div>

            <nav class="mobile-menu-nav" aria-label="Mobile navigation">
              <div
                v-for="item in nav"
                :key="`mobile-${item.label}-${item.href}`"
                class="mobile-menu-item"
                :class="{ 'mobile-menu-item--expanded': isMobileSubmenuOpen(item.label) }"
              >
                <button
                  v-if="isMobileAccordionItem(item)"
                  type="button"
                  class="mobile-menu-item__trigger"
                  :aria-expanded="isMobileSubmenuOpen(item.label)"
                  @click="onMobileItemSelect(item)"
                >
                  <span class="mobile-menu-item__label">{{ item.label }}</span>
                  <svg
                    viewBox="0 0 18 18"
                    fill="none"
                    class="mobile-menu-item__caret"
                    :class="{ 'mobile-menu-item__caret--open': isMobileSubmenuOpen(item.label) }"
                    aria-hidden="true"
                  >
                    <path
                      d="M4.6 7L9 11.1L13.4 7"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </button>

                <a
                  v-else
                  :href="item.href"
                  class="mobile-menu-item__link"
                  :class="{ 'mobile-menu-item__link--active': isItemActive(item) }"
                  @click.prevent="onMobileItemSelect(item)"
                >
                  <span>{{ item.label }}</span>
                  <svg viewBox="0 0 18 18" fill="none" class="mobile-menu-item__arrow" aria-hidden="true">
                    <path d="M6.8 5.2L10.8 9L6.8 12.8" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
                  </svg>
                </a>

                <Transition name="mobile-submenu">
                  <div v-if="isMobileAccordionItem(item) && isMobileSubmenuOpen(item.label)" class="mobile-menu-subnav">
                    <a
                      v-for="child in item.children"
                      :key="`mobile-${item.label}-${child.label}-${child.href}`"
                      :href="child.href"
                      @click.prevent="onNavChildClick(item, child, true)"
                    >
                      {{ child.label }}
                    </a>
                  </div>
                </Transition>
              </div>
            </nav>

            <div v-if="mobileActions.length" class="mobile-menu-actions">
              <a
                v-for="(action, index) in mobileActions"
                :key="action.label"
                :href="action.href"
                :target="action.target || null"
                :rel="action.rel || null"
                class="mobile-menu-action"
                :class="index === mobileActions.length - 1 ? 'mobile-menu-action--primary' : 'mobile-menu-action--secondary'"
                @click="closeMobileMenu"
              >
                {{ action.label }}
              </a>
            </div>
          </aside>
        </div>
      </Transition>
    </Teleport>
  </header>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
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
  mobileActions: {
    type: Array,
    default: () => [],
  },
});

const route = useRoute();
const router = useRouter();

const isMobileMenuOpen = ref(false);
const scrollProgress = ref(0);
const activeDesktopDropdown = ref("");
const mobileExpandedItems = ref({});

let desktopDropdownCloseTimeout = 0;

function updateScrollProgress() {
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight;

  if (maxScroll <= 0) {
    scrollProgress.value = 0;
    return;
  }

  scrollProgress.value = Math.min(Math.max(window.scrollY / maxScroll, 0), 1);
}

function normalizeHash(hash) {
  if (!hash) return "";
  if (hash === "#footer") return "#contacts";
  return hash;
}

function scrollToHash(hash) {
  const normalizedHash = normalizeHash(hash);

  if (!normalizedHash) return;

  if (normalizedHash === "#top") {
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }

  const target = document.querySelector(normalizedHash);
  if (!target) return;

  target.scrollIntoView({ behavior: "smooth", block: "start" });
}

function isHashHref(href) {
  return String(href || "").startsWith("#");
}

function isInternalHref(href) {
  return String(href || "").startsWith("/");
}

function clearDesktopDropdownCloseTimeout() {
  if (!desktopDropdownCloseTimeout) return;
  clearTimeout(desktopDropdownCloseTimeout);
  desktopDropdownCloseTimeout = 0;
}

function openDesktopDropdown(label) {
  clearDesktopDropdownCloseTimeout();
  activeDesktopDropdown.value = label;
}

function scheduleDesktopDropdownClose() {
  clearDesktopDropdownCloseTimeout();
  desktopDropdownCloseTimeout = setTimeout(() => {
    activeDesktopDropdown.value = "";
  }, 120);
}

function closeDesktopDropdown() {
  clearDesktopDropdownCloseTimeout();
  activeDesktopDropdown.value = "";
}

async function navigateToHash(hash) {
  const normalizedHash = normalizeHash(hash);
  if (!normalizedHash) return;

  const shouldPushToHome = route.path !== "/";

  if (shouldPushToHome || route.hash !== normalizedHash) {
    await router.push({ path: "/", hash: normalizedHash });
  }

  await nextTick();
  requestAnimationFrame(() => {
    scrollToHash(normalizedHash);
  });
}

async function navigateToHref(href, target, rel) {
  if (!href) return;

  if (href === "/" && route.path === "/" && !route.hash) {
    scrollToHash("#top");
    return;
  }

  if (isHashHref(href)) {
    await navigateToHash(href);
    return;
  }

  if (isInternalHref(href)) {
    await router.push(href);
    return;
  }

  if (target === "_blank") {
    window.open(href, "_blank", rel || "noopener");
    return;
  }

  window.location.href = href;
}

async function onNavClick(item, closeAfter = false) {
  await navigateToHref(item?.href, item?.target, item?.rel);
  closeDesktopDropdown();

  if (closeAfter) {
    closeMobileMenu();
  }
}

async function onNavChildClick(parentItem, childItem, closeAfter = false) {
  if (isHashHref(childItem?.href)) {
    await navigateToHash(childItem.href);
  } else {
    await navigateToHref(childItem?.href, childItem?.target, childItem?.rel);
  }

  closeDesktopDropdown();

  if (closeAfter) {
    closeMobileMenu();
  }
}

async function onBrandClick() {
  if (route.path === "/") {
    scrollToHash("#top");
    return;
  }

  await router.push("/");
}

function isMobileAccordionItem(item) {
  return Boolean(item?.children?.length);
}

function getDefaultMobileExpandedMap() {
  return props.nav.reduce((acc, item) => {
    if (isMobileAccordionItem(item)) {
      acc[item.label] = false;
    }
    return acc;
  }, {});
}

function toggleMobileSubmenu(label) {
  const currentlyOpen = Boolean(mobileExpandedItems.value[label]);

  const nextState = Object.keys(mobileExpandedItems.value).reduce((acc, key) => {
    acc[key] = false;
    return acc;
  }, {});

  if (!currentlyOpen) {
    nextState[label] = true;
  }

  mobileExpandedItems.value = nextState;
}

function isMobileSubmenuOpen(label) {
  return Boolean(mobileExpandedItems.value[label]);
}

async function onMobileBrandClick() {
  await onBrandClick();
  closeMobileMenu();
}

async function onMobileItemSelect(item) {
  if (isMobileAccordionItem(item)) {
    toggleMobileSubmenu(item.label);
    return;
  }

  await onNavClick(item, true);
}

function openMobileMenu() {
  isMobileMenuOpen.value = true;
  mobileExpandedItems.value = getDefaultMobileExpandedMap();
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

function isItemActive(item) {
  if (!item?.href) return false;

  if (item.href === "/" && route.path === "/") return true;
  if (item.href !== "/" && isInternalHref(item.href) && route.path.startsWith(item.href)) return true;

  return false;
}

watch(
  () => route.fullPath,
  () => {
    closeDesktopDropdown();

    if (isMobileMenuOpen.value) {
      closeMobileMenu();
    }
  },
);

onMounted(() => {
  mobileExpandedItems.value = getDefaultMobileExpandedMap();
  window.addEventListener("keydown", handleEscape);
  window.addEventListener("scroll", updateScrollProgress, { passive: true });
  window.addEventListener("resize", updateScrollProgress, { passive: true });
  updateScrollProgress();
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleEscape);
  window.removeEventListener("scroll", updateScrollProgress);
  window.removeEventListener("resize", updateScrollProgress);
  clearDesktopDropdownCloseTimeout();
  document.body.style.overflow = "";
});
</script>

<style scoped>
.landing-header {
  position: fixed;
  inset-inline: 0;
  top: 0;
  z-index: 120;
  border-bottom: 1px solid rgba(220, 230, 245, 0.85);
  background: rgba(244, 249, 255, 0.72);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.landing-header__outer {
  margin: 0 auto;
  width: 100%;
  max-width: 1400px;
  padding: 8px 12px;
}

.landing-header__inner {
  margin: 0 auto;
  width: 100%;
  max-width: 1280px;
  border-radius: 18px;
  border: 1px solid #dee5f2;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 36px rgba(34, 51, 90, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 10px 12px;
}

.landing-header__brand {
  min-width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 0.625rem;
  padding-right: 0.5rem;
}

.landing-header__logo {
  width: 32px;
  height: 32px;
}

.landing-header__brand-name {
  color: #1f2738;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.landing-header__desktop-nav {
  display: none;
  align-items: center;
  gap: 1.75rem;
}

.landing-header__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.landing-header__cta {
  display: none;
  min-height: 40px;
  border-radius: 11px;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(47, 106, 255, 0.35);
}

.landing-header__burger {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid #d7dfee;
  background: #fff;
  color: #2a3246;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

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

.desktop-nav-item {
  position: relative;
}

.desktop-nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  text-decoration: none;
  color: #2a3244;
  font-size: 0.98rem;
  line-height: 1.2;
  font-weight: 600;
  transition: color 0.2s ease;
}

.desktop-nav-link:hover,
.desktop-nav-link--active {
  color: #1d5fff;
}

.desktop-nav-caret {
  width: 14px;
  height: 14px;
  color: rgba(72, 94, 131, 0.72);
  transition: transform 0.2s ease;
}

.desktop-nav-caret--open {
  transform: rotate(180deg);
}

.desktop-dropdown {
  position: absolute;
  left: 0;
  top: calc(100% + 12px);
  min-width: 220px;
  border-radius: 14px;
  border: 1px solid rgba(208, 223, 245, 0.95);
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 16px 30px rgba(47, 71, 111, 0.16);
  opacity: 0;
  transform: translateY(6px);
  pointer-events: none;
  transition: opacity 0.16s ease, transform 0.16s ease;
  padding: 8px;
}

.desktop-dropdown--open {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.desktop-dropdown__link {
  display: block;
  border-radius: 10px;
  color: #2a3244;
  text-decoration: none;
  font-size: 0.92rem;
  line-height: 1.32;
  font-weight: 600;
  padding: 9px 10px;
}

.desktop-dropdown__link:hover {
  background: rgba(234, 244, 255, 0.85);
  color: #255fb7;
}

.mobile-menu-wrap {
  position: fixed;
  inset: 0;
  z-index: 140;
  display: flex;
  justify-content: flex-end;
}

.mobile-menu-overlay {
  position: absolute;
  inset: 0;
  border: 0;
  background: rgba(14, 23, 39, 0.52);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.mobile-menu-sheet {
  position: relative;
  z-index: 1;
  width: min(100%, 420px);
  height: 100%;
  border-left: 1px solid rgba(202, 218, 241, 0.95);
  background:
    linear-gradient(
      180deg,
      rgba(251, 253, 255, 0.98) 0%,
      rgba(241, 247, 255, 0.96) 100%
    );
  box-shadow: -24px 0 46px rgba(31, 49, 85, 0.24);
  padding: calc(14px + env(safe-area-inset-top)) 14px calc(18px + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
}

.mobile-menu-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(212, 224, 244, 0.82);
}

.mobile-menu-head__brand {
  min-width: 0;
  border: 0;
  padding: 0;
  background: transparent;
  display: inline-flex;
  align-items: center;
  gap: 11px;
  color: #1e2c47;
}

.mobile-menu-head__logo {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid rgba(193, 212, 242, 0.9);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 6px 14px rgba(74, 110, 172, 0.14);
}

.mobile-menu-head__title {
  display: block;
  color: #1f2a43;
  font-size: 1.08rem;
  line-height: 1.22;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.mobile-menu-close {
  width: 52px;
  height: 52px;
  border-radius: 15px;
  border: 1px solid rgba(182, 203, 236, 0.94);
  background: rgba(251, 254, 255, 0.95);
  color: #3f6cae;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mobile-menu-close svg {
  width: 23px;
  height: 23px;
}

.mobile-menu-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mobile-menu-item {
  border-radius: 16px;
  border: 1px solid rgba(216, 229, 247, 0.96);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.82);
  padding: 6px;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.mobile-menu-item--expanded {
  border-color: rgba(176, 203, 242, 0.96);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.95) 0%,
      rgba(243, 249, 255, 0.92) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.92),
    0 10px 20px rgba(57, 88, 138, 0.11);
}

.mobile-menu-item__trigger,
.mobile-menu-item__link {
  width: 100%;
  min-height: 52px;
  border-radius: 12px;
  border: 0;
  background: transparent;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #23304a;
  text-decoration: none;
  font-size: 1.02rem;
  line-height: 1.3;
  font-weight: 650;
  letter-spacing: -0.01em;
  text-align: left;
}

.mobile-menu-item__link--active {
  background: rgba(238, 246, 255, 0.92);
  color: #255dab;
}

.mobile-menu-item__label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mobile-menu-item__caret,
.mobile-menu-item__arrow {
  width: 18px;
  height: 18px;
  color: #6183b8;
  flex-shrink: 0;
}

.mobile-menu-item__caret {
  transition: transform 0.24s ease, color 0.24s ease;
}

.mobile-menu-item__caret--open {
  transform: rotate(180deg);
  color: #2d61b2;
}

.mobile-menu-subnav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 6px 4px;
}

.mobile-menu-subnav a {
  min-height: 46px;
  border-radius: 12px;
  border: 1px solid rgba(216, 229, 247, 0.96);
  background: rgba(252, 254, 255, 0.96);
  color: #26334b;
  text-decoration: none;
  font-size: 0.94rem;
  line-height: 1.3;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
}

.mobile-menu-actions {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid rgba(212, 224, 244, 0.82);
}

.mobile-menu-action {
  min-height: 48px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-size: 0.96rem;
  line-height: 1.2;
  font-weight: 700;
}

.mobile-menu-action--secondary {
  border: 1px solid rgba(181, 206, 242, 0.95);
  background:
    linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.94) 0%,
      rgba(233, 244, 255, 0.98) 100%
    );
  color: #3f73c0;
}

.mobile-menu-action--primary {
  border: 1px solid rgba(66, 124, 232, 0.88);
  background-image: var(--brand-gradient);
  color: #fff;
  box-shadow: 0 12px 24px rgba(47, 106, 255, 0.28);
}

.mobile-menu-fade-enter-active,
.mobile-menu-fade-leave-active {
  transition: opacity 0.24s ease;
}

.mobile-menu-fade-enter-from,
.mobile-menu-fade-leave-to {
  opacity: 0;
}

.mobile-menu-fade-enter-active .mobile-menu-sheet,
.mobile-menu-fade-leave-active .mobile-menu-sheet {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.2s ease;
}

.mobile-menu-fade-enter-from .mobile-menu-sheet,
.mobile-menu-fade-leave-to .mobile-menu-sheet {
  transform: translateX(26px);
  opacity: 0;
}

.mobile-submenu-enter-active,
.mobile-submenu-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.mobile-submenu-enter-from,
.mobile-submenu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (min-width: 640px) {
  .mobile-menu-sheet {
    width: min(430px, calc(100% - 24px));
    height: calc(100% - 24px);
    margin: 12px;
    border-radius: 24px;
    border: 1px solid rgba(202, 218, 241, 0.95);
  }
}

@media (min-width: 640px) {
  .landing-header__outer {
    padding: 10px 24px;
  }

  .landing-header__inner {
    padding: 10px 16px;
  }

  .landing-header__actions {
    gap: 0.625rem;
  }

  .landing-header__cta {
    display: inline-flex;
    padding: 0 1.5rem;
    font-size: 1rem;
  }
}

@media (min-width: 1024px) {
  .landing-header__outer {
    padding: 10px 32px;
  }

  .landing-header__desktop-nav {
    display: flex;
  }

  .landing-header__burger {
    display: none;
  }
}
</style>

