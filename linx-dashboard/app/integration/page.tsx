import { PageHeader, SectionTitle } from "../components/UI";

const sources = ["Okta", "Entra ID", "Workday", "Active Directory", "AWS", "Salesforce", "Snowflake", "Custom apps"];
const graph = ["Normalize identities", "Map entitlements", "Correlate access paths", "Score context & risk"];
const outcomes = [
  ["Modern IGA", "Risk-centric certifications and access governance", "#f2c94c"],
  ["ISPM", "Continuous posture, attack paths, and remediation", "#ff7d5f"],
  ["JIT Access", "Time-bound privilege with automatic revocation", "#48c7a7"],
  ["Lifecycle", "Joiner, mover, and leaver automation", "#5aa7ff"],
  ["NHI Governance", "Owners and least privilege for service identities", "#b89cff"],
  ["AI Access Control", "MCP tool-call enforcement and audit trails", "#ff9f43"],
] as const;

export default function IntegrationPage() {
  return (
    <div>
      <PageHeader title="How Linx Connects" subtitle="Agentless identity data ingestion, one normalized graph, and action across the whole identity lifecycle" />
      <section className="card architecture">
        <div className="architecture-column sources"><span>01 · CONNECT</span><h2>Identity data sources</h2><p>Agentlessly pull from every app, directory, cloud, and system.</p><div>{sources.map((source) => <b key={source}>{source}</b>)}</div></div>
        <div className="flow-arrow"><span>DATA</span><i>→</i></div>
        <div className="architecture-column graph"><span>02 · UNDERSTAND</span><h2>Linx Identity Graph</h2><p>A continuously current source of truth for identity and access.</p><div>{graph.map((item, index) => <b key={item}><i>{index + 1}</i>{item}</b>)}</div><em>AI analytics · Copilot · Autopilot</em></div>
        <div className="flow-arrow"><span>ACTION</span><i>→</i></div>
        <div className="architecture-column outcomes"><span>03 · GOVERN &amp; ACT</span><h2>Identity outcomes</h2><p>Find risk, make the decision, and close the loop in one platform.</p><div>{outcomes.map(([name, description, color]) => <article key={name} style={{ borderLeftColor: color }}><strong>{name}</strong><small>{description}</small></article>)}</div></div>
      </section>

      <SectionTitle meta="the operating model">Four steps to value</SectionTitle>
      <section className="steps-grid"><article><span>01</span><h3>Connect everything</h3><p>Ingest cloud, SaaS, on-prem, and custom identity data without replacing the existing IAM stack.</p></article><article><span>02</span><h3>See every relationship</h3><p>Model human, non-human, and agentic identities down to the entitlement and resource level.</p></article><article><span>03</span><h3>Decide with context</h3><p>Use risk, behavior, ownership, and business context to prioritize the decisions that matter.</p></article><article><span>04</span><h3>Act and prove it</h3><p>Remediate in-platform, automate lifecycle changes, and keep an audit trail of every action.</p></article></section>
      <p className="source-note">Platform mapping reflects current public Linx product positioning. Dashboard metrics and customer records are synthetic.</p>
    </div>
  );
}
