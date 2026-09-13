"""
Google Gemini LLM Integration & Pitch Narration Engine for HALLMARK / AEGIS
Supports live Gemini Flash API calls with API key configuration + offline high-fidelity fallback.
Generates live spoken/text narration for each step of the InsurTech demonstration.
"""

import os
import json
import requests
from typing import Dict, Any, Optional

class GeminiLLMClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")

    def set_api_key(self, key: str):
        self.api_key = key.strip()

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None, temperature: float = 0.2) -> str:
        """
        Execute Gemini 1.5/2.0 Flash generation if API key is present,
        otherwise gracefully fallback to deterministic high-fidelity response.
        """
        if self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature, "maxOutputTokens": 1024}
                }
                if system_instruction:
                    payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

                resp = requests.post(url, headers=headers, json=payload, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            except Exception as e:
                print(f"[GeminiLLMClient] API error, using fallback: {e}")

        # Fallback simulated high-quality response
        return f"[Simulated Gemini Flash Output]\n{prompt[:300]}..."

    def generate_pitch_narration(self, step_num: int, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate synchronized voiceover transcript and speaker commentary for each pitch step.
        """
        narrations = {
            1: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 1. The Research Agent detects a competitor price surge. Chubb and Lloyd's syndicates have hiked diamond specie premiums by 18 percent across Singapore and Hong Kong. AEGIS automatically converts this intelligence into an immediate campaign briefing for Jade by JA Assure.",
                "key_takeaway": "Autonomous Market Intelligence triggers immediate tactical campaigns within minutes of competitor rate adjustments."
            },
            2: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 2. The Content Agent synthesizes platform-native copy across distinct brand voices. Watch how Jade's voice on Instagram captures high-net-worth luxury and atelier craftsmanship, while DoctorShield on LinkedIn uses clinical, authoritative language tailored for surgical specialists.",
                "key_takeaway": "True multi-brand voice awareness across Jade, DoctorShield, and Jaguar Transit with platform-native formatting."
            },
            3: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 3. Here is structural differentiator number one: the Adversarial Skeptical Customer Agent. Before compliance even touches the draft, this red-team agent cold-reads the text and flags an implied guarantee. It asks: 'What did I just get promised?' and catches that a customer will expect an unconditioned 24-hour cash payout without an adjuster report.",
                "key_takeaway": "Catches implied guarantees and perceptual traps that rules-based keyword checkers miss completely."
            },
            4: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 4. The 5-Jurisdiction Matrix. Unlike generic compliance checkers, AEGIS evaluates the asset against individual regulators. This exact post passes Singapore MAS Notice 125 with a score of 85, but triggers a critical violation under Indonesian OJK Circular 19 because express turnaround claims are strictly prohibited in Indonesia without local statutory disclaimers.",
                "key_takeaway": "Jurisdiction-native compliance prevents catastrophic cross-border regulatory fines across SG, MY, HK, ID, and TH."
            },
            5: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 5. The Human Review Studio. Instead of cumbersome text forms, human underwriters submit feedback with a two-click structured tag: 'Overclaim'. This tag immediately embeds the correction and rationale into our pgvector Correction Memory.",
                "key_takeaway": "Frictionless 2-click feedback guarantees human compliance teams actually feed the learning flywheel."
            },
            6: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 6. The Learning Loop headline demo. When we re-run the pipeline, the Content Agent uses vector RAG to retrieve the past correction and injects it as a living style guardrail into its prompt. Watch the live telemetry chart: across simulated feedback cycles, edit distance drops from 74 percent down to 8 percent, and rejection rates plummet to 4 percent.",
                "key_takeaway": "Measurable, real-time learning convergence proven through telemetry curves."
            },
            7: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 7. Localization with Post-Translation Re-Check. AEGIS translates the approved copy into Thai, Bahasa Indonesia, Malay, and Chinese, then runs a mandatory second-pass compliance check to ensure translation didn't cause semantic drift or omit local statutory disclaimers.",
                "key_takeaway": "Zero compliance leakage in multi-lingual translation across ASEAN."
            },
            8: {
                "speaker": "AI Orchestrator Voice",
                "speech_text": "Step 8. Reverse-Signal Lead Hunter and Buffer Auto-Scheduling. Instead of cold scraping, AEGIS watches hiring alerts—like Lee Hwa hiring a Vault Risk Manager—to score hot buying intent. The approved post is auto-queued in Buffer with projected engagement analytics flowing back.",
                "key_takeaway": "End-to-end autonomy connecting market intelligence, compliant content, and high-intent B2B lead generation."
            }
        }
        return narrations.get(step_num, {
            "speaker": "AEGIS Agent Voice",
            "speech_text": f"Executing Step {step_num} of the multi-agent InsurTech workflow.",
            "key_takeaway": "Autonomous multi-agent orchestration."
        })

gemini_client = GeminiLLMClient()
