import Link from "next/link";
import { accounts, atRiskArr, expansionArr, formatMoney, totalArr } from "./lib/data";
import { Kpi, PageHeader, Progress, RiskPill, SectionTitle } from "./components/UI";

export default function DashboardPage() {
  const highRisk = accounts.filter((account) => account.risk === "High").sort((a, b) => a.renewalDays - b.renewalDays);
  const expansion = accounts.filter((account) => account.expansion > 0).sort((a, b) => b.expansion - a.expansion).slice(0, 5);
  const avgAdoption = Math.round(accounts.reduce((sum, account) => sum + account.adoption, 0) / accounts.length);
  const avgCertification = Math.round(accounts.reduce((sum, account) => sum + account.certification, 0) / accounts.length);

  return (
    <div>
      <PageHeader
        title="Executive Dashboard"
        subtitle="Portfolio health · readiness outcomes · renewal and growth signals"
        action={<span className="date-chip">Live demo · Q3 FY26</span>}
      />

      <section className="executive-brief">
        <div className="brief-label"><span>✦</span> AI EXECUTIVE SUMMARY <small>portfolio context</small></div>
        <p>
          Portfolio health is <strong>stable with concentrated renewal risk</strong>. Three accounts represent {formatMoney(atRiskArr)} of ARR at risk, led by Pioneer Systems and Aperture Health. Adoption is strongest where role-play practice is paired with objective coaching and manager insights. The clearest growth motion is expanding healthy programs into <strong>Deal Coach, multilingual delivery, enterprise integrations, and mobile practice</strong>.
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
        <Kpi label="Learner Adoption" value={`${avgAdoption}%`} detail={`${avgCertification}% certification`} tone="aqua" />
      </section>

      <section className="priority-strip">
        <span>THIS WEEK</span>
        <div><strong>Recover the three renewal-critical readiness programs.</strong><p>LMS sync, executive sponsorship, content ownership, and certification are the controllable risks.</p></div>
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
        <SectionTitle meta="outcomes across the portfolio">Readiness program telemetry</SectionTitle>
        <div className="telemetry-grid">
          <article className="card telemetry"><span>Active learners</span><strong>29.4K</strong><Progress value={82} color="#6c4df6" /><small>Sales, enablement, support, and L&amp;D cohorts</small></article>
          <article className="card telemetry"><span>Role plays completed</span><strong>219.5K</strong><Progress value={88} color="#00a98f" /><small>1:1, group, chat, and mobile simulations</small></article>
          <article className="card telemetry"><span>Average readiness lift</span><strong>23%</strong><Progress value={76} color="#ffc928" /><small>Baseline-to-current objective score improvement</small></article>
          <article className="card telemetry"><span>Manager hours returned</span><strong>8,740</strong><Progress value={67} color="#b886ff" /><small>Practice scaled without pulling managers off the floor</small></article>
        </div>
      </section>

      <footer className="demo-footer">Second Nature CX Intelligence OS · Synthetic customer and performance data · Product positioning based on public Second Nature materials</footer>
    </div>
  );
}
