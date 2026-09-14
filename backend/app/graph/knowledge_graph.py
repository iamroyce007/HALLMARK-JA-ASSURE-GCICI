"""HALLMARK — Regulatory & Evidence Knowledge Graph.
Supports optional Neo4j graph database sync and native NetworkX in-memory graph intelligence.
Powers:
1. Evidence-to-Claim Lineage
2. Multi-Jurisdictional Regulatory Constellation
3. Red-Team Attack Surface Mapping
4. Interactive Graph Visualizer in Frontend
"""
import os
import logging
from typing import Optional, Dict, Any, List
import networkx as nx

logger = logging.getLogger("hallmark.graph")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class KnowledgeGraphService:
    def __init__(self):
        self.nx_graph = nx.DiGraph()
        self.neo4j_driver = None
        self._init_neo4j()
        self._build_default_graph()

    def _init_neo4j(self):
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            # Test connectivity with short timeout
            with driver.session(database="neo4j") as session:
                session.run("RETURN 1 AS ping")
            self.neo4j_driver = driver
            logger.info("Connected to live Neo4j instance at %s", NEO4J_URI)
        except Exception as e:
            logger.info("Neo4j not connected (%s) - running in native high-speed graph mode with NetworkX", str(e)[:60])
            self.neo4j_driver = None

    def is_neo4j_connected(self) -> bool:
        return self.neo4j_driver is not None

    def _build_default_graph(self):
        """Construct the rich regulatory and evidence graph for JA Assure InsurTech domains."""
        self.nx_graph.clear()

        # 1. Regulators
        regulators = [
            {"id": "REG_MAS", "label": "MAS (Singapore)", "type": "Regulator", "group": "regulatory", "color": "#06b6d4"},
            {"id": "REG_BNM", "label": "BNM (Malaysia)", "type": "Regulator", "group": "regulatory", "color": "#06b6d4"},
            {"id": "REG_HKIA", "label": "HKIA (Hong Kong)", "type": "Regulator", "group": "regulatory", "color": "#06b6d4"},
            {"id": "REG_OJK", "label": "OJK (Indonesia)", "type": "Regulator", "group": "regulatory", "color": "#06b6d4"},
            {"id": "REG_OIC", "label": "OIC (Thailand)", "type": "Regulator", "group": "regulatory", "color": "#06b6d4"},
        ]

        # 2. Jurisdictions
        jurisdictions = [
            {"id": "JUR_SG", "label": "Singapore (SG)", "type": "Jurisdiction", "group": "jurisdiction", "color": "#3b82f6"},
            {"id": "JUR_MY", "label": "Malaysia (MY)", "type": "Jurisdiction", "group": "jurisdiction", "color": "#3b82f6"},
            {"id": "JUR_HK", "label": "Hong Kong (HK)", "type": "Jurisdiction", "group": "jurisdiction", "color": "#3b82f6"},
            {"id": "JUR_ID", "label": "Indonesia (ID)", "type": "Jurisdiction", "group": "jurisdiction", "color": "#3b82f6"},
            {"id": "JUR_TH", "label": "Thailand (TH)", "type": "Jurisdiction", "group": "jurisdiction", "color": "#3b82f6"},
        ]

        # 3. Brands
        brands = [
            {"id": "BRAND_JADE", "label": "Jade (Jewellers Block)", "type": "Brand", "group": "brand", "color": "#10b981"},
            {"id": "BRAND_JAGUAR", "label": "Jaguar Transit (Cargo)", "type": "Brand", "group": "brand", "color": "#f59e0b"},
            {"id": "BRAND_DOC", "label": "DoctorShield (Med Indemnity)", "type": "Brand", "group": "brand", "color": "#ec4899"},
        ]

        # 4. Regulatory Rules
        rules = [
            {"id": "RULE_MAS_GUARANTEE", "label": "MAS No-Guarantee Notice", "type": "Rule", "group": "rule", "color": "#ef4444", "severity": "CRITICAL"},
            {"id": "RULE_BNM_TAKAFUL", "label": "BNM Islamic vs Conventional Disclosure", "type": "Rule", "group": "rule", "color": "#ef4444", "severity": "HIGH"},
            {"id": "RULE_HKIA_GL10", "label": "HKIA Guideline on Misleading Claims (GL10)", "type": "Rule", "group": "rule", "color": "#ef4444", "severity": "CRITICAL"},
            {"id": "RULE_OJK_PASTI", "label": "OJK Anti-Overpromise & Bahasa Mandate", "type": "Rule", "group": "rule", "color": "#ef4444", "severity": "CRITICAL"},
            {"id": "RULE_OIC_HONORIFIC", "label": "OIC Advertising Ethics & Formal Thai Register", "type": "Rule", "group": "rule", "color": "#ef4444", "severity": "HIGH"},
        ]

        # 5. Evidence & Market Signals
        evidence = [
            {"id": "EVID_GEM_CRIME_2024", "label": "Interpol Jeweller Theft Surge Report", "type": "Evidence", "group": "evidence", "color": "#8b5cf6", "source": "Interpol / SG Police"},
            {"id": "EVID_COLD_CHAIN_LOSS", "label": "ASEAN Transit Spoilage Incident Data", "type": "Evidence", "group": "evidence", "color": "#8b5cf6", "source": "Logistics Federation"},
            {"id": "EVID_MED_MALPRACTICE", "label": "SMC Medico-Legal Dispute Trends 2024", "type": "Evidence", "group": "evidence", "color": "#8b5cf6", "source": "Singapore Medical Council"},
        ]

        # 6. Red-Team Attack Scenarios
        scenarios = [
            {"id": "SCEN_SKEPTIC_SPEED", "label": "Skeptic Trap: 24hr Payout Fallacy", "type": "RiskScenario", "group": "risk", "color": "#f97316"},
            {"id": "SCEN_SKEPTIC_GUARANTEE", "label": "Skeptic Trap: 100% Protection Illusion", "type": "RiskScenario", "group": "risk", "color": "#f97316"},
        ]

        all_nodes = regulators + jurisdictions + brands + rules + evidence + scenarios
        for n in all_nodes:
            self.nx_graph.add_node(n["id"], **n)

        # Edges (Source, Target, Relation, Description)
        edges = [
            ("REG_MAS", "JUR_SG", "REGULATES", "Primary insurance regulator for Singapore"),
            ("REG_BNM", "JUR_MY", "REGULATES", "Central bank & insurance regulator for Malaysia"),
            ("REG_HKIA", "JUR_HK", "REGULATES", "Statutory insurance authority for Hong Kong"),
            ("REG_OJK", "JUR_ID", "REGULATES", "Financial services authority for Indonesia"),
            ("REG_OIC", "JUR_TH", "REGULATES", "Insurance commission of Thailand"),

            ("REG_MAS", "RULE_MAS_GUARANTEE", "ENFORCES", "Strict prohibition on guaranteed insurance payouts"),
            ("REG_BNM", "RULE_BNM_TAKAFUL", "ENFORCES", "Requires explicit conventional vs takaful distinction"),
            ("REG_HKIA", "RULE_HKIA_GL10", "ENFORCES", "Bans exaggerated marketing claims"),
            ("REG_OJK", "RULE_OJK_PASTI", "ENFORCES", "Bans absolute terms like 'pasti' in insurance advertising"),
            ("REG_OIC", "RULE_OIC_HONORIFIC", "ENFORCES", "Mandates respectful register and licensed intermediary citation"),

            ("BRAND_JADE", "JUR_SG", "OPERATES_IN", "Primary market for luxury gem retailers"),
            ("BRAND_JADE", "JUR_HK", "OPERATES_IN", "Hong Kong jewelry trade cluster"),
            ("BRAND_JADE", "JUR_TH", "OPERATES_IN", "Bangkok gemstone cutting and export hub"),
            ("BRAND_JAGUAR", "JUR_MY", "OPERATES_IN", "Cross-border transit corridor SG-MY"),
            ("BRAND_JAGUAR", "JUR_SG", "OPERATES_IN", "Changi freight and bonded logistics hub"),
            ("BRAND_DOC", "JUR_SG", "OPERATES_IN", "Singapore specialist clinics"),
            ("BRAND_DOC", "JUR_ID", "OPERATES_IN", "Indonesian private healthcare providers"),

            ("EVID_GEM_CRIME_2024", "BRAND_JADE", "SUPPORTS_OPPORTUNITY", "High risk drives need for diamond vault coverage"),
            ("EVID_COLD_CHAIN_LOSS", "BRAND_JAGUAR", "SUPPORTS_OPPORTUNITY", "High spoilage rates justify real-time IoT transit policy"),
            ("EVID_MED_MALPRACTICE", "BRAND_DOC", "SUPPORTS_OPPORTUNITY", "Rising litigation costs drive indemnity demand"),

            ("SCEN_SKEPTIC_GUARANTEE", "RULE_MAS_GUARANTEE", "VIOLATES_IF_UNHEDGED", "Adversarial simulation tests guarantee triggers"),
            ("SCEN_SKEPTIC_GUARANTEE", "RULE_OJK_PASTI", "VIOLATES_IF_UNHEDGED", "Cross-checks Indonesian absolute claim prohibition"),
            ("SCEN_SKEPTIC_SPEED", "RULE_HKIA_GL10", "VIOLATES_IF_UNHEDGED", "Instant claims claims trigger regulatory inquiry"),
        ]

        for u, v, rel, desc in edges:
            self.nx_graph.add_edge(u, v, relation=rel, description=desc)

    def get_graph_data(self) -> Dict[str, Any]:
        """Return nodes and edges formatted for interactive visual frontend rendering."""
        nodes = []
        for node_id, data in self.nx_graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": data.get("label", node_id),
                "type": data.get("type", "Entity"),
                "group": data.get("group", "default"),
                "color": data.get("color", "#64748b"),
                "details": {k: v for k, v in data.items() if k not in ["label", "type", "group", "color"]},
            })

        edges = []
        for u, v, data in self.nx_graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relation": data.get("relation", "CONNECTED_TO"),
                "description": data.get("description", ""),
            })

        stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "regulators": sum(1 for n in nodes if n["type"] == "Regulator"),
            "rules": sum(1 for n in nodes if n["type"] == "Rule"),
            "brands": sum(1 for n in nodes if n["type"] == "Brand"),
            "evidence": sum(1 for n in nodes if n["type"] == "Evidence"),
            "neo4j_active": self.is_neo4j_connected(),
        }

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": stats,
        }

    def execute_cypher(self, query: str) -> Dict[str, Any]:
        """Execute Cypher query if Neo4j is available; otherwise run intelligent graph traversal."""
        if self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    result = session.run(query)
                    records = [record.data() for record in result]
                    return {"mode": "neo4j_live", "query": query, "records": records, "count": len(records)}
            except Exception as e:
                logger.error("Cypher execution error in Neo4j: %s", e)

        # Fallback simulator for Cypher on NetworkX
        query_upper = query.upper()
        if "MATCH (R:RULE)" in query_upper or "RULE" in query_upper:
            res = [{"rule": data.get("label"), "severity": data.get("severity", "HIGH")} for n, data in self.nx_graph.nodes(data=True) if data.get("type") == "Rule"]
            return {"mode": "networkx_native", "query": query, "records": res, "count": len(res)}
        elif "REGULATOR" in query_upper:
            res = [{"regulator": data.get("label"), "id": n} for n, data in self.nx_graph.nodes(data=True) if data.get("type") == "Regulator"]
            return {"mode": "networkx_native", "query": query, "records": res, "count": len(res)}
        else:
            return {"mode": "networkx_native", "query": query, "records": list(self.nx_graph.nodes()), "count": self.nx_graph.number_of_nodes()}

knowledge_graph = KnowledgeGraphService()
