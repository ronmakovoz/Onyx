import Link from "next/link";
import { accounts, atRiskArr, expansionArr, formatMoney, platformCapabilities, solutionProducts, totalArr } from "./lib/data";
import { Kpi, PageHeader, Progress, RiskPill, SectionTitle } from "./components/UI";

export default function DashboardPage() {
  const highRisk = accounts.filter((account) => account.risk === "High").sort((a, b) => a.renewalDays - b.renewalDays);
  const expansion = accounts.filter((account) => account.expansion > 0).sort((a, b) => b.expansion - a.expansion).slice(0, 5);
  const avgAdoption = Math.round(accounts.reduce((sum, account) => sum + account.adoption, 0) / accounts.length);
  const avgReview = Math.round(accounts.reduce((sum, account) => sum + account.reviewCompletion, 0) / accounts.length);

  return (
    <div>
      <PageHeader
        title="Executive & Product Dashboard"
        subtitle="Customer health, product adoption, identity outcomes, and growth signals"
        action={<span className="date-chip">Live demo · Q3 FY26</span>}
      />

      <section className="product-compass card">
        <div className="product-compass-copy">
          <span>WHAT LINX IS</span>
          <h2>One identity platform from fragmented access data to governed action.</h2>
          <p>Linx connects identity data without agents, maps every human, non-human, and AI-agent relationship in the Identity Graph, applies identity intelligence, then governs and remediates access.</p>
          <Link href="/integration">See how Linx connects →</Link>
        </div>
        <div className="product-foundation-flow" aria-label="Linx platform foundation">
          {platformCapabilities.map((capability, index) => (
            <div key={capability.id}>
              <i>{String(index + 1).padStart(2, "0")}</i>
              <span>{capability.stage}</span>
              <strong>{capability.name}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="solution-ribbon" aria-label="Linx solution modules">
        {solutionProducts.map((solution) => (
          <article key={solution.id} style={{ borderTopColor: solution.accent }}>
            <span>{solution.short}</span>
            <strong>{solution.name}</strong>
            <p>{solution.outcome}</p>
          </article>
        ))}
      </section>

      <section className="executive-brief">
        <div className="brief-label"><span>✦</span> AI EXECUTIVE SUMMARY <small>portfolio context</small></div>
        <p>
          Portfolio health is <strong>stable with concentrated renewal risk</strong>. Three accounts represent {formatMoney(atRiskArr)} of ARR at risk, led by Pioneer Systems and Aperture Health. Adoption is strongest where the shared Identity Graph foundation is paired with closed-loop remediation. The clearest solution growth motions are <strong>JIT Access, Agentic Identity Governance, and AI Access Control</strong>; Autopilot strengthens continuous operations across those programs.
        </p>
        <div className="brief-metrics">
          <span><i className="dot green" /> 4 healthy</span>
          <span><i className="dot amber" /> 3 watch</span>
          <span><i className="dot coral" /> 3 priority actions</span>
          <span className="brief-source">Built from synthetic account telemetry</span>
        </div>
      </section>

      <section className="kpi-grid six">
        <Kpi label="Portfolio ARR" value={formatMoney(totalArr)} detail="10 enterprise accounts" tone="blue" />
        <Kpi label="Net Revenue Retention" value="112%" detail="GRR 95% · +4 pts YoY" tone="green" />
        <Kpi label="ARR at Risk" value={formatMoney(atRiskArr)} detail="3 high-risk renewals" tone="coral" />
        <Kpi label="Renewal Forecast" value="89%" detail="$3.1M in next 90 days" tone="yellow" />
        <Kpi label="Expansion Pipeline" value={formatMoney(expansionArr)} detail="peer-evidenced whitespace" tone="purple" />
        <Kpi label="Program Adoption" value={`${avgAdoption}%`} detail={`${avgReview}% review completion`} tone="aqua" />
      </section>

      <section className="priority-strip">
        <span>THIS WEEK</span>
        <div><strong>Recover the three renewal-critical identity programs.</strong><p>Connector coverage, executive sponsorship, and remediation ownership are the controllable risks.</p></div>
        <Link href="/briefings">Generate VP review →</Link>
      </section>

      <div className="two-column">
        <section>
          <SectionTitle meta="sorted by urgency">Renewal &amp; risk watchlist</SectionTitle>
          <div className="card list-card">
            {highRisk.map((account) => (
              <Link href="/accounts" className="account-row" key={account.id}>
                <div className="health-score" style={{ color: account.health < 55 ? "#d65745" : "#b97b14" }}>{account.health}</div>
                <div className="account-main"><strong>{account.name}</strong><p>{account.riskReason}</p></div>
                <div className="account-meta"><RiskPill risk={account.risk} /><b>{account.renewalDays}d</b><small>{formatMoney(account.arr)}</small></div>
              </Link>
            ))}
            <Link className="card-link" href="/accounts">View all accounts →</Link>
          </div>
        </section>

        <section>
          <SectionTitle meta="highest-confidence plays">Expansion signals</SectionTitle>
          <div className="card list-card">
            {expansion.map((account) => (
              <div className="expansion-row" key={account.id}>
                <div><strong>{account.name}</strong><p>{account.nextAction}</p></div>
                <span>{formatMoney(account.expansion)}</span>
              </div>
            ))}
            <Link className="card-link" href="/growth">Open whitespace matrix →</Link>
          </div>
        </section>
      </div>

      <section>
        <SectionTitle meta="outcomes across the portfolio">Identity program telemetry</SectionTitle>
        <div className="telemetry-grid">
          <article className="card telemetry"><span>Identities governed</span><strong>664.7K</strong><Progress value={82} color="#2f8cff" /><small>Human, non-human, and agentic identities</small></article>
          <article className="card telemetry"><span>Connected systems</span><strong>275</strong><Progress value={76} color="#43c7a0" /><small>Cloud, SaaS, directories, and HR sources</small></article>
          <article className="card telemetry"><span>Risks remediated</span><strong>4,019</strong><Progress value={88} color="#f2c94c" /><small>Closed directly through Linx workflows</small></article>
          <article className="card telemetry"><span>Standing privilege removed</span><strong>37%</strong><Progress value={67} color="#b89cff" /><small>Across active JIT programs</small></article>
        </div>
      </section>

      <footer className="demo-footer">Linx Customer &amp; Product Intelligence OS · Synthetic customer and performance data · Product positioning based on public Linx materials</footer>
    </div>
  );
}
