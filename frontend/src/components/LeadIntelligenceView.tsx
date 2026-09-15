"use client";

import React, { useState, useEffect } from "react";
import {
  Users,
  Target,
  Sparkles,
  TrendingUp,
  Building2,
  MapPin,
  Shield,
  MessageSquare,
  ArrowUpRight,
} from "lucide-react";
import { Lead, fetchLeads, discoverLeads } from "@/lib/api";

export const LeadIntelligenceView: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>("all");
  const [isDiscovering, setIsDiscovering] = useState<boolean>(false);
  const [activeLead, setActiveLead] = useState<Lead | null>(null);

  useEffect(() => {
    fetchLeads()
      .then((data) => {
        setLeads(data);
        if (data.length > 0) setActiveLead(data[0]);
      })
      .catch((e) => console.error("Error loading leads:", e));
  }, []);

  const handleDiscover = async () => {
    setIsDiscovering(true);
    try {
      const res = await discoverLeads("jade", "SG");
      if (res.leads) {
        setLeads((prev) => [...res.leads, ...prev]);
        if (res.leads.length > 0) setActiveLead(res.leads[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsDiscovering(false);
    }
  };

  const filteredLeads = leads.filter((l) => {
    if (selectedBrand === "all") return true;
    return l.brand === selectedBrand;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Target className="w-5 h-5 text-emerald-400" />
            <span>Lead Intelligence & Reverse Signals</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Identify high-intent enterprise prospects based on real-world triggers (expansion, fleet additions, hiring) with verified compliant outreach.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleDiscover}
            disabled={isDiscovering}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:opacity-90 text-slate-950 text-xs font-bold flex items-center space-x-1.5 transition-all shadow-md shadow-emerald-900/20"
          >
            <Sparkles className="w-3.5 h-3.5 fill-current" />
            <span>{isDiscovering ? "Scanning Signals..." : "Discover Intent Signals"}</span>
          </button>
        </div>
      </div>

      {/* Brand Filters */}
      <div className="flex items-center space-x-2 text-xs">
        <span className="text-slate-400 font-semibold mr-1">Brand Portfolio:</span>
        {[
          { id: "all", label: "All Brands" },
          { id: "jade", label: "Jade (Jewellers)" },
          { id: "jaguar_transit", label: "Jaguar (Cargo)" },
          { id: "doctorshield", label: "DoctorShield (Med)" },
        ].map((btn) => (
          <button
            key={btn.id}
            onClick={() => setSelectedBrand(btn.id)}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              selectedBrand === btn.id
                ? "bg-emerald-950/70 border border-emerald-500/50 text-emerald-300 font-bold"
                : "bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {/* Leads Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 7 Cols: Lead Cards */}
        <div className="lg:col-span-7 space-y-3">
          {filteredLeads.map((lead) => {
            const isSelected = activeLead?.id === lead.id;
            return (
              <div
                key={lead.id}
                onClick={() => setActiveLead(lead)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? "bg-slate-900/90 border-emerald-500/60 shadow-lg shadow-emerald-950/20"
                    : "glass-panel border-slate-800/80 hover:border-slate-700"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-bold text-sm text-white">{lead.company}</h3>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300">
                        {lead.industry}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3 text-xs text-slate-400 mt-1">
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-slate-500" />
                        <span>{lead.location} ({lead.jurisdiction})</span>
                      </span>
                      <span>•</span>
                      <span className="capitalize text-emerald-400 font-semibold">{lead.brand.replace('_', ' ')}</span>
                    </div>
                  </div>

                  {/* Fit Score Badge */}
                  <div className="text-right">
                    <div className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-extrabold text-xs">
                      {lead.fit_score}% Fit
                    </div>
                  </div>
                </div>

                {/* Intent Signals */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {lead.signals?.map((sig, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded bg-slate-800/90 border border-slate-700/60 text-[11px] text-slate-300"
                    >
                      ⚡ {sig}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right 5 Cols: Compliant Outreach Composer */}
        <div className="lg:col-span-5 glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Compliant Prospect Dossier
            </span>
            {activeLead ? (
              <div>
                <h3 className="text-base font-bold text-white">{activeLead.company}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{activeLead.reasoning}</p>
              </div>
            ) : (
              <p className="text-xs text-slate-500">Select a lead to view dossier.</p>
            )}
          </div>

          {activeLead && (
            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[11px] font-semibold text-slate-300 block mb-1">
                  Trigger Event & Strategic Rationale:
                </span>
                <p className="text-slate-400 leading-relaxed">
                  {activeLead.reasoning}
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-semibold text-cyan-400">
                    Recommended Compliant Outreach:
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                    {activeLead.jurisdiction} Regulated
                  </span>
                </div>
                <p className="text-slate-200 italic font-sans leading-relaxed text-xs">
                  &ldquo;{activeLead.recommended_message || `Hello ${activeLead.company} team, congratulations on your recent expansion. JA Assure's ${activeLead.brand} division offers bespoke coverage tailored for your scale, subject to standard underwriting terms.`}&rdquo;
                </p>
              </div>

              <div className="pt-2">
                <button className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs flex items-center justify-center space-x-1.5 transition-all">
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Copy Compliant Message</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
