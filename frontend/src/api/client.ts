const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface CvSuggestion {
  section: string;
  suggestion: string;
}

export interface AnalyzeResponse {
  cover_letter: { markdown: string; filename: string };
  cv_suggestions: CvSuggestion[];
  revised_cv: { content: string; format: "latex" | "markdown"; filename: string };
}

export async function analyze(formData: FormData): Promise<AnalyzeResponse> {
  const res = await fetch(`${BASE}/api/analyze`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Unknown error");
  }
  return res.json();
}

export function downloadUrl(filename: string): string {
  return `${BASE}/api/download/${filename}`;
}
