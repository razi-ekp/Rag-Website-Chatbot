import React, { useState, useRef, useEffect } from "react";
import { Send, Square } from "lucide-react";
import clsx from "clsx";

const ChatInput = ({ onSend, isStreaming, onStop, disabled }) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 160) + "px";
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-zinc-800 bg-zinc-900/95 backdrop-blur px-4 py-3">
      <div className="flex items-end gap-3 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled
                ? "Select a site to start chatting…"
                : "Ask a question about this website…"
            }
            disabled={disabled || isStreaming}
            rows={1}
            className={clsx(
              "w-full resize-none rounded-xl border bg-zinc-800/80 px-4 py-3 pr-12",
              "text-sm text-zinc-100 placeholder-zinc-500",
              "focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50",
              "transition-all duration-150 leading-relaxed",
              disabled ? "border-zinc-700/40 opacity-50 cursor-not-allowed" : "border-zinc-700"
            )}
          />
          <span className="absolute right-3 bottom-3 text-xs text-zinc-600 pointer-events-none">
            {input.length}/1000
          </span>
        </div>

        {isStreaming ? (
          <button
            onClick={onStop}
            className="w-10 h-10 rounded-xl bg-red-500/20 border border-red-500/40 flex items-center justify-center text-red-400 hover:bg-red-500/30 transition-colors shrink-0"
            title="Stop streaming"
          >
            <Square size={16} />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            className={clsx(
              "w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-all duration-150",
              input.trim() && !disabled
                ? "bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-500/25"
                : "bg-zinc-800 text-zinc-600 cursor-not-allowed"
            )}
          >
            <Send size={16} />
          </button>
        )}
      </div>
      <p className="text-center text-xs text-zinc-600 mt-1.5">
        Press Enter to send · Shift+Enter for newline
      </p>
    </div>
  );
};

export default ChatInput;
