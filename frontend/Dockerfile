FROM node:20-alpine

WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org/
ENV NPM_CONFIG_FETCH_RETRIES=5
ENV NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000
ENV NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000
ENV NPM_CONFIG_NETWORK_TIMEOUT=300000

COPY frontend/package.json /app/package.json
RUN npm config set registry ${NPM_REGISTRY} && npm install --no-audit --no-fund --verbose

COPY frontend /app

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "9003"]
