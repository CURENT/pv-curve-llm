import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "../store/appStore";
import { listPlots, getConversation } from "../services/api";
import ParameterPanel from "../components/Parameters/ParameterPanel";
import type { PlotSummary } from "../types";

export default function PlotsPage() {
  const sessionId = useAppStore((s) => s.sessionId);
  const setConversationId = useAppStore((s) => s.setConversationId);
  const setMessages = useAppStore((s) => s.setMessages);
  const navigate = useNavigate();

  const [plots, setPlots] = useState<PlotSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selected, setSelected] = useState<PlotSummary | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    listPlots(sessionId)
      .then(setPlots)
      .catch(() => setPlots([]))
      .finally(() => setLoading(false));
  }, [sessionId]);

  // Esc closes the image first. If no image is open, it closes the mobile drawer.
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key !== "Escape") return;
      if (selected) setSelected(null);
      else setSidebarOpen(false);
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [selected]);

  async function openSourceChat(plot: PlotSummary) {
    const detail = await getConversation(plot.conversation_id);
    setConversationId(plot.conversation_id);
    setMessages(
      detail.messages.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
        timestamp: m.timestamp ?? undefined,
      }))
    );
    navigate("/chat");
  }

  return (
    <div className="flex flex-1 min-h-0">
      <main className="flex-1 flex flex-col min-h-0 min-w-0 overflow-y-auto">
        <div className="p-6 space-y-4">
          <h1 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
            Plots
          </h1>

          {loading && <p className="text-sm text-gray-400">Loading…</p>}

          {!loading && plots.length === 0 && (
            <p className="text-sm text-gray-400 dark:text-gray-500">
              No plots yet. Generate one in a chat to see them here.
            </p>
          )}

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {plots.map((plot) => (
              <PlotTile key={plot.id} plot={plot} onOpen={setSelected} />
            ))}
          </div>
        </div>
      </main>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside
        className={`fixed inset-y-0 right-0 z-40 w-72 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 transition-transform duration-300 md:hidden ${
          sidebarOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <ParameterPanel className="flex-1" />
      </aside>

      <aside className="hidden md:flex flex-col w-64 lg:w-72 border-l border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex-shrink-0">
        <ParameterPanel className="flex-1" />
      </aside>

      {selected && (
        <PlotViewer
          plot={selected}
          onClose={() => setSelected(null)}
          onOpenChat={() => openSourceChat(selected)}
        />
      )}
    </div>
  );
}

function PlotTile({
  plot,
  onOpen,
}: {
  plot: PlotSummary;
  onOpen: (plot: PlotSummary) => void;
}) {
  const label = formatLabel(plot);

  return (
    <button
      onClick={() => onOpen(plot)}
      className="group flex flex-col gap-2 text-left focus:outline-none"
    >
      <div className="relative aspect-square rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 group-hover:border-indigo-400 transition-colors">
        {plot.plot_path ? (
          <img src={plot.plot_path} alt={label} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No image
          </div>
        )}
      </div>
      <p className="text-xs text-gray-600 dark:text-gray-400 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
        {label}
      </p>
    </button>
  );
}

function PlotViewer({
  plot,
  onClose,
  onOpenChat,
}: {
  plot: PlotSummary;
  onClose: () => void;
  onOpenChat: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 bg-black/90">
      <button
        onClick={onClose}
        title="Back to grid (Esc)"
        className="absolute top-4 left-4 p-2 text-white hover:bg-white/10 rounded-lg"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path d="M19 12H5" />
          <path d="M12 19l-7-7 7-7" />
        </svg>
      </button>
  
      <div className="h-full flex flex-col items-center justify-center">
        {plot.plot_path ? (
          <img
            src={plot.plot_path}
            alt={formatLabel(plot)}
            className="max-h-[80vh] max-w-[90vw] object-contain"
          />
        ) : (
          <p className="text-gray-400">No image</p>
        )}
  
        <div className="mt-6 flex items-center gap-1 rounded-full bg-neutral-800 px-2 py-2">
          <button
            onClick={onOpenChat}
            title="Open the chat that created this plot"
            className="p-2 rounded-full text-white hover:bg-white/10"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

function formatLabel(plot: PlotSummary) {
  const grid = plot.grid.replace("ieee", "IEEE ");
  const date = plot.create_at
    ? new Date(plot.create_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : "";
  return `${grid} · Bus ${plot.bus_id} · ${date}`;
}