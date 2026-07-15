"""
Supabase database operations for saving & retrieving scraped data.
"""
import logging
from typing import List, Dict, Optional
from supabase import create_client


logger = logging.getLogger(__name__)


class Database:
    """Handles all Supabase CRUD operations."""

    def __init__(self, url: str, key: str):
        """
        Args:
            url: Supabase project URL
            key: Supabase anon or service key
        """
        self.client = create_client(url, key)
        logger.info("Supabase client initialized")

    # -------- TRENDS --------

    def save_trends(self, trends: List[Dict], niche: str) -> int:
        """
        Save trend analysis results to Supabase.

        Args:
            trends: List of trend dicts from GeminiClient.analyze_trends()
            niche: The niche/category analyzed

        Returns:
            Number of rows inserted
        """
        if not trends:
            return 0

        records = []
        for t in trends:
            records.append({
                "niche": niche,
                "theme": t.get("theme", "Unknown"),
                "description": t.get("description", ""),
                "score": t.get("score", 0),
                "keyword": ", ".join(t.get("keywords", [])),
            })

        try:
            data = self.client.table("trends").insert(records).execute()
            inserted = len(data.data) if data.data else 0
            logger.info(f"Saved {inserted} trend records")
            return inserted
        except Exception as e:
            logger.error(f"Failed to save trends: {e}")
            return 0

    def get_trends(self, niche: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Retrieve saved trends, optionally filtered by niche."""
        try:
            query = self.client.table("trends").select("*").order(
                "created_at", desc=True
            ).limit(limit)

            if niche:
                query = query.eq("niche", niche)

            data = query.execute()
            return data.data or []
        except Exception as e:
            logger.error(f"Failed to fetch trends: {e}")
            return []

    # -------- LEADS --------

    def save_leads(self, leads: List[Dict]) -> int:
        """
        Save lead generation results to Supabase.

        Args:
            leads: List of lead dicts

        Returns:
            Number of rows inserted
        """
        if not leads:
            return 0

        records = []
        for lead in leads:
            records.append({
                "business_name": lead.get("business_name", "Unknown"),
                "category": lead.get("category", ""),
                "address": lead.get("address", ""),
                "phone": lead.get("phone", ""),
                "website": lead.get("website", ""),
                "google_rating": lead.get("google_rating"),
                "has_website": lead.get("has_website", False),
                "website_quality": lead.get("website_quality", "unknown"),
                "needs_improvement": lead.get("needs_improvement", True),
                "pitch_angle": lead.get("pitch_angle", ""),
                "lead_score": lead.get("lead_score", 0),
                "source": lead.get("source", "manual"),
                "location": lead.get("location", ""),
            })

        try:
            data = self.client.table("leads").insert(records).execute()
            inserted = len(data.data) if data.data else 0
            logger.info(f"Saved {inserted} lead records")
            return inserted
        except Exception as e:
            logger.error(f"Failed to save leads: {e}")
            return 0

    def get_leads(
        self,
        category: Optional[str] = None,
        min_score: int = 0,
        has_website: Optional[bool] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve leads with optional filters."""
        try:
            query = self.client.table("leads").select("*").order(
                "lead_score", desc=True
            ).limit(limit)

            if category:
                query = query.eq("category", category)
            if min_score > 0:
                query = query.gte("lead_score", min_score)
            if has_website is not None:
                query = query.eq("has_website", has_website)

            data = query.execute()
            return data.data or []
        except Exception as e:
            logger.error(f"Failed to fetch leads: {e}")
            return []
