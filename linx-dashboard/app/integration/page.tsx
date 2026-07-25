import { PageHeader } from "../components/UI";

const events = [
  {
    number: "01",
    owner: "Customer",
    system: "Approve & connect",
    title: "Start read-only",
    description: "Connect the IdP, HR source, and priority apps with least-privilege read access. Cloud connectors need no inbound firewall rule or installed agent.",
  },
  {
    number: "02",
    owner: "Linx",
    system: "Discover & correlate",
    title: "Build the identity graph",
    description: "Linx calls vendor APIs over scoped OAuth, then correlates identities, accounts, groups, entitlements, and activity across connected systems.",
  },
  {
    number: "03",
    owner: "Linx",
    system: "Evaluate & approve",
    title: "Turn context into a decision",
    description: "Policy evaluates risk and determines whether an action can run inside guardrails or needs human approval from the responsible owner.",
  },
  {
    number: "04",
    owner: "Linx → Customer",
    system: "Remediate & verify",
    title: "Close the loop",
    description: "With separate write approval, Linx uses vendor APIs or SCIM to suspend, revoke, or change access—then re-reads the target and logs the result.",
  },
] as const;

const protocols = [
  { name: "SAML / OIDC", direction: "Customer IdP → Linx", role: "Authenticates Linx administrators.", accent: "#ff9f43" },
  { name: "OAuth + REST", direction: "Linx → connected systems", role: "Discovers identities, access, and activity.", accent: "#5aa7ff" },
  { name: "REST / SCIM", direction: "Linx → connected systems", role: "Executes approved access changes.", accent: "#48c7a7" },
] as const;

export default function IntegrationPage() {
  return (
    <div className="simple-connection-page">
      <PageHeader title="How Linx Connects" subtitle="An agentless, API-based path from discovery to verified action" />

      <section className="connection-hero card">
        <header>
          <span>THE RELATIONSHIP</span>
          <h2>Your systems remain the source of truth. Linx connects, maps access, and acts within your guardrails.</h2>
        </header>
        <div className="connection-parties">
          <article className="customer-party">
            <span>CUSTOMER ENVIRONMENT</span>
            <h3>Identity, HR, apps &amp; cloud</h3>
            <p>Okta / Entra / Google · Workday · SaaS · AWS / Azure</p>
          </article>
          <div className="connection-lanes" aria-label="Data flow between customer and Linx">
            <div><i>←</i><span>CONNECT</span><strong>Linx initiates scoped HTTPS/API calls</strong></div>
            <div><span>DISCOVER</span><strong>Identity and access data</strong><i>→</i></div>
            <div><i>←</i><span>REMEDIATE</span><strong>Approved REST or SCIM changes</strong></div>
          </div>
          <article className="linx-party">
            <span>LINX TENANT</span>
            <h3>Connect, map, decide &amp; act</h3>
            <p>Connector runtime · Identity graph · Policy engine</p>
          </article>
        </div>
      </section>

      <section className="event-story card">
        <header>
          <div><span>THE FLOW</span><h2>Four steps from connection to outcome</h2></div>
          <p>Begin with read-only discovery. Add write permissions only when the customer is ready for remediation.</p>
        </header>
        <div className="event-sequence">
          {events.map((event) => (
            <article key={event.number}>
              <div className="event-number">{event.number}</div>
              <div className="event-owner"><span>{event.owner}</span><strong>{event.system}</strong></div>
              <div className="event-copy"><h3>{event.title}</h3><p>{event.description}</p></div>
            </article>
          ))}
        </div>
        <footer>
          <span>OUTCOME</span>
          <strong>Continuous visibility</strong>
          <i>•</i><strong>Policy-gated action</strong>
          <i>•</i><strong>Verified audit trail</strong>
        </footer>
      </section>

      <section className="protocol-strip" aria-label="Protocol roles">
        {protocols.map((protocol) => (
          <article className="card" key={protocol.name} style={{ borderTopColor: protocol.accent }}>
            <strong>{protocol.name}</strong><span>{protocol.direction}</span><p>{protocol.role}</p>
          </article>
        ))}
      </section>

      <div className="connection-note">
        <p><strong>Direction matters:</strong> OAuth-backed APIs are the primary discovery path. SCIM provisions users and groups; it does not replace discovery. Write access is a separate consent step.</p>
        <div className="connection-actions">
          <a className="guide-link" href="/linx-security-integration-guide.html" target="_blank" rel="noreferrer">Open technical guide ↗</a>
          <a href="https://www.linx.security/platform/integrations" target="_blank" rel="noreferrer">Linx integrations ↗</a>
        </div>
      </div>
      <p className="source-note">Exact permissions, sync methods, and write paths vary by connected system. On-premises targets may require an additional connectivity pattern.</p>
    </div>
  );
}
