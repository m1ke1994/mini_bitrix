export const AUTH_STORAGE_KEYS = {
  accessToken: "accessToken",
  refreshToken: "refreshToken",
  userEmail: "userEmail",
  clientId: "clientId",
};

export const AUTH_STORAGE_KEY_LIST = Object.values(AUTH_STORAGE_KEYS);

const BEARER_PREFIX_PATTERN = /^Bearer\s+/i;

function canUseWebStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function readStorageValue(key) {
  if (!canUseWebStorage()) return "";

  try {
    return String(window.localStorage.getItem(key) || "");
  } catch {
    return "";
  }
}

function writeStorageValue(key, value) {
  if (!canUseWebStorage()) return;

  const normalizedValue = value ? String(value) : "";

  try {
    if (normalizedValue) {
      window.localStorage.setItem(key, normalizedValue);
    } else {
      window.localStorage.removeItem(key);
    }
  } catch {
    // Ignore storage write errors.
  }
}

export function normalizeToken(token) {
  const normalizedToken = String(token || "").trim();
  if (!normalizedToken) return "";
  return normalizedToken.replace(BEARER_PREFIX_PATTERN, "").trim();
}

export function buildAuthorizationHeader(token) {
  const normalizedToken = normalizeToken(token);
  return normalizedToken ? `Bearer ${normalizedToken}` : "";
}

export function maskToken(token) {
  const normalizedToken = normalizeToken(token);
  if (!normalizedToken) return "empty";
  if (normalizedToken.length <= 12) {
    return `${normalizedToken.slice(0, 3)}...${normalizedToken.slice(-3)}`;
  }
  return `${normalizedToken.slice(0, 6)}...${normalizedToken.slice(-6)}`;
}

export function debugAuth(message, details = undefined) {
  if (!import.meta.dev || typeof console === "undefined") return;
  if (typeof details === "undefined") {
    console.debug(`[auth] ${message}`);
    return;
  }
  console.debug(`[auth] ${message}`, details);
}

export function getAccessToken() {
  return normalizeToken(readStorageValue(AUTH_STORAGE_KEYS.accessToken));
}

export function setAccessToken(token) {
  const normalizedToken = normalizeToken(token);
  writeStorageValue(AUTH_STORAGE_KEYS.accessToken, normalizedToken);
  debugAuth("access token updated", { token: maskToken(normalizedToken) });
}

export function getRefreshToken() {
  return normalizeToken(readStorageValue(AUTH_STORAGE_KEYS.refreshToken));
}

export function setRefreshToken(token) {
  const normalizedToken = normalizeToken(token);
  writeStorageValue(AUTH_STORAGE_KEYS.refreshToken, normalizedToken);
  debugAuth("refresh token updated", { token: maskToken(normalizedToken) });
}

export function getUserEmail() {
  return String(readStorageValue(AUTH_STORAGE_KEYS.userEmail) || "").trim();
}

export function setUserEmail(email) {
  writeStorageValue(AUTH_STORAGE_KEYS.userEmail, email ? String(email) : "");
}

export function getClientId() {
  return String(readStorageValue(AUTH_STORAGE_KEYS.clientId) || "").trim();
}

export function setClientId(clientId) {
  writeStorageValue(AUTH_STORAGE_KEYS.clientId, clientId ? String(clientId) : "");
}

export function readAuthStorage() {
  return {
    accessToken: getAccessToken(),
    refreshToken: getRefreshToken(),
    userEmail: getUserEmail(),
    clientId: getClientId(),
  };
}

export function writeAuthStorage({ accessToken = "", refreshToken = "", userEmail = "", clientId = "" } = {}) {
  setAccessToken(accessToken);
  setRefreshToken(refreshToken);
  setUserEmail(userEmail);
  setClientId(clientId);
}

export function clearTokens() {
  setAccessToken("");
  setRefreshToken("");
}

export function clearAuthStorage() {
  clearTokens();
  setUserEmail("");
  setClientId("");
  debugAuth("all auth storage cleared");
}
