"""Sample 3 - The solar learning curve, 50 years on.

Sources (public, no key):
  OWID    - solar PV module cost ($/W, 1975-2024)
  OWID    - installed solar PV capacity, world (GW, 2000-2025)
  OWID/Lazard - levelised cost of energy by technology

Question: how disciplined is the price decline? Fit the experience curve and ask
whether the relationship held through the 2021-22 supply shock.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import owid, write_json

price = owid("solar-pv-prices").rename(columns={"Solar PV module cost": "usd_per_w"})
cap = owid("installed-solar-pv-capacity")
cap = cap[cap.Entity == "World"][["Year", "Solar"]].rename(columns={"Solar": "gw"})

m = price[["Year", "usd_per_w"]].merge(cap, on="Year", how="inner")
m = m[(m.usd_per_w > 0) & (m.gw > 0)].sort_values("Year").reset_index(drop=True)

# experience curve: log(price) = a + b * log(cumulative capacity)
x = np.log(m.gw.values)
y = np.log(m.usd_per_w.values)
b, a = np.polyfit(x, y, 1)
pred = a + b * x
ss_res = ((y - pred) ** 2).sum()
ss_tot = ((y - y.mean()) ** 2).sum()
r2 = 1 - ss_res / ss_tot
learning_rate = (1 - 2 ** b) * 100      # price fall per doubling of cumulative capacity

m["fit"] = np.exp(pred)

print(f"observations          : {len(m)}  ({m.Year.min()}-{m.Year.max()})")
print(f"price  first -> last  : ${m.usd_per_w.iloc[0]:.3f}/W -> ${m.usd_per_w.iloc[-1]:.3f}/W")
print(f"total decline         : {(m.usd_per_w.iloc[-1] / m.usd_per_w.iloc[0] - 1) * 100:.1f}%")
print(f"capacity first -> last: {m.gw.iloc[0]:,.0f} GW -> {m.gw.iloc[-1]:,.0f} GW "
      f"({m.gw.iloc[-1] / m.gw.iloc[0]:.0f}x)")
print(f"learning rate         : {learning_rate:.1f}% per doubling   (slope {b:.3f}, R2 {r2:.4f})")
print()
m = m.assign(resid_pct=(m.usd_per_w / m.fit - 1) * 100)
worst = m.reindex(m.resid_pct.abs().sort_values(ascending=False).index).head(8)
print("largest deviations from the fitted curve:")
print(worst[["Year", "usd_per_w", "gw", "resid_pct"]].round(1).to_string(index=False))

# --- companion: LCOE by technology, world ---
lcoe = owid("levelized-cost-of-energy")
w = lcoe[lcoe.Entity == "World"].set_index("Year")
techs = ["Solar photovoltaic", "Onshore wind", "Offshore wind", "Hydropower",
         "Bioenergy", "Geothermal", "Concentrated solar power"]
lo, hi = 2010, 2025
w = w.loc[(w.index >= lo) & (w.index <= hi), techs]
first_last = pd.DataFrame({
    "tech": techs,
    "y0": [w[t].dropna().iloc[0] for t in techs],
    "y0_year": [int(w[t].dropna().index[0]) for t in techs],
    "y1": [w[t].dropna().iloc[-1] for t in techs],
    "y1_year": [int(w[t].dropna().index[-1]) for t in techs],
})
first_last["chg_pct"] = (first_last.y1 / first_last.y0 - 1) * 100
print()
print("LCOE, first vs latest available (USD/kWh):")
print(first_last.round(3).to_string(index=False))

lcoe_series = {}
for t in techs:
    s = w[t].dropna()
    lcoe_series[t] = [{"year": int(y), "v": round(float(v), 4)} for y, v in s.items()]

write_json("s3_solar.json", {
    "meta": {
        "source": "IRENA/Lazard via Our World in Data - solar PV module cost, installed capacity, LCOE",
    },
    "fit": {"slope": round(float(b), 4), "intercept": round(float(a), 4),
            "r2": round(float(r2), 4), "learning_rate_pct": round(float(learning_rate), 1),
            "n": int(len(m))},
    "series": m.assign(fit=m.fit.round(5))[
        ["Year", "gw", "usd_per_w", "fit"]
    ].round(5).to_dict("records"),
    "lcoe": first_last.round(4).to_dict("records"),
    "lcoe_series": lcoe_series,
})
