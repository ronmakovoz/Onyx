"use client";

import { useState } from "react";
import { accounts } from "../lib/data";
import { PageHeader, SectionTitle } from "../components/UI";

export default function BriefingsPage() {
  const [tab, setTab] = useState<"account" | "vp">("account");
  const [accountId, setAccountId] = useState(1);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState("");
  const [model, setModel] = useState("");

  async function generate() {
    setBusy(true); setResult("");
    try {
      const response = await fetch("/api/agent", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ agentId: tab === "account" ? "ExecutiveBriefing" : "VPChiefOfStaff", accountId: tab === "account" ? accountId : null }) });
      const data = await response.json() as { report?: string; model?: string; error?: string };
      if (!response.ok) throw new Error(data.error || "Briefing generation failed");
      setResult(data.report || ""); setModel(data.model || "Demo model");
    } catch (error) { setResult(`Unable to generate the briefing: ${error instanceof Error ? error.message : String(error)}`); }
    finally { setBusy(false); }
  }

  return (
    <div>
      <PageHeader title="Executive Briefings" subtitle="Enablement-leader account narratives and a weekly VP Customer Success review" />
      <div className="tabbar"><button className={tab === "account" ? "active" : ""} onClick={() => { setTab("account"); setResult(""); }}>Account Briefing</button><button className={tab === "vp" ? "active" : ""} onClick={() => { setTab("vp"); setResult(""); }}>VP Weekly Review</button></div>

      <section className="briefing-layout">
        <div>
          <SectionTitle>Configure briefing</SectionTitle>
          <div className="card briefing-controls">
            {tab === "account" ? <label><span>Customer account</span><select value={accountId} onChange={(event) => setAccountId(Number(event.target.value))}>{accounts.map((account) => <option key={account.id} value={account.id}>{account.name} · {account.risk} risk</option>)}</select></label> : <div className="portfolio-scope"><span>PORTFOLIO SCOPE</span><strong>10 accounts · $9.5M ARR</strong><p>Renewals, readiness-program health, rollout risk, expansion, and team priorities.</p></div>}
            <button className="primary-button" onClick={generate} disabled={busy}>{busy ? "Generating…" : tab === "account" ? "Generate Enablement Briefing" : "Generate VP Weekly Review"}</button>
            <p className="control-note">Uses Anthropic when configured; otherwise produces a deterministic demo briefing.</p>
          </div>
        </div>
        <div>
          <SectionTitle meta={model || undefined}>Generated document</SectionTitle>
          <div className={`card report ${busy ? "loading" : ""}`}>{busy ? <div className="report-placeholder"><i /><strong>Analyzing portfolio context…</strong><p>Connecting health, adoption, outcomes, and commercial signals.</p></div> : result ? <pre>{result}</pre> : <div className="empty-report"><span>✦</span><strong>Ready to generate</strong><p>Your executive-grade document will appear here.</p></div>}</div>
        </div>
      </section>
    </div>
  );
}
