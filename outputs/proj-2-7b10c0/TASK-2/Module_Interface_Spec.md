# Module Interface Specification

## 1. RSS Client

```python
def fetch_feed(url: str, timeout: int = 15, retries: int = 3) -> str:
    """Return raw RSS/Atom text."""
```

Inputs:
- Feed URL
- Timeout and retry settings

Outputs:
- Raw XML string

Failure behavior:
- Raises a custom `FeedFetchError` after retries are exhausted

## 2. Feed Parser

```python
def parse_feed(raw_content: str, source_name: str) -> list[dict]:
    """Convert feed XML into raw entry dictionaries."""
```

Inputs:
- Raw XML/Atom content
- Source name for metadata tagging

Outputs:
- List of raw entry dictionaries

## 3. Article Extractor

```python
def extract_articles(entries: list[dict], source: "FeedSource") -> list["Article"]:
    """Normalize feed entries into Article objects."""
```

Normalization rules:
- `title` is stripped text
- `link` is canonicalized when possible
- `published_at` is parsed to timezone-aware datetime when available
- Missing summaries default to empty string

## 4. Article Filter

```python
def filter_articles(
    articles: list["Article"],
    lookback_hours: int = 24,
    keywords: list[str] | None = None,
) -> list["Article"]:
    """Keep only relevant recent articles."""
```

Rules:
- Reject blank title or blank link
- Reject entries older than the lookback window
- Optionally require title or summary to contain configured keywords

## 5. Deduplicator

```python
def deduplicate_articles(articles: list["Article"]) -> list["Article"]:
    """Return unique articles ordered by priority and publish time."""
```

Rules:
- Unique key 1: normalized URL
- Unique key 2: lowercase title hash
- Winner selection: higher source priority, then newer publish time

## 6. Markdown Generator

```python
def generate_markdown(report_date: str, articles: list["Article"]) -> str:
    """Render the daily digest as Markdown."""
```

Expected sections:
- Title and generation time
- Category-based article groups
- Per-entry bullet with title and link
- Optional short summary line

## 7. Job Runner

```python
def run_daily_job(report_date: str | None = None) -> dict:
    """Execute the full pipeline and return run statistics."""
```

Return payload example:

```python
{
    "report_date": "2026-04-30",
    "feeds_total": 10,
    "feeds_succeeded": 9,
    "feeds_failed": 1,
    "articles_before_dedup": 67,
    "articles_after_dedup": 43,
    "report_path": "output/reports/ai_news_2026-04-30.md",
}
```

## 8. Persistence Interface

```python
def save_report(markdown_text: str, report_date: str, output_dir: str = "output/reports") -> str:
    """Write the Markdown file and return its path."""
```

Requirements:
- Create missing directories automatically
- Use UTF-8 encoding
- Return absolute or project-relative output path
