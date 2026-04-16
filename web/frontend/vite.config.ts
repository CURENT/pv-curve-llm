import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      // REST API calls → FastAPI backend
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      // WebSocket connections → FastAPI backend
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
        changeOrigin: true,
      },
      // Plot images served from backend
      "/plots": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
