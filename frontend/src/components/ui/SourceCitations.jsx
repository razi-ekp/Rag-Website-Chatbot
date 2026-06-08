import React, { useState } from "react";
import { ExternalLink, ChevronDown, ChevronUp } from "lucide-react";

const SourceCitations = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  const visible = expanded ? sources : sources.slice(0, 2);

  return (
    <div className="mt-2 space-y-1">
      <button
        onClick={() => setExpanded((p) => !p)}
        className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
      >
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        {sources.length} source{sources.length > 1 ? "s" : ""}
      </button>

      {expanded && (
        <div className="space-y-1.5 pl-1">
          {visible.map((src, i) => (
            <a
              key={i}
              href={src.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-2 p-2 rounded-lg bg-zinc-800/60 border border-zinc-700/40 hover:border-violet-500/40 transition-colors group"
            >
              <ExternalLink
                size={12}
                className="mt-0.5 shrink-0 text-zinc-500 group-hover:text-violet-400"
              />
              <div className="min-w-0">
                <p className="text-xs font-medium text-zinc-300 truncate group-hover:text-violet-300">
                  {src.title || src.url}
                </p>
                <p className="text-xs text-zinc-500 line-clamp-2 mt-0.5">{src.snippet}</p>
              </div>
              <span className="ml-auto shrink-0 text-xs text-zinc-600">
                {(src.score * 100).toFixed(0)}%
              </span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
};

export default SourceCitations;
