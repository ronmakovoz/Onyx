import { PageHeader, SectionTitle } from "../components/UI";
import { platformCapabilities, solutionProducts } from "../lib/data";

const sources = ["Okta", "Entra ID", "Workday", "Active Directory", "AWS", "Salesforce", "Snowflake", "Custom apps"];
const identityTypes = ["Humans", "Service accounts", "API keys & bots", "AI agents", "Accounts", "Roles & entitlements", "Applications", "Resources"];
const protocolRoles = [
  { name: "OAuth 2.0", role: "Authorize the connector", signal: "SCOPED API ACCESS", description: "A scoped access token lets a Linx connector read identity and entitlement APIs and, when approved, execute remediation. OAuth delegates API access; it does not provision users by itself.", color: "#5aa7ff" },
  { name: "SCIM 2.0", role: "Provision the lifecycle", signal: "USERS + GROUPS", description: "SCIM standardizes user and group creation, updates, and deactivation. Linx can correlate that lifecycle state and use SCIM or the target API for fulfillment where the connected system supports it.", color: "#48c7a7" },
  { name: "SAML 2.0", role: "Federate authentication", signal: "SSO CONTEXT", description: "SAML carries authentication and federation assertions. IdP configuration and app-assignment signals give Linx context for SSO coverage, authentication strength, and possible bypass—not provisioning.", color: "#ff9f43" },
] as const;

const integrationSteps = [
  ["01", "Lifecycle event", "Workday records Alex Rivera's move from Support to Finance, including the effective date, manager, department, and employment status."],
  ["02", "Agentless collection", "OAuth-authorized and connector-specific APIs pull the HR change, Okta groups, SAML app assignments, Salesforce permission sets, AWS roles, and OAuth clients."],
  ["03", "Graph reconciliation", "Linx resolves one person across multiple accounts, then maps groups, roles, entitlements, applications, resources, authentication controls, and inherited access paths."],
  ["04", "Contextual decision", "Identity Intelligence finds an old Support admin path, a missing Finance entitlement, and an OAuth application whose scope is broader than its owner and purpose justify."],
  ["05", "Closed-loop action", "Policy removes obsolete access, provisions the approved Finance baseline through SCIM or an application API, escalates the OAuth risk, and records every decision for audit."],
] as const;

export default function IntegrationPage() {
  return (
    <div>
      <PageHeader title="How Linx Connects" subtitle="A protocol-aware integration from enterprise sources to Identity Graph context and closed-loop action" />

      <section className="product-map-intro card">
        <div><span>THE SIMPLE VERSION</span><h2>Connect → map → understand → decide → act → operate</h2></div>
        <p>Linx uses flexible, agentless connectors to collect identity and entitlement data, normalize it into one context layer, and apply that context to governance, posture, privileged access, lifecycle, non-human identities, and AI-agent actions.</p>
      </section>

      <SectionTitle meta="illustrative enterprise deployment · protocol roles are connector-specific">Actual integration walkthrough</SectionTitle>
      <section className="integration-example card">
        <header>
          <div><span>REFERENCE FLOW</span><h2>Workday → Okta → Salesforce &amp; AWS</h2><p>A mover event shows how Linx combines source-of-truth data, identity-provider context, application access, and fulfillment.</p></div>
          <a href="https://www.linx.security/platform/integrations" target="_blank" rel="noreferrer">View Linx integrations →</a>
        </header>

        <div className="integration-estate" aria-label="Illustrative Linx connected estate">
          <article><span>AUTHORITATIVE SOURCE</span><strong>Workday</strong><p>Worker · manager · department · status</p></article>
          <i>+</i>
          <article><span>IDENTITY PLANE</span><strong>Okta / Entra ID</strong><p>Accounts · groups · SAML apps · MFA</p></article>
          <i>+</i>
          <article><span>RESOURCE PLANE</span><strong>Salesforce / AWS</strong><p>Roles · permission sets · OAuth apps</p></article>
          <b>→</b>
          <article className="linx-node"><span>LINX</span><strong>Agentless connectors</strong><p>Collect · normalize · correlate · act</p></article>
          <b>→</b>
          <article className="graph-node"><span>SHARED CONTEXT</span><strong>Identity Graph</strong><p>Identity → account → access → resource</p></article>
        </div>

        <div className="protocol-explainer">
          {protocolRoles.map((protocol) => (
            <article key={protocol.name} style={{ borderTopColor: protocol.color }}>
              <div><strong>{protocol.name}</strong><span>{protocol.signal}</span></div>
              <h3>{protocol.role}</h3><p>{protocol.description}</p>
            </article>
          ))}
        </div>
        <p className="protocol-note"><strong>Important:</strong> SAML, SCIM, and OAuth solve different parts of the integration. Linx correlates their signals with app APIs, directories, webhooks, and files; the exact read and write path depends on each connector.</p>

        <div className="integration-timeline">
          {integrationSteps.map(([number, title, description]) => (
            <article key={number}><span>{number}</span><div><h3>{title}</h3><p>{description}</p></div></article>
          ))}
        </div>
        <footer><strong>Result</strong><span>One current identity model</span><span>Least-privilege decision</span><span>Provisioning or remediation</span><span>Auditable evidence</span></footer>
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
      <p className="source-note">Platform mapping reflects current public Linx product positioning. The integration is illustrative; protocol use and write-back behavior depend on each connected system. Dashboard metrics and customer records are synthetic.</p>
    </div>
  );
}
