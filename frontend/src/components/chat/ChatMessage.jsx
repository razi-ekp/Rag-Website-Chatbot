import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User, ShieldAlert } from "lucide-react";
import clsx from "clsx";
import ConfidenceBadge from "../ui/ConfidenceBadge";
import SourceCitations from "../ui/SourceCitations";

const TypingDots = () => (
  <span className="inline-flex items-center gap-1 ml-1">
    {[0, 1, 2].map((i) => (
      <span
        key={i}
        className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce"
        style={{ animationDelay: `${i * 0.15}s` }}
      />
    ))}
  </span>
);

const ChatMessage = ({ message }) => {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 px-4 py-2">
        <div className="max-w-[75%] bg-violet-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed shadow-lg">
          {message.content}
        </div>
        <div className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center shrink-0 mt-1">
          <User size={16} className="text-zinc-300" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 px-4 py-2">
      <div className="w-8 h-8 rounded-full bg-violet-900/60 border border-violet-500/30 flex items-center justify-center shrink-0 mt-1">
        <Bot size={16} className="text-violet-400" />
      </div>

      <div className="max-w-[80%] space-y-2">
        {/* Injection alert */}
        {message.isInjection && (
          <div className="flex items-center gap-2 px-3 py-2 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-xs">
            <ShieldAlert size={14} />
            <span>Prompt injection detected — message blocked</span>
          </div>
        )}

        {/* Message bubble */}
        <div className="bg-zinc-800/80 border border-zinc-700/50 rounded-2xl rounded-tl-sm px-4 py-3 shadow-md">
          {message.content ? (
            <div className="prose prose-invert prose-sm max-w-none text-zinc-200 text-sm leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          ) : (
            <TypingDots />
          )}

          {message.streaming && message.content && (
            <span className="inline-block w-0.5 h-4 bg-violet-400 animate-pulse ml-1 align-middle" />
          )}
        </div>

        {/* Confidence + sources — only once streaming is done */}
        {!message.streaming && message.confidence && (
          <div className="flex items-center gap-2 flex-wrap">
            <ConfidenceBadge
              level={message.confidence}
              score={message.confidenceScore}
            />
          </div>
        )}

        {!message.streaming && message.sources?.length > 0 && (
          <SourceCitations sources={message.sources} />
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
