"use client";

import { useMemo, useState } from "react";
import { accounts, formatMoney, riskColor } from "../lib/data";
import { Kpi, PageHeader, Progress, RiskPill, SectionTitle } from "../components/UI";

export default function TeamPage() {
  const owners = useMemo(() => Array.from(new Set(accounts.map((account) => account.owner))).map((owner) => {
    const book = accounts.filter((account) => account.owner === owner);
    return {
      owner,
      book,
      arr: book.reduce((sum, account) => sum + account.arr, 0),
      expansion: book.reduce((sum, account) => sum + account.expansion, 0),
      avgHealth: Math.round(book.reduce((sum, account) => sum + account.health, 0) / book.length),
      avgAdoption: Math.round(book.reduce((sum, account) => sum + account.adoption, 0) / book.length),
      high: book.filter((account) => account.risk === "High").length,
      medium: book.filter((account) => account.risk === "Medium").length,
      low: book.filter((account) => account.risk === "Low").length,
    };
  }).sort((a, b) => a.avgHealth - b.avgHealth), []);
  const [selectedOwner, setSelectedOwner] = useState(owners[0].owner);
  const selected = owners.find((owner) => owner.owner === selectedOwner) ?? owners[0];
  const totalAtRisk = accounts.filter((account) => account.risk === "High").reduce((sum, account) => sum + account.arr, 0);

  return (
    <div>
      <PageHeader title="CSM Performance" subtitle="Portfolio health, adoption, renewal exposure, and expansion by Customer Success Manager" />
      <section className="kpi-grid four"><Kpi label="CS managers" value={String(owners.length)} detail={`${accounts.length} enterprise accounts`} tone="blue" /><Kpi label="ARR at risk" value={formatMoney(totalAtRisk)} detail="across three accounts" tone="coral" /><Kpi label="Average adoption" value="74%" detail="identity-program utilization" tone="green" /><Kpi label="Expansion coverage" value="7/10" detail="accounts with modeled plays" tone="yellow" /></section>

      <div className="team-layout">
        <section><SectionTitle meta="sorted by book health">Team overview</SectionTitle><div className="card team-table">
          <div className="team-head"><span>Manager</span><span>Health</span><span>Book mix</span><span>ARR</span><span>Expansion</span><span>Adoption</span></div>
          {owners.map((owner) => <button key={owner.owner} className={owner.owner === selected.owner ? "selected" : ""} onClick={() => setSelectedOwner(owner.owner)}>
            <span><strong>{owner.owner}</strong><small>{owner.book.length} accounts</small></span><span><b style={{ color: owner.avgHealth < 60 ? "#d65745" : owner.avgHealth < 75 ? "#b97b14" : "#2c8f70" }}>{owner.avgHealth}</b></span><span><i className="mix high" style={{ width: `${(owner.high / owner.book.length) * 100}%` }} /><i className="mix medium" style={{ width: `${(owner.medium / owner.book.length) * 100}%` }} /><i className="mix low" style={{ width: `${(owner.low / owner.book.length) * 100}%` }} /></span><span>{formatMoney(owner.arr)}</span><span className="healthy">{formatMoney(owner.expansion)}</span><span><Progress value={owner.avgAdoption} color="#2f8cff" /><small>{owner.avgAdoption}%</small></span>
          </button>)}
        </div></section>

        <aside><SectionTitle>{selected.owner}&apos;s book</SectionTitle><div className="card team-book">
          <div className="coach-callout"><span>COACHING FOCUS</span><strong>{selected.high ? "Recover renewal-critical programs" : "Convert healthy adoption into expansion"}</strong><p>{selected.high ? "Tighten sponsor coverage, implementation recovery, and value evidence." : "Prioritize peer-evidenced platform whitespace."}</p></div>
          {selected.book.sort((a, b) => a.health - b.health).map((account) => <div className="book-row" key={account.id}><div className="book-health" style={{ color: riskColor(account.risk) }}>{account.health}</div><div><strong>{account.name}</strong><p>{account.nextAction}</p></div><RiskPill risk={account.risk} /></div>)}
        </div></aside>
      </div>
    </div>
  );
}
