FROM node:20-alpine AS deps
WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org/
ENV NPM_CONFIG_FETCH_RETRIES=5
ENV NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000
ENV NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000
ENV NPM_CONFIG_NETWORK_TIMEOUT=300000

# Nuxt-проект находится в ./frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm config set registry ${NPM_REGISTRY} && npm ci --ignore-scripts --no-audit --no-fund


FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./

ENV NODE_ENV=production

RUN set -eux; \
  chmod +x node_modules/.bin/nuxt || true; \
  chmod +x node_modules/nuxt/bin/nuxt.mjs || true; \
  node ./node_modules/nuxt/bin/nuxt.mjs prepare; \
  node ./node_modules/nuxt/bin/nuxt.mjs build


FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=9003
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=9003

COPY --from=builder /app/.output ./.output

EXPOSE 9003
CMD ["node", ".output/server/index.mjs"]