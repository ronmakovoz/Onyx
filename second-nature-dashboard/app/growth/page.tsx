"use client";

import { useState } from "react";
import { accounts, expansionArr, formatMoney, products, totalArr } from "../lib/data";
import { Kpi, PageHeader, SectionTitle } from "../components/UI";

export default function GrowthPage() {
  const [selectedId, setSelectedId] = useState(accounts[0].id);
  const selected = accounts.find((account) => account.id === selectedId) ?? accounts[0];
  const recommended = products.filter((product) => !selected.products.includes(product.id)).slice(0, 3);

  return (
    <div>
      <PageHeader title="Growth & Whitespace" subtitle="What customers use, what similar readiness programs adopt next, and the ARR opportunity" />
      <section className="kpi-grid four"><Kpi label="Current portfolio ARR" value={formatMoney(totalArr)} detail="modeled customer book" tone="blue" /><Kpi label="Identified whitespace" value={formatMoney(expansionArr)} detail="peer-evidenced opportunity" tone="green" /><Kpi label="Ultimate ARR goal" value={formatMoney(totalArr + expansionArr)} detail="current plus whitespace" tone="purple" /><Kpi label="Growth potential" value="+22%" detail="across healthy accounts" tone="yellow" /></section>

      <SectionTitle meta="filled = owned · ring = recommended">Platform penetration</SectionTitle>
      <section className="card matrix-wrap">
        <div className="matrix-head"><span>Account</span>{products.map((product) => <span title={product.name} key={product.id}>{product.short}</span>)}<span>ARR → goal</span></div>
        {accounts.map((account) => (
          <button key={account.id} className={`matrix-row ${selected.id === account.id ? "selected" : ""}`} onClick={() => setSelectedId(account.id)}>
            <span><strong>{account.name}</strong><small>{account.industry}</small></span>
            {products.map((product) => {
              const owned = account.products.includes(product.id);
              const recommendation = !owned && account.expansion > 0 && ["coaching", "insights", "deal-coach", "languages", "integrations", "mobile"].includes(product.id);
              return <span key={product.id}><i className={owned ? "owned" : recommendation ? "recommended" : "empty"} style={owned ? { background: product.accent } : undefined} /></span>;
            })}
            <span><b>{formatMoney(account.arr)}</b>{account.expansion > 0 && <em> → {formatMoney(account.arr + account.expansion)}</em>}</span>
          </button>
        ))}
      </section>

      <section className="card whitespace-detail">
        <div className="whitespace-heading"><div><span>ACCOUNT GROWTH PLAN</span><h2>{selected.name}</h2><p>{selected.industry} · health {selected.health} · adoption {selected.adoption}%</p></div><div><span>ARR goal</span><strong>{formatMoney(selected.arr)} → {formatMoney(selected.arr + selected.expansion)}</strong></div></div>
        {recommended.length ? <div className="recommendation-grid">{recommended.map((product, index) => (
          <article key={product.id} style={{ borderTopColor: product.accent }}><span>{index === 0 ? "NEXT BEST MOVE" : "EXPANSION PLAY"}</span><h3>{product.name}</h3><p>{product.description}</p><div><b>Est. {formatMoney(Math.max(70000, Math.round(selected.expansion / recommended.length)))}/yr</b><small>{68 + index * 7}% peer adoption</small></div></article>
        ))}</div> : <p className="empty-state">This account is fully penetrated across the modeled Second Nature platform.</p>}
      </section>
    </div>
  );
}
