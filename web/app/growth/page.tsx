"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getJSON, fmtM, fmtK } from "@/lib/api";
import { KpiCard, PageHeader, SectionLabel, Spinner } from "@/components/ui";

type Product = {
  id: number;
  name: string;
  category: string;
  description: string;
};

type Cell = {
  product_id: number;
  state: "owned" | "recommended" | "none";
  arr: number;
  peer_penetration_pct?: number;
};

type Rec = {
  product_id: number;
  product_name: string;
  estimated_arr: number;
  peer_penetration_pct: number;
  peer_examples: string[];
  description: string;
};

type Row = {
  customer_id: number;
  customer_name: string;
  industry: string;
  customer_tier: string;
  risk_level: string;
  health_score: number;
  current_arr: number;
  whitespace_arr: number;
  arr_goal: number;
  recommended: Rec[];
  cells: Cell[];
};

type Whitespace = {
  products: Product[];
  rows: Row[];
  total_current_arr: number;
  total_whitespace_arr: number;
  total_arr_goal: number;
  growth_pct: number;
};

// Short column labels for the penetration matrix
const SHORT: Record<string, string> = {
  "Identity Graph": "Graph",
  "Shadow Identity Discovery": "Discovery",
  "Lifecycle Automation (JML)": "JML",
  "Just-in-Time Access": "JIT",
  "Access Reviews & Certifications": "Reviews",
  "Non-Human Identity Security": "NHI",
  "Privileged Access Insights": "PAM",
  "Compliance Reporting Suite": "Compliance",
  "MFA & Posture Enforcement": "MFA",
  "Autopilot AI Agent": "Autopilot",
};

