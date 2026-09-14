/**
 * HALLMARK API Client
 * Connects Next.js frontend to FastAPI backend on http://127.0.0.1:8000
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export interface SystemStatus {
  status: string;
  gemini_live: boolean;
  brands: number;
  jurisdictions: number;
  active_campaigns: number;
  corrections: number;
  leads: number;
}

export interface Brand {
  id: string;
  slug: string;
  name: string;
  category: string;
  tone_description: string;
  target_audience: string;
}

export interface Jurisdiction {
  id: string;
  code: string;
  country: string;
  regulator: string;
  regulator_full: string;
}

export interface Asset {
  id: string;
  channel?: string;
  platform?: string;
  content_text: string;
  status: string;
  is_hedged?: boolean;
  claims?: any[];
  red_team_result?: {
    customer_interpretation?: string;
    implied_promises?: string[];
    overclaim_detected?: boolean;
    severity?: string;
    risk_score?: number;
    reason?: string;
    problematic_phrases?: string[];
  };
  compliance_result?: {
    decision?: string;
    rules_checked?: number;
    rules_passed?: number;
    jurisdiction_matrix?: Record<string, { decision: string; violations?: any[] }>;
  };
  trust_passport?: {
    passport_id: string;
    verification_hash: string;
    model_id: string;
    red_team_passed: boolean;
    compliance_passed: boolean;
    evidence_count: number;
    created_at: string;
  };
  localizations?: Array<{
    jurisdiction_code: string;
    language: string;
    content_text: string;
    status: string;
  }>;
}

export interface Campaign {
  id: string;
  name: string;
  brand_slug: string;
  primary_jurisdiction: string;
  status: string;
  created_at: string;
  assets?: Asset[];
}

export interface Lead {
  id: string;
  company: string;
  industry: string;
  location: string;
  jurisdiction: string;
  brand: string;
  fit_score: number;
  signals: string[];
  reasoning: string;
  recommended_message?: string;
  signal_type: string;
  is_demo: boolean;
}

export interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    group: string;
    color: string;
    details?: any;
  }>;
  edges: Array<{
    source: string;
    target: string;
    relation: string;
    description: string;
  }>;
  stats: {
    total_nodes: number;
    total_edges: number;
    regulators: number;
    rules: number;
    brands: number;
    evidence: number;
    neo4j_active: boolean;
  };
}

export interface AnalyticsData {
  total_campaigns: number;
  total_assets: number;
  approved_assets: number;
  rejected_assets: number;
  total_corrections: number;
  approval_rate: number;
  learning: {
    total_corrections: number;
    times_applied_sum: number;
    approval_rate_trend: number[];
    top_reasons: Record<string, number>;
  };
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/api/system/status`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch system status");
  return res.json();
}

export async function fetchBrands(): Promise<Brand[]> {
  const res = await fetch(`${API_BASE}/api/brands`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch brands");
  return res.json();
}

export async function fetchJurisdictions(): Promise<Jurisdiction[]> {
  const res = await fetch(`${API_BASE}/api/jurisdictions`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch jurisdictions");
  return res.json();
}

export async function fetchCampaigns(): Promise<Campaign[]> {
  const res = await fetch(`${API_BASE}/api/campaigns`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch campaigns");
  return res.json();
}

export async function createCampaign(data: {
  name: string;
  brand_slug: string;
  primary_jurisdiction: string;
  target_jurisdictions: string[];
  topic: string;
  platforms: string[];
}): Promise<Campaign> {
  const res = await fetch(`${API_BASE}/api/campaigns`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create campaign");
  return res.json();
}

export async function runCampaignPipeline(campaignId: string, forceFlawed: boolean = false): Promise<any> {
  const res = await fetch(`${API_BASE}/api/campaigns/${campaignId}/run?force_flawed=${forceFlawed}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to run pipeline");
  return res.json();
}

export async function runDemoFlow(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/demo/run`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to run demo flow");
  return res.json();
}

export async function fetchReviewQueue(): Promise<Asset[]> {
  const res = await fetch(`${API_BASE}/api/review/queue`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch review queue");
  return res.json();
}

export async function submitAssetReview(
  assetId: string,
  decision: "APPROVE" | "REJECT" | "EDIT",
  reasonTag?: string,
  reviewerNote?: string,
  correctedText?: string
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/review/${assetId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision,
      reason_tag: reasonTag,
      reviewer_note: reviewerNote,
      corrected_text: correctedText,
    }),
  });
  if (!res.ok) throw new Error("Failed to submit review");
  return res.json();
}

export async function fetchKnowledgeGraph(): Promise<GraphData> {
  const res = await fetch(`${API_BASE}/api/graph/knowledge`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch knowledge graph");
  return res.json();
}

export async function runCypher(query: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/graph/cypher`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error("Failed to execute cypher query");
  return res.json();
}

export async function fetchLeads(brand?: string): Promise<Lead[]> {
  const url = brand ? `${API_BASE}/api/leads?brand=${brand}` : `${API_BASE}/api/leads`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch leads");
  return res.json();
}

export async function discoverLeads(brand: string, jurisdiction: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/leads/discover?brand=${brand}&jurisdiction=${jurisdiction}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to discover leads");
  return res.json();
}

export async function fetchCorrections(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/corrections`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch corrections");
  return res.json();
}

export async function searchCorrections(query: string, brand?: string, jurisdiction?: string): Promise<any[]> {
  const params = new URLSearchParams({ query });
  if (brand) params.set("brand", brand);
  if (jurisdiction) params.set("jurisdiction", jurisdiction);
  const res = await fetch(`${API_BASE}/api/corrections/search?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to search corrections");
  return res.json();
}

export async function fetchAnalytics(): Promise<AnalyticsData> {
  const res = await fetch(`${API_BASE}/api/analytics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch analytics");
  return res.json();
}

export async function checkComplianceDirect(text: string, jurisdiction: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/compliance/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, jurisdiction_code: jurisdiction }),
  });
  if (!res.ok) throw new Error("Failed to check compliance");
  return res.json();
}
