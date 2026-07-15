"""
Twitter/X scraper — search recent tweets via Playwright (public, no login).
"""
import re
from typing import List, Dict
from .base import BaseScraper


class TwitterScraper(BaseScraper):
    """
    Scrape X/Twitter for design trend mentions.

    NOTE: X.com heavily rate-limits public scraping. This uses Playwright
    to render the public search page. Results may be limited without login.
    """

    def search_public(
        self,
        query: str,
        max_tweets: int = 20
    ) -> List[Dict]:
        """
        Search X.com public search page for recent tweets.

        Args:
            query: Search query string
            max_tweets: Max tweets to collect

        Returns:
            List of dicts with text, likes, retweets, url
        """
        tweets = []
        search_url = f"https://x.com/search?q={query}&src=typed_query&f=live"

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    )
                )

                page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)  # Let JS render

                # Try to extract tweet articles
                articles = page.query_selector_all("article")
                for art in articles[:max_tweets]:
                    try:
                        text_el = art.query_selector('[data-testid="tweetText"]')
                        text = text_el.inner_text() if text_el else ""

                        tweets.append({
                            "text": self.clean_text(text),
                            "source": "twitter",
                            "search_query": query,
                        })
                    except Exception:
                        continue

                browser.close()

        except ImportError:
            self.logger.warning("Playwright not installed. Skipping Twitter scrape.")
        except Exception as e:
            self.logger.warning(f"Twitter scrape failed: {e}")

        return tweets
