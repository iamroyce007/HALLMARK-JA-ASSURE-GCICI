"""HALLMARK — Test Suite for Multi-Agent InsurTech Trust Engine.
Tests:
1. Deterministic Rule Engine across jurisdictions (MAS, BNM, OJK, etc.)
2. Red-Team Adversarial Customer Agent
3. Multi-Jurisdiction Regulatory Matrix
4. Knowledge Graph Service (NetworkX & Neo4j compatibility)
5. Correction Store RAG Memory
"""
import pytest
import asyncio
from app.rules import engine as rule_engine
from app.agents import red_team_agent
from app.agents import compliance_agent
from app.graph.knowledge_graph import knowledge_graph
from app.memory import correction_store

@pytest.mark.asyncio
async def test_rule_engine_flags_absolute_guarantee():
    flawed_text = "Jade by JA Assure guarantees 24-hour instant claims payout with zero hassle and guaranteed peace of mind."
    result = rule_engine.evaluate(flawed_text, jurisdiction_code="SG")
    assert result.decision in ("BLOCK", "REVIEW")
    assert len(result.violations) > 0
    rule_codes = [v.rule_code for v in result.violations]
    assert any("ABS" in c or "SPD" in c for c in rule_codes)

@pytest.mark.asyncio
async def test_rule_engine_passes_hedged_text():
    hedged_text = "Jade by JA Assure provides bespoke jewellery insurance. Subject to underwriting approval and policy terms. Regulated intermediary broker."
    result = rule_engine.evaluate(hedged_text, jurisdiction_code="SG")
    assert result.decision in ("PASS", "REVIEW")
    # No BLOCK level violations for properly hedged copy
    block_violations = [v for v in result.violations if v.action == "BLOCK"]
    assert len(block_violations) == 0

@pytest.mark.asyncio
async def test_jurisdiction_matrix_sg_vs_id():
    text_with_pasti = "Perlindungan pasti cair untuk dokter spesialis di Jakarta."
    result_sg = rule_engine.evaluate(text_with_pasti, jurisdiction_code="SG")
    result_id = rule_engine.evaluate(text_with_pasti, jurisdiction_code="ID")
    # In Indonesia, 'pasti cair' triggers OJK Banned Claim Terms (ID-CLM-001) BLOCK
    id_rules = [v.rule_code for v in result_id.violations]
    assert "ID-CLM-001" in id_rules
    assert result_id.decision == "BLOCK"

@pytest.mark.asyncio
async def test_red_team_adversarial_simulation():
    flawed_text = "Never worry again! We promise 100% full coverage for all jewellery losses without question."
    result = await red_team_agent.run(flawed_text, brand_slug="jade", jurisdiction_code="SG")
    assert "red_team" in result
    red_team_data = result["red_team"]
    assert "customer_interpretation" in red_team_data or "overclaim_detected" in red_team_data
    if "overclaim_detected" in red_team_data:
        assert red_team_data["overclaim_detected"] is True

def test_knowledge_graph_structure():
    graph_data = knowledge_graph.get_graph_data()
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert "stats" in graph_data
    assert graph_data["stats"]["total_nodes"] > 10
    assert graph_data["stats"]["regulators"] == 5

    # Test Cypher query simulator
    cypher_res = knowledge_graph.execute_cypher("MATCH (r:Regulator) RETURN r")
    assert cypher_res["count"] > 0

@pytest.mark.asyncio
async def test_correction_memory_storage_and_search():
    # Test retrieving corrections for brand
    corrections = await correction_store.retrieve_corrections(
        context="diamond payout speed guarantee",
        brand_slug="jade",
        jurisdiction_code="SG",
        top_k=3,
    )
    assert isinstance(corrections, list)
    assert len(corrections) > 0
