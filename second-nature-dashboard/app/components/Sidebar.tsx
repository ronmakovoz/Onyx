"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const groups = [
  { label: "Monitor", items: [["Dashboard", "/"], ["Accounts", "/accounts"], ["Rollouts", "/implementation"], ["CSM Performance", "/team"]] },
  { label: "Grow", items: [["Growth & Whitespace", "/growth"]] },
  { label: "Deliver", items: [["Briefings", "/briefings"], ["Agent Studio", "/agents"], ["How It Connects", "/integration"]] },
  { label: "Govern", items: [["Audit & Costs", "/audit"]] },
] as const;

export default function Sidebar() {
  const pathname = usePathname();
  const [live, setLive] = useState(false);
  const [owner, setOwner] = useState(false);

  useEffect(() => {
    void Promise.all([
      fetch("/api/mode").then((response) => response.json()) as Promise<{ live?: boolean }>,
      fetch("/api/viewer").then((response) => response.json()) as Promise<{ isOwner?: boolean }>,
    ])
      .then(([mode, viewer]) => {
        setLive(mode.live === true);
        setOwner(viewer.isOwner === true);
      })
      .catch(() => undefined);
  }, []);

  return (
    <aside className="sidebar">
      <Link className="brand" href="/" aria-label="Second Nature dashboard home">
        <span className="brand-mark">S</span>
        <span className="brand-word">second<br />nature</span>
        <small>CX INTELLIGENCE OS</small>
      </Link>

      <div className="sidebar-nav">
        {groups.map((group) => (
          <section key={group.label}>
            <h2>{group.label}</h2>
            <nav>
              {group.items.map(([name, href]) => {
                const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
                return <Link key={href} href={href} className={active ? "active" : ""}>{name}</Link>;
              })}
            </nav>
          </section>
        ))}
        {owner && (
          <section>
            <h2>Private</h2>
            <nav>
              <Link href="/activity" className={pathname.startsWith("/activity") ? "active" : ""}>Activity Analytics</Link>
            </nav>
          </section>
        )}
      </div>

      <div className={`mode-card ${live ? "live" : ""}`}>
        <span><i /> {live ? "Anthropic live" : "Demo mode"}</span>
        <small>{live ? "Claude-powered agent runs" : "Synthetic portfolio · no API calls"}</small>
      </div>
      <p className="sidebar-foot">Synthetic customer and performance data for demonstration.</p>
    </aside>
  );
}
