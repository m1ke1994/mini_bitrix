import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
<<<<<<< HEAD
    host: true,               // важно
    port: 9003,
    allowedHosts: ["tracknode.ru", "www.tracknode.ru"],
=======
    host: true,              // важно
    port: 9003,
    allowedHosts: ["tracknode.ru"],
>>>>>>> 156e2de17d2910ddb3f4c000492b8c6fe37b7f6d
  },
});
