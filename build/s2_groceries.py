"""Sample 2 - Where the grocery bill actually went.

Source: BLS CPI-U via FRED (public CSV, no key). Seasonally adjusted, monthly.

Question: food inflation is reported as one number. Which categories actually drove
it, and how does the grocery basket compare with what wages did over the same span?
"""
from __future__ import annotations

import pandas as pd

from common import fred, write_json

START = "2020-01-01"

SERIES = {
    "CUSR0000SAF11":  "Food at home",
    "CUSR0000SAF111": "Cereals & bakery",
    "CUSR0000SAF112": "Meat, poultry, fish & eggs",
    "CUSR0000SAF113": "Dairy",
    "CUSR0000SAF114": "Fruit & vegetables",
    "CUSR0000SAF115": "Nonalcoholic beverages",
    "CUSR0000SAF116": "Other food at home",
    "CUSR0000SEFV":   "Food away from home",
    "CPIAUCSL":       "All items (CPI)",
}
WAGES = "CES0500000003"

frames = {}
for sid in list(SERIES) + [WAGES]:
    s = fred(sid).set_index("date")["value"]
    frames[sid] = s

start = pd.Timestamp(START)
last = min(s.index.max() for s in frames.values())
print(f"window: {start.date()} -> {last.date()}\n")

rows = []
for sid, label in SERIES.items():
    s = frames[sid]
    base = s[s.index >= start].iloc[0]
    end = s.loc[:last].iloc[-1]
    peak = s[s.index >= start].max()
    rows.append({
        "series": sid,
        "label": label,
        "base": round(float(base), 1),
        "now": round(float(end), 1),
        "chg_pct": round((end / base - 1) * 100, 1),
        "peak_chg_pct": round((peak / base - 1) * 100, 1),
        "from_peak_pct": round((end / peak - 1) * 100, 1),
    })

w = frames[WAGES]
w_base = w[w.index >= start].iloc[0]
w_now = w.loc[:last].iloc[-1]
wage_pct = (w_now / w_base - 1) * 100

out = pd.DataFrame(rows).sort_values("chg_pct", ascending=False)
cpis = out[out.series == "CPIAUCSL"].iloc[0]
fah = out[out.series == "CUSR0000SAF11"].iloc[0]
fav = out[out.series == "CUSR0000SEFV"].iloc[0]

print("=== cumulative change since Jan 2020 (to %s) ===" % last.date())
print(out[["label", "chg_pct", "peak_chg_pct", "from_peak_pct"]].to_string(index=False))
print()
print(f"wages (avg hourly earnings) : +{wage_pct:.1f}%")
print(f"food at home real change    : {fah.chg_pct - wage_pct:+.1f} pp vs wages")
print(f"food away real change       : {fav.chg_pct - wage_pct:+.1f} pp vs wages")
print(f"all items real change       : {cpis.chg_pct - wage_pct:+.1f} pp vs wages")
print()
print("=== from peak: which baskets have actually come down ===")
print(out.sort_values("from_peak_pct")[["label", "peak_chg_pct", "from_peak_pct"]].to_string(index=False))

# monthly paths, indexed to 100 at the window open - one axis, comparable
LINE = {
    "CUSR0000SAF11": "Food at home",
    "CUSR0000SEFV": "Food away from home",
    "CPIAUCSL": "All items",
    WAGES: "Average hourly earnings",
}
indexed = {}
for sid, label in LINE.items():
    s = frames[sid]
    s = s[(s.index >= start) & (s.index <= last)]
    indexed[label] = [
        {"d": d.strftime("%Y-%m"), "v": round(float(v / s.iloc[0] * 100), 2)}
        for d, v in s.items()
    ]

write_json("s2_groceries.json", {
    "meta": {
        "source": "BLS CPI-U (seasonally adjusted) and CES average hourly earnings, via FRED",
        "window": f"{start.date()} to {last.date()}",
    },
    "wage_growth_pct": round(float(wage_pct), 1),
    "categories": out.to_dict("records"),
    "indexed": indexed,
})
