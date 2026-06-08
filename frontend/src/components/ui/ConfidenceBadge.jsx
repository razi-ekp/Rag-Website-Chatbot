import React from "react";
import clsx from "clsx";

const CONFIDENCE_CONFIG = {
  HIGH: { label: "HIGH", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
  MEDIUM: { label: "MEDIUM", color: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
  LOW: { label: "LOW", color: "bg-red-500/20 text-red-400 border-red-500/30" },
  FALLBACK: { label: "FALLBACK", color: "bg-zinc-500/20 text-zinc-400 border-zinc-500/30" },
};

const ConfidenceBadge = ({ level, score }) => {
  const config = CONFIDENCE_CONFIG[level] || CONFIDENCE_CONFIG.FALLBACK;

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border",
        config.color
      )}
      title={score !== undefined ? `Score: ${(score * 100).toFixed(1)}%` : ""}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {config.label}
      {score !== undefined && (
        <span className="opacity-60 font-normal ml-0.5">
          {(score * 100).toFixed(0)}%
        </span>
      )}
    </span>
  );
};

export default ConfidenceBadge;
