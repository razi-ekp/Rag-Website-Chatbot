import React, { useEffect, useState } from "react";
import { Lightbulb } from "lucide-react";
import { getSuggestedQuestions } from "../../services/api";

const SuggestedQuestions = ({ siteId, onSelect }) => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!siteId) {
      setQuestions([]);
      return;
    }
    setLoading(true);
    getSuggestedQuestions(siteId)
      .then((data) => setQuestions(data.questions || []))
      .catch(() => setQuestions([]))
      .finally(() => setLoading(false));
  }, [siteId]);

  if (loading || questions.length === 0) return null;

  return (
    <div className="px-4 py-3 space-y-2">
      <div className="flex items-center gap-2 text-xs text-zinc-500">
        <Lightbulb size={12} />
        <span>Suggested questions</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            className="px-3 py-1.5 text-xs rounded-full bg-zinc-800/80 border border-zinc-700/50 text-zinc-300
              hover:border-violet-500/50 hover:text-violet-300 hover:bg-violet-900/20 transition-all duration-150"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestedQuestions;
