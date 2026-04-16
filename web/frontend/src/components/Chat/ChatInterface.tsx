import { useEffect, useRef } from "react";
import { useAppStore } from "../../store/appStore";
import { wsService } from "../../services/websocket";
import MessageBubble from "./MessageBubble";
import MessageInput from "./MessageInput";

export default function ChatInterface() {
  const messages = useAppStore((s) => s.messages);
  const isProcessing = useAppStore((s) => s.isProcessing);
  const currentNode = useAppStore((s) => s.currentNode);
  const connectionStatus = useAppStore((s) => s.connectionStatus);
  const conversationId = useAppStore((s) => s.conversationId);

  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend(text: string) {
    wsService.sendMessage(text, conversationId ?? undefined);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Connection status bar */}
      {connectionStatus !== "connected" && (
        <div className={`px-4 py-2 text-xs text-center font-medium ${
          connectionStatus === "connecting"
            ? "bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400"
            : "bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400"
        }`}>
          {connectionStatus === "connecting"
            ? "⟳ Connecting to server…"
            : "✗ Disconnected — trying to reconnect…"}
        </div>
      )}

      {/* Message list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-1">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))
        )}

        {/* Processing indicator shown when agent is running but hasn't sent text yet */}
        {isProcessing && messages.length > 0 && (() => {
          const last = messages[messages.length - 1];
          return last?.role !== "assistant" ? (
            <div className="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500 pl-9">
              <span className="flex gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0ms]" />
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:300ms]" />
              </span>
              {currentNode && <span>{currentNode}…</span>}
            </div>
          ) : null;
        })()}

        <div ref={bottomRef} />
      </div>

      {/* Message input */}
      <MessageInput
        onSend={handleSend}
        disabled={isProcessing || connectionStatus !== "connected"}
        placeholder={
          connectionStatus !== "connected"
            ? "Waiting for server connection…"
            : "Ask anything about PV curves… (Enter to send)"
        }
      />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center py-16 px-8 select-none">
      <div className="w-16 h-16 rounded-2xl bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center mb-4 text-3xl">
        ⚡
      </div>
      <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
        PV Curve Agent
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs">
        Ask me to generate a PV curve, update parameters, or answer questions about voltage stability.
      </p>
      <div className="mt-6 space-y-2 text-xs text-gray-400 dark:text-gray-500">
        <p>Try: <em>"Generate PV curve for IEEE 39 bus 5"</em></p>
        <p>Try: <em>"What is load margin?"</em></p>
        <p>Try: <em>"Change grid to IEEE 118 and set bus to 10"</em></p>
      </div>
    </div>
  );
}
