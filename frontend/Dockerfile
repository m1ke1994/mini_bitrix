FROM node:20-alpine AS deps

WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org/
ENV NPM_CONFIG_FETCH_RETRIES=5
ENV NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000
ENV NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000
ENV NPM_CONFIG_NETWORK_TIMEOUT=300000

COPY . .

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
      npm ci --ignore-scripts --no-audit --no-fund; \
    else \
      echo "No lock file found: expected pnpm-lock.yaml, yarn.lock, or package-lock.json" >&2; \
      exit 1; \
    fi

FROM node:20-alpine AS build

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NODE_ENV=production

RUN set -eux; \
    if [ -f pnpm-lock.yaml ]; then \
      corepack enable; \
      corepack prepare pnpm@latest --activate; \
      pnpm run build; \
    elif [ -f yarn.lock ]; then \
      corepack enable; \
      yarn build; \
    else \
      npm run build; \
    fi

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=9003
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=9003

COPY --from=build /app/.output ./.output
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./package.json

EXPOSE 9003

CMD ["node", ".output/server/index.mjs"]
