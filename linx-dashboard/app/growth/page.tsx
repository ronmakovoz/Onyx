"use client";

import { useState } from "react";
import { accounts, expansionArr, expansionPlays, formatMoney, solutionProducts, totalArr } from "../lib/data";
import { Kpi, PageHeader, SectionTitle } from "../components/UI";

export default function GrowthPage() {
  const [selectedId, setSelectedId] = useState(accounts[0].id);
  const selected = accounts.find((account) => account.id === selectedId) ?? accounts[0];
  const selectedPlays = (expansionPlays[selected.id] ?? []).map((play) => ({
    ...play,
    product: solutionProducts.find((product) => product.id === play.productId)!,
  })).filter((play) => play.product);
  const ownedSolutions = accounts.reduce((sum, account) => sum + account.solutions.length, 0);
  const solutionCoverage = Math.round((ownedSolutions / (accounts.length * solutionProducts.length)) * 100);

  return (
    <div>
      <PageHeader title="Solution Growth & Whitespace" subtitle="Sequence the next Linx solution from customer evidence—not from an undifferentiated product checklist" />
      <section className="kpi-grid four"><Kpi label="Current portfolio ARR" value={formatMoney(totalArr)} detail="modeled customer book" tone="blue" /><Kpi label="Identified whitespace" value={formatMoney(expansionArr)} detail="evidence-backed opportunity" tone="green" /><Kpi label="Solution coverage" value={`${solutionCoverage}%`} detail={`${ownedSolutions} of ${accounts.length * solutionProducts.length} modeled modules`} tone="purple" /><Kpi label="Growth potential" value="+22%" detail="only where core adoption is healthy" tone="yellow" /></section>

      <SectionTitle meta="foundation capabilities are shared · this matrix tracks solution modules">Solution penetration</SectionTitle>
      <section className="solution-legend card" aria-label="Linx solution definitions">
        {solutionProducts.map((product) => <div key={product.id}><i style={{ background: product.accent }} /><span><strong>{product.short}</strong><small>{product.name}</small></span></div>)}
      </section>
      <section className="card matrix-wrap">
        <div className="matrix-head"><span>Account</span>{solutionProducts.map((product) => <span title={product.name} key={product.id}>{product.short}</span>)}<span>ARR → goal</span></div>
        {accounts.map((account) => (
          <button key={account.id} className={`matrix-row ${selected.id === account.id ? "selected" : ""}`} onClick={() => setSelectedId(account.id)}>
            <span><strong>{account.name}</strong><small>{account.industry}</small></span>
            {solutionProducts.map((product) => {
              const owned = account.solutions.includes(product.id);
              const recommendation = (expansionPlays[account.id] ?? []).some((play) => play.productId === product.id);
              return <span key={product.id}><i className={owned ? "owned" : recommendation ? "recommended" : "empty"} style={owned ? { background: product.accent } : undefined} /></span>;
            })}
            <span><b>{formatMoney(account.arr)}</b>{account.expansion > 0 && <em> → {formatMoney(account.arr + account.expansion)}</em>}</span>
          </button>
        ))}
      </section>

      <section className="card whitespace-detail">
        <div className="whitespace-heading"><div><span>ACCOUNT GROWTH PLAN</span><h2>{selected.name}</h2><p>{selected.industry} · health {selected.health} · adoption {selected.adoption}%</p></div><div><span>ARR goal</span><strong>{formatMoney(selected.arr)} → {formatMoney(selected.arr + selected.expansion)}</strong></div></div>
        {selectedPlays.length ? <div className="recommendation-grid">{selectedPlays.map((play) => (
          <article key={play.productId} style={{ borderTopColor: play.product.accent }}>
            <span>{play.timing.toUpperCase()} · EVIDENCE-BASED PLAY</span>
            <h3>{play.product.name}</h3>
            <p>{play.product.description}</p>
            <div className="play-rationale"><strong>Why it fits</strong><p>{play.rationale}</p></div>
            <div className="play-proof"><strong>Proof before expansion</strong><p>{play.proof}</p></div>
            <div><b>Est. {formatMoney(Math.max(70000, Math.round(selected.expansion / selectedPlays.length)))}/yr</b><small>{play.product.outcome}</small></div>
          </article>
        ))}</div> : <p className="empty-state">No expansion is recommended yet. Stabilize the core identity program and prove durable adoption before adding another solution.</p>}
      </section>
    </div>
  );
}
