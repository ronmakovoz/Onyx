import { PageHeader } from "../components/UI";

const events = [
  {
    number: "01",
    owner: "Customer",
    system: "Workday",
    title: "A role changes",
    description: "Alex Rivera moves from Support to Finance. Workday records the effective date, manager, department, and employment status.",
  },
  {
    number: "02",
    owner: "Customer → Linx",
    system: "OAuth + APIs",
    title: "Linx reads the new state",
    description: "Scoped connectors collect the HR change, Okta groups, SAML app assignments, Salesforce permissions, and AWS roles—without replacing the customer's IAM stack.",
  },
  {
    number: "03",
    owner: "Linx",
    system: "Identity Graph",
    title: "Linx rebuilds the access picture",
    description: "The Graph resolves Alex across accounts and maps the complete path from identity to group, role, entitlement, application, and resource.",
  },
  {
    number: "04",
    owner: "Linx",
    system: "Policy + intelligence",
    title: "Linx makes the decision clear",
    description: "Linx identifies an obsolete Support admin path and the missing Finance baseline, then determines what to remove, add, approve, or escalate.",
  },
  {
    number: "05",
    owner: "Linx → Customer",
    system: "SCIM / app API",
    title: "Linx closes the loop",
    description: "Approved changes are written back through SCIM or the application's API. Old access is removed, new access is provisioned, and every decision is retained for audit.",
  },
] as const;

const protocols = [
  { name: "OAuth 2.0", role: "Authorizes scoped API access for the Linx connector.", accent: "#5aa7ff" },
  { name: "SAML 2.0", role: "Provides SSO and authentication context—not provisioning.", accent: "#ff9f43" },
  { name: "SCIM 2.0", role: "Standardizes user and group provisioning and deprovisioning.", accent: "#48c7a7" },
] as const;

export default function IntegrationPage() {
  return (
    <div className="simple-connection-page">
      <PageHeader title="How Linx Connects" subtitle="One customer change moves through five clear events—from source to governed outcome" />

      <section className="connection-hero card">
        <header>
          <span>THE RELATIONSHIP</span>
          <h2>Customer systems provide the facts. Linx turns them into a decision and closes the loop.</h2>
        </header>
        <div className="connection-parties">
          <article className="customer-party">
            <span>CUSTOMER ENVIRONMENT</span>
            <h3>Systems of record &amp; access</h3>
            <p>Workday · Okta / Entra ID · Salesforce · AWS</p>
          </article>
          <div className="connection-lanes" aria-label="Data flow between customer and Linx">
            <div><span>READ PATH</span><strong>Scoped APIs, directories, webhooks</strong><i>→</i></div>
            <div><i>←</i><span>ACTION PATH</span><strong>SCIM or app API · policy gated</strong></div>
          </div>
          <article className="linx-party">
            <span>LINX PLATFORM</span>
            <h3>Context, decision &amp; action</h3>
            <p>Identity Graph · Intelligence · Automation</p>
          </article>
        </div>
      </section>

      <section className="event-story card">
        <header>
          <div><span>REFERENCE EVENT</span><h2>Alex moves from Support to Finance</h2></div>
          <p>Follow one real-world mover event from the customer source to an auditable access change.</p>
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
          <strong>Correct access for the new role</strong>
          <i>•</i><strong>Obsolete privilege removed</strong>
          <i>•</i><strong>Complete audit evidence</strong>
        </footer>
      </section>

      <section className="protocol-strip" aria-label="Protocol roles">
        {protocols.map((protocol) => (
          <article className="card" key={protocol.name} style={{ borderTopColor: protocol.accent }}>
            <strong>{protocol.name}</strong><p>{protocol.role}</p>
          </article>
        ))}
      </section>

      <div className="connection-note">
        <p><strong>Keep the roles straight:</strong> OAuth authorizes the connection, SAML supplies authentication context, and SCIM changes users and groups. They are complementary—not interchangeable.</p>
        <a href="https://www.linx.security/platform/integrations" target="_blank" rel="noreferrer">View Linx integrations →</a>
      </div>
      <p className="source-note">This is an illustrative integration. The exact read and write path depends on each connected system and the customer&apos;s approval policy.</p>
    </div>
  );
}
