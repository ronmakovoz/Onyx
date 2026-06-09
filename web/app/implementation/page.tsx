"use client";

import { useEffect, useState } from "react";
import {
  getJSON,
  postJSON,
  AgentResult,
  ImplRow,
  confBg,
  confColors,
  implNextAction,
} from "@/lib/api";
import { PageHeader, Pill, ProgressBar, SectionLabel, Spinner } from "@/components/ui";
import AgentReport from "@/components/AgentReport";

export default function ImplementationPage() {
  const [rows, setRows] = useState<ImplRow[] | null>(null);
  const [selIdx, setSelIdx] = useState(0);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AgentResult | null>(null);

  useEffect(() => {
    getJSON<ImplRow[]>("/api/implementation/overview").then(setRows).catch(() => setRows([]));
  }, []);

  if (!rows) return <Spinner label="Loading implementations…" />;
  if (!rows.length)
    return (
      <div>
        <PageHeader title="Implementation Digest" />
        <div className="text-muted text-sm">No active implementations found.</div>
      </div>
    );

  const n = rows.length;
  const atRisk = rows.filter((r) => ["Very Low", "Low"].includes(r.launch_confidence)).length;
  const medium = rows.filter((r) => r.launch_confidence === "Medium").length;
  const onTrack = rows.filter((r) => r.launch_confidence === "High").length;
  const avgPct = Math.round(rows.reduce((a, r) => a + r.pct_complete, 0) / n);
  const notKicked = rows.filter((r) => !r.kicked_off).length;
  const worst = rows.filter((r) => ["Very Low", "Low"].includes(r.launch_confidence)).slice(0, 3);

  const kpis: [string, string, string, string][] = [
    ["Active Projects", String(n), "#1B1040", "#FFFFFF"],
    ["At Risk", String(atRisk), "#9B2335", "#FDF1F2"],
    ["Medium Conf.", String(medium), "#7A5C1E", "#FDFAF0"],
    ["On Track", String(onTrack), "#2D5A3D", "#F0FAF4"],
    ["Avg Completion", `${avgPct}%`, "#1B1040", "#FFFFFF"],
    ["Not Kicked Off", String(notKicked), "#6B6280", "#FFFFFF"],
  ];

  const sel = rows[selIdx];
  const selCc = confColors[sel.launch_confidence] || "#1B1040";

  const runAnalysis = async () => {
    setRunning(true);
    setResult(null);
    try {
      const r = await postJSON<AgentResult>("/api/agents/run", {
        agent_name: "ImplementationAgent",
        customer_id: sel.customer_id,
      });
      setResult(r);
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Implementation Digest"
        subtitle="Delivery health and timeline across all active implementations"
      />

      {/* KPI strip */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-[10px] mb-5">
        {kpis.map(([label, val, color, bg]) => (
          <div key={label} className="rounded-[10px] border border-line px-4 py-[14px]" style={{ background: bg }}>
            <div className="text-[0.64rem] font-bold uppercase tracking-[0.08em]" style={{ color }}>
              {label}
            </div>
            <div className="text-[1.5rem] font-extrabold mt-1" style={{ color }}>
              {val}
            </div>
          </div>
        ))}
      </div>

      {/* This week's priorities */}
      {worst.length ? (
        <>
          <SectionLabel color="#9B2335">This Week&apos;s Priorities</SectionLabel>
          <div className="grid md:grid-cols-3 gap-[10px] mb-5">
            {worst.map((r) => {
              const cc = confColors[r.launch_confidence] || "#1B1040";
              return (
                <div
                  key={r.customer_id}
                  className="bg-white border border-line rounded-[10px] px-[14px] py-3"
                  style={{ borderLeft: `3px solid ${cc}` }}
                >
                  <div className="flex justify-between items-baseline">
                    <span className="font-bold text-navy text-[0.88rem]">{r.customer_name}</span>
                    <span className="text-[0.66rem] font-bold" style={{ color: cc }}>
                      {r.launch_confidence} confidence
                    </span>
                  </div>
                  <div className="text-[0.70rem] text-muted mt-[2px]">
                    {Math.round(r.pct_complete)}% complete ·{" "}
                    {r.days_behind_schedule === 0 ? "on time" : `${r.days_behind_schedule}d behind`} · owner{" "}
                    {r.implementation_owner}
                  </div>
                  <div className="text-[0.78rem] text-navy font-semibold mt-[7px]">→ {implNextAction(r)}</div>
                </div>
              );
            })}
          </div>
        </>
      ) : null}

      {/* Project table */}
      <SectionLabel>
        All Projects <span className="font-normal normal-case tracking-normal">— sorted by risk</span>
      </SectionLabel>
      <div className="bg-white border border-line rounded-[14px] shadow-card overflow-x-auto mb-5">
        <div className="min-w-[1000px]">
          <div className="grid grid-cols-[1.5fr_1fr_1.2fr_0.65fr_0.85fr_0.95fr_2.2fr_1fr] gap-3 px-[18px] py-[10px] text-[0.62rem] font-bold text-faint uppercase tracking-[0.10em]">
            <div>Customer</div>
            <div>Confidence</div>
            <div>Progress</div>
            <div>Stones</div>
            <div>Go-Live</div>
            <div>Schedule</div>
            <div>Recommended Action</div>
            <div>Owner</div>
          </div>
          {rows.map((r, i) => {
            const cc = confColors[r.launch_confidence] || "#1B1040";
            return (
              <div
                key={r.customer_id}
                onClick={() => setSelIdx(i)}
                className="grid grid-cols-[1.5fr_1fr_1.2fr_0.65fr_0.85fr_0.95fr_2.2fr_1fr] gap-3 px-[18px] py-[13px] items-center border-t border-[#F0EBE7] text-[0.82rem] cursor-pointer hover:bg-[#FBF7FA]"
              >
                <div className="font-bold text-navy">{r.customer_name}</div>
                <div>
                  <Pill color={cc} bg={confBg[r.launch_confidence] || "#F5F2EE"}>
                    {r.launch_confidence}
                  </Pill>
                </div>
                <div className="flex items-center gap-2">
                  <ProgressBar pct={r.pct_complete} color={cc} />
                  <span className="text-[0.72rem] font-bold text-ink min-w-[30px]">
                    {Math.round(r.pct_complete)}%
                  </span>
                </div>
                <div className="text-ink">
                  {r.milestones_complete}/{r.milestones_total}
                </div>
                <div className="text-ink">{r.go_live_target || "—"}</div>
                <div>
                  {r.days_behind_schedule === 0 ? (
                    <span className="text-green font-semibold">On time</span>
                  ) : (
                    <span className="text-red font-semibold">{r.days_behind_schedule}d behind</span>
                  )}
                </div>
                <div className="text-navy font-medium">{implNextAction(r)}</div>
                <div className="text-muted">{r.implementation_owner}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Deep dive */}
      <div className="flex items-center justify-between gap-4 mb-2">
        <SectionLabel className="!mb-0">Project Deep Dive</SectionLabel>
        <select
          value={selIdx}
          onChange={(e) => {
            setSelIdx(Number(e.target.value));
            setResult(null);
          }}
          className="bg-white border border-[#E0D8E8] rounded-xl px-3 py-2 text-[0.88rem] text-navy shadow-card outline-none"
        >
          {rows.map((r, i) => (
            <option key={r.customer_id} value={i}>
              {r.customer_name}
            </option>
          ))}
        </select>
      </div>

      <div
        className="bg-white border border-line rounded-xl px-5 py-4"
        style={{ borderLeft: `4px solid ${selCc}` }}
      >
        <div className="flex justify-between items-baseline mb-[10px] flex-wrap gap-2">
          <div className="text-[1.05rem] font-extrabold text-navy">{sel.customer_name}</div>
          <div className="text-[0.8rem] font-bold" style={{ color: selCc }}>
            {sel.launch_confidence} launch confidence · {sel.overall_status}
          </div>
        </div>
        <div className="flex gap-[10px] flex-wrap mb-3">
          {(
            [
              ["Kicked Off", sel.kickoff_date ? `Yes · ${sel.kickoff_date}` : sel.kicked_off ? "In progress" : "Not started", "#1B1040"],
              ["Contract Age", sel.days_post_signature !== null ? `${sel.days_post_signature} days` : "—", "#1B1040"],
              ["Go-Live Target", sel.go_live_target || "—", "#1B1040"],
              ["To Go-Live", sel.days_to_go_live !== null ? `${sel.days_to_go_live} days` : "—", "#1B1040"],
              ["Schedule", sel.days_behind_schedule === 0 ? "On time" : `${sel.days_behind_schedule}d behind`, sel.days_behind_schedule === 0 ? "#2D5A3D" : "#9B2335"],
              ["Milestones", `${sel.milestones_complete} / ${sel.milestones_total} complete`, "#1B1040"],
            ] as [string, string, string][]
          ).map(([lbl, val, color]) => (
            <div key={lbl} className="bg-chip rounded-lg px-[13px] py-[7px]">
              <div className="text-[0.58rem] font-bold text-muted uppercase tracking-[0.08em]">{lbl}</div>
              <div className="text-[0.92rem] font-extrabold" style={{ color }}>
                {val}
              </div>
            </div>
          ))}
        </div>
        <div className="text-[0.78rem] text-ink leading-relaxed">
          <b className="text-green">Implemented:</b> {sel.completed_milestones.join(", ") || "None yet"}
        </div>
        <div className="text-[0.78rem] text-ink leading-relaxed mt-[3px]">
          <b className="text-amber">In progress:</b> {sel.in_progress_milestones.join(", ") || "—"}
        </div>
        <div className="text-[0.78rem] text-ink leading-relaxed mt-[3px]">
          <b className="text-red">Blockers:</b>{" "}
          {sel.active_blockers.length ? sel.active_blockers.join(" · ") : "None recorded"}
        </div>
        <div className="mt-[10px] px-3 py-[9px] bg-lavender rounded-lg text-[0.82rem] text-navy font-semibold">
          Recommended action: {implNextAction(sel)}
        </div>
      </div>

      <div className="mt-3">
        <button
          onClick={runAnalysis}
          disabled={running}
          className="bg-navy text-white rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#2D1A5E] disabled:opacity-60"
        >
          {running ? "Analysing…" : "Generate AI analysis"}
        </button>
        {running ? <Spinner label={`Analysing ${sel.customer_name}…`} /> : null}
        {result && !running ? (
          <div className="mt-3">
            <AgentReport result={result} />
          </div>
        ) : null}
      </div>
    </div>
  );
}
