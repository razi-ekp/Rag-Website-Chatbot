import { useState, useCallback, useRef } from "react";
import { createChatStream } from "../services/api";
import toast from "react-hot-toast";

export const useChat = (siteId) => {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef(null);

  const sendMessage = useCallback(
    async (question) => {
      if (!siteId || isStreaming) return;

      const userMsg = { id: Date.now(), role: "user", content: question };
      const assistantMsgId = Date.now() + 1;
      const assistantMsg = {
        id: assistantMsgId,
        role: "assistant",
        content: "",
        confidence: null,
        confidenceScore: null,
        sources: [],
        isInjection: false,
        streaming: true,
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsStreaming(true);

      const chatHistory = messages
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.content }));

      try {
        const controller = new AbortController();
        abortRef.current = controller;

        const response = await createChatStream(siteId, question, chatHistory);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let fullContent = "";
        let meta = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop();

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const raw = line.slice(6).trim();
            if (!raw) continue;

            try {
              const parsed = JSON.parse(raw);

              if (parsed.type === "meta") {
                meta = parsed;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId
                      ? {
                          ...m,
                          confidence: parsed.confidence,
                          confidenceScore: parsed.confidence_score,
                          sources: parsed.sources || [],
                          isInjection: parsed.is_injection,
                        }
                      : m
                  )
                );
              } else if (parsed.type === "token") {
                fullContent += parsed.content;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId
                      ? { ...m, content: fullContent }
                      : m
                  )
                );
              } else if (parsed.type === "done") {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId ? { ...m, streaming: false } : m
                  )
                );
              }
            } catch (_) {}
          }
        }
      } catch (err) {
        if (err.name !== "AbortError") {
          toast.error("Failed to get response. Please try again.");
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    content: "Sorry, I encountered an error. Please try again.",
                    streaming: false,
                  }
                : m
            )
          );
        }
      } finally {
        setIsStreaming(false);
      }
    },
    [siteId, messages, isStreaming]
  );

  const clearMessages = useCallback(() => setMessages([]), []);

  const stopStreaming = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    setIsStreaming(false);
  }, []);

  return { messages, isStreaming, sendMessage, clearMessages, stopStreaming };
};
