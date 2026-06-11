"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getJSON, Customer, fmtM, fmtK } from "@/lib/api";
import { KpiCard, PageHeader, SectionLabel, Spinner } from "@/components/ui";

type Summary = Record<string, any>;
type ActionSummary = Record<string, any>;

function daysUntil(dateStr: string | undefined): number | null {
  if (!dateStr) return null;
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

function RenewalBadge({ days }: { days: number | null }) {
  if (days === null) return null;
  if (days <= 30)
    return (
      <span className="text-[0.62rem] font-bold bg-red/10 text-red px-2 py-[2px] rounded-full whitespace-nowrap">
        {days <= 0 ? "Overdue" : `${days}d to renew`}
      </span>
    );
  if (days <= 60)
    return (
      <span className="text-[0.62rem] font-bold bg-[#FFF3CD] text-[#856404] px-2 py-[2px] rounded-full whitespace-nowrap">
        {days}d to renew
      </span>
    );
  return (
    <span className="text-[0.62rem] text-muted px-2 py-[2px] rounded-full border border-line whitespace-nowrap">
      {days}d to renew
    </span>
  );
}

function HealthBar({ customers }: { customers: Customer[] }) {
  const healthy = customers.filter((c) => c.risk_level === "Low").length;
  const medium = customers.filter((c) => c.risk_level === "Medium").length;
  const high = customers.filter((c) => c.risk_level === "High").length;
  const total = customers.length || 1;
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 flex rounded-full overflow-hidden h-[8px]">
        <div style={{ width: `${(healthy / total) * 100}%` }} className="bg-green" />
        <div style={{ width: `${(medium / total) * 100}%` }} className="bg-[#F5A623]" />
        <div style={{ width: `${(high / total) * 100}%` }} className="bg-red" />
      </div>
      <div className="flex gap-3 text-[0.65rem] text-[#CFC8E8] whitespace-nowrap">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-green inline-block" />
          {healthy} healthy
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-[#F5A623] inline-block" />
          {medium} watch
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red inline-block" />
          {high} critical
        </span>
      </div>
    </div>
  );
}

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
      status representing <B>{fmtM(arrRisk)}</B> of ARR — most notably {riskNames}. The 90-day
      renewal forecast stands at <B>{fc}%</B>, with {esc} active escalation{esc !== 1 ? "s" : ""}{" "}
      requiring attention. Expansion pipeline totals <B>{fmtM(exp)}</B>, led by {leadInd} accounts.
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

  const urgentRenewals = customers
    .filter((c) => {
      const d = daysUntil(c.renewal_date);
      return d !== null && d <= 60 && c.risk_level !== "Low";
    })
    .sort((a, b) => (daysUntil(a.renewal_date) ?? 999) - (daysUntil(b.renewal_date) ?? 999))
    .slice(0, 3);

  const expAccts = customers
    .filter((c) => c.expansion_pipeline_arr)
    .sort(
      (a, b) =>
        (b.expansion_pipeline_arr || 0) * (b.upsell_likelihood || 0) -
        (a.expansion_pipeline_arr || 0) * (a.upsell_likelihood || 0)
    )
    .slice(0, 5);

  const nrr = summary.nrr_pct ?? 0;
  const nrrColor = nrr >= 105 ? "text-green" : nrr < 100 ? "text-red" : "text-[#F5A623]";
  const fcPct = summary.renewal_forecast_pct ?? 0;
  const fcColor = fcPct >= 90 ? "text-green" : fcPct < 80 ? "text-red" : "text-[#F5A623]";

  return (
    <div>
      <div className="flex items-end justify-between mb-4">
        <div>
          <h1 className="text-[1.55rem] font-extrabold text-navy leading-tight">
            Executive Dashboard
          </h1>
          <p className="text-[0.8rem] text-muted mt-[2px]">
            Portfolio health · renewal risks · growth signals
          </p>
        </div>
        <div className="text-[0.7rem] text-muted hidden lg:block">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            month: "long",
            day: "numeric",
            year: "numeric",
          })}
        </div>
      </div>

      {/* AI Executive Summary */}
      <div
        className="rounded-xl px-5 py-4 mb-5"
        style={{ background: "linear-gradient(135deg, #3B2D72 0%, #51409B 100%)" }}
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[0.62rem] font-bold text-[#B9AEE0] uppercase tracking-[0.12em]">
            AI Executive Summary
          </span>
          <span className="text-[0.58rem] text-[#CFC8E8] bg-white/10 px-2 py-[2px] rounded-full">
            auto-generated · live data
          </span>
        </div>
        <div className="text-[#F0EDF7] text-[0.92rem] leading-[1.65] mb-3">
          {buildExecSummary(summary, customers)}
        </div>
        <HealthBar customers={customers} />
      </div>

      {/* 5 KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-5">
        <div className="bg-white border border-line rounded-xl shadow-card p-4 flex flex-col gap-1">
          <div className="text-[0.62rem] text-muted uppercase tracking-[0.10em] font-bold">
            Net Revenue Retention
          </div>
          <div className={`text-[1.6rem] font-extrabold leading-none ${nrrColor}`}>
            {summary.nrr_pct}%
          </div>
          <div className="text-[0.68rem] text-muted">ARR-weighted · GRR {summary.grr_pct}%</div>
        </div>
        <div className="bg-white border border-line rounded-xl shadow-card p-4 flex flex-col gap-1 border-l-[3px] border-l-red">
          <div className="text-[0.62rem] text-muted uppercase tracking-[0.10em] font-bold">
            ARR at Risk
          </div>
          <div className="text-[1.6rem] font-extrabold leading-none text-red">
            {fmtM(summary.arr_at_risk)}
          </div>
          <div className="text-[0.68rem] text-muted">
            {summary.critical_count} critical · {summary.at_risk_count} medium
          </div>
        </div>
        <div className="bg-white border border-line rounded-xl shadow-card p-4 flex flex-col gap-1">
          <div className="text-[0.62rem] text-muted uppercase tracking-[0.10em] font-bold">
            Renewal Forecast (90d)
          </div>
          <div className={`text-[1.6rem] font-extrabold leading-none ${fcColor}`}>
            {summary.renewal_forecast_pct}%
          </div>
          <div className="text-[0.68rem] text-muted">
            {fmtM(summary.upcoming_renewal_arr || 0)} up for renewal
          </div>
        </div>
        <div className="bg-white border border-line rounded-xl shadow-card p-4 flex flex-col gap-1 border-l-[3px] border-l-green">
          <div className="text-[0.62rem] text-muted uppercase tracking-[0.10em] font-bold">
            Expansion Pipeline
          </div>
          <div className="text-[1.6rem] font-extrabold leading-none text-green">
            {fmtM(summary.expansion_pipeline_arr)}
          </div>
          <div className="text-[0.68rem] text-muted">open upsell ARR</div>
        </div>
        <div className="bg-white border border-line rounded-xl shadow-card p-4 flex flex-col gap-1">
          <div className="text-[0.62rem] text-muted uppercase tracking-[0.10em] font-bold">
            AI Coverage
          </div>
          <div className="text-[1.6rem] font-extrabold leading-none text-navy">
            {actions.actions_actioned}/{actions.at_risk_accounts}
          </div>
          <div className="text-[0.68rem] text-muted">
            {fmtM(actions.arr_protected)} protected · {Math.round(actions.coverage_pct)}% of at-risk
          </div>
        </div>
      </div>

      {/* Priority Actions strip */}
      {urgentRenewals.length > 0 && (
        <div className="mb-5 bg-[#FFF8F0] border border-[#F5A623]/40 rounded-xl px-5 py-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[0.62rem] font-bold text-[#856404] uppercase tracking-[0.10em]">
              Renewing Soon — Act Now
            </span>
            <span className="text-[0.58rem] bg-[#F5A623]/20 text-[#856404] px-2 py-[2px] rounded-full">
              {urgentRenewals.length} account{urgentRenewals.length !== 1 ? "s" : ""} within 60 days
            </span>
          </div>
          <div className="grid md:grid-cols-3 gap-3">
            {urgentRenewals.map((c) => {
              const days = daysUntil(c.renewal_date);
              return (
                <Link key={c.id} href={`/customers/${c.id}`} className="block group">
                  <div className="bg-white rounded-lg border border-[#F5A623]/30 px-3 py-3 group-hover:shadow-card transition-shadow">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-bold text-navy text-[0.84rem]">{c.name}</span>
                      <RenewalBadge days={days} />
                    </div>
                    <div className="text-[0.68rem] text-muted mb-2">
                      {fmtK(c.arr)} ARR · {c.customer_tier}
                    </div>
                    <div className="text-[0.72rem] text-ink leading-snug">
                      {c.recommended_next_action}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* Two columns: at-risk + expansion */}
      <div className="grid lg:grid-cols-2 gap-5">
        <div>
          <SectionLabel color="#9B2335">Accounts Requiring Attention</SectionLabel>
          {atRisk.map((c) => {
            const days = daysUntil(c.renewal_date);
            return (
              <Link key={c.id} href={`/customers/${c.id}`} className="block group">
                <div className="bg-white border border-line border-l-[3px] border-l-red rounded-lg px-[13px] py-[10px] mb-2 group-hover:shadow-card transition-shadow">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-navy text-[0.86rem]">{c.name}</span>
                    <div className="flex items-center gap-2">
                      <RenewalBadge days={days} />
                      <span className="text-[0.7rem] text-red font-bold">{fmtK(c.arr)}</span>
                    </div>
                  </div>
                  <div className="text-[0.7rem] text-muted mt-[1px]">
                    {c.industry} · {c.customer_tier} · health {c.health_score}/100
                  </div>
                  <div className="text-[0.74rem] text-ink mt-[6px] leading-snug">
                    <b className="text-red">Why:</b> {c.primary_risk_reason}
                  </div>
                  <div className="text-[0.74rem] text-ink mt-[3px] leading-snug">
                    <b className="text-green">Action:</b> {c.recommended_next_action}
                  </div>
                </div>
              </Link>
            );
          })}
          <Link
            href="/customers?filter=high-risk"
            className="block text-center text-[0.72rem] text-muted hover:text-navy mt-1 transition-colors"
          >
            View all high-risk accounts →
          </Link>
        </div>

        <div>
          <SectionLabel color="#2D5A3D">Top Expansion Opportunities</SectionLabel>
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
                  {Math.round((c.upsell_likelihood || 0) * 100)}% close probability
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
          <Link
            href="/growth"
            className="block text-center text-[0.72rem] text-muted hover:text-navy mt-1 transition-colors"
          >
            Full whitespace analysis →
          </Link>
        </div>
      </div>
    </div>
  );
}
