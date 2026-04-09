import { getLandingBlogPosts, getLandingCases } from "./landing.js";

export const SITE_URL = "https://tracknode.ru";

export const PUBLIC_STATIC_SEO_PATHS = [
  "/",
  "/seo-audit",
  "/website-analytics",
  "/cases",
  "/pricing",
  "/blog",
  "/contacts",
  "/about",
  "/analitika",
  "/otchety",
  "/tarify",
  "/telegram",
];

export const PUBLIC_DYNAMIC_ROUTE_GLOBS = ["/cases/**", "/blog/**"];

export const PRIVATE_EXACT_PATHS = [
  "/auth",
  "/login",
  "/register",
  "/settings",
  "/account",
  "/integration",
  "/reports",
  "/instructions",
  "/app",
  "/dashboard",
];

export const PRIVATE_GLOB_PATHS = ["/app/**", "/dashboard/**"];

export const TECHNICAL_NOINDEX_PATHS = ["/robots.txt", "/sitemap.xml"];

export const AUTH_NOINDEX_PATHS = ["/auth", "/login", "/register", "/app/auth", "/app/login", "/app/register"];

export function getCaseDetailPaths() {
  return getLandingCases().map((item) => `/cases/${item.slug}`);
}

export function getBlogDetailPaths() {
  return getLandingBlogPosts().map((item) => `/blog/${item.slug}`);
}

export function getPublicSitemapPaths() {
  return [...new Set([...PUBLIC_STATIC_SEO_PATHS, ...getCaseDetailPaths(), ...getBlogDetailPaths()])];
}

export function getPublicPrerenderPaths() {
  return getPublicSitemapPaths();
}
