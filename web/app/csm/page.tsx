"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getJSON, fmtM, fmtK, healthColor, riskColor, riskBg, Customer } from "@/lib/api";
import { KpiCard, PageHeader, Pill, SectionLabel, Spinner } from "@/components/ui";

type CsmRow = {
  csm: string;
  accounts: number;
  arr: number;
  avg_health: number;
  avg_nrr: number;
  high: number;
  med: number;
  low: number;
  expansion: number;
  renewals_90: number;
  arr_risk: number;
  qbr_overdue: number;
  champ_gap: number;
  escalations: number;
  at_risk_n: number;
  actioned: number;
};

type Overview = { csms: CsmRow[]; team: Record<string, number> };

function csmFocus(s: CsmRow): [string, string] {
  const issues: string[] = [];
  if (s.arr_risk) issues.push(`${fmtM(s.arr_risk)} ARR at risk`);
  if (s.at_risk_n && s.actioned / s.at_risk_n < 0.5)
    issues.push(`only ${s.actioned}/${s.at_risk_n} at-risk accounts actioned`);
  if (s.qbr_overdue) issues.push(`${s.qbr_overdue} overdue QBR${s.qbr_overdue !== 1 ? "s" : ""}`);
  if (s.champ_gap) issues.push(`champion gap at ${s.champ_gap} account${s.champ_gap !== 1 ? "s" : ""}`);
  if (s.escalations) issues.push(`${s.escalations} open escalation${s.escalations !== 1 ? "s" : ""}`);
  if (!issues.length) return ["#2D5A3D", "Book is healthy — push expansion and references"];
  return ["#C43D1B", "Coach on: " + issues.slice(0, 3).join(" · ")];
}

const GRID =
  "grid grid-cols-[1.5fr_0.7fr_1.6fr_0.85fr_0.7fr_0.9fr_0.9fr_0.95fr] gap-3 px-[18px] items-center";

