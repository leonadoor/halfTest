from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import requests

from helpers import build_article, build_feed_source, workspace_tempdir
from src.clients.rss_client import RSSClient
from src.parsers.feed_parser import FeedParser
from src.processors.article_extractor import ArticleExtractor
from src.processors.article_filter import ArticleFilter
from src.processors.deduplicator import Deduplicator
from src.renderers.markdown_generator import MarkdownGenerator
from src.schedulers.job_runner import JobRunner


VALID_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>AI Feed</title>
    <link>https://example.com</link>
    <description>Latest AI news</description>
    <item>
      <title>Alpha</title>
      <link>https://example.com/alpha</link>
      <pubDate>Tue, 30 Apr 2026 08:00:00 +0000</pubDate>
      <description>Alpha summary</description>
      <guid>alpha-1</guid>
      <author>Reporter</author>
    </item>
    <item>
      <title>Beta</title>
      <link>https://example.com/beta</link>
      <description>Beta summary</description>
    </item>
  </channel>
</rss>
"""


class RSSClientTests(unittest.TestCase):
    def test_fetch_feed_returns_text_on_success(self):
        client = RSSClient(timeout=5, max_retries=2)
        response = mock.Mock(text="<xml />")
        response.raise_for_status.return_value = None

        with mock.patch.object(client.session, "get", return_value=response) as get_mock:
            result = client.fetch_feed("https://example.com/rss.xml")

        self.assertEqual(result, "<xml />")
        get_mock.assert_called_once_with("https://example.com/rss.xml", timeout=5)

    def test_fetch_feed_retries_and_returns_none_after_failures(self):
        client = RSSClient(timeout=5, max_retries=3)

        with mock.patch.object(
            client.session,
            "get",
            side_effect=requests.RequestException("boom"),
        ) as get_mock, mock.patch("src.clients.rss_client.sleep") as sleep_mock:
            result = client.fetch_feed("https://example.com/rss.xml")

        self.assertIsNone(result)
        self.assertEqual(get_mock.call_count, 3)
        self.assertEqual(sleep_mock.call_args_list, [mock.call(1), mock.call(2)])


class FeedParserTests(unittest.TestCase):
    def test_parse_feed_extracts_metadata_and_entries(self):
        parser = FeedParser()

        parsed = parser.parse_feed(VALID_RSS, "https://example.com/rss.xml")

        self.assertEqual(parsed["title"], "AI Feed")
        self.assertEqual(parsed["link"], "https://example.com")
        self.assertEqual(len(parsed["entries"]), 2)
        self.assertEqual(parsed["entries"][0]["title"], "Alpha")
        self.assertEqual(parser.get_entry_count(parsed), 2)

    def test_parse_feed_returns_empty_entries_for_invalid_content(self):
        parser = FeedParser()

        parsed = parser.parse_feed("not xml", "https://example.com/bad.xml")

        self.assertIn("entries", parsed)
        self.assertEqual(parsed["entries"], [])


class ArticleExtractorTests(unittest.TestCase):
    def setUp(self):
        self.extractor = ArticleExtractor()
        self.feed_source = build_feed_source(priority=8)

    def test_extract_articles_skips_invalid_entries_and_parses_fields(self):
        feed_data = {
            "entries": [
                {
                    "title": "  New model launch  ",
                    "link": " https://example.com/story ",
                    "summary": "  summary text  ",
                    "published": "Tue, 30 Apr 2026 08:00:00 +0000",
                },
                {
                    "title": "Missing link",
                    "link": "mailto:test@example.com",
                    "summary": "ignored",
                    "published": "",
                },
            ]
        }

        articles = self.extractor.extract_articles(feed_data, self.feed_source)

        self.assertEqual(len(articles), 1)
        article = articles[0]
        self.assertEqual(article.title, "New model launch")
        self.assertEqual(article.link, "https://example.com/story")
        self.assertEqual(article.summary, "summary text")
        self.assertEqual(article.priority, 8)
        self.assertIsNotNone(article.published_at)

    def test_parse_publish_date_supports_iso_and_unknown(self):
        iso_dt = self.extractor._parse_publish_date("2026-04-30T08:15:00+0000")
        bad_dt = self.extractor._parse_publish_date("unknown")

        self.assertEqual(iso_dt.year, 2026)
        self.assertIsNone(bad_dt)


class ArticleFilterTests(unittest.TestCase):
    def test_filter_articles_applies_time_window_and_summary_rules(self):
        reference_time = datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc)
        filterer = ArticleFilter(time_window_hours=24, require_summary=True)
        articles = [
            build_article(
                title="Recent",
                link="https://example.com/recent",
                published_at=reference_time - timedelta(hours=2),
                summary="has summary",
            ),
            build_article(
                title="Old",
                link="https://example.com/old",
                published_at=reference_time - timedelta(hours=30),
                summary="has summary",
            ),
            build_article(
                title="No summary",
                link="https://example.com/no-summary",
                published_at=reference_time - timedelta(hours=1),
                summary="",
            ),
            build_article(
                title="No date",
                link="https://example.com/no-date",
                published_at=None,
                summary="kept",
            ),
        ]

        filtered = filterer.filter_articles(articles, reference_time)

        self.assertEqual([article.title for article in filtered], ["Recent", "No date"])


class DeduplicatorTests(unittest.TestCase):
    def test_deduplicate_prefers_high_priority_and_similar_titles(self):
        deduplicator = Deduplicator()
        base_time = datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc)
        articles = [
            build_article(
                title="Breaking: OpenAI ships a new model",
                link="https://example.com/a",
                priority=5,
                published_at=base_time - timedelta(hours=1),
                source_name="Low Priority Feed",
            ),
            build_article(
                title="OpenAI ships a new model",
                link="https://example.com/a",
                priority=10,
                published_at=base_time - timedelta(hours=2),
                source_name="High Priority Feed",
            ),
            build_article(
                title="Update: OpenAI ships a new model",
                link="https://example.com/b",
                priority=9,
                published_at=base_time,
                source_name="Another Feed",
            ),
        ]

        unique_articles = deduplicator.deduplicate(articles)

        self.assertEqual(len(unique_articles), 1)
        self.assertEqual(unique_articles[0].source_name, "High Priority Feed")


class MarkdownGeneratorTests(unittest.TestCase):
    def test_generate_report_creates_toc_sections_and_truncated_summary(self):
        generator = MarkdownGenerator()
        long_summary = "x" * 220
        articles = [
            build_article(
                title="Model update",
                link="https://example.com/model",
                category="Research",
                source_name="OpenAI Blog",
                published_at=datetime(2026, 4, 30, 9, 0),
                summary=long_summary,
            )
        ]

        report = generator.generate_report(articles, datetime(2026, 4, 30))

        self.assertIn("# AI News Daily Digest - 2026-04-30", report)
        self.assertIn("## Table of Contents", report)
        self.assertIn("## Research", report)
        self.assertIn("via OpenAI Blog", report)
        self.assertIn(("x" * 200) + "...", report)

    def test_save_report_writes_file(self):
        generator = MarkdownGenerator()
        with workspace_tempdir("markdown_save") as temp_dir:
            output_path = Path(temp_dir) / "report.md"
            generator.save_report("content", str(output_path))

            self.assertEqual(output_path.read_text(encoding="utf-8"), "content")


class JobRunnerIntegrationTests(unittest.TestCase):
    def test_run_daily_job_with_stubbed_dependencies_generates_report(self):
        with workspace_tempdir("job_runner") as temp_path:
            runner = JobRunner(config_path=str(temp_path / "feeds.yaml"), output_dir=str(temp_path / "reports"))
            article = build_article(
                title="Integrated article",
                link="https://example.com/integrated",
                summary="pipeline summary",
                published_at=datetime(2026, 4, 30, 10, 0, tzinfo=timezone.utc),
                priority=7,
            )
            feed_source = build_feed_source(name="Feed A", priority=7)

            with mock.patch.object(runner, "_load_feed_sources", return_value=[feed_source]), mock.patch.object(
                runner.rss_client, "fetch_feed", return_value="<rss />"
            ), mock.patch.object(
                runner.feed_parser,
                "parse_feed",
                return_value={"entries": [{"title": "Integrated article"}]},
            ), mock.patch.object(
                runner.article_extractor,
                "extract_articles",
                return_value=[article],
            ):
                stats = runner.run_daily_job(datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc))

            report_path = Path(stats["report_path"])
            self.assertTrue(report_path.exists())
            self.assertEqual(stats["successful_feeds"], 1)
            self.assertEqual(stats["failed_feeds"], 0)
            self.assertEqual(stats["final_articles"], 1)
            self.assertIn("Integrated article", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
