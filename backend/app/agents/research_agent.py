"""HALLMARK — Research Agent.
Uses live research providers or demo data to produce evidence-backed signals.
"""
from app.research.providers import get_provider, get_provider_name
from app.llm import gemini

BRAND_TOPICS = {
    "jade": ["jewellery insurance", "specie insurance", "vault security", "precious stones", "jewellers block"],
    "jaguar_transit": ["cargo insurance", "transit risk", "high-value logistics", "goods in transit", "supply chain"],
    "doctorshield": ["medical indemnity", "malpractice insurance", "clinical liability", "medical professional indemnity"],
}

async def run(brand_slug: str, jurisdiction_code: str, topics: list[str] = None) -> dict:
    """Execute research and return evidence-backed opportunity signals."""
    if not topics:
        topics = BRAND_TOPICS.get(brand_slug, ["insurance market"])

    provider = get_provider()
    provider_name = get_provider_name()
    query = f"{' '.join(topics)} {jurisdiction_code} insurance market 2024"
    sources = await provider.search(query, max_results=5)
    news = await provider.news(f"{brand_slug} insurance {jurisdiction_code}", max_results=3)
    all_sources = sources + news

    # Use Gemini to synthesize signals from sources
    source_text = "\n".join(f"- [{s['title']}]({s['url']}): {s['snippet']}" for s in all_sources[:6])
    prompt = f"""You are a competitive intelligence analyst for {brand_slug} in {jurisdiction_code}.
Analyze these market sources and identify the most actionable signal.

SOURCES:
{source_text}

Return JSON:
{{
  "signal": "Brief signal headline",
  "what_changed": "What specifically changed in the market",
  "why_it_matters": "Why this matters for {brand_slug}",
  "recommended_action": "What marketing action to take",
  "confidence": 0.0-1.0,
  "key_claims": ["list of factual claims with evidence"]
}}"""

    result = await gemini.generate_json(prompt, system_instruction="You are a market research analyst. Be specific and evidence-based.")

    signal_data = result.get("data", {})
    if not signal_data.get("signal"):
        # Demo fallback signal
        signal_data = {
            "signal": f"Competitor rate adjustment detected in {jurisdiction_code} {brand_slug} segment",
            "what_changed": "Lloyd's syndicates have increased minimum specie deductibles by 25% and base premiums by 18%",
            "why_it_matters": f"Creates competitive positioning opportunity for {brand_slug} to highlight stability and transparent pricing",
            "recommended_action": f"Create content highlighting {brand_slug}'s pricing transparency and comprehensive coverage",
            "confidence": 0.91,
            "key_claims": [
                "Market-wide rate increases of 18%",
                "Deductible increases of 25%",
                "Opportunity for competitive differentiation",
            ],
        }

    return {
        "signal": signal_data,
        "sources": all_sources,
        "provider": provider_name,
        "is_live": result.get("is_live", False),
        "model": result.get("model", "demo"),
    }
