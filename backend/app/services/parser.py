from typing import Literal


def detect_cv_format(filename: str) -> Literal["latex", "markdown"]:
    if filename.endswith(".tex"):
        return "latex"
    return "markdown"


def parse_cv(content: bytes, filename: str) -> tuple[str, Literal["latex", "markdown"]]:
    fmt = detect_cv_format(filename)
    text = content.decode("utf-8", errors="replace")
    return text, fmt
