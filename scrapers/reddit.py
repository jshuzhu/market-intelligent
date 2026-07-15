"""
Reddit scraper — fetch posts from merchandise subreddits via JSON API (no auth needed).
"""
import requests
from typing import List, Dict
from .base import BaseScraper


class RedditScraper(BaseScraper):
    """Scrape Reddit for trending design/merchandise topics."""

    # Subreddits relevant to graphic design merchandise
    DEFAULT_SUBREDDITS = [
        "stickers",       # Sticker community
        "EnamelPins",     # Enamel pins
        "artprints",      # Art prints
        "artstore",       # Art marketplace
        "artcommissions", # Commission trends
        "streetwearstartup", # Apparel trends
    ]

    # Sort modes
    SORT_MODES = ["hot", "top", "rising"]

    def scrape_subreddit(
        self,
        subreddit: str,
        sort: str = "hot",
        limit: int = 25,
        timeframe: str = "month"
    ) -> List[Dict]:
        """
        Fetch posts from a subreddit via Reddit's old.reddit.com or www.reddit.com JSON API.

        Args:
            subreddit: Subreddit name (without r/)
            sort: 'hot', 'top', 'new', 'rising'
            limit: Number of posts (max 100)
            timeframe: 'hour', 'day', 'week', 'month', 'year', 'all' (only for 'top')

        Returns:
            List of dicts with title, score, url, selftext, created_utc
        """
        # Set a proper Reddit API user-agent (required since 2023)
        ua = self.headers.copy()
        ua["User-Agent"] = "MarketIntelligenceBot/1.0 (by /u/jshuzhu)"

        # Try primary endpoint
        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
        if sort == "top":
            url += f"&t={timeframe}"

        try:
            resp = requests.get(url, headers=ua, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            # Fallback: try old.reddit.com HTML scrape
            self.logger.info(f"r/{subreddit} JSON blocked. Trying HTML fallback...")
            return self._scrape_html(subreddit, sort, limit)

        posts = self._parse_json_response(data, subreddit)
        self._rate_limit()
        return posts

    def _parse_json_response(self, data: dict, subreddit: str) -> List[Dict]:
        """Parse a Reddit JSON API response into clean dicts."""
        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append({
                "id": post.get("id"),
                "title": self.clean_text(post.get("title", "")),
                "score": post.get("score", 0),
                "url": self.clean_url(post.get("url")),
                "permalink": self.clean_url(
                    f"https://www.reddit.com{post.get('permalink', '')}"
                ),
                "selftext": self.clean_text(post.get("selftext", "")),
                "num_comments": post.get("num_comments", 0),
                "upvote_ratio": post.get("upvote_ratio", 0.0),
                "created_utc": post.get("created_utc"),
                "source_subreddit": subreddit,
            })
        return posts

    def _scrape_html(
        self,
        subreddit: str,
        sort: str = "hot",
        limit: int = 25
    ) -> List[Dict]:
        """
        Fallback: scrape old.reddit.com HTML (no API key needed).
        """
        from bs4 import BeautifulSoup

        url = f"https://old.reddit.com/r/{subreddit}/{sort}/?limit={limit}"
        posts = []

        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            entries = soup.select("div.thing")
            for entry in entries[:limit]:
                title_el = entry.select_one("a.title")
                if not title_el:
                    continue

                # Extract score
                score_el = entry.select_one(".score.unvoted")
                score_text = score_el.get_text() if score_el else "0"
                score = self._parse_score(score_text)

                # Extract URL
                permalink_el = entry.select_one("a.bylink")
                permalink = (
                    f"https://www.reddit.com{permalink_el['href']}"
                    if permalink_el else None
                )

                posts.append({
                    "id": entry.get("data-fullname", ""),
                    "title": self.clean_text(title_el.get_text()),
                    "score": score,
                    "url": self.clean_url(title_el.get("href", "")),
                    "permalink": self.clean_url(permalink),
                    "selftext": "",
                    "num_comments": 0,
                    "upvote_ratio": 0.0,
                    "created_utc": None,
                    "source_subreddit": subreddit,
                })

            self._rate_limit()

        except Exception as e:
            self.logger.warning(f"HTML fallback for r/{subreddit} failed: {e}")

        return posts

    @staticmethod
    def _parse_score(text: str) -> int:
        """Parse score text like '1.2k' or '•' into int."""
        text = text.strip()
        if not text or text == "•":
            return 0
        text = text.replace(",", "")
        if "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1000)
        try:
            return int(text)
        except ValueError:
            return 0

        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append({
                "id": post.get("id"),
                "title": self.clean_text(post.get("title", "")),
                "score": post.get("score", 0),
                "url": self.clean_url(post.get("url")),
                "permalink": self.clean_url(
                    f"https://www.reddit.com{post.get('permalink', '')}"
                ),
                "selftext": self.clean_text(post.get("selftext", "")),
                "num_comments": post.get("num_comments", 0),
                "upvote_ratio": post.get("upvote_ratio", 0.0),
                "created_utc": post.get("created_utc"),
                "source_subreddit": subreddit,
            })

        self._rate_limit()
        return posts

    def scrape_all(
        self,
        subreddits: List[str] = None,
        sort: str = "top",
        limit: int = 25,
        timeframe: str = "month"
    ) -> List[Dict]:
        """Scrape multiple subreddits and return combined results."""
        subreddits = subreddits or self.DEFAULT_SUBREDDITS
        all_posts = []

        for sub in subreddits:
            self.logger.info(f"Scraping r/{sub} ({sort})...")
            posts = self.scrape_subreddit(sub, sort, limit, timeframe)
            all_posts.extend(posts)
            self.logger.info(f"  -> {len(posts)} posts")

        # Sort by score descending
        all_posts.sort(key=lambda p: p.get("score", 0), reverse=True)
        return all_posts
