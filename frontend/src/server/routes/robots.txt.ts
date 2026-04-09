import { PRIVATE_EXACT_PATHS, PRIVATE_GLOB_PATHS, SITE_URL } from "~/data/seo-routes";

function getDisallowPaths() {
  const disallow = new Set();

  for (const path of PRIVATE_EXACT_PATHS) {
    disallow.add(path);
    if (path !== "/" && !path.endsWith("/")) {
      disallow.add(`${path}/`);
    }
  }

  for (const path of PRIVATE_GLOB_PATHS) {
    disallow.add(path.replace(/\/\*\*$/, "/*"));
  }

  return [...disallow];
}

export default defineEventHandler(() => {
  const disallowLines = getDisallowPaths().map((path) => `Disallow: ${path}`);
  const body = [
    "User-agent: *",
    "Allow: /",
    ...disallowLines,
    "",
    `Sitemap: ${SITE_URL}/sitemap.xml`,
  ].join("\n");

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      "X-Robots-Tag": "noindex,nofollow",
    },
  });
});
