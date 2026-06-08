import React, { useEffect, useRef } from "react";
import { MessageSquare } from "lucide-react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import SuggestedQuestions from "./SuggestedQuestions";
import { useChat } from "../../hooks/useChat";

const EmptyState = ({ siteId }) => (
  <div className="flex-1 flex flex-col items-center justify-center text-center px-8 py-16 space-y-4">
    <div className="w-16 h-16 rounded-2xl bg-violet-900/40 border border-violet-500/20 flex items-center justify-center">
      <MessageSquare size={32} className="text-violet-400" />
    </div>
    <div>
      <p className="text-zinc-300 font-medium">
        {siteId ? "Start chatting!" : "No site selected"}
      </p>
      <p className="text-zinc-500 text-sm mt-1">
        {siteId
          ? "Ask anything about this website's content."
          : "Ingest a website or select one from the sidebar."}
      </p>
    </div>
  </div>
);

const ChatWindow = ({ siteId, siteTitle }) => {
  const { messages, isStreaming, sendMessage, clearMessages, stopStreaming } = useChat(siteId);
  const bottomRef = useRef(null);
  const prevSiteId = useRef(null);

  useEffect(() => {
    if (prevSiteId.current !== siteId) {
      clearMessages();
      prevSiteId.current = siteId;
    }
  }, [siteId, clearMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-zinc-950">
      {/* Header */}
      <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-900/60 backdrop-blur">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div>
            <h2 className="text-sm font-semibold text-zinc-100 truncate max-w-sm">
              {siteTitle || "RAG Website Chatbot"}
            </h2>
            <p className="text-xs text-zinc-500 mt-0.5">
              {siteId ? "Ask questions about this site" : "Select or ingest a website to begin"}
            </p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-2 py-1 rounded border border-zinc-700/50 hover:border-zinc-600"
            >
              Clear chat
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-1">
        {messages.length === 0 ? (
          <EmptyState siteId={siteId} />
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggested questions */}
      {siteId && messages.length === 0 && (
        <SuggestedQuestions siteId={siteId} onSelect={sendMessage} />
      )}

      {/* Input */}
      <ChatInput
        onSend={sendMessage}
        isStreaming={isStreaming}
        onStop={stopStreaming}
        disabled={!siteId}
      />
    </div>
  );
};

export default ChatWindow;
