"""
Jurisdiction Matrix & Regulatory Rubrics for JA Assure operations across:
- Singapore (MAS - Monetary Authority of Singapore)
- Malaysia (BNM - Bank Negara Malaysia)
- Hong Kong (HKIA - Insurance Authority)
- Indonesia (OJK - Otoritas Jasa Keuangan)
- Thailand (OIC - Office of Insurance Commission)
"""

from typing import Dict, List, Any

JURISDICTIONS = {
    "SG": {
        "country": "Singapore",
        "regulator": "MAS",
        "regulator_full": "Monetary Authority of Singapore",
        "governing_codes": [
            "Insurance Conduct of Business Guidelines (Notice 125)",
            "MAS Financial Advisers Act (Cap. 110)",
            "Singapore Code of Advertising Practice (SCAP)"
        ],
        "current_version": "v2.4 (Aug 2024)",
        "rules": [
            {
                "id": "SG-RULE-01",
                "name": "Mandatory Intermediary Disclosure",
                "description": "Marketing must state JA Assure is a registered exempt corporate insurance broker/coverholder.",
                "severity": "HIGH",
                "keywords": ["regulated by MAS", "licensed broker", "JA Assure Pte Ltd"]
            },
            {
                "id": "SG-RULE-02",
                "name": "Conditional Claim Settlement",
                "description": "Speed of settlement (e.g. 'settled in 24h') must be qualified by 'subject to completed documentation and policy terms'.",
                "severity": "CRITICAL",
                "keywords": ["instant payout", "guaranteed 24h", "no questions asked", "unconditional"]
            },
            {
                "id": "SG-RULE-03",
                "name": "Product Exclusion Visibility",
                "description": "Key exclusions (e.g. unattended vehicle, wear & tear) cannot be obscured in footnotes.",
                "severity": "MEDIUM",
                "keywords": ["covers everything", "all risks without exception"]
            }
        ]
    },
    "MY": {
        "country": "Malaysia",
        "regulator": "BNM",
        "regulator_full": "Bank Negara Malaysia",
        "governing_codes": [
            "Policy Document on Prohibited Business Conduct (BNM/RH/PD 029-2)",
            "Financial Services Act 2013 (FSA)",
            "Takaful and Insurance Advertising Code 2022"
        ],
        "current_version": "v2.2 (Jan 2024)",
        "rules": [
            {
                "id": "MY-RULE-01",
                "name": "Prohibition of Superlatives",
                "description": "Words such as 'No. 1', 'Best in Malaysia', 'Cheapest' prohibited without audited regulatory citation.",
                "severity": "HIGH",
                "keywords": ["terbaik", "no. 1", "nombor satu", "cheapest in malaysia", "paling murah"]
            },
            {
                "id": "MY-RULE-02",
                "name": "Dual-Language Transparency",
                "description": "Key coverage summaries in digital ads targeting consumer SMEs must offer Bahasa Melayu equivalency.",
                "severity": "MEDIUM",
                "keywords": ["syarat & terma", "tertakluk kepada polisi"]
            },
            {
                "id": "MY-RULE-03",
                "name": "Ombudsman for Financial Services Citation",
                "description": "Must cite availability of dispute resolution via Ombudsman for Financial Services (OFS).",
                "severity": "LOW",
                "keywords": ["OFS", "Ombudsman Perkhidmatan Kewangan"]
            }
        ]
    },
    "HK": {
        "country": "Hong Kong",
        "regulator": "HKIA",
        "regulator_full": "Insurance Authority of Hong Kong",
        "governing_codes": [
            "Guideline on Benefit Illustrations and Marketing (GL28)",
            "Code of Conduct for Licensed Insurance Intermediaries",
            "Trade Descriptions Ordinance (Cap. 362)"
        ],
        "current_version": "v3.0 (Mar 2024)",
        "rules": [
            {
                "id": "HK-RULE-01",
                "name": "Clear Separation of Pure Specie vs Investment",
                "description": "High-value jewellery insurance must never be marketed as value-appreciation or asset preservation investment.",
                "severity": "CRITICAL",
                "keywords": ["investment return", "asset growth", "guaranteed value upside", "保證增值"]
            },
            {
                "id": "HK-RULE-02",
                "name": "Licensed Intermediary License Number",
                "description": "IA License number must be prominently shown on digital collateral.",
                "severity": "HIGH",
                "keywords": ["IA License", "持牌保險中介人"]
            },
            {
                "id": "HK-RULE-03",
                "name": "Cooling-Off & ICCB Notification",
                "description": "Clear disclosure on complaints referral to Insurance Complaints Bureau.",
                "severity": "MEDIUM",
                "keywords": ["ICCB", "Insurance Complaints Bureau", "保險投訴局"]
            }
        ]
    },
    "ID": {
        "country": "Indonesia",
        "regulator": "OJK",
        "regulator_full": "Otoritas Jasa Keuangan",
        "governing_codes": [
            "Surat Edaran OJK No. 19/SEOJK.05/2020 on Marketing & Transparency",
            "Peraturan OJK No. 6/POJK.07/2022 on Consumer Protection in Financial Services",
            "Undang-Undang Perasuransian No. 40/2014"
        ],
        "current_version": "v2.5 (June 2024)",
        "rules": [
            {
                "id": "ID-RULE-01",
                "name": "Strict Prohibition on Absolute Claim Terms (Pasti Cair / Tercepat)",
                "description": "OJK strictly forbids phrases implying guaranteed claim acceptance ('pasti cair', 'pasti ganti', 'tanpa syarat', '24 jam pasti selesai'). Claims must state 'klaim diproses sesuai ketentuan polis'.",
                "severity": "CRITICAL",
                "keywords": ["pasti cair", "pasti ganti", "tanpa syarat", "jaminan kilat", "instant approval", "100% cair"]
            },
            {
                "id": "ID-RULE-02",
                "name": "Mandatory OJK Supervised Disclaimer",
                "description": "All Indonesian market promotional materials MUST include: 'PT JA Assure Terdaftar dan Diawasi oleh Otoritas Jasa Keuangan (OJK)'.",
                "severity": "CRITICAL",
                "keywords": ["Terdaftar dan Diawasi oleh Otoritas Jasa Keuangan", "OJK"]
            },
            {
                "id": "ID-RULE-03",
                "name": "Comparative Advertising Ban",
                "description": "Direct negative comparison against other Indonesian licensed general insurers (Asuransi Astra, Sinarmas, etc.) is prohibited.",
                "severity": "HIGH",
                "keywords": ["lebih baik dari kompetitor", "lebih murah dari asuransi lain"]
            }
        ]
    },
    "TH": {
        "country": "Thailand",
        "regulator": "OIC",
        "regulator_full": "Office of Insurance Commission",
        "governing_codes": [
            "OIC Notification on Principles, Methods and Conditions for Advertising B.E. 2551",
            "Non-Life Insurance Act B.E. 2535 (and amendments)",
            "Consumer Protection Act B.E. 2522"
        ],
        "current_version": "v2.0 (Feb 2024)",
        "rules": [
            {
                "id": "TH-RULE-01",
                "name": "Mandatory Consumer Warning Statement",
                "description": "Must include official OIC warning: 'ผู้ซื้อควรทำความเข้าใจในรายละเอียดความคุ้มครองและเงื่อนไขก่อนตัดสินใจทำประกันภัยทุกครั้ง' (Buyers should understand details of coverage and conditions before purchasing).",
                "severity": "CRITICAL",
                "keywords": ["ผู้ซื้อควรทำความเข้าใจในรายละเอียดความคุ้มครอง", "ก่อนตัดสินใจทำประกันภัย"]
            },
            {
                "id": "TH-RULE-02",
                "name": "Clear Premium Indication",
                "description": "Rates cannot state 'from 0 Baht' or deceptive starting prices without full baseline parameters.",
                "severity": "HIGH",
                "keywords": ["ฟรี", "0 บาท", "ไม่มีเงื่อนไข"]
            }
        ]
    }
}

