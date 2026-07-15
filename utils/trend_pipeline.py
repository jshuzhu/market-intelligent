"""
Trend Analyzer Pipeline — orchestrates multi-source scraping + Gemini analysis.
"""
import logging
from typing import List, Dict, Optional

from utils.gemini_client import GeminiClient
from utils.supabase_client import Database
from scrapers import (
    RedditScraper,
    EtsyScraper,
    InstagramScraper,
    TikTokScraper,
    ShopeeScraper,
)


logger = logging.getLogger(__name__)


class TrendPipeline:
    """
    Coordinates the full Trend Analyzer workflow:
    1. Scrape from selected sources (Reddit, Etsy, Instagram, TikTok, Shopee)
    2. Analyze with Gemini Flash
    3. Save to Supabase
    4. Return structured results with charts-ready data
    """

    def __init__(self, gemini_key: str, supabase_url: str, supabase_key: str):
        self.gemini = GeminiClient(api_key=gemini_key)
        self.db = Database(url=supabase_url, key=supabase_key)

        self.reddit = RedditScraper()
        self.etsy = EtsyScraper()
        self.instagram = InstagramScraper()
        self.tiktok = TikTokScraper()
        self.shopee = ShopeeScraper()

    def run(
        self,
        niche: str,
        use_reddit: bool = False,
        use_etsy: bool = False,
        use_instagram: bool = False,
        use_tiktok: bool = False,
        use_shopee: bool = False,
        timeframe: str = "month",
        max_themes: int = 10,
    ) -> Dict:
        """
        Execute full multi-source trend analysis.

        Args:
            niche: Target niche (e.g. "Stickers / Decals")
            use_reddit: Scrape Reddit
            use_etsy: Scrape Etsy
            use_instagram: Scrape Instagram
            use_tiktok: Scrape TikTok
            use_shopee: Scrape Shopee
            timeframe: Lookback period for Reddit
            max_themes: Max themes to extract

        Returns:
            Dict with results, source_stats, and chart-ready data
        """
        all_texts = []
        source_stats = {}

        # --- Step 1: Scrape selected sources ---
        if use_reddit:
            try:
                posts = self.reddit.scrape_all(
                    sort="top", limit=25, timeframe=timeframe,
                )
                texts = [f"{p['title']}. {p['selftext']}".strip() for p in posts]
                all_texts.extend(texts)
                source_stats["reddit"] = len(posts)
                logger.info(f"Reddit: {len(posts)} posts")
            except Exception as e:
                logger.warning(f"Reddit scrape failed: {e}")

        if use_etsy:
            try:
                products = self.etsy.search_all(max_results=15)
                all_texts.extend([p["title"] for p in products])
                source_stats["etsy"] = len(products)
                logger.info(f"Etsy: {len(products)} products")
            except Exception as e:
                logger.warning(f"Etsy scrape failed: {e}")

        if use_instagram:
            try:
                posts = self.instagram.search_trending_hashtags(max_per_tag=8)
                all_texts.extend([p["caption"] for p in posts])
                source_stats["instagram"] = len(posts)
                logger.info(f"Instagram: {len(posts)} posts")
            except Exception as e:
                logger.warning(f"Instagram scrape failed: {e}")

        if use_tiktok:
            try:
                videos = self.tiktok.search_trending(max_per_tag=6)
                all_texts.extend([v["description"] for v in videos])
                source_stats["tiktok"] = len(videos)
                logger.info(f"TikTok: {len(videos)} videos")
            except Exception as e:
                logger.warning(f"TikTok scrape failed: {e}")

        if use_shopee:
            try:
                products = self.shopee.search_all(max_results=8)
                all_texts.extend([p["name"] for p in products])
                source_stats["shopee"] = len(products)
                logger.info(f"Shopee: {len(products)} products")
            except Exception as e:
                logger.warning(f"Shopee scrape failed: {e}")

        # --- Step 2: Extract keywords ---
        keywords = self.gemini.extract_keywords(all_texts) if all_texts else []

        # --- Step 3: Gemini trend analysis ---
        themes = self.gemini.analyze_trends(
            texts=all_texts,
            niche=niche,
            max_themes=max_themes,
        ) if all_texts else [{
            "theme": "No Data",
            "description": "No scraped data — enable at least one source.",
            "score": 0,
            "keywords": [],
        }]

        # --- Step 4: Save to database ---
        saved_count = self.db.save_trends(themes, niche) if all_texts else 0

        # --- Step 5: Build chart-ready data ---
        source_labels = [k.title() for k, v in source_stats.items() if v > 0]
        source_values = [v for v in source_stats.values() if v > 0]

        return {
            "success": True,
            "niche": niche,
            "themes": themes,
            "keywords": keywords,
            "source_stats": source_stats,
            "source_pie": {
                "labels": source_labels,
                "values": source_values,
            },
            "total_texts_analyzed": len(all_texts),
            "saved_to_db": saved_count,
        }

    def get_history(self, niche: Optional[str] = None) -> List[Dict]:
        """Get previous trend analysis results from DB."""
        return self.db.get_trends(niche=niche)
