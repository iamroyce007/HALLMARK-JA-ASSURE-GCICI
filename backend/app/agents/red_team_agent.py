"""HALLMARK — Red Team Agent.
Adversarial 'Skeptical Customer' simulation that evaluates content
from a confused customer's perspective.
"""
from app.llm import gemini

async def run(content_text: str, brand_slug: str, jurisdiction_code: str, evidence: list[dict] = None) -> dict:
    """Simulate a skeptical customer encountering this content with no context."""
    evidence_ctx = ""
    if evidence:
        evidence_ctx = "ACTUAL EVIDENCE AVAILABLE:\n" + "\n".join(f"- {e.get('claim', e.get('snippet', ''))}" for e in evidence[:5])

    prompt = f"""You are a skeptical, confused customer who just encountered this insurance marketing content with NO prior context about the product or company.

CONTENT:
\"\"\"{content_text}\"\"\"

BRAND: {brand_slug}
MARKET: {jurisdiction_code}

{evidence_ctx}

TASK:
1. Read the content as a regular person would.
2. State what you THINK is being promised to you.
3. Identify any claims that seem too good to be true.
4. Check if the content implies guarantees that insurance products typically cannot make.
5. Assess if an average consumer could be misled.

Return JSON:
{{
  "customer_interpretation": "In plain language, what did the customer think they were being promised?",
  "implied_promises": ["list of specific promises the customer believes were made"],
  "overclaim_detected": true/false,
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "risk_score": 0.0-1.0,
  "reason": "Why this is or isn't a problem",
  "problematic_phrases": ["exact phrases that are risky"],
  "suggested_rewrite": "A safer version if overclaim detected, or null"
}}"""

    result = await gemini.generate_json(prompt, system_instruction="You are a consumer protection advocate. Be thorough and skeptical.", model="gemini-2.0-flash")

    data = result.get("data", {})
    if not data.get("customer_interpretation"):
        # Analyze content for common overclaim patterns
        text_lower = content_text.lower()
        has_guarantee = any(w in text_lower for w in ["guaranteed", "guarantee", "100%", "always", "never"])
        has_absolute = any(w in text_lower for w in ["complete protection", "full coverage", "every loss", "no risk"])

        if has_guarantee or has_absolute:
            data = {
                "customer_interpretation": "The customer believes they are being promised absolute, unconditional protection with no exceptions or limitations.",
                "implied_promises": ["Complete coverage for all losses", "No exclusions or conditions"],
                "overclaim_detected": True,
                "severity": "HIGH",
                "risk_score": 0.78,
                "reason": "Absolute language creates an implied guarantee that no insurance product can actually deliver. A reasonable consumer would interpret this as unconditional coverage.",
                "problematic_phrases": [p for p in ["guaranteed", "complete protection", "always covered", "100%"] if p in text_lower],
                "suggested_rewrite": "Consider using qualified language: 'designed to provide comprehensive coverage' instead of absolute claims.",
            }
        else:
            data = {
                "customer_interpretation": "The customer understands this as a professional insurance offering with specific coverage for their industry segment.",
                "implied_promises": ["Professional coverage available", "Industry expertise"],
                "overclaim_detected": False,
                "severity": "LOW",
                "risk_score": 0.15,
                "reason": "Content uses appropriately qualified language without making absolute or unconditional promises.",
                "problematic_phrases": [],
                "suggested_rewrite": None,
            }

    return {
        "red_team": data,
        "is_live": result.get("is_live", False),
        "model": result.get("model", "demo"),
    }
