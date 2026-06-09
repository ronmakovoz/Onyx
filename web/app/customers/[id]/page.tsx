"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  getJSON,
  postJSON,
  AgentResult,
  fmtUSD,
  fmtK,
  riskColor,
  riskBg,
  agentDisplayName,
} from "@/lib/api";
import { Card, Pill, ProgressBar, SectionLabel, Spinner, StatChip, TabBar } from "@/components/ui";
import AgentReport from "@/components/AgentReport";

const TABS = ["Overview", "AI Agents", "Usage & Health", "Implementation", "Support", "People", "Renewal"];

const AGENT_MENU: [string, string, string][] = [
  ["CustomerHealthAgent", "Assess", "Health Assessment"],
  ["ImplementationAgent", "Assess", "Implementation Report"],
  ["ExpansionOpportunityAgent", "Grow", "Expansion Opportunity"],
  ["QBRPreparationAgent", "Grow", "Prepare QBR"],
  ["SuccessPlanAgent", "Grow", "Build Success Plan"],
  ["BriefingAgent", "Communicate", "Generate CEO Briefing"],
  ["EscalationCommanderAgent", "Respond", "Escalation Commander"],
  ["SkeptikQAAgent", "Verify", "Skeptik QA Review"],
];

const ACTION_STATUSES = ["Open", "In Progress", "Done", "Dismissed"] as const;

function HealthChart({ history }: { history: { date: string; health_score: number }[] }) {
  if (!history.length) return null;
  const W = 640;
  const H = 160;
  const PAD = 14;
  const pts = history.map((h, i) => {
    const x = PAD + (i / Math.max(history.length - 1, 1)) * (W - 2 * PAD);
    const y = H - PAD - (h.health_score / 100) * (H - 2 * PAD);
    return [x, y] as const;
  });
  return (
    <div className="bg-white border border-line rounded-[10px] px-3 pt-3 pb-1">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-[160px]">
        {[25, 50, 75].map((g) => {
          const y = H - PAD - (g / 100) * (H - 2 * PAD);
          return <line key={g} x1={PAD} x2={W - PAD} y1={y} y2={y} stroke="#F0EDE7" strokeWidth={1} />;
        })}
        <polyline
          fill="none"
          stroke="#1B1040"
          strokeWidth={2.2}
          points={pts.map(([x, y]) => `${x},${y}`).join(" ")}
        />
        {pts.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r={2.4} fill="#1B1040" />
        ))}
      </svg>
      <div className="flex justify-between text-[0.62rem] text-muted px-1 pb-1">
        <span>{history[0].date.slice(0, 10)}</span>
        <span>{history[history.length - 1].date.slice(0, 10)}</span>
      </div>
    </div>
  );
}

