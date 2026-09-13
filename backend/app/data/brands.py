"""
Brand Profiles & Grounding Knowledge Base for JA Assure Portfolio
"""

from typing import Dict, Any

BRAND_PROFILES: Dict[str, Any] = {
    "jade": {
        "id": "jade",
        "name": "Jade by JA Assure",
        "category": "Jewellery, Diamonds & High-Value Specie Insurance",
        "target_audience": "Master jewellers, diamond merchants, high-net-worth collectors, private vault owners",
        "tone_voice": "Refined, prestigious, bespoke, reassuring, uncompromising on craftsmanship and security",
        "primary_platforms": ["Instagram", "WeChat", "Luxury Portals", "Private Client Newsletters"],
        "forbidden_phrases": [
            "Cheap insurance", "instant payout no questions asked", "discount policy",
            "pasti cair", "100% guaranteed settlement within hours"
        ],
        "mandatory_grounding": [
            "Coverage tailored for bespoke fine jewellery, high-carat diamonds, and rare gemstones",
            "Worldwide transit, exhibition, and vault coverage",
            "Subject to verified appraisal certificate and policy terms & conditions",
            "JA Assure operates as a licensed specialist insurance intermediary"
        ],
        "example_cta": "Request a Private Vault & Specie Consultation with JA Assure Specialists."
    },
    "doctorshield": {
        "id": "doctorshield",
        "name": "DoctorShield",
        "category": "Medical Professional Indemnity & Malpractice Defence",
        "target_audience": "Specialist surgeons, aesthetic medical doctors, private clinic groups, dental practitioners",
        "tone_voice": "Authoritative, clinical, peer-to-peer, legally fortified, objective, protective of medical careers",
        "primary_platforms": ["LinkedIn", "Medical Journals", "Direct Specialist Portals"],
        "forbidden_phrases": [
            "Never get sued", "foolproof malpractice cover", "zero risk",
            "payout guaranteed regardless of negligence", "cheapest indemnity"
        ],
        "mandatory_grounding": [
            "Medico-legal defence costs covered up to policy limits",
            "Access to senior medical litigation legal counsel from day one",
            "Retroactive date protection for prior unbroken indemnity",
            "Policy underwritten by leading A-rated insurance carriers via JA Assure"
        ],
        "example_cta": "Review your medico-legal defence limits with a DoctorShield Advisor."
    },
    "jaguar_transit": {
        "id": "jaguar_transit",
        "name": "Jaguar Transit",
        "category": "High-Value Cargo, Armored Transport & Specie Logistics",
        "target_audience": "Secure logistics operators, bonded warehouse managers, precious metal couriers",
        "tone_voice": "Tactical, institutional, engineering-driven, risk-hardened, direct",
        "primary_platforms": ["LinkedIn", "Logistics Executive Networks", "Trade Portals"],
        "forbidden_phrases": [
            "Never lose a package", "100% claim guarantee", "instant reimbursement"
        ],
        "mandatory_grounding": [
            "All-risks transit coverage from origin vault to destination handover",
            "Includes armored vehicle, air-freight, and bonded custody stages",
            "Subject to security protocols and telemetry tracking clauses"
        ],
        "example_cta": "Secure your high-value logistics corridor today."
    },
    "cybershield": {
        "id": "cybershield",
        "name": "CyberShield by JA Assure",
        "category": "SME Cyber Extortion, Business Interruption & Data Breach",
        "target_audience": "Fintech CEOs, healthcare clinic chains, SME founders across ASEAN",
        "tone_voice": "Data-driven, urgent, pragmatic, risk-aware, breach-response focused",
        "primary_platforms": ["LinkedIn", "Twitter/X", "Tech Newsletters"],
        "forbidden_phrases": [
            "100% unhackable", "guaranteed zero downtime", "we pay all ransoms instantly"
        ],
        "mandatory_grounding": [
            "Incident response team deployed within 60 minutes of notified breach",
            "Covers forensic investigation, regulatory fines (where insurable), and business interruption loss",
            "Underwritten in compliance with national cyber security agency guidelines"
        ],
        "example_cta": "Assess your cyber vulnerability exposure with CyberShield."
    }
}
