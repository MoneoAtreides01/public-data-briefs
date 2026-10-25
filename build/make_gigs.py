"""Generate three Fiverr gig images as 1280x769 HTML, for Chrome to rasterise."""
from __future__ import annotations

import pathlib

OUT = pathlib.Path(r"C:\Users\liama\FREELANCE\site\gigs")
OUT.mkdir(parents=True, exist_ok=True)

HEAD = """<meta charset="utf-8">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{width:1280px;height:769px;overflow:hidden}}
  body{{
    background:#f2f4f1;color:#0f1713;
    font-family:'IBM Plex Sans',system-ui,sans-serif;
    padding:64px 72px;position:relative;
    display:flex;flex-direction:column;justify-content:space-between;
  }}
  .bgbar{{position:absolute;left:0;top:0;width:100%;height:8px;background:#0f6b4f}}
  .eyebrow{{font-family:'IBM Plex Mono',monospace;font-size:19px;letter-spacing:.18em;
    text-transform:uppercase;color:#0b5440;font-weight:500}}
  h1{{font-family:'Source Serif 4',Georgia,serif;font-weight:600;font-size:82px;
    line-height:1.02;letter-spacing:-.022em;max-width:940px;margin-top:34px;text-wrap:balance}}
  h1 em{{font-style:normal;color:#0f6b4f}}
  .foot{{display:flex;align-items:flex-end;justify-content:space-between;gap:40px}}
  .sub{{font-size:25px;line-height:1.45;color:#4a5650;max-width:620px}}
  .sub b{{color:#0f1713;font-weight:500}}
  .rule{{height:1px;background:#c6cfc7;margin:26px 0 0;width:60%}}
  .viz{{flex:none}}
  .tag{{position:absolute;right:72px;top:64px;font-family:'IBM Plex Mono',monospace;
    font-size:17px;letter-spacing:.1em;text-transform:uppercase;color:#78847d;
    border:1px solid #c6cfc7;border-radius:100px;padding:9px 20px}}
</style>
"""

PAGE = """<!doctype html><html><head>{head}</head><body>
<div class="bgbar"></div>
<div class="tag">{tag}</div>
<div>
  <div class="eyebrow">{eyebrow}</div>
  <h1>{headline}</h1>
</div>
<div>
  <div class="rule"></div>
  <div class="foot">
    <div class="sub">{sub}</div>
    <div class="viz">{viz}</div>
  </div>
</div>
</body></html>"""

# ---- visuals -------------------------------------------------------------
V1 = """<svg width="330" height="190" viewBox="0 0 330 190" fill="none">
  <path d="M6 168 L74 150 L142 118 L210 92 L278 54 L324 34" stroke="#2a78d6" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M6 176 L74 172 L142 160 L210 148 L278 132 L324 120" stroke="#1baf7a" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M6 182 L74 178 L142 174 L210 168 L278 164 L324 158" stroke="#8d978f" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="324" cy="34" r="7" fill="#2a78d6" stroke="#f2f4f1" stroke-width="3"/>
  <circle cx="324" cy="120" r="7" fill="#1baf7a" stroke="#f2f4f1" stroke-width="3"/>
</svg>"""

V2 = """<svg width="330" height="190" viewBox="0 0 330 190" fill="none">
  <g fill="#cdd5cf">
    <rect x="0" y="0" width="52" height="40" rx="5"/><rect x="66" y="0" width="52" height="40" rx="5"/>
    <rect x="132" y="0" width="52" height="40" rx="5" fill="#e6c1b2"/><rect x="198" y="0" width="52" height="40" rx="5"/>
    <rect x="264" y="0" width="52" height="40" rx="5"/>
    <rect x="0" y="54" width="52" height="40" rx="5"/><rect x="66" y="54" width="52" height="40" rx="5" fill="#e6c1b2"/>
    <rect x="132" y="54" width="52" height="40" rx="5"/><rect x="198" y="54" width="52" height="40" rx="5"/>
    <rect x="264" y="54" width="52" height="40" rx="5"/>
  </g>
  <g fill="#1baf7a">
    <rect x="0" y="108" width="52" height="40" rx="5"/><rect x="66" y="108" width="52" height="40" rx="5"/>
    <rect x="132" y="108" width="52" height="40" rx="5"/><rect x="198" y="108" width="52" height="40" rx="5"/>
    <rect x="264" y="108" width="52" height="40" rx="5"/>
    <rect x="0" y="162" width="52" height="28" rx="5"/><rect x="66" y="162" width="52" height="28" rx="5"/>
    <rect x="132" y="162" width="52" height="28" rx="5"/><rect x="198" y="162" width="52" height="28" rx="5"/>
    <rect x="264" y="162" width="52" height="28" rx="5"/>
  </g>
</svg>"""

V3 = """<svg width="330" height="190" viewBox="0 0 330 190" fill="none">
  <g fill="#2a78d6">
    <rect x="0" y="10" width="300" height="26" rx="6"/>
    <rect x="0" y="60" width="232" height="26" rx="6"/>
    <rect x="0" y="110" width="168" height="26" rx="6"/>
  </g>
  <g fill="#9aa6a0">
    <rect x="0" y="160" width="104" height="26" rx="6"/>
  </g>
  <line x1="248" y1="0" x2="248" y2="190" stroke="#0f1713" stroke-width="2" stroke-opacity=".35"/>
</svg>"""

GIGS = [
    dict(
        slug="gig-1-brief",
        title="Gig 1",
        tag="Brief",
        eyebrow="Research &amp; data",
        headline="The finding, not<br>just the <em>chart</em>.",
        sub="A public dataset, checked and analysed, delivered as a <b>short brief that ends in one clear answer</b>.",
        viz=V1,
    ),
    dict(
        slug="gig-2-clean",
        title="Gig 2",
        tag="Cleanup",
        eyebrow="Research &amp; data",
        headline="Messy data in.<br><em>Clean file out</em>.",
        sub="Duplicates resolved, types and units normalised, missing values documented — <b>with a schema note and the script</b>.",
        viz=V2,
    ),
    dict(
        slug="gig-3-market",
        title="Gig 3",
        tag="Market brief",
        eyebrow="Research &amp; data",
        headline="Every number,<br>with its <em>source</em>.",
        sub="Market and competitor briefs that state their boundary, show the working, <b>and say what they can't confirm</b>.",
        viz=V3,
    ),
]

for g in GIGS:
    head = HEAD.format(title=g["title"])
    html = PAGE.format(
        head=head, tag=g["tag"], eyebrow=g["eyebrow"],
        headline=g["headline"], sub=g["sub"], viz=g["viz"],
    )
    path = OUT / f"{g['slug']}.html"
    path.write_text(html, encoding="utf-8")
    print(f"[gig] {path}")
