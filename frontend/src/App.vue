<template>
  <router-view />
</template>

<script setup>
import { useHead } from "@vueuse/head";
import { seoState } from "./seo";

useHead(() => {
  const seo = seoState.value;
  const scripts = seo.schema
    ? [
        {
          type: "application/ld+json",
          children: JSON.stringify(seo.schema),
        },
      ]
    : [];

  const meta = [
    { name: "description", content: seo.description },
    { name: "keywords", content: seo.keywords },
    { name: "robots", content: seo.robots },
    { name: "application-name", content: "TrackNode" },
    { name: "apple-mobile-web-app-title", content: "TrackNode" },
    { property: "og:title", content: seo.ogTitle },
    { property: "og:description", content: seo.ogDescription },
    { property: "og:url", content: seo.ogUrl },
    { property: "og:type", content: seo.ogType },
    { property: "og:image", content: seo.ogImage },
    seo.ogImageAlt ? { property: "og:image:alt", content: seo.ogImageAlt } : null,
    { name: "twitter:card", content: seo.twitterCard },
    seo.twitterImageAlt ? { name: "twitter:image:alt", content: seo.twitterImageAlt } : null,
  ].filter(Boolean);

  return {
    title: seo.title,
    meta,
    link: [{ rel: "canonical", href: seo.canonical }],
    script: scripts,
  };
});
</script>
