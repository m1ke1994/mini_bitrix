import { ref } from "vue";

export const SITE_NAME = "TrackNode";
export const BASE_URL = "https://tracknode.ru";
export const DEFAULT_IMAGE = `${BASE_URL}/og-preview.jpg`;
export const DEFAULT_OG_IMAGE_ALT = "Интерфейс аналитики сайта TrackNode";
export const DEFAULT_TWITTER_IMAGE_ALT = "Дашборд учета заявок TrackNode";

export const DEFAULT_TITLE = "TrackNode: аналитика сайта и учет заявок с Telegram";
export const DEFAULT_DESCRIPTION =
  "TrackNode объединяет аналитику сайта, учет заявок и уведомления в Telegram, чтобы контролировать лиды, источники трафика и конверсию без потери обращений.";
export const DEFAULT_KEYWORDS =
  "анализ сайтов, аналитика сайта, SEO-оптимизация, отслеживание лидов, уведомления в Telegram, учет заявок, конверсия";

export function getCanonicalUrl(path = "/") {
  const normalizedPath = String(path || "/");
  if (normalizedPath === "/") {
    return `${BASE_URL}/`;
  }
  return `${BASE_URL}${normalizedPath.replace(/\/$/, "")}`;
}

export function createOrganizationSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE_NAME,
    url: BASE_URL,
    logo: `${BASE_URL}/favicon.png`,
  };
}

export function createWebSiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: SITE_NAME,
    url: BASE_URL,
    potentialAction: {
      "@type": "SearchAction",
      target: `${BASE_URL}/?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };
}

export function createServiceSchema({ name, description, path }) {
  return {
    "@context": "https://schema.org",
    "@type": "Service",
    name,
    description,
    provider: {
      "@type": "Organization",
      name: SITE_NAME,
      url: BASE_URL,
    },
    areaServed: "RU",
    serviceType: "SaaS",
    url: getCanonicalUrl(path),
  };
}

export function createFaqSchema(items = []) {
  const mainEntity = items
    .filter((item) => item?.question && item?.answer)
    .map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    }));

  if (!mainEntity.length) return null;

  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity,
  };
}

export const homepageSoftwareSchema = [createOrganizationSchema(), createWebSiteSchema()];

// Совместимость со старой vue-router версией маршрутизации.
export const seoState = ref({
  title: DEFAULT_TITLE,
  description: DEFAULT_DESCRIPTION,
  keywords: DEFAULT_KEYWORDS,
  canonical: `${BASE_URL}/`,
  ogTitle: DEFAULT_TITLE,
  ogDescription: DEFAULT_DESCRIPTION,
  ogUrl: `${BASE_URL}/`,
  ogType: "website",
  ogImage: DEFAULT_IMAGE,
  ogImageAlt: DEFAULT_OG_IMAGE_ALT,
  twitterCard: "summary_large_image",
  twitterTitle: DEFAULT_TITLE,
  twitterDescription: DEFAULT_DESCRIPTION,
  twitterImage: DEFAULT_IMAGE,
  twitterImageAlt: DEFAULT_TWITTER_IMAGE_ALT,
  robots: "index,follow",
  schema: [],
});

export function setSeoForRoute(route) {
  const meta = route?.meta ?? {};
  const title = meta.title || DEFAULT_TITLE;
  const description = meta.description || DEFAULT_DESCRIPTION;
  const keywords = meta.keywords || DEFAULT_KEYWORDS;
  const canonical = getCanonicalUrl(route?.path || "/");
  const noindex = Boolean(meta.noindex || meta?.seo?.noindex);

  seoState.value = {
    title,
    description,
    keywords,
    canonical,
    ogTitle: meta.ogTitle || title,
    ogDescription: meta.ogDescription || description,
    ogUrl: canonical,
    ogType: meta.ogType || "website",
    ogImage: meta.ogImage || DEFAULT_IMAGE,
    ogImageAlt: meta.ogImageAlt || DEFAULT_OG_IMAGE_ALT,
    twitterCard: meta.twitterCard || "summary_large_image",
    twitterTitle: meta.twitterTitle || title,
    twitterDescription: meta.twitterDescription || description,
    twitterImage: meta.twitterImage || DEFAULT_IMAGE,
    twitterImageAlt: meta.twitterImageAlt || DEFAULT_TWITTER_IMAGE_ALT,
    robots: noindex ? "noindex,nofollow" : "index,follow",
    schema: meta.schema || [],
  };
}

