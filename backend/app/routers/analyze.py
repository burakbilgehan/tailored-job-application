from datetime import datetime
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.models.schemas import AnalyzeResponse, CoverLetterResult, CvSuggestion, RevisedCvResult
from app.services.fetcher import fetch_job_listing
from app.services.llm import analyze_and_generate
from app.services.parser import parse_cv

router = APIRouter(prefix="/api")

_file_cache: dict[str, tuple[str, str]] = {}  # filename -> (content, media_type)


@router.post("/analyze", response_model=AnalyzeResponse)
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

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    key = gemini_api_key.strip()

    try:
        result = analyze_and_generate(cv_text, cv_format, job_listing, profile_context, extra_context, key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    cover_letter_md = result["cover_letter"]
    suggestions_raw = result["cv_suggestions"]
    revised_cv_content = result["revised_cv"]

    cl_filename = f"cover_letter_{ts}.md"
    cv_ext = "tex" if cv_format == "latex" else "md"
    cv_filename = f"cv_revised_{ts}.{cv_ext}"
    media_type = "text/plain"

    _file_cache[cl_filename] = (cover_letter_md, media_type)
    _file_cache[cv_filename] = (revised_cv_content, media_type)

    return AnalyzeResponse(
        cover_letter=CoverLetterResult(markdown=cover_letter_md, filename=cl_filename),
        cv_suggestions=[CvSuggestion(**s) for s in suggestions_raw],
        revised_cv=RevisedCvResult(
            content=revised_cv_content,
            format=cv_format,
            filename=cv_filename,
        ),
    )


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
