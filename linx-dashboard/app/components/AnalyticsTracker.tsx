"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";

type EventName = "session_start" | "page_view" | "page_leave" | "click" | "heartbeat" | "session_end";

type EventPayload = {
  eventType: EventName;
  path: string;
  target?: string;
  label?: string;
  referrer?: string;
  durationMs?: number;
  sessionDurationMs?: number;
};

const VISITOR_KEY = "linx_analytics_visitor";
const SESSION_KEY = "linx_analytics_session";

function randomId() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function getStoredId(storage: Storage, key: string) {
  const current = storage.getItem(key);
  if (current) return current;
  const value = randomId();
  storage.setItem(key, value);
  return value;
}

function currentPath() {
  return `${window.location.pathname}${window.location.search}`.slice(0, 500);
}

function sendAnalytics(payload: EventPayload, beacon = false) {
  let visitorId: string;
  let sessionId: string;
  try {
    visitorId = getStoredId(window.localStorage, VISITOR_KEY);
    sessionId = getStoredId(window.sessionStorage, SESSION_KEY);
  } catch {
    visitorId = randomId();
    sessionId = randomId();
  }

  const body = JSON.stringify({ visitorId, sessionId, ...payload });
  if (beacon && navigator.sendBeacon) {
    navigator.sendBeacon("/api/analytics/events", new Blob([body], { type: "application/json" }));
    return;
  }

  void fetch("/api/analytics/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    credentials: "same-origin",
    keepalive: true,
  }).catch(() => undefined);
}

export default function AnalyticsTracker() {
  const pathname = usePathname();
  const pageStartedAt = useRef(Date.now());
  const sessionStartedAt = useRef(Date.now());
  const sessionStarted = useRef(false);

  useEffect(() => {
    const now = Date.now();
    const trackedPath = currentPath();
    pageStartedAt.current = now;
    if (!sessionStarted.current) {
      sessionStarted.current = true;
      sendAnalytics({ eventType: "session_start", path: trackedPath, referrer: document.referrer.slice(0, 1000) });
    }
    sendAnalytics({ eventType: "page_view", path: trackedPath });

    return () => {
      const endedAt = Date.now();
      sendAnalytics({
        eventType: "page_leave",
        path: trackedPath,
        durationMs: endedAt - pageStartedAt.current,
        sessionDurationMs: endedAt - sessionStartedAt.current,
      }, true);
    };
  }, [pathname]);

  useEffect(() => {
    function handleClick(event: MouseEvent) {
      const origin = event.target instanceof Element ? event.target : null;
      const control = origin?.closest("a,button,[role='button']");
      if (!control) return;
      const label = (control.getAttribute("aria-label") || control.textContent || control.tagName)
        .replace(/\s+/g, " ")
        .trim()
        .slice(0, 180);
      const target = control instanceof HTMLAnchorElement
        ? control.href
        : control.getAttribute("data-action") || control.getAttribute("name") || control.tagName.toLowerCase();
      sendAnalytics({ eventType: "click", path: currentPath(), label, target: target.slice(0, 1000) });
    }

    function handleHeartbeat() {
      if (document.visibilityState !== "hidden") return;
      const now = Date.now();
      sendAnalytics({
        eventType: "heartbeat",
        path: currentPath(),
        durationMs: now - pageStartedAt.current,
        sessionDurationMs: now - sessionStartedAt.current,
      }, true);
    }

    function handlePageHide() {
      const now = Date.now();
      sendAnalytics({
        eventType: "session_end",
        path: currentPath(),
        durationMs: now - pageStartedAt.current,
        sessionDurationMs: now - sessionStartedAt.current,
      }, true);
    }

    document.addEventListener("click", handleClick, true);
    document.addEventListener("visibilitychange", handleHeartbeat);
    window.addEventListener("pagehide", handlePageHide);
    return () => {
      document.removeEventListener("click", handleClick, true);
      document.removeEventListener("visibilitychange", handleHeartbeat);
      window.removeEventListener("pagehide", handlePageHide);
    };
  }, []);

  return null;
}
