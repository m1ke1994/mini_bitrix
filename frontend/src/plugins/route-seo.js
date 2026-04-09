import {
  DEFAULT_DESCRIPTION,
  DEFAULT_IMAGE,
  DEFAULT_KEYWORDS,
  DEFAULT_OG_IMAGE_ALT,
  DEFAULT_TITLE,
  DEFAULT_TWITTER_IMAGE_ALT,
  SITE_NAME,
  BASE_URL,
  getCanonicalUrl,
} from "~/seo";

function toAbsoluteImage(url = DEFAULT_IMAGE) {
  const value = String(url || DEFAULT_IMAGE);
  return value.startsWith("http") ? value : `${BASE_URL}${value}`;
}

function toSeoMeta(meta) {
  if (meta && typeof meta === "object") {
    return meta;
  }
  return {};
}

export default defineNuxtPlugin(() => {
  const route = useRoute();

  useHead(() => {
    if (route.meta?.disableGlobalSeo) {
      return {};
    }

    const seo = toSeoMeta(route.meta?.seo);
    const title = seo.title || DEFAULT_TITLE;
    const description = seo.description || DEFAULT_DESCRIPTION;
    const keywords = seo.keywords || DEFAULT_KEYWORDS;
    const canonical = seo.canonical || getCanonicalUrl(route.path || "/");
    const noindex = Boolean(route.meta?.noindex || seo.noindex);
    const robots = noindex ? "noindex,nofollow" : "index,follow";
    const ogImage = toAbsoluteImage(seo.ogImage || DEFAULT_IMAGE);
    const twitterImage = toAbsoluteImage(seo.twitterImage || ogImage);
    const schema = Array.isArray(seo.schema) ? seo.schema.filter(Boolean) : [];

    return {
      title,
      meta: [
        { key: "route-seo-description", name: "description", content: description },
        { key: "route-seo-keywords", name: "keywords", content: keywords },
        { key: "route-seo-robots", name: "robots", content: robots },
        { key: "route-seo-og-title", property: "og:title", content: seo.ogTitle || title },
        { key: "route-seo-og-description", property: "og:description", content: seo.ogDescription || description },
        { key: "route-seo-og-type", property: "og:type", content: seo.ogType || "website" },
        { key: "route-seo-og-url", property: "og:url", content: canonical },
        { key: "route-seo-og-site-name", property: "og:site_name", content: SITE_NAME },
        { key: "route-seo-og-image", property: "og:image", content: ogImage },
        { key: "route-seo-og-image-alt", property: "og:image:alt", content: seo.ogImageAlt || DEFAULT_OG_IMAGE_ALT },
        { key: "route-seo-twitter-card", name: "twitter:card", content: seo.twitterCard || "summary_large_image" },
        { key: "route-seo-twitter-title", name: "twitter:title", content: seo.twitterTitle || title },
        { key: "route-seo-twitter-description", name: "twitter:description", content: seo.twitterDescription || description },
        { key: "route-seo-twitter-image", name: "twitter:image", content: twitterImage },
        { key: "route-seo-twitter-image-alt", name: "twitter:image:alt", content: seo.twitterImageAlt || DEFAULT_TWITTER_IMAGE_ALT },
      ],
      link: [{ key: "route-seo-canonical", rel: "canonical", href: canonical }],
      script: schema.map((entry, index) => ({
        key: `route-seo-schema-${index}`,
        type: "application/ld+json",
        children: JSON.stringify(entry),
      })),
    };
  });
});
