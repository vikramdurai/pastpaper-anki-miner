from __future__ import annotations

import re

from .models import CardCandidate


QUESTION_RE = re.compile(r"^(?P<number>[1-9]\d*)[\).]?\s+(?P<text>[A-Z].+)$")
QUESTION_PART_RE = re.compile(
    r"^(?P<number>[1-9]\d*)\s+\((?P<label>[a-z]|[ivxlcdm]+)\)\s+(?P<text>.+)$",
    re.IGNORECASE,
)
PART_RE = re.compile(r"^\((?P<label>[a-z]|[ivxlcdm]+)\)\s+(?P<text>.+)$", re.IGNORECASE)
ANSWER_RE = re.compile(
    r"^(?P<id>"
    r"\d+\s*(?:\([a-z]\)|[a-z])(?:\([ivxlcdm]+\)|[ivxlcdm]+)?"
    r"|\d+\s*(?:\([ivxlcdm]+\)|[ivxlcdm]+)"
    r"|\d+"
    r")(?P<delimiter>[\).:]|\s)\s*(?P<text>.+)$",
    re.IGNORECASE,
)


def parse_question_text(text: str) -> dict[str, str]:
    questions: dict[str, str] = {}
    current_number: str | None = None
    current_part: str | None = None
    current_id: str | None = None

    for raw_line in text.splitlines():
        line = _clean_line(raw_line)
        if not line or line.startswith("#"):
            continue

        question_part_match = QUESTION_PART_RE.match(line)
        if question_part_match:
            current_number = question_part_match.group("number")
            current_part = question_part_match.group("label").lower()
            current_id = f"{current_number}{current_part}"
            questions[current_id] = question_part_match.group("text")
            continue

        question_match = QUESTION_RE.match(line)
        if question_match:
            current_number = question_match.group("number")
            current_part = None
            current_id = current_number
            questions[current_id] = question_match.group("text")
            continue

        part_match = PART_RE.match(line)
        if part_match and current_number:
            label = part_match.group("label").lower()
            if current_part and _is_roman_label(label):
                current_id = f"{current_number}{current_part}{label}"
            else:
                current_part = label
                current_id = f"{current_number}{label}"
            questions[current_id] = part_match.group("text")
            continue

        if current_id:
            questions[current_id] = f"{questions[current_id]} {line}"

    return questions


def parse_answer_text(text: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    current_id: str | None = None

    for raw_line in text.splitlines():
        line = _clean_line(raw_line)
        if not line or line.startswith("#"):
            continue

        answer_match = ANSWER_RE.match(line)
        if answer_match:
            raw_id = answer_match.group("id")
            delimiter = answer_match.group("delimiter")
            if delimiter.isspace() and raw_id.strip().isdigit():
                if current_id:
                    answers[current_id] = f"{answers[current_id]} {line}"
                continue
            current_id = normalize_question_id(answer_match.group("id"))
            answers[current_id] = answer_match.group("text")
            continue

        if current_id:
            answers[current_id] = f"{answers[current_id]} {line}"

    return answers


def build_cards(
    question_text: str,
    answer_text: str,
    *,
    source: str,
    tags: list[str] | None = None,
) -> list[CardCandidate]:
    questions = parse_question_text(question_text)
    answers = parse_answer_text(answer_text)
    cards: list[CardCandidate] = []

    for question_id, front in questions.items():
        back = answers.get(question_id)
        if not back:
            continue
        cards.append(
            CardCandidate(
                source=source,
                question_id=question_id,
                front=front,
                back=back,
                tags=tags or [],
            )
        )

    return cards


def _clean_line(line: str) -> str:
    return " ".join(line.strip().split())


def normalize_question_id(question_id: str) -> str:
    return re.sub(r"[^0-9a-z]+", "", question_id.lower())


def _is_roman_label(label: str) -> bool:
    return label in {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}
