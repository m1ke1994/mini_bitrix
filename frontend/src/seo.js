import { ref } from "vue";

const SITE_NAME = "TrackNode";
const BASE_URL = "https://tracknode.ru";
const DEFAULT_TITLE = "Аналитика сайтов и учет заявок — сервис отслеживания лидов | TrackNode";
const DEFAULT_DESCRIPTION =
  "Сервис аналитики сайтов и учета заявок. Отслеживайте лиды, конверсию и путь клиента. Аналитика воронки продаж и Telegram-уведомления в одном кабинете.";
const DEFAULT_KEYWORDS =
  "аналитика сайтов, сервис аналитики, учет заявок, аналитика воронки продаж, отслеживание конверсии, TrackNode";
const DEFAULT_IMAGE = `${BASE_URL}/og-preview.jpg`;
const DEFAULT_OG_IMAGE_ALT = "аналитика сайтов интерфейс";
const DEFAULT_TWITTER_IMAGE_ALT = "учет заявок дашборд";

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
  twitterImageAlt: DEFAULT_TWITTER_IMAGE_ALT,
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
    ogImageAlt: meta.ogImageAlt || DEFAULT_OG_IMAGE_ALT,
    twitterCard: meta.twitterCard || "summary_large_image",
    twitterImageAlt: meta.twitterImageAlt || DEFAULT_TWITTER_IMAGE_ALT,
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
  description:
    "Сервис аналитики сайтов и учета заявок для отслеживания лидов, конверсии и пути клиента в одном кабинете.",
  image: {
    "@type": "ImageObject",
    url: DEFAULT_IMAGE,
    description: "аналитика воронки продаж",
  },
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
