#!/usr/bin/env python3
"""
AI News Aggregator - Main entry point

This script fetches AI news from configured RSS feeds, processes the content,
and generates a daily digest in Markdown format.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

# Add project roots to path for package imports.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.schedulers.job_runner import JobRunner
from src.utils.logger import setup_logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AI News Aggregator - Generate daily AI news digest")
    parser.add_argument(
        "--date",
        type=str,
        help="Target date for the report (YYYY-MM-DD format). Defaults to today.",
        default=None
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to feed configuration file",
        default=str(BASE_DIR / "config" / "feeds.yaml")
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for reports",
        default=str(BASE_DIR / "output" / "reports")
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Optional log file path",
        default=None
    )

    args = parser.parse_args()

    # Setup logging
    setup_logger("ai_news_aggregator", args.log_level, args.log_file)

    # Parse target date if provided
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD format.")
            sys.exit(1)

    # Initialize and run job
    try:
        job_runner = JobRunner(config_path=args.config, output_dir=args.output)
        stats = job_runner.run_daily_job(target_date)

        print(f"\nJob completed successfully!")
        print(f"Report saved to: {stats['report_path']}")
        print(f"Articles processed: {stats['final_articles']}")
        print(f"Feeds: {stats['successful_feeds']} successful, {stats['failed_feeds']} failed")

    except Exception as e:
        logging.error(f"Job failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
