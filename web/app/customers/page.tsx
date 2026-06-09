"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getJSON, Customer, fmtUSD, healthColor, riskColor, riskBg } from "@/lib/api";
import { PageHeader, Pill, Spinner } from "@/components/ui";

export default function CustomersPage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[] | null>(null);
  const [q, setQ] = useState("");

  useEffect(() => {
    getJSON<Customer[]>("/api/customers").then(setCustomers).catch(() => setCustomers([]));
  }, []);

  const filtered = useMemo(() => {
    if (!customers) return [];
    const s = q.trim().toLowerCase();
    if (!s) return customers;
    return customers.filter(
      (c) =>
        c.name.toLowerCase().includes(s) ||
        c.industry.toLowerCase().includes(s) ||
        (c.customer_tier || "").toLowerCase().includes(s) ||
        (c.csm_owner || "").toLowerCase().includes(s)
    );
  }, [customers, q]);

  if (!customers) return <Spinner label="Loading customers…" />;

  return (
    <div>
      <PageHeader title="Customers" subtitle="Full portfolio — sorted by health, click any account to open its 360" />

      <input
        type="text"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search by name, industry, tier or CSM…"
        className="w-full max-w-md bg-white border border-[#E0D8E8] rounded-xl px-4 py-2 text-[0.88rem] text-navy shadow-card mb-4 outline-none focus:border-navy"
      />

      <div className="bg-white border border-line rounded-[14px] shadow-card overflow-hidden">
        <div className="grid grid-cols-[1.6fr_1.1fr_0.8fr_0.9fr_0.6fr_0.9fr_0.6fr_0.9fr] gap-3 px-[18px] py-[10px] text-[0.62rem] font-bold text-faint uppercase tracking-[0.10em]">
          <div>Customer</div>
          <div>Industry</div>
          <div>Tier</div>
          <div className="text-right">ARR</div>
          <div className="text-center">Health</div>
          <div className="text-center">Risk</div>
          <div className="text-center">NRR</div>
          <div>Renewal</div>
        </div>
        {filtered.map((c) => (
          <div
            key={c.id}
            onClick={() => router.push(`/customers/${c.id}`)}
            className="grid grid-cols-[1.6fr_1.1fr_0.8fr_0.9fr_0.6fr_0.9fr_0.6fr_0.9fr] gap-3 px-[18px] py-[13px] items-center border-t border-[#F0EBE7] text-[0.82rem] cursor-pointer hover:bg-[#FBF7FA] transition-colors"
          >
            <div className="font-bold text-navy">{c.name}</div>
            <div className="text-ink">{c.industry}</div>
            <div className="text-ink">{c.customer_tier}</div>
            <div className="text-right text-ink font-semibold">{fmtUSD(c.arr)}</div>
            <div className="text-center font-extrabold" style={{ color: healthColor(c.health_score) }}>
              {c.health_score}
            </div>
            <div className="text-center">
              <Pill color={riskColor[c.risk_level]} bg={riskBg[c.risk_level]} bordered>
                {c.risk_level === "Low" ? "Healthy" : `${c.risk_level} risk`}
              </Pill>
            </div>
            <div className="text-center text-ink">{c.nrr_pct ?? "—"}%</div>
            <div className="text-muted">{c.renewal_date}</div>
          </div>
        ))}
        {!filtered.length ? (
          <div className="px-[18px] py-6 text-muted text-sm border-t border-[#F0EBE7]">
            No customers match “{q}”.
          </div>
        ) : null}
      </div>
    </div>
  );
}
