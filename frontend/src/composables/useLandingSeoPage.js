import { BASE_URL, DEFAULT_IMAGE, SITE_NAME, getCanonicalUrl } from "~/seo";

function toAbsoluteImage(url = DEFAULT_IMAGE) {
  const value = String(url || DEFAULT_IMAGE);
  return value.startsWith("http") ? value : `${BASE_URL}${value}`;
}

function sanitizePathForKey(path = "/") {
  return String(path || "/").replace(/[^a-z0-9]/gi, "-");
}

export function useLandingSeoPage(options = {}) {
  const path = options.path || "/";
  const canonical = getCanonicalUrl(path);
  const title = options.title || SITE_NAME;
  const description = options.description || "";
  const keywords = options.keywords || "";
  const ogImage = toAbsoluteImage(options.ogImage || DEFAULT_IMAGE);
  const twitterImage = toAbsoluteImage(options.twitterImage || ogImage);
  const schema = Array.isArray(options.schema) ? options.schema.filter(Boolean) : [];
  const routeKey = sanitizePathForKey(path);
  const robots = options.robots || "index,follow";

  useSeoMeta({
    title,
    description,
    keywords,
    robots,
    ogTitle: options.ogTitle || title,
    ogDescription: options.ogDescription || description,
    ogType: options.ogType || "website",
    ogUrl: canonical,
    ogSiteName: SITE_NAME,
    ogImage,
    twitterCard: options.twitterCard || "summary_large_image",
    twitterTitle: options.twitterTitle || title,
    twitterDescription: options.twitterDescription || description,
    twitterImage,
  });

  useHead({
    link: [
      { key: `canonical-${routeKey}`, rel: "canonical", href: canonical },
    ],
    script: schema.map((entry, index) => ({
      key: `ld-${routeKey}-${index}`,
      type: "application/ld+json",
      children: JSON.stringify(entry),
    })),
  });

  return { canonical };
}
