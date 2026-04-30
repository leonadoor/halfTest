import logging
from datetime import datetime
from typing import List, Optional
from ..models.article import Article, FeedSource


class ArticleExtractor:
    """Extracts and normalizes article data from raw feed entries."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_articles(self, feed_data: dict, feed_source: FeedSource) -> List[Article]:
        """
        Convert raw feed entries into normalized Article objects.

        Args:
            feed_data: Parsed feed data dictionary
            feed_source: FeedSource object containing metadata

        Returns:
            List of normalized Article objects
        """
        articles = []
        entries = feed_data.get("entries", [])

        for entry in entries:
            article = self._extract_single_article(entry, feed_source)
            if article:
                articles.append(article)

        self.logger.info(f"Extracted {len(articles)} articles from {feed_source.name}")
        return articles

    def _extract_single_article(self, entry: dict, feed_source: FeedSource) -> Optional[Article]:
        """Extract a single article from a feed entry."""
        try:
            # Extract and validate required fields
            title = self._clean_text(entry.get("title", ""))
            link = self._clean_link(entry.get("link", ""))

            if not title or not link:
                self.logger.debug(f"Skipping entry with missing title or link from {feed_source.name}")
                return None

            # Extract optional fields
            summary = self._clean_text(entry.get("summary", ""))
            published_at = self._parse_publish_date(entry.get("published", ""))

            return Article(
                title=title,
                link=link,
                published_at=published_at,
                summary=summary,
                source_name=feed_source.name,
                source_url=feed_source.url,
                category=feed_source.category,
                priority=feed_source.priority
            )

        except Exception as e:
            self.logger.error(f"Error extracting article from {feed_source.name}: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        # Remove leading/trailing whitespace and normalize spaces
        return " ".join(text.strip().split())

    def _clean_link(self, link: str) -> str:
        """Clean and validate link."""
        if not link:
            return ""
        link = link.strip()
        # Basic validation - should start with http(s)://
        if link.startswith(("http://", "https://")):
            return link
        return ""

    def _parse_publish_date(self, date_str: str) -> Optional[datetime]:
        """Parse publish date string into datetime object."""
        if not date_str:
            return None

        try:
            # Try common date formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601
                "%Y-%m-%dT%H:%M:%SZ",     # ISO 8601 UTC
                "%a, %d %b %Y %H:%M:%S %z",  # RFC 2822
                "%Y-%m-%d %H:%M:%S",      # Standard format
            ]:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue

            # If all formats fail, log and return None
            self.logger.debug(f"Could not parse date: {date_str}")
            return None

        except Exception as e:
            self.logger.debug(f"Date parsing error for '{date_str}': {e}")
            return None