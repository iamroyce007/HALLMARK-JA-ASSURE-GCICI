"""HALLMARK — LangGraph State Machine.
Real stateful workflow orchestrating all agents.
"""
import time, uuid, logging, asyncio
from typing import TypedDict, Any, Optional, Literal
from datetime import datetime
from langgraph.graph import StateGraph, END

from app.agents import research_agent, content_agent, red_team_agent, compliance_agent, localization_agent
from app.rules import engine as rule_engine
from app.memory import correction_store

logger = logging.getLogger("hallmark.graph")

# ─── State Definition ────────────────────────────────────────────────

class HallmarkState(TypedDict, total=False):
    # Identity
    campaign_id: str
    brand: str
    platform: str
    jurisdiction: str

    # Research
    research: dict
    evidence: list
    opportunity: dict
    sources: list

    # Content
    draft_content: dict
    full_content: str

    # Red Team
    red_team_result: dict

    # Compliance
    rule_engine_result: dict
    llm_compliance_result: dict
    final_compliance: dict

    # Correction Memory
    retrieved_corrections: list

    # Localization
    localization_results: list

    # Trust Passport
    trust_passport: dict

    # Human Review
    human_decision: dict

    # Analytics
    analytics: dict

    # Narration / events
    narration: list
    agent_timings: dict

    # Control
    needs_repair: bool
    cycle_number: int
    error: str

# ─── Event Emitter ────────────────────────────────────────────────────

# Global event queue for SSE streaming
_event_listeners: dict[str, list] = {}

def register_listener(campaign_id: str) -> asyncio.Queue:
    q = asyncio.Queue()
    _event_listeners.setdefault(campaign_id, []).append(q)
    return q

def unregister_listener(campaign_id: str, q: asyncio.Queue):
    if campaign_id in _event_listeners:
        _event_listeners[campaign_id] = [x for x in _event_listeners[campaign_id] if x is not q]

async def emit_event(campaign_id: str, agent: str, message: str, data: dict = None):
    event = {
        "agent": agent,
        "message": message,
        "data": data or {},
        "timestamp": datetime.utcnow().isoformat(),
    }
    for q in _event_listeners.get(campaign_id, []):
        await q.put(event)

# ─── Node Functions ──────────────────────────────────────────────────

async def research_node(state: HallmarkState) -> dict:
    t0 = time.time()
    cid = state.get("campaign_id", "")
    await emit_event(cid, "Research Agent", "Scanning market intelligence...")

    result = await research_agent.run(
        brand_slug=state["brand"],
        jurisdiction_code=state["jurisdiction"],
    )

    signal = result.get("signal", {})
    sources = result.get("sources", [])
    evidence = [{"claim": c, "snippet": c} for c in signal.get("key_claims", [])]

    await emit_event(cid, "Research Agent", f"Signal detected: {signal.get('signal', 'Market signal')}", {"confidence": signal.get("confidence", 0)})

    return {
        "research": result,
        "evidence": evidence,
        "sources": sources,
        "opportunity": signal,
        "narration": state.get("narration", []) + [{"agent": "Research Agent", "message": f"Detected: {signal.get('signal', '')}"}],
        "agent_timings": {**state.get("agent_timings", {}), "research": round((time.time() - t0) * 1000)},
    }

async def retrieve_corrections_node(state: HallmarkState) -> dict:
    t0 = time.time()
    cid = state.get("campaign_id", "")
    await emit_event(cid, "Correction Memory", "Searching past lessons...")

    context = f"{state['brand']} {state['platform']} {state['jurisdiction']} {state.get('opportunity', {}).get('signal', '')}"
    corrections = await correction_store.retrieve_corrections(
        context=context,
        brand_slug=state["brand"],
        platform=state["platform"],
        jurisdiction_code=state["jurisdiction"],
    )

    msg = f"{len(corrections)} relevant corrections retrieved" if corrections else "No past corrections found"
    await emit_event(cid, "Correction Memory", msg, {"count": len(corrections)})

    return {
        "retrieved_corrections": corrections,
        "narration": state.get("narration", []) + [{"agent": "Correction Memory", "message": msg}],
        "agent_timings": {**state.get("agent_timings", {}), "corrections": round((time.time() - t0) * 1000)},
    }

async def content_node(state: HallmarkState) -> dict:
    t0 = time.time()
    cid = state.get("campaign_id", "")
    cycle = state.get("cycle_number", 1)
    await emit_event(cid, "Content Agent", f"Generating {state['brand']}/{state['platform']} content (cycle {cycle})...")

    result = await content_agent.run(
        brand_slug=state["brand"],
        platform=state["platform"],
        jurisdiction_code=state["jurisdiction"],
        opportunity=state.get("opportunity", {}),
        evidence=state.get("evidence", []),
        corrections=state.get("retrieved_corrections", []),
    )

    content = result.get("content", {})
    full_content = content.get("full_content", content.get("body", ""))

    await emit_event(cid, "Content Agent", f"Generated: \"{content.get('headline', 'Content')}\"", {"corrections_used": result.get("corrections_used", 0)})

    return {
        "draft_content": content,
        "full_content": full_content,
        "narration": state.get("narration", []) + [{"agent": "Content Agent", "message": f"Created {state['platform']} content for {state['brand']}"}],
        "agent_timings": {**state.get("agent_timings", {}), "content": round((time.time() - t0) * 1000)},
    }

