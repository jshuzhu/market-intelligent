"""
Instagram scraper — search hashtags via Playwright for trending design content.
"""
from typing import List, Dict, Optional
from .base import BaseScraper


class InstagramScraper(BaseScraper):
    """
    Scrape Instagram for hashtag trends.

    NOTE: Instagram locks down public scraping aggressively.
    This uses Playwright to render the public hashtag page.
    Results may be limited without login. Use sparingly.
    """

    def search_hashtag(
        self,
        hashtag: str,
        max_posts: int = 15
    ) -> List[Dict]:
        """
        Search Instagram by hashtag and extract post captions.

        Args:
            hashtag: Hashtag without #
            max_posts: Maximum posts to extract

        Returns:
            List of dicts with caption, likes, url
        """
        url = f"https://www.instagram.com/explore/tags/{hashtag}/"
        posts = []

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=self.headers["User-Agent"]
                )

                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

                # Instagram loads content via JS — wait for articles
                page.wait_for_selector("article", timeout=10000)

                # Extract post captions
                articles = page.query_selector_all("article")
                for art in articles[:max_posts]:
                    try:
                        # Try to get caption text
                        caption_el = art.query_selector(
                            "h1, ._a9zr, span"
                        )
                        caption = caption_el.inner_text() if caption_el else ""

                        # Try to get the post link
                        link_el = art.query_selector("a")
                        link = ""
                        if link_el:
                            href = link_el.get_attribute("href", "")
                            if href:
                                link = f"https://www.instagram.com{href}"

                        caption = self.clean_text(caption)
                        if caption and len(caption) > 10:
                            posts.append({
                                "caption": caption,
                                "post_url": link,
                                "hashtag": hashtag,
                                "source": "instagram",
                            })
                    except Exception:
                        continue

                browser.close()

        except ImportError:
            self.logger.warning("Playwright not installed. Skipping Instagram.")
        except Exception as e:
            self.logger.warning(f"Instagram hashtag search failed: {e}")

        return posts

    def search_trending_hashtags(
        self,
        base_hashtags: Optional[List[str]] = None,
        max_per_tag: int = 10
    ) -> List[Dict]:
        """
        Search multiple hashtags for design trends.

        Default hashtags relevant to merchandise design.
        """
        tags = base_hashtags or [
            "stickers", "enamelpins", "artprints", "digitalart",
            "kawaii", "cyberpunk", "minimalistart", "aestheticart",
            "stickershop", "pindesign", "posterdesign", "wallart",
            "cutedesign", "trendyart", "animeart",
        ]
        all_posts = []

        for tag in tags:
            self.logger.info(f"Scraping Instagram #{tag}...")
            posts = self.search_hashtag(tag, max_per_tag)
            all_posts.extend(posts)
            self.logger.info(f"  -> {len(posts)} posts")

        return all_posts
