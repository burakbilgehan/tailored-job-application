import json
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash-lite"
DELIMITER = "===REVISED_CV==="

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

Your response MUST have exactly two parts separated by the delimiter line {DELIMITER}

PART 1 (before the delimiter): A valid JSON object with these three keys:
- "fit_analysis": structured analysis string (strong matches, gaps, key themes)
- "cover_letter": professional cover letter in markdown (3-4 paragraphs, no generic openers, raw markdown)
- "cv_suggestions": array of objects with "section" and "suggestion" keys

PART 2 (after the delimiter): The full rewritten CV in raw {cv_format} format.
- Preserve exact format and structure
- Only apply content improvements from your suggestions
- Do NOT invent new experiences, companies, or degrees
- Output the raw file content only, no code block wrapper

Example structure:
{{"fit_analysis": "...", "cover_letter": "...", "cv_suggestions": [{{"section": "...", "suggestion": "..."}}]}}
{DELIMITER}
\\documentclass{{article}}
..."""

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

    if DELIMITER not in raw:
        raise ValueError(f"Model response missing delimiter '{DELIMITER}'")

    json_part, cv_part = raw.split(DELIMITER, 1)
    result = json.loads(json_part.strip())
    result["revised_cv"] = cv_part.strip()
    return result
