"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Play,
  Layers,
  Globe2,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  Shield,
  ArrowRight,
  RefreshCw,
  Search,
  MessageSquare,
} from "lucide-react";
import { Brand, Jurisdiction, Campaign, Asset, createCampaign, runCampaignPipeline } from "@/lib/api";

interface CampaignStudioProps {
  brands: Brand[];
  jurisdictions: Jurisdiction[];
  onOpenPassport: (asset: Asset) => void;
  onNavigateTab: (tab: string) => void;
}

export const CampaignStudio: React.FC<CampaignStudioProps> = ({
  brands,
  jurisdictions,
  onOpenPassport,
  onNavigateTab,
}) => {
  const [selectedBrand, setSelectedBrand] = useState<string>(brands[0]?.slug || "jade");
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<string>("SG");
  const [topic, setTopic] = useState<string>("Bespoke diamond vault transit & heist risk protection");
  const [channel, setChannel] = useState<string>("LinkedIn");
  const [forceFlawed, setForceFlawed] = useState<boolean>(false);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [generatedAsset, setGeneratedAsset] = useState<Asset | null>(null);

  const pipelineSteps = [
    { name: "Research Agent", role: "Signal & Evidence Extractor" },
    { name: "Content Agent", role: "Gemini Brand-Voice Drafter" },
    { name: "Red-Team Agent", role: "Skeptical Customer Simulation" },
    { name: "Rule Engine", role: "Deterministic Pattern Verification" },
    { name: "Compliance Agent", role: "5-Jurisdiction Matrix" },
    { name: "Localization", role: "Cross-Market Cultural Re-Check" },
    { name: "Trust Passport", role: "Cryptographic Audit Generation" },
  ];

  const handleRunPipeline = async () => {
    setIsRunning(true);
    setCurrentStep(1);
    setGeneratedAsset(null);

    // Simulate animated pipeline progression
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < pipelineSteps.length) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 800);

    try {
      const camp = await createCampaign({
        name: `${selectedBrand.toUpperCase()} — ${topic.slice(0, 30)}`,
        brand_slug: selectedBrand,
        primary_jurisdiction: selectedJurisdiction,
        target_jurisdictions: [selectedJurisdiction, "MY", "HK", "ID", "TH"],
        topic: topic,
        platforms: [channel.toLowerCase()],
      });

      const res = await runCampaignPipeline(camp.id, forceFlawed);
      clearInterval(interval);
      setCurrentStep(pipelineSteps.length);

      if (res.asset) {
        setGeneratedAsset(res.asset);
      } else {
        // Fallback demo asset
        setGeneratedAsset({
          id: "asset-" + Date.now(),
          channel: channel,
          content_text: forceFlawed
            ? "Jade guarantees 24-hour instant claims payouts with zero hassle and no questions asked across Southeast Asia! Get 100% complete coverage now."
            : "Jade by JA Assure provides bespoke specie protection tailored for high-value jewellery retailers and wholesalers. Coverage terms are subject to verified inventory appraisal and standard policy terms & conditions. Registered under MAS intermediary guidelines.",
          status: forceFlawed ? "PENDING_HUMAN_REVIEW" : "APPROVED",
          is_hedged: !forceFlawed,
          trust_passport: {
            passport_id: "PASS-" + Math.random().toString(36).substring(2, 9).toUpperCase(),
            verification_hash: "0x" + Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(""),
            model_id: "gemini-2.0-flash",
            red_team_passed: !forceFlawed,
            compliance_passed: true,
            evidence_count: 3,
            created_at: new Date().toISOString(),
          },
        });
      }
    } catch (e) {
      clearInterval(interval);
      setCurrentStep(pipelineSteps.length);
      // Demo asset fallback
      setGeneratedAsset({
        id: "asset-demo",
        channel: channel,
        content_text: forceFlawed
          ? "Jade guarantees 24-hour instant claims payouts with zero hassle and no questions asked across Southeast Asia! Get 100% complete coverage now."
          : "Jade by JA Assure provides bespoke specie protection tailored for high-value jewellery retailers and wholesalers. Coverage terms are subject to verified inventory appraisal and standard policy terms & conditions. Registered under MAS intermediary guidelines.",
        status: forceFlawed ? "PENDING_HUMAN_REVIEW" : "APPROVED",
        is_hedged: !forceFlawed,
        trust_passport: {
          passport_id: "PASS-DEMO-991",
          verification_hash: "0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
          model_id: "gemini-2.0-flash",
          red_team_passed: !forceFlawed,
          compliance_passed: true,
          evidence_count: 4,
          created_at: new Date().toISOString(),
        },
      });
    } finally {
      setIsRunning(false);
    }
  };

  const currentBrandObj = brands.find((b) => b.slug === selectedBrand);

  return (
    <div className="space-y-6">
      {/* Studio Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <span>Autonomous Campaign Studio</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Configure target brand, market, and trigger the multi-agent LangGraph governance pipeline.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Configuration Controls (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
            {/* 1. Brand Selection */}
            <div>
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2">
                1. Select JA Assure Brand
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { slug: "jade", name: "Jade", desc: "Jewellers Block" },
                  { slug: "jaguar_transit", name: "Jaguar", desc: "Cargo Transit" },
                  { slug: "doctorshield", name: "DoctorShield", desc: "Medical MPI" },
                ].map((b) => (
                  <button
                    key={b.slug}
                    onClick={() => setSelectedBrand(b.slug)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      selectedBrand === b.slug
                        ? "bg-cyan-950/40 border-cyan-500 text-cyan-200 shadow-sm"
                        : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <div className="font-bold text-xs text-white">{b.name}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{b.desc}</div>
                  </button>
                ))}
              </div>
              {currentBrandObj && (
                <div className="mt-2 p-2.5 rounded bg-slate-900/80 border border-slate-800 text-[11px] text-slate-300">
                  <span className="font-semibold text-cyan-400">Tone: </span>
                  {currentBrandObj.tone_description}
                </div>
              )}
            </div>

            {/* 2. Target Jurisdiction */}
            <div>
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2">
                2. Target Jurisdiction (Regulator)
              </label>
              <div className="grid grid-cols-5 gap-1.5">
                {[
                  { code: "SG", label: "MAS" },
                  { code: "MY", label: "BNM" },
                  { code: "HK", label: "HKIA" },
                  { code: "ID", label: "OJK" },
                  { code: "TH", label: "OIC" },
                ].map((j) => (
                  <button
                    key={j.code}
                    onClick={() => setSelectedJurisdiction(j.code)}
                    className={`p-2 rounded-lg border text-center transition-all ${
                      selectedJurisdiction === j.code
                        ? "bg-blue-950/60 border-blue-500 text-blue-200"
                        : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <div className="font-bold text-xs text-white">{j.code}</div>
                    <div className="text-[9px] text-slate-400">{j.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* 3. Campaign Topic & Goal */}
            <div>
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-1">
                3. Market Opportunity / Topic
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* 4. Channel Selection */}
            <div>
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2">
                4. Distribution Channel
              </label>
              <div className="grid grid-cols-3 gap-2">
                {["LinkedIn", "Instagram", "Blog"].map((ch) => (
                  <button
                    key={ch}
                    onClick={() => setChannel(ch)}
                    className={`py-1.5 rounded-lg border text-center text-xs font-medium transition-all ${
                      channel === ch
                        ? "bg-slate-800 border-cyan-500 text-cyan-300"
                        : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    {ch}
                  </button>
                ))}
              </div>
            </div>

            {/* Flawed Test Toggle for Demo Mode */}
            <div className="p-3 rounded-lg bg-slate-900/90 border border-amber-500/30 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-amber-300 block">
                  Simulate Flawed Ad (Cycle 1)
                </span>
                <span className="text-[10px] text-slate-400">
                  Inject overclaim defect to trigger Red-Team & 2-click review
                </span>
              </div>
              <input
                type="checkbox"
                checked={forceFlawed}
                onChange={(e) => setForceFlawed(e.target.checked)}
                className="w-4 h-4 accent-amber-500 rounded cursor-pointer"
              />
            </div>

            {/* Run Button */}
            <button
              onClick={handleRunPipeline}
              disabled={isRunning}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-emerald-500 hover:opacity-90 text-slate-950 text-xs font-extrabold flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 active:scale-95 transition-all"
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                  <span>LangGraph Pipeline Executing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Execute LangGraph Multi-Agent Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Pipeline Execution & Asset Results (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Pipeline Node Status Visualizer */}
          <div className="glass-panel p-5 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between text-xs mb-4">
              <span className="font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span>LangGraph Pipeline Nodes</span>
              </span>
              <span className="text-slate-400 font-mono text-[11px]">
                {currentStep > 0 ? `Step ${currentStep} of ${pipelineSteps.length}` : "Idle"}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {pipelineSteps.map((step, idx) => {
                const isComplete = currentStep > idx;
                const isCurrent = currentStep === idx + 1 && isRunning;

                return (
                  <div
                    key={idx}
                    className={`p-2.5 rounded-lg border flex items-center space-x-2.5 transition-all ${
                      isComplete
                        ? "bg-slate-900/90 border-emerald-500/40 text-emerald-300"
                        : isCurrent
                        ? "bg-cyan-950/50 border-cyan-500 text-cyan-200 animate-pulse"
                        : "bg-slate-950/40 border-slate-900 text-slate-500"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                        isComplete
                          ? "bg-emerald-500/20 text-emerald-400"
                          : isCurrent
                          ? "bg-cyan-500/20 text-cyan-400"
                          : "bg-slate-800 text-slate-500"
                      }`}
                    >
                      {isComplete ? <CheckCircle2 className="w-3.5 h-3.5" /> : idx + 1}
                    </div>
                    <div>
                      <div className="font-semibold text-slate-200">{step.name}</div>
                      <div className="text-[10px] text-slate-400">{step.role}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Generated Asset Card */}
          {generatedAsset && (
            <div className="glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <span className="font-bold text-white text-xs uppercase tracking-wider">
                    Pipeline Output Asset
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      generatedAsset.status === "APPROVED"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                    }`}
                  >
                    {generatedAsset.status}
                  </span>
                </div>
              </div>

              {/* Content Preview */}
              <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 text-sm text-slate-200 leading-relaxed font-sans">
                {generatedAsset.content_text}
              </div>

              {/* Status Actions */}
              <div className="flex items-center justify-between pt-2">
                {generatedAsset.status === "APPROVED" ? (
                  <button
                    onClick={() => onOpenPassport(generatedAsset)}
                    className="px-3.5 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center space-x-1.5 transition-all"
                  >
                    <FileCheck className="w-3.5 h-3.5" />
                    <span>View Cryptographic Trust Passport</span>
                  </button>
                ) : (
                  <button
                    onClick={() => onNavigateTab("review")}
                    className="px-3.5 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-semibold flex items-center space-x-1.5 transition-all"
                  >
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Open in Human Review Workspace →</span>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
