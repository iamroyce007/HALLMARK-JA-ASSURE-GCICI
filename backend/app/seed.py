"""HALLMARK — Demo Data Seeder.
Seeds the database with realistic demo data for hackathon demonstrations.
"""
import uuid
from datetime import datetime, timedelta
from app.db import async_session
from app.models import (
    Brand, Jurisdiction, RuleSet, Rule, Source, ResearchSignal,
    Evidence, Opportunity, Correction, Lead, Campaign, Asset, Analytics,
)

async def seed_all():
    """Seed all demo data. Idempotent — checks before inserting."""
    async with async_session() as session:
        # Check if already seeded
        from sqlalchemy import select, func
        count = await session.scalar(select(func.count()).select_from(Brand))
        if count and count > 0:
            return {"status": "already_seeded", "brands": count}

        # ─── Brands ──────────────────────────
        brands = [
            Brand(id=str(uuid.uuid4()), slug="jade", name="Jade", category="Jewellers Block Insurance",
                  tone_description="Sophisticated, trustworthy, premium, concise",
                  target_audience="High-end jewellery retailers, wholesalers, gem dealers"),
            Brand(id=str(uuid.uuid4()), slug="jaguar_transit", name="Jaguar Transit", category="High-Value Goods Transit Insurance",
                  tone_description="Operational, risk-aware, professional, B2B",
                  target_audience="Logistics companies, courier services, luxury goods transporters"),
            Brand(id=str(uuid.uuid4()), slug="doctorshield", name="DoctorShield", category="Medical Professional Indemnity",
                  tone_description="Professional, empathetic, credible, medical-industry appropriate",
                  target_audience="Medical practitioners, clinic owners, specialists"),
        ]
        session.add_all(brands)

        # ─── Jurisdictions ───────────────────
        jurisdictions = [
            Jurisdiction(id=str(uuid.uuid4()), code="SG", country="Singapore", regulator="MAS",
                         regulator_full="Monetary Authority of Singapore"),
            Jurisdiction(id=str(uuid.uuid4()), code="MY", country="Malaysia", regulator="BNM",
                         regulator_full="Bank Negara Malaysia"),
            Jurisdiction(id=str(uuid.uuid4()), code="HK", country="Hong Kong", regulator="HKIA",
                         regulator_full="Hong Kong Insurance Authority"),
            Jurisdiction(id=str(uuid.uuid4()), code="ID", country="Indonesia", regulator="OJK",
                         regulator_full="Otoritas Jasa Keuangan"),
            Jurisdiction(id=str(uuid.uuid4()), code="TH", country="Thailand", regulator="OIC",
                         regulator_full="Office of Insurance Commission"),
        ]
        session.add_all(jurisdictions)

        # ─── RuleSets ──────────────────────
        for j in jurisdictions:
            ruleset = RuleSet(
                id=str(uuid.uuid4()), jurisdiction_id=j.id, version="v1.2",
                effective_date=datetime(2024, 1, 1), last_verified=datetime.utcnow(),
                is_demo=True, notes="DEMO POLICY — NOT LEGAL ADVICE",
            )
            session.add(ruleset)

        # ─── Demo Sources ───────────────────
        sources = [
            Source(id=str(uuid.uuid4()), url="https://www.insuranceinsider.com/asia/specie-rates-2024",
                   title="Lloyd's Specie Syndicate Raises APAC Diamond Dealer Rates by 18%",
                   snippet="Leading Lloyd's syndicates have increased minimum vault specie deductibles by 25% and base premiums by 18%.",
                   source_type="news", is_demo=True),
            Source(id=str(uuid.uuid4()), url="https://www.sma.org.sg/indemnity-updates-2024",
                   title="MPS Introduces Mandatory Excess for Aesthetic Surgery Claims",
                   snippet="MPS has introduced a new mandatory $25,000 excess on aesthetic surgery malpractice claims.",
                   source_type="news", is_demo=True),
            Source(id=str(uuid.uuid4()), url="https://www.sja.org.sg/market-report-q3-2024",
                   title="Singapore Jewellers Association — Record High-Value Inventory Levels",
                   snippet="Aggregate jewellery inventory values have reached SGD 2.8 billion, a 34% increase year-on-year.",
                   source_type="market", is_demo=True),
            Source(id=str(uuid.uuid4()), url="https://www.ojk.go.id/regulation/seojk-05-2024",
                   title="OJK Tightens Digital Insurance Marketing Rules",
                   snippet="Indonesia's OJK strictly prohibits 'pasti' (guaranteed) or unqualified speed-of-settlement claims in digital marketing.",
                   source_type="regulatory", is_demo=True),
        ]
        session.add_all(sources)

        # ─── Demo Signals ───────────────────
        sig1 = ResearchSignal(
            id=str(uuid.uuid4()), brand_slug="jade", jurisdiction_code="SG",
            signal_type="COMPETITOR_PRICING",
            headline="Competitor specie rates surge 18% across APAC",
            what_changed="Lloyd's syndicates increased minimum deductibles by 25% and base premiums by 18%",
            why_it_matters="Creates positioning opportunity for Jade to highlight stable pricing and transparent coverage",
            recommended_action="Create content highlighting pricing transparency and comprehensive coverage",
            confidence=0.94, is_demo=True,
        )
        session.add(sig1)

        # ─── Demo Corrections (Learning Loop) ────
        reason_tags = [
            ("overclaim", "Avoid absolute guarantee language", "Get complete protection with guaranteed peace of mind.",
             "Explore comprehensive protection designed for your specific needs.", "jade", "linkedin", "SG"),
            ("too_salesy", "Jade prefers understated premium language over aggressive sales",
             "AMAZING DEAL! Don't miss this incredible opportunity!!!",
             "Discover specialist coverage crafted for the jewellery trade.", "jade", "instagram", "SG"),
            ("wrong_cta", "LinkedIn CTA should invite professional consultation not urgency",
             "ACT NOW! Limited time offer!",
             "Schedule a specialist consultation →", "jade", "linkedin", "SG"),
            ("off_brand", "DoctorShield tone must be empathetic not fear-based",
             "Without indemnity you could lose everything!",
             "Medical indemnity provides the professional foundation that allows you to focus on patient care.", "doctorshield", "linkedin", "SG"),
            ("inaccurate_claim", "Do not cite specific coverage percentages unless verified",
             "We cover 95% of all medical malpractice scenarios.",
             "Our coverage is designed to address the most common professional indemnity scenarios.", "doctorshield", "blog", "SG"),
            ("compliance_risk", "Indonesia OJK prohibits any 'pasti' guarantee language",
             "Perlindungan pasti untuk dokter Indonesia.",
             "Perlindungan profesional yang dirancang untuk praktisi medis Indonesia.", "doctorshield", "instagram", "ID"),
            ("too_long", "Instagram content must be concise — under 150 words",
             "A very long paragraph about insurance coverage...",
             "Short, impactful specialist content.", "jaguar_transit", "instagram", "MY"),
            ("bad_localization", "Thai content needs proper honorific register",
             "Direct informal Thai translation.",
             "Properly registers Thai translation with ครับ/ค่ะ.", "jade", "instagram", "TH"),
        ]

        from app.llm import gemini
        for i, (tag, lesson, orig, corrected, brand, platform, jur) in enumerate(reason_tags):
            embed_text = f"{tag}: {lesson}. Original: {orig[:200]}. Corrected: {corrected[:200]}"
            embedding = await gemini.embed_text(embed_text)
            correction = Correction(
                id=str(uuid.uuid4()),
                reason_tag=tag,
                original_text=orig,
                corrected_text=corrected,
                lesson=lesson,
                brand_slug=brand,
                platform=platform,
                jurisdiction_code=jur,
                embedding=embedding,
                times_applied=max(0, 12 - i * 2),
                created_at=datetime.utcnow() - timedelta(days=30 - i * 3),
            )
            session.add(correction)

        # ─── Demo Leads ─────────────────────
        leads = [
            Lead(id=str(uuid.uuid4()), company="Brilliance Gems Pte Ltd", industry="Precious Stones Wholesale",
                 location="Singapore", jurisdiction_code="SG", matched_brand="jade", fit_score=92,
                 signals=["Expanded to 3 new retail locations", "Inventory SGD 45M", "Hiring security"],
                 reasoning="Rapid expansion with significant inventory growth.", signal_type="EXPANSION", is_demo=True),
            Lead(id=str(uuid.uuid4()), company="SwiftCargo Asia", industry="High-Value Logistics",
                 location="Malaysia", jurisdiction_code="MY", matched_brand="jaguar_transit", fit_score=87,
                 signals=["New temperature-controlled fleet", "Cross-border route launched"],
                 reasoning="Entering high-value cargo segment.", signal_type="SERVICE_EXPANSION", is_demo=True),
            Lead(id=str(uuid.uuid4()), company="Dr. Sarah Lim Aesthetics", industry="Aesthetic Surgery",
                 location="Singapore", jurisdiction_code="SG", matched_brand="doctorshield", fit_score=94,
                 signals=["Second clinic at Novena", "Added injectable treatments"],
                 reasoning="Multi-location aesthetic practice with high MPI risk.", signal_type="PRACTICE_EXPANSION", is_demo=True),
        ]
        session.add_all(leads)

        await session.commit()
        return {"status": "seeded", "brands": 3, "jurisdictions": 5, "corrections": len(reason_tags), "leads": len(leads)}

if __name__ == "__main__":
    import asyncio
    from app.db import init_db

    async def main():
        print("Initializing database tables...")
        await init_db()
        print("Seeding demo data...")
        result = await seed_all()
        print("Seeding complete:", result)

    asyncio.run(main())

