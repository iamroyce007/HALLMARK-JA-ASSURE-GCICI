"""HALLMARK — Deterministic Rule Engine.
Pattern/keyword-based compliance checks that run BEFORE LLM analysis.
Rules are configurable and jurisdiction-specific.
"""
import re, json, logging
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger("hallmark.rules")

@dataclass
class RuleViolation:
    rule_code: str
    rule_name: str
    severity: str
    action: str  # BLOCK, REVIEW, WARN
    matched_text: str
    explanation: str
    citation: str = ""

@dataclass
class RuleEngineResult:
    decision: str  # PASS, REVIEW, BLOCK
    violations: list[RuleViolation] = field(default_factory=list)
    rules_checked: int = 0
    rules_passed: int = 0

# ─── Built-in Rule Definitions (Demo) ────────────────────────────────
# These are clearly demo rules, not legal advice.

DEMO_RULES: dict[str, list[dict]] = {
    "GLOBAL": [
        {"code": "GL-ABS-001", "name": "Absolute Guarantee Language", "severity": "CRITICAL",
         "pattern": r"\b(guaranteed?|100%\s*(?:protected|covered|safe)|always covered|never lose|zero risk)\b",
         "action": "BLOCK", "citation": "DEMO POLICY — Absolute claim prohibition"},
        {"code": "GL-ABS-002", "name": "Unconditional Promise", "severity": "HIGH",
         "pattern": r"\b(no questions asked|unconditional(?:ly)?|no matter what|every loss covered)\b",
         "action": "BLOCK", "citation": "DEMO POLICY — Unconditional promise prohibition"},
        {"code": "GL-SUP-001", "name": "Unsupported Superlative", "severity": "HIGH",
         "pattern": r"\b(best in (?:class|market|industry)|number[# ]?1|unbeatable|cheapest|lowest price)\b",
         "action": "REVIEW", "citation": "DEMO POLICY — Superlative claim requires evidence"},
        {"code": "GL-SPD-001", "name": "Speed Guarantee", "severity": "HIGH",
         "pattern": r"\b(instant(?:ly)?\s*(?:payout|claim|settlement)|(?:24|48)\s*(?:hour|hr)\s*(?:payout|guarantee|settlement))\b",
         "action": "BLOCK", "citation": "DEMO POLICY — Turnaround time must be qualified"},
        {"code": "GL-FRE-001", "name": "Misleading Free Language", "severity": "MEDIUM",
         "pattern": r"\b(completely free|free insurance|no cost ever|free coverage)\b",
         "action": "REVIEW", "citation": "DEMO POLICY — 'Free' claim guidelines"},
    ],
    "SG": [
        {"code": "SG-DIS-001", "name": "MAS Intermediary Disclosure", "severity": "HIGH",
         "pattern": None, "action": "REVIEW",
         "check_missing": ["regulated", "licensed", "MAS", "intermediary", "broker"],
         "citation": "DEMO POLICY — MAS Notice 125 intermediary disclosure"},
    ],
    "ID": [
        {"code": "ID-CLM-001", "name": "OJK Banned Claim Terms", "severity": "CRITICAL",
         "pattern": r"\b(pasti\s*cair|pasti\s*ganti|tanpa\s*syarat|jaminan\s*kilat|100%\s*cair)\b",
         "action": "BLOCK", "citation": "DEMO POLICY — SEOJK.05/2020 claims language"},
        {"code": "ID-DIS-001", "name": "OJK Supervisory Disclaimer", "severity": "CRITICAL",
         "pattern": None, "action": "REVIEW",
         "check_missing": ["OJK", "Otoritas Jasa Keuangan", "terdaftar"],
         "citation": "DEMO POLICY — POJK No. 6/2022 supervisory declaration"},
    ],
    "MY": [
        {"code": "MY-SUP-001", "name": "BNM Superlative Prohibition", "severity": "HIGH",
         "pattern": r"\b(terbaik|nombor\s*satu|no\.?\s*1|paling\s*murah)\b",
         "action": "BLOCK", "citation": "DEMO POLICY — BNM/RH/PD 029-2 prohibited conduct"},
    ],
    "HK": [
        {"code": "HK-INV-001", "name": "HKIA Investment Language Ban", "severity": "CRITICAL",
         "pattern": r"\b(investment\s*return|asset\s*growth|capital\s*gain|wealth\s*appreciation|保證增值)\b",
         "action": "BLOCK", "citation": "DEMO POLICY — HKIA GL28 marketing guideline"},
    ],
    "TH": [
        {"code": "TH-WRN-001", "name": "OIC Consumer Warning", "severity": "HIGH",
         "pattern": None, "action": "REVIEW",
         "check_missing": ["ผู้ซื้อควรทำความเข้าใจ", "buyers should understand", "terms and conditions"],
         "citation": "DEMO POLICY — OIC Advertising Notification B.E. 2551"},
    ],
}

def evaluate(text: str, jurisdiction_code: str = "SG") -> RuleEngineResult:
    """Run deterministic rule checks against content text."""
    text_lower = text.lower()
    violations: list[RuleViolation] = []
    rules_checked = 0

    # Check global rules + jurisdiction-specific rules
    rulesets_to_check = [DEMO_RULES.get("GLOBAL", []), DEMO_RULES.get(jurisdiction_code, [])]

    for ruleset in rulesets_to_check:
        for rule in ruleset:
            rules_checked += 1

            if rule.get("pattern"):
                matches = re.findall(rule["pattern"], text_lower, re.IGNORECASE)
                if matches:
                    violations.append(RuleViolation(
                        rule_code=rule["code"],
                        rule_name=rule["name"],
                        severity=rule["severity"],
                        action=rule["action"],
                        matched_text=", ".join(set(m if isinstance(m, str) else m[0] for m in matches[:3])),
                        explanation=f"Deterministic match: prohibited pattern detected",
                        citation=rule["citation"],
                    ))

            elif rule.get("check_missing"):
                # Check if ANY of the required terms are present
                found = any(term.lower() in text_lower for term in rule["check_missing"])
                if not found:
                    violations.append(RuleViolation(
                        rule_code=rule["code"],
                        rule_name=rule["name"],
                        severity=rule["severity"],
                        action=rule["action"],
                        matched_text="[MISSING REQUIRED DISCLOSURE]",
                        explanation=f"Required disclosure not found. Expected one of: {', '.join(rule['check_missing'])}",
                        citation=rule["citation"],
                    ))

    # Determine decision
    has_block = any(v.action == "BLOCK" for v in violations)
    has_review = any(v.action == "REVIEW" for v in violations)

    if has_block:
        decision = "BLOCK"
    elif has_review:
        decision = "REVIEW"
    else:
        decision = "PASS"

    return RuleEngineResult(
        decision=decision,
        violations=violations,
        rules_checked=rules_checked,
        rules_passed=rules_checked - len(violations),
    )

def evaluate_all_jurisdictions(text: str) -> dict[str, RuleEngineResult]:
    """Run rules across all 5 jurisdictions simultaneously."""
    results = {}
    for code in ["SG", "MY", "HK", "ID", "TH"]:
        results[code] = evaluate(text, code)
    return results
