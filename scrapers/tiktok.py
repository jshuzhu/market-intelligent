"""
TikTok scraper — search trending hashtags via Playwright.
"""
from typing import List, Dict, Optional
from .base import BaseScraper


class TikTokScraper(BaseScraper):
    """
    Scrape TikTok for trending design/video content.

    NOTE: TikTok uses aggressive anti-scraping. Public page renders
    limited content. Results may vary. Best-effort only.
    """

    def search_hashtag(
        self,
        hashtag: str,
        max_videos: int = 10
    ) -> List[Dict]:
        """
        Search TikTok by hashtag and extract video descriptions.

        Args:
            hashtag: Hashtag without #
            max_videos: Max videos to extract

        Returns:
            List of dicts with description, plays, url
        """
        url = f"https://www.tiktok.com/tag/{hashtag}"
        videos = []

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=self.headers["User-Agent"]
                )

                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

                # Try to extract video containers
                containers = page.query_selector_all(
                    "[data-e2e=search_video-item], "
                    ".video-card, "
                    "div[class*=video-feed] article"
                )

                for vid in containers[:max_videos]:
                    try:
                        desc_el = vid.query_selector(
                            "[data-e2e=search_video-desc], "
                            ".video-desc, "
                            "span[class*=desc]"
                        )
                        desc = desc_el.inner_text() if desc_el else ""

                        link_el = vid.query_selector("a")
                        link = ""
                        if link_el:
                            href = link_el.get_attribute("href", "")
                            if href:
                                link = f"https://www.tiktok.com{href}"

                        desc = self.clean_text(desc)
                        if desc and len(desc) > 5:
                            videos.append({
                                "description": desc,
                                "url": link,
                                "hashtag": hashtag,
                                "source": "tiktok",
                            })
                    except Exception:
                        continue

                browser.close()

        except ImportError:
            self.logger.warning("Playwright not installed. Skipping TikTok.")
        except Exception as e:
            self.logger.warning(f"TikTok search failed: {e}")

        return videos

    def search_trending(
        self,
        hashtags: Optional[List[str]] = None,
        max_per_tag: int = 8
    ) -> List[Dict]:
        """Search multiple TikTok hashtags."""
        tags = hashtags or [
            "stickers", "enamelpins", "artprint", "digitalart",
            "kawaii", "cyberpunk", "aesthetic", "cutedesign",
            "posterart", "trendingart", "smallartist",
        ]
        all_vids = []

        for tag in tags:
            self.logger.info(f"Scraping TikTok #{tag}...")
            vids = self.search_hashtag(tag, max_per_tag)
            all_vids.extend(vids)
            self.logger.info(f"  -> {len(vids)} videos")

        return all_vids
