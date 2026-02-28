const SITE_URL = "https://tracknode.ru";

export default defineEventHandler(() => {
  const body = [
    "User-agent: *",
    "Allow: /",
    "Disallow: /dashboard",
    "Disallow: /dashboard/",
    "Disallow: /dashboard/*",
    "",
    `Sitemap: ${SITE_URL}/sitemap.xml`,
  ].join("\n");

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
    },
  });
});
