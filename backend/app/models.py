"""HALLMARK — Complete SQLAlchemy ORM Models.
All tables for the InsurTech Trust Engine.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, DateTime, JSON,
    ForeignKey, Index, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db import Base
import enum

def gen_uuid():
    return str(uuid.uuid4())

def now():
    return datetime.utcnow()

# ─── Enums ───────────────────────────────────────────────────────────

class AssetStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RED_TEAMED = "RED_TEAMED"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    LOCALIZED = "LOCALIZED"
    PENDING_HUMAN = "PENDING_HUMAN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDITED = "EDITED"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    ANALYZED = "ANALYZED"

class ReviewDecision(str, enum.Enum):
    APPROVE = "APPROVE"
    EDIT = "EDIT"
    REJECT = "REJECT"

class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ComplianceDecision(str, enum.Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"

# ─── Brands ──────────────────────────────────────────────────────────

class Brand(Base):
    __tablename__ = "brands"
    id = Column(String, primary_key=True, default=gen_uuid)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(200))
    tone_description = Column(Text)
    target_audience = Column(Text)
    forbidden_phrases = Column(JSON, default=list)
    mandatory_grounding = Column(JSON, default=list)
    created_at = Column(DateTime, default=now)

# ─── Jurisdictions & Compliance Rules ────────────────────────────────

class Jurisdiction(Base):
    __tablename__ = "jurisdictions"
    id = Column(String, primary_key=True, default=gen_uuid)
    code = Column(String(10), unique=True, nullable=False)
    country = Column(String(100), nullable=False)
    regulator = Column(String(50), nullable=False)
    regulator_full = Column(String(300))
    governing_codes = Column(JSON, default=list)
    created_at = Column(DateTime, default=now)

class RuleSet(Base):
    __tablename__ = "rulesets"
    id = Column(String, primary_key=True, default=gen_uuid)
    jurisdiction_id = Column(String, ForeignKey("jurisdictions.id"))
    version = Column(String(20), nullable=False)
    effective_date = Column(DateTime)
    last_verified = Column(DateTime)
    is_demo = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=now)

class Rule(Base):
    __tablename__ = "rules"
    id = Column(String, primary_key=True, default=gen_uuid)
    ruleset_id = Column(String, ForeignKey("rulesets.id"))
    rule_code = Column(String(50), nullable=False)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="HIGH")
    rule_type = Column(String(50), default="keyword")  # keyword, pattern, semantic
    pattern = Column(Text)  # regex or keyword list JSON
    action = Column(String(20), default="BLOCK")  # BLOCK, REVIEW, WARN
    source_url = Column(Text)
    source_title = Column(Text)
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

# ─── Research & Evidence ─────────────────────────────────────────────

class Source(Base):
    __tablename__ = "sources"
    id = Column(String, primary_key=True, default=gen_uuid)
    url = Column(Text)
    title = Column(String(500))
    snippet = Column(Text)
    source_type = Column(String(50))  # web, news, registry, manual
    retrieved_at = Column(DateTime, default=now)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

class ResearchSignal(Base):
    __tablename__ = "research_signals"
    id = Column(String, primary_key=True, default=gen_uuid)
    brand_slug = Column(String(50))
    jurisdiction_code = Column(String(10))
    signal_type = Column(String(100))
    headline = Column(String(500))
    what_changed = Column(Text)
    why_it_matters = Column(Text)
    recommended_action = Column(Text)
    confidence = Column(Float, default=0.0)
    sources = Column(JSON, default=list)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(String, primary_key=True, default=gen_uuid)
    signal_id = Column(String, ForeignKey("research_signals.id"), nullable=True)
    source_id = Column(String, ForeignKey("sources.id"), nullable=True)
    claim = Column(Text)
    supporting_text = Column(Text)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=now)

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(String, primary_key=True, default=gen_uuid)
    signal_id = Column(String, ForeignKey("research_signals.id"), nullable=True)
    brand_slug = Column(String(50))
    jurisdiction_code = Column(String(10))
    title = Column(String(500))
    description = Column(Text)
    recommended_angle = Column(Text)
    evidence_ids = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=now)

# ─── Campaigns & Assets ──────────────────────────────────────────────

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True, default=gen_uuid)
    brand_slug = Column(String(50), nullable=False)
    jurisdiction_code = Column(String(10), nullable=False)
    platform = Column(String(50), nullable=False)
    title = Column(String(500))
    goal = Column(Text)
    opportunity_id = Column(String, ForeignKey("opportunities.id"), nullable=True)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, default=gen_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    brand_slug = Column(String(50))
    platform = Column(String(50))
    jurisdiction_code = Column(String(10))
    headline = Column(Text)
    body = Column(Text)
    cta = Column(Text)
    hashtags = Column(Text)
    full_content = Column(Text)
    status = Column(String(50), default=AssetStatus.DRAFT.value)
    cycle_number = Column(Integer, default=1)
    corrections_applied = Column(Integer, default=0)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class AssetClaim(Base):
    __tablename__ = "asset_claims"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    claim_text = Column(Text)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=True)
    is_supported = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

# ─── Red Team & Compliance ───────────────────────────────────────────

class RedTeamResult(Base):
    __tablename__ = "red_team_results"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    customer_interpretation = Column(Text)
    implied_promises = Column(JSON, default=list)
    overclaim_detected = Column(Boolean, default=False)
    severity = Column(String(20), default="LOW")
    reason = Column(Text)
    suggested_rewrite = Column(Text)
    risk_score = Column(Float, default=0.0)
    model_used = Column(String(100))
    is_live = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

class ComplianceResult(Base):
    __tablename__ = "compliance_results"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    jurisdiction_code = Column(String(10))
    ruleset_version = Column(String(20))
    # Deterministic rule engine
    rule_engine_decision = Column(String(20), default="PASS")
    rule_violations = Column(JSON, default=list)
    # LLM compliance
    llm_decision = Column(String(20), default="PASS")
    llm_risk_score = Column(Float, default=0.0)
    llm_confidence = Column(Float, default=0.0)
    llm_explanation = Column(Text)
    llm_violations = Column(JSON, default=list)
    # Combined
    final_decision = Column(String(20), default="PASS")
    model_used = Column(String(100))
    is_live = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

# ─── Trust Passport ──────────────────────────────────────────────────

class TrustPassport(Base):
    __tablename__ = "trust_passports"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    evidence_count = Column(Integer, default=0)
    claims_count = Column(Integer, default=0)
    red_team_status = Column(String(20))
    rule_engine_status = Column(String(20))
    llm_compliance_status = Column(String(20))
    confidence = Column(Float, default=0.0)
    human_review_status = Column(String(20))
    ruleset_version = Column(String(20))
    corrections_applied = Column(Integer, default=0)
    overall_status = Column(String(50), default="PENDING")
    jurisdiction_matrix = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now)

# ─── Localization ────────────────────────────────────────────────────

class Localization(Base):
    __tablename__ = "localizations"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    language = Column(String(50))
    locale_code = Column(String(10))
    jurisdiction_code = Column(String(10))
    headline = Column(Text)
    body = Column(Text)
    cta = Column(Text)
    full_content = Column(Text)
    compliance_recheck_status = Column(String(20))
    red_team_recheck_status = Column(String(20))
    created_at = Column(DateTime, default=now)

# ─── Human Review ────────────────────────────────────────────────────

class Review(Base):
    __tablename__ = "reviews"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    decision = Column(String(20))
    reason_tag = Column(String(50))
    reviewer_note = Column(Text)
    edited_text = Column(Text)
    created_at = Column(DateTime, default=now)

# ─── Correction Memory ──────────────────────────────────────────────

class Correction(Base):
    __tablename__ = "corrections"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)
    review_id = Column(String, ForeignKey("reviews.id"), nullable=True)
    reason_tag = Column(String(50))
    original_text = Column(Text)
    corrected_text = Column(Text)
    lesson = Column(Text)
    reviewer_note = Column(Text)
    brand_slug = Column(String(50))
    platform = Column(String(50))
    jurisdiction_code = Column(String(10))
    embedding = Column(JSON)  # Store as JSON array (no pgvector extension needed)
    times_applied = Column(Integer, default=0)
    created_at = Column(DateTime, default=now)

# ─── Leads ───────────────────────────────────────────────────────────

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, default=gen_uuid)
    company = Column(String(300))
    industry = Column(String(200))
    location = Column(String(200))
    jurisdiction_code = Column(String(10))
    matched_brand = Column(String(50))
    fit_score = Column(Float, default=0.0)
    signals = Column(JSON, default=list)
    reasoning = Column(Text)
    recommended_message = Column(Text)
    signal_type = Column(String(100))  # JOB_POSTING, REGISTRY, EXPANSION, etc.
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

# ─── Publishing & Analytics ──────────────────────────────────────────

class PublishingJob(Base):
    __tablename__ = "publishing_jobs"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    channel = Column(String(50))
    scheduled_time = Column(DateTime)
    status = Column(String(50), default="QUEUED")
    external_id = Column(String(200))
    created_at = Column(DateTime, default=now)

class Analytics(Base):
    __tablename__ = "analytics"
    id = Column(String, primary_key=True, default=gen_uuid)
    asset_id = Column(String, ForeignKey("assets.id"))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    leads_generated = Column(Integer, default=0)
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

# ─── Agent Operations ────────────────────────────────────────────────

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(String, primary_key=True, default=gen_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    agent_name = Column(String(100))
    status = Column(String(50), default="RUNNING")
    started_at = Column(DateTime, default=now)
    finished_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    model_used = Column(String(100))
    input_summary = Column(Text)
    output_summary = Column(Text)
    token_usage = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

class AgentEvent(Base):
    __tablename__ = "agent_events"
    id = Column(String, primary_key=True, default=gen_uuid)
    run_id = Column(String, ForeignKey("agent_runs.id"), nullable=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    agent_name = Column(String(100))
    event_type = Column(String(50))  # STARTED, PROGRESS, COMPLETED, ERROR
    message = Column(Text)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=now)
