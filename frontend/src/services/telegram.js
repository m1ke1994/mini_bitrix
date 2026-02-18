import { getSubscriptionStatus } from "./subscription";

export const TELEGRAM_BOT_USERNAME = "TrackNode_bot";
export const TELEGRAM_ADMIN_URL = "https://t.me/M1ke994";

export function buildTelegramPaymentUrl(clientId) {
  return `https://t.me/${TELEGRAM_BOT_USERNAME}?start=pay_${clientId}`;
}

export async function redirectToTelegramPayment() {
  const statusResponse = await getSubscriptionStatus();
  const apiClientId = statusResponse?.client_id;
  if (!apiClientId) {
    throw new Error("PAYMENT_CLIENT_ID_MISSING");
  }

  const normalizedClientId = Number(apiClientId);
  window.location.href = buildTelegramPaymentUrl(normalizedClientId);
  return normalizedClientId;
}
