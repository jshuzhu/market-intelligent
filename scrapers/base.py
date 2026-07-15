"""
Base scraper class with common utilities.
"""
import time
import re
import logging
from typing import Optional


class BaseScraper:
    """Base class for all scrapers."""

    def __init__(self, delay: float = 1.5):
        self.delay = delay
        self.logger = logging.getLogger(self.__class__.__name__)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/json,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _rate_limit(self):
        """Respect rate limits between requests."""
        time.sleep(self.delay)

    def clean_text(self, text: str) -> str:
        """Clean and normalize scraped text."""
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s.,!?\'\"\-@#/:()&%$€£]", "", text)
        return text.strip()

    def clean_url(self, url: Optional[str]) -> Optional[str]:
        """Clean and validate URL."""
        if not url:
            return None
        url = url.strip()
        if url.startswith("//"):
            url = "https:" + url
        if not url.startswith(("http://", "https://")):
            return None
        return url
