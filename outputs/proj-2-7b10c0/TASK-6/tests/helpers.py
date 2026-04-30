from __future__ import annotations

import importlib.util
import shutil
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path


TASK6_DIR = Path(__file__).resolve().parent.parent
TASK3_DIR = TASK6_DIR.parent / "TASK-3"
TASK3_SRC_DIR = TASK3_DIR / "src"
TASK4_DIR = TASK6_DIR.parent / "TASK-4"

for path in (TASK3_DIR, TASK3_SRC_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def load_task4_module():
    module_path = TASK4_DIR / "markdown_generator.py"
    spec = importlib.util.spec_from_file_location("task4_markdown_generator", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def build_article(
    *,
    title: str = "AI title",
    link: str = "https://example.com/article",
    published_at: datetime | None = None,
    summary: str = "Summary",
    source_name: str = "Example Source",
    source_url: str = "https://example.com/feed",
    category: str = "Research",
    priority: int = 5,
):
    from src.models.article import Article

    return Article(
        title=title,
        link=link,
        published_at=published_at,
        summary=summary,
        source_name=source_name,
        source_url=source_url,
        category=category,
        priority=priority,
    )


def build_feed_source(
    *,
    name: str = "Example Feed",
    url: str = "https://example.com/rss.xml",
    category: str = "Research",
    priority: int = 5,
    enabled: bool = True,
    update_hours: int = 24,
):
    from src.models.article import FeedSource

    return FeedSource(
        name=name,
        url=url,
        category=category,
        priority=priority,
        enabled=enabled,
        update_hours=update_hours,
    )


def recent_datetime(hours_ago: int = 1) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours_ago)


@contextmanager
def workspace_tempdir(prefix: str):
    base_dir = TASK6_DIR / ".tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"{prefix}_{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
