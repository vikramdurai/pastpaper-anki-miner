import tempfile
import unittest
from pathlib import Path

from pastpaper_anki_miner.documents import extract_pdf_text, load_document_text


class FakePage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class FakeReader:
    def __init__(self, _path):
        self.pages = [
            FakePage("1. Algorithms\n(a) Define abstraction."),
            FakePage(None),
            FakePage("1a. Hiding unnecessary detail."),
        ]


class BoilerplateReader:
    def __init__(self, _path):
        self.pages = [
            FakePage(
                "3\n"
                "1234/12/ Sample Session (C) Example Board 2026 [Turn over\n"
                "1 (a) Define abstraction.\n"
                "........................................................................\n"
                "[2]"
            )
        ]


class EmptyReader:
    def __init__(self, _path):
        self.pages = [FakePage("   "), FakePage(None)]


class DocumentTests(unittest.TestCase):
    def test_load_document_text_reads_utf8_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "input.txt"
            path.write_text("1. Example\n", encoding="utf-8")

            self.assertEqual(load_document_text(path), "1. Example\n")

    def test_extract_pdf_text_uses_reader_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "input.pdf"
            path.write_bytes(b"%PDF test placeholder")

            text = extract_pdf_text(path, reader_factory=FakeReader)

        self.assertIn("# Page 1\n1. Algorithms", text)
        self.assertIn("# Page 3\n1a. Hiding unnecessary detail.", text)
        self.assertNotIn("# Page 2", text)

    def test_extract_pdf_text_fails_when_no_text_is_extractable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty.pdf"
            path.write_bytes(b"%PDF test placeholder")

            with self.assertRaisesRegex(ValueError, "No extractable text"):
                extract_pdf_text(path, reader_factory=EmptyReader)

    def test_extract_pdf_text_removes_common_pdf_boilerplate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "input.pdf"
            path.write_bytes(b"%PDF test placeholder")

            text = extract_pdf_text(path, reader_factory=BoilerplateReader)

        self.assertIn("1 (a) Define abstraction.", text)
        self.assertNotIn("1234/12", text)
        self.assertNotIn("................................................................", text)


if __name__ == "__main__":
    unittest.main()
