import { ref } from "vue";
import api from "../services/api";

const devicesData = ref({
  devices: { mobile: 0, desktop: 0, tablet: 0 },
  browsers: {},
  os: {},
});
const loading = ref(false);
const error = ref("");

async function loadDevices(params = {}) {
  loading.value = true;
  error.value = "";
  try {
    const response = await api.get("/api/analytics/devices/", { params });
    devicesData.value = {
      devices: response.data?.devices || { mobile: 0, desktop: 0, tablet: 0 },
      browsers: response.data?.browsers || {},
      os: response.data?.os || {},
    };
  } catch (err) {
    error.value = "Ошибка загрузки аналитики устройств.";
  } finally {
    loading.value = false;
  }
}

export function useAnalyticsDevices() {
  return {
    devicesData,
    loading,
    error,
    loadDevices,
  };
}
