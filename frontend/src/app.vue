<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import {
  BASE_URL,
  DEFAULT_DESCRIPTION,
  DEFAULT_IMAGE,
  DEFAULT_KEYWORDS,
  DEFAULT_OG_IMAGE_ALT,
  DEFAULT_TITLE,
  DEFAULT_TWITTER_IMAGE_ALT,
  SITE_NAME,
  getCanonicalUrl,
} from "~/seo";

const route = useRoute();

function normalizeSchema(schema) {
  if (!schema) return [];
  if (Array.isArray(schema)) return schema.filter(Boolean);
  return [schema];
}

useHead(() => {
  const meta = route.meta || {};
  const seo = meta.seo || {};

  const title = seo.title || DEFAULT_TITLE;
  const description = seo.description || DEFAULT_DESCRIPTION;
  const keywords = seo.keywords || DEFAULT_KEYWORDS;
  const canonical = seo.canonical || getCanonicalUrl(route.path || "/");
  const noindex = Boolean(meta.noindex || seo.noindex);
  const robots = noindex ? "noindex,nofollow" : "index,follow";
  const schemaList = normalizeSchema(seo.schema);

  return {
    title,
    meta: [
      { name: "description", content: description },
      { name: "keywords", content: keywords },
      { name: "robots", content: robots },
      { name: "application-name", content: SITE_NAME },
      { name: "apple-mobile-web-app-title", content: SITE_NAME },
      { property: "og:title", content: seo.ogTitle || title },
      { property: "og:description", content: seo.ogDescription || description },
      { property: "og:url", content: seo.ogUrl || canonical },
      { property: "og:type", content: seo.ogType || "website" },
      { property: "og:site_name", content: SITE_NAME },
      { property: "og:image", content: seo.ogImage || DEFAULT_IMAGE },
      { property: "og:image:alt", content: seo.ogImageAlt || DEFAULT_OG_IMAGE_ALT },
      { name: "twitter:card", content: seo.twitterCard || "summary_large_image" },
      { name: "twitter:title", content: seo.twitterTitle || title },
      { name: "twitter:description", content: seo.twitterDescription || description },
      { name: "twitter:image", content: seo.twitterImage || DEFAULT_IMAGE },
      {
        name: "twitter:image:alt",
        content: seo.twitterImageAlt || DEFAULT_TWITTER_IMAGE_ALT,
      },
    ],
    link: [{ rel: "canonical", href: canonical }, { rel: "home", href: BASE_URL }],
    script: schemaList.map((entry, index) => ({
      key: `ld-json-${index}`,
      type: "application/ld+json",
      children: JSON.stringify(entry),
    })),
  };
});
</script>

