"""HALLMARK — LLM Compliance Agent.
Semantic compliance analysis via Gemini, runs AFTER deterministic rule engine.
"""
from app.llm import gemini

async def run(
    content_text: str,
    jurisdiction_code: str,
    brand_slug: str,
    rule_engine_result: dict,
    red_team_result: dict,
    evidence: list[dict] = None,
) -> dict:
    """LLM-based semantic compliance analysis."""
    evidence_ctx = ""
    if evidence:
        evidence_ctx = "EVIDENCE AVAILABLE:\n" + "\n".join(f"- {e.get('claim', e.get('snippet', ''))}" for e in evidence[:5])

    rule_ctx = ""
    if rule_engine_result.get("violations"):
        rule_ctx = "DETERMINISTIC RULE VIOLATIONS ALREADY FOUND:\n" + "\n".join(
            f"- [{v.get('rule_code', '')}] {v.get('rule_name', '')}: {v.get('matched_text', '')}" for v in rule_engine_result["violations"]
        )

    red_team_ctx = ""
    if red_team_result:
        rt = red_team_result.get("red_team", red_team_result)
        red_team_ctx = f"""RED TEAM FINDINGS:
Customer interpretation: {rt.get('customer_interpretation', 'N/A')}
Overclaim detected: {rt.get('overclaim_detected', False)}
Severity: {rt.get('severity', 'N/A')}"""

    jurisdictions_info = {
        "SG": "Singapore — Regulated by MAS (Monetary Authority of Singapore). Key: no misleading claims, intermediary disclosure required.",
        "MY": "Malaysia — Regulated by BNM (Bank Negara Malaysia). Key: no superlatives, fair dealing guidelines.",
        "HK": "Hong Kong — Regulated by HKIA (Insurance Authority). Key: no investment return language for insurance, clear disclaimers.",
        "ID": "Indonesia — Regulated by OJK (Otoritas Jasa Keuangan). Key: strict ban on 'pasti' guarantees, supervisory banners required.",
        "TH": "Thailand — Regulated by OIC (Office of Insurance Commission). Key: consumer understanding warnings required.",
    }
    jurisdiction_info = jurisdictions_info.get(jurisdiction_code, f"Jurisdiction: {jurisdiction_code}")

    prompt = f"""You are a compliance officer reviewing insurance marketing content for regulatory adherence.

CONTENT:
\"\"\"{content_text}\"\"\"

JURISDICTION: {jurisdiction_info}
BRAND: {brand_slug}

{rule_ctx}

{red_team_ctx}

{evidence_ctx}

TASK:
1. Analyze semantic meaning — could this mislead a consumer?
2. Check for implied claims beyond what the evidence supports.
3. Check ambiguous language that could be interpreted as a guarantee.
4. Assess jurisdiction-specific compliance requirements.
5. Verify evidence supports all claims made.

IMPORTANT: This is a DEMO system with example policies. Do NOT claim these are actual regulatory decisions.

Return JSON:
{{
  "decision": "PASS|REVIEW|BLOCK",
  "risk_score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "violations": [
    {{
      "type": "semantic|implied|ambiguity|unsupported|jurisdiction",
      "description": "...",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "problematic_text": "...",
      "suggested_fix": "..."
    }}
  ],
  "unsupported_claims": ["list of claims without evidence"],
  "explanation": "Brief overall assessment",
  "suggested_rewrite": "If issues found, a compliant version. Null if passing."
}}"""

    result = await gemini.generate_json(
        prompt,
        system_instruction="You are a regulatory compliance expert. Be thorough but fair. This is a DEMO system — label all findings as demo analysis.",
        model="gemini-2.0-flash",
        temperature=0.1,
    )

    data = result.get("data", {})
    if not data.get("decision"):
        # Deterministic fallback analysis
        text_lower = content_text.lower()
        violations = []
        risk = 0.1

        if any(w in text_lower for w in ["guaranteed", "guarantee", "100%"]):
            violations.append({
                "type": "semantic",
                "description": "Absolute guarantee language detected",
                "severity": "HIGH",
                "problematic_text": "guarantee/absolute language",
                "suggested_fix": "Replace with qualified language",
            })
            risk = 0.8

        if red_team_result and red_team_result.get("red_team", {}).get("overclaim_detected"):
            risk = max(risk, 0.6)

        data = {
            "decision": "BLOCK" if risk > 0.7 else "REVIEW" if risk > 0.3 else "PASS",
            "risk_score": risk,
            "confidence": 0.75,
            "violations": violations,
            "unsupported_claims": [],
            "explanation": "Demo compliance analysis based on pattern matching.",
            "suggested_rewrite": None,
        }

    return {
        "compliance": data,
        "jurisdiction": jurisdiction_code,
        "is_live": result.get("is_live", False),
        "model": result.get("model", "demo"),
    }
