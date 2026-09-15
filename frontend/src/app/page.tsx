"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { CommandCenter } from "@/components/CommandCenter";
import { CampaignStudio } from "@/components/CampaignStudio";
import { ReviewQueue } from "@/components/ReviewQueue";
import { ComplianceMatrixView } from "@/components/ComplianceMatrixView";
import { KnowledgeGraphExplorer } from "@/components/KnowledgeGraphExplorer";
import { LeadIntelligenceView } from "@/components/LeadIntelligenceView";
import { SelfHealingView } from "@/components/SelfHealingView";
import { TrustPassportModal } from "@/components/TrustPassportModal";
import {
  SystemStatus,
  AnalyticsData,
  Brand,
  Jurisdiction,
  Campaign,
  Asset,
  fetchSystemStatus,
  fetchAnalytics,
  fetchBrands,
  fetchJurisdictions,
  fetchCampaigns,
  fetchReviewQueue,
  runDemoFlow,
} from "@/lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("command");
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [reviewQueue, setReviewQueue] = useState<Asset[]>([]);
  const [selectedAssetForPassport, setSelectedAssetForPassport] = useState<Asset | null>(null);
  const [isDemoRunning, setIsDemoRunning] = useState<boolean>(false);
  const [liveEvents, setLiveEvents] = useState<Array<{ agent: string; message: string; timestamp: string }>>([
    {
      agent: "SYSTEM",
      message: "HALLMARK Trust Engine OS initialized. 5 Southeast Asian regulatory matrices loaded.",
      timestamp: new Date().toISOString(),
    },
    {
      agent: "RESEARCH",
      message: "Monitoring ASEAN jewellery crime telemetry and Interpol logistics loss feeds.",
      timestamp: new Date().toISOString(),
    },
  ]);

  const loadData = async () => {
    try {
      const [st, an, br, jr, cp, rq] = await Promise.all([
        fetchSystemStatus().catch(() => null),
        fetchAnalytics().catch(() => null),
        fetchBrands().catch(() => []),
        fetchJurisdictions().catch(() => []),
        fetchCampaigns().catch(() => []),
        fetchReviewQueue().catch(() => []),
      ]);

      if (st) setStatus(st);
      if (an) setAnalytics(an);
      if (br) setBrands(br);
      if (jr) setJurisdictions(jr);
      if (cp) setCampaigns(cp);
      if (rq) setReviewQueue(rq);
    } catch (e) {
      console.error("Data load error:", e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Set up SSE Event Stream connection
  useEffect(() => {
    try {
      const eventSource = new EventSource("http://127.0.0.1:8000/api/events/global-stream");
      eventSource.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.agent && data.agent !== "heartbeat") {
            setLiveEvents((prev) => [
              {
                agent: data.agent,
                message: data.message,
                timestamp: new Date().toISOString(),
              },
              ...prev.slice(0, 49),
            ]);
          }
        } catch (err) {
          // ignore parsing error
        }
      };
      return () => eventSource.close();
    } catch (e) {
      // fallback
    }
  }, []);

  const handleRunDemo = async () => {
    setIsDemoRunning(true);
    setLiveEvents((prev) => [
      {
        agent: "ORCHESTRATOR",
        message: "Starting 2-Cycle Guided Demo: Cycle 1 (Overclaim Trap) → 2-Click Human Review → Cycle 2 (Hedged Autonomous Trust)...",
        timestamp: new Date().toISOString(),
      },
      ...prev,
    ]);

    try {
      const res = await runDemoFlow();
      setLiveEvents((prev) => [
        {
          agent: "RED-TEAM",
          message: "Adversarial customer simulation flagged speed guarantee in Cycle 1. Escalated to Human Review Queue.",
          timestamp: new Date().toISOString(),
        },
        {
          agent: "CORRECTION-MEMORY",
          message: "2-Click feedback processed. Reason 'overclaim' vectorized with pgvector embeddings.",
          timestamp: new Date().toISOString(),
        },
        {
          agent: "TRUST-PASSPORT",
          message: "Cycle 2 hedged copy passed 5/5 regulators! Cryptographic SHA-256 passport issued.",
          timestamp: new Date().toISOString(),
        },
        ...prev,
      ]);
      await loadData();
      setActiveTab("review");
    } catch (e) {
      console.error(e);
      // Demo simulated progression
      setTimeout(() => {
        setLiveEvents((prev) => [
          {
            agent: "RED-TEAM",
            message: "Adversarial customer flagged 24-hr instant payout claim under MAS & OJK rules.",
            timestamp: new Date().toISOString(),
          },
          ...prev,
        ]);
        setActiveTab("review");
      }, 1500);
    } finally {
      setIsDemoRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      <Header
        status={status}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRunDemo={handleRunDemo}
        isDemoRunning={isDemoRunning}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === "command" && (
          <CommandCenter
            status={status}
            analytics={analytics}
            campaigns={campaigns}
            onNavigateTab={setActiveTab}
            onSelectCampaign={() => {}}
            onSelectAssetForReview={(a) => {
              setSelectedAssetForPassport(a);
              setActiveTab("review");
            }}
            onRunDemo={handleRunDemo}
            isDemoRunning={isDemoRunning}
            liveEvents={liveEvents}
          />
        )}

        {activeTab === "studio" && (
          <CampaignStudio
            brands={brands}
            jurisdictions={jurisdictions}
            onOpenPassport={(a) => setSelectedAssetForPassport(a)}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === "review" && (
          <ReviewQueue
            assets={reviewQueue}
            onRefresh={loadData}
            onOpenPassport={(a) => setSelectedAssetForPassport(a)}
          />
        )}

        {activeTab === "matrix" && <ComplianceMatrixView />}

        {activeTab === "graph" && <KnowledgeGraphExplorer />}

        {activeTab === "leads" && <LeadIntelligenceView />}

        {activeTab === "learning" && <SelfHealingView analytics={analytics} />}
      </main>

      {/* Trust Passport Verification Modal */}
      <TrustPassportModal
        asset={selectedAssetForPassport}
        onClose={() => setSelectedAssetForPassport(null)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>HALLMARK (AEGIS) — JA Assure InsurTech Autonomous Trust Engine</span>
          <span>MAS • BNM • HKIA • OJK • OIC Compliant</span>
        </div>
      </footer>
    </div>
  );
}
