"""
Reverse-Signal Buying Intent Feeds & Corporate Registry Intelligence
Detects public hiring vacancies, company registry updates (ACRA / SSM / AHU), and risk triggers.
"""

from typing import List, Dict, Any

REVERSE_SIGNAL_LEADS: List[Dict[str, Any]] = [
    {
        "id": "lead-sg-01",
        "company": "Lee Hwa Fine Jewels & Specie Pte Ltd",
        "jurisdiction": "SG",
        "industry": "Luxury Fine Jewellery & High-End Gems",
        "intent_score": 96,
        "signal_type": "JOB_POSTING_ALERT",
        "signal_title": "Hiring: Senior Vault & Armored Transit Risk Manager",
        "signal_source": "LinkedIn Talent Insights / MyCareersFuture SG",
        "signal_detail": "Company posted urgent opening for 'Senior Vault & Armored Transit Risk Manager' handling >$15M SGD monthly diamond transfers between Singapore FreePort and Orchard boutique.",
        "matched_brand": "jade",
        "recommended_action": "Outbound campaign for Jade Specie & Armored Courier Insurance + Transit endorsements.",
        "status": "HOT_LEAD",
        "detected_at": "2026-09-15 14:20:00"
    },
    {
        "id": "lead-sg-02",
        "company": "Novena Advanced Spine & Aesthetic Surgery Centre",
        "jurisdiction": "SG",
        "industry": "Specialist Private Healthcare & Surgery",
        "intent_score": 92,
        "signal_type": "REGISTRY_EXPANSION_ALERT",
        "signal_title": "ACRA & MOH Filing: 3 New Orthopaedic & Spine Surgeons Appointed",
        "signal_source": "MOH Specialist Register & ACRA Corporate Filings",
        "signal_detail": "Added 3 high-risk endoscopic spine surgeons to private practice registry. Malpractice exposure increased by estimated $10M liability limit.",
        "matched_brand": "doctorshield",
        "recommended_action": "Targeted DoctorShield Medical Malpractice & Group Defence Package briefing.",
        "status": "HOT_LEAD",
        "detected_at": "2026-09-15 11:45:00"
    },
    {
        "id": "lead-my-01",
        "company": "Malacca Straits Vault & Secure Logistics Sdn Bhd",
        "jurisdiction": "MY",
        "industry": "Armored Freight & Precious Metal Custody",
        "intent_score": 89,
        "signal_type": "CUSTOMS_LICENSE_ALERT",
        "signal_title": "SSM Filing: New Bonded Precious Metal Facility in Port of Tanjung Pelepas",
        "signal_source": "Suruhanjaya Syarikat Malaysia (SSM) & Royal Malaysian Customs",
        "signal_detail": "Obtained customs authorization for Class-A bonded high-security bullion storage facility in Johor.",
        "matched_brand": "jaguar_transit",
        "recommended_action": "Jaguar Transit institutional specie cargo coverage proposal.",
        "status": "QUALIFIED",
        "detected_at": "2026-09-14 09:30:00"
    },
    {
        "id": "lead-id-01",
        "company": "PT Nusantara Digital Medika",
        "jurisdiction": "ID",
        "industry": "Telemedicine & HealthTech Platform",
        "intent_score": 94,
        "signal_type": "FINANCING_AND_COMPLIANCE",
        "signal_title": "Series-A $8M USD Raise + OJK Electronic System Compliance Mandate",
        "signal_source": "TechInAsia / OJK Fintech Notification",
        "signal_detail": "Platform holds health data for 1.2M users; required by Indonesian Data Protection Law (UU PDP) to secure cyber liability coverage.",
        "matched_brand": "cybershield",
        "recommended_action": "CyberShield SME Enterprise & Data Breach Defence proposal (Bahasa Indonesia).",
        "status": "HOT_LEAD",
        "detected_at": "2026-09-13 16:15:00"
    }
]
