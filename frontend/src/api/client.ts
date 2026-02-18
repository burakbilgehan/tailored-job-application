const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface CvSuggestion {
  section: string;
  suggestion: string;
  reasoning: string;
}

export interface AnalyzeResponse {
  cover_letter: { markdown: string; filename: string };
  cv_summary: string;
  cv_suggestions: CvSuggestion[];
  revised_cv: { content: string; format: "latex" | "markdown"; filename: string };
  fit_analysis: string;
}

export async function analyze(
  formData: FormData,
  onStage: (message: string) => void,
): Promise<AnalyzeResponse> {
  const res = await fetch(`${BASE}/api/analyze`, { method: "POST", body: formData });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Unknown error");
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop()!;

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = JSON.parse(line.slice(6));
      if (data.type === "stage") {
        onStage(data.message);
      } else if (data.type === "result") {
        const { type: _type, ...result } = data;
        return result as AnalyzeResponse;
      } else if (data.type === "error") {
        throw new Error(data.detail);
      }
    }
  }

  throw new Error("Stream ended without result");
}

export function downloadUrl(filename: string): string {
  return `${BASE}/api/download/${filename}`;
}
