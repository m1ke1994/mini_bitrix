<template>
  <PublicHomePage />
</template>

<script setup>
import PublicHomePage from "~/views/PublicHomePage.vue";
import { getLandingData } from "~/data/landing";
import { BASE_URL, SITE_NAME } from "~/seo";

const landing = getLandingData();
const canonical = `${BASE_URL}/`;
const seo = landing.seo || {};
const title = seo.title || SITE_NAME;
const description = seo.description || "";
const keywords = seo.keywords || "";
const ogImage = String(seo.ogImage || "/og-preview.jpg").startsWith("http")
  ? seo.ogImage
  : `${BASE_URL}${seo.ogImage || "/og-preview.jpg"}`;

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: landing.homepage?.brand?.name || SITE_NAME,
  url: BASE_URL,
  logo: `${BASE_URL}${landing.homepage?.brand?.logoSrc || "/favicon.png"}`,
};

const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: landing.homepage?.brand?.name || SITE_NAME,
  url: BASE_URL,
};

const softwareSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: landing.homepage?.brand?.name || SITE_NAME,
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  description,
  url: canonical,
};

definePageMeta({
  publicPage: true,
  disableGlobalSeo: true,
});

useSeoMeta({
  title,
  description,
  keywords,
  robots: "index,follow",
  ogTitle: title,
  ogDescription: description,
  ogType: "website",
  ogUrl: canonical,
  ogSiteName: landing.homepage?.brand?.name || SITE_NAME,
  ogImage,
  twitterCard: seo.twitterCard || "summary_large_image",
  twitterTitle: title,
  twitterDescription: description,
  twitterImage: ogImage,
});

useHead({
  link: [
    { rel: "canonical", href: canonical },
    { rel: "stylesheet", href: "/landing_mock/css/main.css" },
  ],
  script: [
    {
      key: "ld-org",
      type: "application/ld+json",
      children: JSON.stringify(organizationSchema),
    },
    {
      key: "ld-website",
      type: "application/ld+json",
      children: JSON.stringify(websiteSchema),
    },
    {
      key: "ld-software",
      type: "application/ld+json",
      children: JSON.stringify(softwareSchema),
    },
  ],
});
</script>
