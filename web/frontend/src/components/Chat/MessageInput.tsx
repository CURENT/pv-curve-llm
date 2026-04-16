import { useRef, useEffect, type KeyboardEvent, type ChangeEvent } from "react";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function MessageInput({ onSend, disabled = false, placeholder }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const valueRef = useRef("");

  // Auto-resize the textarea up to ~6 lines
  function resize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 144)}px`;
  }

  useEffect(() => {
    resize();
  }, []);

  function handleChange(e: ChangeEvent<HTMLTextAreaElement>) {
    valueRef.current = e.target.value;
    resize();
  }

  function submit() {
    const text = valueRef.current.trim();
    if (!text || disabled) return;
    onSend(text);
    // Clear textarea
    if (textareaRef.current) {
      textareaRef.current.value = "";
      valueRef.current = "";
      resize();
      textareaRef.current.focus();
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  const examplePrompts = [
    "Generate PV curve for IEEE 39 bus 5",
    "What is load margin?",
    "Change grid to IEEE 118",
  ];

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-3 space-y-2">
      {/* Example prompts (shown when input is empty) */}
      <div className="flex flex-wrap gap-2">
        {examplePrompts.map((p) => (
          <button
            key={p}
            onClick={() => {
              if (textareaRef.current) {
                textareaRef.current.value = p;
                valueRef.current = p;
                resize();
                textareaRef.current.focus();
              }
            }}
            className="text-xs px-3 py-1 rounded-full border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 hover:border-indigo-300 dark:hover:border-indigo-700 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
          >
            {p}
          </button>
        ))}
      </div>

      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
          placeholder={placeholder ?? "Ask anything about PV curves… (Enter to send, Shift+Enter for newline)"}
          className="flex-1 resize-none rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-600 disabled:opacity-50 placeholder-gray-400 dark:placeholder-gray-500 leading-relaxed"
          aria-label="Message input"
        />
        <button
          onClick={submit}
          disabled={disabled}
          aria-label="Send message"
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors"
        >
          {/* Send icon */}
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
      <p className="text-[11px] text-gray-400 dark:text-gray-600 text-right pr-1">
        Enter to send · Shift+Enter for newline
      </p>
    </div>
  );
}
