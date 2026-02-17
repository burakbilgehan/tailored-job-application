import json
from google import genai
from google.genai import types

MODEL = "gemini-1.5-flash"

SYSTEM_PROMPT = """You are an expert career coach and professional writer.
Your task is to help candidates tailor their job applications to specific positions.
Always output in English, regardless of the input language.
Use tricks according to 2026 february job market best practices. 
Make sure our candidate stands out assuming that the evaluations can also be done by AI tools.
Be specific, actionable, and honest — highlight genuine strengths without fabricating experience."""


def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def analyze_and_generate(
    cv_text: str,
    cv_format: str,
    job_listing: str,
    profile_context: str,
    extra_context: str,
    api_key: str,
) -> dict:
    prompt = f"""You are given a candidate's CV and a job listing. Perform a complete application tailoring in one pass.

## Candidate CV ({cv_format})
{cv_text}

## Additional Profile Context
{profile_context or "None provided."}

## Job Listing
{job_listing}

## Extra Instructions
{extra_context or "None provided."}

Produce a JSON object with exactly these four keys:

1. "fit_analysis": A structured analysis string covering:
   - Strong matches (skills, experience, accomplishments that align well)
   - Gaps or weaknesses relative to this role
   - Key themes to emphasize in the application

2. "cover_letter": A professional cover letter in markdown. Requirements:
   - 3-4 paragraphs, concise and impactful
   - Opening: why this role, why this company (infer from the listing)
   - Middle: 2-3 specific achievements/skills that directly address the role
   - Closing: call to action
   - Tone: confident but not arrogant, professional
   - Do NOT use generic filler phrases like "I am writing to express my interest..."
   - Raw markdown, no code block wrapper

3. "cv_suggestions": A JSON array where each item has:
   - "section": the CV section to modify (e.g., "Summary", "Experience - Company X", "Skills")
   - "suggestion": specific, actionable improvement instruction
   Example: [{{"section": "Summary", "suggestion": "Rewrite to emphasize distributed systems experience."}}]

4. "revised_cv": The full rewritten CV in {cv_format} format, applying the suggestions.
   - Preserve the original format exactly (same structure, same LaTeX commands if applicable)
   - Only modify content that is directly improved by the suggestions
   - Do NOT invent new experiences, companies, or degrees
   - Raw {cv_format} content only, no code block wrapper

Return ONLY the JSON object, no markdown wrapper, no extra text."""

    client = _client(api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=8192,
        ),
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    return json.loads(raw)
