"""
Gemini Flash (Free Tier) client for trend analysis & website evaluation.
Uses the new google-genai SDK (v2).
"""
import logging
from typing import List, Dict, Optional
from google.genai import types as genai_types


logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Wrapper around Gemini 1.5 Flash / 2.0 Flash Free Tier API.

    Handles:
    - Trend analysis from scraped text
    - Business website quality evaluation
    - Keyword extraction
    """

    def __init__(self, api_key: str, model: str = "gemini-3.1-flash-lite"):
        """
        Args:
            api_key: Gemini API key (Free Tier)
            model: Model name. Default uses Gemini 2.0 Flash (free tier).
        """
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model = model
        logger.info(f"Gemini client initialized with model: {model}")

    def analyze_trends(
        self,
        texts: List[str],
        niche: str,
        max_themes: int = 10
    ) -> List[Dict]:
        """
        Analyze scraped texts and extract trending themes/design ideas.

        Args:
            texts: List of scraped text (Reddit posts, reviews, tweets)
            niche: e.g. "stickers", "enamel pins", "art prints"
            max_themes: Maximum number of themes to extract

        Returns:
            List of dicts: {theme, description, score, keywords}
        """
        if not texts:
            return [{"theme": "No data", "description": "No scraped data available.",
                     "score": 0, "keywords": []}]

        # Combine texts (limit to avoid token overflow)
        sample = texts[:50]
        combined = "\n---\n".join(
            [t[:500] for t in sample if len(t) > 20]
        )

        prompt = f"""You are a market trend analyst for graphic design merchandise.

Your job: Analyze the following scraped social media posts, reviews, and discussions
to identify the TOP {max_themes} trending themes/styles/concepts for {niche}.

For each theme, provide:
1. Theme name (short, catchy)
2. Description (1-2 sentences)
3. Trend score (0-100 based on frequency/engagement)
4. Related keywords (comma-separated)

Focus ONLY on design trends relevant to {niche}.
Ignore generic comments or off-topic posts.

Output MUST be valid JSON array format only:
[
  {{
    "theme": "Cyberpunk Neon",
    "description": "Bright neon color palettes with cyberpunk aesthetics...",
    "score": 85,
    "keywords": ["neon", "cyberpunk", "grid", "holographic"]
  }}
]

Scraped data:
{combined[:30000]}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                )
            )

            result = self._parse_json_response(response.text)
            return result if isinstance(result, list) else [
                {"theme": "Parse Error", "description": "Could not parse AI response",
                 "score": 0, "keywords": []}
            ]

        except Exception as e:
            logger.error(f"Gemini trend analysis failed: {e}")
            return [{"theme": "Error", "description": str(e), "score": 0, "keywords": []}]

    def evaluate_website_quality(
        self,
        business_name: str,
        website_url: Optional[str],
        description: Optional[str] = None
    ) -> Dict:
        """
        Evaluate a business's web presence quality.

        Args:
            business_name: Business name
            website_url: Their website URL (if any)
            description: Additional context about the business

        Returns:
            Dict: {has_website, quality, needs_improvement, pitch_angle, score}
        """
        if not website_url:
            return {
                "has_website": False,
                "quality": "none",
                "needs_improvement": True,
                "pitch_angle": (
                    f"This business has no online presence. "
                    f"Pitch a modern website + online ordering system."
                ),
                "score": 10,
            }

        prompt = f"""You are a business development consultant.

Evaluate this business's web presence:
- Business: {business_name}
- Website: {website_url}
- Context: {description or 'N/A'}

Based only on the URL/name (not scraping the actual site), assess:
1. Quality: "good" (modern/professional), "decent" (basic but functional),
   "poor" (outdated/broken), or "none"
2. Does it NEED improvement? (true/false)
3. What's a compelling sales pitch angle for a web developer?

Output JSON:
{{
  "has_website": true,
  "quality": "poor|decent|good",
  "needs_improvement": true|false,
  "pitch_angle": "string",
  "score": 0-100
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1024,
                )
            )
            return self._parse_json_response(response.text)

        except Exception as e:
            logger.error(f"Gemini website eval failed: {e}")
            return {
                "has_website": bool(website_url),
                "quality": "unknown",
                "needs_improvement": True,
                "pitch_angle": "Unable to evaluate automatically.",
                "score": 50,
            }

    def extract_keywords(
        self,
        texts: List[str],
        max_keywords: int = 20
    ) -> List[str]:
        """Extract trending keywords from texts."""
        if not texts:
            return []

        combined = "\n".join([t[:300] for t in texts[:30]])

        prompt = f"""Extract the {max_keywords} most relevant design/trend keywords
from the text below. Return ONLY a JSON array of strings.

Keywords:
{combined[:15000]}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=1024,
                )
            )
            result = self._parse_json_response(response.text)
            return result if isinstance(result, list) else []

        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []

    def _parse_json_response(self, text: str):
        """Parse JSON from Gemini response (handles markdown fences)."""
        import json
        import re

        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON array/object in the text
            obj_match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
            if obj_match:
                try:
                    return json.loads(obj_match.group(1))
                except json.JSONDecodeError:
                    pass
            raise
