import { useState } from "react";
import { analyze } from "./api/client";
import type { AnalyzeResponse } from "./api/client";
import InputForm from "./components/InputForm/InputForm";
import ResultTabs from "./components/ResultTabs/ResultTabs";
import "./App.css";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [originalCv, setOriginalCv] = useState("");

  async function handleSubmit(fd: FormData) {
    setLoading(true);
    setError(null);
    setResult(null);
    setStage("Reading your CV...");

    const file = fd.get("cv_file") as File;
    const cvText = await file.text();
    setOriginalCv(cvText);

    try {
      const res = await analyze(fd, (message) => setStage(message));
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
            <p>{stage}</p>
            <p className="hint">This may take 30–60 seconds.</p>
          </div>
        )}

        {error && <div className="error-box">{error}</div>}

        {result && <ResultTabs result={result} originalCv={originalCv} />}
      </main>
    </div>
  );
}
