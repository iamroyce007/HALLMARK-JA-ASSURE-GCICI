"""HALLMARK — Content Agent.
Brand-voice, platform-native content generation with correction memory.
"""
from app.llm import gemini

BRAND_VOICES = {
    "jade": {
        "name": "Jade",
        "full_name": "Jade Jewellers Block Insurance",
        "tone": "Sophisticated, trustworthy, premium, concise. Speak to discerning jewellery professionals who understand value.",
        "forbidden": ["cheap", "bargain", "deal", "budget", "mass market"],
        "style": "Elegant. Minimal. Every word carries weight. Premium language.",
    },
    "jaguar_transit": {
        "name": "Jaguar Transit",
        "full_name": "Jaguar Transit High-Value Goods Insurance",
        "tone": "Operational, risk-aware, professional, B2B. Direct and data-driven.",
        "forbidden": ["fun", "exciting", "amazing", "incredible"],
        "style": "Technical. Precise. Risk-quantified. Professional.",
    },
    "doctorshield": {
        "name": "DoctorShield",
        "full_name": "DoctorShield Medical Professional Indemnity",
        "tone": "Professional, empathetic, credible, medical-industry appropriate.",
        "forbidden": ["lawsuit-proof", "sue-proof", "guaranteed protection", "never worry"],
        "style": "Authoritative yet empathetic. Evidence-based. Clinically credible.",
    },
}

PLATFORM_SPECS = {
    "linkedin": {
        "format": "Professional insight post. 200-400 words. Open with a hook insight. Include data point. End with CTA.",
        "char_limit": 3000,
    },
    "instagram": {
        "format": "Visual-first. Carousel-friendly. Short punchy text. 100-150 words. Hashtag suggestions.",
        "char_limit": 2200,
    },
    "x": {
        "format": "Hook-first. Under 280 chars. Thread-ready. Punchy.",
        "char_limit": 280,
    },
    "blog": {
        "format": "Educational article. 500-800 words. Structured with headers. Insight-driven.",
        "char_limit": 5000,
    },
    "email": {
        "format": "Personalized B2B outreach. Concise. 150-250 words. Clear CTA.",
        "char_limit": 2000,
    },
    "reel": {
        "format": "20-45 second video script with: hook (3s), scenes, voiceover, captions, CTA.",
        "char_limit": 500,
    },
}

async def run(
    brand_slug: str,
    platform: str,
    jurisdiction_code: str,
    opportunity: dict,
    evidence: list[dict],
    corrections: list[dict] = None,
) -> dict:
    """Generate platform-native, brand-voice content."""
    voice = BRAND_VOICES.get(brand_slug, BRAND_VOICES["jade"])
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["linkedin"])

    # Build corrections context
    corrections_ctx = ""
    if corrections:
        corrections_ctx = "\n\nPAST CORRECTIONS TO APPLY (LEARN FROM THESE):\n"
        for i, c in enumerate(corrections[:5], 1):
            corrections_ctx += f"{i}. [{c.get('reason_tag', '')}] {c.get('lesson', '')}\n"
            if c.get('original_text'):
                corrections_ctx += f"   AVOID: \"{c['original_text'][:100]}\"\n"
            if c.get('corrected_text'):
                corrections_ctx += f"   PREFER: \"{c['corrected_text'][:100]}\"\n"

    evidence_ctx = "\n".join(f"- {e.get('claim', e.get('snippet', ''))}" for e in evidence[:5])

    prompt = f"""Create marketing content for {voice['full_name']}.

BRAND VOICE: {voice['tone']}
STYLE: {voice['style']}
FORBIDDEN WORDS/PHRASES: {', '.join(voice.get('forbidden', []))}

PLATFORM: {platform.upper()}
FORMAT: {spec['format']}
CHARACTER LIMIT: {spec['char_limit']}

TARGET MARKET: {jurisdiction_code}

OPPORTUNITY:
Signal: {opportunity.get('signal', 'Market opportunity detected')}
Why It Matters: {opportunity.get('why_it_matters', '')}
Recommended Action: {opportunity.get('recommended_action', '')}

EVIDENCE:
{evidence_ctx}
{corrections_ctx}

IMPORTANT:
- Do NOT use absolute guarantees ("guaranteed", "100% protected", "always covered")
- Do NOT make claims that cannot be supported by the evidence
- Include a clear but non-aggressive call-to-action
- Adapt language for {jurisdiction_code} market

Return JSON:
{{
  "headline": "...",
  "body": "...",
  "cta": "...",
  "hashtags": "...",
  "full_content": "The complete post/content as it would appear",
  "claims": ["list of factual claims made in the content"],
  "evidence_used": ["which evidence points were used"]
}}"""

    result = await gemini.generate_json(prompt, system_instruction=f"You are a premium insurance marketing copywriter for {voice['name']}. Never use guarantee language.")

    content = result.get("data", {})
    if not content.get("headline"):
        # Demo fallback content
        demo_contents = {
            "jade": {
                "linkedin": {
                    "headline": "When Market Rates Rise, Coverage Clarity Matters More",
                    "body": f"Lloyd's syndicates have adjusted specie deductibles by 25% this quarter.\n\nFor jewellers carrying SGD 2.8 billion in collective inventory across Singapore, understanding exactly what your policy covers — and what it doesn't — is no longer optional.\n\nJade Jewellers Block was designed for this moment.\n\nTransparent coverage terms. Clear deductible structures. Expert claims guidance from specialists who understand the trade.\n\nBecause in a hardening market, the most valuable thing a jeweller can have isn't the lowest premium — it's the clearest policy.\n\n📞 Speak with a Jade specialist.",
                    "cta": "Request a coverage review →",
                    "hashtags": "#JewelleryInsurance #SpecieInsurance #JewellersBlock #Singapore #RiskManagement",
                    "full_content": "When Market Rates Rise, Coverage Clarity Matters More\n\nLloyd's syndicates have adjusted specie deductibles by 25% this quarter.\n\nFor jewellers carrying SGD 2.8 billion in collective inventory across Singapore, understanding exactly what your policy covers — and what it doesn't — is no longer optional.\n\nJade Jewellers Block was designed for this moment.\n\nTransparent coverage terms. Clear deductible structures. Expert claims guidance from specialists who understand the trade.\n\nBecause in a hardening market, the most valuable thing a jeweller can have isn't the lowest premium — it's the clearest policy.\n\n📞 Speak with a Jade specialist.\n\n#JewelleryInsurance #SpecieInsurance #JewellersBlock #Singapore #RiskManagement",
                    "claims": ["Lloyd's deductibles increased 25%", "SGD 2.8B collective inventory"],
                    "evidence_used": ["Specie rate increase", "SJA market report"],
                },
            },
        }
        platform_content = demo_contents.get(brand_slug, {}).get(platform)
        if not platform_content:
            platform_content = {
                "headline": f"{voice['name']}: Navigating Market Changes with Confidence",
                "body": f"Market conditions are evolving. {voice['name']} provides the coverage clarity professionals need in a changing landscape. Our specialist team understands your industry — and your risks.\n\nContact us for a tailored coverage review.",
                "cta": "Learn more →",
                "hashtags": f"#{voice['name'].replace(' ', '')} #Insurance #{jurisdiction_code}",
                "full_content": "",
                "claims": [],
                "evidence_used": [],
            }
        content = platform_content

    return {
        "content": content,
        "brand": voice["name"],
        "platform": platform,
        "corrections_used": len(corrections) if corrections else 0,
        "is_live": result.get("is_live", False),
        "model": result.get("model", "demo"),
    }
