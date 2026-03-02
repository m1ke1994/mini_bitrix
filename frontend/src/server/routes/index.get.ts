import { createReadStream, existsSync } from "node:fs";
import { resolve } from "node:path";
import { createError, defineEventHandler, sendStream, setHeader } from "h3";

const LANDING_INDEX_FILE = resolve(process.cwd(), "landing_dist", "index.html");

export default defineEventHandler((event) => {
  if (!existsSync(LANDING_INDEX_FILE)) {
    throw createError({
      statusCode: 503,
      statusMessage: "Landing build is missing. Run `npm --prefix ../nuxt run generate`.",
    });
  }

  setHeader(event, "Content-Type", "text/html; charset=utf-8");
  setHeader(event, "Cache-Control", "public, max-age=60");
  return sendStream(event, createReadStream(LANDING_INDEX_FILE));
});
