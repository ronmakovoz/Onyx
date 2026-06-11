"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/ui";

const NAVY = "#1B1040";
const PURPLE = "#6B5CA8";
const GREEN = "#2D5A3D";
const AMBER = "#B8860B";

const SECURITY_STACK = ["SentinelOne", "Zscaler", "CrowdStrike", "Wiz"];

const CONNECT_GROUPS = [
  { label: "Platforms", items: ["Microsoft Copilot", "Salesforce", "OpenAI", "Glean"] },
  { label: "Frameworks", items: ["LangGraph", "smolagents", "LlamaIndex", "CrewAI"] },
  { label: "3rd Party", items: ["Claude", "Cohere", "Custom agents"] },
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
    body: "Onyx plugs into the security stack the client already runs — CrowdStrike, Wiz, Zscaler, SentinelOne — via read-only API. No endpoint agents, no code changes. Within hours it builds a complete inventory of every AI agent in the environment.",
  },
  {
    n: "2",
    title: "Connect To Agents",
    body: "Using the agent inventory from Step 1, Onyx establishes direct connections to the agents themselves — platforms, frameworks, and 3rd-party models — via read-only API or optional gateway for in-line guardrails.",
  },
  {
    n: "3",
    title: "Analyze in Cloud Backend",
    body: "Telemetry from both steps flows into the Onyx Cloud Backend: ingestion and normalization, configuration analysis, guardrail evaluation, and chain-of-thought inspection — all in real time.",
  },
  {
    n: "4",
    title: "Act with Guardian Agent",
    body: "The Guardian Agent surfaces protections back to the client: discovery maps, runtime alerts, posture scores, governance policies, honeypots, red-team findings, and continuous compliance evidence.",
  },
];

function flowPath(x1: number, y1: number, x2: number, y2: number) {
  const mx = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
}

// Vertical S-curve from Step 1 down into Step 2 left side
function vBridge(x: number, y1: number, y2: number) {
  const my = (y1 + y2) / 2;
  return `M ${x} ${y1} C ${x} ${my}, ${x} ${my}, ${x} ${y2}`;
}

