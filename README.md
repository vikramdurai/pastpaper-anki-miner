# Pastpaper Anki Miner

Convert past-paper text or PDFs into structured flashcard candidates for spaced repetition.

This project is a small Python CLI for turning question-paper inputs and mark-scheme inputs into review-ready JSON or CSV.

## What Works

- Parses simple numbered question text.
- Matches question IDs against mark-scheme answers.
- Exports card candidates as JSON or CSV.
- Accepts `.txt` directly and `.pdf` when the optional PDF dependency is installed.
- Includes deterministic parser and document-loading tests.

## What Does Not Work Yet

- PDF extraction depends on the quality of text embedded in the PDF.
- Extraction expects labels such as `1.`, `(a)`, `(i)`, `1a.`, or `1(a)(i)`.
- Cards are candidates for review, not guaranteed final Anki cards.

## Install

```bash
python -m pip install -e .
```

For PDF input support:

```bash
python -m pip install -e ".[pdf]"
```

## Usage

```bash
pastpaper-anki-miner \
  --questions path/to/question-paper.pdf \
  --marks path/to/mark-scheme.pdf \
  --source paper-code \
  --tag computer-science \
  --out out/cards.json
```

The same command can write CSV by changing the output extension:

```bash
pastpaper-anki-miner \
  --questions path/to/question-paper.pdf \
  --marks path/to/mark-scheme.pdf \
  --source paper-code \
  --tag computer-science \
  --out out/cards.csv
```

Plain text files can be passed to the same flags:

```bash
pastpaper-anki-miner \
  --questions path/to/question-paper.txt \
  --marks path/to/mark-scheme.txt \
  --source paper-code \
  --tag computer-science \
  --out out/cards.json
```

## Example Output

```json
[
  {
    "source": "paper-code",
    "question_id": "1a",
    "front": "Question text extracted from the paper.",
    "back": "Answer text extracted from the mark scheme.",
    "tags": ["computer-science"],
    "confidence": "manual-check"
  }
]
```

## Test

```bash
python -m unittest discover -s tests
```

## Architecture

- `extract.py` parses question and mark-scheme text into matched records.
- `documents.py` loads `.txt` files and extracts text from `.pdf` files.
- `models.py` defines the card candidate schema.
- `export.py` writes JSON or CSV.
- `cli.py` provides the command-line interface.

## Roadmap

- Add stronger validation reports for unmatched questions and answers.
- Improve extraction against more real-world PDF layouts.
- Add Anki CSV presets.
- Add a manual review workflow before Anki import.
