#!/usr/bin/env python3
"""
Markdown Generator for AI News Aggregator

This module provides enhanced Markdown generation functionality specifically for TASK-4,
focusing on formatting news data with titles, links, summaries, and publication dates,
organized by date.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'TASK-3', 'src'))
from models.article import Article


class TASK4MarkdownGenerator:
    """
    Enhanced Markdown generator specifically designed for TASK-4 requirements.
    Formats news data with titles, links, summaries, and publication dates,
    organized chronologically.
    """

    def __init__(self, date_format: str = "%Y-%m-%d", time_format: str = "%H:%M"):
        self.date_format = date_format
        self.time_format = time_format
        self.logger = logging.getLogger(__name__)

    def generate_daily_report(self, articles: List[Article], report_date: datetime = None) -> str:
        """
        Generate a complete daily Markdown report with articles organized by date.

        Args:
            articles: List of articles to include
            report_date: Target date for the report (defaults to today)

        Returns:
            Formatted Markdown string
        """
        if report_date is None:
            report_date = datetime.now()

        self.logger.info(f"Generating daily report for {report_date.strftime(self.date_format)}")

        # Remove duplicates and sort articles
        unique_articles = self._remove_duplicates(articles)
        sorted_articles = self._sort_articles_by_date(unique_articles)

        # Group by publication date
        articles_by_date = self._group_by_publication_date(sorted_articles)

        # Generate report sections
        report_parts = []

        # Main header
        report_parts.append(self._generate_main_header(report_date))

        # Executive summary
        if sorted_articles:
            report_parts.append(self._generate_executive_summary(sorted_articles))

        # Articles by date
        for date_str, date_articles in articles_by_date.items():
            report_parts.append(self._generate_date_section(date_str, date_articles))

        # Statistics footer
        report_parts.append(self._generate_statistics_footer(sorted_articles, articles_by_date))

        report = "\n".join(report_parts)
        self.logger.info(f"Generated report with {len(sorted_articles)} articles")
        return report

    def generate_weekly_report(self, articles: List[Article], week_start: datetime = None) -> str:
        """
        Generate a weekly summary report.

        Args:
            articles: List of articles from the week
            week_start: Start of the week (defaults to current week)

        Returns:
            Formatted weekly Markdown report
        """
        if week_start is None:
            # Get current week start (Monday)
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())

        unique_articles = self._remove_duplicates(articles)
        sorted_articles = self._sort_articles_by_date(unique_articles)

        report_parts = []
        report_parts.append(f"# AI News Weekly Summary - Week of {week_start.strftime('%Y-%m-%d')}\n")

        # Group by category for weekly view
        articles_by_category = self._group_by_category(sorted_articles)

        for category, category_articles in articles_by_category.items():
            report_parts.append(f"## {category}\n")
            for article in category_articles:
                date_str = article.published_at.strftime(self.date_format) if article.published_at else "Unknown date"
                report_parts.append(f"- **{date_str}**: [{article.title}]({article.link})")
                if article.summary:
                    report_parts.append(f"  *{article.summary[:150]}...*\n")

        return "\n".join(report_parts)

    def save_report(self, content: str, output_path: str, ensure_unique: bool = True) -> str:
        """
        Save the report to a file with optional unique naming.

        Args:
            content: Markdown content to save
            output_path: Base path for the file
            ensure_unique: If True, add timestamp to avoid overwriting

        Returns:
            Actual path where the file was saved
        """
        try:
            final_path = output_path

            if ensure_unique:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base, ext = os.path.splitext(output_path)
                final_path = f"{base}_{timestamp}{ext}"

            # Ensure directory exists
            dir_path = os.path.dirname(final_path)
            if dir_path:  # Only create directory if path is specified
                os.makedirs(dir_path, exist_ok=True)

            with open(final_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Saved report to {final_path}")
            return final_path

        except Exception as e:
            self.logger.error(f"Failed to save report to {output_path}: {e}")
            raise

    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles based on URL."""
        seen_urls = set()
        unique_articles = []

        for article in articles:
            if article.link not in seen_urls:
                seen_urls.add(article.link)
                unique_articles.append(article)

        return unique_articles

    def _sort_articles_by_date(self, articles: List[Article]) -> List[Article]:
        """Sort articles by publication date (newest first)."""
        return sorted(
            articles,
            key=lambda a: a.published_at if a.published_at else datetime.min,
            reverse=True
        )

    def _group_by_publication_date(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """Group articles by their publication date."""
        groups = defaultdict(list)

        for article in articles:
            if article.published_at:
                date_str = article.published_at.strftime(self.date_format)
            else:
                date_str = "Unknown Date"

            groups[date_str].append(article)

        # Sort dates in descending order
        return dict(sorted(groups.items(), reverse=True))

    def _group_by_category(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """Group articles by category."""
        groups = defaultdict(list)

        for article in articles:
            category = article.category or "Uncategorized"
            groups[category].append(article)

        # Sort by category name
        return dict(sorted(groups.items()))

    def _generate_main_header(self, report_date: datetime) -> str:
        """Generate the main report header."""
        date_str = report_date.strftime(self.date_format)
        return f"# 🤖 AI News Daily Digest - {date_str}\n"

    def _generate_executive_summary(self, articles: List[Article]) -> str:
        """Generate an executive summary of the day's news."""
        summary_parts = ["## 📊 Executive Summary\n"]

        # Category breakdown
        by_category = self._group_by_category(articles)
        summary_parts.append("### Categories Covered:")
        for category, category_articles in by_category.items():
            summary_parts.append(f"- **{category}**: {len(category_articles)} articles")

        summary_parts.append(f"\n### Total Articles: {len(articles)}")
        summary_parts.append("---\n")

        return "\n".join(summary_parts)

    def _generate_date_section(self, date_str: str, articles: List[Article]) -> str:
        """Generate a section for articles from a specific date."""
        section_parts = [f"## 📅 {date_str}\n"]

        # Group articles by source within the date
        by_source = defaultdict(list)
        for article in articles:
            by_source[article.source_name].append(article)

        for source_name, source_articles in by_source.items():
            section_parts.append(f"### 📰 {source_name}\n")

            for article in source_articles:
                # Format article entry with all required fields
                time_str = article.published_at.strftime(self.time_format) if article.published_at else "N/A"
                entry = f"- **[{article.title}]({article.link})**"
                entry += f"\n  - **Time**: {time_str}"
                entry += f"\n  - **Category**: {article.category}"

                if article.summary:
                    # Format summary with proper indentation
                    summary_lines = article.summary.strip().split('\n')
                    formatted_summary = '> ' + '\n> '.join(summary_lines[:3])  # Limit to first 3 lines
                    if len(summary_lines) > 3:
                        formatted_summary += "\n> ..."
                    entry += f"\n  - **Summary**:\n{formatted_summary}"

                section_parts.append(entry + "\n")

        return "\n".join(section_parts) + "\n"

    def _generate_statistics_footer(self, articles: List[Article], articles_by_date: Dict) -> str:
        """Generate a footer with statistics."""
        footer_parts = ["---\n", "## 📈 Report Statistics\n"]

        footer_parts.append(f"- **Total Articles**: {len(articles)}")
        footer_parts.append(f"- **Date Range**: {len(articles_by_date)} days")
        footer_parts.append(f"- **Sources**: {len(set(a.source_name for a in articles))}")

        # Category breakdown
        categories = defaultdict(int)
        for article in articles:
            categories[article.category] += 1

        footer_parts.append("\n### Categories Breakdown:")
        for category, count in sorted(categories.items()):
            footer_parts.append(f"- {category}: {count} articles")

        # Generation timestamp
        footer_parts.append(f"\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(footer_parts)


def main():
    """CLI entry point for TASK-4 Markdown generator."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="TASK-4: Enhanced Markdown Generator for AI News")
    parser.add_argument("--input", "-i", help="JSON file containing articles", required=True)
    parser.add_argument("--output", "-o", help="Output Markdown file path", default="output.md")
    parser.add_argument("--date", help="Report date (YYYY-MM-DD)", default=None)
    parser.add_argument("--weekly", help="Generate weekly report instead of daily", action="store_true")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    try:
        # Load articles from JSON
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)

        articles = []
        for item in data.get("articles", []):
            article = Article(
                title=item.get("title", ""),
                link=item.get("link", ""),
                published_at=datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None,
                summary=item.get("summary", ""),
                source_name=item.get("source_name", ""),
                source_url=item.get("source_url", ""),
                category=item.get("category", ""),
                priority=item.get("priority", 5)
            )
            articles.append(article)

        # Parse report date
        report_date = None
        if args.date:
            report_date = datetime.strptime(args.date, "%Y-%m-%d")

        # Generate report
        generator = TASK4MarkdownGenerator()

        if args.weekly:
            content = generator.generate_weekly_report(articles, report_date)
        else:
            content = generator.generate_daily_report(articles, report_date)

        # Save report
        output_path = generator.save_report(content, args.output)
        print(f"Report saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    from datetime import timedelta
    exit(main())