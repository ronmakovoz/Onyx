"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getJSON, Customer, fmtM, fmtK } from "@/lib/api";
import { KpiCard, PageHeader, SectionLabel, Spinner } from "@/components/ui";

type Summary = Record<string, any>;
type ActionSummary = Record<string, any>;

function buildExecSummary(summary: Summary, customers: Customer[]) {
  const nrr = summary.nrr_pct ?? 0;
  const grr = summary.grr_pct ?? 0;
  const hi = summary.critical_count ?? 0;
  const arrRisk = summary.arr_at_risk ?? 0;
  const exp = summary.expansion_pipeline_arr ?? 0;
  const esc = summary.open_escalations ?? 0;
  const fc = summary.renewal_forecast_pct ?? 0;

  const atRisk = customers
    .filter((c) => c.risk_level === "High")
    .sort((a, b) => b.arr - a.arr)
    .slice(0, 2);
  const riskNames = atRisk.length ? atRisk.map((c) => c.name).join(" and ") : "no major accounts";

  const expByInd: Record<string, number> = {};
  for (const c of customers) {
    if (c.expansion_pipeline_arr)
      expByInd[c.industry] = (expByInd[c.industry] || 0) + c.expansion_pipeline_arr;
  }
  const leadInd =
    Object.entries(expByInd).sort((a, b) => b[1] - a[1])[0]?.[0] || "financial services";

  const healthWord = nrr >= 105 ? "stable" : nrr < 100 ? "under pressure" : "holding";
  const B = ({ children }: { children: React.ReactNode }) => (
    <strong className="text-white font-bold">{children}</strong>
  );

  return (
    <>
      Net revenue retention is {nrr}% with gross retention at {grr}%, leaving portfolio health{" "}
      <B>{healthWord}</B>. {hi} account{hi !== 1 ? "s" : ""} {hi !== 1 ? "are" : "is"} in high-risk
      status representing <B>{fmtM(arrRisk)}</B> of ARR — most notably {riskNames}, driven by
      adoption decline and unresolved escalations. The 90-day renewal forecast stands at{" "}
      <B>{fc}%</B>, with {esc} active escalation{esc !== 1 ? "s" : ""} requiring attention.
      Expansion pipeline totals <B>{fmtM(exp)}</B>, led by strong growth in {leadInd} accounts.
    </>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [actions, setActions] = useState<ActionSummary | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    Promise.all([
      getJSON<Summary>("/api/summary"),
      getJSON<Customer[]>("/api/customers"),
      getJSON<ActionSummary>("/api/actions/summary"),
    ])
      .then(([s, c, a]) => {
        setSummary(s);
        setCustomers(c);
        setActions(a);
      })
      .catch((e) => setErr(String(e)));
  }, []);

  if (err)
    return (
      <div className="text-red text-sm">
        Failed to load data — is the API running on :8000? ({err})
      </div>
    );
  if (!summary || !actions) return <Spinner label="Loading portfolio…" />;

  const atRisk = customers
    .filter((c) => c.risk_level === "High")
    .sort((a, b) => b.arr - a.arr)
    .slice(0, 5);
  const expAccts = customers
    .filter((c) => c.expansion_pipeline_arr)
    .sort(
      (a, b) =>
        (b.expansion_pipeline_arr || 0) * (b.upsell_likelihood || 0) -
        (a.expansion_pipeline_arr || 0) * (a.upsell_likelihood || 0)
    )
    .slice(0, 5);

  return (
    <div>
      <PageHeader title="Executive Dashboard" subtitle="The state of the customer base at a glance" />

      {/* AI Executive Summary band */}
      <div
        className="rounded-xl px-5 py-4 mb-4"
        style={{ background: "linear-gradient(135deg, #1B1040 0%, #2D2154 100%)" }}
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[0.62rem] font-bold text-[#B9AEE0] uppercase tracking-[0.12em]">
            AI Executive Summary
          </span>
          <span className="text-[0.58rem] text-[#8579B0] bg-white/10 px-2 py-[2px] rounded-full">
            Weekly · auto-generated
          </span>
        </div>
        <div className="text-[#F0EDF7] text-[0.92rem] leading-[1.65]">
          {buildExecSummary(summary, customers)}
        </div>
      </div>

      {/* 5 hero KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-5">
        <KpiCard label="Net Revenue Retention" value={`${summary.nrr_pct}%`} sub="ARR-weighted" />
        <KpiCard
          label="ARR at Risk"
          value={fmtM(summary.arr_at_risk)}
          sub={`${summary.critical_count} high · ${summary.at_risk_count} medium`}
        />
        <KpiCard
          label="Renewal Forecast (90d)"
          value={`${summary.renewal_forecast_pct}%`}
          sub={`${fmtM(summary.upcoming_renewal_arr || 0)} up for renewal`}
        />
        <KpiCard
          label="Expansion Pipeline"
          value={fmtM(summary.expansion_pipeline_arr)}
          sub="open upsell ARR"
        />
        <KpiCard
          label="AI Actions Taken"
          value={`${actions.actions_actioned}/${actions.at_risk_accounts}`}
          sub={`${fmtM(actions.arr_protected)} ARR protected · ${Math.round(
            actions.coverage_pct
          )}% of at-risk`}
        />
      </div>

      {/* Two columns: at-risk + expansion */}
      <div className="grid lg:grid-cols-2 gap-5">
        <div>
          <SectionLabel color="#9B2335">Accounts Requiring Attention</SectionLabel>
          {atRisk.map((c) => (
            <Link key={c.id} href={`/customers/${c.id}`} className="block group">
              <div className="bg-white border border-line border-l-[3px] border-l-red rounded-lg px-[13px] py-[10px] mb-2 group-hover:shadow-card transition-shadow">
                <div className="flex justify-between items-baseline">
                  <span className="font-bold text-navy text-[0.86rem]">{c.name}</span>
                  <span className="text-[0.7rem] text-red font-bold">{fmtK(c.arr)} ARR</span>
                </div>
                <div className="text-[0.7rem] text-muted mt-[1px]">
                  {c.industry} · {c.customer_tier} · {c.region}
                </div>
                <div className="text-[0.74rem] text-ink mt-[6px] leading-snug">
                  <b className="text-red">Why:</b> {c.primary_risk_reason}
                </div>
                <div className="text-[0.74rem] text-ink mt-[3px] leading-snug">
                  <b className="text-green">Action:</b> {c.recommended_next_action}
                </div>
              </div>
            </Link>
          ))}
        </div>
        <div>
          <SectionLabel color="#2D5A3D">Expansion Opportunities</SectionLabel>
          {expAccts.map((c) => (
            <Link key={c.id} href={`/customers/${c.id}`} className="block group">
              <div className="bg-white border border-line border-l-[3px] border-l-green rounded-lg px-[13px] py-[10px] mb-2 group-hover:shadow-card transition-shadow">
                <div className="flex justify-between items-baseline">
                  <span className="font-bold text-navy text-[0.86rem]">{c.name}</span>
                  <span className="text-[0.7rem] text-green font-bold">
                    +{fmtK(c.expansion_pipeline_arr || 0)}
                  </span>
                </div>
                <div className="text-[0.7rem] text-muted mt-[1px]">
                  {c.industry} · NRR {c.nrr_pct ?? "?"}% ·{" "}
                  {Math.round((c.upsell_likelihood || 0) * 100)}% likely
                </div>
                <div className="text-[0.74rem] text-ink mt-[6px] leading-snug">
                  <b className="text-green">Signal:</b> {c.roi_outcome}; adoption{" "}
                  {c.adoption_score ?? "?"}%
                </div>
                <div className="text-[0.74rem] text-ink mt-[3px] leading-snug">
                  <b className="text-navy">Next:</b> {c.recommended_next_action}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
