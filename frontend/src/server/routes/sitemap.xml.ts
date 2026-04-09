import { SITE_URL, getPublicSitemapPaths } from "~/data/seo-routes";

const PUBLIC_PATHS = getPublicSitemapPaths();

export default defineEventHandler(() => {
  const lastmod = new Date().toISOString().split("T")[0];
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${PUBLIC_PATHS.map((path) => {
    const url = path === "/" ? `${SITE_URL}/` : `${SITE_URL}${path}`;
    const priority = path === "/" ? "1.0" : path.includes("/blog/") || path.includes("/cases/") ? "0.7" : "0.8";
    return `  <url>
    <loc>${url}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>${priority}</priority>
  </url>`;
  }).join("\n")}
</urlset>`;

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=900, stale-while-revalidate=3600",
      "X-Robots-Tag": "noindex,nofollow",
    },
  });
});
