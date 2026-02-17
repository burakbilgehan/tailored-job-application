from pydantic import BaseModel
from typing import Literal


class CvSuggestion(BaseModel):
    section: str
    suggestion: str


class CoverLetterResult(BaseModel):
    markdown: str
    filename: str


class RevisedCvResult(BaseModel):
    content: str
    format: Literal["latex", "markdown"]
    filename: str


class AnalyzeResponse(BaseModel):
    cover_letter: CoverLetterResult
    cv_suggestions: list[CvSuggestion]
    revised_cv: RevisedCvResult
