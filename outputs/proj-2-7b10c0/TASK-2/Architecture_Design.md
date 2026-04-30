# AI News Aggregator Python Script Architecture

## 1. Goal

Build a daily Python job that fetches predefined AI-news RSS feeds, extracts normalized article data, filters and deduplicates entries, and renders the final daily digest as a Markdown file.

This design consumes the validated feed list from `outputs/proj-2-7b10c0/TASK-1/`.

## 2. High-Level Flow

1. Load RSS source configuration.
2. Pull all enabled feeds with retry and timeout controls.
3. Parse feed content into raw entries.
4. Normalize fields into a unified article schema.
5. Filter invalid, outdated, or irrelevant entries.
6. Deduplicate entries across different feeds.
7. Group articles by source category.
8. Generate a Markdown daily report.
9. Save report and execution logs.

## 3. Suggested Project Structure

```text
ai_news_aggregator/
  main.py
  config/
    feeds.yaml
    scheduler.example.yaml
  src/
    clients/
      rss_client.py
    parsers/
      feed_parser.py
    processors/
      article_extractor.py
      article_filter.py
      deduplicator.py
    renderers/
      markdown_generator.py
    schedulers/
      job_runner.py
    models/
      article.py
      feed_source.py
    utils/
      logger.py
      time_utils.py
      hash_utils.py
  output/
    reports/
  logs/
```

## 4. Module Responsibilities

### `config/feeds.yaml`
- Stores validated RSS source list from TASK-1.
- Defines feed URL, category, priority, polling interval, and enabled flag.

### `src/clients/rss_client.py`
- Sends HTTP requests to RSS endpoints.
- Applies timeout, retry, and user-agent settings.
- Returns raw XML or Atom payload.

### `src/parsers/feed_parser.py`
- Parses RSS/Atom content with `feedparser`.
- Converts heterogeneous feed structures into raw Python dictionaries.
- Preserves source metadata for downstream processing.

### `src/processors/article_extractor.py`
- Maps raw feed entries to a standard `Article` model.
- Extracts `title`, `link`, `published_at`, `summary`, `source_name`, and `category`.
- Fills missing fields with safe defaults when possible.

### `src/processors/article_filter.py`
- Removes entries with missing title or link.
- Keeps only items inside the configured time window, such as the last 24 hours.
- Applies optional keyword-based relevance filters.

### `src/processors/deduplicator.py`
- Deduplicates by canonical URL first.
- Falls back to normalized title hash for near-duplicates.
- Keeps the entry from the higher-priority source when duplicates conflict.

### `src/renderers/markdown_generator.py`
- Groups articles by category or source.
- Renders a Markdown digest with date header, section titles, and bullet links.
- Produces deterministic output so scheduled runs are easy to diff.

### `src/schedulers/job_runner.py`
- Exposes a callable `run_daily_job()` entrypoint.
- Coordinates the end-to-end pipeline.
- Returns execution statistics for logs and observability.

### `main.py`
- CLI entrypoint for local execution and scheduler integration.
- Supports direct run modes such as `python main.py --date 2026-04-30`.

## 5. Core Data Model

### `Article`

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Article:
    title: str
    link: str
    published_at: datetime | None
    summary: str
    source_name: str
    source_url: str
    category: str
    priority: int
```

### `FeedSource`

```python
from dataclasses import dataclass

@dataclass
class FeedSource:
    name: str
    url: str
    category: str
    priority: int
    enabled: bool
    update_hours: int
```

## 6. End-to-End Runtime Sequence

1. `main.py` loads feed definitions.
2. `job_runner.py` loops through enabled feeds.
3. `rss_client.py` downloads feed content.
4. `feed_parser.py` parses each document.
5. `article_extractor.py` normalizes entries into `Article` objects.
6. `article_filter.py` keeps recent and valid news only.
7. `deduplicator.py` removes overlap.
8. `markdown_generator.py` renders the final report.
9. The report is written to `output/reports/ai_news_YYYY-MM-DD.md`.

## 7. Error-Handling Strategy

- A single feed failure must not stop the whole job.
- Network failures use up to 3 retries with exponential backoff.
- Parse failures are logged with source name and URL.
- Empty feeds are treated as warnings, not fatal errors.
- Final job status should include successful-feed count and failed-feed count.

## 8. Technology Choices

- RSS/Atom parsing: `feedparser`
- HTTP client: `requests`
- Scheduling: OS cron / Windows Task Scheduler, with optional in-process `schedule`
- Config format: YAML
- Logging: Python `logging`

## 9. Output Contract

Final Markdown example:

```markdown
# AI News Daily Digest - 2026-04-30

## Frontline Research
- [OpenAI publishes new model update](https://example.com)
- [New paper in arXiv cs.AI](https://example.com)

## Industry News
- [TechCrunch covers major AI release](https://example.com)
```

## 10. Design Decisions

- Keep fetching, parsing, filtering, and rendering separate so each unit is independently testable.
- Use configuration files for feed definitions so source updates do not require code edits.
- Keep scheduling outside business logic so the same pipeline can run locally, in CI, or on a server.
