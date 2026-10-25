"""Sample 1 - When did each national grid tip to majority renewable?

Sources (public, no key):
  OWID / Ember  - share of electricity from renewables, wind, solar (annual, 2000-2025)
  World Bank    - population (used only to drop micro-territories from the sample)

Question: the club of majority-renewable grids has grown. Is the *kind* of entrant
changing - are new members arriving on wind and solar rather than hydro?
"""
from __future__ import annotations

import pandas as pd

from common import iso_countries, owid, worldbank, write_json

START, END, THRESH = 2000, 2025, 50.0
MIN_POP = 1_000_000

ren = owid("share-electricity-renewables").rename(columns={"Renewables": "renew"})
wind = owid("share-electricity-wind").rename(columns={"Wind": "wind"})
solar = owid("share-electricity-solar").rename(columns={"Solar": "solar"})

df = (
    ren[["Entity", "Code", "Year", "renew"]]
    .merge(wind[["Code", "Year", "wind"]], on=["Code", "Year"], how="left")
    .merge(solar[["Code", "Year", "solar"]], on=["Code", "Year"], how="left")
)
df = iso_countries(df)
df = df[(df.Year >= START) & (df.Year <= END)].copy()
df["wind"] = df["wind"].fillna(0.0)
df["solar"] = df["solar"].fillna(0.0)
df["vres"] = df["wind"] + df["solar"]

pop = worldbank("SP.POP.TOTL", "2023")

rows = []
dropped_pop, dropped_short = [], []
for entity, g in df.groupby("Entity"):
    g = g.sort_values("Year")
    code = g["Code"].iloc[0]

    if pop.get(code, 0) < MIN_POP:                       # micro-territories out
        dropped_pop.append(entity)
        continue
    if g["renew"].notna().sum() < 12:
        dropped_short.append(entity)
        continue

    first = g.iloc[0]
    tail = g[g.Year >= 2024]
    if pd.isna(first["renew"]) or tail.empty:            # need both ends of the window
        dropped_short.append(entity)
        continue
    last = tail.iloc[-1]

    hit = g[(g["renew"] >= THRESH) & g["renew"].notna()]
    cross_year = int(hit["Year"].iloc[0]) if len(hit) else None
    already = bool(first["renew"] >= THRESH)

    kind = vres_at = None
    if cross_year is not None:
        at = g[g.Year == cross_year].iloc[0]
        vres_at = round(float(at["vres"]), 1)
        kind = "wind & solar" if vres_at >= 20 else ("mixed" if vres_at >= 8 else "hydro")

    rows.append({
        "country": entity,
        "code": code,
        "population_m": round(pop.get(code, 0) / 1e6, 1),
        "renew_first": round(float(first["renew"]), 1),
        "first_year": int(first["Year"]),
        "renew_last": round(float(last["renew"]), 1),
        "last_year": int(last["Year"]),
        "vres_last": round(float(last["vres"]), 1),
        "already": already,
        "cross_year": cross_year,
        "kind": kind,
    })

res = pd.DataFrame(rows)
res["delta"] = res["renew_last"] - res["renew_first"]
res["majority_first"] = res["renew_first"] >= THRESH
res["majority_last"] = res["renew_last"] >= THRESH

entrants = res[res["majority_last"] & ~res["majority_first"]]
exiters = res[res["majority_first"] & ~res["majority_last"]]

print(f"sample: {len(res)} countries (pop >= 1M, usable series)")
print(f"  dropped - micro-territory : {len(dropped_pop)}  e.g. {dropped_pop[:6]}")
print(f"  dropped - short/incomplete: {len(dropped_short)}")
print()
print(f"majority-renewable at window open : {int(res['majority_first'].sum())}")
print(f"majority-renewable at window close: {int(res['majority_last'].sum())}")
print(f"entrants during window            : {len(entrants)}")
print(f"exits during window               : {len(exiters)}")
print()
print("entrants by kind:")
print(entrants["kind"].value_counts().to_string())
print()
e = entrants.copy()
e["decade"] = (e["cross_year"] // 10 * 10).astype(int)
print("entrants by decade x kind:")
print(e.groupby(["decade", "kind"]).size().unstack(fill_value=0).to_string())
print()
print("=== entrants, chronological ===")
print(e.sort_values("cross_year")[
    ["country", "cross_year", "renew_first", "renew_last", "vres_last", "kind"]
].to_string(index=False))
print()
print("=== exits (majority-renewable at open, not at close) ===")
print(exiters.sort_values("delta")[
    ["country", "renew_first", "renew_last", "delta", "population_m"]
].to_string(index=False))

write_json("s1_tipping.json", {
    "meta": {
        "source": "Ember via Our World in Data (electricity shares); World Bank (population filter)",
        "window": f"{START}-{END}", "threshold": THRESH, "min_population": MIN_POP,
    },
    "summary": {
        "sample": int(len(res)),
        "majority_first": int(res["majority_first"].sum()),
        "majority_last": int(res["majority_last"].sum()),
        "entrants": int(len(entrants)),
        "exits": int(len(exiters)),
        "entrants_by_kind": entrants["kind"].value_counts().to_dict(),
        "entrants_by_decade": e.groupby("decade").size().to_dict(),
    },
    "entrants": e.sort_values("cross_year")[
        ["country", "code", "cross_year", "kind", "renew_first", "renew_last", "vres_last"]
    ].to_dict("records"),
    "exits": exiters.sort_values("delta")[
        ["country", "code", "renew_first", "renew_last", "delta"]
    ].to_dict("records"),
    "members_last": res[res["majority_last"]].sort_values("renew_last", ascending=False)[
        ["country", "code", "renew_last", "vres_last", "kind", "cross_year", "already"]
    ].to_dict("records"),
})
