from __future__ import annotations

import re
import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Protocol


class PdfPage(Protocol):
    def extract_text(self, *args: object, **kwargs: object) -> str | None:
        ...


class PdfReaderLike(Protocol):
    pages: list[PdfPage]


ReaderFactory = Callable[[str | Path], PdfReaderLike]


def load_document_text(path: str | Path) -> str:
    source = _validate_input_path(path)

    if source.suffix.lower() == ".pdf":
        return extract_pdf_text(source)

    return source.read_text(encoding="utf-8")


def extract_pdf_text(path: str | Path, reader_factory: ReaderFactory | None = None) -> str:
    source = _validate_input_path(path)
    reader = _build_pdf_reader(source, reader_factory)
    page_text: list[str] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        normalized = _normalize_pdf_text(text)
        if normalized.strip():
            page_text.append(f"# Page {index}\n{normalized.strip()}")

    if not page_text:
        raise ValueError(f"No extractable text found in PDF: {source}")

    return "\n\n".join(page_text) + "\n"


def _build_pdf_reader(path: Path, reader_factory: ReaderFactory | None) -> PdfReaderLike:
    if reader_factory:
        return reader_factory(path)

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="ARC4 has been moved.*")
            from pypdf import PdfReader

            return PdfReader(str(path))
    except ImportError as exc:
        raise RuntimeError(
            "PDF input requires pypdf. Install it with: python -m pip install -e '.[pdf]'"
        ) from exc


def _validate_input_path(path: str | Path) -> Path:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file does not exist: {source}")
    if not source.is_file():
        raise ValueError(f"Input path is not a file: {source}")
    return source


def _normalize_pdf_text(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or _is_pdf_boilerplate(line):
            continue
        line = re.sub(r"\.{5,}", " ", line)
        lines.append(" ".join(line.split()))
    return "\n".join(lines)


def _is_pdf_boilerplate(line: str) -> bool:
    boilerplate_patterns = [
        r"^\d+$",
        r"^\[Turn over",
        r"^(\u00a9|\(C\)|Copyright)\b",
        r"^[A-Za-z ]+International .*Mark Scheme$",
        r"^This document (has|consists)",
        r"^DC \(",
        r"^\*?\d{8,}\*?$",
        r"^\d{4}/",
        r"^PUBLISHED\b",
        r"^Page \d+ of \d+$",
        r"^Question Answer Marks$",
    ]
    return any(re.search(pattern, line) for pattern in boilerplate_patterns)
