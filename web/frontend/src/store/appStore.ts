import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  ChatMessage,
  ConversationSummary,
  ConnectionStatus,
  Parameters,
  LLMConfigResponse,
  PVCurveResult,
} from "../types";

interface AppState {
  // ── Session ───────────────────────────────────────────────────────────────
  sessionId: string | null;
  setSessionId: (id: string) => void;

  // ── Active conversation ──────────────────────────────────────────────────
  conversationId: string | null;
  setConversationId: (id: string | null) => void;

  messages: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  /** Append text to the last streaming assistant message */
  appendToLastMessage: (content: string, node?: string) => void;
  /** Stop streaming flag on the last assistant message */
  finaliseLastMessage: () => void;
  setMessages: (msgs: ChatMessage[]) => void;
  clearMessages: () => void;

  // ── WebSocket connection ──────────────────────────────────────────────────
  connectionStatus: ConnectionStatus;
  setConnectionStatus: (s: ConnectionStatus) => void;

  // ── Agent processing ──────────────────────────────────────────────────────
  isProcessing: boolean;
  currentNode: string | null;
  setProcessing: (v: boolean, node?: string | null) => void;

  // ── PV Curve results ──────────────────────────────────────────────────────
  latestResult: PVCurveResult | null;
  latestPlotPath: string | null;
  setResult: (result: PVCurveResult, plotPath: string) => void;

  // ── Parameters ────────────────────────────────────────────────────────────
  parameters: Parameters | null;
  setParameters: (p: Parameters) => void;

  // ── LLM config ────────────────────────────────────────────────────────────
  llmConfig: LLMConfigResponse | null;
  setLLMConfig: (c: LLMConfigResponse) => void;

  // ── History ────────────────────────────────────────────────────────────────
  conversations: ConversationSummary[];
  setConversations: (list: ConversationSummary[]) => void;

  // ── UI ────────────────────────────────────────────────────────────────────
  isDark: boolean;
  toggleDark: () => void;

  // ── New conversation ──────────────────────────────────────────────────────
  startNewConversation: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Session
      sessionId: null,
      setSessionId: (id) => set({ sessionId: id }),

      // Active conversation
      conversationId: null,
      setConversationId: (id) => set({ conversationId: id }),

      messages: [],
      addMessage: (msg) =>
        set((s) => ({ messages: [...s.messages, msg] })),
      appendToLastMessage: (content, node) =>
        set((s) => {
          const msgs = [...s.messages];
          const last = msgs[msgs.length - 1];
          if (last && last.role === "assistant" && last.streaming) {
            msgs[msgs.length - 1] = {
              ...last,
              content: last.content + content,
              node: node ?? last.node,
            };
          }
          return { messages: msgs };
        }),
      finaliseLastMessage: () =>
        set((s) => {
          const msgs = [...s.messages];
          const last = msgs[msgs.length - 1];
          if (last && last.streaming) {
            msgs[msgs.length - 1] = { ...last, streaming: false, node: undefined };
          }
          return { messages: msgs };
        }),
      setMessages: (msgs) => set({ messages: msgs }),
      clearMessages: () => set({ messages: [] }),

      // Connection
      connectionStatus: "disconnected",
      setConnectionStatus: (s) => set({ connectionStatus: s }),

      // Agent processing
      isProcessing: false,
      currentNode: null,
      setProcessing: (v, node = null) =>
        set({ isProcessing: v, currentNode: node }),

      // PV Curve results
      latestResult: null,
      latestPlotPath: null,
      setResult: (result, plotPath) =>
        set({ latestResult: result, latestPlotPath: plotPath }),

      // Parameters
      parameters: null,
      setParameters: (p) => set({ parameters: p }),

      // LLM config
      llmConfig: null,
      setLLMConfig: (c) => set({ llmConfig: c }),

      // History
      conversations: [],
      setConversations: (list) => set({ conversations: list }),

      // UI
      isDark: false,
      toggleDark: () => set((s) => ({ isDark: !s.isDark })),

      // New conversation
      startNewConversation: () =>
        set({
          conversationId: null,
          messages: [],
          latestResult: null,
          latestPlotPath: null,
          isProcessing: false,
          currentNode: null,
        }),
    }),
    {
      name: "pv-curve-app",
      // Only persist the session id, LLM config choice, and dark mode
      partialize: (s) => ({
        sessionId: s.sessionId,
        llmConfig: s.llmConfig,
        isDark: s.isDark,
      }),
    }
  )
);
