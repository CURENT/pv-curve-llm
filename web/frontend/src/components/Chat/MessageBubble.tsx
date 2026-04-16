import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../../types";

interface Props {
  message: ChatMessage;
}

const NODE_LABELS: Record<string, string> = {
  classifier:   "Classifying…",
  router:       "Routing…",
  planner:      "Planning…",
  parameter:    "Updating parameters…",
  generation:   "Generating PV curve…",
  summary:      "Summarising…",
  question_general:   "Answering question…",
  question_parameter: "Answering question…",
  error_handler: "Handling error…",
  step_controller:  "Checking steps…",
  advance_step:     "Advancing step…",
};

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-3">
        <div className="max-w-[75%] bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start mb-3">
      {/* Avatar */}
      <div className="flex-shrink-0 w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center mr-2 mt-1 text-xs font-bold text-indigo-700 dark:text-indigo-300 select-none">
        AI
      </div>
      <div className="max-w-[80%] space-y-1">
        {/* Node indicator shown while streaming */}
        {message.streaming && message.node && (
          <p className="text-[11px] text-gray-400 dark:text-gray-500 font-medium tracking-wide">
            {NODE_LABELS[message.node] ?? `${message.node}…`}
          </p>
        )}

        <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none">
          {message.content ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          ) : (
            // Empty streaming bubble: show typing indicator
            <span className="flex gap-1 items-center h-4">
              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:300ms]" />
            </span>
          )}
        </div>

        {/* Timestamp */}
        {!message.streaming && message.timestamp && (
          <p className="text-[11px] text-gray-400 dark:text-gray-500 ml-1">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </p>
        )}
      </div>
    </div>
  );
}
