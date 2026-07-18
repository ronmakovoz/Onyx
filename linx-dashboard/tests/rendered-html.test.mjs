import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("defines the Linx executive dashboard and metadata", async () => {
  const [page, layout] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
  ]);

  assert.match(layout, /const title = "Linx CX Intelligence OS"/);
  assert.match(layout, /new URL\("\/og\.png", baseUrl\)/);
  assert.match(layout, /card:\s*"summary_large_image"/);
  assert.match(page, /Executive Dashboard/);
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
  ];

  for (const [route, expected] of routes) {
    const page = await readFile(new URL(`../app/${route}/page.tsx`, import.meta.url), "utf8");
    assert.match(page, expected, route);
  }
});

test("keeps live Anthropic routing and demo fallback explicit", async () => {
  const [agentRoute, modeRoute, exampleEnv] = await Promise.all([
    readFile(new URL("../app/api/agent/route.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/api/mode/route.ts", import.meta.url), "utf8"),
    readFile(new URL("../.env.example", import.meta.url), "utf8"),
  ]);

  assert.match(agentRoute, /api\.anthropic\.com\/v1\/messages/);
  assert.match(agentRoute, /ANTHROPIC_API_KEY/);
  assert.match(agentRoute, /mockReport/);
  assert.match(modeRoute, /live:\s*available/);
  assert.match(exampleEnv, /ANTHROPIC_API_KEY=/);
});
