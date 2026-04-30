from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from helpers import build_article, load_task4_module, workspace_tempdir


task4_module = load_task4_module()
TASK4MarkdownGenerator = task4_module.TASK4MarkdownGenerator


class TASK4MarkdownGeneratorTests(unittest.TestCase):
    def test_generate_daily_report_groups_by_date_and_removes_duplicate_urls(self):
        generator = TASK4MarkdownGenerator()
        articles = [
            build_article(
                title="Alpha",
                link="https://example.com/shared",
                published_at=datetime(2026, 4, 30, 8, 0, tzinfo=timezone.utc),
                summary="line1\nline2\nline3\nline4",
                source_name="OpenAI Blog",
            ),
            build_article(
                title="Alpha duplicate",
                link="https://example.com/shared",
                published_at=datetime(2026, 4, 30, 7, 0, tzinfo=timezone.utc),
                summary="ignored duplicate",
                source_name="OpenAI Blog",
            ),
            build_article(
                title="Beta",
                link="https://example.com/beta",
                published_at=datetime(2026, 4, 29, 9, 30, tzinfo=timezone.utc),
                summary="summary beta",
                source_name="MIT Tech Review",
                category="Industry",
            ),
        ]

        report = generator.generate_daily_report(articles, datetime(2026, 4, 30, 12, 0))

        self.assertIn("# 🤖 AI News Daily Digest - 2026-04-30", report)
        self.assertIn("## 📅 2026-04-30", report)
        self.assertIn("## 📅 2026-04-29", report)
        self.assertEqual(report.count("https://example.com/shared"), 1)
        self.assertIn("> line1", report)
        self.assertIn("> ...", report)

    def test_generate_weekly_report_and_save_report(self):
        generator = TASK4MarkdownGenerator()
        articles = [
            build_article(
                title="Weekly article",
                link="https://example.com/weekly",
                published_at=datetime(2026, 4, 28, 8, 0, tzinfo=timezone.utc),
                summary="summary",
                category="Research",
            )
        ]

        weekly = generator.generate_weekly_report(articles, datetime(2026, 4, 27))
        self.assertIn("# AI News Weekly Summary - Week of 2026-04-27", weekly)
        self.assertIn("## Research", weekly)

        with workspace_tempdir("task4_save") as temp_dir:
            output = Path(temp_dir) / "weekly.md"
            saved_path = generator.save_report(weekly, str(output), ensure_unique=False)

            self.assertEqual(saved_path, str(output))
            self.assertEqual(output.read_text(encoding="utf-8"), weekly)


if __name__ == "__main__":
    unittest.main()
