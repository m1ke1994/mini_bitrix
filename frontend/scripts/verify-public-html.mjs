import { spawn } from "node:child_process";
import http from "node:http";
import { getLandingBlogPosts, getLandingCases } from "../src/data/landing.js";

const PORT = Number(process.env.NITRO_PORT || 3903);
const HOST = process.env.NITRO_HOST || "127.0.0.1";
const BASE_URL = `http://${HOST}:${PORT}`;
const SITE_URL = "https://tracknode.ru";

const BASE_PUBLIC_SEO_ROUTES = ["/", "/seo-audit", "/website-analytics", "/cases", "/pricing", "/blog", "/contacts"];
const CASE_DETAIL_ROUTES = getLandingCases().map((item) => `/cases/${item.slug}`);
const BLOG_DETAIL_ROUTES = getLandingBlogPosts().map((item) => `/blog/${item.slug}`);
const ROUTES_TO_CHECK = [...new Set([...BASE_PUBLIC_SEO_ROUTES, ...CASE_DETAIL_ROUTES, ...BLOG_DETAIL_ROUTES])];

function toCanonical(path) {
  return path === "/" ? `${SITE_URL}/` : `${SITE_URL}${path}`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function fetchHtml(pathname) {
  const url = `${BASE_URL}${pathname}`;
  return new Promise((resolve, reject) => {
    http
      .get(url, (response) => {
        const chunks = [];
        response.on("data", (chunk) => chunks.push(chunk));
        response.on("end", () => {
          const body = Buffer.concat(chunks).toString("utf8");
          resolve({ status: response.statusCode || 0, body });
        });
      })
      .on("error", reject);
  });
}

async function waitForServer(maxAttempts = 25) {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const response = await fetchHtml("/");
      if (response.status >= 200 && response.status < 500) return;
    } catch {
      // keep waiting
    }
    await sleep(300);
  }
  throw new Error("Nuxt server did not start in time.");
}

async function run() {
  const child = spawn(process.execPath, [".output/server/index.mjs"], {
    env: {
      ...process.env,
      NITRO_HOST: HOST,
      NITRO_PORT: String(PORT),
      HOST,
      PORT: String(PORT),
    },
    stdio: ["ignore", "pipe", "pipe"],
  });

  const childLogs = [];
  child.stdout.on("data", (chunk) => childLogs.push(String(chunk)));
  child.stderr.on("data", (chunk) => childLogs.push(String(chunk)));

  try {
    await waitForServer();

    const errors = [];
    for (const path of ROUTES_TO_CHECK) {
      const { status, body } = await fetchHtml(path);
      if (status !== 200) {
        errors.push(`${path}: HTTP ${status}`);
        continue;
      }

      const normalizedBody = body.toLowerCase();
      const markers = ["<h1", "<main", `rel=\"canonical\" href=\"${toCanonical(path)}\"`];
      for (const marker of markers) {
        if (!normalizedBody.includes(String(marker).toLowerCase())) {
          errors.push(`${path}: missing marker \"${marker}\"`);
        }
      }
    }

    if (errors.length) {
      console.error("SSR HTML verification failed:");
      for (const err of errors) console.error(`- ${err}`);
      if (childLogs.length) {
        console.error("Server logs:");
        console.error(childLogs.join(""));
      }
      process.exitCode = 1;
      return;
    }

    console.log(`SSR HTML verification passed for ${ROUTES_TO_CHECK.length} public SEO pages.`);
  } finally {
    child.kill("SIGTERM");
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
