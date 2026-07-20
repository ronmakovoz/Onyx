"use client";

import { useState } from "react";
import { implementations } from "../lib/data";
import { Kpi, PageHeader, Progress, SectionTitle } from "../components/UI";

const confidenceColor: Record<string, string> = { Low: "#d65745", Medium: "#b97b14", High: "#2c8f70" };

export default function ImplementationPage() {
  const [selected, setSelected] = useState(0);
  const project = implementations[selected];
  const atRisk = implementations.filter((item) => item.confidence === "Low").length;
  const average = Math.round(implementations.reduce((sum, item) => sum + item.progress, 0) / implementations.length);

  return (
    <div>
      <PageHeader title="Launch Command Center" subtitle="Delivery health from property-accounting integration through resident activation" />
      <section className="kpi-grid four"><Kpi label="Active launches" value="6" detail="property-manager rollouts" tone="blue" /><Kpi label="At risk" value={String(atRisk)} detail="need executive action" tone="coral" /><Kpi label="Average completion" value={`${average}%`} detail="across all milestones" tone="green" /><Kpi label="Median time to value" value="31d" detail="first activated properties" tone="yellow" /></section>

      <SectionTitle meta="click a row for project detail">All portfolio launches</SectionTitle>
      <div className="implementation-layout">
        <section className="card implementation-table">
          <div className="impl-head"><span>Account / phase</span><span>Confidence</span><span>Progress</span><span>Target</span><span>Schedule</span></div>
          {implementations.map((item, index) => (
            <button key={item.account} className={selected === index ? "selected" : ""} onClick={() => setSelected(index)}>
              <span><strong>{item.account}</strong><small>{item.phase}</small></span>
              <span><b style={{ color: confidenceColor[item.confidence] }}>{item.confidence}</b></span>
              <span><Progress value={item.progress} color={confidenceColor[item.confidence]} /><small>{item.progress}%</small></span>
              <span>{item.target}</span>
              <span className={item.delay ? "urgent" : "healthy"}>{item.delay ? `${item.delay}d behind` : "On time"}</span>
            </button>
          ))}
        </section>

        <aside className="card project-detail" style={{ borderTopColor: confidenceColor[project.confidence] }}>
          <span>PROJECT DEEP DIVE</span><h2>{project.account}</h2><p>{project.phase} · owner {project.owner}</p>
          <div className="project-progress"><div><strong>{project.progress}%</strong><span>{project.confidence} confidence</span></div><Progress value={project.progress} color={confidenceColor[project.confidence]} /></div>
          <div className="project-grid"><div><span>Go-live target</span><strong>{project.target}</strong></div><div><span>Schedule</span><strong className={project.delay ? "urgent" : "healthy"}>{project.delay ? `${project.delay} days behind` : "On time"}</strong></div></div>
          <div className="project-block"><span>ACTIVE BLOCKER</span><p>{project.blocker}</p></div>
          <div className="project-action"><span>RECOMMENDED ACTION</span><p>{project.action}</p></div>
          <div className="milestone-list"><span className="done">✓ Build the resident experience</span><span className="done">✓ Integrate PAS, fields, and GL codes</span><span className={project.progress > 70 ? "done" : "active"}>{project.progress > 70 ? "✓" : "●"} Go live with addenda and resident education</span><span className="pending">○ Scale toward 100% portfolio activation</span></div>
        </aside>
      </div>
    </div>
  );
}
