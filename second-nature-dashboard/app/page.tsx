import Link from "next/link";
import { accounts, atRiskArr, expansionArr, formatMoney, totalArr } from "./lib/data";
import { Kpi, PageHeader, Progress, RiskPill, SectionTitle } from "./components/UI";

export default function DashboardPage() {
  const highRisk = accounts.filter((account) => account.risk === "High").sort((a, b) => a.renewalDays - b.renewalDays);
  const expansion = accounts.filter((account) => account.expansion > 0).sort((a, b) => b.expansion - a.expansion).slice(0, 5);
  const avgAdoption = Math.round(accounts.reduce((sum, account) => sum + account.adoption, 0) / accounts.length);
  const avgActivation = Math.round(accounts.reduce((sum, account) => sum + account.rbpActivation, 0) / accounts.length);

  return (
    <div>
      <PageHeader
        title="Executive Dashboard"
        subtitle="Portfolio health · resident experience outcomes · renewal and growth signals"
        action={<span className="date-chip">Live demo · Q3 FY26</span>}
      />

      <section className="executive-brief">
        <div className="brief-label"><span>✦</span> AI EXECUTIVE SUMMARY <small>portfolio context</small></div>
        <p>
          Portfolio health is <strong>stable with concentrated renewal risk</strong>. Three accounts represent {formatMoney(atRiskArr)} of ARR at risk, led by Pioneer Residential and Aperture Residential. Outcomes are strongest where a fully managed Resident Benefits Package is paired with Resident Onboarding. The clearest growth motion is expanding healthy portfolios into <strong>Maestro™, Group Rate Internet, Credit Building, and interactive onboarding</strong>.
        </p>
        <div className="brief-metrics">
          <span><i className="dot green" /> 4 healthy</span>
          <span><i className="dot amber" /> 3 watch</span>
          <span><i className="dot coral" /> 3 priority actions</span>
          <span className="brief-source">Built from synthetic property-manager telemetry</span>
        </div>
      </section>

      <section className="kpi-grid six">
        <Kpi label="Portfolio ARR" value={formatMoney(totalArr)} detail="10 property-management accounts" tone="blue" />
        <Kpi label="Net Revenue Retention" value="112%" detail="GRR 95% · +4 pts YoY" tone="green" />
        <Kpi label="ARR at Risk" value={formatMoney(atRiskArr)} detail="3 high-risk renewals" tone="coral" />
        <Kpi label="Renewal Forecast" value="89%" detail="$3.1M in next 90 days" tone="yellow" />
        <Kpi label="Expansion Pipeline" value={formatMoney(expansionArr)} detail="onboarding + RBP whitespace" tone="purple" />
        <Kpi label="Platform Adoption" value={`${avgAdoption}%`} detail={`${avgActivation}% RBP activation`} tone="aqua" />
      </section>

      <section className="priority-strip">
        <span>THIS WEEK</span>
        <div><strong>Recover the three renewal-critical resident programs.</strong><p>PAS mapping, lease addenda, executive sponsorship, and resident activation are the controllable risks.</p></div>
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
        <SectionTitle meta="synthetic outcomes across this portfolio">Resident experience telemetry</SectionTitle>
        <div className="telemetry-grid">
          <article className="card telemetry"><span>Doors managed</span><strong>113.7K</strong><Progress value={82} color="#6c4df6" /><small>Single-family, multifamily, and build-to-rent homes</small></article>
          <article className="card telemetry"><span>Resident experiences</span><strong>253K</strong><Progress value={88} color="#00a98f" /><small>Personalized onboarding and fully managed benefits</small></article>
          <article className="card telemetry"><span>Annual onboardings</span><strong>50.5K</strong><Progress value={76} color="#ffc928" /><small>Lease Guide, e-sign, benefits, and Move Guide</small></article>
          <article className="card telemetry"><span>Team hours saved</span><strong>25.9K</strong><Progress value={67} color="#b886ff" /><small>Automation and fully managed resident services</small></article>
        </div>
      </section>

      <section>
        <SectionTitle meta="public Second Nature proof points">The resident experience triple win</SectionTitle>
        <div className="proof-strip card">
          <a href="https://www.secondnature.com/" target="_blank" rel="noreferrer"><strong>2,500+</strong><span>property managers</span></a>
          <a href="https://www.secondnature.com/" target="_blank" rel="noreferrer"><strong>2M+</strong><span>resident experiences</span></a>
          <a href="https://www.secondnature.com/benefits" target="_blank" rel="noreferrer"><strong>Up to 64 pts</strong><span>credit-score lift in year one</span></a>
          <a href="https://www.secondnature.com/benefits" target="_blank" rel="noreferrer"><strong>37%</strong><span>fewer HVAC work orders</span></a>
        </div>
      </section>

      <footer className="demo-footer">Second Nature Resident Experience Intelligence OS · Synthetic customer and performance data · Product positioning based on secondnature.com</footer>
    </div>
  );
}
