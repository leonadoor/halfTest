import requests
import logging
from typing import Optional
from time import sleep


class RSSClient:
    """HTTP client for fetching RSS feeds with retry logic and timeout controls."""

    def __init__(self, timeout: int = 30, max_retries: int = 3, user_agent: str = None):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or "AI-News-Aggregator/1.0"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.logger = logging.getLogger(__name__)

    def fetch_feed(self, url: str) -> Optional[str]:
        """
        Fetch RSS feed content from the given URL with retry logic.

        Args:
            url: The RSS feed URL to fetch

        Returns:
            The raw XML/Atom content as string, or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Fetching feed from {url} (attempt {attempt + 1}/{self.max_retries})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                self.logger.info(f"Successfully fetched feed from {url}")
                return response.text

            except requests.RequestException as e:
                self.logger.warning(f"Failed to fetch {url}: {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2  ** attempt
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    sleep(wait_time)
                else:
                    self.logger.error(f"All retries failed for {url}")
                    return None

        return None