"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  Cpu,
  ArrowRight,
  Activity,
  AlertTriangle,
  FileCheck,
  Sparkles,
  Zap,
} from "lucide-react";
import { SystemStatus, AnalyticsData, Campaign, Asset } from "@/lib/api";

interface CommandCenterProps {
  status: SystemStatus | null;
  analytics: AnalyticsData | null;
  campaigns: Campaign[];
  onNavigateTab: (tab: string) => void;
  onSelectCampaign: (campaign: Campaign) => void;
  onSelectAssetForReview: (asset: Asset) => void;
  onRunDemo: () => void;
  isDemoRunning: boolean;
  liveEvents: Array<{ agent: string; message: string; timestamp: string }>;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({
  status,
  analytics,
  campaigns,
  onNavigateTab,
  onSelectCampaign,
  onSelectAssetForReview,
  onRunDemo,
  isDemoRunning,
  liveEvents,
}) => {
  return (
    <div className="space-y-6">
      {/* Top Value Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800/80 p-6 shadow-xl">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Autonomous Trust & Governance</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              HALLMARK Trust Engine
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl mt-1">
              AI creates the marketing claim. HALLMARK proves it, red-teams it against confused customer traps, enforces 5 regulatory jurisdictions, and prevents repeated errors through pgvector correction memory.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => onNavigateTab("studio")}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center space-x-2 transition-all"
            >
              <span>Create Campaign</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onRunDemo}
              disabled={isDemoRunning}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-bold flex items-center space-x-2 shadow-lg shadow-cyan-500/20 transition-all active:scale-95"
            >
              <Zap className="w-3.5 h-3.5 fill-current" />
              <span>{isDemoRunning ? "Running Pipeline..." : "Execute 2-Cycle Demo"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Trust Passports Issued */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Trust Passports</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-white">
              {analytics?.approved_assets ?? 0}
            </span>
            <span className="text-xs text-emerald-400 font-medium">Cryptographically Verified</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Approved with SHA-256 evidence audit hash
          </div>
        </div>

        {/* Metric 2: Autonomous Approval Rate */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Approval Velocity</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-white">
              {analytics?.approval_rate ?? 75}%
            </span>
            <span className="text-xs text-cyan-400 font-medium">Cycle 2: +42%</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Self-healing improves rate each iteration
          </div>
        </div>

        {/* Metric 3: Regulators Governed */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Regulator Matrix</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-white">5 / 5</span>
            <span className="text-xs text-blue-400 font-medium">MAS • BNM • HKIA • OJK • OIC</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Deterministic rules + LLM compliance check
          </div>
        </div>

        {/* Metric 4: Learned Human Corrections */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Correction Memory</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-white">
              {status?.corrections ?? 8}
            </span>
            <span className="text-xs text-purple-400 font-medium">pgvector embeddings</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Injected as few-shot guardrails into generation
          </div>
        </div>
      </div>

      {/* Main Grid: Live Agent Narration Stream & Active Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Live Multi-Agent Narration */}
        <div className="lg:col-span-2 glass-panel rounded-xl border border-slate-800/80 p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800/80 pb-3">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Autonomous Agent Narration Stream
              </h2>
            </div>
            <div className="flex items-center space-x-2">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 badge-pulse" />
              <span className="text-xs text-slate-400 font-mono">SSE LIVE</span>
            </div>
          </div>

          <div className="h-80 overflow-y-auto space-y-2 pr-2 font-mono text-xs">
            {liveEvents.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
                <Cpu className="w-8 h-8 text-slate-600 animate-pulse" />
                <p>Awaiting next pipeline execution event...</p>
                <button
                  onClick={onRunDemo}
                  className="text-xs text-cyan-400 hover:text-cyan-300 underline font-sans"
                >
                  Click here to trigger demo pipeline narration
                </button>
              </div>
            ) : (
              liveEvents.map((evt, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start space-x-2.5"
                >
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] uppercase font-bold text-cyan-400 shrink-0">
                    {evt.agent}
                  </span>
                  <div className="flex-1 text-slate-200">
                    <p>{evt.message}</p>
                    <span className="text-[10px] text-slate-500 mt-1 block">
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right 1 Col: Quick Review Queue Preview */}
        <div className="glass-panel rounded-xl border border-slate-800/80 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-slate-800/80 pb-3">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Human Review Hub
                </h2>
              </div>
              <button
                onClick={() => onNavigateTab("review")}
                className="text-xs text-cyan-400 hover:underline"
              >
                View All
              </button>
            </div>

            <p className="text-xs text-slate-400 mb-4">
              Assets flagged by Red-Team or requiring 2-click rejection feedback to update correction memory.
            </p>

            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-slate-900/80 border border-amber-500/30">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-semibold text-amber-300">Pending Human Sign-Off</span>
                  <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 text-[10px]">
                    2-Click Loop
                  </span>
                </div>
                <p className="text-xs text-slate-300 line-clamp-2 italic">
                  &ldquo;Jade by JA Assure guarantees 24-hour instant claims payout with zero hassle...&rdquo;
                </p>
                <div className="mt-2 flex items-center justify-between text-[11px]">
                  <span className="text-rose-400 font-medium">Flagged: Absolute Guarantee</span>
                  <button
                    onClick={() => onNavigateTab("review")}
                    className="text-cyan-400 font-semibold hover:underline"
                  >
                    Resolve in Queue →
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Jurisdiction Engine</span>
              <span className="text-emerald-400 font-medium">MAS / BNM / HKIA Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
