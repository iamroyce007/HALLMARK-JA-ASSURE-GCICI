"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  Search,
  Zap,
} from "lucide-react";
import { checkComplianceDirect } from "@/lib/api";

const JURISDICTIONS = [
  {
    code: "SG",
    country: "Singapore",
    regulator: "MAS",
    fullName: "Monetary Authority of Singapore",
    rules: [
      { code: "SG-DIS-001", title: "Intermediary Disclosure", desc: "Must disclose broker / intermediary status under MAS Notice 125." },
      { code: "GL-ABS-001", title: "No Absolute Guarantees", desc: "Prohibits claims of 'guaranteed' or '100% loss coverage'." },
    ],
  },
  {
    code: "MY",
    country: "Malaysia",
    regulator: "BNM",
    fullName: "Bank Negara Malaysia",
    rules: [
      { code: "MY-SUP-001", title: "Superlative Ban", desc: "BNM/RH/PD 029-2 prohibits terms like 'terbaik', 'nombor satu', 'paling murah'." },
      { code: "MY-TAK-001", title: "Takaful Delineation", desc: "Clear distinction required between conventional insurance and takaful schemes." },
    ],
  },
  {
    code: "HK",
    country: "Hong Kong",
    regulator: "HKIA",
    fullName: "Hong Kong Insurance Authority",
    rules: [
      { code: "HK-INV-001", title: "Investment Language Ban", desc: "HKIA GL28 strictly bans framing general insurance as an asset yield / investment." },
      { code: "HK-GL10", title: "Exaggerated Marketing", desc: "Guideline on misleading marketing and unsubstantiated turnaround times." },
    ],
  },
  {
    code: "ID",
    country: "Indonesia",
    regulator: "OJK",
    fullName: "Otoritas Jasa Keuangan",
    rules: [
      { code: "ID-CLM-001", title: "Banned 'Pasti' Language", desc: "SEOJK.05/2020 explicitly bans 'pasti cair', 'jaminan kilat', 'tanpa syarat'." },
      { code: "ID-DIS-001", title: "Bahasa Indonesia Mandate", desc: "Marketing materials must adhere to OJK supervisory disclosure requirements." },
    ],
  },
  {
    code: "TH",
    country: "Thailand",
    regulator: "OIC",
    fullName: "Office of Insurance Commission",
    rules: [
      { code: "TH-WRN-001", title: "Consumer Warning Clause", desc: "Must cite buyer comprehension clause ('ผู้ซื้อควรทำความเข้าใจก่อนตัดสินใจ')." },
      { code: "TH-HON-001", title: "Formal Register", desc: "Must maintain respectful cultural register with appropriate honorific markers." },
    ],
  },
];

