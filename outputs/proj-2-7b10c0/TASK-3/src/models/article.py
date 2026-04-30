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


@dataclass
class FeedSource:
    name: str
    url: str
    category: str
    priority: int
    enabled: bool
    update_hours: int