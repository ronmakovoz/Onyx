import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("defines the Linx executive dashboard and metadata", async () => {
  const [page, layout] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
  ]);

  assert.match(layout, /const title = "Linx Customer & Product Intelligence OS"/);
  assert.match(layout, /new URL\("\/og-v2\.png", baseUrl\)/);
  assert.match(layout, /card:\s*"summary_large_image"/);
  assert.match(page, /Executive & Product Dashboard/);
  assert.match(page, /AI EXECUTIVE SUMMARY/);
  assert.match(page, /Synthetic customer and performance data/);
  assert.doesNotMatch(page, /Your site is taking shape|react-loading-skeleton/);
});

test("defines every core workspace route", async () => {
  const routes = [
    ["accounts", /Account Intelligence/],
    ["implementation", /Implementation Command Center/],
    ["team", /CSM Performance/],
    ["growth", /Growth & Whitespace/],
    ["briefings", /Executive Briefings/],
    ["agents", /Agent Studio/],
    ["integration", /How Linx Connects/],
    ["audit", /Audit & Costs/],
    ["activity", /ActivityDashboard/],
  ];

  for (const [route, expected] of routes) {
    const page = await readFile(new URL(`../app/${route}/page.tsx`, import.meta.url), "utf8");
    assert.match(page, expected, route);
  }
});

test("adds durable, owner-only activity analytics", async () => {
  const [layout, tracker, activityPage, summaryRoute, schema, hosting] = await Promise.all([
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/components/AnalyticsTracker.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/activity/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/api/analytics/summary/route.ts", import.meta.url), "utf8"),
    readFile(new URL("../db/schema.ts", import.meta.url), "utf8"),
    readFile(new URL("../.openai/hosting.json", import.meta.url), "utf8"),
  ]);

  assert.match(layout, /<AnalyticsTracker \/>/);
  assert.match(tracker, /session_start|page_view/);
  assert.match(tracker, /document\.addEventListener\("click"/);
  assert.match(tracker, /sessionDurationMs/);
  assert.match(activityPage, /requireChatGPTUser\("\/activity"\)/);
  assert.match(activityPage, /isOwnerEmail/);
  assert.match(summaryRoute, /isOwnerEmail/);
  assert.match(schema, /analyticsSessions/);
  assert.match(schema, /analyticsEvents/);
  assert.equal(JSON.parse(hosting).d1, "DB");
});

test("keeps live Anthropic routing and demo fallback explicit", async () => {
  const [agentRoute, modeRoute, exampleEnv] = await Promise.all([
    readFile(new URL("../app/api/agent/route.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/api/mode/route.ts", import.meta.url), "utf8"),
    readFile(new URL("../.env.example", import.meta.url), "utf8"),
  ]);

  assert.match(agentRoute, /api\.anthropic\.com\/v1\/messages/);
  assert.match(agentRoute, /ANTHROPIC_API_KEY/);
  assert.doesNotMatch(agentRoute, /temperature:/);
  assert.match(agentRoute, /mockReport/);
  assert.match(modeRoute, /live:\s*available/);
  assert.match(exampleEnv, /ANTHROPIC_API_KEY=/);
});

test("separates the Linx platform foundation from customer-facing solutions", async () => {
  const [data, dashboard, accounts, growth, productMap, agentRoute] = await Promise.all([
    readFile(new URL("../app/lib/data.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/accounts/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/growth/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/integration/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/api/agent/route.ts", import.meta.url), "utf8"),
  ]);

  assert.match(data, /export const platformCapabilities/);
  assert.match(data, /export const solutionProducts/);
  assert.match(data, /Modern IGA/);
  assert.match(data, /Identity Security Posture Management/);
  assert.match(data, /Just-in-Time Access/);
  assert.match(data, /Identity Lifecycle Management/);
  assert.match(data, /Non-Human & Agentic Identity Governance/);
  assert.match(data, /AI Access Control/);
  assert.match(data, /inline MCP gateway/);
  assert.match(dashboard, /One identity platform/);
  assert.match(accounts, /Platform foundation/);
  assert.match(growth, /Solution Growth & Whitespace/);
  assert.match(productMap, /AI identities: two layers of control/);
  assert.match(productMap, /Actual integration walkthrough/);
  assert.match(productMap, /Workday → Okta → Salesforce/);
  assert.match(productMap, /OAuth 2\.0/);
  assert.match(productMap, /SCIM 2\.0/);
  assert.match(productMap, /SAML 2\.0/);
  assert.match(productMap, /SAML, SCIM, and OAuth solve different parts/);
  assert.match(productMap, /target="_blank" rel="noreferrer"/);
  assert.match(agentRoute, /LINX_PRODUCT_CONTEXT/);
  assert.match(agentRoute, /Do not describe the Identity Graph/);
  assert.match(data, /OAuth authorizes scoped API access/);
  assert.match(data, /SCIM standardizes user and group provisioning/);
  assert.match(data, /SAML supplies authentication and federation context/);
  assert.doesNotMatch(data, /export const products\s*=/);
});

test("formats model reports instead of exposing Markdown syntax", async () => {
  const [agentsPage, briefingsPage, renderer] = await Promise.all([
    readFile(new URL("../app/agents/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/briefings/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/components/ReportDocument.tsx", import.meta.url), "utf8"),
  ]);

  assert.match(agentsPage, /<ReportDocument content=\{result\} \/>/);
  assert.match(briefingsPage, /<ReportDocument content=\{result\} \/>/);
  assert.doesNotMatch(agentsPage + briefingsPage, /<pre>/);
  assert.match(renderer, /<h1|<h2|<ul|<ol|<table/);
  assert.match(renderer, /target="_blank" rel="noreferrer"/);
  assert.doesNotMatch(renderer, /dangerouslySetInnerHTML/);
});
