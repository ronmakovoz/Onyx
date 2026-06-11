"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/ui";

const NAVY = "#1B1040";
const PURPLE = "#6B5CA8";
const GREEN = "#2D5A3D";
const TEAL = "#1B6B72";

const SECURITY_STACK = ["SentinelOne", "Zscaler", "CrowdStrike", "Wiz"];

const CONNECT_GROUPS = [
  {
    label: "Platforms",
    items: ["Microsoft Copilot", "Salesforce", "OpenAI", "Glean"],
    payload: "agent configs, permissions, usage",
    mode: "api" as const,
  },
  {
    label: "Frameworks",
    items: ["LangGraph", "smolagents", "LlamaIndex", "CrewAI"],
    payload: "traces, tool calls, reasoning steps",
    mode: "api" as const,
  },
  {
    label: "3rd Party",
    items: ["Claude", "Cohere", "Custom agents"],
    payload: "prompts & responses, in-line",
    mode: "gateway" as const,
  },
];

const BACKEND = [
  "Ingestion & Normalization",
  "Configuration Analysis",
  "Guardrails",
  "Chain-of-Thought Evaluation",
];

const GUARDIAN = [
  { label: "Discovery", bg: "#FDE8EF", border: "#F3B8CD" },
  { label: "Runtime Protection", bg: "#E2F6F8", border: "#A8DEE4" },
  { label: "Posture Management", bg: "#E8F4EA", border: "#B5D9BC" },
  { label: "Governance", bg: "#FDF3DC", border: "#EAD08F" },
  { label: "Honeypot", bg: "#FBE8D8", border: "#EDBE94" },
  { label: "Red-Teaming", bg: "#FBE3E1", border: "#EFB0AB" },
  { label: "Audit & Compliance", bg: "#FFFFFF", border: "#D8D3C8" },
];

const STEPS = [
  {
    n: "1",
    title: "Discover Agents",
    body: "Onyx authenticates to the security tools the client already runs — CrowdStrike, Wiz, Zscaler, SentinelOne — with read-only API credentials. It pulls endpoint inventories, network logs, and cloud posture findings, and from those identifies every AI agent running in the environment. Nothing is installed, nothing is rerouted.",
  },
  {
    n: "2",
    title: "Connect To Agents",
    body: "Each agent surface connects differently: platforms (Copilot, Salesforce, Glean) expose admin APIs for configs and permissions; frameworks (LangGraph, LlamaIndex) emit traces and tool-call telemetry; 3rd-party model traffic (Claude, Cohere) can optionally route through the Onyx gateway for in-line inspection.",
  },
  {
    n: "3",
    title: "Analyze in Cloud Backend",
    body: "All of it lands in the Onyx Cloud Backend: telemetry is normalized into one schema, agent configurations are analyzed for risky permissions, guardrails evaluate every interaction, and chain-of-thought evaluation inspects agent reasoning for drift or manipulation.",
  },
  {
    n: "4",
    title: "Act with Guardian Agent",
    body: "The Guardian Agent turns analysis into protection: live discovery maps, runtime alerts, posture scores, governance policies, honeypots, red-team findings, and continuous audit & compliance evidence.",
  },
];

function flowPath(x1: number, y1: number, x2: number, y2: number) {
  const mx = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
}

