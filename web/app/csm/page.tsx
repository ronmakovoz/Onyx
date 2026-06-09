"use client";

import { useEffect, useState } from "react";
import { getJSON, fmtM, fmtK, healthColor } from "@/lib/api";
import { KpiCard, PageHeader, Spinner } from "@/components/ui";

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
  return ["#9B2335", "Coach on: " + issues.slice(0, 3).join(" · ")];
}

export default function CsmPage() {
  const [data, setData] = useState<Overview | null>(null);

  useEffect(() => {
    getJSON<Overview>("/api/csm/overview").then(setData).catch(() => setData({ csms: [], team: {} }));
  }, []);

  if (!data) return <Spinner label="Loading CSM performance…" />;
  const { csms, team } = data;

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

      {csms.map((s) => {
        const hc = healthColor(s.avg_health);
        const tot = Math.max(s.accounts, 1);
        const [fc, fmsg] = csmFocus(s);
        const metrics: [string, string, string][] = [
          ["ARR at Risk", fmtM(s.arr_risk), s.arr_risk ? "#9B2335" : "#2D5A3D"],
          ["Avg NRR", `${Math.round(s.avg_nrr)}%`, "#1B1040"],
          ["Expansion", fmtK(s.expansion), "#2D5A3D"],
          ["Renewals 90d", String(s.renewals_90), "#1B1040"],
          [
            "Risk Actioned",
            `${s.actioned}/${s.at_risk_n}`,
            !s.at_risk_n || s.actioned / s.at_risk_n >= 0.5 ? "#2D5A3D" : "#9B2335",
          ],
        ];
        return (
          <div key={s.csm} className="bg-white border border-line rounded-[10px] px-4 py-[13px] mb-[9px]">
            <div className="flex items-center gap-[14px] flex-wrap">
              <div className="basis-[150px] shrink-0">
                <div className="font-bold text-navy text-[0.92rem]">{s.csm}</div>
                <div className="text-[0.68rem] text-muted">
                  {s.accounts} accounts · {fmtM(s.arr)} ARR
                </div>
              </div>
              <div className="basis-[70px] text-center shrink-0">
                <div className="text-[1.3rem] font-extrabold leading-none" style={{ color: hc }}>
                  {Math.round(s.avg_health)}
                </div>
                <div className="text-[0.56rem] text-muted uppercase tracking-[0.08em]">Avg Health</div>
              </div>
              <div className="flex-1 min-w-[160px]">
                <div className="flex h-2 rounded-full overflow-hidden gap-[2px]">
                  <div style={{ width: `${(s.high / tot) * 100}%`, background: "#9B2335" }} />
                  <div style={{ width: `${(s.med / tot) * 100}%`, background: "#C9952A" }} />
                  <div style={{ width: `${(s.low / tot) * 100}%`, background: "#2D5A3D" }} />
                </div>
                <div className="flex gap-3 mt-[5px] text-[0.66rem]">
                  <span className="text-red font-semibold">{s.high} high</span>
                  <span className="text-amber font-semibold">{s.med} med</span>
                  <span className="text-green font-semibold">{s.low} healthy</span>
                </div>
              </div>
              {metrics.map(([lbl, val, color]) => (
                <div key={lbl} className="basis-[88px] text-center border-l border-line pl-3 shrink-0">
                  <div className="text-[0.95rem] font-extrabold leading-tight" style={{ color }}>
                    {val}
                  </div>
                  <div className="text-[0.56rem] text-muted uppercase tracking-[0.08em]">{lbl}</div>
                </div>
              ))}
            </div>
            <div
              className="mt-[9px] px-3 py-[7px] rounded-lg text-[0.76rem] font-semibold"
              style={{ color: fc, background: fc === "#2D5A3D" ? "#EFF6F1" : "#FDF6F3" }}
            >
              {fmsg}
            </div>
          </div>
        );
      })}
    </div>
  );
}
