import api from "./api";

export async function getSubscriptionStatus() {
  const response = await api.get("/api/subscription/status/");
  return response.data;
}

export async function getSubscriptionPlans() {
  const response = await api.get("/api/subscription/plans/");
  return Array.isArray(response.data) ? response.data : response.data?.results ?? [];
}

export async function createSubscriptionPayment(planId) {
  const response = await api.post("/api/subscription/create-payment/", { plan_id: planId });
  return response.data;
}

export async function redirectToYooKassaCheckout(planId = null) {
  let resolvedPlanId = planId;
  if (!resolvedPlanId) {
    const plans = await getSubscriptionPlans();
    if (!plans.length) {
      throw new Error("NO_ACTIVE_PLANS");
    }
    resolvedPlanId = Number(plans[0].id);
  }

  const paymentData = await createSubscriptionPayment(resolvedPlanId);
  const confirmationUrl = paymentData?.confirmation_url || paymentData?.checkout_url;
  if (!confirmationUrl) {
    throw new Error("NO_CONFIRMATION_URL");
  }

  window.location.href = confirmationUrl;
  return paymentData;
}
