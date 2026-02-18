import json
from datetime import datetime
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse

from app.services.fetcher import fetch_job_listing
from app.services.llm import (
    analyze_fit,
    generate_cover_letter,
    generate_cv_suggestions,
    generate_revised_cv,
)
from app.services.parser import parse_cv

router = APIRouter(prefix="/api")

_file_cache: dict[str, tuple[str, str]] = {}  # filename -> (content, media_type)


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@router.post("/analyze")
async def analyze(
    cv_file: UploadFile = File(...),
    profile_context: str = Form(""),
    job_listing: str = Form(""),
    job_url: str = Form(""),
    extra_context: str = Form(""),
    gemini_api_key: str = Form(...),
):
    if not gemini_api_key.strip():
        raise HTTPException(status_code=422, detail="Gemini API key is required")

    cv_bytes = await cv_file.read()
    cv_text, cv_format = parse_cv(cv_bytes, cv_file.filename or "cv.md")

    if not job_listing and not job_url:
        raise HTTPException(status_code=422, detail="job_listing or job_url is required")

    if not job_listing and job_url:
        try:
            job_listing = await fetch_job_listing(job_url)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not fetch job URL: {e}")

    key = gemini_api_key.strip()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def generate():
        try:
            yield _sse({"type": "stage", "message": "Analyzing fit against the job listing..."})
            fit = analyze_fit(cv_text, job_listing, profile_context, extra_context, key)

            yield _sse({"type": "stage", "message": "Writing cover letter..."})
            cover_letter = generate_cover_letter(cv_text, fit, job_listing, extra_context, key)

            yield _sse({"type": "stage", "message": "Generating CV suggestions..."})
            suggestions_result = generate_cv_suggestions(cv_text, fit, job_listing, key)
            cv_summary = suggestions_result.get("summary", "")
            suggestions = suggestions_result.get("suggestions", [])

            yield _sse({"type": "stage", "message": "Rewriting your CV..."})
            revised_cv = generate_revised_cv(cv_text, cv_format, suggestions, job_listing, key)

            yield _sse({"type": "stage", "message": "Almost done..."})

            cl_filename = f"cover_letter_{ts}.md"
            cv_ext = "tex" if cv_format == "latex" else "md"
            cv_filename = f"cv_revised_{ts}.{cv_ext}"

            _file_cache[cl_filename] = (cover_letter, "text/plain")
            _file_cache[cv_filename] = (revised_cv, "text/plain")

            yield _sse({
                "type": "result",
                "cover_letter": {"markdown": cover_letter, "filename": cl_filename},
                "cv_summary": cv_summary,
                "cv_suggestions": suggestions,
                "revised_cv": {"content": revised_cv, "format": cv_format, "filename": cv_filename},
                "fit_analysis": fit,
            })
        except Exception as e:
            yield _sse({"type": "error", "detail": str(e)})

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/download/{filename}")
def download(filename: str):
    if filename not in _file_cache:
        raise HTTPException(status_code=404, detail="File not found or expired")
    content, media_type = _file_cache[filename]
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
