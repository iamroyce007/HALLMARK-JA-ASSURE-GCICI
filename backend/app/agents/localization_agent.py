"""HALLMARK — Localization Agent.
Cultural adaptation + compliance re-check for translated content.
"""
from app.llm import gemini

LANGUAGES = {
    "SG": {"primary": "en", "name": "English"},
    "MY": {"primary": "ms", "name": "Malay"},
    "ID": {"primary": "id", "name": "Bahasa Indonesia"},
    "TH": {"primary": "th", "name": "Thai"},
    "HK": {"primary": "zh", "name": "Traditional Chinese"},
}

async def run(content_text: str, source_jurisdiction: str, target_jurisdiction: str, brand_slug: str) -> dict:
    """Localize content for a target jurisdiction with cultural adaptation."""
    target_lang = LANGUAGES.get(target_jurisdiction, {"primary": "en", "name": "English"})

    prompt = f"""Localize this insurance marketing content for the {target_jurisdiction} market.

ORIGINAL CONTENT ({source_jurisdiction}):
\"\"\"{content_text}\"\"\"

TARGET LANGUAGE: {target_lang['name']} ({target_lang['primary']})
TARGET MARKET: {target_jurisdiction}
BRAND: {brand_slug}

IMPORTANT RULES:
1. This is NOT simple translation — culturally adapt the message.
2. Adjust tone for local market expectations.
3. Use locally appropriate insurance terminology.
4. Preserve the core message but make it feel native.
5. Do NOT translate brand names.
6. Maintain all compliance-safe language (avoid guarantees, absolutes).
7. Add any locally required disclaimers or disclosures.

Return JSON:
{{
  "headline": "Localized headline",
  "body": "Localized body content",
  "cta": "Localized call to action",
  "full_content": "Complete localized content",
  "adaptation_notes": ["What was culturally adapted and why"],
  "terminology_changes": ["Insurance terms that were adapted"],
  "added_disclaimers": ["Any locally required disclaimers added"]
}}"""

    result = await gemini.generate_json(
        prompt,
        system_instruction=f"You are a professional insurance content localizer for the {target_jurisdiction} market. Produce culturally native content.",
    )

    data = result.get("data", {})
    if not data.get("headline"):
        # Demo fallback localization
        data = {
            "headline": f"[{target_lang['name']}] {content_text[:50]}...",
            "body": f"[Localized for {target_jurisdiction}] {content_text[:300]}",
            "cta": "Learn more →",
            "full_content": f"[{target_jurisdiction} Localization]\n{content_text}",
            "adaptation_notes": [f"Adapted tone for {target_jurisdiction} market", f"Translated to {target_lang['name']}"],
            "terminology_changes": ["Insurance terms adapted for local regulations"],
            "added_disclaimers": [],
        }

    return {
        "localization": data,
        "source_jurisdiction": source_jurisdiction,
        "target_jurisdiction": target_jurisdiction,
        "language": target_lang["name"],
        "is_live": result.get("is_live", False),
        "model": result.get("model", "demo"),
    }