REGULATORY_CHANGELOG = [
    {
        "version": "v2.5",
        "date": "2024-06-15",
        "regulator": "OJK (Indonesia)",
        "change_type": "MAJOR TIGHTENING",
        "title": "SEOJK.05/2024 Strict Claims Language Enforcement",
        "summary": "Prohibits any digital asset from using 'pasti' or 'guaranteed speed' claims. Requires prominent OJK supervisory banner in minimum 10pt equivalent.",
        "impact_example": "A post stating 'Fast claims within 24 hours for jewellers' was PASS in v1.0, but is now a CRITICAL VIOLATION in v2.5."
    },
    {
        "version": "v2.4",
        "date": "2024-08-01",
        "regulator": "MAS (Singapore)",
        "change_type": "UPDATE",
        "title": "Notice 125 Digital Intermediary Transparency",
        "summary": "Mandates explicit mention of brokerage / coverholder capacity in digital carousels and influencer partnerships.",
        "impact_example": "Jade by JA Assure posts must include coverholder disclosure on the first slide or caption body."
    },
    {
        "version": "v3.0",
        "date": "2024-03-10",
        "regulator": "HKIA (Hong Kong)",
        "change_type": "GUIDELINE REVISION",
        "title": "GL28 Luxury Asset Valuation Guardrails",
        "summary": "High-value jewellery insurance cannot use wealth accumulation or speculative value hedging analogies.",
        "impact_example": "Copy framing diamond insurance as 'protecting your capital gain' is now barred."
    }
]