export default function CustomerDetailPage() {
  const params = useParams<{ id: string }>();
  const cid = Number(params.id);

  const [data, setData] = useState<any>(null);
  const [tab, setTab] = useState("Overview");
  const [action, setAction] = useState<any>(null);
  const [agent, setAgent] = useState("CustomerHealthAgent");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AgentResult | null>(null);

  useEffect(() => {
    getJSON(`/api/customers/${cid}/360`).then(setData).catch(() => setData({}));
    getJSON(`/api/actions/${cid}`).then(setAction).catch(() => {});
  }, [cid]);

  if (!data) return <Spinner label="Loading account…" />;
  if (!data.customer) return <div className="text-red text-sm">Customer not found.</div>;

  const c = data.customer;
  const tickets: any[] = data.tickets || [];
  const escs: any[] = data.escalations || [];
  const stk: any[] = data.stakeholders || [];
  const metrics: any[] = data.metrics || [];
  const milestones: any[] = data.milestones || [];
  const notes: any[] = data.meeting_notes || [];
  const impl = data.implementation || null;
  const renewal = data.renewal || null;
  const history: any[] = data.health_history || [];

  const rc = riskColor[c.risk_level] || "#1B1040";
  const rb = riskBg[c.risk_level] || "#F5F2EE";
  const openTickets = tickets.filter((t) => t.status !== "Resolved").length;
  const renewalDays = renewal?.days_to_renewal ?? "?";
  const champColor =
    { Active: "#2D5A3D", Disengaged: "#7A5C1E", "Left Company": "#9B2335" }[
      c.champion_status as string
    ] || "#6B6280";

  // Overview derivations (mirror app.py)
  const rr = c.renewal_risk_score ?? 0;
  const renewConf = Math.round((1 - rr) * 100);
  const rconfColor = renewConf >= 70 ? "#2D5A3D" : renewConf >= 45 ? "#7A5C1E" : "#9B2335";
  const rverdict =
    renewConf >= 70 ? "Likely to Renew" : renewConf < 45 ? "Renewal at Risk" : "Needs Attention";

  const plan: string[] = [];
  if (c.champion_status === "Left Company") plan.push("Identify and recruit a new executive champion");
  if (escs.length)
    plan.push(`Resolve ${escs.length} open escalation${escs.length !== 1 ? "s" : ""} with daily exec updates`);
  if (openTickets >= 3) plan.push(`Clear support backlog (${openTickets} open tickets)`);
  if ((c.adoption_score ?? 100) < 50) plan.push("Run an adoption workshop to drive feature activation");
  if (c.qbr_completion === "Overdue") plan.push("Schedule the overdue QBR with the economic buyer");
  if (c.expansion_pipeline_arr) plan.push(`Advance ${fmtK(c.expansion_pipeline_arr)} expansion opportunity`);
  const finalPlan = (plan.length ? plan : ["Maintain cadence; pursue reference and advocacy opportunities"]).slice(0, 4);

  const curStatus = action?.status || "Open";
  const statusMeta: Record<string, [string, string, string]> = {
    Open: ["#7A5C1E", "#FDF8EE", "Not yet actioned"],
    "In Progress": ["#2D4A7A", "#EEF2FB", "In progress"],
    Done: ["#2D5A3D", "#EFF6F1", "Closed — action taken"],
    Dismissed: ["#6B6280", "#F0EEEA", "Dismissed"],
  };
  const [sColor, sBg, sLabel] = statusMeta[curStatus] || statusMeta.Open;

  const setStatus = async (s: string) => {
    const updated = await postJSON(`/api/actions/${cid}`, { status: s });
    setAction(updated);
  };

  const runAgent = async () => {
    setRunning(true);
    try {
      const r = await postJSON<AgentResult>("/api/agents/run", { agent_name: agent, customer_id: cid });
      setResult(r);
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setRunning(false);
    }
  };

  const mrow = metrics[0] || {};
  const dauTrend = mrow.dau_trend_30d ?? 0;
  const usageItems: [string, string, string][] = [
    ["Daily Active Users", String(Math.round(mrow.dau ?? 0)), `${dauTrend >= 0 ? "+" : ""}${Math.round(dauTrend * 100)}% vs 30d`],
    ["AI Asset Coverage", `${Math.round(mrow.asset_coverage_pct ?? 0)}%`, ""],
    ["Modules Active", `${Math.round(mrow.features_enabled ?? 0)}/18`, ""],
    ["Guardian False-Positive Rate", `${Math.round((mrow.false_positive_rate ?? 0) * 100)}%`, ""],
    ["Prompts Inspected (30d)", Math.round(mrow.api_calls_last_30d ?? 0).toLocaleString(), ""],
    ["Guardian Interventions (30d)", String(Math.round(mrow.alerts_generated_last_30d ?? 0)), ""],
    ["Logins (7d)", String(Math.round(mrow.unique_logins_last_7d ?? 0)), ""],
    ["AI Agents Governed", String(Math.round(mrow.agents_deployed ?? 0)), ""],
  ];

  return (
    <div>
      {/* Hero */}
      <div className="text-[0.64rem] font-bold text-faint uppercase tracking-[0.14em]">Customer 360</div>
      <h1 className="text-[1.75rem] font-extrabold text-navy tracking-tight mb-3">{c.name}</h1>

      <div
        className="bg-white border border-line rounded-xl px-5 py-4 mb-4"
        style={{ borderLeft: `4px solid ${rc}` }}
      >
        <div className="flex items-start gap-5">
          <div className="flex-1 min-w-0">
            <div className="text-muted text-[0.8rem]">
              {c.industry} · {c.customer_tier} · {c.region} ·{" "}
              {(c.employee_count ?? 0).toLocaleString()} employees ·{" "}
              <span className="font-bold text-navy">{fmtUSD(c.arr)} ARR</span>
            </div>
            <div className="mt-[10px] px-3 py-2 bg-chip rounded-lg text-[0.78rem] text-ink leading-relaxed">
              <span className="font-bold text-navy">Risk:</span> {c.primary_risk_reason}
              <br />
              <span className="text-muted">→</span> {c.recommended_next_action}
            </div>
          </div>
          <div
            className="text-center rounded-[10px] px-4 py-3 shrink-0 min-w-[80px]"
            style={{ background: rb, border: `1px solid ${rc}33` }}
          >
            <div className="text-[2.4rem] font-black leading-none" style={{ color: rc }}>
              {c.health_score}
            </div>
            <div className="text-[0.58rem] font-bold text-muted tracking-[0.10em] mt-[2px]">HEALTH</div>
            <div className="text-[0.72rem] font-bold mt-1" style={{ color: rc }}>
              {c.risk_level}
            </div>
            <div className="text-[0.65rem] text-muted">{c.health_trend ?? ""}</div>
          </div>
        </div>
        <div className="flex gap-[10px] mt-3 flex-wrap">
          <StatChip label="Adoption" value={<>{c.adoption_score ?? 0}<span className="text-[0.65rem] font-medium text-muted">/100</span></>} />
          <StatChip label="Churn Risk" value={`${Math.round(rr * 100)}%`} valueColor={rc} />
          <StatChip label="Renewal" value={`${renewalDays}d`} />
          <StatChip label="Champion" value={c.champion_status ?? "?"} valueColor={champColor} />
          <StatChip
            label="NRR"
            value={`${c.nrr_pct ?? "?"}%`}
            valueColor={(c.nrr_pct ?? 0) >= 105 ? "#2D5A3D" : (c.nrr_pct ?? 0) >= 98 ? "#7A5C1E" : "#9B2335"}
          />
          <StatChip
            label="NPS"
            value={c.nps ?? "?"}
            valueColor={(c.nps ?? 0) >= 8 ? "#2D5A3D" : (c.nps ?? 0) >= 5 ? "#7A5C1E" : "#9B2335"}
          />
        </div>
      </div>

      <TabBar tabs={TABS} active={tab} onChange={setTab} />

      {tab === "Overview" && (
        <div>
          <div className="grid md:grid-cols-[1fr_1fr_1.4fr] gap-3">
            <Card>
              <SectionLabel>Renewal Prediction</SectionLabel>
              <div className="text-[1.6rem] font-black leading-tight" style={{ color: rconfColor }}>
                {renewConf}%
              </div>
              <div className="text-[0.74rem] font-bold" style={{ color: rconfColor }}>
                {rverdict}
              </div>
              <div className="text-[0.68rem] text-muted mt-1">
                {renewalDays}d to renewal · {c.forecast_category ?? renewal?.forecast_category ?? "—"}
              </div>
            </Card>
            <Card>
              <SectionLabel>Proven Business Outcome</SectionLabel>
              <div className="text-[0.92rem] font-bold text-green leading-snug mt-1">
                {c.roi_outcome ?? "—"}
              </div>
              <div className="text-[0.68rem] text-muted mt-[6px]">
                Utilization {c.utilization_pct ?? "?"}% · Exec engagement {c.executive_engagement ?? "?"}
              </div>
            </Card>
            <Card>
              <SectionLabel>Recommended Action Plan</SectionLabel>
              {finalPlan.map((step, i) => (
                <div key={i} className="text-[0.76rem] text-ink mt-[5px] leading-snug">
                  {i + 1}. {step}
                </div>
              ))}
            </Card>
          </div>

          <div className="grid md:grid-cols-[1.5fr_2.5fr] gap-3 mt-3">
            <div
              className="rounded-[10px] px-[14px] py-[10px]"
              style={{ background: sBg, border: `1px solid ${sColor}33` }}
            >
              <SectionLabel className="!mb-0">Recommendation Status</SectionLabel>
              <div className="text-[0.95rem] font-extrabold mt-[3px]" style={{ color: sColor }}>
                {sLabel}
              </div>
              <div className="text-[0.64rem] text-faint mt-[2px]">
                {action?.updated_at
                  ? `updated ${action.updated_at.slice(0, 16).replace("T", " ")}`
                  : "no action logged yet"}
              </div>
            </div>
            <div>
              <SectionLabel className="!mb-1">Log Outcome</SectionLabel>
              <div className="grid grid-cols-4 gap-2">
                {ACTION_STATUSES.map((s) => (
                  <button
                    key={s}
                    onClick={() => setStatus(s)}
                    className={`rounded-full text-[0.78rem] font-semibold py-[6px] px-3 transition-all ${
                      curStatus === s
                        ? "bg-navy text-white border-[1.5px] border-navy shadow"
                        : "bg-white text-navy border-[1.5px] border-[#D0CADE] hover:bg-[#F0ECE8]"
                    }`}
                  >
                    {s === "Dismissed" ? "Dismiss" : s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {tab === "AI Agents" && (
        <div>
          <div className="flex gap-3 items-center mb-1 flex-wrap">
            <select
              value={agent}
              onChange={(e) => setAgent(e.target.value)}
              className="bg-white border border-[#E0D8E8] rounded-xl px-3 py-2 text-[0.88rem] text-navy shadow-card outline-none min-w-[300px]"
            >
              {AGENT_MENU.map(([name, group, label]) => (
                <option key={name} value={name}>
                  {group} · {label}
                </option>
              ))}
            </select>
            <button
              onClick={runAgent}
              disabled={running}
              className="bg-navy text-white rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#2D1A5E] disabled:opacity-60 transition-colors"
            >
              {running ? "Running…" : "Run Agent"}
            </button>
          </div>
          {running ? <Spinner label={`Running ${agentDisplayName(agent)}…`} /> : null}
          {result && !running ? (
            <div className="mt-3">
              <div className="text-[0.78rem] font-extrabold text-navy mb-1">
                {agentDisplayName(result.agent_name || agent)}
              </div>
              <AgentReport result={result} />
            </div>
          ) : null}
          {!result && !running ? (
            <div className="text-muted text-[0.78rem] mt-3">
              Pick an agent above — results appear here and stay while you browse other tabs.
            </div>
          ) : null}
        </div>
      )}

      {tab === "Usage & Health" && (
        <div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
            {usageItems.map(([lbl, val, sub]) => (
              <div key={lbl} className="bg-white border border-line rounded-xl shadow-card px-[18px] py-4">
                <div className="text-[0.66rem] text-muted uppercase tracking-[0.10em] font-bold mb-[3px]">{lbl}</div>
                <div className="text-[1.3rem] font-extrabold text-navy leading-tight">{val}</div>
                {sub ? (
                  <div className={`text-[0.68rem] ${dauTrend >= 0 ? "text-green" : "text-red"}`}>{sub}</div>
                ) : null}
              </div>
            ))}
          </div>
          {history.length ? (
            <>
              <SectionLabel>30-Day Health Trend</SectionLabel>
              <HealthChart history={history} />
            </>
          ) : null}
        </div>
      )}

      {tab === "Implementation" && (
        <div>
          {impl ? (
            <Card className="mb-3">
              <div className="flex items-center justify-between mb-2">
                <Pill
                  color={
                    ["Stalled", "Behind Schedule"].includes(impl.overall_status)
                      ? "#9B2335"
                      : impl.overall_status === "Slight Delay"
                      ? "#C9952A"
                      : "#2D5A3D"
                  }
                  bg={
                    ["Stalled", "Behind Schedule"].includes(impl.overall_status)
                      ? "#FDF1F2"
                      : impl.overall_status === "Slight Delay"
                      ? "#FDF8EE"
                      : "#EFF6F1"
                  }
                  bordered
                >
                  {impl.overall_status}
                </Pill>
                <span className="text-[0.72rem] text-muted">{impl.pct_complete}% complete</span>
              </div>
              <ProgressBar pct={impl.pct_complete} />
              <div className="flex gap-4 mt-2 text-[0.72rem] text-muted flex-wrap">
                <span>
                  Owner: <b className="text-navy">{impl.implementation_owner}</b>
                </span>
                <span>
                  Go-live: <b className="text-navy">{impl.go_live_target}</b>
                </span>
                {impl.days_behind_schedule > 0 ? (
                  <span className="text-red font-semibold">{impl.days_behind_schedule}d behind schedule</span>
                ) : null}
              </div>
            </Card>
          ) : (
            <div className="text-muted text-[0.78rem]">No implementation record found.</div>
          )}
          {milestones.map((m, i) => (
            <div key={i} className="flex items-start gap-[10px] py-2 border-b border-line">
              <Pill
                color={{ Complete: "#2D5A3D", "In Progress": "#7A5C1E" }[m.status as string] || "#6B6280"}
                bg={{ Complete: "#EFF6F1", "In Progress": "#FDF8EE" }[m.status as string] || "#F5F2EE"}
              >
                {m.status}
              </Pill>
              <div>
                <div className="text-[0.82rem] font-semibold text-navy">
                  {m.milestone_name || m.name || "?"}
                </div>
                {m.blocker ? <div className="text-[0.72rem] text-red mt-[2px]">{m.blocker}</div> : null}
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "Support" && (
        <div className="grid lg:grid-cols-2 gap-5">
          <div>
            <SectionLabel>Support Tickets</SectionLabel>
            <div className="text-[0.78rem] font-bold text-navy mb-2">
              {openTickets} Open <span className="text-muted font-normal">· {tickets.length - openTickets} Resolved</span>
            </div>
            {tickets.map((t, i) => {
              const sc = { P1: "#9B2335", P2: "#7A5C1E", P3: "#5C4A1E", P4: "#6B6280" }[t.severity as string] || "#6B6280";
              const stc = { Open: "#9B2335", "In Progress": "#7A5C1E" }[t.status as string] || "#2D5A3D";
              return (
                <Card key={i} className="mb-2">
                  <div className="flex justify-between items-center">
                    <Pill color={sc} bg={`${sc}18`} bordered>{t.severity}</Pill>
                    <span className="text-[0.72rem] font-bold" style={{ color: stc }}>{t.status}</span>
                  </div>
                  <div className="text-navy text-[0.88rem] mt-[6px] font-medium">{t.title}</div>
                  <div className="text-muted text-[0.72rem] mt-[3px]">
                    Opened {(t.opened_at || "").slice(0, 10)} · Assignee: {t.assignee ?? "?"}
                  </div>
                </Card>
              );
            })}
          </div>
          <div>
            <SectionLabel>Escalations</SectionLabel>
            {!escs.length ? <div className="text-green text-[0.78rem]">No active escalations.</div> : null}
            {escs.map((e, i) => {
              const crit = e.severity === "Critical";
              const sc = crit ? "#9B2335" : "#7A5C1E";
              return (
                <Card key={i} className="mb-2" accent={sc}>
                  <div className="flex items-center justify-between">
                    <div className="flex gap-[5px] items-center flex-wrap">
                      <Pill color={sc} bg={crit ? "#FDF1F2" : "#FDF8EE"} bordered>{e.severity}</Pill>
                      <Pill color="#6B6280" bg="#F5F2EE">{e.status}</Pill>
                      {e.executive_aware ? <Pill color="#3D3458" bg="#EAE6E0">Exec Aware</Pill> : null}
                    </div>
                    <span className="text-[0.68rem] text-faint">{(e.opened_at || "").slice(0, 10)}</span>
                  </div>
                  <div className="text-[0.85rem] font-semibold text-navy mt-[7px]">{e.title}</div>
                  <div className="text-[0.72rem] text-muted mt-[3px]">Owner: {e.owner}</div>
                  {e.resolution_plan ? (
                    <div className="text-[0.72rem] text-muted mt-1 italic">{e.resolution_plan}</div>
                  ) : null}
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {tab === "People" && (
        <div className="grid lg:grid-cols-2 gap-5">
          <div>
            <SectionLabel>Stakeholders</SectionLabel>
            {stk.map((s, i) => {
              const ec = { High: "#2D5A3D", Medium: "#7A5C1E", Low: "#9B2335" }[s.engagement_level as string] || "#6B6280";
              return (
                <Card key={i} className="mb-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-bold text-navy text-[0.95rem]">{s.name}</span>
                      <div className="text-[0.80rem] text-muted mt-[1px]">{s.title}</div>
                    </div>
                    <span className="text-[0.72rem] font-bold" style={{ color: ec }}>
                      {s.engagement_level ?? "?"} engagement
                    </span>
                  </div>
                  <div className="mt-[6px] flex items-center gap-2">
                    <Pill color="#1B1040" bg="#EAE6E0">{s.role}</Pill>
                    <span className="text-muted text-[0.72rem]">{s.email}</span>
                  </div>
                </Card>
              );
            })}
          </div>
          <div>
            <SectionLabel>Meeting Notes</SectionLabel>
            {notes.map((n, i) => {
              const sc = { Positive: "#2D5A3D", Negative: "#9B2335" }[n.sentiment_signal as string] || "#6B6280";
              const sb = { Positive: "#EBF2EE", Negative: "#F5ECEC" }[n.sentiment_signal as string] || "#EFEBE5";
              let actions: string[] = [];
              try {
                actions = n.action_items ? JSON.parse(n.action_items) : [];
              } catch {}
              return (
                <Card key={i} className="mb-2">
                  <div className="flex justify-between items-center">
                    <span className="text-muted text-[0.75rem]">
                      {(n.date || "").slice(0, 10)} · <b className="text-ink">{n.meeting_type ?? "?"}</b>
                    </span>
                    <Pill color={sc} bg={sb}>{n.sentiment_signal ?? "?"}</Pill>
                  </div>
                  <div className="text-navy text-[0.88rem] mt-[6px] leading-relaxed">{n.summary}</div>
                  {actions.length ? (
                    <div className="mt-[6px]">
                      {actions.map((a, j) => (
                        <div key={j} className="text-[0.75rem] text-ink mt-[2px]">→ {a}</div>
                      ))}
                    </div>
                  ) : null}
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {tab === "Renewal" && (
        <div>
          {renewal ? (
            <>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-3">
                <Card>
                  <SectionLabel className="!mb-0">Days to Renewal</SectionLabel>
                  <div className="text-[1.3rem] font-extrabold text-navy">{renewal.days_to_renewal ?? "?"}</div>
                </Card>
                <Card>
                  <SectionLabel className="!mb-0">Renewal Stage</SectionLabel>
                  <div className="text-[1.1rem] font-extrabold text-navy">{renewal.renewal_stage ?? "?"}</div>
                </Card>
                <Card>
                  <SectionLabel className="!mb-0">Current ARR</SectionLabel>
                  <div className="text-[1.3rem] font-extrabold text-navy">{fmtUSD(renewal.current_arr ?? 0)}</div>
                </Card>
                <Card>
                  <SectionLabel className="!mb-0">Expansion Opp.</SectionLabel>
                  <div className="text-[1.3rem] font-extrabold text-navy">{fmtUSD(renewal.expansion_arr ?? 0)}</div>
                </Card>
              </div>
              <Card>
                <SectionLabel>Renewal Details</SectionLabel>
                <div className="text-[0.85rem]">
                  Forecast: <b style={{ color: rconfColor }}>{renewal.forecast_category ?? "?"}</b>
                </div>
                <div className="text-[0.85rem] mt-1">
                  Risk Score: <b style={{ color: rconfColor }}>{Math.round(rr * 100)}%</b>
                </div>
                <div className="text-[0.85rem] mt-1">Commercial Note: {renewal.commercial_terms_note ?? "?"}</div>
                <div className="text-[0.85rem] mt-1 text-muted">
                  Procurement Contact: {renewal.procurement_contact ?? "?"}
                </div>
                <div className="text-[0.85rem] text-muted">
                  Exec Involvement Required: {renewal.requires_exec_involvement ? "Yes" : "No"}
                </div>
              </Card>
            </>
          ) : (
            <div className="text-muted text-[0.78rem]">No renewal record found within 180-day window.</div>
          )}
        </div>
      )}
    </div>
  );
}
