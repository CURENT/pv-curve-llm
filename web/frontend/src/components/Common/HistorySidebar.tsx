/**
 * Left sidebar — always visible on desktop.
 *
 * Responsibilities:
 *   • Show logo + "new chat" button
 *   • Load and list past conversations
 *   • Open or delete a conversation
 *   • Settings link, dark-mode toggle, connection status at the bottom
 */
import { useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAppStore } from "../../store/appStore";
import {
  listConversations,
  getConversation,
  deleteConversation,
} from "../../services/api";
import type { ConversationSummary } from "../../types";

export default function HistorySidebar() {
  const sessionId        = useAppStore((s) => s.sessionId);
  const conversationId   = useAppStore((s) => s.conversationId);
  const conversations    = useAppStore((s) => s.conversations);
  const setConversations = useAppStore((s) => s.setConversations);
  const setMessages      = useAppStore((s) => s.setMessages);
  const setConversationId = useAppStore((s) => s.setConversationId);
  const startNew         = useAppStore((s) => s.startNewConversation);
  const isDark           = useAppStore((s) => s.isDark);
  const toggleDark       = useAppStore((s) => s.toggleDark);
  const connectionStatus = useAppStore((s) => s.connectionStatus);

  const navigate  = useNavigate();
  const location  = useLocation();

  // Reload the conversation list whenever the active conversation changes
  // (e.g. after the user finishes a new chat and a conversation is saved).
  useEffect(() => {
    if (!sessionId) return;
    listConversations(sessionId)
      .then(setConversations)
      .catch(() => {}); // silently ignore network errors
  }, [sessionId, conversationId]);

  // ── Handlers ────────────────────────────────────────────────────────────────

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

  async function handleDelete(e: React.MouseEvent, id: string) {
    e.stopPropagation(); // don't trigger handleOpen
    if (!window.confirm("Delete this conversation?")) return;
    await deleteConversation(id);
    setConversations(conversations.filter((c) => c.id !== id));
  }

  const dotColor =
    connectionStatus === "connected"  ? "bg-green-400" :
    connectionStatus === "connecting" ? "bg-yellow-400 animate-pulse" :
                                        "bg-red-400";

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <aside className="hidden md:flex flex-col w-56 flex-shrink-0 h-full bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">

      {/* ── Logo + New Chat button ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-3 py-3 border-b border-gray-200 dark:border-gray-800">
        <span className="flex items-center gap-2 font-bold text-sm text-gray-900 dark:text-gray-100 select-none">
          <span className="text-indigo-600 text-lg">⚡</span>
          PV Curve
        </span>

        <button
          onClick={() => { startNew(); navigate("/chat"); }}
          title="New chat"
          className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          {/* Pencil icon */}
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5" />
            <path d="M15.5 3.5a2.121 2.121 0 013 3L12 13l-4 1 1-4 6.5-6.5z" />
          </svg>
        </button>
      </div>

      {/* ── Conversation list ──────────────────────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
        {conversations.length === 0 && (
          <p className="text-xs text-gray-400 dark:text-gray-500 text-center py-8 select-none">
            No conversations yet
          </p>
        )}

        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => handleOpen(conv)}
            className={`w-full flex items-center gap-1.5 px-2 py-2 rounded-lg text-left group transition-colors ${
              conv.id === conversationId
                ? "bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300"
                : "text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-800"
            }`}
          >
            <span className="flex-1 truncate text-xs leading-snug">
              {conv.title ?? "Untitled"}
            </span>

            {/* Delete button — only appears on hover */}
            <span
              role="button"
              title="Delete"
              onClick={(e) => handleDelete(e, conv.id)}
              className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity shrink-0"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </span>
          </button>
        ))}
      </nav>

      {/* ── Bottom bar: Settings + dark-mode toggle + connection dot ──────── */}
      <div className="flex items-center justify-between px-3 py-3 border-t border-gray-200 dark:border-gray-800">
        <Link
          to="/settings"
          title="Settings"
          className={`p-1.5 rounded-lg transition-colors ${
            location.pathname === "/settings"
              ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/40"
              : "text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700"
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
          </svg>
        </Link>

        <div className="flex items-center gap-2">
          <span title={`Backend: ${connectionStatus}`} className={`w-2 h-2 rounded-full ${dotColor}`} />

          <button
            onClick={toggleDark}
            title="Toggle dark mode"
            className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors text-sm"
          >
            {isDark ? "☀️" : "🌙"}
          </button>
        </div>
      </div>
    </aside>
  );
}
