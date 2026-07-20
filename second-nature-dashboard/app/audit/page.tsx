import { auditRuns } from "../lib/data";
import { Kpi, PageHeader, SectionTitle } from "../components/UI";

export default function AuditPage() {
  const tokens = auditRuns.reduce((sum, run) => sum + run.tokens, 0);
  const cost = auditRuns.reduce((sum, run) => sum + run.cost, 0);
  return (
    <div>
      <PageHeader title="AI Audit & Costs" subtitle="Every agent run, model decision, token, cost, and confidence score" />
      <section className="kpi-grid four"><Kpi label="Agent runs" value="1,084" detail="all-time demo audit" tone="blue" /><Kpi label="Runs this month" value="146" detail="82% Sonnet-routed" tone="green" /><Kpi label="Tokens sampled" value={tokens.toLocaleString()} detail="latest five runs" tone="purple" /><Kpi label="Sampled cost" value={`$${cost.toFixed(3)}`} detail="transparent model spend" tone="yellow" /></section>

      <div className="audit-grid">
        <section><SectionTitle>Model routing</SectionTitle><div className="card routing-card"><div><span><i style={{ background: "#6c4df6" }} />Sonnet</span><b>82%</b><small>Complex account analysis and briefings</small></div><div><span><i style={{ background: "#161616" }} />Opus</span><b>12%</b><small>Portfolio synthesis and Skeptik QA</small></div><div><span><i style={{ background: "#00a98f" }} />Haiku</span><b>6%</b><small>Fast portfolio and next-action drafts</small></div></div></section>
        <section><SectionTitle>Governance controls</SectionTitle><div className="card controls-card"><div><span>✓</span><p><strong>Account-scoped context</strong>Agents receive only the selected customer record.</p></div><div><span>✓</span><p><strong>Full run trace</strong>Model, tokens, cost, confidence, and output are logged.</p></div><div><span>✓</span><p><strong>Synthetic demo data</strong>No production property-manager or resident records are present.</p></div></div></section>
      </div>

      <SectionTitle meta="latest five runs">Run history</SectionTitle>
      <section className="card audit-table">
        <div className="audit-head"><span>Run</span><span>Agent / account</span><span>Model</span><span>Tokens</span><span>Confidence</span><span>Cost</span><span>Time</span></div>
        {auditRuns.map((run) => <div className="audit-row" key={run.id}><span>#{run.id}</span><span><strong>{run.agent}</strong><small>{run.account}</small></span><span><code>{run.model}</code></span><span>{run.tokens.toLocaleString()}</span><span><b>{run.confidence}%</b></span><span>${run.cost.toFixed(4)}</span><span>{run.time}</span></div>)}
      </section>
    </div>
  );
}
