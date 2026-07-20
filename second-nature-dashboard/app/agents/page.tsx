"use client";

import { useState } from "react";
import { accounts, agents } from "../lib/data";
import { PageHeader, SectionTitle } from "../components/UI";
import ReportDocument from "../components/ReportDocument";

export default function AgentsPage() {
  const [agentId, setAgentId] = useState(agents[0].id);
  const [accountId, setAccountId] = useState(1);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState("");
  const [meta, setMeta] = useState<{ model?: string; confidence?: number; live?: boolean }>({});
  const agent = agents.find((item) => item.id === agentId) ?? agents[0];
  const portfolioAgent = agent.id === "VPChiefOfStaff";

  async function run() {
    setBusy(true); setResult("");
    try {
      const response = await fetch("/api/agent", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ agentId, accountId: portfolioAgent ? null : accountId }) });
      const data = await response.json() as { report?: string; model?: string; confidence?: number; live?: boolean; error?: string };
      if (!response.ok) throw new Error(data.error || "Agent run failed");
      setResult(data.report || ""); setMeta(data);
    } catch (error) { setResult(`Agent error: ${error instanceof Error ? error.message : String(error)}`); }
    finally { setBusy(false); }
  }

  return (
    <div>
      <PageHeader title="Agent Studio" subtitle="Run Second Nature resident-experience agents and inspect their account context" />
      <div className="agent-layout">
        <section>
          <SectionTitle>Configure</SectionTitle>
          <div className="card agent-controls">
            <label><span>Agent</span><select value={agentId} onChange={(event) => { setAgentId(event.target.value); setResult(""); }}>{agents.map((item) => <option key={item.id} value={item.id}>{item.group} · {item.name}</option>)}</select></label>
            {!portfolioAgent && <label><span>Account context</span><select value={accountId} onChange={(event) => setAccountId(Number(event.target.value))}>{accounts.map((account) => <option key={account.id} value={account.id}>{account.name} · health {account.health}</option>)}</select></label>}
            <div className="agent-card"><span>{agent.group} WORKFLOW</span><h2>{agent.name}</h2><p>{agent.description}</p><div><b>Routed to {agent.tier}</b><small>Context: {portfolioAgent ? "portfolio-wide" : "account 360"}</small></div></div>
            <button className="primary-button" onClick={run} disabled={busy}>{busy ? "Running agent…" : `Run ${agent.name}`}</button>
          </div>
        </section>
        <section>
          <SectionTitle meta={meta.model ? `${meta.live ? "LIVE" : "DEMO"} · ${meta.model} · ${meta.confidence}% confidence` : undefined}>Agent output</SectionTitle>
          <div className={`card report agent-output ${busy ? "loading" : ""}`}>{busy ? <div className="report-placeholder"><i /><strong>Running {agent.name}…</strong><p>Grounding recommendations in resident, property, operational, and commercial context.</p></div> : result ? <ReportDocument content={result} /> : <div className="empty-report"><span>✦</span><strong>Configure an agent and click Run</strong><p>Recommendations, model choice, and confidence will appear here.</p></div>}</div>
        </section>
      </div>
    </div>
  );
}
