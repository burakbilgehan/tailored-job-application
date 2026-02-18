import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { diffLines } from "diff";
import type { AnalyzeResponse } from "../../api/client";
import { downloadUrl } from "../../api/client";

interface Props {
  result: AnalyzeResponse;
  originalCv: string;
}

type Tab = "cover" | "suggestions" | "diff";

export default function ResultTabs({ result, originalCv }: Props) {
  const [tab, setTab] = useState<Tab>("cover");

  return (
    <div className="result-tabs">
      <div className="tab-bar">
        <button className={tab === "cover" ? "active" : ""} onClick={() => setTab("cover")}>Cover Letter</button>
        <button className={tab === "suggestions" ? "active" : ""} onClick={() => setTab("suggestions")}>CV Suggestions</button>
        <button className={tab === "diff" ? "active" : ""} onClick={() => setTab("diff")}>Revised CV</button>
      </div>

      {tab === "cover" && (
        <div className="tab-content">
          <div className="actions">
            <a href={downloadUrl(result.cover_letter.filename)} download className="btn">Download .md</a>
            <button className="btn" onClick={() => navigator.clipboard.writeText(result.cover_letter.markdown)}>Copy</button>
          </div>
          <div className="markdown-body">
            <ReactMarkdown>{result.cover_letter.markdown}</ReactMarkdown>
          </div>
        </div>
      )}

      {tab === "suggestions" && (
        <div className="tab-content">
          {result.cv_summary && (
            <div className="cv-summary">
              <p>{result.cv_summary}</p>
            </div>
          )}
          <ul className="suggestions-list">
            {result.cv_suggestions.map((s, i) => (
              <li key={i}>
                <strong>{s.section}</strong>
                <p>{s.suggestion}</p>
                {s.reasoning && (
                  <p className="suggestion-reasoning">
                    <span className="reasoning-label">Why:</span> {s.reasoning}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === "diff" && (
        <div className="tab-content">
          <div className="actions">
            <a href={downloadUrl(result.revised_cv.filename)} download className="btn">
              Download .{result.revised_cv.format === "latex" ? "tex" : "md"}
            </a>
          </div>
          <DiffView original={originalCv} revised={result.revised_cv.content} />
        </div>
      )}
    </div>
  );
}

function DiffView({ original, revised }: { original: string; revised: string }) {
  const parts = diffLines(original, revised);
  return (
    <pre className="diff-view">
      {parts.map((part, i) => (
        <span
          key={i}
          className={part.added ? "diff-added" : part.removed ? "diff-removed" : "diff-unchanged"}
        >
          {part.value}
        </span>
      ))}
    </pre>
  );
}
