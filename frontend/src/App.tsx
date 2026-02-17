import { useState, useEffect, useRef } from "react";
import { analyze } from "./api/client";
import type { AnalyzeResponse } from "./api/client";
import InputForm from "./components/InputForm/InputForm";
import ResultTabs from "./components/ResultTabs/ResultTabs";
import "./App.css";

const STAGES = [
  "Reading your CV...",
  "Analyzing fit against the job listing...",
  "Writing cover letter...",
  "Generating CV suggestions...",
  "Rewriting your CV...",
  "Almost done...",
];

export default function App() {
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [originalCv, setOriginalCv] = useState("");
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (loading) {
      setStage(0);
      timerRef.current = setInterval(() => {
        setStage(s => Math.min(s + 1, STAGES.length - 1));
      }, 8000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [loading]);

  async function handleSubmit(fd: FormData) {
    setLoading(true);
    setError(null);
    setResult(null);

    const file = fd.get("cv_file") as File;
    const cvText = await file.text();
    setOriginalCv(cvText);

    try {
      const res = await analyze(fd);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Tailored Job Application</h1>
        <p>Upload your CV and a job listing — get a tailored cover letter and CV revisions.</p>
      </header>

      <main>
        <InputForm onSubmit={handleSubmit} loading={loading} />

        {loading && (
          <div className="loading-state">
            <div className="spinner" />
            <p>{STAGES[stage]}</p>
            <p className="hint">This may take 30–60 seconds.</p>
          </div>
        )}

        {error && <div className="error-box">{error}</div>}

        {result && <ResultTabs result={result} originalCv={originalCv} />}
      </main>
    </div>
  );
}
