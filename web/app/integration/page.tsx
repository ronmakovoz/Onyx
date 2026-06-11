"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/ui";

const NAVY = "#1B1040";
const GREEN = "#2D5A3D";
const RED = "#9B2335";
const AMBER = "#B8860B";
const PURPLE = "#6B5CA8";

// Client-side sources (left), Onyx in the middle, model providers (right)
const SOURCES = [
  { id: "apps", label: "Internal Apps", sub: "LLM features in product", y: 70 },
  { id: "agents", label: "AI Agents", sub: "autonomous workflows", y: 150 },
  { id: "copilots", label: "Employee Copilots", sub: "chat, code, docs", y: 230 },
  { id: "mcp", label: "MCP Servers", sub: "tools & connectors", y: 310 },
  { id: "shadow", label: "Shadow AI", sub: "unsanctioned usage", y: 390 },
];

const PROVIDERS = [
  { id: "anthropic", label: "Anthropic", y: 110 },
  { id: "openai", label: "OpenAI / Azure", y: 190 },
  { id: "bedrock", label: "AWS Bedrock", y: 270 },
  { id: "selfhosted", label: "Self-hosted Models", y: 350 },
];

const STEPS = [
  {
    n: "1",
    title: "Discover",
    body: "Onyx deploys as a lightweight gateway in the client's VPC — no agents on endpoints, no code changes. Within hours it maps every app, agent, copilot, and MCP server talking to an LLM, including shadow AI nobody knew about.",
  },
  {
    n: "2",
    title: "Route",
    body: "AI traffic flows through the Onyx gateway. One integration point replaces dozens of direct provider connections — with model routing, failover, and cost controls built in.",
  },
  {
    n: "3",
    title: "Protect",
    body: "Every request and response is inspected in-line: prompt injection, data exfiltration, jailbreaks, and policy violations are blocked in real time — before they reach the model or leave the environment.",
  },
  {
    n: "4",
    title: "Prove",
    body: "Every interaction is logged with full lineage. Compliance evidence for SOC 2, ISO 42001, and the EU AI Act is generated continuously — audits go from weeks to hours.",
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

  // Onyx box geometry
  const OX = 390, OW = 220, OY = 60, OH = 360;
  const onyxMidY = OY + OH / 2;

  return (
    <div>
      <PageHeader
        title="How Onyx Integrates"
        subtitle="One gateway between everything that calls an LLM and every model it calls — discovered, routed, protected, and proven"
      />

      <div className="bg-white border border-line rounded-xl shadow-card p-4 mb-5 overflow-x-auto">
        <svg viewBox="0 0 1000 480" className="w-full min-w-[820px]" role="img" aria-label="Onyx integration architecture animation">
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Client environment boundary */}
          <rect x="20" y="30" width="290" height="420" rx="14" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="165" y="52" textAnchor="middle" fontSize="11" fontWeight="800" fill="#8A8475" letterSpacing="1.5">
            CLIENT ENVIRONMENT
          </text>

          {/* Provider zone */}
          <rect x="700" y="60" width="280" height="350" rx="14" fill="#FAF8F4" stroke="#D8D3C8" strokeDasharray="6 4" />
          <text x="840" y="84" textAnchor="middle" fontSize="11" fontWeight="800" fill="#8A8475" letterSpacing="1.5">
            MODEL PROVIDERS
          </text>

          {/* Flow paths: sources -> Onyx */}
          {SOURCES.map((s, i) => {
            const isThreat = s.id === "shadow";
            const p = flowPath(255, s.y + 18, isThreat ? OX + 4 : OX, isThreat ? onyxMidY + 110 : onyxMidY - 80 + i * 40);
            return (
              <g key={s.id}>
                <path d={p} fill="none" stroke={isThreat ? "#E8C8CE" : "#DDD6EC"} strokeWidth="1.5" />
                {/* travelling packet */}
                <circle r="5" fill={isThreat ? RED : PURPLE} filter="url(#glow)">
                  <animateMotion dur={`${2.6 + i * 0.5}s`} repeatCount="indefinite" path={p} begin={`${i * 0.6}s`} />
                  {isThreat ? (
                    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.92;1" dur={`${2.6 + i * 0.5}s`} repeatCount="indefinite" begin={`${i * 0.6}s`} />
                  ) : null}
                </circle>
              </g>
            );
          })}

          {/* blocked burst where shadow AI hits the Onyx wall */}
          <g>
            <circle cx={OX + 4} cy={onyxMidY + 110} r="9" fill="none" stroke={RED} strokeWidth="2">
              <animate attributeName="r" values="4;14" dur="1.4s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.9;0" dur="1.4s" repeatCount="indefinite" />
            </circle>
            <text x={OX + 22} y={onyxMidY + 132} fontSize="10" fontWeight="800" fill={RED}>
              ✕ THREAT BLOCKED
            </text>
          </g>

          {/* Flow paths: Onyx -> providers */}
          {PROVIDERS.map((pr, i) => {
            const p = flowPath(OX + OW, onyxMidY - 60 + i * 40, 715, pr.y + 16);
            return (
              <g key={pr.id}>
                <path d={p} fill="none" stroke="#CFE0D5" strokeWidth="1.5" />
                <circle r="5" fill={GREEN} filter="url(#glow)">
                  <animateMotion dur={`${2.4 + i * 0.4}s`} repeatCount="indefinite" path={p} begin={`${0.8 + i * 0.5}s`} />
                </circle>
              </g>
            );
          })}

          {/* Source nodes */}
          {SOURCES.map((s) => {
            const isThreat = s.id === "shadow";
            return (
              <g key={s.id}>
                <rect x="40" y={s.y} width="215" height="38" rx="9" fill="#fff" stroke={isThreat ? "#E0B4BC" : "#E4E0D8"} strokeWidth="1.5" />
                <text x="54" y={s.y + 16} fontSize="12" fontWeight="700" fill={isThreat ? RED : NAVY}>
                  {s.label}
                </text>
                <text x="54" y={s.y + 30} fontSize="9.5" fill="#8A8475">
                  {s.sub}
                </text>
              </g>
            );
          })}

          {/* Onyx control plane */}
          <rect x={OX} y={OY} width={OW} height={OH} rx="16" fill={NAVY} />
          <text x={OX + OW / 2} y={OY + 32} textAnchor="middle" fontSize="17" fontWeight="900" fill="#fff" letterSpacing="2">
            ONYX
          </text>
          <text x={OX + OW / 2} y={OY + 49} textAnchor="middle" fontSize="9" fontWeight="700" fill="#B9AEE0" letterSpacing="1.5">
            SECURE AI CONTROL PLANE
          </text>
          {["AI Discovery", "LLM Routing Gateway", "Guardian Runtime", "Prompt Injection Defense", "Data Exfil Prevention", "Policy & Governance", "Compliance Evidence"].map((layer, i) => (
            <g key={layer}>
              <rect x={OX + 18} y={OY + 64 + i * 40} width={OW - 36} height="30" rx="7" fill="#2D2154" stroke="#4A3D7A" strokeWidth="1" />
              <text x={OX + OW / 2} y={OY + 83 + i * 40} textAnchor="middle" fontSize="10.5" fontWeight="600" fill="#E8E3F5">
                {layer}
              </text>
            </g>
          ))}

          {/* Provider nodes */}
          {PROVIDERS.map((pr) => (
            <g key={pr.id}>
              <rect x="720" y={pr.y} width="240" height="34" rx="9" fill="#fff" stroke="#E4E0D8" strokeWidth="1.5" />
              <text x="736" y={pr.y + 21} fontSize="12" fontWeight="700" fill={NAVY}>
                {pr.label}
              </text>
            </g>
          ))}

          {/* Legend */}
          <g fontSize="10" fill="#8A8475">
            <circle cx="40" cy="466" r="5" fill={PURPLE} />
            <text x="52" y="470">AI traffic in</text>
            <circle cx="135" cy="466" r="5" fill={GREEN} />
            <text x="147" y="470">Inspected &amp; routed</text>
            <circle cx="270" cy="466" r="5" fill={RED} />
            <text x="282" y="470">Threat blocked at the gateway</text>
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
        Typical deployment: gateway live in the client VPC in under a day · discovery complete within 72 hours · zero application code changes.
      </div>
    </div>
  );
}
