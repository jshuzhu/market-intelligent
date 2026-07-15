"""
E-commerce scraper — scrape product reviews from Amazon/Shopee for trend analysis.
"""
import re
from typing import List, Dict, Optional
from .base import BaseScraper


class EcommerceScraper(BaseScraper):
    """
    Scrape e-commerce product reviews for design trend keywords.

    Currently supports: Amazon (via Playwright)
    Future: Shopee, Etsy, Redbubble
    """

    # Search terms relevant to merchandise design
    DEFAULT_SEARCH_TERMS = [
        "aesthetic stickers",
        "enamel pins cute",
        "art print poster",
        "trendy wall art",
        "kawaii stickers",
        "cyberpunk art print",
        "anime enamel pin",
        "minimalist poster",
    ]

    def search_amazon(
        self,
        query: str,
        max_products: int = 5,
        max_reviews_per_product: int = 5
    ) -> List[Dict]:
        """
        Search Amazon products and extract review snippets.

        Args:
            query: Search keyword
            max_products: Number of products to analyze
            max_reviews_per_product: Reviews per product

        Returns:
            List of review dicts
        """
        results = []
        search_url = (
            f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            f"&ref=nb_sb_noss"
        )

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=self.headers["User-Agent"]
                )

                # --- Search Amazon ---
                page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                # Get product links
                product_links = []
                links = page.query_selector_all(
                    'a[href*="/dp/"], a[href*="/product/"]'
                )
                for link in links[:max_products]:
                    href = link.get_attribute("href")
                    if href:
                        full_url = (
                            f"https://www.amazon.com{href}"
                            if href.startswith("/")
                            else href
                        )
                        product_links.append(full_url)

                # --- Visit each product page for reviews ---
                for prod_url in product_links[:max_products]:
                    try:
                        page.goto(prod_url, timeout=20000, wait_until="domcontentloaded")
                        page.wait_for_timeout(2000)

                        # Try to get title
                        title_el = page.query_selector("#productTitle")
                        title = title_el.inner_text().strip() if title_el else query

                        # Scroll to reviews section
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(2000)

                        # Look for review text
                        reviews = page.query_selector_all(
                            '[data-hook="review-body"] span, '
                            '.review-text-content span'
                        )
                        for rev in reviews[:max_reviews_per_product]:
                            text = rev.inner_text().strip()
                            if len(text) > 10:
                                results.append({
                                    "product_title": title,
                                    "review_text": self.clean_text(text),
                                    "product_url": prod_url,
                                    "search_query": query,
                                    "source": "amazon",
                                })
                    except Exception as e:
                        self.logger.warning(f"Product scrape failed: {e}")
                        continue

                browser.close()

        except ImportError:
            self.logger.warning("Playwright not installed. Skipping Amazon scrape.")
        except Exception as e:
            self.logger.warning(f"Amazon scrape failed: {e}")

        return results

    def search_all(
        self,
        terms: Optional[List[str]] = None,
        max_products: int = 3,
        max_reviews: int = 3
    ) -> List[Dict]:
        """Search multiple e-commerce terms."""
        terms = terms or self.DEFAULT_SEARCH_TERMS
        all_reviews = []

        for term in terms:
            self.logger.info(f"Scraping Amazon for '{term}'...")
            reviews = self.search_amazon(term, max_products, max_reviews)
            all_reviews.extend(reviews)
            self.logger.info(f"  -> {len(reviews)} reviews")

        return all_reviews
