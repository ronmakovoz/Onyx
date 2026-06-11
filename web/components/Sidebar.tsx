"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const GROUPS: { label: string; items: { name: string; href: string }[] }[] = [
  {
    label: "Monitor",
    items: [
      { name: "Dashboard", href: "/" },
      { name: "Customers", href: "/customers" },
      { name: "Implementation", href: "/implementation" },
      { name: "CSM Performance", href: "/csm" },
    ],
  },
  {
    label: "Grow",
    items: [{ name: "Growth & Whitespace", href: "/growth" }],
  },
  {
    label: "Deliver",
    items: [
      { name: "Briefings", href: "/briefings" },
      { name: "Agent Console", href: "/console" },
    ],
  },
  {
    label: "Govern",
    items: [{ name: "Audit & Costs", href: "/audit" }],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <aside className="w-[230px] shrink-0 bg-white border-r border-line shadow-[2px_0_12px_rgba(27,16,64,0.06)] px-3 py-4 sticky top-0 h-screen overflow-y-auto">
      <div className="px-2 pb-4">
        <span className="text-[1.3rem] font-black text-navy tracking-[-0.04em]">ONYX</span>
        <span className="text-[0.65rem] font-bold text-muted tracking-[0.12em] ml-2 align-middle">
          CX AGENT OS
        </span>
      </div>
      {GROUPS.map((g) => (
        <div key={g.label} className="mb-4">
          <div className="px-3 mb-1 text-[0.60rem] font-bold text-faint uppercase tracking-[0.12em]">
            {g.label}
          </div>
          <nav className="flex flex-col gap-[3px]">
            {g.items.map((it) => {
              const active = isActive(it.href);
              return (
                <Link
                  key={it.href}
                  href={it.href}
                  className={`rounded-lg px-3 py-2 text-[0.88rem] transition-colors ${
                    active
                      ? "bg-lavender text-navy font-bold shadow-[inset_3px_0_0_#1B1040]"
                      : "text-ink font-medium hover:bg-[#EDE9E4] hover:text-navy"
                  }`}
                >
                  {it.name}
                </Link>
              );
            })}
          </nav>
        </div>
      ))}
      <ModeToggle />
      <div className="px-3 mt-4 text-[0.62rem] text-faint leading-relaxed">
        Onyx · Secure AI Control Plane
        <br />
        Synthetic demo data
      </div>
    </aside>
  );
}

function ModeToggle() {
  const [live, setLive] = useState(false);
  const [available, setAvailable] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch("/api/mode")
      .then((r) => r.json())
      .then((d) => {
        setLive(d.live);
        setAvailable(d.available);
      })
      .catch(() => {});
  }, []);

  const toggle = async () => {
    if (!available || busy) return;
    setBusy(true);
    try {
      const r = await fetch("/api/mode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ live: !live }),
      });
      const d = await r.json();
      setLive(d.live);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="px-3 mt-6 pt-4 border-t border-line">
      <button
        onClick={toggle}
        disabled={!available || busy}
        className="flex items-center gap-2.5 w-full disabled:cursor-not-allowed"
        title={available ? "Toggle between mock data and live Claude calls" : "Set ANTHROPIC_API_KEY on the API server to enable live mode"}
      >
        <span
          className={`relative inline-block w-9 h-5 rounded-full transition-colors ${
            live ? "bg-navy" : "bg-[#D8D3C8]"
          } ${!available ? "opacity-40" : ""}`}
        >
          <span
            className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-all ${
              live ? "left-[18px]" : "left-0.5"
            }`}
          />
        </span>
        <span className="text-[0.78rem] font-semibold text-ink">Live Anthropic API</span>
      </button>
      <div
        className={`mt-1.5 text-[0.64rem] font-bold ${
          live ? "text-green" : "text-amber"
        }`}
      >
        {live
          ? "LIVE — calling Claude"
          : available
          ? "MOCK — no API calls"
          : "MOCK — set ANTHROPIC_API_KEY to enable live"}
      </div>
    </div>
  );
}
