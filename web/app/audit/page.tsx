"use client";

import { useEffect, useState } from "react";
import { getJSON, modelTierFromId, tierColor } from "@/lib/api";
import { KpiCard, PageHeader, SectionLabel, Spinner } from "@/components/ui";
import ReactMarkdown from "react-markdown";

type Costs = { by_model: any[]; grand_total: number };

export default function AuditPage() {
  const [costs, setCosts] = useState<Costs | null>(null);
  const [runs, setRuns] = useState<any[] | null>(null);

  useEffect(() => {
    getJSON<Costs>("/api/costs").then(setCosts).catch(() => setCosts({ by_model: [], grand_total: 0 }));
    getJSON<any[]>("/api/audit?limit=100").then(setRuns).catch(() => setRuns([]));
  }, []);

  if (!costs || !runs) return <Spinner label="Loading audit trail…" />;

  const mockCount = runs.filter((r) => !r.model_used).length;
  const total = costs.grand_total || 0;

  return (
    <div>
      <PageHeader title="Audit Trail & Cost Tracking" subtitle="Every agent run, its model, tokens and spend" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        <KpiCard label="Total Spend" value={`$${total.toFixed(4)}`} sub="all agent runs" />
        <KpiCard label="Total Runs" value={String(runs.length)} sub="last 100 shown" />
        <KpiCard label="Avg Cost / Run" value={`$${(total / Math.max(runs.length, 1)).toFixed(5)}`} />
        <KpiCard label="Live / Mock" value={`${runs.length - mockCount} / ${runs.length}`} sub="runs using real API" />
      </div>

      <SectionLabel>Spend by Model</SectionLabel>
      {costs.by_model.length ? (
        <div className="bg-white border border-line rounded-[14px] shadow-card overflow-hidden mb-6">
          <div className="grid grid-cols-[0.7fr_2fr_0.6fr_1fr_1fr] gap-3 px-[18px] py-[10px] text-[0.62rem] font-bold text-faint uppercase tracking-[0.10em]">
            <div>Tier</div>
            <div>Model</div>
            <div className="text-right">Runs</div>
            <div className="text-right">Tokens</div>
            <div className="text-right">Cost</div>
          </div>
          {costs.by_model.map((row, i) => {
            const tier = modelTierFromId(row.model_used || "");
            const totTok = (row.total_input_tokens || 0) + (row.total_output_tokens || 0);
            return (
              <div
                key={i}
                className="grid grid-cols-[0.7fr_2fr_0.6fr_1fr_1fr] gap-3 px-[18px] py-3 border-t border-[#F0EBE7] text-[0.82rem] items-center"
              >
                <div className="font-bold" style={{ color: tierColor(tier) }}>
                  {tier.charAt(0).toUpperCase() + tier.slice(1)}
                </div>
                <div className="text-ink">{row.model_used || "(mock)"}</div>
                <div className="text-right text-ink">{row.run_count}</div>
                <div className="text-right text-ink">{totTok.toLocaleString()}</div>
                <div className="text-right font-semibold text-navy">${(row.total_cost || 0).toFixed(5)}</div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-muted text-[0.78rem] mb-6">No live runs recorded yet.</div>
      )}

      <SectionLabel>
        Run History <span className="font-normal normal-case tracking-normal">({runs.length} records)</span>
      </SectionLabel>
      {runs.map((run) => {
        const tier = modelTierFromId(run.model_used || "");
        const color = tierColor(tier);
        return (
          <details key={run.id} className="bg-white border border-line rounded-lg mb-[5px]">
            <summary className="px-3 py-2 text-[0.82rem] font-semibold text-navy cursor-pointer">
              #{run.id} · {run.agent_name} · {run.customer_name || "Portfolio"} ·{" "}
              {(run.created_at || "").slice(0, 16).replace("T", " ")} UTC
            </summary>
            <div className="px-4 pb-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-3">
                <div>
                  <div className="font-bold" style={{ color }}>
                    {tier.charAt(0).toUpperCase() + tier.slice(1)}
                  </div>
                  <div className="text-[0.70rem] text-muted">{run.model_used || "(mock)"}</div>
                </div>
                <div>
                  <div className="text-[0.62rem] text-muted uppercase tracking-[0.08em] font-bold">Cost</div>
                  <div className="font-extrabold text-navy">${(run.estimated_cost_usd || 0).toFixed(5)}</div>
                </div>
                <div>
                  <div className="text-[0.62rem] text-muted uppercase tracking-[0.08em] font-bold">Confidence</div>
                  <div className="font-extrabold text-navy">
                    {Math.round((run.confidence_score || 0) * 100)}%
                  </div>
                </div>
                <div>
                  <div className="text-[0.62rem] text-muted uppercase tracking-[0.08em] font-bold">Tokens</div>
                  <div className="font-extrabold text-navy">
                    {(run.input_tokens || 0).toLocaleString()}+{(run.output_tokens || 0).toLocaleString()}
                  </div>
                </div>
              </div>
              {run.model_rationale ? (
                <div className="text-[0.78rem] text-muted italic mb-3">{run.model_rationale}</div>
              ) : null}
              <hr className="border-line mb-3" />
              <div className="agent-report">
                <ReactMarkdown>{run.output_text || ""}</ReactMarkdown>
              </div>
            </div>
          </details>
        );
      })}
    </div>
  );
}
