"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Kpi, PageHeader, SectionTitle } from "../components/UI";

type Range = "24h" | "7d" | "30d";
type RecordValue = Record<string, string | number | null>;
type Summary = {
  generatedAt: number;
  kpis: RecordValue;
  sessions: RecordValue[];
  pages: RecordValue[];
  clicks: RecordValue[];
  activity: RecordValue[];
  events: RecordValue[];
};

function number(value: unknown) {
  return Number(value) || 0;
}

function formatDuration(value: unknown) {
  const seconds = Math.round(number(value) / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return minutes < 60 ? `${minutes}m ${remaining}s` : `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

function formatTime(value: unknown) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(number(value)));
}

function visitorName(row: RecordValue) {
  return String(row.authenticated_email || `Anonymous · ${String(row.visitor_id || "unknown").slice(0, 8)}`);
}

export default function ActivityDashboard({ ownerEmail }: { ownerEmail: string }) {
  const [range, setRange] = useState<Range>("7d");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/analytics/summary?range=${range}`, { cache: "no-store" });
      if (!response.ok) throw new Error("Analytics could not be loaded.");
      setSummary(await response.json() as Summary);
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Analytics could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [range]);

  useEffect(() => {
    const initial = window.setTimeout(() => void load(), 0);
    const timer = window.setInterval(() => void load(), 30_000);
    return () => {
      window.clearTimeout(initial);
      window.clearInterval(timer);
    };
  }, [load]);

  const chartMax = useMemo(() => Math.max(1, ...(summary?.activity ?? []).map((item) => number(item.page_views) + number(item.clicks))), [summary]);
  const kpis = summary?.kpis ?? {};

  return (
    <div>
      <PageHeader
        title="Activity Analytics"
        subtitle="Opens, page navigation, clicks, engagement time, and visitor sessions"
        action={<span className="owner-chip">OWNER ONLY · {ownerEmail}</span>}
      />

      <div className="analytics-toolbar card">
        <div className="segmented" aria-label="Analytics date range">
          {(["24h", "7d", "30d"] as Range[]).map((item) => <button key={item} className={range === item ? "active" : ""} onClick={() => setRange(item)}>{item === "24h" ? "24 hours" : item === "7d" ? "7 days" : "30 days"}</button>)}
        </div>
        <span>{loading ? "Refreshing…" : summary ? `Updated ${formatTime(summary.generatedAt)}` : "Waiting for data"}</span>
        <button className="refresh-button" onClick={() => void load()} disabled={loading}>Refresh</button>
      </div>

      {error && <div className="analytics-error">{error}</div>}

      <section className="kpi-grid analytics-kpis">
        <Kpi label="Sessions" value={String(number(kpis.sessions))} detail="dashboard opens" tone="blue" />
        <Kpi label="Unique visitors" value={String(number(kpis.unique_visitors))} detail="signed-in or anonymous IDs" tone="green" />
        <Kpi label="Page views" value={String(number(kpis.page_views))} detail="route navigation" tone="purple" />
        <Kpi label="Clicks" value={String(number(kpis.clicks))} detail="links and actions" tone="coral" />
        <Kpi label="Avg. session" value={formatDuration(kpis.avg_duration_ms)} detail="active elapsed time" tone="yellow" />
      </section>

      <div className="analytics-grid">
        <section className="analytics-wide">
          <SectionTitle meta={`${range} window`}>Engagement timeline</SectionTitle>
          <div className="card activity-chart">
            {(summary?.activity ?? []).length ? (summary?.activity ?? []).map((item) => {
              const pageViews = number(item.page_views);
              const clicks = number(item.clicks);
              return <div className="chart-column" key={String(item.bucket)}><div className="chart-bars"><i className="views" style={{ height: `${Math.max(4, (pageViews / chartMax) * 100)}%` }} title={`${pageViews} page views`} /><i className="clicks" style={{ height: `${Math.max(4, (clicks / chartMax) * 100)}%` }} title={`${clicks} clicks`} /></div><span>{String(item.bucket).slice(range === "24h" ? 11 : 5)}</span></div>;
            }) : <div className="analytics-empty">Activity will appear as people use the dashboard.</div>}
          </div>
          <div className="chart-legend"><span><i className="views" /> Page views</span><span><i className="clicks" /> Clicks</span></div>
        </section>

        <section>
          <SectionTitle meta="most visited">Top pages</SectionTitle>
          <div className="card rank-list">{(summary?.pages ?? []).length ? summary?.pages.map((item, index) => <div key={String(item.path)}><b>{index + 1}</b><span><strong>{String(item.path)}</strong><small>{number(item.sessions)} sessions</small></span><em>{number(item.views)}</em></div>) : <div className="analytics-empty">No page views yet.</div>}</div>
        </section>
      </div>

      <section>
        <SectionTitle meta="most recent first">Visitor sessions</SectionTitle>
        <div className="card analytics-table-wrap">
          <div className="session-head"><span>Visitor</span><span>Entry → current</span><span>Started</span><span>Last seen</span><span>Time</span><span>Views</span><span>Clicks</span></div>
          {(summary?.sessions ?? []).length ? summary?.sessions.map((item) => <div className="session-row" key={String(item.id)}><span><strong>{visitorName(item)}</strong><small>{String(item.user_agent || "Unknown device").slice(0, 54)}</small></span><span><strong>{String(item.entry_path)}</strong><small>→ {String(item.current_path)}</small></span><span>{formatTime(item.started_at)}</span><span>{formatTime(item.last_seen_at)}</span><span>{formatDuration(item.duration_ms)}</span><b>{number(item.page_views)}</b><b>{number(item.clicks)}</b></div>) : <div className="analytics-empty">No sessions in this period.</div>}
        </div>
      </section>

      <div className="analytics-grid analytics-bottom">
        <section>
          <SectionTitle meta="links and actions">Top clicks</SectionTitle>
          <div className="card rank-list">{(summary?.clicks ?? []).length ? summary?.clicks.map((item, index) => <div key={`${item.label}-${item.path}-${index}`}><b>{index + 1}</b><span><strong>{String(item.label)}</strong><small>{String(item.path)}</small></span><em>{number(item.clicks)}</em></div>) : <div className="analytics-empty">No clicks yet.</div>}</div>
        </section>
        <section className="analytics-wide">
          <SectionTitle meta="latest 150 events">Event stream</SectionTitle>
          <div className="card event-stream">{(summary?.events ?? []).length ? summary?.events.map((item, index) => <div key={`${item.session_id}-${item.occurred_at}-${index}`}><i className={`event-${item.event_type}`} /><span><strong>{String(item.event_type).replaceAll("_", " ")}</strong><small>{visitorName(item)} · {String(item.path)}</small></span><time>{formatTime(item.occurred_at)}</time></div>) : <div className="analytics-empty">No events yet.</div>}</div>
        </section>
      </div>

      <p className="analytics-privacy">Tracks route views, elapsed time, and link or button clicks. It does not record form values, keystrokes, or raw IP addresses.</p>
    </div>
  );
}