export default function IntegrationPage() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setStep((s) => (s + 1) % STEPS.length), 5000);
    return () => clearInterval(t);
  }, []);

  const BX = 470, BW = 220, BY = 100, BH = 310;

  return (
    <div>
      <PageHeader
        title="How Onyx Integrates"
        subtitle="A unified platform to secure agentic AI — two independent integration paths into the Onyx Cloud Backend, one Guardian Agent protecting everything"
      />

      <div className="bg-white border border-line rounded-xl shadow-card p-4 mb-5 overflow-x-auto">
        <svg viewBox="0 0 1040 560" className="w-full min-w-[880px]" role="img" aria-label="Onyx unified platform architecture animation">
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>

          {/* ===== Step 1: Discover Agents ===== */}
          <rect x="20" y="28" width="350" height="148" rx="12" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="38" y="52" fontSize="13" fontWeight="800" fill={NAVY}>Step 1: Discover Agents</text>
          <rect x="36" y="64" width="318" height="98" rx="9" fill="#fff" stroke="#E4E0D8" />
          <text x="52" y="83" fontSize="10" fontWeight="700" fill="#8A8475" fontFamily="monospace">Security Stack</text>
          {SECURITY_STACK.map((s, i) => (
            <g key={s}>
              <rect x={52 + i * 76} y={92} width="70" height="38" rx="7" fill="#F4F1EB" stroke="#E4E0D8" />
              <text x={87 + i * 76} y={116} textAnchor="middle" fontSize="9" fontWeight="700" fill={NAVY}>{s}</text>
            </g>
          ))}
          <text x="52" y="150" fontSize="8.5" fill="#8A8475">
            endpoint inventory · network logs · cloud posture findings
          </text>

          {/* Step 1 → Backend: one line per security tool, converging */}
          {SECURITY_STACK.map((s, i) => {
            // lines exit the right side of the step-1 box at staggered heights
            const exitY = 70 + i * 24;
            const path = flowPath(370, exitY + 30, BX, BY + 40 + i * 18);
            return (
              <g key={s}>
                <path d={path} fill="none" stroke="#DDD6EC" strokeWidth="1.2" strokeDasharray="4 3" />
                <circle r="4" fill={PURPLE} filter="url(#glow)">
                  <animateMotion dur={`${2.6 + i * 0.4}s`} repeatCount="indefinite" path={path} begin={`${i * 0.6}s`} />
                </circle>
              </g>
            );
          })}
          <text x="378" y="64" fontSize="8.5" fill={PURPLE} fontFamily="monospace" fontWeight="700">read-only API</text>
          <text x="378" y="76" fontSize="8" fill="#8A8475" fontFamily="monospace">agent inventory + findings</text>

          {/* ===== Step 2: Connect To Agents ===== */}
          <rect x="20" y="196" width="350" height="340" rx="12" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="38" y="220" fontSize="13" fontWeight="800" fill={NAVY}>Step 2: Connect To Agents</text>
          {CONNECT_GROUPS.map((g, gi) => (
            <g key={g.label}>
              <rect x="36" y={232 + gi * 98} width="318" height="88" rx="9" fill="#fff" stroke="#E4E0D8" />
              <text x="52" y={251 + gi * 98} fontSize="10" fontWeight="700" fill="#8A8475" fontFamily="monospace">{g.label}</text>
              {g.items.map((it, ii) => (
                <g key={it}>
                  <rect x={52 + (ii % 2) * 152} y={259 + gi * 98 + Math.floor(ii / 2) * 27}
                    width="144" height="22" rx="6" fill="#F4F1EB" stroke="#E4E0D8" />
                  <text x={124 + (ii % 2) * 152} y={274 + gi * 98 + Math.floor(ii / 2) * 27}
                    textAnchor="middle" fontSize="9" fontWeight="700" fill={NAVY}>{it}</text>
                </g>
              ))}
            </g>
          ))}

          {/* Step 2 → Backend: one labeled line per group */}
          {CONNECT_GROUPS.map((g, gi) => {
            const exitY = 276 + gi * 98;
            const entryY = BY + 150 + gi * 45;
            const path = flowPath(370, exitY, BX, entryY);
            const isGateway = g.mode === "gateway";
            return (
              <g key={g.label}>
                <path
                  d={path}
                  fill="none"
                  stroke={isGateway ? "#BFDDE0" : "#DDD6EC"}
                  strokeWidth={isGateway ? 2.2 : 1.2}
                  strokeDasharray={isGateway ? undefined : "4 3"}
                />
                <circle r="4.5" fill={isGateway ? TEAL : PURPLE} filter="url(#glow)">
                  <animateMotion dur={`${2.4 + gi * 0.5}s`} repeatCount="indefinite" path={path} begin={`${gi * 0.8}s`} />
                </circle>
                {isGateway ? (
                  <circle r="4.5" fill={TEAL} filter="url(#glow)">
                    <animateMotion dur={`${2.4 + gi * 0.5}s`} repeatCount="indefinite" path={path} begin={`${gi * 0.8 + 1.2}s`} />
                  </circle>
                ) : null}
              </g>
            );
          })}
          {/* payload labels for step 2 lines, stacked clear of the lines */}
          <text x="378" y="262" fontSize="8" fill="#8A8475" fontFamily="monospace">configs · permissions · usage</text>
          <text x="378" y="354" fontSize="8" fill="#8A8475" fontFamily="monospace">traces · tool calls · reasoning</text>
          <text x="378" y="452" fontSize="8.5" fill={TEAL} fontFamily="monospace" fontWeight="700">gateway (in-line)</text>
          <text x="378" y="464" fontSize="8" fill="#8A8475" fontFamily="monospace">prompts &amp; responses</text>

          {/* ===== Onyx Cloud Backend ===== */}
          <rect x={BX} y={BY} width={BW} height={BH} rx="16" fill="#F3EFFC" stroke="#C9B8EE" strokeWidth="1.5" />
          <text x={BX + BW / 2} y={BY - 16} textAnchor="middle" fontSize="12" fontWeight="900" fill={NAVY} letterSpacing="0.5">
            ONYX <tspan fontWeight="600">Cloud Backend</tspan>
          </text>
          {BACKEND.map((b, i) => (
            <g key={b}>
              <rect x={BX + 16} y={BY + 20 + i * 70} width={BW - 32} height="56" rx="9" fill="#fff" stroke="#DDD0F2" />
              <text x={BX + BW / 2} y={BY + 52 + i * 70} textAnchor="middle" fontSize="10.5" fontWeight="700" fill={NAVY}>{b}</text>
              <rect x={BX + 16} y={BY + 20 + i * 70} width={BW - 32} height="56" rx="9" fill="none" stroke={PURPLE} strokeWidth="1.5">
                <animate attributeName="opacity" values="0;0.4;0" dur="3s" repeatCount="indefinite" begin={`${i * 0.7}s`} />
              </rect>
            </g>
          ))}

          {/* Backend → Guardian flows */}
          {GUARDIAN.map((gd, i) => {
            const gy = 44 + i * 68;
            const p = flowPath(BX + BW, BY + 60 + i * 30, 770, gy + 25);
            return (
              <g key={gd.label}>
                <path d={p} fill="none" stroke="#CFE0D5" strokeWidth="1.2" />
                <circle r="4.5" fill={GREEN} filter="url(#glow)">
                  <animateMotion dur={`${2.4 + i * 0.25}s`} repeatCount="indefinite" path={p} begin={`${0.6 + i * 0.35}s`} />
                </circle>
              </g>
            );
          })}

          {/* ===== Guardian Agent ===== */}
          <rect x="770" y="24" width="250" height="510" rx="14" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="895" y="46" textAnchor="middle" fontSize="12" fontWeight="900" fill={NAVY} letterSpacing="0.5">
            ONYX <tspan fontWeight="600">Guardian Agent</tspan>
          </text>
          {GUARDIAN.map((gd, i) => (
            <g key={gd.label}>
              <rect x="784" y={56 + i * 68} width="222" height="54" rx="10" fill={gd.bg} stroke={gd.border} strokeWidth="1.5" />
              <text x="895" y={87 + i * 68} textAnchor="middle" fontSize="11.5" fontWeight="700" fill={NAVY}>{gd.label}</text>
            </g>
          ))}

          {/* Legend */}
          <g fontSize="10" fill="#8A8475">
            <line x1="24" y1="548" x2="48" y2="548" stroke="#DDD6EC" strokeWidth="1.5" strokeDasharray="4 3" />
            <text x="54" y="552">Read-only API (nothing installed, nothing rerouted)</text>
            <line x1="330" y1="548" x2="354" y2="548" stroke="#BFDDE0" strokeWidth="2.5" />
            <text x="360" y="552">Gateway — traffic flows through Onyx in-line</text>
            <circle cx="620" cy="548" r="5" fill={GREEN} />
            <text x="632" y="552">Guardian protections out</text>
          </g>
        </svg>
      </div>

      {/* Step cards */}
      <div className="grid md:grid-cols-4 gap-3">
        {STEPS.map((s, i) => (
          <button
            key={s.n}
            onClick={() => setStep(i)}
            className={`text-left rounded-xl border p-4 transition-all ${
              step === i
                ? "bg-navy text-white border-navy shadow-card"
                : "bg-white text-ink border-line hover:border-[#B9AEE0]"
            }`}
          >
            <div className={`text-[0.62rem] font-bold uppercase tracking-[0.12em] mb-1 ${step === i ? "text-[#B9AEE0]" : "text-muted"}`}>
              Step {s.n}
            </div>
            <div className={`text-[1rem] font-extrabold mb-2 ${step === i ? "text-white" : "text-navy"}`}>
              {s.title}
            </div>
            <div className={`text-[0.74rem] leading-relaxed ${step === i ? "text-[#E8E3F5]" : "text-muted"}`}>
              {s.body}
            </div>
          </button>
        ))}
      </div>

      <div className="mt-4 text-[0.72rem] text-muted px-1">
        Read-only API integrations by default — no endpoint agents, no code changes. Optional gateway mode for in-line guardrails on model traffic.
      </div>
    </div>
  );
}
