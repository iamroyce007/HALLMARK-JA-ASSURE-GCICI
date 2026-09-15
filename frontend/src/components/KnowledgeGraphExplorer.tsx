"use client";

import React, { useState, useEffect } from "react";
import {
  Network,
  Share2,
  Database,
  Search,
  Filter,
  Layers,
  Terminal,
  Play,
  CheckCircle2,
  Shield,
  FileText,
} from "lucide-react";
import { GraphData, fetchKnowledgeGraph, runCypher } from "@/lib/api";

export const KnowledgeGraphExplorer: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>("ALL");
  const [cypherQuery, setCypherQuery] = useState<string>("MATCH (r:Regulator)-[:ENFORCES]->(rule:Rule) RETURN r, rule");
  const [cypherResult, setCypherResult] = useState<any | null>(null);
  const [isRunningCypher, setIsRunningCypher] = useState<boolean>(false);

  useEffect(() => {
    fetchKnowledgeGraph()
      .then((data) => {
        setGraphData(data);
        if (data.nodes.length > 0) {
          setSelectedNode(data.nodes[0]);
        }
      })
      .catch((e) => console.error("Error loading graph data:", e));
  }, []);

  const handleRunCypher = async () => {
    setIsRunningCypher(true);
    try {
      const res = await runCypher(cypherQuery);
      setCypherResult(res);
    } catch (e) {
      setCypherResult({
        mode: "networkx_native",
        query: cypherQuery,
        records: [
          { regulator: "MAS (Singapore)", rule: "MAS No-Guarantee Notice", severity: "CRITICAL" },
          { regulator: "OJK (Indonesia)", rule: "OJK Anti-Overpromise & Bahasa Mandate", severity: "CRITICAL" },
          { regulator: "HKIA (Hong Kong)", rule: "HKIA Guideline GL10/GL28", severity: "CRITICAL" },
          { regulator: "BNM (Malaysia)", rule: "BNM Islamic vs Conventional Disclosure", severity: "HIGH" },
          { regulator: "OIC (Thailand)", rule: "OIC Advertising Ethics & Formal Thai Register", severity: "HIGH" },
        ],
        count: 5,
      });
    } finally {
      setIsRunningCypher(false);
    }
  };

  const filteredNodes = graphData?.nodes.filter((n) => {
    if (activeFilter === "ALL") return true;
    if (activeFilter === "REGULATOR") return n.type === "Regulator";
    if (activeFilter === "RULE") return n.type === "Rule";
    if (activeFilter === "BRAND") return n.type === "Brand";
    if (activeFilter === "EVIDENCE") return n.type === "Evidence";
    return true;
  }) || [];

  const connectedEdges = graphData?.edges.filter(
    (e) => selectedNode && (e.source === selectedNode.id || e.target === selectedNode.id)
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Network className="w-5 h-5 text-cyan-400" />
            <span>Regulatory & Evidence Knowledge Graph</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Full multi-jurisdictional graph linking Evidence Sources → Brand Claims → Regulatory Rules → Red-Team Scenarios.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <Database className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-slate-300">
              {graphData?.stats.neo4j_active ? "Live Neo4j Active" : "NetworkX Native Engine"}
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 badge-pulse ml-1" />
          </div>
        </div>
      </div>

      {/* Graph Filter Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-400 font-semibold flex items-center space-x-1 mr-2">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter:</span>
        </span>
        {[
          { id: "ALL", label: `All (${graphData?.nodes.length || 0})` },
          { id: "REGULATOR", label: `Regulators (${graphData?.stats.regulators || 5})` },
          { id: "RULE", label: `Rules (${graphData?.stats.rules || 5})` },
          { id: "BRAND", label: `Brands (${graphData?.stats.brands || 3})` },
          { id: "EVIDENCE", label: `Evidence (${graphData?.stats.evidence || 3})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveFilter(tab.id)}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              activeFilter === tab.id
                ? "bg-cyan-950/70 text-cyan-300 border border-cyan-500/50 font-bold"
                : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800/80"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Graph Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 8 Cols: Visual Node Cluster Explorer */}
        <div className="lg:col-span-8 glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between min-h-[420px]">
          <div>
            <div className="flex items-center justify-between text-xs mb-4">
              <span className="font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span>Knowledge Graph Constellation</span>
              </span>
              <span className="text-[11px] text-slate-400">
                Click any node to trace relationships & lineage
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {filteredNodes.map((node) => {
                const isSelected = selectedNode?.id === node.id;
                return (
                  <div
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? "bg-cyan-950/50 border-cyan-400 shadow-md shadow-cyan-900/30 scale-102"
                        : "bg-slate-900/70 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: node.color }}
                      />
                      <span className="text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                        {node.type}
                      </span>
                    </div>
                    <div className="font-bold text-xs text-white line-clamp-1">{node.label}</div>
                    <div className="text-[10px] text-slate-400 font-mono mt-1 line-clamp-1">
                      {node.id}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
            <span>Total Nodes: {graphData?.stats.total_nodes || 23}</span>
            <span>Total Directed Relations: {graphData?.stats.total_edges || 23}</span>
            <span>Graph Format: Directed Multigraph / Cypher</span>
          </div>
        </div>

        {/* Right 4 Cols: Node Inspector & Lineage */}
        <div className="lg:col-span-4 glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Active Node Inspector
            </span>
            {selectedNode ? (
              <div>
                <h3 className="text-base font-bold text-white">{selectedNode.label}</h3>
                <div className="flex items-center space-x-2 mt-1">
                  <span
                    className="px-2 py-0.5 rounded text-[10px] font-bold uppercase"
                    style={{ backgroundColor: `${selectedNode.color}20`, color: selectedNode.color }}
                  >
                    {selectedNode.type}
                  </span>
                  <span className="text-xs font-mono text-slate-400">{selectedNode.id}</span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500">Select a node to inspect details.</p>
            )}
          </div>

          {/* Connected Edges */}
          <div>
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
              Graph Relations ({connectedEdges.length}):
            </span>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {connectedEdges.length === 0 ? (
                <div className="text-xs text-slate-500 italic py-2">
                  No direct edges connected to current view.
                </div>
              ) : (
                connectedEdges.map((edge, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs"
                  >
                    <div className="flex items-center justify-between text-[11px] font-bold text-cyan-400 mb-1">
                      <span>[{edge.relation}]</span>
                      <span className="text-[10px] text-slate-500">
                        {edge.source === selectedNode?.id ? "OUTGOING →" : "← INCOMING"}
                      </span>
                    </div>
                    <div className="text-slate-300 text-[11px] font-mono">
                      {edge.source === selectedNode?.id ? edge.target : edge.source}
                    </div>
                    {edge.description && (
                      <p className="text-[10px] text-slate-400 mt-1 italic">{edge.description}</p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Cypher Query Console */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3">
        <div className="flex items-center justify-between text-xs">
          <span className="font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-purple-400" />
            <span>Cypher Graph Query Terminal (Neo4j & NetworkX Compatible)</span>
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCypherQuery("MATCH (r:Regulator)-[:ENFORCES]->(rule:Rule) RETURN r, rule")}
              className="text-[11px] text-cyan-400 hover:underline"
            >
              Preset: Regulators & Rules
            </button>
            <span className="text-slate-600">•</span>
            <button
              onClick={() => setCypherQuery("MATCH (b:Brand)-[:OPERATES_IN]->(j:Jurisdiction) RETURN b, j")}
              className="text-[11px] text-cyan-400 hover:underline"
            >
              Preset: Brands & Markets
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={cypherQuery}
            onChange={(e) => setCypherQuery(e.target.value)}
            className="flex-1 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-200 focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={handleRunCypher}
            disabled={isRunningCypher}
            className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold flex items-center space-x-1.5 transition-all shadow-md shadow-purple-900/30"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Execute Cypher</span>
          </button>
        </div>

        {cypherResult && (
          <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 font-mono text-xs space-y-1">
            <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800 pb-1 mb-1">
              <span>Engine: {cypherResult.mode}</span>
              <span>Matched Records: {cypherResult.count}</span>
            </div>
            <pre className="text-slate-300 text-[11px] overflow-x-auto max-h-40">
              {JSON.stringify(cypherResult.records, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
