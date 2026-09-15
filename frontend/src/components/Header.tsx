"use client";

import React from "react";
import { Shield, Sparkles, Database, Network, Cpu, CheckCircle2, Play } from "lucide-react";
import { SystemStatus } from "@/lib/api";

interface HeaderProps {
  status: SystemStatus | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onRunDemo: () => void;
  isDemoRunning: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  status,
  activeTab,
  setActiveTab,
  onRunDemo,
  isDemoRunning,
}) => {
  const tabs = [
    { id: "command", label: "Command Center" },
    { id: "studio", label: "Campaign Studio" },
    { id: "review", label: "Review Queue" },
    { id: "matrix", label: "Compliance Matrix" },
    { id: "graph", label: "Knowledge Graph" },
    { id: "leads", label: "Lead Intelligence" },
    { id: "learning", label: "Self-Healing Memory" },
  ];

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Vision */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-emerald-400 p-[2px] flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                  <Shield className="w-5 h-5 text-cyan-400" />
                </div>
              </div>
              <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-500 rounded-full border-2 border-slate-950" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-wider bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  HALLMARK
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                  AEGIS OS
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                The Trust Engine for Autonomous Insurance Marketing
              </p>
            </div>
          </div>

          {/* Infrastructure Health Badges */}
          <div className="hidden md:flex items-center space-x-3 text-xs">
            {/* FastAPI / Engine */}
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span>LangGraph OS</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 badge-pulse" />
            </div>

            {/* PostgreSQL */}
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-300">
              <Database className="w-3.5 h-3.5 text-blue-400" />
              <span>PostgreSQL + pgvector</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            </div>

            {/* Knowledge Graph / Neo4j */}
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-300">
              <Network className="w-3.5 h-3.5 text-purple-400" />
              <span>Graph Engine</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            </div>

            {/* Gemini LLM Status */}
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span className={status?.gemini_live ? "text-emerald-300 font-medium" : "text-amber-300 font-medium"}>
                {status?.gemini_live ? "Gemini Live" : "Demo Model"}
              </span>
            </div>
          </div>

          {/* Action: 1-Click Guided Demo */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onRunDemo}
              disabled={isDemoRunning}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold shadow-lg transition-all ${
                isDemoRunning
                  ? "bg-cyan-900/60 text-cyan-300 cursor-not-allowed border border-cyan-700/50"
                  : "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold shadow-cyan-500/25 active:scale-95"
              }`}
            >
              {isDemoRunning ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                  <span>Executing Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Run 1-Click Demo</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 overflow-x-auto py-2 border-t border-slate-900/60 text-xs font-medium no-scrollbar">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? "bg-slate-800/90 text-cyan-300 border border-cyan-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};
