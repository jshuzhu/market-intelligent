"""
Shopee scraper — search products and extract reviews via Playwright.

NOTE: Shopee has aggressive anti-bot protection. This is best-effort
and may require additional headers/cookies to work reliably.
"""
from typing import List, Dict, Optional
from .base import BaseScraper


class ShopeeScraper(BaseScraper):
    """
    Scrape Shopee Malaysia for product listings and reviews.
    Targets merchandise categories: stickers, prints, pins.
    """

    # Shopee Malaysia-specific search terms
    DEFAULT_SEARCH_TERMS = [
        "sticker decal",
        "enamel pin",
        "art print poster",
        "wall art poster",
        "kawaii sticker",
        "aesthetic poster",
        "cyberpunk art",
        "custom sticker",
    ]

    def search_products(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search Shopee MY and extract product listings.

        Args:
            query: Search keyword
            max_results: Max listings

        Returns:
            List of dicts with name, price, shop, sales
        """
        products = []
        search_url = (
            f"https://shopee.com.my/search"
            f"?keyword={query.replace(' ', '%20')}"
        )

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)

                context = browser.new_context(
                    user_agent=self.headers["User-Agent"],
                    locale="en-MY",
                    viewport={"width": 1920, "height": 1080},
                )
                page = context.new_page()

                page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

                # Shopee renders products in a grid
                items = page.query_selector_all(
                    "[data-sqe=item], "
                    ".shopee-search-item-result__item, "
                    "div[class*=card__item]"
                )

                for item in items[:max_results]:
                    try:
                        name_el = item.query_selector(
                            "[data-sqe=name], "
                            "div[class*=item__name]"
                        )
                        name = name_el.inner_text().strip() if name_el else ""

                        price_el = item.query_selector(
                            "[data-sqe=price], "
                            "span[class*=price]"
                        )
                        price = price_el.inner_text().strip() if price_el else ""

                        link_el = item.query_selector("a")
                        link = ""
                        if link_el:
                            href = link_el.get_attribute("href", "")
                            if href:
                                link = f"https://shopee.com.my{href}"

                        if name and len(name) > 5:
                            products.append({
                                "name": self.clean_text(name),
                                "price": price,
                                "url": link,
                                "source": "shopee",
                                "search_query": query,
                            })
                    except Exception:
                        continue

                browser.close()

        except ImportError:
            self.logger.warning("Playwright not installed. Skipping Shopee.")
        except Exception as e:
            self.logger.warning(f"Shopee search failed: {e}")

        return products

    def search_all(
        self,
        terms: Optional[List[str]] = None,
        max_results: int = 8
    ) -> List[Dict]:
        """Search multiple Shopee terms."""
        terms = terms or self.DEFAULT_SEARCH_TERMS
        all_products = []

        for term in terms:
            self.logger.info(f"Scraping Shopee for '{term}'...")
            products = self.search_products(term, max_results)
            all_products.extend(products)
            self.logger.info(f"  -> {len(products)} products")

        return all_products
