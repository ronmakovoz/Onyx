"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AgentResult, agentDisplayName, modelTierFromId, tierColor } from "@/lib/api";

export function MetaPills({ result }: { result: AgentResult }) {
  const tier = result.model_tier || modelTierFromId(result.model_used || "");
  const color = tierColor(tier);
  const conf = result.confidence_score ?? 0;
  const confColor = conf >= 0.75 ? "#2D5A3D" : conf >= 0.55 ? "#7A5C1E" : "#9B2335";
  const disp = result.model_display || result.model_used || "?";
  const sep = <span className="text-[#C8C2B8]">·</span>;
  return (
    <div className="flex items-center gap-2 flex-wrap mb-[10px] mt-[2px]">
      <span
        className="bg-white rounded-full px-[11px] py-[2px] text-[0.70rem] font-bold"
        style={{ border: `1px solid ${color}`, color }}
      >
        {disp}
      </span>
      {sep}
      <span className="text-muted text-[0.72rem]">
        Confidence <b style={{ color: confColor }}>{Math.round(conf * 100)}%</b>
      </span>
      {sep}
      <span className="text-muted text-[0.72rem]">
        Est. cost <b className="text-ink">${(result.estimated_cost_usd ?? 0).toFixed(4)}</b>
      </span>
      {sep}
      <span className="text-muted text-[0.72rem]">
        {(result.input_tokens ?? 0).toLocaleString()} in · {(result.output_tokens ?? 0).toLocaleString()} out
      </span>
      {result.is_mock ? (
        <span className="rounded-full px-[10px] py-[2px] text-[0.68rem] font-bold bg-[#F5F0E8] text-amber border border-[#D8C89A]">
          MOCK
        </span>
      ) : null}
    </div>
  );
}

export default function AgentReport({
  result,
  showMeta = true,
}: {
  result: AgentResult;
  showMeta?: boolean;
}) {
  if (result.error) {
    return (
      <div className="bg-[#FDF1F2] border border-[#D4AAAA] text-red rounded-lg px-4 py-3 text-sm">
        Agent error: {result.error}
      </div>
    );
  }

  const ts = (result.created_at || "").slice(0, 16).replace("T", " ");

  return (
    <div>
      {showMeta ? <MetaPills result={result} /> : null}
      <div
        className="relative rounded-[14px] border border-[#E0D8E8] border-t-4 border-t-navy shadow-report px-[30px] pt-[14px] pb-[22px]"
        style={{ background: "linear-gradient(180deg, #FDFBF7 0%, #FFFFFF 120px)" }}
      >
        <span className="absolute top-[14px] right-5 text-[0.62rem] font-black tracking-[0.18em] text-[#D8CFE4]">
          ONYX
        </span>
        <div className="agent-report">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.output_text || ""}</ReactMarkdown>
        </div>
      </div>
      {result.run_id ? (
        <div className="text-[0.70rem] text-muted mt-2">
          Generated {ts} UTC · Run #{result.run_id} · {agentDisplayName(result.agent_name || "")}
        </div>
      ) : null}
      {result.model_rationale ? (
        <details className="bg-white border border-line rounded-lg mt-2">
          <summary className="px-3 py-2 text-[0.82rem] font-semibold text-navy cursor-pointer">
            Model routing rationale
          </summary>
          <div className="px-3 pb-3 text-[0.82rem] text-muted italic">{result.model_rationale}</div>
        </details>
      ) : null}
    </div>
  );
}
