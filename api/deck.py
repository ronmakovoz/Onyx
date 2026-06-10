"""
Renders the KickoffDeckAgent's structured output as a branded, self-contained
HTML slide deck (16:9). Matches Onyx Security's deck style: warm cream
background, near-black display headings, white rounded cards, lavender
accents, lowercase "onyx" wordmark, subtle circuit-trace motif.

Open in a browser to present (arrow keys / scroll), or print to PDF
(each slide is one landscape page).
"""

import html
import math
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


# ── Content-aware slide packing ───────────────────────────────────────────────
# Slides are fixed 1280×720; live model output is much longer than mock output,
# so lists must be measured and split across slides instead of overflowing.

_COL_BUDGET = 520   # usable px for cards in one column of a two-column slide
_FULL_BUDGET = 500  # usable px for full-width cards under an h2


def _card_h(text: str, chars_per_line: int) -> int:
    lines = max(1, math.ceil(len(str(text)) / chars_per_line))
    return 44 + lines * 23 + 12  # padding + text lines + gap


def _col_h(items: list) -> int:
    return sum(_card_h(i, 50) for i in items)


def _chunk_full(items: list, budget: int = _FULL_BUDGET) -> list[list]:
    """Split items into chunks that each fit a full-width slide."""
    chunks, cur, h = [], [], 0
    for it in items:
        ih = _card_h(it, 105)
        if cur and h + ih > budget:
            chunks.append(cur)
            cur, h = [], 0
        cur.append(it)
        h += ih
    if cur:
        chunks.append(cur)
    return chunks


def _list_section_slides(heading: str, items: list, icon: str = "→") -> str:
    """One or more full-width slides for a list, chunked to fit."""
    out = ""
    for n, chunk in enumerate(_chunk_full(items)):
        h = heading if n == 0 else f"{heading} (cont.)"
        out += _slide(f"<h2>{h}</h2>{_card_list(chunk, icon)}")
    return out


def _two_lists_slides(h_a: str, items_a: list, icon_a: str,
                      h_b: str, items_b: list, icon_b: str) -> str:
    """Side-by-side columns when both lists fit; separate chunked slides otherwise."""
    if _col_h(items_a) <= _COL_BUDGET and _col_h(items_b) <= _COL_BUDGET:
        return _slide(
            f'<div class="cols"><div><h2>{h_a}</h2>{_card_list(items_a, icon_a)}</div>'
            f'<div><h2>{h_b}</h2>{_card_list(items_b, icon_b)}</div></div>'
        )
    return _list_section_slides(h_a, items_a, icon_a) + _list_section_slides(h_b, items_b, icon_b)


AGENT_DECK_TITLES = {
    "CustomerHealthAgent":       "Customer Health Assessment",
    "ImplementationAgent":       "Implementation Report",
    "BriefingAgent":             "Executive Briefing",
    "EscalationCommanderAgent":  "Escalation Command Plan",
    "SkeptikQAAgent":            "Skeptik QA Review",
    "VPChiefOfStaffAgent":       "VP Weekly Review",
    "ExpansionOpportunityAgent": "Expansion Opportunity",
    "QBRPreparationAgent":       "Quarterly Business Review",
    "SuccessPlanAgent":          "Success Plan",
}


def _humanize(field: str) -> str:
    words = field.replace("_", " ").strip()
    fixes = {"arr": "ARR", "qbr": "QBR", "ceo": "CEO", "nrr": "NRR", "30 60 90": "30 / 60 / 90",
             "2wks": "2 weeks", "48h": "48 hours", "5": "5"}
    out = []
    for w in words.split():
        out.append(fixes.get(w.lower(), w))
    s = " ".join(out)
    return s[:1].upper() + s[1:]


def _md_table_to_html(text: str) -> str:
    """Convert a string containing a markdown table into prose + an HTML table."""
    table_rows, prose = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):
            if set(s) <= {"|", "-", " ", ":"}:
                continue  # separator row
            cells = [c.strip() for c in s.strip("|").split("|")]
            table_rows.append(cells)
        elif s:
            prose.append(s)
    out = ""
    if prose:
        out += f'<p class="lede">{_esc(" ".join(prose))}</p>'
    if table_rows:
        head = "".join(f"<th>{_esc(c)}</th>" for c in table_rows[0])
        body = "".join(
            "<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in row) + "</tr>"
            for row in table_rows[1:]
        )
        out += f'<table class="timeline"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
    return out


