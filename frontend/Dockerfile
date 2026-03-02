FROM node:20-alpine AS deps

WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org/
ENV NPM_CONFIG_FETCH_RETRIES=5
ENV NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000
ENV NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000
ENV NPM_CONFIG_NETWORK_TIMEOUT=300000

COPY frontend/package.json frontend/package-lock.json ./
RUN npm config set registry ${NPM_REGISTRY} && npm ci --ignore-scripts --no-audit --no-fund

FROM node:20-alpine AS landing_deps

WORKDIR /landing

ARG NPM_REGISTRY=https://registry.npmjs.org/
ENV NPM_CONFIG_FETCH_RETRIES=5
ENV NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000
ENV NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000
ENV NPM_CONFIG_NETWORK_TIMEOUT=300000

COPY nuxt/package.json nuxt/package-lock.json ./
RUN npm config set registry ${NPM_REGISTRY} && npm ci --ignore-scripts --no-audit --no-fund

FROM node:20-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./
ENV NODE_ENV=production
RUN set -eux; \
    ls -la node_modules/.bin | head -n 50 || true; \
    ls -la node_modules/.bin/nuxt || true; \
    stat node_modules/.bin/nuxt || true; \
    chmod +x node_modules/.bin/nuxt || true; \
    chmod +x node_modules/nuxt/bin/nuxt.mjs || true; \
    node ./node_modules/nuxt/bin/nuxt.mjs prepare; \
    node ./node_modules/nuxt/bin/nuxt.mjs build

FROM node:20-alpine AS landing_builder

WORKDIR /landing
COPY --from=landing_deps /landing/node_modules ./node_modules

COPY nuxt/app.vue ./app.vue
COPY nuxt/nuxt.config.ts ./nuxt.config.ts
COPY nuxt/tailwind.config.cjs ./tailwind.config.cjs
COPY nuxt/package.json ./package.json
COPY nuxt/package-lock.json ./package-lock.json
COPY nuxt/assets ./assets
COPY nuxt/components ./components
COPY nuxt/data ./data
COPY nuxt/layouts ./layouts
COPY nuxt/pages ./pages
COPY nuxt/plugins ./plugins
COPY nuxt/public ./public
COPY nuxt/utils ./utils

ENV NODE_ENV=production
RUN set -eux; \
    node ./node_modules/nuxt/bin/nuxt.mjs prepare; \
    node ./node_modules/nuxt/bin/nuxt.mjs generate; \
    test -f /frontend/landing_dist/index.html

FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=9003
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=9003
COPY --from=builder /app/.output ./.output
COPY --from=landing_builder /frontend/landing_dist ./landing_dist
EXPOSE 9003
CMD ["node", ".output/server/index.mjs"]
