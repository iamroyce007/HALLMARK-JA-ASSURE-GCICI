"""
LangGraph Multi-Agent State Machine Orchestrator for HALLMARK / AEGIS
Coordinates the lifecycle of marketing assets:
RESEARCH -> CONTENT_GENERATION -> RED_TEAM -> COMPLIANCE_MATRIX -> HUMAN_REVIEW -> LOCALIZATION -> SCHEDULED
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.agents.research_agent import research_agent
from app.agents.content_agent import content_agent
from app.agents.red_team_agent import red_team_agent
from app.agents.compliance_agent import compliance_agent
from app.agents.localization_agent import localization_agent
from app.agents.lead_agent import lead_agent
from app.memory.correction_memory import correction_memory

class Orchestrator:
    def __init__(self):
        self.active_campaigns: Dict[str, Any] = {}
        self.execution_logs: List[Dict[str, Any]] = []
        self.scheduled_posts: List[Dict[str, Any]] = []

    def _log_event(self, campaign_id: str, stage: str, agent_name: str, status: str, message: str, metadata: Any = None):
        event = {
            "id": f"evt-{uuid.uuid4().hex[:8]}",
            "campaign_id": campaign_id,
            "stage": stage,
            "agent_name": agent_name,
            "status": status,
            "message": message,
            "metadata": metadata,
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
        }
        self.execution_logs.append(event)
        return event

    def run_pipeline(
        self,
        brand_id: str = "jade",
        topic: str = "Bespoke Diamond & Vault Protection without Punitive Rate Surges",
        channel: str = "Instagram",
        target_country: str = "SG",
        force_flawed: bool = False,
        intel_id: Optional[str] = "intel-01"
    ) -> Dict[str, Any]:
        """
        Execute full multi-agent workflow for an asset.
        """
        campaign_id = f"cmp-{uuid.uuid4().hex[:6]}"
        self._log_event(campaign_id, "INIT", "Orchestrator", "STARTED", f"Initializing campaign pipeline for {brand_id.upper()} on {channel} ({target_country})")

        # Step 1: Research Agent Brief
        intel_brief = research_agent.trigger_campaign_brief(intel_id)
        self._log_event(campaign_id, "RESEARCH", research_agent.name, "COMPLETED", f"Market signal captured: {intel_brief['trigger_event']}", intel_brief)

        # Step 2: Content Agent Generation (with RAG Living Guardrails)
        draft = content_agent.generate(
            brand_id=brand_id,
            topic=topic,
            channel=channel,
            target_country=target_country,
            force_flawed=force_flawed
        )
        self._log_event(
            campaign_id,
            "CONTENT",
            content_agent.name,
            "COMPLETED",
            f"Draft generated in {brand_id} voice with {draft['guardrails_injected_count']} living guardrails",
            draft
        )

        # Step 3: Red-Team Adversarial Agent Cold Read
        red_team_result = red_team_agent.evaluate(
            content_text=draft["full_content"],
            brand_id=brand_id,
            channel=channel
        )
        self._log_event(
            campaign_id,
            "RED_TEAM",
            red_team_agent.name,
            red_team_result["status"],
            f"Adversarial pass: {red_team_result['verdict']}",
            red_team_result
        )

        # Step 4: 5-Jurisdiction Compliance Matrix Evaluation
        compliance_matrix = compliance_agent.evaluate_matrix(
            content_text=draft["full_content"],
            brand_id=brand_id,
            primary_country=target_country
        )
        self._log_event(
            campaign_id,
            "COMPLIANCE",
            compliance_agent.name,
            compliance_matrix["primary_status"],
            f"Evaluated against 5 regulators. Primary ({target_country}): {compliance_matrix['primary_status']} (Score {compliance_matrix['primary_score']})",
            compliance_matrix
        )

        # Step 5: Localization Preview & Re-check
        localized_versions = localization_agent.translate_and_recheck(
            content_text=draft["full_content"],
            brand_id=brand_id,
            target_countries=["ID", "TH", "MS", "ZH"]
        )
        self._log_event(
            campaign_id,
            "LOCALIZATION",
            localization_agent.name,
            "COMPLETED",
            f"Localized to 4 languages with post-translation compliance re-check verified.",
            {"languages_count": len(localized_versions)}
        )

        # Build composite campaign object
        campaign_record = {
            "id": campaign_id,
            "brand_id": brand_id,
            "topic": topic,
            "channel": channel,
            "target_country": target_country,
            "status": "PENDING_HUMAN_REVIEW" if compliance_matrix["primary_status"] != "COMPLIANT" or red_team_result["status"] == "FLAGGED" else "APPROVED",
            "cycle_number": 1 if force_flawed else 2,
            "intel_brief": intel_brief,
            "draft": draft,
            "red_team": red_team_result,
            "compliance_matrix": compliance_matrix,
            "localized_versions": localized_versions,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.active_campaigns[campaign_id] = campaign_record
        return campaign_record

    def submit_human_review(
        self,
        campaign_id: str,
        decision: str, # "APPROVE", "REJECT", "EDIT"
        feedback_tag: Optional[str] = "overclaim",
        feedback_notes: Optional[str] = None,
        edited_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record human review decision.
        If REJECT or EDIT, automatically ingests correction into Correction Memory vector store.
        """
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        tag_labels = {
            "overclaim": "Overclaimed Speed / Guarantee",
            "non_compliant_id": "OJK Indonesia Non-Compliant Claims Phrasing",
            "too_salesy": "Excessively Aggressive / Salesy Tone",
            "wrong_cta": "Inappropriate Call-To-Action",
            "off_brand": "Off-Brand Vocabulary",
            "missing_disclaimer": "Missing Regulatory Disclosure"
        }

        if decision in ["REJECT", "EDIT"]:
            # Store in Correction Memory
            tag_label = tag_labels.get(feedback_tag, "General Correction")
            original_text = campaign["draft"]["full_content"]
            correction_instruction = feedback_notes or f"Flagged for {tag_label}. Must remove absolute guarantees and qualify policy turnaround."
            
            mem_entry = correction_memory.add_correction(
                brand=campaign["brand_id"],
                tag=feedback_tag,
                tag_label=tag_label,
                original_text=original_text,
                human_correction=correction_instruction,
                market=campaign["target_country"]
            )
            
            campaign["status"] = "REJECTED_AND_LEARNED" if decision == "REJECT" else "EDITED_AND_LEARNED"
            campaign["correction_entry"] = mem_entry

            self._log_event(
                campaign_id,
                "LEARNING_FEEDBACK",
                "Human Reviewer & Correction Memory",
                "INGESTED",
                f"Human feedback [{tag_label}] embedded into Vector RAG memory (ID: {mem_entry['id']}). Next generation will apply as living guardrail.",
                mem_entry
            )
            return {
                "campaign_id": campaign_id,
                "status": campaign["status"],
                "decision": decision,
                "correction_memory_id": mem_entry["id"],
                "telemetry": correction_memory.get_learning_telemetry()
            }

        elif decision == "APPROVE":
            campaign["status"] = "APPROVED"
            # Auto-schedule to Buffer / Ayrshare queue
            scheduled_entry = {
                "id": f"sched-{uuid.uuid4().hex[:6]}",
                "campaign_id": campaign_id,
                "brand_id": campaign["brand_id"],
                "channel": campaign["channel"],
                "content": campaign["draft"]["full_content"],
                "scheduled_time": "2026-09-16 18:00:00 (Prime Engagement Window)",
                "distribution_status": "QUEUED_IN_BUFFER",
                "mock_analytics": {
                    "estimated_reach": "14,500 High-Net-Worth & Specie Trades",
                    "projected_ctr": "4.8%",
                    "target_cpa": "$18.50 SGD per Qualified Inbound Lead"
                }
            }
            self.scheduled_posts.append(scheduled_entry)
            self._log_event(
                campaign_id,
                "SCHEDULED",
                "Buffer / Ayrshare Connector",
                "SUCCESS",
                f"Asset successfully scheduled for automated publishing to {campaign['channel']}.",
                scheduled_entry
            )
            return {
                "campaign_id": campaign_id,
                "status": "APPROVED_AND_SCHEDULED",
                "scheduled_entry": scheduled_entry
            }

orchestrator = Orchestrator()