async def red_team_node(state: HallmarkState) -> dict:
    t0 = time.time()
    cid = state.get("campaign_id", "")
    await emit_event(cid, "Red Team Agent", "Simulating skeptical customer...")

    result = await red_team_agent.run(
        content_text=state.get("full_content", ""),
        brand_slug=state["brand"],
        jurisdiction_code=state["jurisdiction"],
        evidence=state.get("evidence", []),
    )

    rt = result.get("red_team", {})
    severity = rt.get("severity", "LOW")
    overclaim = rt.get("overclaim_detected", False)

    msg = f"Overclaim detected (severity: {severity})" if overclaim else "No significant overclaims found"
    await emit_event(cid, "Red Team Agent", msg, {"severity": severity, "overclaim": overclaim})

    return {
        "red_team_result": result,
        "needs_repair": overclaim and severity in ("HIGH", "CRITICAL"),
        "narration": state.get("narration", []) + [{"agent": "Red Team", "message": msg}],
        "agent_timings": {**state.get("agent_timings", {}), "red_team": round((time.time() - t0) * 1000)},
    }

async def deterministic_rules_node(state: HallmarkState) -> dict:
    t0 = time.time()
    cid = state.get("campaign_id", "")
    await emit_event(cid, "Rule Engine", f"Running deterministic rules for {state['jurisdiction']}...")

    result = rule_engine.evaluate(state.get("full_content", ""), state["jurisdiction"])

    # Also evaluate against all jurisdictions for the matrix
    all_results = rule_engine.evaluate_all_jurisdictions(state.get("full_content", ""))

    rule_dict = {
        "decision": result.decision,
        "violations": [
            {
                "rule_code": v.rule_code,
                "rule_name": v.rule_name,
                "severity": v.severity,
                "action": v.action,
                "matched_text": v.matched_text,
                "explanation": v.explanation,
                "citation": v.citation,
            }
            for v in result.violations
        ],
        "rules_checked": result.rules_checked,
        "rules_passed": result.rules_passed,
        "jurisdiction_matrix": {
            code: {
                "decision": r.decision,
                "violations_count": len(r.violations),
                "violations": [{"rule_code": v.rule_code, "rule_name": v.rule_name, "severity": v.severity, "action": v.action, "matched_text": v.matched_text} for v in r.violations],
            }
            for code, r in all_results.items()
        },
    }

    await emit_event(cid, "Rule Engine", f"{state['jurisdiction']}: {result.decision} ({result.rules_checked} rules checked)", {"decision": result.decision})

    return {
        "rule_engine_result": rule_dict,
        "narration": state.get("narration", []) + [{"agent": "Rule Engine", "message": f"{state['jurisdiction']} → {result.decision}"}],
        "agent_timings": {**state.get("agent_timings", {}), "rule_engine": round((time.time() - t0) * 1000)},
    }

async def llm_compliance_node(state: HallmarkState) -> dict:
    t0 = time.time()
    cid = state.get("campaign_id", "")
    await emit_event(cid, "Compliance Agent", "Running semantic compliance analysis...")

    result = await compliance_agent.run(
        content_text=state.get("full_content", ""),
        jurisdiction_code=state["jurisdiction"],
        brand_slug=state["brand"],
        rule_engine_result=state.get("rule_engine_result", {}),
        red_team_result=state.get("red_team_result", {}),
        evidence=state.get("evidence", []),
    )

    comp = result.get("compliance", {})
    await emit_event(cid, "Compliance Agent", f"LLM Review: {comp.get('decision', 'N/A')} (confidence: {comp.get('confidence', 0):.0%})")

    # Compute final decision per spec logic
    re_decision = state.get("rule_engine_result", {}).get("decision", "PASS")
    rt_severity = state.get("red_team_result", {}).get("red_team", {}).get("severity", "LOW")
    llm_confidence = comp.get("confidence", 1.0)
    unsupported = comp.get("unsupported_claims", [])

    if re_decision == "BLOCK":
        final = "BLOCK"
    elif rt_severity in ("HIGH", "CRITICAL"):
        final = "REVIEW"
    elif llm_confidence < 0.6:
        final = "REVIEW"
    elif unsupported:
        final = "REVIEW"
    elif comp.get("decision") == "BLOCK":
        final = "BLOCK"
    else:
        final = comp.get("decision", "PASS")

    final_compliance = {
        "final_decision": final,
        "rule_engine": re_decision,
        "llm_compliance": comp.get("decision", "PASS"),
        "red_team_severity": rt_severity,
        "confidence": comp.get("confidence", 0),
        "risk_score": comp.get("risk_score", 0),
        "explanation": comp.get("explanation", ""),
    }

    return {
        "llm_compliance_result": result,
        "final_compliance": final_compliance,
        "narration": state.get("narration", []) + [{"agent": "Compliance", "message": f"Final: {final}"}],
        "agent_timings": {**state.get("agent_timings", {}), "llm_compliance": round((time.time() - t0) * 1000)},
    }

