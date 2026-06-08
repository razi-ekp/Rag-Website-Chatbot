import React, { useState } from "react";
import {
  Globe, Plus, Trash2, CheckCircle2, Loader2,
  AlertCircle, ChevronRight, Bot
} from "lucide-react";
import clsx from "clsx";

const StatusIcon = ({ status }) => {
  if (status === "ready") return <CheckCircle2 size={12} className="text-emerald-400" />;
  if (status === "error") return <AlertCircle size={12} className="text-red-400" />;
  return <Loader2 size={12} className="text-violet-400 animate-spin" />;
};

const ProgressBar = ({ ingestStatus }) => {
  if (!ingestStatus) return null;
  const { status, pages_crawled, chunks_count, title } = ingestStatus;

  const statusLabel = {
    starting: "Initializing…",
    crawling: `Crawling pages… (${pages_crawled} found)`,
    indexing: `Indexing ${chunks_count} chunks…`,
    ready: "Ready!",
    error: "Error occurred",
  }[status] || status;

  return (
    <div className="mx-3 mb-3 p-3 rounded-xl bg-zinc-800/60 border border-zinc-700/50 space-y-2">
      <div className="flex items-center gap-2">
        <Loader2 size={12} className="text-violet-400 animate-spin shrink-0" />
        <p className="text-xs text-zinc-300 truncate">{title}</p>
      </div>
      <div className="h-1 bg-zinc-700 rounded-full overflow-hidden">
        <div
          className={clsx(
            "h-full rounded-full transition-all duration-500",
            status === "indexing" ? "bg-amber-400 w-[85%]" :
            status === "ready" ? "bg-emerald-400 w-full" :
            "bg-violet-500 w-[40%] animate-pulse"
          )}
        />
      </div>
      <p className="text-xs text-zinc-500">{statusLabel}</p>
    </div>
  );
};

const Sidebar = ({
  sites, activeSiteId, ingestStatus, isIngesting,
  onIngest, onSelectSite, onRemoveSite,
}) => {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");

  const handleIngest = () => {
    setError("");
    const trimmed = url.trim();
    if (!trimmed) return;

    try {
      new URL(trimmed.startsWith("http") ? trimmed : `https://${trimmed}`);
    } catch {
      setError("Please enter a valid URL");
      return;
    }

    const normalized = trimmed.startsWith("http") ? trimmed : `https://${trimmed}`;
    onIngest(normalized);
    setUrl("");
  };

  return (
    <aside className="w-72 shrink-0 flex flex-col bg-zinc-900 border-r border-zinc-800 h-full">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-zinc-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-zinc-100">RAG Chatbot</h1>
            <p className="text-xs text-zinc-500">Website Intelligence</p>
          </div>
        </div>
      </div>

      {/* URL Input */}
      <div className="p-3 border-b border-zinc-800 space-y-2">
        <p className="text-xs font-medium text-zinc-400 px-1">Ingest a website</p>
        <div className="flex gap-2">
          <input
            type="text"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setError(""); }}
            onKeyDown={(e) => e.key === "Enter" && handleIngest()}
            placeholder="https://example.com"
            disabled={isIngesting}
            className="flex-1 text-xs bg-zinc-800/80 border border-zinc-700 rounded-lg px-3 py-2
              text-zinc-200 placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-violet-500/50
              focus:border-violet-500/50 disabled:opacity-50 transition-all"
          />
          <button
            onClick={handleIngest}
            disabled={isIngesting || !url.trim()}
            className="w-9 h-9 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-40
              disabled:cursor-not-allowed flex items-center justify-center transition-colors shrink-0"
            title="Ingest"
          >
            {isIngesting ? (
              <Loader2 size={15} className="text-white animate-spin" />
            ) : (
              <Plus size={15} className="text-white" />
            )}
          </button>
        </div>
        {error && <p className="text-xs text-red-400 px-1">{error}</p>}
      </div>

      {/* Progress */}
      {isIngesting && ingestStatus && (
        <div className="pt-3">
          <ProgressBar ingestStatus={ingestStatus} />
        </div>
      )}

      {/* Sites List */}
      <div className="flex-1 overflow-y-auto py-2 space-y-0.5 px-2">
        <p className="text-xs font-medium text-zinc-500 px-2 py-1.5">
          Indexed sites ({sites.length})
        </p>
        {sites.length === 0 && !isIngesting && (
          <div className="text-center py-8 space-y-2">
            <Globe size={24} className="text-zinc-700 mx-auto" />
            <p className="text-xs text-zinc-600">No sites indexed yet</p>
          </div>
        )}
        {sites.map((site) => (
          <div
            key={site.site_id}
            className={clsx(
              "group flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all",
              activeSiteId === site.site_id
                ? "bg-violet-600/20 border border-violet-500/30"
                : "hover:bg-zinc-800/60 border border-transparent"
            )}
            onClick={() => onSelectSite(site.site_id)}
          >
            <Globe
              size={14}
              className={activeSiteId === site.site_id ? "text-violet-400" : "text-zinc-500"}
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-zinc-200 truncate">{site.title || site.url}</p>
              <p className="text-xs text-zinc-500 truncate">{site.pages_count} pages · {site.chunks_count} chunks</p>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <StatusIcon status={site.status} />
              <button
                onClick={(e) => { e.stopPropagation(); onRemoveSite(site.site_id); }}
                className="opacity-0 group-hover:opacity-100 text-zinc-600 hover:text-red-400 transition-all"
                title="Remove site"
              >
                <Trash2 size={12} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-zinc-800">
        <p className="text-xs text-zinc-600 text-center">
          Powered by Groq · ChromaDB · LLaMA 3.3
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
