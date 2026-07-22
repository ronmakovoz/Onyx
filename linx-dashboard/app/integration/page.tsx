import { PageHeader, SectionTitle } from "../components/UI";
import { platformCapabilities, solutionProducts } from "../lib/data";

const sources = ["Okta", "Entra ID", "Workday", "Active Directory", "AWS", "Salesforce", "Snowflake", "Custom apps"];
const identityTypes = ["Humans", "Service accounts", "API keys & bots", "AI agents", "Accounts", "Roles & entitlements", "Applications", "Resources"];

export default function IntegrationPage() {
  return (
    <div>
      <PageHeader title="Linx Product Map" subtitle="The shared platform foundation, six identity-security solutions, and two distinct controls for AI agents" />

      <section className="product-map-intro card">
        <div><span>THE SIMPLE VERSION</span><h2>Connect → map → understand → decide → act → operate</h2></div>
        <p>Linx is not a collection of disconnected identity tools. The platform creates one context layer, then applies it to governance, posture, privileged access, lifecycle, non-human identities, and AI-agent actions.</p>
      </section>

      <SectionTitle meta="shared by every solution">Platform foundation</SectionTitle>
      <section className="foundation-map">
        {platformCapabilities.map((capability, index) => (
          <article key={capability.id} className="card">
            <div><span>{String(index + 1).padStart(2, "0")}</span><b>{capability.stage}</b></div>
            <h3>{capability.name}</h3>
            <p>{capability.description}</p>
          </article>
        ))}
      </section>

      <div className="product-map-core card">
        <section>
          <span>INPUTS</span><h2>Identity data sources</h2><p>Agentless connections bring existing systems into Linx without replacing the IAM stack.</p>
          <div className="source-cloud">{sources.map((source) => <b key={source}>{source}</b>)}</div>
        </section>
        <i>→</i>
        <section>
          <span>CONTEXT LAYER</span><h2>Identity Graph</h2><p>Correlates access relationships and exposes direct, inherited, and hidden privilege paths.</p>
          <div className="identity-cloud">{identityTypes.map((identity) => <b key={identity}>{identity}</b>)}</div>
        </section>
        <i>→</i>
        <section>
          <span>DECISION &amp; ACTION</span><h2>Intelligence that closes the loop</h2><p>Risk, peer, usage, behavior, ownership, and semantic context drive recommendations, governed actions, and continuous operation.</p>
          <div className="action-stack"><b>Identity Intelligence</b><b>AI Copilot</b><b>Automation &amp; Remediation</b><b>Autopilot</b></div>
        </section>
      </div>

      <SectionTitle meta="customer-facing use cases powered by the same foundation">Solution modules</SectionTitle>
      <section className="solution-catalog">
        {solutionProducts.map((solution) => (
          <article className="card" key={solution.id} style={{ borderTopColor: solution.accent }}>
            <span>{solution.short}</span><h3>{solution.name}</h3><p>{solution.description}</p><strong>{solution.outcome}</strong>
          </article>
        ))}
      </section>

      <SectionTitle meta="related products · different control points">AI identities: two layers of control</SectionTitle>
      <section className="ai-control-grid">
        <article className="card governance-layer">
          <span>GOVERN THE IDENTITY</span><h2>Agentic Identity Governance</h2><p>Discovers AI agents, identifies their owners and users, maps downstream access, and brings lifecycle, least privilege, reviews, and audit into the same governance model as every other identity.</p>
          <div><b>Question answered</b><strong>What is this agent, who owns it, and what access should it have?</strong></div>
          <a href="https://www.linx.security/solutions/agentic-identity-governance" target="_blank" rel="noreferrer">View Linx solution →</a>
        </article>
        <article className="card enforcement-layer">
          <span>CONTROL THE ACTION</span><h2>AI Access Control</h2><p>The MCP Gateway sits inline between AI platforms and enterprise tools, evaluates individual tool calls before execution, applies the same policies across identities, and records the full attribution chain.</p>
          <div><b>Question answered</b><strong>Should this specific agent tool call be allowed right now?</strong></div>
          <a href="https://www.linx.security/platform/mcp-gateway" target="_blank" rel="noreferrer">View Linx MCP Gateway →</a>
        </article>
      </section>

      <SectionTitle meta="the operating model">Four steps to measurable value</SectionTitle>
      <section className="steps-grid"><article><span>01</span><h3>Connect the estate</h3><p>Ingest cloud, SaaS, on-prem, and custom identity data without replacing existing IAM investments.</p></article><article><span>02</span><h3>Build trusted context</h3><p>Model every identity, entitlement, resource, access path, owner, and usage signal in the Identity Graph.</p></article><article><span>03</span><h3>Activate a solution</h3><p>Apply that context to the highest-value workflow: governance, posture, JIT, lifecycle, agentic identity, or AI action control.</p></article><article><span>04</span><h3>Automate and prove</h3><p>Close findings in-platform, automate policy-aligned decisions, escalate ambiguity, and retain evidence of every action.</p></article></section>
      <p className="source-note">Platform mapping reflects current public Linx product positioning. Dashboard metrics and customer records are synthetic.</p>
    </div>
  );
}
