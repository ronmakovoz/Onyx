import { env } from "cloudflare:workers";

export const OWNER_EMAIL = "ron.makovoz@gmail.com";

export type AnalyticsRange = "24h" | "7d" | "30d";
export type AnalyticsEventType = "session_start" | "page_view" | "page_leave" | "click" | "heartbeat" | "session_end";

export type AnalyticsEventInput = {
  visitorId: string;
  sessionId: string;
  eventType: AnalyticsEventType;
  path: string;
  target?: string;
  label?: string;
  referrer?: string;
  durationMs?: number;
  sessionDurationMs?: number;
};

const EVENT_TYPES = new Set<AnalyticsEventType>(["session_start", "page_view", "page_leave", "click", "heartbeat", "session_end"]);

function database() {
  if (!env.DB) throw new Error("Analytics database is unavailable.");
  return env.DB;
}

function cleanText(value: unknown, max: number) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function cleanDuration(value: unknown) {
  const duration = Number(value);
  return Number.isFinite(duration) ? Math.max(0, Math.min(86_400_000, Math.round(duration))) : 0;
}

export function isOwnerEmail(email: string | null | undefined) {
  return email?.trim().toLowerCase() === OWNER_EMAIL;
}

export function parseAnalyticsEvent(value: unknown): AnalyticsEventInput | null {
  if (!value || typeof value !== "object") return null;
  const body = value as Record<string, unknown>;
  const eventType = cleanText(body.eventType, 32) as AnalyticsEventType;
  const visitorId = cleanText(body.visitorId, 80);
  const sessionId = cleanText(body.sessionId, 80);
  const path = cleanText(body.path, 500);
  if (!EVENT_TYPES.has(eventType) || !visitorId || !sessionId || !path.startsWith("/")) return null;

  return {
    visitorId,
    sessionId,
    eventType,
    path,
    target: cleanText(body.target, 1000) || undefined,
    label: cleanText(body.label, 180) || undefined,
    referrer: cleanText(body.referrer, 1000) || undefined,
    durationMs: cleanDuration(body.durationMs),
    sessionDurationMs: cleanDuration(body.sessionDurationMs),
  };
}

export async function recordAnalyticsEvent(input: AnalyticsEventInput, request: Request) {
  const db = database();
  const now = Date.now();
  const email = cleanText(request.headers.get("oai-authenticated-user-email"), 320).toLowerCase() || null;
  const userAgent = cleanText(request.headers.get("user-agent"), 500) || null;
  const pageViewDelta = input.eventType === "page_view" ? 1 : 0;
  const clickDelta = input.eventType === "click" ? 1 : 0;
  const isEnd = input.eventType === "session_end" ? 1 : 0;
  const updatesCurrentPath = input.eventType === "session_start" || input.eventType === "page_view" ? 1 : 0;

  await db.batch([
    db.prepare(`INSERT OR IGNORE INTO analytics_sessions
      (id, visitor_id, authenticated_email, started_at, last_seen_at, ended_at, entry_path, current_path, page_views, clicks, duration_ms, referrer, user_agent)
      VALUES (?, ?, ?, ?, ?, NULL, ?, ?, 0, 0, 0, ?, ?)`)
      .bind(input.sessionId, input.visitorId, email, now, now, input.path, input.path, input.referrer ?? null, userAgent),
    db.prepare(`UPDATE analytics_sessions SET
      last_seen_at = ?,
      current_path = CASE WHEN ? = 1 THEN ? ELSE current_path END,
      authenticated_email = COALESCE(?, authenticated_email),
      page_views = page_views + ?,
      clicks = clicks + ?,
      duration_ms = MAX(duration_ms, ?),
      ended_at = CASE WHEN ? = 1 THEN ? ELSE ended_at END
      WHERE id = ?`)
      .bind(now, updatesCurrentPath, input.path, email, pageViewDelta, clickDelta, input.sessionDurationMs ?? 0, isEnd, now, input.sessionId),
    db.prepare(`INSERT INTO analytics_events
      (id, session_id, visitor_id, authenticated_email, event_type, path, target, label, referrer, user_agent, occurred_at, duration_ms)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
      .bind(crypto.randomUUID(), input.sessionId, input.visitorId, email, input.eventType, input.path, input.target ?? null, input.label ?? null, input.referrer ?? null, userAgent, now, input.durationMs ?? 0),
  ]);
}

function rangeStart(range: AnalyticsRange) {
  const hours = range === "24h" ? 24 : range === "30d" ? 24 * 30 : 24 * 7;
  return Date.now() - hours * 60 * 60 * 1000;
}

export async function getAnalyticsSummary(range: AnalyticsRange) {
  const db = database();
  const since = rangeStart(range);
  const bucketExpression = range === "24h"
    ? "strftime('%Y-%m-%d %H:00', occurred_at / 1000, 'unixepoch')"
    : "strftime('%Y-%m-%d', occurred_at / 1000, 'unixepoch')";

  const [kpis, sessions, pages, clicks, activity, events] = await Promise.all([
    db.prepare(`SELECT
      COUNT(*) AS sessions,
      COUNT(DISTINCT COALESCE(authenticated_email, visitor_id)) AS unique_visitors,
      COALESCE(SUM(page_views), 0) AS page_views,
      COALESCE(SUM(clicks), 0) AS clicks,
      COALESCE(AVG(duration_ms), 0) AS avg_duration_ms
      FROM analytics_sessions WHERE started_at >= ?`).bind(since).first(),
    db.prepare(`SELECT id, visitor_id, authenticated_email, started_at, last_seen_at, ended_at, entry_path, current_path, page_views, clicks, duration_ms, referrer, user_agent
      FROM analytics_sessions WHERE started_at >= ? ORDER BY last_seen_at DESC LIMIT 100`).bind(since).all(),
    db.prepare(`SELECT path, COUNT(*) AS views, COUNT(DISTINCT session_id) AS sessions
      FROM analytics_events WHERE occurred_at >= ? AND event_type = 'page_view'
      GROUP BY path ORDER BY views DESC, path ASC LIMIT 12`).bind(since).all(),
    db.prepare(`SELECT COALESCE(NULLIF(label, ''), NULLIF(target, ''), 'Unknown click') AS label, target, path, COUNT(*) AS clicks
      FROM analytics_events WHERE occurred_at >= ? AND event_type = 'click'
      GROUP BY label, target, path ORDER BY clicks DESC LIMIT 12`).bind(since).all(),
    db.prepare(`SELECT ${bucketExpression} AS bucket,
      SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) AS page_views,
      SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS clicks,
      COUNT(DISTINCT session_id) AS sessions
      FROM analytics_events WHERE occurred_at >= ? GROUP BY bucket ORDER BY bucket ASC`).bind(since).all(),
    db.prepare(`SELECT event_type, path, target, label, occurred_at, duration_ms, session_id, authenticated_email, visitor_id
      FROM analytics_events WHERE occurred_at >= ? ORDER BY occurred_at DESC LIMIT 150`).bind(since).all(),
  ]);

  return {
    range,
    generatedAt: Date.now(),
    kpis: kpis ?? { sessions: 0, unique_visitors: 0, page_views: 0, clicks: 0, avg_duration_ms: 0 },
    sessions: sessions.results ?? [],
    pages: pages.results ?? [],
    clicks: clicks.results ?? [],
    activity: activity.results ?? [],
    events: events.results ?? [],
  };
}
