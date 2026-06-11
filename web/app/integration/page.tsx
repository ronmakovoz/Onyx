"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/ui";

const NAVY = "#1B1040";
const PURPLE = "#6B5CA8";
const GREEN = "#2D5A3D";

// Step 1 — discover agents through the existing security stack (read-only API)
const SECURITY_STACK = ["SentinelOne", "Zscaler", "CrowdStrike", "Wiz"];

// Step 2 — connect to the agents themselves
const CONNECT_GROUPS = [
  { label: "Platforms", items: ["Microsoft Copilot", "Salesforce", "OpenAI", "Glean"] },
  { label: "Frameworks", items: ["LangGraph", "smolagents", "LlamaIndex", "CrewAI"] },
  { label: "3rd Party", items: ["Claude", "Cohere", "Custom agents"] },
];

// Onyx Cloud Backend processing
const BACKEND = [
  "Ingestion & Normalization",
  "Configuration Analysis",
  "Guardrails",
  "Chain-of-Thought Evaluation",
];

// Guardian Agent capabilities (right column) — colors echo the brand diagram
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
    body: "Onyx plugs into the security stack the client already runs — CrowdStrike, Wiz, Zscaler, SentinelOne — via read-only API integration. No endpoint agents, no traffic rerouting: Onyx sees every AI agent the existing tooling can see, instantly.",
  },
  {
    n: "2",
    title: "Connect To Agents",
    body: "Onyx then connects to the agents themselves — platforms like Microsoft Copilot, Salesforce, and Glean; frameworks like LangGraph, smolagents, and LlamaIndex; and 3rd-party models like Claude — via read-only API or an optional gateway.",
  },
  {
    n: "3",
    title: "Analyze in the Cloud Backend",
    body: "Everything lands in the Onyx Cloud Backend: telemetry is ingested and normalized, agent configurations are analyzed, guardrails are applied, and agent reasoning is checked with chain-of-thought evaluation.",
  },
  {
    n: "4",
    title: "Act with the Guardian Agent",
    body: "The Guardian Agent turns analysis into protection: discovery, runtime protection, posture management, governance, honeypots, red-teaming, and continuous audit & compliance evidence.",
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

  // Backend box geometry
  const BX = 430, BW = 230, BY = 130, BH = 280;
  const bMidY = BY + BH / 2;

  return (
    <div>
      <PageHeader
        title="How Onyx Integrates"
        subtitle="A unified platform to secure agentic AI — discover agents through the existing security stack, connect to them directly, analyze in the cloud backend, and protect with the Guardian Agent"
      />

      <div className="bg-white border border-line rounded-xl shadow-card p-4 mb-5 overflow-x-auto">
        <svg viewBox="0 0 1000 540" className="w-full min-w-[860px]" role="img" aria-label="Onyx unified platform architecture animation">
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* ===== Step 1: Discover Agents ===== */}
          <rect x="20" y="30" width="330" height="130" rx="12" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="36" y="54" fontSize="13" fontWeight="800" fill={NAVY}>Step 1: Discover Agents</text>
          <rect x="36" y="66" width="298" height="78" rx="9" fill="#fff" stroke="#E4E0D8" />
          <text x="50" y="86" fontSize="10" fontWeight="700" fill="#8A8475" fontFamily="monospace">Security Stack</text>
          {SECURITY_STACK.map((s, i) => (
            <g key={s}>
              <rect x={50 + i * 70} y={96} width="64" height="32" rx="7" fill="#F4F1EB" stroke="#E4E0D8" />
              <text x={82 + i * 70} y={115} textAnchor="middle" fontSize="8.5" fontWeight="700" fill={NAVY}>{s}</text>
            </g>
          ))}

          {/* ===== Step 2: Connect To Agents ===== */}
          <rect x="20" y="180" width="330" height="330" rx="12" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="36" y="204" fontSize="13" fontWeight="800" fill={NAVY}>Step 2: Connect To Agents</text>
          {CONNECT_GROUPS.map((g, gi) => (
            <g key={g.label}>
              <rect x="36" y={216 + gi * 94} width="298" height="84" rx="9" fill="#fff" stroke="#E4E0D8" />
              <text x="50" y={236 + gi * 94} fontSize="10" fontWeight="700" fill="#8A8475" fontFamily="monospace">{g.label}</text>
              {g.items.map((it, ii) => (
                <g key={it}>
                  <rect x={50 + (ii % 2) * 138} y={244 + gi * 94 + Math.floor(ii / 2) * 26} width="130" height="22" rx="6" fill="#F4F1EB" stroke="#E4E0D8" />
                  <text x={115 + (ii % 2) * 138} y={259 + gi * 94 + Math.floor(ii / 2) * 26} textAnchor="middle" fontSize="9" fontWeight="700" fill={NAVY}>{it}</text>
                </g>
              ))}
            </g>
          ))}

          {/* ===== Connection labels + animated flows into the backend ===== */}
          {/* Step 1 -> backend (read-only) */}
          {(() => {
            const p = flowPath(350, 110, BX, bMidY - 60);
            return (
              <g>
                <path d={p} fill="none" stroke="#DDD6EC" strokeWidth="1.5" />
                <text x="368" y="100" fontSize="9" fill="#8A8475" fontFamily="monospace">API Integration (Read-Only)</text>
                <circle r="5" fill={PURPLE} filter="url(#glow)">
                  <animateMotion dur="2.8s" repeatCount="indefinite" path={p} />
                </circle>
              </g>
            );
          })()}
          {/* Step 2 -> backend (read-only or gateway) */}
          {(() => {
            const p = flowPath(350, 345, BX, bMidY + 40);
            return (
              <g>
                <path d={p} fill="none" stroke="#DDD6EC" strokeWidth="1.5" />
                <text x="360" y="394" fontSize="9" fill="#8A8475" fontFamily="monospace">API Integration (Read-Only)</text>
                <text x="360" y="406" fontSize="9" fill="#8A8475" fontFamily="monospace">- or - Gateway</text>
                <circle r="5" fill={PURPLE} filter="url(#glow)">
                  <animateMotion dur="2.4s" repeatCount="indefinite" path={p} begin="0.9s" />
                </circle>
                <circle r="5" fill={PURPLE} filter="url(#glow)">
                  <animateMotion dur="2.4s" repeatCount="indefinite" path={p} begin="2.1s" />
                </circle>
              </g>
            );
          })()}

          {/* ===== Onyx Cloud Backend ===== */}
          <rect x={BX} y={BY} width={BW} height={BH} rx="16" fill="#F3EFFC" stroke="#C9B8EE" strokeWidth="1.5" />
          <text x={BX + BW / 2} y={BY - 14} textAnchor="middle" fontSize="13" fontWeight="900" fill={NAVY} letterSpacing="0.5">
            ONYX <tspan fontWeight="600">Cloud Backend</tspan>
          </text>
          {BACKEND.map((b, i) => (
            <g key={b}>
              <rect x={BX + 18} y={BY + 24 + i * 62} width={BW - 36} height="48" rx="9" fill="#fff" stroke="#DDD0F2" />
              <text x={BX + BW / 2} y={BY + 52 + i * 62} textAnchor="middle" fontSize="10.5" fontWeight="700" fill={NAVY}>
                {b}
              </text>
            </g>
          ))}

          {/* ===== Backend -> Guardian flows ===== */}
          {GUARDIAN.map((gd, i) => {
            const gy = 56 + i * 64;
            const p = flowPath(BX + BW, bMidY - 90 + i * 30, 740, gy + 22);
            return (
              <g key={gd.label}>
                <path d={p} fill="none" stroke="#CFE0D5" strokeWidth="1.2" />
                <circle r="4.5" fill={GREEN} filter="url(#glow)">
                  <animateMotion dur={`${2.2 + i * 0.3}s`} repeatCount="indefinite" path={p} begin={`${0.6 + i * 0.4}s`} />
                </circle>
              </g>
            );
          })}

          {/* ===== Onyx Guardian Agent ===== */}
          <rect x="740" y="26" width="240" height="488" rx="14" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="860" y="48" textAnchor="middle" fontSize="12" fontWeight="900" fill={NAVY} letterSpacing="0.5">
            ONYX <tspan fontWeight="600">Guardian Agent</tspan>
          </text>
          {GUARDIAN.map((gd, i) => (
            <g key={gd.label}>
              <rect x="756" y={56 + i * 64} width="208" height="50" rx="10" fill={gd.bg} stroke={gd.border} strokeWidth="1.5" />
              <text x="860" y={86 + i * 64} textAnchor="middle" fontSize="11.5" fontWeight="700" fill={NAVY}>
                {gd.label}
              </text>
            </g>
          ))}

          {/* Legend */}
          <g fontSize="10" fill="#8A8475">
            <circle cx="40" cy="528" r="5" fill={PURPLE} />
            <text x="52" y="532">Agent telemetry &amp; configs in</text>
            <circle cx="220" cy="528" r="5" fill={GREEN} />
            <text x="232" y="532">Guardian protections out</text>
          </g>
        </svg>
      </div>

      {/* Auto-cycling step narrative */}
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
