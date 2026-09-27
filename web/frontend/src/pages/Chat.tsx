/**
 * Main Chat page layout:
 *   ┌─────────────────────────────────────────┐
 *   │  ChatInterface       │  ParameterPanel  │
 *   │                      │  (right sidebar) │
 *   │  PVCurvePlot (bottom)│                  │
 *   └──────────────────────┴──────────────────┘
 *
 * On mobile the parameter panel slides in from the right.
 */
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ChatInterface from "../components/Chat/ChatInterface";
import ParameterPanel from "../components/Parameters/ParameterPanel";
import PVCurvePlot from "../components/Visualization/PVCurvePlot";
import { useAppStore } from "../store/appStore";

export default function ChatPage() {
  const { conversationId } = useParams<{ conversationId?: string }>();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const latestResult = useAppStore((s) => s.latestResult);
  const viewingPlotId = useAppStore((s) => s.viewingPlotId);
  const navigate = useNavigate();
  const setViewingPlotId = useAppStore((s) => s.setViewingPlotId);
  
  function closePlotView() {
    setViewingPlotId(null);
    navigate("/plots");
  }
  // Close drawer on Escape key (keyboard accessibility)
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key !== "Escape") return;
      if (viewingPlotId) closePlotView();
      else setSidebarOpen(false);
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [viewingPlotId]);

  // If URL has a conversation id, switch to it on mount
  // (handled by History page via store)
  void conversationId; // suppress unused warning; routing handled by parent

  return (
    <div className="flex flex-1 min-h-0">
      {/* ── Main area (left / center) ─────────────────────────────────────── */}
      <main className="flex-1 flex flex-col min-h-0 min-w-0">
        {/* Mobile toolbar */}
        <div className="md:hidden flex items-center justify-end px-3 py-2 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <button
            onClick={() => setSidebarOpen(true)}
            className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            aria-label="Open parameters"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <line x1="3" y1="6"  x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
            Parameters
          </button>
        </div>

        {/* Split: normal (chat top, plot bottom) OR viewing mode (plot top, chat bottom) */}
        <div className="flex-1 flex flex-col min-h-0">
          {viewingPlotId ? (
            // Plot viewing mode: plot above, chat below (50/50)
            <>
              <div className="flex-1 flex flex-col border-b border-gray-200 dark:border-gray-700 min-h-0">
                <div className="flex justify-end px-2 py-1">
                  <button
                    onClick={closePlotView}
                    className="text-xs px-2 py-1 rounded text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700"
                  >
                    Back
                  </button>
                </div>
                <div className="flex-1 min-h-0 overflow-y-auto">
                  <PVCurvePlot />
                </div>
              </div>
              <div className="flex-1 min-h-0 overflow-y-auto flex flex-col">
                <ChatInterface />
              </div>
            </>
          ) : (
            // Normal mode: chat flexible, plot when result available
            <>
              <div className={`flex flex-col min-h-0 ${latestResult ? "flex-[2]" : "flex-1"}`}>
                <ChatInterface />
              </div>
              {latestResult && (
                <div className="flex-1 border-t border-gray-200 dark:border-gray-700 min-h-0 overflow-y-auto">
                  <PVCurvePlot />
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* ── Mobile drawer backdrop ─────────────────────────────────────── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Mobile drawer (slides from right) ─────────────────────────── */}
      <aside className={`fixed inset-y-0 right-0 z-40 w-72 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 transition-transform duration-300 md:hidden ${
        sidebarOpen ? "translate-x-0" : "translate-x-full"
      }`}>
        <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-800">
          <span className="font-medium text-sm text-gray-800 dark:text-gray-200">Parameters</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Close parameters"
          >
            ✕
          </button>
        </div>
        <ParameterPanel className="flex-1" />
      </aside>

      {/* ── Desktop parameter sidebar (right) ─────────────────────────── */}
      <aside className="hidden md:flex flex-col w-64 lg:w-72 border-l border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex-shrink-0">
        <ParameterPanel className="flex-1" />
      </aside>
    </div>
  );
}
