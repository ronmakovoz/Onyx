"""
Renders the KickoffDeckAgent's structured output as a branded, self-contained
HTML slide deck (16:9). Matches Onyx Security's deck style: warm cream
background, near-black display headings, white rounded cards, lavender
accents, lowercase "onyx" wordmark, subtle circuit-trace motif.

Open in a browser to present (arrow keys / scroll), or print to PDF
(each slide is one landscape page).
"""

import html
import re
from datetime import datetime


def _esc(s) -> str:
    """Escape HTML, then re-apply markdown bold (**x**) as <b>x</b>."""
    out = html.escape(str(s or ""))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)


def _split_row(item: str, n: int) -> list[str]:
    """Split an 'a — b — c' structured row into exactly n cells.

    Field values can themselves contain em-dashes (e.g. "QBR #1 — 90-Day
    Review"), so when there are extra parts the surplus is merged into the
    second cell (the descriptive one) rather than shifting columns.
    """
    parts = [p.strip() for p in str(item).split("—")]
    if len(parts) > n:
        surplus = len(parts) - n
        parts = [parts[0], " — ".join(parts[1:2 + surplus])] + parts[2 + surplus:]
    parts += [""] * (n - len(parts))
    return parts[:n]


# Circuit-trace background motif (subtle, like the brand deck)
_TRACES = """<svg class="traces" viewBox="0 0 1280 720" preserveAspectRatio="none">
<g stroke="#1B1040" stroke-opacity="0.05" stroke-width="1.5" fill="none">
<path d="M-20 120 H 240 L 300 180 H 520"/><path d="M1300 90 H 1080 L 1020 150 H 880"/>
<path d="M-20 600 H 180 L 260 520 H 420"/><path d="M1300 640 H 1120 L 1040 560 H 900"/>
<path d="M120 740 V 620 L 200 540"/><path d="M1180 -20 V 110 L 1100 190"/>
</g>
<g fill="#1B1040" fill-opacity="0.07">
<circle cx="520" cy="180" r="4"/><circle cx="880" cy="150" r="4"/><circle cx="420" cy="520" r="4"/>
<circle cx="900" cy="560" r="4"/><circle cx="200" cy="540" r="4"/><circle cx="1100" cy="190" r="4"/>
</g></svg>"""

_WORDMARK = '<div class="wordmark">onyx</div>'


def _slide(body: str, cls: str = "") -> str:
    return f'<section class="slide {cls}">{_TRACES}{body}{_WORDMARK}</section>'


def _chips(items: list, color="#7C5CBF", bg="#EDE7F8") -> str:
    return "".join(
        f'<span class="chip" style="color:{color};background:{bg}">{_esc(i)}</span>' for i in items
    )


def _card_list(items: list, icon: str = "→") -> str:
    return "".join(
        f'<div class="card"><span class="card-icon">{icon}</span><div>{_esc(i)}</div></div>'
        for i in items
    )