export default function GrowthPage() {
  const [data, setData] = useState<Whitespace | null>(null);
  const [sel, setSel] = useState<Row | null>(null);

  useEffect(() => {
    getJSON<Whitespace>("/api/whitespace?top_n=12").then(setData).catch(() => null);
  }, []);

  if (!data) return <Spinner label="Computing whitespace across the portfolio…" />;
  const { products, rows } = data;

  return (
    <div>
      <PageHeader
        title="Growth & Whitespace"
        subtitle="What the largest clients own today, what similar clients own that they don't, and the ARR goal if we close the gap"
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        <KpiCard label="Top-12 Current ARR" value={fmtM(data.total_current_arr)} sub="largest accounts" />
        <KpiCard label="Identified Whitespace" value={fmtM(data.total_whitespace_arr)} sub="peer-evidenced upsell" />
        <KpiCard label="Ultimate ARR Goal" value={fmtM(data.total_arr_goal)} sub="current + whitespace" />
        <KpiCard label="Growth Potential" value={`+${data.growth_pct}%`} sub="on the top-12 book" />
      </div>

      <SectionLabel>Product Penetration — Largest 12 Clients</SectionLabel>
      <div className="bg-white border border-line rounded-xl shadow-card overflow-x-auto mb-2">
        <table className="w-full text-[0.78rem]">
          <thead>
            <tr className="border-b border-line">
              <th className="text-left px-4 py-2 text-[0.62rem] text-muted uppercase tracking-[0.10em] font-bold whitespace-nowrap">
                Customer
              </th>
              {products.map((p) => (
                <th
                  key={p.id}
                  title={`${p.name} — ${p.description}`}
                  className="px-1 py-2 text-[0.6rem] text-muted uppercase tracking-[0.04em] font-bold whitespace-nowrap"
                >
                  {SHORT[p.name] || p.name}
                </th>
              ))}
              <th className="text-right px-3 py-2 text-[0.62rem] text-muted uppercase tracking-[0.10em] font-bold whitespace-nowrap">
                ARR → Goal
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.customer_id}
                onClick={() => setSel(sel?.customer_id === r.customer_id ? null : r)}
                className={`border-b border-[#F1ECD9] cursor-pointer transition-colors ${
                  sel?.customer_id === r.customer_id ? "bg-lavender" : "hover:bg-[#FCFAEE]"
                }`}
              >
                <td className="px-4 py-[9px] whitespace-nowrap">
                  <div className="font-bold text-navy">{r.customer_name}</div>
                  <div className="text-[0.65rem] text-muted">
                    {r.industry} · {r.customer_tier}
                  </div>
                </td>
                {r.cells.map((c) => (
                  <td key={c.product_id} className="text-center px-1 py-[9px]">
                    {c.state === "owned" ? (
                      <span
                        title={`Owned — ${fmtK(c.arr)}/yr`}
                        className="inline-block w-[14px] h-[14px] rounded-full bg-navy"
                      />
                    ) : c.state === "recommended" ? (
                      <span
                        title={`Recommended — est. ${fmtK(c.arr)}/yr · ${c.peer_penetration_pct}% of peers own it`}
                        className="inline-block w-[14px] h-[14px] rounded-full border-2 border-dashed border-[#2D5A3D] bg-[#EBF2EE]"
                      />
                    ) : (
                      <span className="inline-block w-[6px] h-[6px] rounded-full bg-[#E5DFC8]" />
                    )}
                  </td>
                ))}
                <td className="text-right px-3 py-[9px] whitespace-nowrap">
                  <span className="font-bold text-navy">{fmtK(r.current_arr)}</span>
                  {r.whitespace_arr > 0 ? (
                    <span className="text-green font-bold"> → {fmtK(r.arr_goal)}</span>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex gap-5 items-center text-[0.7rem] text-muted mb-6 px-1">
        <span className="flex items-center gap-2">
          <span className="inline-block w-[12px] h-[12px] rounded-full bg-navy" /> Owned
        </span>
        <span className="flex items-center gap-2">
          <span className="inline-block w-[12px] h-[12px] rounded-full border-2 border-dashed border-[#2D5A3D] bg-[#EBF2EE]" />{" "}
          Recommended (peers own it)
        </span>
        <span className="flex items-center gap-2">
          <span className="inline-block w-[6px] h-[6px] rounded-full bg-[#E5DFC8]" /> Not owned, weak peer signal
        </span>
      </div>

      {sel ? (
        <div className="bg-white border border-line rounded-xl shadow-card p-5 mb-6">
          <div className="flex items-baseline justify-between mb-3 flex-wrap gap-2">
            <div>
              <span className="text-[1.05rem] font-extrabold text-navy">{sel.customer_name}</span>
              <span className="text-[0.75rem] text-muted ml-3">
                {sel.industry} · {sel.customer_tier} · health {sel.health_score}/100
              </span>
            </div>
            <div className="text-[0.85rem]">
              <span className="text-muted">ARR goal: </span>
              <span className="font-extrabold text-navy">{fmtK(sel.current_arr)}</span>
              {sel.whitespace_arr > 0 ? (
                <span className="font-extrabold text-green"> → {fmtK(sel.arr_goal)} (+{fmtK(sel.whitespace_arr)})</span>
              ) : (
                <span className="text-muted"> — fully penetrated</span>
              )}
            </div>
          </div>
          {sel.recommended.length ? (
            <div className="grid md:grid-cols-3 gap-3">
              {sel.recommended.map((o) => (
                <div key={o.product_id} className="border border-line rounded-[10px] p-3 bg-[#FCFAEE]">
                  <div className="font-bold text-navy text-[0.85rem] mb-1">{o.product_name}</div>
                  <div className="text-[0.72rem] text-ink leading-relaxed mb-2">{o.description}</div>
                  <div className="text-[0.78rem] font-extrabold text-green mb-1">est. {fmtK(o.estimated_arr)}/yr</div>
                  <div className="text-[0.68rem] text-muted">
                    {o.peer_penetration_pct}% of similar clients own it
                    {o.peer_examples.length ? ` — e.g. ${o.peer_examples.slice(0, 2).join(", ")}` : ""}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-[0.8rem] text-muted">
              No high-confidence whitespace — this account already owns what its peers own.
            </div>
          )}
          <div className="mt-4 flex gap-3">
            <Link
              href={`/customers/${sel.customer_id}`}
              className="bg-navy text-white rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#000000] transition-colors"
            >
              Open Customer 360
            </Link>
            <button
              onClick={() => window.open(`/api/customers/${sel.customer_id}/debate`, "_blank")}
              className="bg-white text-navy border-[1.5px] border-[#DCD5B8] rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#F2EDDA] transition-colors"
            >
              ⚔ Red Team the Renewal ↗
            </button>
          </div>
        </div>
      ) : (
        <div className="text-[0.78rem] text-muted px-1">
          Click a row to see the recommended upsell plays with peer evidence and the account's ARR goal.
        </div>
      )}
    </div>
  );
}
