"""HALLMARK — FastAPI Application.
The Trust Engine for Autonomous Insurance Marketing.
"""
import os, json, uuid, asyncio, logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import select, func

from app.db import init_db, async_session
from app.models import (
    Brand, Jurisdiction, RuleSet, Campaign, Asset, AssetStatus,
    Review, ReviewDecision, Correction, Lead, ComplianceResult,
    TrustPassport as TrustPassportModel, RedTeamResult,
    AgentRun, AgentEvent, Analytics, ResearchSignal, Source, Evidence, Opportunity,
)
from app.graph.workflow import run_pipeline, register_listener, unregister_listener, emit_event
from app.rules import engine as rule_engine
from app.memory import correction_store
from app.agents import lead_agent
from app.llm import gemini
from app.seed import seed_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hallmark")

# ─── Lifespan ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🏛️  HALLMARK — Initializing Trust Engine...")
    await init_db()
    result = await seed_all()
    logger.info(f"📦 Seed result: {result}")
    logger.info("✅ HALLMARK ready.")
    yield
    logger.info("🛑 HALLMARK shutting down.")

app = FastAPI(
    title="HALLMARK — Trust Engine",
    description="AI Trust Engine for Autonomous Insurance Marketing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Models ─────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    brand: str = "jade"
    platform: str = "linkedin"
    jurisdiction: str = "SG"
    goal: Optional[str] = None

class ReviewAction(BaseModel):
    decision: str  # APPROVE, EDIT, REJECT
    reason_tag: Optional[str] = None
    reviewer_note: Optional[str] = None
    edited_text: Optional[str] = None

class CorrectionSearch(BaseModel):
    context: str
    brand: Optional[str] = None
    platform: Optional[str] = None
    jurisdiction: Optional[str] = None
    top_k: int = 5

# ─── Health & Status ─────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "operational",
        "engine": "HALLMARK Trust Engine",
        "version": "1.0.0",
        "gemini_live": gemini.is_live(),
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/api/system/status")
async def system_status():
    async with async_session() as session:
        brands = await session.scalar(select(func.count()).select_from(Brand))
        jurisdictions = await session.scalar(select(func.count()).select_from(Jurisdiction))
        campaigns = await session.scalar(select(func.count()).select_from(Campaign))
        corrections = await session.scalar(select(func.count()).select_from(Correction))
        leads = await session.scalar(select(func.count()).select_from(Lead))
    return {
        "status": "operational",
        "gemini_live": gemini.is_live(),
        "brands": brands or 0,
        "jurisdictions": jurisdictions or 0,
        "active_campaigns": campaigns or 0,
        "corrections": corrections or 0,
        "leads": leads or 0,
    }

# ─── Brands & Jurisdictions ─────────────────────────────────────────

@app.get("/api/brands")
async def get_brands():
    async with async_session() as session:
        result = await session.execute(select(Brand))
        brands = result.scalars().all()
        return [{"slug": b.slug, "name": b.name, "category": b.category, "tone": b.tone_description} for b in brands]

@app.get("/api/jurisdictions")
async def get_jurisdictions():
    async with async_session() as session:
        result = await session.execute(select(Jurisdiction))
        jurisdictions = result.scalars().all()
        items = []
        for j in jurisdictions:
            # Get ruleset
            rs = await session.execute(select(RuleSet).where(RuleSet.jurisdiction_id == j.id).order_by(RuleSet.created_at.desc()).limit(1))
            ruleset = rs.scalar_one_or_none()
            items.append({
                "code": j.code,
                "country": j.country,
                "regulator": j.regulator,
                "regulator_full": j.regulator_full,
                "ruleset_version": ruleset.version if ruleset else "N/A",
                "last_verified": ruleset.last_verified.isoformat() if ruleset and ruleset.last_verified else None,
                "is_demo": ruleset.is_demo if ruleset else True,
            })
        return items

# ─── Campaigns ───────────────────────────────────────────────────────

@app.post("/api/campaigns")
async def create_campaign(data: CampaignCreate):
    campaign_id = str(uuid.uuid4())
    async with async_session() as session:
        campaign = Campaign(
            id=campaign_id,
            brand_slug=data.brand,
            jurisdiction_code=data.jurisdiction,
            platform=data.platform,
            title=f"{data.brand} {data.platform} Campaign — {data.jurisdiction}",
            goal=data.goal,
        )
        session.add(campaign)
        await session.commit()
    return {"id": campaign_id, "status": "created"}

@app.get("/api/campaigns")
async def list_campaigns():
    async with async_session() as session:
        result = await session.execute(select(Campaign).order_by(Campaign.created_at.desc()).limit(20))
        campaigns = result.scalars().all()
        return [
            {
                "id": c.id, "brand": c.brand_slug, "jurisdiction": c.jurisdiction_code,
                "platform": c.platform, "title": c.title, "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in campaigns
        ]

@app.post("/api/campaigns/{campaign_id}/run")
async def run_campaign(campaign_id: str):
    """Execute the full HALLMARK pipeline for a campaign."""
    async with async_session() as session:
        campaign = await session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(404, "Campaign not found")

        result = await run_pipeline(
            brand=campaign.brand_slug,
            platform=campaign.platform,
            jurisdiction=campaign.jurisdiction_code,
            campaign_id=campaign_id,
        )

        # Save asset
        content = result.get("draft_content", {})
        passport = result.get("trust_passport", {})
        asset = Asset(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            brand_slug=campaign.brand_slug,
            platform=campaign.platform,
            jurisdiction_code=campaign.jurisdiction_code,
            headline=content.get("headline", ""),
            body=content.get("body", ""),
            cta=content.get("cta", ""),
            hashtags=content.get("hashtags", ""),
            full_content=result.get("full_content", ""),
            status=AssetStatus.PENDING_HUMAN.value if passport.get("overall_status") != "BLOCKED" else AssetStatus.COMPLIANCE_REVIEW.value,
            corrections_applied=len(result.get("retrieved_corrections", [])),
        )
        session.add(asset)

        # Save trust passport
        tp = TrustPassportModel(
            id=str(uuid.uuid4()),
            asset_id=asset.id,
            evidence_count=passport.get("evidence_count", 0),
            claims_count=passport.get("claims_count", 0),
            red_team_status=passport.get("red_team_status", ""),
            rule_engine_status=passport.get("rule_engine_status", ""),
            llm_compliance_status=passport.get("llm_compliance_status", ""),
            confidence=passport.get("confidence", 0),
            human_review_status="PENDING",
            ruleset_version=passport.get("ruleset_version", ""),
            corrections_applied=passport.get("corrections_applied", 0),
            overall_status=passport.get("overall_status", "PENDING"),
            jurisdiction_matrix=result.get("rule_engine_result", {}).get("jurisdiction_matrix", {}),
        )
        session.add(tp)

        # Save red team result
        rt = result.get("red_team_result", {}).get("red_team", {})
        rtr = RedTeamResult(
            id=str(uuid.uuid4()),
            asset_id=asset.id,
            customer_interpretation=rt.get("customer_interpretation", ""),
            implied_promises=rt.get("implied_promises", []),
            overclaim_detected=rt.get("overclaim_detected", False),
            severity=rt.get("severity", "LOW"),
            reason=rt.get("reason", ""),
            suggested_rewrite=rt.get("suggested_rewrite"),
            risk_score=rt.get("risk_score", 0),
            model_used=result.get("red_team_result", {}).get("model", "demo"),
            is_live=result.get("red_team_result", {}).get("is_live", False),
        )
        session.add(rtr)

        # Save compliance result
        fc = result.get("final_compliance", {})
        cr = ComplianceResult(
            id=str(uuid.uuid4()),
            asset_id=asset.id,
            jurisdiction_code=campaign.jurisdiction_code,
            ruleset_version=passport.get("ruleset_version", ""),
            rule_engine_decision=fc.get("rule_engine", "PASS"),
            rule_violations=result.get("rule_engine_result", {}).get("violations", []),
            llm_decision=fc.get("llm_compliance", "PASS"),
            llm_risk_score=fc.get("risk_score", 0),
            llm_confidence=fc.get("confidence", 0),
            llm_explanation=fc.get("explanation", ""),
            final_decision=fc.get("final_decision", "PASS"),
            model_used=result.get("llm_compliance_result", {}).get("model", "demo"),
            is_live=result.get("llm_compliance_result", {}).get("is_live", False),
        )
        session.add(cr)

        campaign.status = "COMPLETED"
        await session.commit()

    return {
        "campaign_id": campaign_id,
        "asset_id": asset.id,
        "content": content,
        "full_content": result.get("full_content", ""),
        "red_team": rt,
        "rule_engine": result.get("rule_engine_result", {}),
        "compliance": fc,
        "trust_passport": passport,
        "corrections_applied": result.get("retrieved_corrections", []),
        "narration": result.get("narration", []),
        "agent_timings": result.get("agent_timings", {}),
        "research": result.get("research", {}),
        "evidence": result.get("evidence", []),
        "sources": result.get("sources", []),
    }

# ─── Quick Demo ─────────────────────────────────────────────────

@app.post("/api/demo/run")
async def run_demo(brand: str = "jade", platform: str = "linkedin", jurisdiction: str = "SG"):
    """One-click demo — creates campaign and runs full pipeline."""
    campaign_id = str(uuid.uuid4())
    async with async_session() as session:
        campaign = Campaign(
            id=campaign_id,
            brand_slug=brand,
            jurisdiction_code=jurisdiction,
            platform=platform,
            title=f"DEMO — {brand} {platform} {jurisdiction}",
            goal="Demo campaign: Competitor Price Shock scenario",
        )
        session.add(campaign)
        await session.commit()

    return await run_campaign(campaign_id)

# ─── Review Queue ────────────────────────────────────────────────────

@app.get("/api/review/queue")
async def review_queue():
    async with async_session() as session:
        result = await session.execute(
            select(Asset).where(Asset.status == AssetStatus.PENDING_HUMAN.value).order_by(Asset.created_at.desc())
        )
        assets = result.scalars().all()
        items = []
        for a in assets:
            # Get trust passport
            tp_result = await session.execute(select(TrustPassportModel).where(TrustPassportModel.asset_id == a.id))
            tp = tp_result.scalar_one_or_none()
            # Get red team result
            rt_result = await session.execute(select(RedTeamResult).where(RedTeamResult.asset_id == a.id))
            rt = rt_result.scalar_one_or_none()
            # Get compliance result
            cr_result = await session.execute(select(ComplianceResult).where(ComplianceResult.asset_id == a.id))
            cr = cr_result.scalar_one_or_none()
            items.append({
                "id": a.id,
                "campaign_id": a.campaign_id,
                "brand": a.brand_slug,
                "platform": a.platform,
                "jurisdiction": a.jurisdiction_code,
                "headline": a.headline,
                "body": a.body,
                "cta": a.cta,
                "full_content": a.full_content,
                "status": a.status,
                "cycle_number": a.cycle_number,
                "corrections_applied": a.corrections_applied,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "trust_passport": {
                    "evidence_count": tp.evidence_count if tp else 0,
                    "claims_count": tp.claims_count if tp else 0,
                    "red_team_status": tp.red_team_status if tp else "",
                    "rule_engine_status": tp.rule_engine_status if tp else "",
                    "llm_compliance_status": tp.llm_compliance_status if tp else "",
                    "confidence": tp.confidence if tp else 0,
                    "ruleset_version": tp.ruleset_version if tp else "",
                    "corrections_applied": tp.corrections_applied if tp else 0,
                    "overall_status": tp.overall_status if tp else "",
                    "jurisdiction_matrix": tp.jurisdiction_matrix if tp else {},
                } if tp else None,
                "red_team": {
                    "customer_interpretation": rt.customer_interpretation if rt else "",
                    "overclaim_detected": rt.overclaim_detected if rt else False,
                    "severity": rt.severity if rt else "",
                    "reason": rt.reason if rt else "",
                    "suggested_rewrite": rt.suggested_rewrite if rt else "",
                } if rt else None,
                "compliance": {
                    "rule_engine_decision": cr.rule_engine_decision if cr else "",
                    "llm_decision": cr.llm_decision if cr else "",
                    "final_decision": cr.final_decision if cr else "",
                    "risk_score": cr.llm_risk_score if cr else 0,
                    "confidence": cr.llm_confidence if cr else 0,
                    "violations": cr.rule_violations if cr else [],
                } if cr else None,
            })
        return items

@app.post("/api/review/{asset_id}/approve")
async def approve_asset(asset_id: str, action: ReviewAction):
    async with async_session() as session:
        asset = await session.get(Asset, asset_id)
        if not asset:
            raise HTTPException(404, "Asset not found")
        if asset.status != AssetStatus.PENDING_HUMAN.value:
            raise HTTPException(400, f"Asset status is {asset.status}, not PENDING_HUMAN")

        review = Review(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            decision=action.decision,
            reason_tag=action.reason_tag,
            reviewer_note=action.reviewer_note,
            edited_text=action.edited_text,
        )
        session.add(review)

        if action.decision == "APPROVE":
            asset.status = AssetStatus.APPROVED.value
            # Update trust passport
            tp_result = await session.execute(select(TrustPassportModel).where(TrustPassportModel.asset_id == asset_id))
            tp = tp_result.scalar_one_or_none()
            if tp:
                tp.human_review_status = "APPROVED"
                tp.overall_status = "READY_TO_PUBLISH"

        elif action.decision == "REJECT":
            asset.status = AssetStatus.REJECTED.value
            # Create correction
            correction_data = await correction_store.store_correction(
                asset_id=asset_id,
                review_id=review.id,
                reason_tag=action.reason_tag or "unknown",
                original_text=asset.full_content or "",
                corrected_text=action.edited_text or "",
                lesson=action.reviewer_note or f"Rejected: {action.reason_tag}",
                brand_slug=asset.brand_slug or "",
                platform=asset.platform or "",
                jurisdiction_code=asset.jurisdiction_code or "",
            )
            if tp := (await session.execute(select(TrustPassportModel).where(TrustPassportModel.asset_id == asset_id))).scalar_one_or_none():
                tp.human_review_status = "REJECTED"
                tp.overall_status = "REJECTED"

        elif action.decision == "EDIT":
            asset.status = AssetStatus.EDITED.value
            if action.edited_text:
                asset.full_content = action.edited_text
            # Also create correction from the edit
            await correction_store.store_correction(
                asset_id=asset_id,
                review_id=review.id,
                reason_tag=action.reason_tag or "edited",
                original_text=asset.full_content or "",
                corrected_text=action.edited_text or "",
                lesson=action.reviewer_note or f"Edited: {action.reason_tag}",
                brand_slug=asset.brand_slug or "",
                platform=asset.platform or "",
                jurisdiction_code=asset.jurisdiction_code or "",
            )

        await session.commit()
        return {"id": asset_id, "status": asset.status, "decision": action.decision}

# ─── Compliance Matrix ───────────────────────────────────────────────

@app.get("/api/compliance/matrix")
async def compliance_matrix():
    """Return the jurisdiction compliance rules matrix."""
    jurisdictions = ["SG", "MY", "HK", "ID", "TH"]
    matrix = {}
    for code in jurisdictions:
        rules = rule_engine.DEMO_RULES.get("GLOBAL", []) + rule_engine.DEMO_RULES.get(code, [])
        matrix[code] = {
            "rules_count": len(rules),
            "rules": [
                {
                    "code": r["code"],
                    "name": r["name"],
                    "severity": r["severity"],
                    "action": r["action"],
                    "citation": r.get("citation", ""),
                    "type": "pattern" if r.get("pattern") else "missing_check",
                }
                for r in rules
            ],
        }
    return {"matrix": matrix, "note": "DEMO POLICY — NOT LEGAL ADVICE"}

@app.post("/api/compliance/check")
async def compliance_check(text: str = "", jurisdiction: str = "SG"):
    """Run deterministic compliance check on arbitrary text."""
    result = rule_engine.evaluate(text, jurisdiction)
    all_results = rule_engine.evaluate_all_jurisdictions(text)
    return {
        "primary": {
            "jurisdiction": jurisdiction,
            "decision": result.decision,
            "violations": [{"rule_code": v.rule_code, "rule_name": v.rule_name, "severity": v.severity, "matched_text": v.matched_text, "citation": v.citation} for v in result.violations],
            "rules_checked": result.rules_checked,
        },
        "all_jurisdictions": {
            code: {
                "decision": r.decision,
                "violations_count": len(r.violations),
            }
            for code, r in all_results.items()
        },
    }

# ─── Corrections ─────────────────────────────────────────────────────

@app.get("/api/corrections")
async def get_corrections():
    return await correction_store.get_all_corrections()

@app.post("/api/corrections/search")
async def search_corrections(data: CorrectionSearch):
    return await correction_store.retrieve_corrections(
        context=data.context,
        brand_slug=data.brand or "",
        platform=data.platform or "",
        jurisdiction_code=data.jurisdiction or "",
        top_k=data.top_k,
    )

# ─── Learning Metrics ────────────────────────────────────────────────

@app.get("/api/learning")
async def learning_metrics():
    return await correction_store.get_learning_metrics()

# ─── Leads ───────────────────────────────────────────────────────────

@app.get("/api/leads")
async def get_leads(brand: Optional[str] = None):
    async with async_session() as session:
        q = select(Lead).order_by(Lead.fit_score.desc())
        if brand:
            q = q.where(Lead.matched_brand == brand)
        result = await session.execute(q.limit(20))
        leads = result.scalars().all()
        return [
            {
                "id": l.id, "company": l.company, "industry": l.industry,
                "location": l.location, "jurisdiction": l.jurisdiction_code,
                "brand": l.matched_brand, "fit_score": l.fit_score,
                "signals": l.signals, "reasoning": l.reasoning,
                "recommended_message": l.recommended_message,
                "signal_type": l.signal_type, "is_demo": l.is_demo,
            }
            for l in leads
        ]

@app.post("/api/leads/discover")
async def discover_leads(brand: str = "jade", jurisdiction: str = "SG"):
    return await lead_agent.run(brand, jurisdiction)

# ─── SSE Event Stream ────────────────────────────────────────────────

@app.get("/api/events/{campaign_id}")
async def event_stream(campaign_id: str):
    """SSE endpoint for live agent narration."""
    queue = register_listener(campaign_id)

    async def generate():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'agent': 'heartbeat', 'message': 'alive'})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            unregister_listener(campaign_id, queue)

    return StreamingResponse(generate(), media_type="text/event-stream")

