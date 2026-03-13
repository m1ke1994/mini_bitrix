# syntax=docker/dockerfile:1

############################
# 1) deps — install deps
############################
FROM node:20-alpine AS deps

WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org/
ENV NPM_CONFIG_FETCH_RETRIES=5 \
    NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000 \
    NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000 \
    NPM_CONFIG_NETWORK_TIMEOUT=300000

# Сначала копируем только манифесты/локи — для кеша
COPY package.json ./
COPY package-lock.json* ./
COPY pnpm-lock.yaml* ./
COPY yarn.lock* ./

RUN set -eux; \
    npm config set registry "${NPM_REGISTRY}"; \
    if [ -f pnpm-lock.yaml ]; then \
      corepack enable; \
      corepack prepare pnpm@latest --activate; \
      pnpm install --frozen-lockfile; \
    elif [ -f yarn.lock ]; then \
      corepack enable; \
      yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then \
      npm ci --no-audit --no-fund; \
    else \
      echo "No lock file found: expected pnpm-lock.yaml, yarn.lock, or package-lock.json" >&2; \
      exit 1; \
    fi

############################
# 2) build — build Nuxt
############################
FROM node:20-alpine AS build

WORKDIR /app
ENV NODE_ENV=production

# Забираем node_modules из deps
COPY --from=deps /app/node_modules ./node_modules

# Теперь копируем исходники
COPY . .

# На всякий случай чинит права на .bin (иногда в Alpine они странно приезжают)
# И главное — запускаем сборку через node по nuxi/nuxt, без вызова "nuxt" бинаря
RUN set -eux; \
    chmod -R a+x node_modules/.bin || true; \
    if [ -f ./node_modules/nuxi/bin/nuxi.mjs ]; then \
      node ./node_modules/nuxi/bin/nuxi.mjs build; \
    elif [ -f ./node_modules/nuxt/bin/nuxt.mjs ]; then \
      node ./node_modules/nuxt/bin/nuxt.mjs build; \
    else \
      echo "Cannot find nuxi/nuxt binary in node_modules" >&2; \
      ls -la node_modules || true; \
      ls -la node_modules/.bin || true; \
      exit 1; \
    fi

############################
# 3) runner — production runtime
############################
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=9003 \
    NITRO_HOST=0.0.0.0 \
    NITRO_PORT=9003

# (опционально, но полезно) запуск не под root
RUN addgroup -S nodejs && adduser -S nuxt -G nodejs

# Копируем только то, что нужно для запуска
COPY --from=build /app/.output ./.output
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./package.json

EXPOSE 9003

USER nuxt

CMD ["node", ".output/server/index.mjs"]