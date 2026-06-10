"""
Red Team Debate — branded HTML view served by FastAPI.
Renders the Bull vs Bear adversarial debate with the Synthesis verdict
as a self-contained Onyx-branded page (no frontend framework required).
"""

import html
import re


# ── Minimal markdown → HTML (headers, bold, italics, lists, hr) ───────────────

def _md_to_html(md: str) -> str:
    lines = md.splitlines()
    out, in_list = [], False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        return s

    for raw in lines:
        line = raw.strip()
        if not line:
            close_list()
            continue
        if line.startswith("---"):
            close_list()
            out.append("<hr>")
        elif line.startswith("### "):
            close_list()
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            close_list()
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            close_list()
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif re.match(r"^[-*•]\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^[-*•]\s+", "", line)
            out.append("<li>" + inline(item) + "</li>")
        elif re.match(r"^\d+\.\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^\d+\.\s+", "", line)
            out.append("<li>" + inline(item) + "</li>")
        else:
            close_list()
            out.append(f"<p>{inline(line)}</p>")
    close_list()
    return "\n".join(out)


_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { margin:0; padding:0; box-sizing:border-box; font-family:'Inter',sans-serif; }
body { background:#F5F2EE; color:#1B1040; min-height:100vh; }
.wrap { max-width:1320px; margin:0 auto; padding:28px 28px 60px; }
.brand { display:flex; align-items:baseline; gap:10px; margin-bottom:4px; }
.brand .logo { font-size:1.5rem; font-weight:900; letter-spacing:-0.04em; color:#1B1040; }
.brand .sub { font-size:0.65rem; font-weight:700; letter-spacing:0.14em; color:#6B6280; }
h1.title { font-size:1.7rem; font-weight:800; letter-spacing:-0.03em; margin:10px 0 2px; }
.subtitle { color:#6B6280; font-size:0.85rem; margin-bottom:22px; }

.verdict-band { background:#1B1040; border-radius:16px; padding:24px 28px; margin-bottom:24px;
  box-shadow:0 4px 24px rgba(27,16,64,0.25); }
.verdict-label { color:#9B93C8; font-size:0.62rem; font-weight:700; text-transform:uppercase; letter-spacing:0.14em; }
.verdict-value { color:#FFFFFF; font-size:1.9rem; font-weight:800; letter-spacing:-0.02em; line-height:1.15; }
.verdict-pill { display:inline-block; border-radius:50px; padding:4px 16px; font-size:0.78rem; font-weight:800;
  vertical-align:middle; margin-left:14px; }
.pill-renew  { background:#2D5A3D; color:#fff; }
.pill-tossup { background:#7A5C1E; color:#fff; }
.pill-churn  { background:#9B2335; color:#fff; }

.gauge { position:relative; height:30px; border-radius:50px; overflow:hidden; margin:18px 0 6px;
  background:linear-gradient(90deg,#9B2335 0%,#7A5C1E 50%,#2D5A3D 100%); opacity:0.92; }
.gauge .range { position:absolute; top:0; bottom:0; background:rgba(255,255,255,0.32);
  border-left:3px solid #fff; border-right:3px solid #fff; }
.gauge-labels { display:flex; justify-content:space-between; color:#9B93C8; font-size:0.66rem; font-weight:600; }
.gauge-marks { position:relative; height:18px; }
.gauge-marks span { position:absolute; transform:translateX(-50%); color:#fff; font-size:0.7rem; font-weight:800; }

.cols { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:24px; }
@media (max-width:900px) { .cols { grid-template-columns:1fr; } }

.panel { background:#FFFFFF; border:1px solid #E8E4DC; border-radius:16px; padding:22px 26px;
  box-shadow:0 1px 6px rgba(27,16,64,0.05); }
.panel-bull  { border-top:4px solid #2D5A3D; }
.panel-bear  { border-top:4px solid #9B2335; }
.panel-synth { border-top:4px solid #1B1040; }

.panel-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
.panel-tag { font-size:0.64rem; font-weight:800; text-transform:uppercase; letter-spacing:0.12em;
  border-radius:50px; padding:4px 13px; }
.tag-bull  { background:#EBF2EE; color:#2D5A3D; }
.tag-bear  { background:#F5ECEC; color:#9B2335; }
.tag-synth { background:#EDEAF4; color:#1B1040; }
.panel-prob { font-size:1.3rem; font-weight:800; }
.prob-bull { color:#2D5A3D; } .prob-bear { color:#9B2335; }

.panel h1 { font-size:1.05rem; font-weight:800; margin:10px 0 4px; letter-spacing:-0.01em; }
.panel h2 { font-size:0.98rem; font-weight:800; margin:12px 0 4px; letter-spacing:-0.01em; }
.panel h3 { font-size:0.74rem; font-weight:800; color:#6B6280; text-transform:uppercase;
  letter-spacing:0.09em; margin:18px 0 6px; padding-bottom:5px; border-bottom:1px solid #EFEBE4; }
.panel p  { font-size:0.85rem; line-height:1.6; color:#3D3458; margin:5px 0; }
.panel ul { margin:4px 0 4px 18px; }
.panel li { font-size:0.85rem; line-height:1.55; color:#3D3458; margin:5px 0; }
.panel strong { color:#1B1040; }
.panel hr { border:none; border-top:1px solid #EFEBE4; margin:14px 0; }

.meta { color:#9B93A8; font-size:0.68rem; margin-top:8px; }
.footer { color:#9B93A8; font-size:0.7rem; text-align:center; margin-top:28px; }
.topbar { display:flex; justify-content:space-between; align-items:flex-start; }
.btn { display:inline-block; background:#1B1040; color:#fff; border-radius:50px; padding:8px 20px;
  font-size:0.78rem; font-weight:700; text-decoration:none; box-shadow:0 1px 6px rgba(27,16,64,0.2); }
.btn:hover { background:#2D1A5E; }
"""


def _verdict_pill(verdict: str) -> str:
    cls = {"Lean Renew": "pill-renew", "Toss-Up": "pill-tossup", "Lean Churn": "pill-churn"}.get(verdict, "pill-tossup")
    return f'<span class="verdict-pill {cls}">{html.escape(verdict)}</span>'


def render_debate(bull: dict, bear: dict, synth: dict, ctx: dict) -> str:
    """bull/bear/synth: dicts with output_text + structured (as plain dicts)."""
    name = ctx.get("customer_name", "Customer")
    arr  = ctx.get("arr", 0)
    days = ctx.get("renewal_days", "?")

    s = synth.get("structured") or {}
    lo, hi  = s.get("renewal_probability_low", 40), s.get("renewal_probability_high", 60)
    verdict = s.get("verdict", "Toss-Up")
    bull_p  = (bull.get("structured") or {}).get("renewal_probability", 70)
    bear_p  = (bear.get("structured") or {}).get("renewal_probability", 35)

    def meta(r):
        cost = r.get("estimated_cost_usd", 0)
        mock = " · MOCK" if r.get("is_mock") else ""
        return (f'{r.get("model_display", r.get("model_used", "?"))} · '
                f'{r.get("input_tokens",0):,} in / {r.get("output_tokens",0):,} out · '
                f'${cost:.4f}{mock}')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Red Team Debate — {html.escape(name)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{_BASE_CSS}</style></head>
<body><div class="wrap">
  <div class="topbar">
    <div>
      <div class="brand"><span class="logo">ONYX</span><span class="sub">CX AGENT OS · RED TEAM DEBATE</span></div>
      <h1 class="title">{html.escape(name)}</h1>
      <div class="subtitle">${arr:,} ARR · renews in {days} days · two adversarial agents argued this account, a third judged the debate</div>
    </div>
    <a class="btn" href="?fresh=1">↻ Re-run debate</a>
  </div>

  <div class="verdict-band">
    <div class="verdict-label">Calibrated renewal probability</div>
    <div class="verdict-value">{lo}–{hi}% {_verdict_pill(verdict)}</div>
    <div class="gauge">
      <div class="range" style="left:{lo}%;width:{max(hi-lo,2)}%"></div>
    </div>
    <div class="gauge-marks">
      <span style="left:{bear_p}%">▲ Bear {bear_p}%</span>
      <span style="left:{bull_p}%;color:#fff">▲ Bull {bull_p}%</span>
    </div>
    <div class="gauge-labels"><span>0% — certain churn</span><span>100% — certain renewal</span></div>
  </div>

  <div class="cols">
    <div class="panel panel-bull">
      <div class="panel-head">
        <span class="panel-tag tag-bull">Bull Case · Advocate</span>
        <span class="panel-prob prob-bull">{bull_p}%</span>
      </div>
      {_md_to_html(bull.get("output_text",""))}
      <div class="meta">{meta(bull)}</div>
    </div>
    <div class="panel panel-bear">
      <div class="panel-head">
        <span class="panel-tag tag-bear">Bear Case · Adversary</span>
        <span class="panel-prob prob-bear">{bear_p}%</span>
      </div>
      {_md_to_html(bear.get("output_text",""))}
      <div class="meta">{meta(bear)}</div>
    </div>
  </div>

  <div class="panel panel-synth">
    <div class="panel-head">
      <span class="panel-tag tag-synth">Synthesis · Judge (Opus)</span>
      <span class="panel-prob">{lo}–{hi}%</span>
    </div>
    {_md_to_html(synth.get("output_text",""))}
    <div class="meta">{meta(synth)}</div>
  </div>

  <div class="footer">Generated by Onyx CX Agent OS · Multi-agent adversarial debate · Bull + Bear ran in parallel (Sonnet), Synthesis judged (Opus)</div>
</div></body></html>"""


def render_debate_loading(customer_name: str, customer_id: int) -> str:
    """Branded interstitial that fires the debate run via JS, then reloads."""
    name = html.escape(customer_name)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Running Red Team Debate — {name}</title>
<style>{_BASE_CSS}
.center {{ min-height:80vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }}
.dots span {{ display:inline-block; width:11px; height:11px; border-radius:50%; background:#1B1040; margin:0 5px;
  animation:pulse 1.2s infinite ease-in-out; }}
.dots span:nth-child(2) {{ animation-delay:0.2s; background:#9B2335; }}
.dots span:nth-child(3) {{ animation-delay:0.4s; background:#2D5A3D; }}
@keyframes pulse {{ 0%,80%,100% {{ transform:scale(0.6); opacity:0.4; }} 40% {{ transform:scale(1); opacity:1; }} }}
.stage {{ color:#6B6280; font-size:0.85rem; margin-top:14px; }}
</style></head>
<body><div class="wrap"><div class="center">
  <div class="brand" style="justify-content:center"><span class="logo">ONYX</span><span class="sub">CX AGENT OS</span></div>
  <h1 class="title" style="margin-top:18px">Red Team Debate — {name}</h1>
  <div class="subtitle">Bull and Bear agents are arguing this account in parallel. The Synthesis judge will rule.</div>
  <div class="dots"><span></span><span></span><span></span></div>
  <div class="stage" id="stage">Opening arguments…</div>
</div></div>
<script>
const stages = ["Opening arguments…","Bull case building…","Bear case attacking…","Cross-examination…","Synthesis judging the debate…"];
let i = 0;
setInterval(() => {{ i = (i + 1) % stages.length; document.getElementById("stage").textContent = stages[i]; }}, 4000);
fetch("/agents/run-red-team-debate?customer_id={customer_id}", {{ method: "POST" }})
  .then(r => {{ if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }})
  .then(() => location.replace("/customers/{customer_id}/debate"))
  .catch(e => {{ document.getElementById("stage").textContent = "Debate failed: " + e.message; }});
</script></body></html>"""
