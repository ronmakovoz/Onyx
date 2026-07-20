CREATE TABLE `analytics_events` (
	`id` text PRIMARY KEY NOT NULL,
	`session_id` text NOT NULL,
	`visitor_id` text NOT NULL,
	`authenticated_email` text,
	`event_type` text NOT NULL,
	`path` text NOT NULL,
	`target` text,
	`label` text,
	`referrer` text,
	`user_agent` text,
	`occurred_at` integer NOT NULL,
	`duration_ms` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE INDEX `analytics_events_occurred_at_idx` ON `analytics_events` (`occurred_at`);--> statement-breakpoint
CREATE INDEX `analytics_events_session_id_idx` ON `analytics_events` (`session_id`);--> statement-breakpoint
CREATE INDEX `analytics_events_type_path_idx` ON `analytics_events` (`event_type`,`path`);--> statement-breakpoint
CREATE TABLE `analytics_sessions` (
	`id` text PRIMARY KEY NOT NULL,
	`visitor_id` text NOT NULL,
	`authenticated_email` text,
	`started_at` integer NOT NULL,
	`last_seen_at` integer NOT NULL,
	`ended_at` integer,
	`entry_path` text NOT NULL,
	`current_path` text NOT NULL,
	`page_views` integer DEFAULT 0 NOT NULL,
	`clicks` integer DEFAULT 0 NOT NULL,
	`duration_ms` integer DEFAULT 0 NOT NULL,
	`referrer` text,
	`user_agent` text
);
--> statement-breakpoint
CREATE INDEX `analytics_sessions_started_at_idx` ON `analytics_sessions` (`started_at`);--> statement-breakpoint
CREATE INDEX `analytics_sessions_last_seen_at_idx` ON `analytics_sessions` (`last_seen_at`);--> statement-breakpoint
CREATE INDEX `analytics_sessions_visitor_id_idx` ON `analytics_sessions` (`visitor_id`);