"""Regressions for repository links, included notes and readable diagrams."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_docs


class DocumentSources(unittest.TestCase):
    def test_fenced_examples_are_parsed_but_never_executed(self):
        source = Path("README.md")
        self.assertEqual(
            check_docs.check_commands("```python\nraise RuntimeError()\n```", source),
            [],
        )
        for text in (
            "```python\ndef (\n```",
            '```json\n{"key":}\n```',
            "```sh\npython -m\n```",
        ):
            with self.subTest(text=text):
                self.assertTrue(check_docs.check_commands(text, source))

    def test_missing_script_requirements_and_tests_are_rejected(self):
        text = """```sh
python scripts/does-not-exist.py
python -m pip install -r missing-requirements.txt
python -m unittest discover -s tests -p 'missing_*.py'
```
"""
        self.assertEqual(len(check_docs.check_commands(text, Path("README.md"))), 3)

    def test_links_in_collapsed_notes_are_checked_in_destination_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            article = root / "docs/en/lesson.md"
            article.parent.mkdir(parents=True)
            article.write_text("# Lesson\n\n## Evidence\n")
            partial = root / "site/lessons/en/lesson-details.md"
            partial.parent.mkdir(parents=True)
            partial.write_text(
                "<details><summary>Read</summary>\n\n[Evidence](lesson.md#evidence)\n\n</details>"
            )
            manifest = [
                {
                    "id": "lesson",
                    "source": "docs/zh/lesson.md",
                    "en_source": "docs/en/lesson.md",
                }
            ]
            with (
                patch.object(check_docs, "ROOT", root),
                patch.object(check_docs, "load_curriculum", return_value=manifest),
            ):
                check_docs.check()
                partial.write_text("[Missing](lesson.md#missing)")
                with self.assertRaisesRegex(SystemExit, "missing anchor"):
                    check_docs.check()

    def test_english_links_must_not_silently_route_to_chinese(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for language in ("zh", "en"):
                folder = root / f"docs/{language}"
                folder.mkdir(parents=True)
                (folder / "lesson.md").write_text("# Lesson\n")
            (root / "docs/en/lesson.md").write_text("[Wrong language](../zh/lesson.md)")
            manifest = [
                {
                    "id": "lesson",
                    "source": "docs/zh/lesson.md",
                    "en_source": "docs/en/lesson.md",
                }
            ]
            with (
                patch.object(check_docs, "ROOT", root),
                patch.object(check_docs, "load_curriculum", return_value=manifest),
                self.assertRaisesRegex(SystemExit, "English lesson links to Chinese"),
            ):
                check_docs.check()

    def test_scope_and_procedure_text_cannot_exist_only_inside_images(self):
        data = {
            "scope": "Local mechanism only",
            "procedures": [
                {
                    "steps": ["read", "compute", "commit", "retry"],
                    "state": "version",
                    "failure": "conflict",
                    "measure": "one winner",
                    "case": "v7 to v8",
                }
            ],
        }
        source = "Local mechanism only read compute commit retry version conflict one winner v7 to v8"
        self.assertEqual(check_docs.check_lesson_text(data, source), [])
        self.assertEqual(
            len(check_docs.check_lesson_text(data, "![Diagram](diagram.png)")), 2
        )


if __name__ == "__main__":
    unittest.main()
