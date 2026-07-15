"""
Trend Analyzer Pipeline — orchestrates scraping + Gemini analysis.
"""
import logging
from typing import List, Dict, Optional

from utils.gemini_client import GeminiClient
from utils.supabase_client import Database
from scrapers import RedditScraper, TwitterScraper, EcommerceScraper


logger = logging.getLogger(__name__)


class TrendPipeline:
    """
    Coordinates the full Trend Analyzer workflow:
    1. Scrape sources (Reddit, Twitter, E-commerce)
    2. Analyze with Gemini Flash
    3. Save to Supabase
    4. Return structured results
    """

    def __init__(self, gemini_key: str, supabase_url: str, supabase_key: str):
        self.gemini = GeminiClient(api_key=gemini_key)
        self.db = Database(url=supabase_url, key=supabase_key)

        self.reddit = RedditScraper()
        self.twitter = TwitterScraper()
        self.ecommerce = EcommerceScraper()

    def run(
        self,
        niche: str,
        use_reddit: bool = True,
        use_twitter: bool = False,
        use_ecommerce: bool = False,
        timeframe: str = "month",
        max_themes: int = 10,
    ) -> Dict:
        """
        Execute full trend analysis pipeline.

        Args:
            niche: Target niche (e.g. "Stickers / Decals")
            use_reddit: Scrape Reddit
            use_twitter: Scrape X/Twitter
            use_ecommerce: Scrape e-commerce reviews
            timeframe: Lookback period
            max_themes: Max themes to extract

        Returns:
            Dict with results and metadata
        """
        all_texts = []
        source_stats = {}

        # --- Step 1: Scrape ---
        if use_reddit:
            reddit_posts = self.reddit.scrape_all(
                sort="top",
                limit=25,
                timeframe=timeframe,
            )
            texts = [p["title"] + " " + p["selftext"] for p in reddit_posts]
            all_texts.extend(texts)
            source_stats["reddit"] = len(reddit_posts)

        if use_twitter:
            search_terms = [niche.lower(), f"{niche} trend", f"{niche} design"]
            for term in search_terms:
                tweets = self.twitter.search_public(query=term, max_tweets=10)
                texts = [t["text"] for t in tweets]
                all_texts.extend(texts)
            source_stats["twitter"] = len([
                t for t in all_texts if "search_query" in str(t)
            ]) if not use_reddit else 0  # approximate

        if use_ecommerce:
            reviews = self.ecommerce.search_all(
                terms=[niche.lower()],
                max_products=3,
                max_reviews=3,
            )
            texts = [r["review_text"] for r in reviews]
            all_texts.extend(texts)
            source_stats["ecommerce"] = len(reviews)

        # --- Step 2: Classic keyword extraction ---
        keywords = self.gemini.extract_keywords(all_texts)

        # --- Step 3: Gemini trend analysis ---
        themes = self.gemini.analyze_trends(
            texts=all_texts,
            niche=niche,
            max_themes=max_themes,
        )

        # --- Step 4: Save to database ---
        saved_count = self.db.save_trends(themes, niche)

        return {
            "success": True,
            "niche": niche,
            "themes": themes,
            "keywords": keywords,
            "source_stats": source_stats,
            "total_texts_analyzed": len(all_texts),
            "saved_to_db": saved_count,
        }

    def get_history(self, niche: Optional[str] = None) -> List[Dict]:
        """Get previous trend analysis results."""
        return self.db.get_trends(niche=niche)
