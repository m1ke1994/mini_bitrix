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

  return {
    title: seo.title,
    meta: [
      { name: "description", content: seo.description },
      { name: "keywords", content: seo.keywords },
      { name: "robots", content: seo.robots },
      { property: "og:title", content: seo.ogTitle },
      { property: "og:description", content: seo.ogDescription },
      { property: "og:url", content: seo.ogUrl },
      { property: "og:type", content: seo.ogType },
      { property: "og:image", content: seo.ogImage },
      { name: "twitter:card", content: seo.twitterCard },
    ],
    link: [{ rel: "canonical", href: seo.canonical }],
    script: scripts,
  };
});
</script>
