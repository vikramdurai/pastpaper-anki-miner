from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class CardCandidate:
    source: str
    question_id: str
    front: str
    back: str
    tags: list[str] = field(default_factory=list)
    confidence: str = "manual-check"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