# ─── Evidence & Regulatory Knowledge Graph ───────────────────────────

from app.graph.knowledge_graph import knowledge_graph

class CypherQuery(BaseModel):
    query: str = "MATCH (r:Regulator)-[:ENFORCES]->(rule:Rule) RETURN r, rule"

@app.get("/api/graph/knowledge")
async def get_knowledge_graph():
    """Retrieve full multi-jurisdictional regulatory & evidence graph."""
    return knowledge_graph.get_graph_data()

@app.post("/api/graph/cypher")
async def run_cypher_query(req: CypherQuery):
    """Execute Cypher query via Neo4j if available or native NetworkX engine."""
    return knowledge_graph.execute_cypher(req.query)

@app.get("/api/evidence")
async def get_evidence():
    async with async_session() as session:
        sources = (await session.execute(select(Source).limit(20))).scalars().all()
        signals = (await session.execute(select(ResearchSignal).limit(20))).scalars().all()
        return {
            "sources": [{"id": s.id, "title": s.title, "url": s.url, "type": s.source_type, "snippet": s.snippet, "is_demo": s.is_demo} for s in sources],
            "signals": [{"id": s.id, "brand": s.brand_slug, "jurisdiction": s.jurisdiction_code, "headline": s.headline, "confidence": s.confidence, "is_demo": s.is_demo} for s in signals],
            "graph": knowledge_graph.get_graph_data(),
        }

# ─── Analytics ───────────────────────────────────────────────────────

@app.get("/api/analytics")
async def get_analytics():
    async with async_session() as session:
        total_campaigns = await session.scalar(select(func.count()).select_from(Campaign))
        total_assets = await session.scalar(select(func.count()).select_from(Asset))
        approved = await session.scalar(select(func.count()).select_from(Asset).where(Asset.status == AssetStatus.APPROVED.value))
        rejected = await session.scalar(select(func.count()).select_from(Asset).where(Asset.status == AssetStatus.REJECTED.value))
        total_corrections = await session.scalar(select(func.count()).select_from(Correction))

    learning = await correction_store.get_learning_metrics()

    return {
        "total_campaigns": total_campaigns or 0,
        "total_assets": total_assets or 0,
        "approved_assets": approved or 0,
        "rejected_assets": rejected or 0,
        "total_corrections": total_corrections or 0,
        "approval_rate": round((approved / total_assets * 100) if total_assets else 0, 1),
        "learning": learning,
    }