def render_generic_deck(agent_name: str, structured: dict, ctx: dict) -> str:
    """Render any agent's structured output as a branded slide deck.

    Short scalar fields become stat tiles on an "At a glance" slide; string
    fields become statement paragraphs (markdown tables converted to real
    tables); list fields become card grids packed two sections per slide.
    """
    customer = ctx.get("customer_name") or "Portfolio"
    title = AGENT_DECK_TITLES.get(agent_name, agent_name.replace("Agent", " Report"))
    date_str = datetime.now().strftime("%B %Y")

    # Build sections in dataclass field order
    stats: list[tuple[str, str]] = []          # (label, value) → "At a glance" tiles
    sections: list[tuple[str, str, int]] = []  # (heading, html, weight 1..2)
    for field, val in structured.items():
        if val in (None, "", [], 0) or isinstance(val, bool):
            continue
        heading = _humanize(field)
        if isinstance(val, (int, float)):
            if "arr" in field:
                stats.append((heading, f"${val:,.0f}"))
            elif "confidence" in field and val <= 1:
                stats.append((heading, f"{val:.0%}"))
            else:
                stats.append((heading, f"{val:,}" if isinstance(val, int) else str(val)))
        elif isinstance(val, str):
            if "|" in val and val.count("|") >= 4:
                sections.append((heading, _md_table_to_html(val), 2))
            elif len(val) <= 60 and "\n" not in val:
                stats.append((heading, val))
            else:
                sections.append((heading, f'<p class="lede">{_esc(val)}</p>', 1))
        elif isinstance(val, list):
            icon = "✓" if any(k in field for k in ("positive", "metric", "value", "proof")) else "→"
            if _col_h(val) <= _COL_BUDGET:
                sections.append((heading, _card_list(val, icon), 1))
            else:
                # Too tall for a shared slide — full-width chunks, one per slide
                for n, chunk in enumerate(_chunk_full(val)):
                    h = heading if n == 0 else f"{heading} (cont.)"
                    sections.append((h, _card_list(chunk, icon), 2))

    if stats:
        tiles = "".join(
            f'<div class="stat-tile"><div class="stat-label">{_esc(l)}</div>'
            f'<div class="stat-value">{_esc(v)}</div></div>'
            for l, v in stats[:8]
        )
        sections.insert(0, ("At a glance", f'<div class="stat-grid">{tiles}</div>', 2))

    # Pack sections into slides — max weight 2 per slide
    slides_html = ""
    i = 0
    while i < len(sections):
        h1s, b1, w1 = sections[i]
        if w1 >= 2 or i + 1 >= len(sections) or sections[i + 1][2] >= 2:
            slides_html += _slide(f"<h2>{h1s}</h2>{b1}")
            i += 1
        else:
            h2s, b2, _ = sections[i + 1]
            slides_html += _slide(
                f'<div class="cols"><div><h2>{h1s}</h2>{b1}</div><div><h2>{h2s}</h2>{b2}</div></div>'
            )
            i += 2

    title_slide = _slide(f"""
      <div class="title-wrap">
        <div class="lockup"><span class="lockup-onyx">onyx</span><span class="lockup-x">✕</span><span class="lockup-cust">{_esc(customer)}</span></div>
        <h1 class="display">{_esc(title)}</h1>
        <div class="title-sub">{_esc(customer)} · Prepared by Onyx CX Agent OS</div>
        <div class="title-date">{date_str} · INTERNAL</div>
      </div>""", "center")

    closing = _slide(f"""
      <div class="title-wrap">
        <h1 class="display">Questions?</h1>
        <div class="title-sub">Onyx Security · {date_str}</div>
      </div>""", "center")

    return _page(f"{title} — {customer}", title_slide + slides_html + closing)


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

    # ── Slide 2: Vision + Scope (scope moves to its own slide when long) ─────
    grid2_h = sum(
        max(_card_h(a, 50), _card_h(b, 50) if b is not None else 0)
        for a, b in zip(scope[0::2], list(scope[1::2]) + [None])
    )
    vision_h = math.ceil(len(vision) / 105) * 26
    if vision_h + 40 + grid2_h <= 500:
        s2 = _slide(f"""
          <h2>Our partnership</h2>
          <p class="lede">{_esc(vision)}</p>
          <div class="label">Scope &amp; objectives</div>
          <div class="grid-2">{_card_list(scope, "◆")}</div>""")
    else:
        s2 = _slide(f'<h2>Our partnership</h2><p class="lede">{_esc(vision)}</p>')
        s2 += _list_section_slides("Scope & objectives", scope, "◆")

    # ── Slide 3: How Onyx deploys (standard integration story) ───────────────
    pillars = [
        ("Unified Control Plane",
         f"One console for every AI agent and model across SaaS, cloud, endpoint, and code. "
         f"We integrate with {_esc(customer)}'s browser, AI platforms, CNAPP, SASE, and EDR "
         f"discovery sources so nothing is invisible."),
        ("Flexible Deployment",
         "Cloud, hybrid, or self-hosted options for sensitive data residency requirements. "
         "Deploy in hours with support for AWS VPC, Bedrock Gateway, and custom proxy configurations."),
        ("Seamless Integrations",
         "Connect to any agent platform, frontier model provider, SIEM, or cloud platform with "
         "100+ pre-built integrations — including AWS, GCP, Azure, OpenAI, Anthropic, and more."),
    ]
    pillar_cards = "".join(
        f'<div class="pillar"><div class="pillar-title">{t}</div><div class="pillar-body">{b}</div></div>'
        for t, b in pillars
    )
    s2b = _slide(f"""
      <h2>Deploy in hours. Scale without limits.</h2>
      <p class="lede">Onyx meets you where you are — whether you're running on-prem, in the cloud,
      or in a hybrid environment. Built for security-first enterprises from day one.</p>
      <div class="grid-3">{pillar_cards}</div>""")

    # ── Slide 4: Engagement Team ──────────────────────────────────────────────
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

    # ── Slide 5: Success Metrics + First 30 Days (split when long) ──────────
    s5 = _two_lists_slides("How we measure success", metrics, "✓",
                           "The first 30 days", first30, "→")

    # ── Slide 6: Governance + Prerequisites (split when long) ───────────────
    gov_h = 62 + math.ceil(len(governance) / 50) * 26
    if gov_h <= _COL_BUDGET and _col_h(prereqs) <= _COL_BUDGET:
        s6 = _slide(f"""
          <div class="cols">
            <div><h2>Communication &amp; governance</h2><p class="lede">{_esc(governance)}</p></div>
            <div><h2>What we need from you</h2>{_card_list(prereqs, "◆")}</div>
          </div>""")
    else:
        s6 = _slide(f'<h2>Communication &amp; governance</h2><p class="lede">{_esc(governance)}</p>')
        s6 += _list_section_slides("What we need from you", prereqs, "◆")

    # ── Slide 7: Closing ──────────────────────────────────────────────────────
    s7 = _slide(f"""
      <div class="title-wrap">
        <h1 class="display">Let's get started.</h1>
        <div class="title-sub">Onyx Security ✕ {_esc(customer)} · {date_str}</div>
      </div>""", "center")

    slides = s1 + s2 + s2b + s3 + s4 + s5 + s6 + s7
    return _page(f"Implementation Kickoff — {customer}", slides)


def _page(title: str, slides: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{_esc(title)} · Onyx Security</title>
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
  .pillar {{ background:#FAEDF0; border:1px solid #F0DDE2; border-radius:16px; padding:26px 24px; }}
  .pillar-title {{ font-size:22px; font-weight:800; letter-spacing:-0.01em; color:#16131F;
    margin-bottom:10px; }}
  .pillar-body {{ font-size:14.5px; line-height:1.6; color:#3D3458; }}
  .bigstat {{ font-size:72px; font-weight:800; letter-spacing:-0.03em; color:#16131F; }}
  .stat-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }}
  .stat-tile {{ background:#FFFFFF; border:1px solid #E9E3DA; border-radius:14px;
    padding:20px 22px; box-shadow:0 1px 3px rgba(27,16,64,0.04); }}
  .stat-label {{ font-size:11px; font-weight:800; text-transform:uppercase;
    letter-spacing:0.10em; color:#6B6280; margin-bottom:8px; }}
  .stat-value {{ font-size:26px; font-weight:800; letter-spacing:-0.02em; color:#16131F;
    line-height:1.15; }}
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
