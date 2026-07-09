"use client";

import { ReactNode } from "react";

// ── Card ───────────────────────────────────────────────────────────────────
export function Card({
  children,
  className = "",
  accent,
}: {
  children: ReactNode;
  className?: string;
  accent?: string; // left-border accent color
}) {
  return (
    <div
      className={`bg-white border border-line rounded-xl shadow-card p-4 ${className}`}
      style={accent ? { borderLeft: `3px solid ${accent}` } : undefined}
    >
      {children}
    </div>
  );
}

// ── KPI Card ───────────────────────────────────────────────────────────────
export function KpiCard({
  label,
  value,
  sub,
  valueColor,
}: {
  label: string;
  value: string;
  sub?: string;
  valueColor?: string;
}) {
  return (
    <div className="bg-white border border-line rounded-xl shadow-card px-[18px] py-4 min-h-[102px] flex flex-col justify-center">
      <div className="text-[0.66rem] text-muted uppercase tracking-[0.10em] font-bold mb-[3px]">
        {label}
      </div>
      <div
        className="text-[1.7rem] font-extrabold text-navy leading-[1.1]"
        style={valueColor ? { color: valueColor } : undefined}
      >
        {value}
      </div>
      {sub ? <div className="text-[0.72rem] text-muted mt-[2px]">{sub}</div> : null}
    </div>
  );
}

// ── Pill / badge ───────────────────────────────────────────────────────────
export function Pill({
  children,
  color = "#0E1E45",
  bg = "#F5F2EE",
  bordered = false,
}: {
  children: ReactNode;
  color?: string;
  bg?: string;
  bordered?: boolean;
}) {
  return (
    <span
      className="inline-block px-[9px] py-[2px] rounded-full text-[0.68rem] font-bold whitespace-nowrap align-middle"
      style={{
        color,
        background: bg,
        border: bordered ? `1px solid ${color}44` : undefined,
      }}
    >
      {children}
    </span>
  );
}

// ── Progress bar ───────────────────────────────────────────────────────────
export function ProgressBar({ pct, color = "#0E1E45" }: { pct: number; color?: string }) {
  return (
    <div className="flex-1 h-[6px] bg-[#EFEAE5] rounded-md overflow-hidden">
      <div
        className="h-full rounded-md"
        style={{ width: `${Math.max(0, Math.min(100, pct))}%`, background: color }}
      />
    </div>
  );
}

// ── Section label ──────────────────────────────────────────────────────────
export function SectionLabel({
  children,
  color = "#6B6280",
  className = "",
}: {
  children: ReactNode;
  color?: string;
  className?: string;
}) {
  return (
    <div
      className={`text-[0.72rem] font-bold uppercase tracking-[0.10em] mb-2 ${className}`}
      style={{ color }}
    >
      {children}
    </div>
  );
}

// ── Page header ────────────────────────────────────────────────────────────
export function PageHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  return (
    <div className="flex items-end justify-between gap-4 border-b border-line pb-3 mb-4">
      <div>
        <h1 className="text-[1.75rem] font-extrabold text-navy tracking-tight leading-tight">{title}</h1>
        {subtitle ? <div className="text-muted text-[0.84rem] mt-[2px]">{subtitle}</div> : null}
      </div>
      <div className="text-right shrink-0">
        <div className="text-[0.70rem] text-faint">{today}</div>
        <div className="text-[0.66rem] font-bold text-muted uppercase tracking-[0.10em] mt-[2px]">
          Linx · Identity Security &amp; Governance
        </div>
      </div>
    </div>
  );
}

// ── Stat chip (small grey tile) ───────────────────────────────────────────
export function StatChip({
  label,
  value,
  valueColor = "#0E1E45",
}: {
  label: string;
  value: ReactNode;
  valueColor?: string;
}) {
  return (
    <div className="bg-chip rounded-lg px-[14px] py-[7px] text-center min-w-[80px]">
      <div className="text-[0.60rem] font-bold text-muted uppercase tracking-[0.08em]">{label}</div>
      <div className="text-[1.05rem] font-extrabold leading-[1.3]" style={{ color: valueColor }}>
        {value}
      </div>
    </div>
  );
}

// ── Tabs (client-side) ─────────────────────────────────────────────────────
export function TabBar({
  tabs,
  active,
  onChange,
}: {
  tabs: string[];
  active: string;
  onChange: (t: string) => void;
}) {
  return (
    <div className="flex gap-[6px] border-b border-[#E0D8E8] mb-4 overflow-x-auto">
      {tabs.map((t) => (
        <button
          key={t}
          onClick={() => onChange(t)}
          className={`px-[14px] py-2 text-[0.88rem] whitespace-nowrap rounded-t-lg transition-colors ${
            t === active
              ? "text-navy font-bold border-b-[3px] border-navy -mb-px"
              : "text-muted font-semibold hover:text-navy hover:bg-lavender"
          }`}
        >
          {t}
        </button>
      ))}
    </div>
  );
}

// ── Spinner / loading row ──────────────────────────────────────────────────
export function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-muted text-sm py-6">
      <span className="inline-block w-4 h-4 border-2 border-line border-t-navy rounded-full animate-spin" />
      {label}
    </div>
  );
}
