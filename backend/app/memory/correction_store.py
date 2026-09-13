"""HALLMARK — Correction Memory Store.
Embeds corrections, stores in PostgreSQL, retrieves via cosine similarity.
"""
import math, logging
from datetime import datetime
from sqlalchemy import select, text
from app.db import async_session
from app.models import Correction
from app.llm import gemini

logger = logging.getLogger("hallmark.memory")

async def store_correction(
    asset_id: str,
    review_id: str,
    reason_tag: str,
    original_text: str,
    corrected_text: str,
    lesson: str,
    reviewer_note: str = "",
    brand_slug: str = "",
    platform: str = "",
    jurisdiction_code: str = "",
) -> dict:
    """Store a correction with embedding for future retrieval."""
    embed_text = f"{reason_tag}: {lesson}. Original: {original_text[:200]}. Corrected: {corrected_text[:200]}"
    embedding = await gemini.embed_text(embed_text)

    correction = Correction(
        asset_id=asset_id,
        review_id=review_id,
        reason_tag=reason_tag,
        original_text=original_text,
        corrected_text=corrected_text,
        lesson=lesson,
        reviewer_note=reviewer_note,
        brand_slug=brand_slug,
        platform=platform,
        jurisdiction_code=jurisdiction_code,
        embedding=embedding,
    )
    async with async_session() as session:
        session.add(correction)
        await session.commit()
        await session.refresh(correction)
        return {"id": correction.id, "lesson": lesson, "reason_tag": reason_tag}

def _cosine_sim(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(x*x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

async def retrieve_corrections(
    context: str,
    brand_slug: str = "",
    platform: str = "",
    jurisdiction_code: str = "",
    top_k: int = 5,
) -> list[dict]:
    """Retrieve relevant corrections by embedding similarity."""
    query_embedding = await gemini.embed_text(context)

    async with async_session() as session:
        result = await session.execute(select(Correction))
        corrections = result.scalars().all()

    scored = []
    for c in corrections:
        if not c.embedding:
            continue
        sim = _cosine_sim(query_embedding, c.embedding)
        # Boost for matching brand/platform/jurisdiction
        if brand_slug and c.brand_slug == brand_slug:
            sim += 0.1
        if platform and c.platform == platform:
            sim += 0.05
        if jurisdiction_code and c.jurisdiction_code == jurisdiction_code:
            sim += 0.1
        scored.append((sim, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "id": c.id,
            "similarity": round(s, 3),
            "reason_tag": c.reason_tag,
            "lesson": c.lesson,
            "original_text": c.original_text[:200] if c.original_text else "",
            "corrected_text": c.corrected_text[:200] if c.corrected_text else "",
            "brand_slug": c.brand_slug,
            "platform": c.platform,
            "jurisdiction_code": c.jurisdiction_code,
            "times_applied": c.times_applied,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for s, c in scored[:top_k]
    ]

async def get_all_corrections() -> list[dict]:
    async with async_session() as session:
        result = await session.execute(select(Correction).order_by(Correction.created_at.desc()))
        corrections = result.scalars().all()
        return [
            {
                "id": c.id,
                "reason_tag": c.reason_tag,
                "lesson": c.lesson,
                "original_text": c.original_text,
                "corrected_text": c.corrected_text,
                "brand_slug": c.brand_slug,
                "platform": c.platform,
                "jurisdiction_code": c.jurisdiction_code,
                "times_applied": c.times_applied,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in corrections
        ]

async def increment_applied(correction_id: str):
    async with async_session() as session:
        result = await session.execute(select(Correction).where(Correction.id == correction_id))
        c = result.scalar_one_or_none()
        if c:
            c.times_applied = (c.times_applied or 0) + 1
            await session.commit()

async def get_learning_metrics() -> dict:
    """Compute learning metrics from correction data."""
    async with async_session() as session:
        result = await session.execute(select(Correction).order_by(Correction.created_at))
        corrections = list(result.scalars().all())

    if not corrections:
        return {
            "total_corrections": 0,
            "reason_breakdown": {},
            "rejection_trend": [],
            "edit_distance_trend": [],
            "repeated_mistake_rate": 0.0,
        }

    reason_counts = {}
    for c in corrections:
        tag = c.reason_tag or "unknown"
        reason_counts[tag] = reason_counts.get(tag, 0) + 1

    # Simulate cycle-based trends from correction timestamps
    cycles = []
    batch_size = max(1, len(corrections) // 5)
    for i in range(0, len(corrections), batch_size):
        batch = corrections[i:i+batch_size]
        cycles.append({
            "cycle": len(cycles) + 1,
            "rejection_count": len(batch),
            "corrections_in_batch": len(batch),
        })

    return {
        "total_corrections": len(corrections),
        "reason_breakdown": reason_counts,
        "rejection_trend": cycles,
        "most_common_reason": max(reason_counts, key=reason_counts.get) if reason_counts else None,
        "learning_velocity": round(max(0, 100 - len(corrections) * 3), 1),
    }
