"use client";

import { useMemo, useState } from "react";
import { accounts, formatMoney, products, riskColor, type Risk } from "../lib/data";
import { PageHeader, Progress, RiskPill, SectionTitle } from "../components/UI";

export default function AccountsPage() {
  const [search, setSearch] = useState("");
  const [risk, setRisk] = useState<"All" | Risk>("All");
  const [selectedId, setSelectedId] = useState(1);

  const visible = useMemo(() => accounts.filter((account) => {
    const matchSearch = `${account.name} ${account.industry} ${account.owner}`.toLowerCase().includes(search.toLowerCase());
    return matchSearch && (risk === "All" || account.risk === risk);
  }), [search, risk]);
  const selected = accounts.find((account) => account.id === selectedId) ?? accounts[0];

  return (
    <div>
      <PageHeader title="Account Intelligence" subtitle="Portfolio triage and customer 360 for every property-management partner" />

      <section className="account-toolbar card">
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search account, industry, or owner…" aria-label="Search accounts" />
        <div className="segmented">{(["All", "High", "Medium", "Low"] as const).map((item) => <button key={item} className={risk === item ? "active" : ""} onClick={() => setRisk(item)}>{item}</button>)}</div>
        <span>{visible.length} accounts</span>
      </section>

      <div className="account-layout">
        <section className="card account-table-card">
          <div className="table-head"><span>Account</span><span>Health</span><span>Adoption</span><span>Renewal</span><span>ARR</span></div>
          {visible.map((account) => (
            <button className={`table-account ${selected.id === account.id ? "selected" : ""}`} key={account.id} onClick={() => setSelectedId(account.id)}>
              <span><strong>{account.name}</strong><small>{account.industry} · {account.owner}</small></span>
              <span><b style={{ color: riskColor(account.risk) }}>{account.health}</b><RiskPill risk={account.risk} /></span>
              <span><Progress value={account.adoption} color="#6c4df6" /><small>{account.adoption}%</small></span>
              <span><b className={account.renewalDays < 60 ? "urgent" : ""}>{account.renewalDays}d</b></span>
              <span><b>{formatMoney(account.arr)}</b></span>
            </button>
          ))}
        </section>

        <aside className="card account-detail" style={{ borderTopColor: riskColor(selected.risk) }}>
          <div className="detail-heading"><div><span>CUSTOMER 360</span><h2>{selected.name}</h2><p>{selected.industry} · {selected.tier} · {selected.region}</p></div><div className="detail-health" style={{ color: riskColor(selected.risk) }}><strong>{selected.health}</strong><small>HEALTH</small></div></div>
          <div className="detail-kpis">
            <div><span>ARR</span><strong>{formatMoney(selected.arr)}</strong></div>
            <div><span>Renewal</span><strong>{selected.renewalDays}d</strong></div>
            <div><span>Adoption</span><strong>{selected.adoption}%</strong></div>
            <div><span>RBP active</span><strong>{selected.rbpActivation}%</strong></div>
          </div>
          <div className="insight-box"><span>PRIMARY RISK</span><p>{selected.riskReason}</p><strong>→ {selected.nextAction}</strong></div>

          <SectionTitle>Resident experience telemetry</SectionTitle>
          <div className="detail-telemetry">
            <div><span>Doors</span><b>{selected.doors.toLocaleString()}</b></div>
            <div><span>Residents</span><b>{selected.residents.toLocaleString()}</b></div>
            <div><span>Onboardings</span><b>{selected.onboardings.toLocaleString()}</b></div>
            <div><span>Lease completion</span><b>{selected.leaseCompletion}%</b></div>
          </div>

          <SectionTitle>Platform footprint</SectionTitle>
          <div className="product-tags">{products.map((product) => <span className={selected.products.includes(product.id) ? "owned" : "gap"} key={product.id}><i style={{ background: product.accent }} />{product.short}</span>)}</div>

          {selected.expansion > 0 && <div className="expansion-callout"><span>IDENTIFIED WHITESPACE</span><strong>{formatMoney(selected.expansion)}</strong><p>Peer-evidenced expansion across Resident Onboarding, Maestro™, and RBP benefits.</p></div>}
        </aside>
      </div>
    </div>
  );
}
