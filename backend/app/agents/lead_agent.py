"""HALLMARK — Lead Intelligence Agent.
Discovers prospects via research + reverse signal detection.
"""
from app.llm import gemini
from app.research.providers import get_provider

BRAND_TARGETS = {
    "jade": {
        "industries": ["jewellery retail", "precious stones wholesale", "gem cutting", "watch retail", "luxury goods"],
        "signals": ["new store opening", "inventory expansion", "high-value exhibition", "auction event"],
    },
    "jaguar_transit": {
        "industries": ["logistics", "courier services", "luxury goods transport", "art shipping", "pharmaceutical logistics"],
        "signals": ["fleet expansion", "new warehouse", "cross-border route", "temperature-controlled fleet"],
    },
    "doctorshield": {
        "industries": ["medical clinic", "specialist practice", "dental clinic", "aesthetic surgery", "physiotherapy"],
        "signals": ["new practice opening", "hiring specialist", "multi-location expansion", "new medical equipment"],
    },
}

DEMO_LEADS = [
    {
        "company": "Brilliance Gems Pte Ltd",
        "industry": "Precious Stones Wholesale",
        "location": "Singapore",
        "jurisdiction_code": "SG",
        "matched_brand": "jade",
        "fit_score": 92,
        "signals": ["Expanded to 3 new retail locations in Orchard Road", "Inventory reported at SGD 45M", "Hiring security personnel"],
        "reasoning": "Rapid expansion with significant inventory growth creates immediate need for comprehensive jewellers block coverage. Multiple locations increase transit risk between stores.",
        "recommended_message": "With 3 new Orchard Road locations and growing inventory, ensuring each piece is protected in vault, display, and transit becomes increasingly complex. Jade Jewellers Block specializes in exactly this challenge.",
        "signal_type": "EXPANSION",
        "is_demo": True,
    },
    {
        "company": "SwiftCargo Asia",
        "industry": "High-Value Logistics",
        "location": "Malaysia",
        "jurisdiction_code": "MY",
        "matched_brand": "jaguar_transit",
        "fit_score": 87,
        "signals": ["New temperature-controlled fleet acquired", "Cross-border SG-MY route launched", "High-value art shipment contract won"],
        "reasoning": "Entering high-value cargo segment with new fleet and art contracts. Transit insurance gaps likely with standard logistics coverage.",
        "recommended_message": "High-value art shipments require specialist transit coverage beyond standard cargo policies. Jaguar Transit covers the specific risks of premium goods in motion.",
        "signal_type": "SERVICE_EXPANSION",
        "is_demo": True,
    },
    {
        "company": "Dr. Sarah Lim Aesthetics",
        "industry": "Aesthetic Surgery",
        "location": "Singapore",
        "jurisdiction_code": "SG",
        "matched_brand": "doctorshield",
        "fit_score": 94,
        "signals": ["Opening second clinic at Novena Medical Centre", "Added injectable treatments to services", "Hiring 2 additional aesthetic doctors"],
        "reasoning": "Multi-location aesthetic practice with injectable procedures represents high MPI risk. MPS excess changes make standalone coverage essential.",
        "recommended_message": "With expanding aesthetic services across two locations, DoctorShield's specialist medical indemnity provides the focused protection that general schemes may not fully address.",
        "signal_type": "PRACTICE_EXPANSION",
        "is_demo": True,
    },
]

async def run(brand_slug: str, jurisdiction_code: str) -> dict:
    """Discover leads and reverse signals."""
    targets = BRAND_TARGETS.get(brand_slug, BRAND_TARGETS["jade"])

    # Try live research
    provider = get_provider()
    query = f"{' '.join(targets['industries'][:3])} {jurisdiction_code} new opening expansion 2024"
    sources = await provider.search(query, max_results=3)

    if sources and any(not s.get("is_demo") for s in sources):
        # Use Gemini to synthesize leads from live sources
        source_text = "\n".join(f"- {s['title']}: {s['snippet']}" for s in sources[:5])
        prompt = f"""From these business sources, identify potential insurance prospects for {brand_slug}.

SOURCES:
{source_text}

TARGET INDUSTRIES: {', '.join(targets['industries'])}
EXPANSION SIGNALS TO LOOK FOR: {', '.join(targets['signals'])}

Return JSON array of leads:
[{{
  "company": "...",
  "industry": "...",
  "location": "...",
  "fit_score": 0-100,
  "signals": ["list of detected signals"],
  "reasoning": "Why this is a good prospect",
  "recommended_message": "Outreach message",
  "signal_type": "EXPANSION|HIRING|REGISTRY|NEWS"
}}]"""

        result = await gemini.generate_json(prompt)
        data = result.get("data", [])
        if isinstance(data, list) and data:
            for lead in data:
                lead["jurisdiction_code"] = jurisdiction_code
                lead["matched_brand"] = brand_slug
                lead["is_demo"] = False
            return {"leads": data, "is_live": True, "model": result.get("model")}

    # Demo fallback
    filtered = [l for l in DEMO_LEADS if l["matched_brand"] == brand_slug]
    if not filtered:
        filtered = DEMO_LEADS[:2]
    return {"leads": filtered, "is_live": False, "model": "demo"}
