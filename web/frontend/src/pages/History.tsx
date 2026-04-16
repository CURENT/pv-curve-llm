import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "../store/appStore";
import {
  listConversations,
  deleteConversation,
  getConversation,
} from "../services/api";
import type { ConversationSummary } from "../types";
import Loading from "../components/Common/Loading";
import Modal from "../components/Common/Modal";

export default function HistoryPage() {
  const sessionId = useAppStore((s) => s.sessionId);
  const conversations = useAppStore((s) => s.conversations);
  const setConversations = useAppStore((s) => s.setConversations);
  const setMessages = useAppStore((s) => s.setMessages);
  const setConversationId = useAppStore((s) => s.setConversationId);
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) { setLoading(false); return; }
    listConversations(sessionId)
      .then(setConversations)
      .catch(() => setError("Could not load history"))
      .finally(() => setLoading(false));
  }, [sessionId]);

  const filtered = conversations.filter((c) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      (c.title ?? "").toLowerCase().includes(q) ||
      (c.created_at ?? "").includes(q)
    );
  });

  async function handleOpen(conv: ConversationSummary) {
    try {
      const detail = await getConversation(conv.id);
      setConversationId(conv.id);
      setMessages(
        detail.messages.map((m) => ({
          role: m.role as "user" | "assistant",
          content: m.content,
          timestamp: m.timestamp ?? undefined,
        }))
      );
      navigate("/chat");
    } catch {
      // ignore
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await deleteConversation(deleteTarget);
    setConversations(conversations.filter((c) => c.id !== deleteTarget));
    setDeleteTarget(null);
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 md:p-6 max-w-3xl mx-auto w-full">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">History</h1>
        {/* Filter input */}
        <input
          type="search"
          placeholder="Search…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-44 px-3 py-1.5 text-sm rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder-gray-400 dark:placeholder-gray-500"
        />
      </div>

      {loading && <Loading text="Loading history…" />}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-16 text-gray-400 dark:text-gray-500 select-none">
          <p className="text-4xl mb-3">💬</p>
          <p className="text-sm">
            {filter ? "No conversations match your search." : "No conversations yet. Start chatting!"}
          </p>
        </div>
      )}

      <ul className="space-y-3">
        {filtered.map((conv) => (
          <li key={conv.id}>
            <div className="flex items-start gap-3 p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors group">
              <button
                className="flex-1 text-left"
                onClick={() => handleOpen(conv)}
              >
                <p className="font-medium text-sm text-gray-800 dark:text-gray-200 line-clamp-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {conv.title ?? "Untitled conversation"}
                </p>
                <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-1">
                  {conv.created_at
                    ? new Date(conv.created_at).toLocaleString()
                    : "Unknown date"}
                </p>
              </button>
              <button
                onClick={() => setDeleteTarget(conv.id)}
                aria-label="Delete conversation"
                className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors md:opacity-0 md:group-hover:opacity-100"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
                  <path d="M10 11v6M14 11v6" />
                  <path d="M9 6V4h6v2" />
                </svg>
              </button>
            </div>
          </li>
        ))}
      </ul>

      <Modal
        open={!!deleteTarget}
        title="Delete conversation"
        message="This will permanently delete the conversation and all its messages."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        danger
      />
    </div>
  );
}
