"use client";

import { useEffect, useState } from "react";
import {
  getJSON,
  postJSON,
  AgentResult,
  Customer,
  AGENT_GROUPS,
  agentDisplayName,
  tierColor,
} from "@/lib/api";
import { PageHeader, SectionLabel, Spinner } from "@/components/ui";
import AgentReport from "@/components/AgentReport";

type AgentInfo = { name: string; description: string; model_tier: string };

export default function ConsolePage() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selAgent, setSelAgent] = useState("CustomerHealthAgent");
  const [selCid, setSelCid] = useState<number | null>(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AgentResult | null>(null);

  useEffect(() => {
    getJSON<AgentInfo[]>("/api/agents").then(setAgents).catch(() => {});
    getJSON<Customer[]>("/api/customers").then((cs) => {
      setCustomers(cs);
      if (cs.length) setSelCid(cs[0].id);
    });
  }, []);

  const info = agents.find((a) => a.name === selAgent);
  const tier = info?.model_tier || "sonnet";
  const color = tierColor(tier);
  const needsCust = selAgent !== "VPChiefOfStaffAgent";

  const run = async () => {
    setRunning(true);
    try {
      setResult(
        await postJSON("/api/agents/run", {
          agent_name: selAgent,
          customer_id: needsCust ? selCid : null,
        })
      );
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Agent Console"
        subtitle="Run any agent, inspect model routing rationale, cost, and structured output in real time."
      />

      <div className="grid lg:grid-cols-[1fr_2fr] gap-5">
        <div>
          <SectionLabel>Configure</SectionLabel>
          <select
            value={selAgent}
            onChange={(e) => setSelAgent(e.target.value)}
            className="w-full bg-white border border-[#E0D8E8] rounded-xl px-3 py-2 text-[0.88rem] text-navy shadow-card outline-none mb-3"
          >
            {agents.map((a) => (
              <option key={a.name} value={a.name}>
                {AGENT_GROUPS[a.name] || "Other"} · {agentDisplayName(a.name)} —{" "}
                {a.model_tier.charAt(0).toUpperCase() + a.model_tier.slice(1)}
              </option>
            ))}
          </select>

          {needsCust ? (
            <select
              value={selCid ?? ""}
              onChange={(e) => setSelCid(Number(e.target.value))}
              className="w-full bg-white border border-[#E0D8E8] rounded-xl px-3 py-2 text-[0.88rem] text-navy shadow-card outline-none mb-3"
            >
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} · {c.risk_level === "Low" ? "Healthy" : `${c.risk_level} risk`}
                </option>
              ))}
            </select>
          ) : null}

          <div
            className="bg-white border border-line rounded-xl shadow-card px-3 py-[9px] mb-3"
            style={{ borderLeft: `3px solid ${color}` }}
          >
            <div className="text-[0.66rem] text-muted uppercase tracking-[0.10em] font-bold">Routed To</div>
            <div className="font-extrabold text-[0.95rem]" style={{ color }}>
              {tier.charAt(0).toUpperCase() + tier.slice(1)}
            </div>
            <div className="text-muted text-[0.72rem] mt-[1px]">{info?.description}</div>
            <div className="text-faint text-[0.66rem] mt-1 uppercase tracking-[0.08em]">
              {AGENT_GROUPS[selAgent] || "Other"} workflow
            </div>
          </div>

          <button
            onClick={run}
            disabled={running}
            className="w-full bg-navy text-white rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#2D1A5E] disabled:opacity-60"
          >
            {running ? "Running…" : `Run ${agentDisplayName(selAgent)}`}
          </button>

          {selAgent === "SkeptikQAAgent" ? (
            <div className="text-[0.70rem] text-muted mt-2">
              Skeptik requires a prior agent run for the selected customer.
            </div>
          ) : null}
          {selAgent === "VPChiefOfStaffAgent" ? (
            <div className="text-[0.70rem] text-muted mt-2">Portfolio-wide — no customer selection needed.</div>
          ) : null}
        </div>

        <div>
          {running ? <Spinner label={`Running ${selAgent} (${tier})…`} /> : null}
          {result && !running ? (
            <AgentReport result={result} />
          ) : !running ? (
            <div className="border-2 border-dashed border-[#D8D3C8] rounded-[14px] p-12 text-center bg-white">
              <div className="text-[0.95rem] font-semibold text-navy">Configure an agent and click Run</div>
              <div className="mt-1 text-[0.80rem] text-muted">
                Model routing rationale, cost, and confidence will appear here
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
