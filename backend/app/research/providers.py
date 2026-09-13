"""HALLMARK — Research Providers.
Modular interface for Tavily, Firecrawl, and demo fallback.
"""
import os, logging
from typing import Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger("hallmark.research")

class ResearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[dict]: ...
    @abstractmethod
    async def extract(self, url: str) -> dict: ...
    @abstractmethod
    async def news(self, query: str, max_results: int = 5) -> list[dict]: ...

class TavilyProvider(ResearchProvider):
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        self._client = None

    def _get_client(self):
        if self._client is None and self.api_key:
            try:
                from tavily import TavilyClient
                self._client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Tavily init error: {e}")
        return self._client

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        client = self._get_client()
        if not client:
            return []
        try:
            response = client.search(query=query, max_results=max_results)
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:500],
                    "source_type": "web",
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "is_demo": False,
                }
                for r in response.get("results", [])
            ]
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []

    async def extract(self, url: str) -> dict:
        return {"url": url, "content": "", "error": "Tavily does not support direct extraction"}

    async def news(self, query: str, max_results: int = 5) -> list[dict]:
        return await self.search(f"{query} news latest", max_results)

class DemoProvider(ResearchProvider):
    """Provides realistic seeded research data for demo mode."""

    DEMO_SOURCES = [
        {
            "title": "Lloyd's Specie Syndicate Raises APAC Diamond Dealer Rates by 18%",
            "url": "https://www.insuranceinsider.com/asia/specie-rates-2024",
            "snippet": "Leading Lloyd's syndicates have increased minimum vault specie deductibles by 25% and base premiums by 18% following a series of high-profile regional heist and transit loss events across Singapore and Hong Kong diamond corridors.",
            "source_type": "news", "is_demo": True,
        },
        {
            "title": "MPS Introduces Mandatory Excess for Aesthetic Surgery Claims in Singapore",
            "url": "https://www.sma.org.sg/indemnity-updates-2024",
            "snippet": "The Medical Protection Society has introduced a new mandatory $25,000 excess on aesthetic surgery malpractice claims and a 15% rate loading for multi-location specialist clinics in Singapore.",
            "source_type": "news", "is_demo": True,
        },
        {
            "title": "OJK Tightens Digital Insurance Marketing Rules with SEOJK.05/2024",
            "url": "https://www.ojk.go.id/regulation/seojk-05-2024",
            "snippet": "Indonesia's OJK has issued new guidance strictly prohibiting any digital marketing asset from using 'pasti' (guaranteed) or unqualified speed-of-settlement claims. Mandatory supervisory banners required in minimum 10pt equivalent.",
            "source_type": "regulatory", "is_demo": True,
        },
        {
            "title": "Singapore Jewellers Association Reports Record High-Value Inventory Levels",
            "url": "https://www.sja.org.sg/market-report-q3-2024",
            "snippet": "The SJA's quarterly market report shows aggregate jewellery inventory values across Orchard Road and Marina Bay boutiques have reached SGD 2.8 billion, a 34% increase year-on-year driven by demand for investment-grade diamonds.",
            "source_type": "market", "is_demo": True,
        },
    ]

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        results = []
        for src in self.DEMO_SOURCES[:max_results]:
            results.append({**src, "retrieved_at": datetime.utcnow().isoformat()})
        return results

    async def extract(self, url: str) -> dict:
        for src in self.DEMO_SOURCES:
            if src["url"] == url:
                return {"url": url, "content": src["snippet"], "title": src["title"], "is_demo": True}
        return {"url": url, "content": "[Demo extraction]", "is_demo": True}

    async def news(self, query: str, max_results: int = 5) -> list[dict]:
        return await self.search(query, max_results)

def get_provider() -> ResearchProvider:
    """Get the best available research provider."""
    if os.getenv("TAVILY_API_KEY"):
        return TavilyProvider()
    return DemoProvider()

def get_provider_name() -> str:
    if os.getenv("TAVILY_API_KEY"):
        return "Tavily (LIVE)"
    return "Demo Provider (SEEDED DATA)"
