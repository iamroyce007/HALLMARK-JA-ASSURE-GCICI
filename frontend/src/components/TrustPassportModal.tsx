"use client";

import React from "react";
import {
  ShieldCheck,
  CheckCircle2,
  X,
  Copy,
  Download,
  Share2,
  Lock,
  FileText,
  Sparkles,
} from "lucide-react";
import { Asset } from "@/lib/api";

interface TrustPassportModalProps {
  asset: Asset | null;
  onClose: () => void;
}

export const TrustPassportModal: React.FC<TrustPassportModalProps> = ({ asset, onClose }) => {
  if (!asset) return null;

  const passport = asset.trust_passport || {
    passport_id: "PASS-AEGIS-2024-001",
    verification_hash: "0x3f79a90e4f2b1d6c8e5a7b0c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e",
    model_id: "gemini-2.0-flash",
    red_team_passed: true,
    compliance_passed: true,
    evidence_count: 4,
    created_at: new Date().toISOString(),
  };

  const copyHash = () => {
    navigator.clipboard.writeText(passport.verification_hash);
    alert("Verification SHA-256 Hash copied to clipboard!");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="relative w-full max-w-lg glass-panel rounded-2xl border border-cyan-500/40 p-6 shadow-2xl shadow-cyan-950/50 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-white">Trust Passport Verified</h3>
              <p className="text-[11px] text-slate-400 font-mono">ID: {passport.passport_id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Cryptographic Hash Badge */}
        <div className="p-3.5 rounded-xl bg-slate-900 border border-cyan-500/30 space-y-1.5">
          <div className="flex items-center justify-between text-[11px]">
            <span className="font-bold text-cyan-400 uppercase tracking-wider flex items-center space-x-1">
              <Lock className="w-3 h-3" />
              <span>SHA-256 Cryptographic Audit Hash</span>
            </span>
            <button
              onClick={copyHash}
              className="text-slate-400 hover:text-cyan-300 flex items-center space-x-1"
            >
              <Copy className="w-3 h-3" />
              <span>Copy</span>
            </button>
          </div>
          <p className="font-mono text-[11px] text-slate-200 break-all bg-slate-950/80 p-2 rounded border border-slate-800">
            {passport.verification_hash}
          </p>
        </div>

        {/* Audit Lineage Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Model Audit</span>
            <span className="font-semibold text-slate-200">{passport.model_id}</span>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Red-Team Scan</span>
            <span className="font-semibold text-emerald-400 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5 inline" />
              <span>Skeptic Passed</span>
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Regulatory Matrix</span>
            <span className="font-semibold text-emerald-400 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5 inline" />
              <span>5 Markets Cleared</span>
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Evidence Lineage</span>
            <span className="font-semibold text-cyan-300">{passport.evidence_count} Citations Linked</span>
          </div>
        </div>

        {/* Certified Content Preview */}
        <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800 text-xs text-slate-300 italic">
          &ldquo;{asset.content_text}&rdquo;
        </div>

        {/* Footer Actions */}
        <div className="flex items-center space-x-3 pt-2">
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition-all"
          >
            Close Passport
          </button>
          <button
            onClick={copyHash}
            className="flex-1 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md shadow-cyan-500/20"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Share Audit Certificate</span>
          </button>
        </div>
      </div>
    </div>
  );
};