export default function IntegrationPage() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setStep((s) => (s + 1) % STEPS.length), 5000);
    return () => clearInterval(t);
  }, []);

  const BX = 450, BW = 220, BY = 100, BH = 310;
  const bMidY = BY + BH / 2;

  // Step 1 box bottom, Step 2 box top
  const s1Bottom = 160;
  const s2Top = 190;
  const bridgeX = 185; // midpoint of left boxes

  return (
    <div>
      <PageHeader
        title="How Onyx Integrates"
        subtitle="A unified platform to secure agentic AI — the security stack reveals which agents exist, then Onyx connects to them, analyzes everything, and protects continuously"
      />

      <div className="bg-white border border-line rounded-xl shadow-card p-4 mb-5 overflow-x-auto">
        <svg viewBox="0 0 1040 560" className="w-full min-w-[880px]" role="img" aria-label="Onyx unified platform architecture animation">
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
            <filter id="glow-amber" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
            <marker id="arrow" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
              <path d="M0,0 L7,3.5 L0,7 Z" fill="#C9A83C" />
            </marker>
          </defs>

          {/* ══════════════════════════════════════════
              STEP 1 BOX — Discover Agents
          ══════════════════════════════════════════ */}
          <rect x="20" y="28" width="350" height="132" rx="12" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="38" y="52" fontSize="13" fontWeight="800" fill={NAVY}>Step 1: Discover Agents</text>

          {/* Security stack inner box */}
          <rect x="36" y="64" width="318" height="82" rx="9" fill="#fff" stroke="#E4E0D8" />
          <text x="52" y="83" fontSize="10" fontWeight="700" fill="#8A8475" fontFamily="monospace">Security Stack  →  reads your existing tools</text>
          {SECURITY_STACK.map((s, i) => (
            <g key={s}>
              <rect x={52 + i * 76} y={92} width="70" height="38" rx="7" fill="#F4F1EB" stroke="#E4E0D8" />
              <text x={87 + i * 76} y={116} textAnchor="middle" fontSize="9" fontWeight="700" fill={NAVY}>{s}</text>
              {/* Each security tool pulses to show it's being read */}
              <circle cx={87 + i * 76} cy={111 + 38} r="3" fill="none" stroke={PURPLE} strokeWidth="1.2">
                <animate attributeName="r" values="3;8;3" dur="2.5s" repeatCount="indefinite" begin={`${i * 0.5}s`} />
                <animate attributeName="opacity" values="0.8;0;0.8" dur="2.5s" repeatCount="indefinite" begin={`${i * 0.5}s`} />
              </circle>
            </g>
          ))}

          {/* ══════════════════════════════════════════
              BRIDGE: Step 1 → Step 2 (discovery feeds connection)
          ══════════════════════════════════════════ */}
          {/* Vertical bridge line with arrow */}
          <line x1={bridgeX} y1={s1Bottom} x2={bridgeX} y2={s2Top} stroke="#C9A83C" strokeWidth="2" markerEnd="url(#arrow)" />
          {/* Label */}
          <rect x="196" y="164" width="148" height="22" rx="6" fill="#FFFAE8" stroke="#E8D98A" />
          <text x="270" y="179" textAnchor="middle" fontSize="9" fontWeight="700" fill={AMBER}>
            Agents discovered — now connect
          </text>
          {/* Animated discovery pulse travelling down the bridge */}
          <circle r="5" fill={AMBER} filter="url(#glow-amber)">
            <animateMotion dur="1.8s" repeatCount="indefinite"
              path={`M ${bridgeX} ${s1Bottom} L ${bridgeX} ${s2Top}`} />
          </circle>

          {/* ══════════════════════════════════════════
              STEP 2 BOX — Connect To Agents
          ══════════════════════════════════════════ */}
          <rect x="20" y="190" width="350" height="346" rx="12" fill="#FAF8F4" stroke="#C9A83C" strokeWidth="1.5" strokeDasharray="6 4" />
          <text x="38" y="214" fontSize="13" fontWeight="800" fill={NAVY}>Step 2: Connect To Agents</text>
          {/* "informed by Step 1" callout */}
          <text x="38" y="228" fontSize="9" fill={AMBER} fontWeight="600">↑ inventory from Step 1 tells Onyx exactly what to connect to</text>

          {CONNECT_GROUPS.map((g, gi) => (
            <g key={g.label}>
              <rect x="36" y={238 + gi * 96} width="318" height="86" rx="9" fill="#fff" stroke="#E4E0D8" />
              <text x="52" y={257 + gi * 96} fontSize="10" fontWeight="700" fill="#8A8475" fontFamily="monospace">{g.label}</text>
              {g.items.map((it, ii) => (
                <g key={it}>
                  <rect x={52 + (ii % 2) * 152} y={265 + gi * 96 + Math.floor(ii / 2) * 27}
                    width="144" height="22" rx="6" fill="#F4F1EB" stroke="#E4E0D8" />
                  <text x={124 + (ii % 2) * 152} y={280 + gi * 96 + Math.floor(ii / 2) * 27}
                    textAnchor="middle" fontSize="9" fontWeight="700" fill={NAVY}>{it}</text>
                </g>
              ))}
            </g>
          ))}

          {/* ══════════════════════════════════════════
              FLOWS → Onyx Cloud Backend
          ══════════════════════════════════════════ */}
          {/* Step 1 → Backend */}
          {(() => {
            const p = flowPath(370, 115, BX, bMidY - 70);
            return (
              <g>
                <path d={p} fill="none" stroke="#DDD6EC" strokeWidth="1.5" />
                <text x="378" y="102" fontSize="8.5" fill="#8A8475" fontFamily="monospace">API (Read-Only)</text>
                {/* Two packets staggered — showing continuous discovery data */}
                <circle r="5" fill={PURPLE} filter="url(#glow)">
                  <animateMotion dur="3s" repeatCount="indefinite" path={p} />
                </circle>
                <circle r="5" fill={PURPLE} filter="url(#glow)">
                  <animateMotion dur="3s" repeatCount="indefinite" path={p} begin="1.5s" />
                </circle>
              </g>
            );
          })()}

          {/* Step 2 → Backend — packets begin only AFTER amber bridge fires (begin offset) */}
          {(() => {
            const p = flowPath(370, 365, BX, bMidY + 50);
            return (
              <g>
                <path d={p} fill="none" stroke="#DDD6EC" strokeWidth="1.5" />
                <text x="374" y="420" fontSize="8.5" fill="#8A8475" fontFamily="monospace">API (Read-Only)</text>
                <text x="374" y="432" fontSize="8.5" fill="#8A8475" fontFamily="monospace">- or - Gateway</text>
                {/* Packets start slightly delayed relative to Step 1 to show dependency */}
                <circle r="5" fill={PURPLE} filter="url(#glow)">
                  <animateMotion dur="2.6s" repeatCount="indefinite" path={p} begin="0.9s" />
                </circle>
                <circle r="5" fill={AMBER} filter="url(#glow-amber)" opacity="0.9">
                  <animateMotion dur="2.6s" repeatCount="indefinite" path={p} begin="2.1s" />
                </circle>
              </g>
            );
          })()}

          {/* ══════════════════════════════════════════
              ONYX CLOUD BACKEND
          ══════════════════════════════════════════ */}
          <rect x={BX} y={BY} width={BW} height={BH} rx="16" fill="#F3EFFC" stroke="#C9B8EE" strokeWidth="1.5" />
          <text x={BX + BW / 2} y={BY - 16} textAnchor="middle" fontSize="12" fontWeight="900" fill={NAVY} letterSpacing="0.5">
            ONYX <tspan fontWeight="600">Cloud Backend</tspan>
          </text>
          {BACKEND.map((b, i) => (
            <g key={b}>
              <rect x={BX + 16} y={BY + 20 + i * 70} width={BW - 32} height="56" rx="9" fill="#fff" stroke="#DDD0F2" />
              <text x={BX + BW / 2} y={BY + 52 + i * 70} textAnchor="middle" fontSize="10.5" fontWeight="700" fill={NAVY}>{b}</text>
              {/* Pulse inside each layer shows processing */}
              <rect x={BX + 16} y={BY + 20 + i * 70} width={BW - 32} height="56" rx="9" fill="none" stroke={PURPLE} strokeWidth="1.5">
                <animate attributeName="opacity" values="0;0.4;0" dur="3s" repeatCount="indefinite" begin={`${i * 0.7}s`} />
              </rect>
            </g>
          ))}

          {/* ══════════════════════════════════════════
              Backend → Guardian flows
          ══════════════════════════════════════════ */}
          {GUARDIAN.map((gd, i) => {
            const gy = 44 + i * 68;
            const p = flowPath(BX + BW, bMidY - 100 + i * 38, 770, gy + 25);
            return (
              <g key={gd.label}>
                <path d={p} fill="none" stroke="#CFE0D5" strokeWidth="1.2" />
                <circle r="4.5" fill={GREEN} filter="url(#glow)">
                  <animateMotion dur={`${2.4 + i * 0.25}s`} repeatCount="indefinite" path={p} begin={`${0.6 + i * 0.35}s`} />
                </circle>
              </g>
            );
          })}

          {/* ══════════════════════════════════════════
              GUARDIAN AGENT
          ══════════════════════════════════════════ */}
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

          {/* ══════════════════════════════════════════
              LEGEND
          ══════════════════════════════════════════ */}
          <g fontSize="10" fill="#8A8475">
            <circle cx="24" cy="548" r="5" fill={PURPLE} />
            <text x="36" y="552">Telemetry in</text>
            <circle cx="120" cy="548" r="5" fill={AMBER} />
            <text x="132" y="552">Discovery → connection signal</text>
            <circle cx="320" cy="548" r="5" fill={GREEN} />
            <text x="332" y="552">Guardian protections out</text>
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
        Read-only API integrations by default — no endpoint agents, no code changes. Optional gateway mode for in-line guardrails.
      </div>
    </div>
  );
}
