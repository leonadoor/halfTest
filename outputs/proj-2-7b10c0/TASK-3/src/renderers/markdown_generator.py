import logging
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
from ..models.article import Article


class MarkdownGenerator:
    """Generates formatted Markdown reports from article data."""

    def __init__(self, date_format: str = "%Y-%m-%d"):
        self.date_format = date_format
        self.logger = logging.getLogger(__name__)

    def generate_report(self, articles: List[Article], report_date: datetime = None) -> str:
        """
        Generate a complete Markdown report from articles.

        Args:
            articles: List of articles to include in the report
            report_date: Date for the report header (defaults to today)

        Returns:
            Formatted Markdown string
        """
        if report_date is None:
            report_date = datetime.now()

        # Group articles by category
        articles_by_category = self._group_by_category(articles)

        # Generate report sections
        report_parts = []

        # Header
        report_parts.append(self._generate_header(report_date))

        # Table of contents
        if articles_by_category:
            report_parts.append(self._generate_table_of_contents(articles_by_category))

        # Article sections
        for category, category_articles in articles_by_category.items():
            report_parts.append(self._generate_category_section(category, category_articles))

        # Footer
        report_parts.append(self._generate_footer())

        report = "\n".join(report_parts)
        self.logger.info(f"Generated report with {len(articles)} articles across {len(articles_by_category)} categories")
        return report

    def save_report(self, content: str, output_path: str) -> None:
        """
        Save the generated report to a file.

        Args:
            content: Markdown content to save
            output_path: Path where to save the file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info(f"Saved report to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save report to {output_path}: {e}")
            raise

    def _group_by_category(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """Group articles by their category."""
        categories = defaultdict(list)
        for article in articles:
            category = article.category or "Uncategorized"
            categories[category].append(article)

        # Sort articles within each category by priority and date
        for category in categories:
            categories[category].sort(key=lambda a: (
                -a.priority,
                a.published_at if a.published_at else datetime.min
            ), reverse=True)

        # Sort categories alphabetically for consistent output
        return dict(sorted(categories.items()))

    def _generate_header(self, report_date: datetime) -> str:
        """Generate the report header."""
        date_str = report_date.strftime(self.date_format)
        return f"# AI News Daily Digest - {date_str}\n"

    def _generate_table_of_contents(self, articles_by_category: Dict[str, List[Article]]) -> str:
        """Generate a table of contents."""
        toc_parts = ["## Table of Contents"]
        for category, articles in articles_by_category.items():
            count = len(articles)
            toc_parts.append(f"- [{category} ({count} articles)](#{category.lower().replace(' ', '-')})")
        return "\n".join(toc_parts) + "\n"

    def _generate_category_section(self, category: str, articles: List[Article]) -> str:
        """Generate a section for a specific category."""
        section_parts = [f"## {category}"]

        for article in articles:
            section_parts.append(self._format_article_entry(article))

        return "\n".join(section_parts) + "\n"

    def _format_article_entry(self, article: Article) -> str:
        """Format a single article as a markdown list item."""
        # Format title with link
        entry = f"- [{article.title}]({article.link})"

        # Add source and date information
        source_info = []
        if article.source_name:
            source_info.append(f"via {article.source_name}")

        if article.published_at:
            date_str = article.published_at.strftime("%Y-%m-%d %H:%M")
            source_info.append(f"on {date_str}")

        if source_info:
            entry += f" ({', '.join(source_info)})"

        # Add summary if available
        if article.summary:
            # Truncate long summaries
            summary = article.summary[:200] + "..." if len(article.summary) > 200 else article.summary
            entry += f"\n  > {summary}"

        return entry

    def _generate_footer(self) -> str:
        """Generate the report footer."""
        return f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by AI News Aggregator*"