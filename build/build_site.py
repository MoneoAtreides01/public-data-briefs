"""Inject the three analysis outputs into the page template."""
from __future__ import annotations

import json

from common import OUT, ROOT

tmpl = (ROOT / "site" / "template.html").read_text(encoding="utf-8")

data = {
    "s1": json.loads((OUT / "s1_tipping.json").read_text(encoding="utf-8")),
    "s2": json.loads((OUT / "s2_groceries.json").read_text(encoding="utf-8")),
    "s3": json.loads((OUT / "s3_solar.json").read_text(encoding="utf-8")),
}

blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
if "/*__DATA__*/" not in tmpl:
    raise SystemExit("template placeholder missing")

html = tmpl.replace("/*__DATA__*/", blob)

# root index.html is what GitHub Pages serves; the site/ copy is for local browsing
for out in (ROOT / "index.html", ROOT / "site" / "index.html"):
    out.write_text(html, encoding="utf-8")
    print(f"[site] {out}  ({len(html)/1024:.1f} KB, data {len(blob)/1024:.1f} KB)")
