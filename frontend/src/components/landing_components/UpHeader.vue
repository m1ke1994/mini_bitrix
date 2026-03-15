<template>
  <header
    class="fixed inset-x-0 top-0 z-[120] border-b border-[#dce6f5]/85 bg-[rgba(244,249,255,0.72)] backdrop-blur-[14px]"
  >
    <div class="mx-auto w-full max-w-[1400px] px-3 py-2 sm:px-6 sm:py-2.5 lg:px-8">
      <div
        class="mx-auto flex w-full max-w-[1280px] items-center justify-between gap-2 rounded-[18px] border border-[#dee5f2] bg-white/95 px-3 py-2.5 shadow-[0_12px_36px_rgba(34,51,90,0.08)] backdrop-blur sm:px-4"
      >
        <a href="/" class="flex min-w-fit items-center gap-2.5 pr-2" @click.prevent="onBrandClick">
          <img :src="brand.logoSrc || '/landing_media/brand/logo.svg'" :alt="brand.name" class="h-8 w-8" />
          <span class="text-[22px] font-semibold tracking-[-0.02em] text-[#1f2738]">{{ brand.name }}</span>
        </a>

        <nav class="hidden items-center gap-7 lg:flex" aria-label="Главная навигация">
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
            aria-label="Меню"
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

          <nav class="mobile-menu-nav" aria-label="Мобильная навигация">
            <div
              v-for="item in nav"
              :key="`mobile-${item.label}-${item.href}`"
              class="mobile-menu-item"
            >
              <div class="mobile-menu-item__head">
                <a :href="item.href" @click.prevent="onNavClick(item, true)">
                  {{ item.label }}
                </a>
                <button
                  v-if="item.children?.length"
                  type="button"
                  :aria-label="`Показать разделы пункта ${item.label}`"
                  @click="toggleMobileSubmenu(item.label)"
                >
                  <svg
                    viewBox="0 0 16 16"
                    fill="none"
                    :class="{ 'mobile-menu-item__caret--open': isMobileSubmenuOpen(item.label) }"
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
                </button>
              </div>

              <div v-if="item.children?.length && isMobileSubmenuOpen(item.label)" class="mobile-menu-subnav">
                <a
                  v-for="child in item.children"
                  :key="`mobile-${item.label}-${child.label}-${child.href}`"
                  :href="child.href"
                  @click.prevent="onNavChildClick(item, child, true)"
                >
                  {{ child.label }}
                </a>
              </div>
            </div>
          </nav>

          <div class="mobile-menu-actions">
            <a
              v-for="action in mobileActions"
              :key="action.label"
              :href="action.href"
              :target="action.target || null"
              :rel="action.rel || null"
              @click="closeMobileMenu"
            >
              {{ action.label }}
            </a>
          </div>
        </aside>
      </div>
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

function getDefaultMobileExpandedMap() {
  return props.nav.reduce((acc, item) => {
    if (item?.children?.length) {
      acc[item.label] = item.label === "Главная";
    }
    return acc;
  }, {});
}

function toggleMobileSubmenu(label) {
  mobileExpandedItems.value = {
    ...mobileExpandedItems.value,
    [label]: !mobileExpandedItems.value[label],
  };
}

function isMobileSubmenuOpen(label) {
  return Boolean(mobileExpandedItems.value[label]);
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
  gap: 8px;
}

.mobile-menu-item {
  border-radius: 12px;
  border: 1px solid rgba(220, 232, 248, 0.95);
  background: rgba(255, 255, 255, 0.72);
  padding: 8px;
}

.mobile-menu-item__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.mobile-menu-item__head a {
  color: #2a3244;
  text-decoration: none;
  font-size: 0.96rem;
  font-weight: 700;
  line-height: 1.35;
  padding: 2px 4px;
}

.mobile-menu-item__head button {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  border: 1px solid rgba(188, 208, 238, 0.9);
  background: rgba(249, 253, 255, 0.95);
  color: #4e79ba;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mobile-menu-item__head svg {
  width: 14px;
  height: 14px;
  transition: transform 0.2s ease;
}

.mobile-menu-item__caret--open {
  transform: rotate(180deg);
}

.mobile-menu-subnav {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 6px;
}

.mobile-menu-subnav a {
  border-radius: 10px;
  border: 1px solid rgba(220, 232, 248, 0.95);
  background: rgba(244, 249, 255, 0.8);
  color: #2a3244;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.35;
  padding: 8px 10px;
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
