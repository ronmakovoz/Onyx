"use client";

import { useEffect, useState } from "react";
import { getJSON, postJSON, AgentResult, Customer, fmtUSD } from "@/lib/api";
import { PageHeader, SectionLabel, Spinner, TabBar } from "@/components/ui";
import AgentReport from "@/components/AgentReport";
import ReactMarkdown from "react-markdown";

const TABS = ["CEO Briefing", "VP Weekly Review", "History"];

export default function BriefingsPage() {
  const [tab, setTab] = useState(TABS[0]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selCid, setSelCid] = useState<number | null>(null);

  const [ceo, setCeo] = useState<AgentResult | null>(null);
  const [skeptik, setSkeptik] = useState<AgentResult | null>(null);
  const [vp, setVp] = useState<AgentResult | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const [ceoHist, setCeoHist] = useState<any[]>([]);
  const [vpHist, setVpHist] = useState<any[]>([]);

  useEffect(() => {
    getJSON<Customer[]>("/api/customers").then((cs) => {
      setCustomers(cs);
      if (cs.length) setSelCid(cs[0].id);
    });
  }, []);

  useEffect(() => {
    if (tab === "History") {
      getJSON<any[]>("/api/briefings?type=CEO").then(setCeoHist).catch(() => {});
      getJSON<any[]>("/api/briefings?type=VP_CX").then(setVpHist).catch(() => {});
    }
  }, [tab]);

  const run = async (kind: "ceo" | "skeptik" | "vp") => {
    setBusy(kind);
    try {
      if (kind === "ceo") {
        setSkeptik(null);
        setCeo(await postJSON("/api/agents/run", { agent_name: "BriefingAgent", customer_id: selCid }));
      } else if (kind === "skeptik") {
        setSkeptik(await postJSON("/api/agents/run", { agent_name: "SkeptikQAAgent", customer_id: selCid }));
      } else {
        setVp(await postJSON("/api/agents/run", { agent_name: "VPChiefOfStaffAgent" }));
      }
    } catch (e) {
      const err = { error: String(e) };
      if (kind === "ceo") setCeo(err);
      else if (kind === "skeptik") setSkeptik(err);
      else setVp(err);
    } finally {
      setBusy(null);
    }
  };

  return (
    <div>
      <PageHeader title="Briefings" subtitle="Executive-grade documents generated on demand" />
      <TabBar tabs={TABS} active={tab} onChange={setTab} />

      {tab === "CEO Briefing" && (
        <div>
          <div className="flex gap-3 items-center flex-wrap mb-4">
            <select
              value={selCid ?? ""}
              onChange={(e) => setSelCid(Number(e.target.value))}
              className="bg-white border border-[#E0D8E8] rounded-xl px-3 py-2 text-[0.88rem] text-navy shadow-card outline-none min-w-[320px]"
            >
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} — {fmtUSD(c.arr)} · {c.risk_level} risk
                </option>
              ))}
            </select>
            <button
              onClick={() => run("ceo")}
              disabled={busy !== null || selCid === null}
              className="bg-navy text-white rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#16306E] disabled:opacity-60"
            >
              {busy === "ceo" ? "Generating…" : "Generate CEO Briefing"}
            </button>
            {ceo && !ceo.error ? (
              <button
                onClick={() => run("skeptik")}
                disabled={busy !== null}
                className="bg-white text-navy border-[1.5px] border-[#C4D0E8] rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#F0ECE8] disabled:opacity-60"
              >
                {busy === "skeptik" ? "Reviewing…" : "Review with Skeptik Agent"}
              </button>
            ) : null}
          </div>
          {busy === "ceo" ? <Spinner label="Generating CEO Briefing (Sonnet)…" /> : null}
          {busy === "skeptik" ? <Spinner label="Running Skeptik QA (Opus)…" /> : null}
          {ceo && skeptik ? (
            <div className="grid lg:grid-cols-2 gap-5">
              <div>
                <SectionLabel>Original Briefing</SectionLabel>
                <AgentReport result={ceo} />
              </div>
              <div>
                <SectionLabel>Skeptik QA Review</SectionLabel>
                <AgentReport result={skeptik} />
              </div>
            </div>
          ) : ceo ? (
            <AgentReport result={ceo} />
          ) : null}
        </div>
      )}

      {tab === "VP Weekly Review" && (
        <div>
          <button
            onClick={() => run("vp")}
            disabled={busy !== null}
            className="bg-navy text-white rounded-full px-5 py-2 text-[0.78rem] font-semibold hover:bg-[#16306E] disabled:opacity-60 mb-4"
          >
            {busy === "vp" ? "Generating…" : "Generate Weekly VP CX Review"}
          </button>
          {busy === "vp" ? <Spinner label="Running VP Chief of Staff Agent (Opus)…" /> : null}
          {vp ? <AgentReport result={vp} /> : null}
        </div>
      )}

      {tab === "History" && (
        <div>
          <SectionLabel>Recent CEO Briefings</SectionLabel>
          {!ceoHist.length ? <div className="text-muted text-[0.78rem] mb-4">No CEO briefings generated yet.</div> : null}
          {ceoHist.map((b) => (
            <details key={b.id} className="bg-white border border-line rounded-lg mb-[5px]">
              <summary className="px-3 py-2 text-[0.82rem] font-semibold text-navy cursor-pointer">
                {b.customer_name ?? "?"} · {(b.created_at || "").slice(0, 16).replace("T", " ")} UTC
              </summary>
              <div className="px-5 pb-4 agent-report">
                <ReactMarkdown>{b.content || ""}</ReactMarkdown>
              </div>
            </details>
          ))}

          <SectionLabel className="mt-6">Recent VP CX Reviews</SectionLabel>
          {!vpHist.length ? <div className="text-muted text-[0.78rem]">No VP CX reviews generated yet.</div> : null}
          {vpHist.map((b) => (
            <details key={b.id} className="bg-white border border-line rounded-lg mb-[5px]">
              <summary className="px-3 py-2 text-[0.82rem] font-semibold text-navy cursor-pointer">
                Weekly Review · {(b.created_at || "").slice(0, 16).replace("T", " ")} UTC
              </summary>
              <div className="px-5 pb-4 agent-report">
                <ReactMarkdown>{b.content || ""}</ReactMarkdown>
              </div>
            </details>
          ))}
        </div>
      )}
    </div>
  );
}
