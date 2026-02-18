import json
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash-lite"

SYSTEM_PROMPT = """You are an expert career coach and professional writer.
Your task is to help candidates tailor their job applications to specific positions.
Always output in English, regardless of the input language.
Use tricks according to 2026 february job market best practices.
Make sure our candidate stands out assuming that the evaluations can also be done by AI tools. Specifically ATS.
Be specific, actionable, and honest — highlight genuine strengths without fabricating experience."""


def _generate(prompt: str, api_key: str, max_tokens: int = 2048) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text.strip()


def analyze_fit(
    cv_text: str,
    job_listing: str,
    profile_context: str,
    extra_context: str,
    api_key: str,
) -> str:
    prompt = f"""Analyze how well this candidate's CV fits the job listing.

## Candidate CV
{cv_text}

## Additional Profile Context
{profile_context or "None provided."}

## Job Listing
{job_listing}

## Extra Instructions
{extra_context or "None provided."}

Provide a structured analysis covering:
- Strong matches (skills, experience, achievements that align well)
- Gaps (requirements not clearly demonstrated)
- Key themes the candidate should emphasize

Be concise and specific. Plain text output."""
    return _generate(prompt, api_key, max_tokens=1024)


def generate_cover_letter(
    cv_text: str,
    fit_analysis: str,
    job_listing: str,
    extra_context: str,
    api_key: str,
) -> str:
    prompt = f"""Write a professional cover letter for this candidate.

## Fit Analysis
{fit_analysis}

## Candidate CV
{cv_text}

## Job Listing
{job_listing}

## Extra Instructions
{extra_context or "None provided."}

Requirements:
- 2-3 paragraphs
- No generic openers like "I am writing to apply..."
- Highlight genuine strengths from the fit analysis
- Make it sound natural, simple and humanlike
- Emphasize enthusiasm for the specific role and company, along with achievements
- Output in markdown format"""
    return _generate(prompt, api_key, max_tokens=1024)


def generate_cv_suggestions(
    cv_text: str,
    fit_analysis: str,
    job_listing: str,
    api_key: str,
) -> dict:
    prompt = f"""Based on this fit analysis, provide a CV improvement report for the candidate.

## Fit Analysis
{fit_analysis}

## Candidate CV
{cv_text}

## Job Listing
{job_listing}

Output a JSON object only, no other text, no markdown code blocks.
The object must have:
- "summary": a 2-3 sentence overall assessment of the candidate's fit and the main direction of improvements needed
- "suggestions": an array of specific CV changes, each with:
  - "section": which CV section to change
  - "suggestion": exactly what to change or add
  - "reasoning": why this change matters for this specific role — connect it to something concrete in the job listing or the candidate's gap

Example:
{{
  "summary": "Strong technical background but the CV undersells impact. Prioritize quantifying results and surfacing role-relevant keywords the ATS will scan for.",
  "suggestions": [
    {{
      "section": "Work Experience",
      "suggestion": "Add metrics to the data pipeline project — e.g. 'reduced processing time by 40%'",
      "reasoning": "The job listing explicitly asks for experience with high-volume data systems. A bare description of the project gives no signal on scale; a number makes it credible and scannable."
    }}
  ]
}}"""
    raw = _generate(prompt, api_key, max_tokens=2048).strip()
    if raw.startswith("```"):
        raw = raw.split("```", 1)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw.strip())


def generate_revised_cv(
    cv_text: str,
    cv_format: str,
    suggestions: list[dict],
    job_listing: str,
    api_key: str,
) -> str:
    suggestions_text = "\n".join(
        f"- [{s['section']}] {s['suggestion']}" for s in suggestions
    )
    prompt = f"""Rewrite this CV applying the improvements listed below.

## Original CV ({cv_format})
{cv_text}

## Improvements to Apply
{suggestions_text}

## Job Listing Context
{job_listing}

Requirements:
- Preserve the exact format and structure of the original
- Only apply content improvements from the list above
- Do NOT invent new experiences, companies, or degrees
- Output the raw file content only, no code block wrapper, no explanation"""
    return _generate(prompt, api_key, max_tokens=4096)