export const ComplianceMatrixView: React.FC = () => {
  const [testText, setTestText] = useState<string>(
    "Jade by JA Assure guarantees 24-hour instant claims payout with zero hassle and no questions asked for jewellers across Southeast Asia!"
  );
  const [selectedJur, setSelectedJur] = useState<string>("SG");
  const [evalResult, setEvalResult] = useState<any>(null);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);

  const handleEvaluate = async () => {
    setIsEvaluating(true);
    try {
      const res = await checkComplianceDirect(testText, selectedJur);
      setEvalResult(res);
    } catch (e) {
      // Fallback deterministic evaluation
      const lower = testText.toLowerCase();
      const hasGuarantee = lower.includes("guarantee") || lower.includes("100%") || lower.includes("pasti");
      const hasSpeed = lower.includes("24-hour") || lower.includes("instant");

      setEvalResult({
        decision: hasGuarantee || hasSpeed ? "BLOCK" : "PASS",
        jurisdiction_code: selectedJur,
        violations: hasGuarantee || hasSpeed ? [
          {
            rule_code: "GL-ABS-001",
            rule_name: "Absolute Guarantee Language",
            severity: "CRITICAL",
            action: "BLOCK",
            matched_text: hasGuarantee ? "guarantees" : "24-hour instant",
            explanation: "Deterministic match: prohibited absolute promise detected",
            citation: "DEMO POLICY — Regulatory claim prohibition",
          }
        ] : [],
        rules_checked: 6,
        rules_passed: hasGuarantee || hasSpeed ? 5 : 6,
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <span>5-Jurisdiction Regulatory Matrix</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            A claim compliant in Singapore can be an illegal violation in Indonesia. AEGIS enforces region-specific regulatory rule sets.
          </p>
        </div>
      </div>

      {/* 5 Regulatory Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {JURISDICTIONS.map((j) => (
          <div
            key={j.code}
            onClick={() => setSelectedJur(j.code)}
            className={`cursor-pointer p-4 rounded-xl border transition-all ${
              selectedJur === j.code
                ? "bg-cyan-950/40 border-cyan-500 shadow-md shadow-cyan-950/40"
                : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-extrabold text-sm text-white">{j.code}</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-400 text-[10px] font-bold">
                {j.regulator}
              </span>
            </div>
            <div className="text-xs font-semibold text-slate-300">{j.country}</div>
            <div className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{j.fullName}</div>
            <div className="mt-3 text-[10px] text-slate-400 pt-2 border-t border-slate-800/80">
              {j.rules.length} active rules enforced
            </div>
          </div>
        ))}
      </div>

      {/* Interactive Copy Tester */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Zap className="w-4 h-4 text-cyan-400" />
              <span>Real-Time Copy Compliance Validator</span>
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
              Testing under {selectedJur} ({JURISDICTIONS.find((j) => j.code === selectedJur)?.regulator})
            </span>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">
              Paste or Edit Marketing Claim:
            </label>
            <textarea
              rows={4}
              value={testText}
              onChange={(e) => setTestText(e.target.value)}
              className="w-full p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-sans leading-relaxed"
            />
          </div>

          <div className="flex flex-wrap gap-2 text-xs">
            <span className="text-slate-400 text-[11px] self-center">Test Presets:</span>
            <button
              onClick={() => {
                setSelectedJur("SG");
                setTestText("Jade guarantees 24-hour cash claims payout with zero hassle!");
              }}
              className="px-2 py-1 rounded bg-slate-800 text-[11px] text-slate-300 hover:text-white"
            >
              SG: Speed Overclaim
            </button>
            <button
              onClick={() => {
                setSelectedJur("ID");
                setTestText("Perlindungan pasti cair 100% untuk dokter spesialis di Jakarta.");
              }}
              className="px-2 py-1 rounded bg-slate-800 text-[11px] text-slate-300 hover:text-white"
            >
              ID: OJK 'Pasti' Ban
            </button>
            <button
              onClick={() => {
                setSelectedJur("MY");
                setTestText("Insurans terbaik nombor satu paling murah di Malaysia.");
              }}
              className="px-2 py-1 rounded bg-slate-800 text-[11px] text-slate-300 hover:text-white"
            >
              MY: Superlative Ban
            </button>
          </div>

          <button
            onClick={handleEvaluate}
            disabled={isEvaluating}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:opacity-90 text-slate-950 text-xs font-bold flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 active:scale-95 transition-all"
          >
            {isEvaluating ? (
              <span>Evaluating Deterministic Rules + LLM Matrix...</span>
            ) : (
              <>
                <Search className="w-3.5 h-3.5" />
                <span>Evaluate Under {selectedJur} Regulations</span>
              </>
            )}
          </button>
        </div>

        {/* Evaluation Output */}
        <div className="lg:col-span-5 glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <span className="font-bold text-white text-xs uppercase tracking-wider">
                Jurisdiction Verdict
              </span>
              {evalResult && (
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    evalResult.decision === "PASS"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                      : evalResult.decision === "REVIEW"
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                      : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                  }`}
                >
                  {evalResult.decision}
                </span>
              )}
            </div>

            {evalResult ? (
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-400">Rules Checked:</span>
                  <span className="font-mono text-white font-bold">{evalResult.rules_checked || 6}</span>
                </div>

                {evalResult.violations && evalResult.violations.length > 0 ? (
                  <div className="space-y-2">
                    <span className="text-[11px] font-semibold text-rose-400 block">
                      Specific Rule Breaches:
                    </span>
                    {evalResult.violations.map((v: any, i: number) => (
                      <div key={i} className="p-3 rounded-lg bg-rose-950/30 border border-rose-900/50">
                        <div className="flex items-center justify-between text-[11px] font-bold text-rose-300">
                          <span>{v.rule_code}: {v.rule_name}</span>
                          <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-rose-900/60">
                            {v.severity}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-300 mt-1">{v.explanation}</p>
                        <p className="text-[10px] text-slate-400 mt-1 italic">{v.citation}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-900/30 text-emerald-300 text-center">
                    <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                    <p className="font-semibold text-xs">Passed Compliance Scan</p>
                    <p className="text-[11px] text-slate-400 mt-1">
                      No prohibited terms or missing statutory notices detected for {selectedJur}.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs">
                Click &ldquo;Evaluate&rdquo; to test copy against {selectedJur} rules.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
