import api from "./api";

export async function getReportSettings() {
  const response = await api.get("/api/reports/settings/");
  console.log("[reports] /api/reports/settings response", response.data);
  return response.data;
}

export async function updateReportSettings(payload) {
  const response = await api.patch("/api/reports/settings/", payload);
  console.log("[reports] /api/reports/settings update response", response.data);
  return response.data;
}

export async function getLatestReportLog() {
  const response = await api.get("/api/reports/logs/latest/");
  console.log("[reports] /api/reports/logs/latest response", response.data);
  return response.data;
}

export async function startTelegramConnect() {
  const response = await api.post("/api/reports/telegram/connect/");
  console.log("[reports] /api/reports/telegram/connect response", response.data);
  return response.data;
}

export async function disconnectTelegram() {
  const response = await api.post("/api/reports/telegram/disconnect/");
  console.log("[reports] /api/reports/telegram/disconnect response", response.data);
  return response.data;
}

export async function generateReportNow(payload) {
  const response = await api.post("/api/reports/generate/", payload, {
    responseType: "blob",
  });
  console.log("[reports] /api/reports/generate headers", response.headers);
  return response;
}
