import { createApp } from "vue";
import { createPinia } from "pinia";
import { createHead } from "@vueuse/head";
import { registerSW } from "virtual:pwa-register";
import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "./stores/auth";
import "./style.css";

const app = createApp(App);
const pinia = createPinia();
const head = createHead();
async function bootstrap() {
  app.use(pinia);

  const auth = useAuthStore(pinia);
  await auth.initializeAuth();
  auth.bindStorageSync();

  app.use(head);
  app.use(router);
  app.mount("#app");
}

void bootstrap();

if (import.meta.env.PROD) {
  window.addEventListener(
    "load",
    () => {
      registerSW();
    },
    { once: true }
  );
}
