import json
from google import genai
from google.genai import types

MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """You are an expert career coach and professional writer.
Your task is to help candidates tailor their job applications to specific positions.
Always output in English, regardless of the input language.
Use tricks according to 2026 february job market best practices. 
Make sure our candidate stands out assuming that the evaluations can also be done by AI tools.
Be specific, actionable, and honest — highlight genuine strengths without fabricating experience."""


def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _chat(client: genai.Client, prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=4096,
        ),
    )
    return response.text


def analyze_fit(cv_text: str, job_listing: str, profile_context: str, extra_context: str, api_key: str) -> str:
    prompt = f"""Analyze how well this candidate fits the job listing.

## Candidate CV
{cv_text}

## Additional Profile Context
{profile_context or "None provided."}

## Job Listing
{job_listing}

## Extra Context
{extra_context or "None provided."}

Produce a structured analysis with:
1. Strong matches (skills, experience, accomplishments that align well)
2. Gaps or weaknesses relative to this role
3. Key themes to emphasize in the application

Be specific and reference actual content from the CV and job listing."""
    return _chat(_client(api_key), prompt)


def generate_cover_letter(analysis: str, cv_text: str, job_listing: str, extra_context: str, api_key: str) -> str:
    prompt = f"""Write a professional cover letter in English based on the analysis below.

## Fit Analysis
{analysis}

## Original CV
{cv_text}

## Job Listing
{job_listing}

## Extra Instructions
{extra_context or "None."}

Requirements:
- 3-4 paragraphs, concise and impactful
- Opening: why this role, why this company (infer from the listing)
- Middle: 2-3 specific achievements/skills that directly address the role requirements
- Closing: call to action
- Tone: confident but not arrogant, professional
- Do NOT use generic filler phrases ("I am writing to express my interest...")
- Output raw markdown, no code block wrapper"""
    return _chat(_client(api_key), prompt)


def generate_cv_suggestions(analysis: str, cv_text: str, cv_format: str, api_key: str) -> list[dict]:
    prompt = f"""Based on the fit analysis, suggest specific improvements to this CV for the target role.

## Fit Analysis
{analysis}

## Current CV ({cv_format})
{cv_text}

Output a JSON array (no markdown wrapper) where each item has:
- "section": the CV section to modify (e.g., "Summary", "Experience - Company X", "Skills")
- "suggestion": specific, actionable improvement instruction

Example:
[
  {{"section": "Summary", "suggestion": "Rewrite to emphasize distributed systems experience. Current version is too generic."}},
  {{"section": "Experience - Acme Corp", "suggestion": "Add a quantified achievement for the API migration project mentioned. E.g., 'reduced latency by X%'."}}
]

Return only the JSON array."""

    raw = _chat(_client(api_key), prompt)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


def generate_revised_cv(analysis: str, cv_text: str, cv_format: str, suggestions: list[dict], api_key: str) -> str:
    suggestions_text = "\n".join(
        f"- [{s['section']}]: {s['suggestion']}" for s in suggestions
    )
    prompt = f"""Rewrite the CV below in English, applying the suggested improvements for the target role.
Preserve the original format ({cv_format}) exactly — same structure, same commands/syntax if LaTeX.

## Fit Analysis
{analysis}

## Suggested Improvements
{suggestions_text}

## Original CV
{cv_text}

Rules:
- Only modify content that is directly improved by the suggestions
- Do NOT invent new experiences, companies, or degrees
- Do NOT add a code block wrapper — output the raw {cv_format} content only"""
    return _chat(_client(api_key), prompt)
