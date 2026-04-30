import logging
from datetime import datetime, timedelta, timezone
from typing import List
from ..models.article import Article


class ArticleFilter:
    """Filters articles based on various criteria like time window and validity."""

    def __init__(self, time_window_hours: int = 24, require_summary: bool = False):
        self.time_window_hours = time_window_hours
        self.require_summary = require_summary
        self.logger = logging.getLogger(__name__)

    def filter_articles(self, articles: List[Article], reference_time: datetime = None) -> List[Article]:
        """
        Apply all filters to the article list.

        Args:
            articles: List of articles to filter
            reference_time: Reference time for time-based filtering (defaults to now)

        Returns:
            Filtered list of articles
        """
        if reference_time is None:
            reference_time = datetime.now()

        filtered_articles = articles.copy()

        # Apply various filters
        filtered_articles = self._filter_invalid_entries(filtered_articles)
        filtered_articles = self._filter_by_time_window(filtered_articles, reference_time)
        filtered_articles = self._filter_by_summary(filtered_articles)

        self.logger.info(f"Filtered {len(articles)} articles down to {len(filtered_articles)}")
        return filtered_articles

    def _filter_invalid_entries(self, articles: List[Article]) -> List[Article]:
        """Remove articles with missing required fields."""
        valid_articles = []
        for article in articles:
            if self._is_valid_article(article):
                valid_articles.append(article)
            else:
                self.logger.debug(f"Removed invalid article: {article.title[:50]}...")
        return valid_articles

    def _is_valid_article(self, article: Article) -> bool:
        """Check if an article has all required fields."""
        return bool(article.title and article.link)

    def _filter_by_time_window(self, articles: List[Article], reference_time: datetime) -> List[Article]:
        """Keep only articles within the configured time window."""
        if self.time_window_hours <= 0:
            return articles

        normalized_reference_time = self._normalize_datetime(reference_time)
        cutoff_time = normalized_reference_time - timedelta(hours=self.time_window_hours)
        recent_articles = []

        for article in articles:
            if article.published_at:
                published_at = self._normalize_datetime(article.published_at)
                if published_at >= cutoff_time:
                    recent_articles.append(article)
                else:
                    self.logger.debug(f"Article too old: {article.title[:50]}... ({article.published_at})")
            else:
                # Articles without publish date are included by default
                recent_articles.append(article)

        return recent_articles

    def _normalize_datetime(self, value: datetime) -> datetime:
        """Convert datetimes into naive UTC values so comparisons are stable."""
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def _filter_by_summary(self, articles: List[Article]) -> List[Article]:
        """Filter articles based on summary requirements."""
        if not self.require_summary:
            return articles

        articles_with_summary = []
        for article in articles:
            if article.summary and len(article.summary.strip()) > 0:
                articles_with_summary.append(article)
            else:
                self.logger.debug(f"Article without summary: {article.title[:50]}...")

        return articles_with_summary
