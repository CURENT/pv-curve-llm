/**
 * WebSocket service — manages the single persistent connection to the FastAPI backend.
 *
 * Protocol summary:
 *   Client → Server:  { type: "message", content: "...", conversation_id?: "..." }
 *                     { type: "ping" }
 *   Server → Client:  { type: "session",              session_id }
 *                     { type: "conversation_created",  conversation_id, title }
 *                     { type: "node_update",           node, content, conversation_id }
 *                     { type: "result",                results, plot_path }
 *                     { type: "complete" }  (client refetches GET /parameters so sidebar matches agent state)
 *                     { type: "error",                 content }
 *                     { type: "pong" }
 */
import { useAppStore } from "../store/appStore";
import { getParameters } from "./api";
import type { WSIncoming, WSOutgoing } from "../types";

const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;

// How long to wait before attempting reconnect (doubles each attempt, max 30s)
const INITIAL_RETRY_MS = 1_000;
const MAX_RETRY_MS = 30_000;

class WebSocketService {
  private ws: WebSocket | null = null;
  private retryMs = INITIAL_RETRY_MS;
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private destroyed = false;

  connect() {
    this.destroyed = false;
    const store = useAppStore.getState();
    store.setConnectionStatus("connecting");

    const sessionId = store.sessionId ?? "";
    const url = sessionId ? `${WS_URL}?session_id=${sessionId}` : WS_URL;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.retryMs = INITIAL_RETRY_MS;
      useAppStore.getState().setConnectionStatus("connected");
      // Keep-alive ping every 20s
      this.pingTimer = setInterval(() => this.send({ type: "ping" }), 20_000);
    };

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const msg: WSIncoming = JSON.parse(event.data as string);
        this.handleMessage(msg);
      } catch {
        // ignore malformed frames
      }
    };

    this.ws.onclose = () => {
      this.clearTimers();
      if (!this.destroyed) {
        useAppStore.getState().setConnectionStatus("disconnected");
        // Reconnect with back-off
        this.reconnectTimer = setTimeout(() => {
          this.retryMs = Math.min(this.retryMs * 2, MAX_RETRY_MS);
          this.connect();
        }, this.retryMs);
      }
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  private handleMessage(msg: WSIncoming) {
    const store = useAppStore.getState();

    switch (msg.type) {
      case "session":
        if (msg.session_id) store.setSessionId(msg.session_id);
        break;

      case "conversation_created":
        if (msg.conversation_id) {
          store.setConversationId(msg.conversation_id);
        }
        break;

      case "node_update": {
        const content = msg.content ?? "";
        const node = msg.node ?? "";

        // Update "processing" indicator so user sees which node is running
        store.setProcessing(true, node);

        if (content) {
          // Check if we already have a streaming assistant bubble
          const msgs = store.messages;
          const last = msgs[msgs.length - 1];
          if (last && last.role === "assistant" && last.streaming) {
            store.appendToLastMessage(content, node);
          } else {
            // Start a new streaming bubble
            store.addMessage({
              role: "assistant",
              content,
              streaming: true,
              node,
            });
          }
        }
        break;
      }

      case "result":
        if (msg.results) {
          store.setResult(msg.results, msg.plot_path ?? "");
        }
        break;

      case "complete":
        store.finaliseLastMessage();
        store.setProcessing(false, null);
        // Agent may have updated inputs (e.g. "change power factor to 0.9"); REST panel only had mount/Apply — sync now.
        {
          const sid = store.sessionId;
          if (sid) {
            void getParameters(sid)
              .then((p) => useAppStore.getState().setParameters(p))
              .catch(() => {
                /* offline or session evicted — ignore */
              });
          }
        }
        break;

      case "error":
        store.finaliseLastMessage();
        store.setProcessing(false, null);
        store.addMessage({
          role: "assistant",
          content: `⚠️ Error: ${msg.content ?? "Unknown error"}`,
          streaming: false,
        });
        break;

      case "pong":
        // heartbeat response — nothing to do
        break;
    }
  }

  send(msg: WSOutgoing) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg));
    }
  }

  sendMessage(content: string, conversationId?: string) {
    const store = useAppStore.getState();
    // Optimistically add user bubble immediately
    store.addMessage({ role: "user", content });
    store.setProcessing(true, null);

    this.send({
      type: "message",
      content,
      conversation_id: conversationId ?? store.conversationId ?? undefined,
    });
  }

  disconnect() {
    this.destroyed = true;
    this.clearTimers();
    this.ws?.close();
  }

  private clearTimers() {
    if (this.pingTimer) { clearInterval(this.pingTimer); this.pingTimer = null; }
    if (this.reconnectTimer) { clearTimeout(this.reconnectTimer); this.reconnectTimer = null; }
  }

  get status() {
    return this.ws?.readyState;
  }
}

// Singleton — one connection for the whole app lifetime
export const wsService = new WebSocketService();
