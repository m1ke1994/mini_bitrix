import { ref } from "vue";

const SITE_NAME = "TrackNode";
const BASE_URL = "https://tracknode.ru";
const DEFAULT_TITLE = "TrackNode — SaaS аналитика сайтов и воронка лидогенерации";
const DEFAULT_DESCRIPTION =
  "TrackNode — платформа аналитики сайтов для малого бизнеса. Отслеживание заявок, воронка лидов, отчёты и Telegram-уведомления в одном сервисе.";
const DEFAULT_KEYWORDS = "аналитика сайта, SaaS аналитика, TrackNode, воронка лидогенерации, отслеживание заявок";
const DEFAULT_IMAGE = `${BASE_URL}/og-preview.jpg`;

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
  twitterCard: "summary_large_image",
  robots: "index,follow",
  schema: null,
});

export function setSeoForRoute(route) {
  const meta = route?.meta ?? {};
  const title = meta.title || DEFAULT_TITLE;
  const description = meta.description || DEFAULT_DESCRIPTION;
  const keywords = meta.keywords || DEFAULT_KEYWORDS;
  const canonical = `${BASE_URL}${route?.path || "/"}`;
  const noindex = Boolean(meta.noindex);

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
    twitterCard: meta.twitterCard || "summary_large_image",
    robots: noindex ? "noindex,nofollow" : "index,follow",
    schema: meta.schema || null,
  };
}

export const homepageSoftwareSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: SITE_NAME,
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  url: BASE_URL,
  description: "SaaS аналитика сайтов и система отслеживания заявок",
  offers: [
    {
      "@type": "Offer",
      name: "Starter",
      price: "990",
      priceCurrency: "RUB",
      availability: "https://schema.org/InStock",
      url: `${BASE_URL}/tarify`,
    },
    {
      "@type": "Offer",
      name: "Growth",
      price: "2990",
      priceCurrency: "RUB",
      availability: "https://schema.org/InStock",
      url: `${BASE_URL}/tarify`,
    },
  ],
};
