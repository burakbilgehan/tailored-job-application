import { useRef, useState } from "react";

interface Props {
  onSubmit: (data: FormData) => void;
  loading: boolean;
}

const API_KEY_STORAGE_KEY = "gemini_api_key";

export default function InputForm({ onSubmit, loading }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [jobSource, setJobSource] = useState<"text" | "url">("text");
  const [apiKey, setApiKey] = useState(() => localStorage.getItem(API_KEY_STORAGE_KEY) ?? "");

  function handleApiKeyChange(e: React.ChangeEvent<HTMLInputElement>) {
    const val = e.target.value;
    setApiKey(val);
    localStorage.setItem(API_KEY_STORAGE_KEY, val);
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!apiKey.trim()) return alert("Gemini API key is required");
    const form = e.currentTarget;
    const fd = new FormData();

    const file = fileRef.current?.files?.[0];
    if (!file) return alert("CV file is required");
    fd.append("cv_file", file);

    fd.append("gemini_api_key", apiKey.trim());
    fd.append("profile_context", (form.elements.namedItem("profile_context") as HTMLTextAreaElement).value);
    fd.append("extra_context", (form.elements.namedItem("extra_context") as HTMLTextAreaElement).value);

    if (jobSource === "text") {
      fd.append("job_listing", (form.elements.namedItem("job_listing") as HTMLTextAreaElement).value);
    } else {
      fd.append("job_url", (form.elements.namedItem("job_url") as HTMLInputElement).value);
    }

    onSubmit(fd);
  }

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <section>
        <label>Gemini API Key <span className="required">*</span></label>
        <p className="hint">Get your key from <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer">Google AI Studio</a>. It's saved in your browser.</p>
        <input
          type="password"
          value={apiKey}
          onChange={handleApiKeyChange}
          placeholder="AIza..."
          autoComplete="off"
        />
      </section>

      <section>
        <label>CV File <span className="required">*</span></label>
        <p className="hint">Accepts .tex (LaTeX) or .md (Markdown)</p>
        <input ref={fileRef} type="file" accept=".tex,.md" required />
      </section>

      <section>
        <label>Profile Context <span className="optional">(optional)</span></label>
        <p className="hint">Paste LinkedIn summary, portfolio notes, or anything that adds context to your profile</p>
        <textarea name="profile_context" rows={5} placeholder="e.g. I have 3 years of experience in distributed systems, led a team of 4..." />
      </section>

      <section>
        <label>Job Listing <span className="required">*</span></label>
        <div className="toggle">
          <button type="button" className={jobSource === "text" ? "active" : ""} onClick={() => setJobSource("text")}>Paste text</button>
          <button type="button" className={jobSource === "url" ? "active" : ""} onClick={() => setJobSource("url")}>URL</button>
        </div>
        {jobSource === "text" ? (
          <textarea name="job_listing" rows={8} placeholder="Paste the full job description here..." required />
        ) : (
          <input name="job_url" type="url" placeholder="https://..." required />
        )}
      </section>

      <section>
        <label>Extra Context <span className="optional">(optional)</span></label>
        <p className="hint">Specific points to emphasize, tone preferences, company notes</p>
        <textarea name="extra_context" rows={3} placeholder="e.g. Emphasize leadership experience. Formal tone." />
      </section>

      <button type="submit" disabled={loading} className="submit-btn">
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </form>
  );
}
