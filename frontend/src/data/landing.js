import { landingData } from "../../public/landing_mock/landing.js";

export function getLandingData() {
  return landingData;
}

export function getLandingSeoPages() {
  return landingData.seoPages || {};
}

export function getLandingCases() {
  return getLandingSeoPages().cases?.items || [];
}

export function getLandingCaseBySlug(slug = "") {
  const normalizedSlug = String(slug || "").trim();
  return getLandingCases().find((item) => item.slug === normalizedSlug) || null;
}

export function getLandingBlogPosts() {
  return [...(getLandingSeoPages().blog?.posts || [])].sort((a, b) =>
    String(b.date || "").localeCompare(String(a.date || "")),
  );
}

export function getLandingBlogPostBySlug(slug = "") {
  const normalizedSlug = String(slug || "").trim();
  return getLandingBlogPosts().find((item) => item.slug === normalizedSlug) || null;
}
