import logging
import hashlib
from datetime import datetime
from typing import List, Set, Dict
from ..models.article import Article


class Deduplicator:
    """Removes duplicate articles from multiple feeds based on URL and title similarity."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """
        Remove duplicate articles, keeping the highest priority version.

        Args:
            articles: List of articles to deduplicate

        Returns:
            Deduplicated list of articles
        """
        # Group articles by URL first
        url_groups = self._group_by_url(articles)

        # For each URL, select the best article (highest priority)
        unique_articles = []
        for url, url_articles in url_groups.items():
            best_article = self._select_best_article(url_articles, key="URL")
            if best_article:
                unique_articles.append(best_article)

        # Now check for title-based near-duplicates among the unique URLs
        final_articles = self._deduplicate_by_title(unique_articles)

        self.logger.info(f"Deduplicated {len(articles)} articles down to {len(final_articles)}")
        return final_articles

    def _group_by_url(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """Group articles by their URL."""
        groups = {}
        for article in articles:
            if article.link not in groups:
                groups[article.link] = []
            groups[article.link].append(article)
        return groups

    def _select_best_article(self, articles: List[Article], key: str = "") -> Article:
        """Select the best article from a group based on priority."""
        if not articles:
            return None

        # Sort by priority (higher priority first), then by published date (newer first)
        sorted_articles = sorted(
            articles,
            key=lambda a: (a.priority, a.published_at if a.published_at else datetime.min),
            reverse=True
        )

        best_article = sorted_articles[0]

        if len(articles) > 1:
            self.logger.debug(f"Selected article from {best_article.source_name} "
                            f"(priority={best_article.priority}) over {[a.source_name for a in articles[1:]]} "
                            f"for {key}: {best_article.link[:50]}...")

        return best_article

    def _deduplicate_by_title(self, articles: List[Article]) -> List[Article]:
        """Remove near-duplicate articles based on title similarity."""
        if len(articles) < 2:
            return articles

        # Group by normalized title hash
        title_groups = {}
        for article in articles:
            title_hash = self._get_title_hash(article.title)
            if title_hash not in title_groups:
                title_groups[title_hash] = []
            title_groups[title_hash].append(article)

        # For groups with multiple articles, select the best one
        final_articles = []
        for title_hash, group_articles in title_groups.items():
            if len(group_articles) == 1:
                final_articles.extend(group_articles)
            else:
                # Check if these are truly duplicates (similar titles)
                if self._are_titles_similar([a.title for a in group_articles]):
                    best_article = self._select_best_article(group_articles, key="title")
                    if best_article:
                        final_articles.append(best_article)
                else:
                    # Different articles with similar hash, keep all
                    final_articles.extend(group_articles)

        return final_articles

    def _get_title_hash(self, title: str) -> str:
        """Generate a hash for title-based deduplication."""
        # Normalize title: lowercase, remove common words, extra spaces
        normalized = self._normalize_title(title)
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        if not title:
            return ""

        # Convert to lowercase
        title = title.lower()

        # Remove common prefixes/suffixes that don't affect meaning
        noise_words = ["the ", "a ", "an ", "breaking: ", "update: ", "news: "]
        for noise in noise_words:
            if title.startswith(noise):
                title = title[len(noise):]

        # Remove extra whitespace and punctuation
        title = " ".join(title.split())

        return title.strip()

    def _are_titles_similar(self, titles: List[str], similarity_threshold: float = 0.8) -> bool:
        """Check if titles are similar enough to be considered duplicates."""
        if len(titles) < 2:
            return False

        # Normalize all titles
        normalized_titles = [self._normalize_title(title) for title in titles]

        # Compare first title with others
        base_title = normalized_titles[0]
        if not base_title:
            return False

        for other_title in normalized_titles[1:]:
            if not other_title:
                continue

            # Calculate similarity based on common words
            base_words = set(base_title.split())
            other_words = set(other_title.split())

            if not base_words or not other_words:
                continue

            # Calculate Jaccard similarity
            intersection = len(base_words.intersection(other_words))
            union = len(base_words.union(other_words))
            similarity = intersection / union if union > 0 else 0

            if similarity < similarity_threshold:
                return False

        return True