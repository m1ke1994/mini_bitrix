const INVALID_TOKEN_VALUES = new Set(["", "null", "undefined", "nan"]);

export function normalizeToken(value) {
  const normalized = String(value ?? "").trim();
  if (INVALID_TOKEN_VALUES.has(normalized.toLowerCase())) {
    return "";
  }
  return normalized;
}

export function hasToken(value) {
  return Boolean(normalizeToken(value));
}
