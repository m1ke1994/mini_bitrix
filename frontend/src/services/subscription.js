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
