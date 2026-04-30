import logging
from datetime import datetime
from typing import List, Dict, Any
from ..models.article import FeedSource
from ..clients.rss_client import RSSClient
from ..parsers.feed_parser import FeedParser
from ..processors.article_extractor import ArticleExtractor
from ..processors.article_filter import ArticleFilter
from ..processors.deduplicator import Deduplicator
from ..renderers.markdown_generator import MarkdownGenerator


class JobRunner:
    """Coordinates the end-to-end pipeline for AI news aggregation."""

    def __init__(self, config_path: str, output_dir: str = "output/reports"):
        self.config_path = config_path
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.rss_client = RSSClient()
        self.feed_parser = FeedParser()
        self.article_extractor = ArticleExtractor()
        self.article_filter = ArticleFilter()
        self.deduplicator = Deduplicator()
        self.markdown_generator = MarkdownGenerator()

    def run_daily_job(self, target_date: datetime = None) -> Dict[str, Any]:
        """
        Execute the complete news aggregation pipeline.

        Args:
            target_date: Optional target date for the report (defaults to today)

        Returns:
            Dictionary containing execution statistics
        """
        if target_date is None:
            target_date = datetime.now()

        self.logger.info(f"Starting AI news aggregation job for {target_date.strftime('%Y-%m-%d')}")

        # Load feed sources
        feed_sources = self._load_feed_sources()
        self.logger.info(f"Loaded {len(feed_sources)} feed sources")

        all_articles = []
        successful_feeds = 0
        failed_feeds = 0

        # Process each feed
        for feed_source in feed_sources:
            if not feed_source.enabled:
                self.logger.debug(f"Skipping disabled feed: {feed_source.name}")
                continue

            try:
                articles = self._process_feed(feed_source)
                all_articles.extend(articles)
                successful_feeds += 1
            except Exception as e:
                self.logger.error(f"Failed to process feed {feed_source.name}: {e}")
                failed_feeds += 1

        # Apply processing pipeline
        self.logger.info(f"Processing {len(all_articles)} total articles")

        # Filter articles
        filtered_articles = self.article_filter.filter_articles(all_articles, target_date)
        self.logger.info(f"Filtered to {len(filtered_articles)} articles")

        # Deduplicate articles
        unique_articles = self.deduplicator.deduplicate(filtered_articles)
        self.logger.info(f"Deduplicated to {len(unique_articles)} articles")

        # Generate report
        report_content = self.markdown_generator.generate_report(unique_articles, target_date)

        # Save report
        report_path = self._get_report_path(target_date)
        self.markdown_generator.save_report(report_content, report_path)

        # Prepare execution statistics
        stats = {
            "execution_time": datetime.now().isoformat(),
            "target_date": target_date.strftime("%Y-%m-%d"),
            "total_feeds": len(feed_sources),
            "successful_feeds": successful_feeds,
            "failed_feeds": failed_feeds,
            "total_articles": len(all_articles),
            "filtered_articles": len(filtered_articles),
            "final_articles": len(unique_articles),
            "report_path": str(report_path)
        }

        self.logger.info(f"Job completed successfully. Statistics: {stats}")
        return stats

    def _load_feed_sources(self) -> List[FeedSource]:
        """Load feed sources from configuration file."""
        import yaml
        from pathlib import Path

        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                self.logger.error(f"Config file not found: {self.config_path}")
                return []

            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            feed_sources = []
            feeds_config = config.get("feeds", [])

            for feed_data in feeds_config:
                feed_source = FeedSource(
                    name=feed_data.get("name", ""),
                    url=feed_data.get("url", ""),
                    category=feed_data.get("category", "Uncategorized"),
                    priority=feed_data.get("priority", 5),
                    enabled=feed_data.get("enabled", True),
                    update_hours=feed_data.get("update_hours", 24)
                )
                feed_sources.append(feed_source)

            return feed_sources

        except Exception as e:
            self.logger.error(f"Failed to load feed sources: {e}")
            return []

    def _process_feed(self, feed_source: FeedSource) -> List:
        """Process a single feed source."""
        self.logger.info(f"Processing feed: {feed_source.name}")

        # Fetch feed content
        content = self.rss_client.fetch_feed(feed_source.url)
        if not content:
            raise Exception(f"Failed to fetch content for {feed_source.name}")

        # Parse feed
        feed_data = self.feed_parser.parse_feed(content, feed_source.url)

        # Extract articles
        articles = self.article_extractor.extract_articles(feed_data, feed_source)

        self.logger.info(f"Extracted {len(articles)} articles from {feed_source.name}")
        return articles

    def _get_report_path(self, target_date: datetime) -> Path:
        """Generate the report file path based on date."""
        from pathlib import Path

        date_str = target_date.strftime("%Y-%m-%d")
        filename = f"ai_news_{date_str}.md"

        # Ensure output directory exists
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        return output_path / filename