import json
import subprocess
import sys
import unittest
import csv
import tempfile
from pathlib import Path

from pastpaper_anki_miner.extract import build_cards


ROOT = Path(__file__).resolve().parents[1]


class ExtractTests(unittest.TestCase):
    def test_build_cards_matches_questions_to_answers(self):
        cards = build_cards(
            "1. Topic heading.\n(a) Question one.\n(b) Question two.",
            "1a. Answer one.\n1b. Answer two.",
            source="parser-fixture",
            tags=["test"],
        )

        self.assertEqual(
            [card.to_dict() for card in cards],
            [
                {
                    "source": "parser-fixture",
                    "question_id": "1a",
                    "front": "Question one.",
                    "back": "Answer one.",
                    "tags": ["test"],
                    "confidence": "manual-check",
                },
                {
                    "source": "parser-fixture",
                    "question_id": "1b",
                    "front": "Question two.",
                    "back": "Answer two.",
                    "tags": ["test"],
                    "confidence": "manual-check",
                },
            ],
        )

    def test_cli_writes_json_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            questions = temp_path / "questions.txt"
            marks = temp_path / "marks.txt"
            output = temp_path / "cards.json"
            questions.write_text("1. Topic heading.\n(a) Question one.\n", encoding="utf-8")
            marks.write_text("1a. Answer one.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pastpaper_anki_miner.cli",
                    "--questions",
                    str(questions),
                    "--marks",
                    str(marks),
                    "--source",
                    "parser-fixture",
                    "--tag",
                    "test",
                    "--out",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            cards = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(cards[0]["question_id"], "1a")
        self.assertEqual(cards[0]["tags"], ["test"])
        self.assertIn("Wrote 1 card candidate(s)", result.stdout)

    def test_nested_roman_labels_include_parent_part(self):
        cards = build_cards(
            "1. A program processes input.\n(a) Consider this algorithm.\n(i) Identify the output.",
            "1ai. The output is the value printed by the final statement.",
            source="parser-fixture",
        )

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].question_id, "1ai")
        self.assertEqual(cards[0].front, "Identify the output.")

    def test_multiline_answer_continuations_are_preserved(self):
        cards = build_cards(
            "1. Algorithms.\n(a) Explain abstraction.",
            "1a. Hides unnecessary detail.\nFocuses on important features.",
            source="parser-fixture",
        )

        self.assertEqual(len(cards), 1)
        self.assertEqual(
            cards[0].back,
            "Hides unnecessary detail. Focuses on important features.",
        )

    def test_mark_scheme_id_variants_match_question_ids(self):
        cards = build_cards(
            "1. Algorithms.\n(a) Explain abstraction.\n(i) Identify the hidden detail.",
            "1(a)(i) The implementation detail is hidden.",
            source="parser-fixture",
        )

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].question_id, "1ai")
        self.assertEqual(cards[0].back, "The implementation detail is hidden.")

    def test_mark_scheme_mark_count_lines_are_continuations(self):
        cards = build_cards(
            "1. Algorithms.\n(a) Define abstraction.\n2 A car has several features.",
            "1(a) Hiding unnecessary detail.\n2 marks for a clear definition.",
            source="parser-fixture",
        )

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].question_id, "1a")
        self.assertEqual(
            cards[0].back,
            "Hiding unnecessary detail. 2 marks for a clear definition.",
        )

    def test_pdf_style_question_labels_match_mark_scheme_labels(self):
        cards = build_cards(
            "1 (a) Draw one line from each term to its definition.\n"
            "(b) Explain why colour depth affects file size.\n"
            "2 A car has several features.\n"
            "(a) Explain why this is an embedded system.",
            "1(a) Correct matching lines.\n"
            "1(b) More bits per pixel means more stored data.\n"
            "2(a) It is built into a larger system for a dedicated function.",
            source="parser-fixture",
        )

        self.assertEqual([card.question_id for card in cards], ["1a", "1b", "2a"])

    def test_cli_writes_csv_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            questions = temp_path / "questions.txt"
            marks = temp_path / "marks.txt"
            output = temp_path / "cards.csv"
            questions.write_text("1. Topic heading.\n(a) Question one.\n", encoding="utf-8")
            marks.write_text("1a. Answer one.\n", encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pastpaper_anki_miner.cli",
                    "--questions",
                    str(questions),
                    "--marks",
                    str(marks),
                    "--source",
                    "parser-fixture",
                    "--tag",
                    "test",
                    "--out",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["question_id"], "1a")
        self.assertEqual(rows[0]["tags"], "test")


if __name__ == "__main__":
    unittest.main()