export default function CsmPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selected, setSelected] = useState<CsmRow | null>(null);

  useEffect(() => {
    getJSON<Overview>("/api/csm/overview").then(setData).catch(() => setData({ csms: [], team: {} }));
    getJSON<Customer[]>("/api/customers").then(setCustomers).catch(() => {});
  }, []);

  if (!data) return <Spinner label="Loading CSM performance…" />;
  const { csms, team } = data;

  const book = selected
    ? customers
        .filter((c) => c.csm_owner === selected.csm)
        .sort((a, b) => a.health_score - b.health_score)
    : [];
  const selFocus = selected ? csmFocus(selected) : null;

  return (
    <div>
      <PageHeader
        title="CSM Performance"
        subtitle="Portfolio health, ARR, renewals and expansion by Customer Success Manager"
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        <KpiCard
          label="CS Managers"
          value={String(team.managers ?? 0)}
          sub={`${Math.round((team.accounts || 0) / Math.max(team.managers || 1, 1))} accounts · ${fmtM(
            (team.total_arr || 0) / Math.max(team.managers || 1, 1)
          )} ARR avg per CSM`}
        />
        <KpiCard label="ARR at Risk (team)" value={fmtM(team.arr_risk || 0)} sub="in high-risk accounts" />
        <KpiCard
          label="AI Action Follow-Through"
          value={`${team.actioned ?? 0}/${team.at_risk_n ?? 0}`}
          sub="at-risk accounts actioned"
        />
        <KpiCard label="Engagement Hygiene" value={String(team.qbr_overdue ?? 0)} sub="overdue QBRs across the team" />
      </div>

      <SectionLabel>
        Team <span className="font-normal normal-case tracking-normal">— sorted by portfolio health; click a manager for their book</span>
      </SectionLabel>
      <div className="bg-white border border-line rounded-[14px] shadow-card overflow-x-auto">
        <div className="min-w-[1000px]">
          <div className={`${GRID} py-[10px] text-[0.62rem] font-bold text-faint uppercase tracking-[0.10em]`}>
            <div>Manager</div>
            <div>Health</div>
            <div>Book Mix</div>
            <div>ARR at Risk</div>
            <div>NRR</div>
            <div>Expansion</div>
            <div>Renewals 90d</div>
            <div>Risk Actioned</div>
          </div>
          {csms.map((s) => {
            const hc = healthColor(s.avg_health);
            const tot = Math.max(s.accounts, 1);
            const followOk = !s.at_risk_n || s.actioned / s.at_risk_n >= 0.5;
            return (
              <div
                key={s.csm}
                onClick={() => setSelected(s)}
                className={`${GRID} py-[13px] border-t border-[#F0EBE7] text-[0.82rem] cursor-pointer hover:bg-[#FBF7FA]`}
              >
                <div>
                  <div className="font-bold text-navy">{s.csm}</div>
                  <div className="text-[0.68rem] text-muted">
                    {s.accounts} accounts · {fmtM(s.arr)} ARR
                  </div>
                </div>
                <div className="text-[1.05rem] font-extrabold" style={{ color: hc }}>
                  {Math.round(s.avg_health)}
                </div>
                <div>
                  <div className="flex h-2 rounded-full overflow-hidden gap-[2px]">
                    <div style={{ width: `${(s.high / tot) * 100}%`, background: "#C43D1B" }} />
                    <div style={{ width: `${(s.med / tot) * 100}%`, background: "#C9952A" }} />
                    <div style={{ width: `${(s.low / tot) * 100}%`, background: "#2D5A3D" }} />
                  </div>
                  <div className="text-[0.64rem] text-muted mt-1">
                    {s.high} high · {s.med} med · {s.low} healthy
                  </div>
                </div>
                <div className="font-bold" style={{ color: s.arr_risk ? "#C43D1B" : "#2D5A3D" }}>
                  {fmtM(s.arr_risk)}
                </div>
                <div className="text-ink font-semibold">{Math.round(s.avg_nrr)}%</div>
                <div className="text-green font-semibold">{fmtK(s.expansion)}</div>
                <div className="text-ink">{s.renewals_90}</div>
                <div className="font-bold" style={{ color: followOk ? "#2D5A3D" : "#C43D1B" }}>
                  {s.actioned}/{s.at_risk_n}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Slide-over: CSM deep dive */}
      {selected ? (
        <div className="fixed inset-0 z-50">
          <div
            className="absolute inset-0 bg-navy/30 backdrop-blur-[2px]"
            onClick={() => setSelected(null)}
          />
          <div className="absolute right-0 top-0 h-full w-full max-w-[640px] bg-white shadow-2xl overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-line border-t-4 border-t-navy px-6 py-4 flex items-center justify-between z-10">
              <div>
                <div className="text-[0.62rem] font-bold text-faint uppercase tracking-[0.12em]">
                  CSM Deep Dive
                </div>
                <div className="text-[1.15rem] font-extrabold text-navy leading-tight">{selected.csm}</div>
                <div className="text-[0.74rem] text-muted mt-[2px]">
                  {selected.accounts} accounts · {fmtM(selected.arr)} ARR · avg health{" "}
                  {Math.round(selected.avg_health)}
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="rounded-full border border-line w-8 h-8 flex items-center justify-center text-muted hover:text-navy hover:border-navy text-[1rem] leading-none"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="px-6 py-5">
              {selFocus ? (
                <div
                  className="px-3 py-[9px] rounded-lg text-[0.84rem] font-semibold mb-4"
                  style={{
                    color: selFocus[0],
                    background: selFocus[0] === "#2D5A3D" ? "#EFF6F1" : "#FDF6F3",
                  }}
                >
                  {selFocus[1]}
                </div>
              ) : null}

              <div className="grid grid-cols-3 gap-[10px] mb-5">
                {(
                  [
                    ["ARR at Risk", fmtM(selected.arr_risk), selected.arr_risk ? "#C43D1B" : "#2D5A3D"],
                    ["Avg NRR", `${Math.round(selected.avg_nrr)}%`, "#161616"],
                    ["Expansion", fmtK(selected.expansion), "#2D5A3D"],
                    ["Renewals 90d", String(selected.renewals_90), "#161616"],
                    ["Overdue QBRs", String(selected.qbr_overdue), selected.qbr_overdue ? "#C43D1B" : "#2D5A3D"],
                    ["Champion Gaps", String(selected.champ_gap), selected.champ_gap ? "#C43D1B" : "#2D5A3D"],
                    ["Open Escalations", String(selected.escalations), selected.escalations ? "#C43D1B" : "#2D5A3D"],
                    [
                      "Risk Actioned",
                      `${selected.actioned}/${selected.at_risk_n}`,
                      !selected.at_risk_n || selected.actioned / selected.at_risk_n >= 0.5
                        ? "#2D5A3D"
                        : "#C43D1B",
                    ],
                  ] as [string, string, string][]
                ).map(([lbl, val, color]) => (
                  <div key={lbl} className="bg-chip rounded-lg px-[13px] py-[8px]">
                    <div className="text-[0.58rem] font-bold text-muted uppercase tracking-[0.08em]">{lbl}</div>
                    <div className="text-[0.95rem] font-extrabold" style={{ color }}>
                      {val}
                    </div>
                  </div>
                ))}
              </div>

              <SectionLabel>
                Book of Business{" "}
                <span className="font-normal normal-case tracking-normal">— sorted by health, click to open</span>
              </SectionLabel>
              <div className="border border-line rounded-xl overflow-hidden">
                {book.map((c) => (
                  <Link
                    key={c.id}
                    href={`/customers/${c.id}`}
                    className="flex items-center justify-between gap-3 px-4 py-3 border-t border-[#F0EBE7] first:border-t-0 hover:bg-[#FBF7FA]"
                  >
                    <div className="min-w-0">
                      <div className="font-bold text-navy text-[0.84rem] truncate">{c.name}</div>
                      <div className="text-[0.68rem] text-muted">
                        {c.industry} · ${c.arr.toLocaleString()} ARR
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span
                        className="text-[0.95rem] font-extrabold"
                        style={{ color: healthColor(c.health_score) }}
                      >
                        {c.health_score}
                      </span>
                      <Pill color={riskColor[c.risk_level] || "#6B6280"} bg={riskBg[c.risk_level] || "#F5F2EE"}>
                        {c.risk_level === "Low" ? "Healthy" : `${c.risk_level} risk`}
                      </Pill>
                    </div>
                  </Link>
                ))}
                {!book.length ? (
                  <div className="px-4 py-3 text-[0.8rem] text-muted">No accounts found.</div>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
