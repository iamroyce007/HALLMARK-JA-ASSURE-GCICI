"""
Research & Intelligence Tools Architecture for InsurTech AI Systems
Provides curated recommendations, API capabilities, and integration guides for:
- Crawl4AI: Asynchronous Markdown Web Crawler for insurer policy wording and rate cards
- Tavily AI: Real-time LLM-optimized search engine for competitor & regulatory intelligence
- Corporate Registry Connectors (ACRA, SSM, Ditjen AHU)
- Niche Talent & Job Board Scrapers (Reverse-Signal Intent)
- Ad Library Monitors (Meta Ad Library, LinkedIn Ad Spy)
"""

from typing import List, Dict, Any

RECOMMENDED_RESEARCH_TOOLS: List[Dict[str, Any]] = [
    {
        "id": "crawl4ai",
        "name": "Crawl4AI",
        "category": "Deep Web Crawling & Document Ingestion",
        "badge": "RECOMMENDED (Open Source)",
        "tech_type": "Asynchronous Headless Browser & Markdown Extractor",
        "description": "Blazing-fast open-source crawler that converts complex insurer websites, policy wording PDFs, and dynamic rate calculation pages directly into clean, LLM-ready markdown.",
        "why_superior": "Bypasses bot-detection, executes client-side JavaScript, extracts clean markdown without boilerplate HTML noise, and operates 10x faster than traditional Selenium scrapers.",
        "best_use_case_for_ja_assure": "Scraping competitor policy wordings (e.g. Chubb Specie, Allianz MedMal, Tokio Marine Cargo) to compare coverage sub-limits and exclusions.",
        "integration_example": """from crawl4ai import AsyncWebCrawler

async def fetch_competitor_policy(url: str):
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url)
        return result.markdown # Clean LLM-ready text for RAG"""
    },
    {
        "id": "tavily",
        "name": "Tavily Search API",
        "category": "Real-Time AI Search Engine",
        "badge": "RECOMMENDED (LLM Native)",
        "tech_type": "Agentic Search API",
        "description": "Search engine purpose-built for AI agents and LLMs. Delivers pre-filtered, citation-backed news snippets and regulatory updates without bloated search results.",
        "why_superior": "Zero hallucination risk on factual competitor rate updates; handles domain filtering (e.g., search only mas.gov.sg, bnm.gov.my, ojk.go.id).",
        "best_use_case_for_ja_assure": "Real-time monitoring of regulatory circulars from MAS, BNM, HKIA, OJK, and OIC, plus competitor press releases.",
        "integration_example": """from tavily import TavilyClient

tavily = TavilyClient(api_key="tvly-...")
response = tavily.search(
    query="Southeast Asia diamond jewelry insurance rates price increase 2024",
    include_domains=["insuranceinsider.com", "mas.gov.sg", "ojk.go.id"],
    max_results=5
)"""
    },
    {
        "id": "corporate_registries",
        "name": "ASEAN Corporate Registries (ACRA / SSM / Ditjen AHU)",
        "category": "Reverse-Signal Company Intent",
        "badge": "STRATEGIC MOAT",
        "tech_type": "Government API & Public Gazette Scrapers",
        "description": "Direct feeds and gazette scrapers monitoring newly incorporated luxury boutiques, licensed clinics, and bonded logistics warehouses.",
        "why_superior": "Detects insurance buying intent before the company even starts shopping for insurance brokers, enabling zero-competition outbound prospecting.",
        "best_use_case_for_ja_assure": "Catching new clinic branch registrations for DoctorShield and new gem dealer incorporations for Jade.",
        "integration_example": """# Webhook listener monitoring ACRA Singapore entity filings
# Filter SSIC codes: 47731 (Retail sale of jewellery) & 86201 (Clinics)"""
    },
    {
        "id": "job_intent_crawlers",
        "name": "LinkedIn Talent Insights & Job Board Monitors",
        "category": "Reverse-Signal Talent Intent",
        "badge": "HIGH CONVERSION",
        "tech_type": "Hiring Vacancy Scrapers (LinkedIn, JobStreet, MyCareersFuture)",
        "description": "Monitors job postings for high-risk titles (e.g., 'Head of Vault Security', 'Endoscopic Spine Surgeon', 'Chief Information Security Officer').",
        "why_superior": "A jeweller hiring an armored transit manager is a 95%+ high-intent buying signal for Jade / Jaguar Transit specie insurance.",
        "best_use_case_for_ja_assure": "Automated pipeline population for JA Assure brokers with context-aware cold outreach scripts.",
        "integration_example": """# Automated query: company hiring 'Specie Risk Manager' OR 'Vault Custody'"""
    },
    {
        "id": "meta_ad_library",
        "name": "Meta Ad Library & LinkedIn Ad Spy",
        "category": "Competitor Creative Intelligence",
        "badge": "CREATIVE R&D",
        "tech_type": "Ad Transparency API",
        "description": "Tracks active marketing creatives, value propositions, and discount hooks deployed by competing insurance intermediaries across Singapore, Malaysia, and Indonesia.",
        "why_superior": "Reveals which ad hooks competitors are scaling and highlights compliance vulnerabilities in competitor claims.",
        "best_use_case_for_ja_assure": "Benchmarking visual styles and CTAs for Jade (Instagram) and DoctorShield (LinkedIn).",
        "integration_example": """# Query Meta Ad Library API for terms: 'jewellery insurance' OR 'medical indemnity'"""
    }
]