async def trust_passport_node(state: HallmarkState) -> dict:
    t0 = time.time()
    cid = state.get("campaign_id", "")
    await emit_event(cid, "Trust Passport", "Generating governance passport...")

    rt = state.get("red_team_result", {}).get("red_team", {})
    fc = state.get("final_compliance", {})
    re = state.get("rule_engine_result", {})

    passport = {
        "asset_brand": state["brand"],
        "asset_platform": state["platform"],
        "jurisdiction": state["jurisdiction"],
        "campaign_id": state.get("campaign_id", ""),
        "evidence_count": len(state.get("evidence", [])),
        "claims_count": len(state.get("draft_content", {}).get("claims", [])),
        "red_team_status": "PASS" if not rt.get("overclaim_detected") else rt.get("severity", "REVIEW"),
        "rule_engine_status": re.get("decision", "PASS"),
        "llm_compliance_status": fc.get("llm_compliance", "PASS"),
        "confidence": fc.get("confidence", 0),
        "ruleset_version": f"{state['jurisdiction']}-v1.2",
        "corrections_applied": len(state.get("retrieved_corrections", [])),
        "human_review_status": "PENDING",
        "overall_status": "PENDING_HUMAN" if fc.get("final_decision") != "BLOCK" else "BLOCKED",
        "jurisdiction_matrix": re.get("jurisdiction_matrix", {}),
        "cycle_number": state.get("cycle_number", 1),
        "generated_at": datetime.utcnow().isoformat(),
    }

    await emit_event(cid, "Trust Passport", f"Passport generated — Status: {passport['overall_status']}")

    return {
        "trust_passport": passport,
        "narration": state.get("narration", []) + [{"agent": "Trust Passport", "message": f"Status: {passport['overall_status']}"}],
        "agent_timings": {**state.get("agent_timings", {}), "trust_passport": round((time.time() - t0) * 1000)},
    }

# ─── Conditional Edges ───────────────────────────────────────────────

def should_repair(state: HallmarkState) -> Literal["repair", "continue"]:
    if state.get("needs_repair") and state.get("cycle_number", 1) <= 3:
        return "repair"
    return "continue"

# ─── Graph Builder ───────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Build the HALLMARK LangGraph workflow."""
    graph = StateGraph(HallmarkState)

    # Add nodes
    graph.add_node("research", research_node)
    graph.add_node("retrieve_corrections", retrieve_corrections_node)
    graph.add_node("content", content_node)
    graph.add_node("red_team", red_team_node)
    graph.add_node("deterministic_rules", deterministic_rules_node)
    graph.add_node("llm_compliance", llm_compliance_node)
    graph.add_node("trust_passport", trust_passport_node)

    # Linear flow
    graph.set_entry_point("research")
    graph.add_edge("research", "retrieve_corrections")
    graph.add_edge("retrieve_corrections", "content")
    graph.add_edge("content", "red_team")
    graph.add_edge("red_team", "deterministic_rules")
    graph.add_edge("deterministic_rules", "llm_compliance")
    graph.add_edge("llm_compliance", "trust_passport")
    graph.add_edge("trust_passport", END)

    return graph.compile()

# Compiled graph singleton
workflow = build_graph()

async def run_pipeline(brand: str, platform: str, jurisdiction: str, campaign_id: str = None, cycle: int = 1) -> dict:
    """Execute the full HALLMARK pipeline."""
    if not campaign_id:
        campaign_id = str(uuid.uuid4())

    initial_state: HallmarkState = {
        "campaign_id": campaign_id,
        "brand": brand,
        "platform": platform,
        "jurisdiction": jurisdiction,
        "narration": [],
        "agent_timings": {},
        "cycle_number": cycle,
        "needs_repair": False,
    }

    await emit_event(campaign_id, "Orchestrator", f"Starting HALLMARK pipeline: {brand}/{platform}/{jurisdiction}")

    try:
        final_state = await workflow.ainvoke(initial_state)
        await emit_event(campaign_id, "Orchestrator", "Pipeline complete", {"status": "COMPLETE"})
        return dict(final_state)
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        await emit_event(campaign_id, "Orchestrator", f"Pipeline error: {str(e)}", {"status": "ERROR"})
        return {**initial_state, "error": str(e)}
