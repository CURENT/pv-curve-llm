import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAppStore } from "./store/appStore";
import { wsService } from "./services/websocket";
import HistorySidebar from "./components/Common/HistorySidebar";
import ChatPage from "./pages/Chat";
import SettingsPage from "./pages/Settings";

export default function App() {
  const isDark = useAppStore((s) => s.isDark);

  // Apply / remove "dark" class on <html> whenever the store changes
  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  // Open WebSocket once on startup
  useEffect(() => {
    wsService.connect();
    return () => wsService.disconnect();
  }, []);

  return (
    <BrowserRouter>
      {/* Horizontal root: sidebar on the left, page content on the right */}
      <div className="flex h-screen overflow-hidden">
        <HistorySidebar />

        <div className="flex-1 flex min-h-0 overflow-hidden">
          <Routes>
            <Route path="/"                     element={<Navigate to="/chat" replace />} />
            <Route path="/chat"                 element={<ChatPage />} />
            <Route path="/chat/:conversationId" element={<ChatPage />} />
            <Route path="/history"              element={<Navigate to="/chat" replace />} />
            <Route path="/settings"             element={<SettingsPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
