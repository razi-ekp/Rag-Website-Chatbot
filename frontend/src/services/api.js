import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000/api/v1";
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// ── Ingest ──────────────────────────────────────────────────────────────────

export const startIngest = async (url, maxPages = 50) => {
  const res = await api.post("/ingest/start", { url, max_pages: maxPages });
  return res.data;
};

export const getIngestStatus = async (siteId) => {
  const res = await api.get(`/ingest/status/${siteId}`);
  return res.data;
};

export const listSites = async () => {
  const res = await api.get("/ingest/sites");
  return res.data;
};

export const deleteSite = async (siteId) => {
  const res = await api.delete(`/ingest/sites/${siteId}`);
  return res.data;
};

// Returns an EventSource for SSE crawl progress
export const createProgressStream = (siteId) => {
  return new EventSource(`${API_URL}/ingest/stream/${siteId}`);
};

// ── Chat ────────────────────────────────────────────────────────────────────

export const askQuestion = async (siteId, question, chatHistory = []) => {
  const res = await api.post("/chat/ask", {
    site_id: siteId,
    question,
    chat_history: chatHistory,
  });
  return res.data;
};

export const getSuggestedQuestions = async (siteId) => {
  const res = await api.get(`/chat/suggested/${siteId}`);
  return res.data;
};

// Streaming chat — returns an EventSource
export const createChatStream = (siteId, question, chatHistory = []) => {
  // POST-based SSE via fetch (EventSource doesn't support POST)
  return fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ site_id: siteId, question, chat_history: chatHistory }),
  });
};