def render_kickoff_deck(structured: dict, ctx: dict) -> str:
    customer = ctx.get("customer_name", "Customer")
    industry = ctx.get("industry", "")
    date_str = datetime.now().strftime("%B %Y")
    golive = ctx.get("go_live_target", "")
    golive = "" if golive in (None, "Not set") else golive

    vision = structured.get("partnership_vision", "")
    team = structured.get("engagement_team", [])
    scope = structured.get("scope_objectives", [])
    timeline = structured.get("timeline", [])
    metrics = structured.get("success_metrics", [])
    first30 = structured.get("first_30_days", [])
    governance = structured.get("governance", "")
    prereqs = structured.get("customer_prerequisites", [])

    # ── Slide 1: Title ────────────────────────────────────────────────────────
    s1 = _slide(f"""
      <div class="title-wrap">
        <div class="lockup"><span class="lockup-onyx">onyx</span><span class="lockup-x">✕</span><span class="lockup-cust">{_esc(customer)}</span></div>
        <h1 class="display">Implementation<br>Kickoff</h1>
        <div class="title-sub">{_esc(industry)}{' · Go-live target ' + _esc(golive) if golive else ''}</div>
        <div class="title-date">{date_str}</div>
      </div>""", "center")

    # ── Slide 2: Vision + Scope ───────────────────────────────────────────────
    s2 = _slide(f"""
      <h2>Our partnership</h2>
      <p class="lede">{_esc(vision)}</p>
      <div class="label">Scope &amp; objectives</div>
      <div class="grid-2">{_card_list(scope, "◆")}</div>""")

    # ── Slide 3: Engagement Team ──────────────────────────────────────────────
    team_cards = ""
    for item in team:
        role, name, resp = _split_row(item, 3)
        is_onyx = "onyx" in role.lower()
        tag = "ONYX" if is_onyx else _esc(customer).upper()[:18]
        tagbg = "#EDE7F8" if is_onyx else "#FBEFE6"
        tagc = "#7C5CBF" if is_onyx else "#B06A2E"
        team_cards += f"""<div class="team-card">
          <span class="chip" style="background:{tagbg};color:{tagc}">{tag}</span>
          <div class="team-role">{_esc(role)}</div>
          <div class="team-name">{_esc(name)}</div>
          <div class="team-resp">{_esc(resp)}</div></div>"""
    s3 = _slide(f"""<h2>Engagement team</h2><div class="grid-3">{team_cards}</div>""")

    # ── Slide 4: Timeline ─────────────────────────────────────────────────────
    phase_colors = {
        "Foundation": ("#7C5CBF", "#EDE7F8"), "Integration": ("#2D6A8A", "#E4F0F6"),
        "Pilot": ("#B06A2E", "#FBEFE6"), "Validation": ("#7A5C1E", "#F7F0DC"),
        "Launch": ("#2D5A3D", "#E8F5EC"), "Value": ("#9B2335", "#FBEAEC"),
    }
    tl_rows = ""
    for item in timeline:
        phase, milestone, date, owner = _split_row(item, 4)
        pc, pb = phase_colors.get(phase, ("#1B1040", "#EFEBE4"))
        tl_rows += f"""<tr>
          <td><span class="chip" style="color:{pc};background:{pb}">{_esc(phase)}</span></td>
          <td class="tl-milestone">{_esc(milestone)}</td>
          <td class="tl-date">{_esc(date)}</td>
          <td class="tl-owner">{_esc(owner)}</td></tr>"""
    s4 = _slide(f"""
      <h2>Implementation timeline</h2>
      <table class="timeline"><thead><tr><th>Phase</th><th>Milestone</th><th>Target</th><th>Owner</th></tr></thead>
      <tbody>{tl_rows}</tbody></table>""")

    # ── Slide 5: Success Metrics + First 30 Days ─────────────────────────────
    s5 = _slide(f"""
      <div class="cols">
        <div><h2>How we measure success</h2>{_card_list(metrics, "✓")}</div>
        <div><h2>The first 30 days</h2>{_card_list(first30, "→")}</div>
      </div>""")

    # ── Slide 6: Governance + Prerequisites ──────────────────────────────────
    s6 = _slide(f"""
      <div class="cols">
        <div><h2>Communication &amp; governance</h2><p class="lede">{_esc(governance)}</p></div>
        <div><h2>What we need from you</h2>{_card_list(prereqs, "◆")}</div>
      </div>""")

    # ── Slide 7: Closing ──────────────────────────────────────────────────────
    s7 = _slide(f"""
      <div class="title-wrap">
        <h1 class="display">Let's get started.</h1>
        <div class="title-sub">Onyx Security ✕ {_esc(customer)} · {date_str}</div>
      </div>""", "center")

    slides = s1 + s2 + s3 + s4 + s5 + s6 + s7

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Implementation Kickoff — {_esc(customer)} · Onyx Security</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Inter',sans-serif; }}
  body {{ background:#2A2433; }}
  .slide {{
    position:relative; width:1280px; height:720px; margin:24px auto; overflow:hidden;
    background:linear-gradient(135deg,#F8F4EF 0%,#F5F0EA 55%,#F3EDEF 100%);
    border-radius:6px; padding:64px 72px;
  }}
  .slide.center {{ display:flex; align-items:center; justify-content:center; text-align:center; }}
  .traces {{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }}
  .slide > *:not(.traces) {{ position:relative; }}
  .wordmark {{ position:absolute !important; left:28px; bottom:20px; font-size:15px;
    font-weight:800; letter-spacing:0.04em; color:#16131F; }}
  h1.display {{ font-size:84px; font-weight:800; letter-spacing:-0.03em; line-height:1.05; color:#16131F; }}
  h2 {{ font-size:40px; font-weight:800; letter-spacing:-0.02em; color:#16131F; margin-bottom:22px; }}
  .lede {{ font-size:19px; line-height:1.65; color:#3D3458; max-width:980px; margin-bottom:26px; }}
  .label {{ font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.14em;
    color:#7C5CBF; margin:6px 0 14px; }}
  .chip {{ display:inline-block; font-size:11px; font-weight:800; letter-spacing:0.08em;
    padding:3px 12px; border-radius:999px; text-transform:uppercase; }}
  .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
  .grid-3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
  .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:48px; }}
  .card {{ display:flex; gap:12px; align-items:flex-start; background:#FFFFFF;
    border:1px solid #E9E3DA; border-radius:14px; padding:16px 18px;
    font-size:15.5px; line-height:1.5; color:#2B2438; margin-bottom:12px;
    box-shadow:0 1px 3px rgba(27,16,64,0.04); }}
  .grid-2 .card {{ margin-bottom:0; }}
  .card-icon {{ color:#7C5CBF; font-weight:800; font-size:14px; padding-top:2px; }}
  .team-card {{ background:#FFFFFF; border:1px solid #E9E3DA; border-radius:14px; padding:18px;
    box-shadow:0 1px 3px rgba(27,16,64,0.04); }}
  .team-role {{ font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;
    color:#6B6280; margin-top:12px; }}
  .team-name {{ font-size:19px; font-weight:800; color:#16131F; margin:2px 0 6px; }}
  .team-resp {{ font-size:13.5px; line-height:1.45; color:#3D3458; }}
  table.timeline {{ width:100%; border-collapse:separate; border-spacing:0 6px; }}
  table.timeline th {{ font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.12em;
    color:#6B6280; text-align:left; padding:0 14px 4px; }}
  table.timeline td {{ background:#FFFFFF; padding:9px 14px; font-size:14.5px;
    border-top:1px solid #E9E3DA; border-bottom:1px solid #E9E3DA; }}
  table.timeline td:first-child {{ border-left:1px solid #E9E3DA; border-radius:10px 0 0 10px; }}
  table.timeline td:last-child {{ border-right:1px solid #E9E3DA; border-radius:0 10px 10px 0; }}
  .tl-milestone {{ font-weight:700; color:#16131F; }}
  .tl-date {{ color:#3D3458; white-space:nowrap; }}
  .tl-owner {{ color:#6B6280; }}
  .lockup {{ display:flex; gap:18px; align-items:center; justify-content:center;
    font-weight:800; margin-bottom:48px; }}
  .lockup-onyx {{ font-size:30px; letter-spacing:0.04em; color:#16131F; }}
  .lockup-x {{ font-size:18px; color:#9A92A8; }}
  .lockup-cust {{ font-size:24px; letter-spacing:-0.01em; color:#16131F; }}
  .title-sub {{ font-size:18px; color:#6B6280; margin-top:26px; font-weight:500; }}
  .title-date {{ font-size:14px; color:#9A92A8; margin-top:56px; font-weight:600;
    letter-spacing:0.06em; }}
  @media print {{
    body {{ background:#FFFFFF; }}
    .slide {{ margin:0; border-radius:0; page-break-after:always; }}
    @page {{ size:1280px 720px; margin:0; }}
  }}
</style></head>
<body>{slides}</body></html>"""
