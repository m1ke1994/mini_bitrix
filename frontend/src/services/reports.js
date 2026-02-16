import api from "./api";

export async function getDailyPdfStatus() {
  const response = await api.get("/api/reports/toggle-daily/");
  return response.data;
}

export async function sendPdfNow() {
  const response = await api.post("/api/reports/send-now/");
  return response.data;
}

export async function toggleDailyPdf(enabled) {
  const response = await api.post("/api/reports/toggle-daily/", { enabled });
  return response.data;
}
