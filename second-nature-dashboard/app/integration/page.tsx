import { PageHeader, SectionTitle } from "../components/UI";

const sources = ["AppFolio", "Rentvine", "Property accounting", "Resident profiles", "Leases & addenda", "Custom fields", "GL codes", "Property groups"];
const maestro = ["Map documents", "Personalize journeys", "Apply when/then rules", "Automate communications"];
const outcomes = [
  ["Resident Onboarding", "Lease Guide, e-sign, benefits, and Move Guide", "#ff7452"],
  ["Group Rate Internet", "Portfolio-priced internet with 24/7 support", "#6c4df6"],
  ["Renters Insurance", "Coverage tracking and automatic enrollment", "#00a98f"],
  ["Financial Health", "Credit Building, Rewards, and Identity Protection", "#2c8cff"],
  ["Asset Protection", "Air Filter Delivery and On-Demand Pest Control", "#78b84c"],
  ["Move-In Concierge", "Guided utility and service setup", "#ff9c66"],
] as const;

export default function IntegrationPage() {
  return (
    <div>
      <PageHeader title="How Second Nature Connects" subtitle="Integrate property data, orchestrate personalized resident journeys, and deliver a fully managed Resident Benefits Package" />
      <section className="card architecture">
        <div className="architecture-column sources"><span>01 · INTEGRATE</span><h2>Property systems &amp; data</h2><p>Connect the existing property accounting system and map the portfolio once.</p><div>{sources.map((source) => <b key={source}>{source}</b>)}</div></div>
        <div className="flow-arrow"><span>CONTEXT</span><i>→</i></div>
        <div className="architecture-column graph"><span>02 · ORCHESTRATE</span><h2>Maestro™</h2><p>Personalize the approved-to-moved journey by property, market, and resident.</p><div>{maestro.map((item, index) => <b key={item}><i>{index + 1}</i>{item}</b>)}</div><em>Documents · compliance · automation · personalization</em></div>
        <div className="flow-arrow"><span>EXPERIENCE</span><i>→</i></div>
        <div className="architecture-column outcomes"><span>03 · DELIVER</span><h2>The triple win</h2><p>Build resident financial health, protect investor assets, and take work off PM teams.</p><div>{outcomes.map(([name, description, color]) => <article key={name} style={{ borderLeftColor: color }}><strong>{name}</strong><small>{description}</small></article>)}</div></div>
      </section>

      <SectionTitle meta="from approved to moved">Four steps to value</SectionTitle>
      <section className="steps-grid"><article><span>01</span><h3>Build</h3><p>Design the right Resident Benefits Package and personalized onboarding experience for each market.</p></article><article><span>02</span><h3>Integrate</h3><p>Connect the property accounting system and map custom fields, GL codes, documents, and properties.</p></article><article><span>03</span><h3>Go live</h3><p>Launch lease addenda, resident education, SMS access, e-sign, benefit choice, and move-in tasks.</p></article><article><span>04</span><h3>Scale activation</h3><p>Attach the experience to every new lease and renewal until the portfolio reaches full activation.</p></article></section>

      <div className="platform-proof-grid">
        <article className="card"><span>RESIDENTS WIN</span><strong>Financial health &amp; frictionless living</strong><p>Choice, clarity, credit building, savings, protection, and simpler move-ins.</p></article>
        <article className="card"><span>INVESTORS WIN</span><strong>Protected assets &amp; stronger returns</strong><p>Fewer HVAC work orders, complete insurance coverage, differentiation, and retention.</p></article>
        <article className="card"><span>PROPERTY MANAGERS WIN</span><strong>More NOI with less operational work</strong><p>Fully managed benefits, automated workflows, clearer leases, and fewer resident calls.</p></article>
      </div>
      <p className="source-note">Platform mapping reflects current public secondnature.com positioning. Dashboard metrics and customer records are synthetic.</p>
    </div>
  );
}
