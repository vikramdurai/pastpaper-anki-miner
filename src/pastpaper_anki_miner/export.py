from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import CardCandidate


def write_cards(cards: list[CardCandidate], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.suffix.lower() == ".csv":
        write_csv(cards, output)
        return

    write_json(cards, output)


def write_json(cards: list[CardCandidate], path: Path) -> None:
    path.write_text(
        json.dumps([card.to_dict() for card in cards], indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(cards: list[CardCandidate], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["source", "question_id", "front", "back", "tags", "confidence"],
        )
        writer.writeheader()
        for card in cards:
            row = card.to_dict()
            row["tags"] = " ".join(card.tags)
            writer.writerow(row)
