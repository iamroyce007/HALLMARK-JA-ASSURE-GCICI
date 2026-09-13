"""
LangGraph Multi-Agent State Machine Implementation for HALLMARK / AEGIS
Defines explicit typed states, graph nodes, and conditional transition edges.
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime

from app.agents.research_agent import research_agent
from app.agents.content_agent import content_agent
from app.agents.red_team_agent import red_team_agent
from app.agents.compliance_agent import compliance_agent
from app.agents.localization_agent import localization_agent
from app.memory.correction_memory import correction_memory

class PipelineState(TypedDict, total=False):
    campaign_id: str
    brand_id: str
    topic: str
    channel: str
    target_country: str
    force_flawed: bool
    current_node: str
    status: str
    intel_brief: Dict[str, Any]
    draft: Dict[str, Any]
    red_team: Dict[str, Any]
    compliance_matrix: Dict[str, Any]
    localized_versions: List[Dict[str, Any]]
    human_feedback: Optional[Dict[str, Any]]
    living_guardrails: List[Dict[str, Any]]
    scheduled_entry: Optional[Dict[str, Any]]
    execution_history: List[str]

class LangGraphPipeline:
    """
    LangGraph StateGraph Engine for InsurTech multi-agent orchestration.
    """
    def __init__(self):
        self.nodes = {
            "research_node": self._research_node,
            "content_node": self._content_node,
            "red_team_node": self._red_team_node,
            "compliance_node": self._compliance_node,
            "human_review_node": self._human_review_node,
            "localization_node": self._localization_node,
            "schedule_node": self._schedule_node
        }

    def _research_node(self, state: PipelineState) -> PipelineState:
        brief = research_agent.trigger_campaign_brief("intel-01")
        state["intel_brief"] = brief
        state["current_node"] = "research_node"
        state["execution_history"].append(f"research_node: Captured intel '{brief['trigger_event']}'")
        return state

    def _content_node(self, state: PipelineState) -> PipelineState:
        draft = content_agent.generate(
            brand_id=state.get("brand_id", "jade"),
            topic=state.get("topic", "Bespoke Specie Protection"),
            channel=state.get("channel", "Instagram"),
            target_country=state.get("target_country", "SG"),
            force_flawed=state.get("force_flawed", False)
        )
        state["draft"] = draft
        state["living_guardrails"] = draft["applied_guardrails"]
        state["current_node"] = "content_node"
        state["execution_history"].append(f"content_node: Generated draft with {len(draft['applied_guardrails'])} guardrails")
        return state

    def _red_team_node(self, state: PipelineState) -> PipelineState:
        res = red_team_agent.evaluate(
            content_text=state["draft"]["full_content"],
            brand_id=state.get("brand_id", "jade"),
            channel=state.get("channel", "Instagram")
        )
        state["red_team"] = res
        state["current_node"] = "red_team_node"
        state["execution_history"].append(f"red_team_node: Adversarial verdict '{res['status']}'")
        return state

    def _compliance_node(self, state: PipelineState) -> PipelineState:
        matrix = compliance_agent.evaluate_matrix(
            content_text=state["draft"]["full_content"],
            brand_id=state.get("brand_id", "jade"),
            primary_country=state.get("target_country", "SG")
        )
        state["compliance_matrix"] = matrix
        state["current_node"] = "compliance_node"
        state["execution_history"].append(f"compliance_node: Primary score {matrix['primary_score']}/100 ({matrix['primary_status']})")
        return state

    def _human_review_node(self, state: PipelineState) -> PipelineState:
        # Check if automated or flagged
        is_safe = (state["red_team"]["status"] == "PASSED" and state["compliance_matrix"]["primary_status"] == "COMPLIANT")
        state["status"] = "APPROVED" if is_safe else "PENDING_HUMAN_REVIEW"
        state["current_node"] = "human_review_node"
        state["execution_history"].append(f"human_review_node: Routed to status '{state['status']}'")
        return state

    def _localization_node(self, state: PipelineState) -> PipelineState:
        localized = localization_agent.translate_and_recheck(
            content_text=state["draft"]["full_content"],
            brand_id=state.get("brand_id", "jade"),
            target_countries=["ID", "TH", "MS", "ZH"]
        )
        state["localized_versions"] = localized
        state["current_node"] = "localization_node"
        state["execution_history"].append(f"localization_node: Localized & re-checked 4 languages")
        return state

    def _schedule_node(self, state: PipelineState) -> PipelineState:
        state["status"] = "SCHEDULED"
        state["scheduled_entry"] = {
            "channel": state.get("channel", "Instagram"),
            "brand": state.get("brand_id", "jade"),
            "status": "QUEUED_IN_BUFFER",
            "time": "2026-09-16 18:00:00"
        }
        state["current_node"] = "schedule_node"
        state["execution_history"].append("schedule_node: Queued to Buffer/Ayrshare distribution pipeline")
        return state

    def execute_graph(
        self,
        brand_id: str = "jade",
        topic: str = "Bespoke Diamond & Vault Protection",
        channel: str = "Instagram",
        target_country: str = "SG",
        force_flawed: bool = False
    ) -> PipelineState:
        """
        Execute full StateGraph traversal from Start -> End.
        """
        state: PipelineState = {
            "campaign_id": f"lg-{datetime.now().strftime('%M%S')}",
            "brand_id": brand_id,
            "topic": topic,
            "channel": channel,
            "target_country": target_country,
            "force_flawed": force_flawed,
            "execution_history": []
        }

        # Step 1: Research Node
        state = self._research_node(state)
        # Step 2: Content Node
        state = self._content_node(state)
        # Step 3: Red-Team Node
        state = self._red_team_node(state)
        # Step 4: Compliance Node
        state = self._compliance_node(state)
        # Step 5: Human Review Node
        state = self._human_review_node(state)

        # Conditional Branch: If compliant/approved, proceed to localization and schedule
        if state["status"] == "APPROVED":
            state = self._localization_node(state)
            state = self._schedule_node(state)

        return state

langgraph_engine = LangGraphPipeline()
