from __future__ import annotations

import argparse
from pathlib import Path

from .documents import load_document_text
from .extract import build_cards
from .export import write_cards


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert past-paper question and mark-scheme text or PDFs into flashcard candidates."
    )
    parser.add_argument("--questions", required=True, help="Path to question paper text or PDF")
    parser.add_argument("--marks", required=True, help="Path to mark scheme text or PDF")
    parser.add_argument("--out", required=True, help="Output .json or .csv path")
    parser.add_argument("--source", default=None, help="Source label stored on each card")
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Tag to add to every card. May be passed more than once.",
    )
    args = parser.parse_args(argv)

    question_path = Path(args.questions)
    source = args.source or question_path.stem
    cards = build_cards(
        load_document_text(question_path),
        load_document_text(args.marks),
        source=source,
        tags=args.tag,
    )

    if not cards:
        parser.error("No matching question-answer pairs were found.")

    write_cards(cards, args.out)
    print(f"Wrote {len(cards)} card candidate(s) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
