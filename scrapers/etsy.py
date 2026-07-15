"""
Etsy scraper — search products & extract listing titles, tags, reviews.
Etsy HTML is relatively static; no Playwright needed for basic searches.
"""
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper


class EtsyScraper(BaseScraper):
    """Scrape Etsy for trending product designs and descriptions."""

    # Search terms relevant to digitalcanvasmy products
    DEFAULT_SEARCH_TERMS = [
        "aesthetic stickers",
        "enamel pins",
        "art print poster",
        "trendy wall art",
        "kawaii stickers",
        "minimalist art print",
        "cyberpunk poster",
        "anime enamel pin",
    ]

    def search_products(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search Etsy and extract product listings.

        Args:
            query: Search keyword
            max_results: Max listings to fetch

        Returns:
            List of dicts with title, tags, price, url
        """
        results = []

        # Etsy requires more realistic browser headers
        etsy_headers = {
            **self.headers,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

        url = f"https://www.etsy.com/search?q={query.replace(' ', '+')}"

        session = requests.Session()
        try:
            resp = session.get(url, headers=etsy_headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Etsy uses data attributes and specific class names
            listings = soup.select(
                "div.v2-listing-card, "
                "li.wt-list-unstyled, "
                "div[data-listing-id]"
            )

            for item in listings[:max_results]:
                try:
                    # Title
                    title_el = item.select_one(
                        "h3.v2-listing-card__title, "
                        ".v2-listing-card__title, "
                        "a[href*='/listing/']"
                    )
                    title = title_el.get_text(strip=True) if title_el else ""

                    # URL
                    link = title_el.get("href", "") if title_el else ""
                    if link and not link.startswith("http"):
                        link = f"https://www.etsy.com{link}"

                    # Price
                    price_el = item.select_one(
                        ".currency-value, .n-listing-card__price"
                    )
                    price = price_el.get_text(strip=True) if price_el else ""

                    # Tags — extract from search result text
                    tags = self._extract_tags(title)

                    if title and len(title) > 5:
                        results.append({
                            "title": self.clean_text(title),
                            "tags": tags,
                            "price": price,
                            "url": link,
                            "source": "etsy",
                            "search_query": query,
                        })

                except Exception:
                    continue

            self._rate_limit()

        except Exception as e:
            self.logger.info(f"Etsy HTML failed for '{query}', trying Playwright fallback...")
            results = self._search_playwright(query, max_results)

        return results

    def _search_playwright(
        self,
        query: str,
        max_results: int = 15
    ) -> List[Dict]:
        """Fallback: use Playwright to render Etsy search page."""
        results = []
        url = f"https://www.etsy.com/search?q={query.replace(' ', '+')}"

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=self.headers["User-Agent"]
                )
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(4000)

                # Extract listing cards
                cards = page.query_selector_all(
                    "div.v2-listing-card, "
                    "div[data-listing-id], "
                    "li.wt-list-unstyled"
                )

                for card in cards[:max_results]:
                    try:
                        title_el = card.query_selector(
                            "h3, .v2-listing-card__title, a[href*='/listing/']"
                        )
                        title = title_el.inner_text().strip() if title_el else ""

                        link = ""
                        if title_el:
                            href = title_el.get_attribute("href", "")
                            if href and not href.startswith("http"):
                                link = f"https://www.etsy.com{href}"
                            else:
                                link = href

                        if title and len(title) > 3:
                            results.append({
                                "title": self.clean_text(title),
                                "tags": self._extract_tags(title),
                                "url": link,
                                "source": "etsy",
                                "search_query": query,
                            })
                    except Exception:
                        continue

                browser.close()

        except Exception as e:
            self.logger.warning(f"Etsy Playwright fallback failed: {e}")

        return results

    def _extract_tags(self, title: str) -> List[str]:
        """Extract potential tags/categories from product title."""
        words = title.lower().split()
        # Filter for design-relevant words
        design_kw = [
            "sticker", "pin", "print", "poster", "art", "design",
            "aesthetic", "kawaii", "minimalist", "cyberpunk", "vintage",
            "anime", "cute", "dark", "neon", "pastel", "gothic",
            "abstract", "geometric", "floral", "pattern", "illustration",
            "digital", "wall", "decor", "gift", "custom", "personalized",
        ]
        return [w for w in words if w in design_kw or w.endswith(("s", "ed", "ing"))][:8]

    def search_all(
        self,
        terms: Optional[List[str]] = None,
        max_results: int = 15
    ) -> List[Dict]:
        """Search multiple terms on Etsy."""
        terms = terms or self.DEFAULT_SEARCH_TERMS
        all_results = []

        for term in terms:
            self.logger.info(f"Scraping Etsy for '{term}'...")
            products = self.search_products(term, max_results)
            all_results.extend(products)
            self.logger.info(f"  -> {len(products)} products")

        return all_results
