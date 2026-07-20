import { index, integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const analyticsSessions = sqliteTable("analytics_sessions", {
  id: text("id").primaryKey(),
  visitorId: text("visitor_id").notNull(),
  authenticatedEmail: text("authenticated_email"),
  startedAt: integer("started_at").notNull(),
  lastSeenAt: integer("last_seen_at").notNull(),
  endedAt: integer("ended_at"),
  entryPath: text("entry_path").notNull(),
  currentPath: text("current_path").notNull(),
  pageViews: integer("page_views").notNull().default(0),
  clicks: integer("clicks").notNull().default(0),
  durationMs: integer("duration_ms").notNull().default(0),
  referrer: text("referrer"),
  userAgent: text("user_agent"),
}, (table) => [
  index("analytics_sessions_started_at_idx").on(table.startedAt),
  index("analytics_sessions_last_seen_at_idx").on(table.lastSeenAt),
  index("analytics_sessions_visitor_id_idx").on(table.visitorId),
]);

export const analyticsEvents = sqliteTable("analytics_events", {
  id: text("id").primaryKey(),
  sessionId: text("session_id").notNull(),
  visitorId: text("visitor_id").notNull(),
  authenticatedEmail: text("authenticated_email"),
  eventType: text("event_type").notNull(),
  path: text("path").notNull(),
  target: text("target"),
  label: text("label"),
  referrer: text("referrer"),
  userAgent: text("user_agent"),
  occurredAt: integer("occurred_at").notNull(),
  durationMs: integer("duration_ms").notNull().default(0),
}, (table) => [
  index("analytics_events_occurred_at_idx").on(table.occurredAt),
  index("analytics_events_session_id_idx").on(table.sessionId),
  index("analytics_events_type_path_idx").on(table.eventType, table.path),
]);
