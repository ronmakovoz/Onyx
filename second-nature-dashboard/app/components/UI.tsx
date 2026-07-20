import type { ReactNode } from "react";

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return <header className="page-header"><div><h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>{action}</header>;
}

export function Kpi({ label, value, detail, tone = "blue" }: { label: string; value: string; detail: string; tone?: string }) {
  return <article className={`kpi tone-${tone}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

export function SectionTitle({ children, meta }: { children: ReactNode; meta?: string }) {
  return <div className="section-title"><h2>{children}</h2>{meta && <span>{meta}</span>}</div>;
}

export function RiskPill({ risk }: { risk: string }) {
  return <span className={`risk-pill risk-${risk.toLowerCase()}`}>{risk}</span>;
}

export function Progress({ value, color = "#6c4df6" }: { value: number; color?: string }) {
  return <span className="progress"><i style={{ width: `${Math.max(0, Math.min(100, value))}%`, background: color }} /></span>;
}
