import feedparser
import logging
from typing import List, Dict, Any


class FeedParser:
    """Parser for RSS/Atom feeds using feedparser library."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_feed(self, content: str, source_url: str = "") -> Dict[str, Any]:
        """
        Parse RSS/Atom content into a structured dictionary.

        Args:
            content: Raw XML/Atom content as string
            source_url: Optional source URL for logging

        Returns:
            Dictionary containing feed metadata and entries
        """
        try:
            self.logger.debug(f"Parsing feed content from {source_url or 'unknown source'}")
            parsed = feedparser.parse(content)

            if parsed.bozo:
                # Handle parsing errors
                error_msg = parsed.bozo_exception.getMessage() if parsed.bozo_exception else "Unknown parsing error"
                self.logger.warning(f"Feed parsing warning for {source_url}: {error_msg}")

            # Extract feed metadata
            feed_info = {
                "title": getattr(parsed.feed, "title", ""),
                "link": getattr(parsed.feed, "link", ""),
                "description": getattr(parsed.feed, "description", ""),
                "entries": []
            }

            # Extract entries
            for entry in parsed.entries:
                entry_data = {
                    "title": getattr(entry, "title", ""),
                    "link": getattr(entry, "link", ""),
                    "published": getattr(entry, "published", ""),
                    "summary": getattr(entry, "summary", getattr(entry, "description", "")),
                    "id": getattr(entry, "id", ""),
                    "author": getattr(entry, "author", "")
                }
                feed_info["entries"].append(entry_data)

            self.logger.info(f"Successfully parsed {len(feed_info['entries'])} entries from {source_url}")
            return feed_info

        except Exception as e:
            self.logger.error(f"Failed to parse feed from {source_url}: {e}")
            return {"title": "", "link": "", "description": "", "entries": []}

    def get_entry_count(self, feed_data: Dict[str, Any]) -> int:
        """Get the number of entries in parsed feed data."""
        return len(feed_data.get("entries", []))