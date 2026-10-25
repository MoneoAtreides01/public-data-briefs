# Public data briefs

Three worked analyses, each from a public source, each ending in one sentence a
non-specialist can act on. Charts are drawn by hand in SVG; there is no charting
library and no build step to view the page.

Open `index.html` directly, or view the published page.

## The briefs

| # | Question | Finding | Method |
|---|----------|---------|--------|
| 01 | When did national grids tip to majority-renewable? | 16 joined and 10 left the 50% club since 2000. All ten leavers were hydro-only at the start; five of the seven arrivals since 2020 came on wind and solar. | Cohort analysis across 156 countries |
| 02 | Where did the grocery bill actually go? | Food at home +31.9% since Jan 2020, average hourly earnings +33.0%. The gap opened at restaurants, +37.9%. | Indexing, real-terms comparison |
| 03 | How disciplined is solar's price decline? | 27.7% price fall per doubling of installed capacity, R² 0.96, with a documented 2008–11 excursion. | Log-log OLS experience curve |

## Sources — all public, no API key

- **Ember** electricity shares via Our World in Data (renewables, wind, solar)
- **World Bank** population, used only to drop territories under one million people
- **BLS** CPI-U (seasonally adjusted) and CES average hourly earnings, via FRED
- **IRENA / Lazard** solar module cost, installed capacity and LCOE, via Our World in Data

## Reproduce

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install pandas matplotlib requests
cd build
..\.venv\Scripts\python.exe s1_tipping.py
..\.venv\Scripts\python.exe s2_groceries.py
..\.venv\Scripts\python.exe s3_solar.py
..\.venv\Scripts\python.exe build_site.py
```

Raw downloads are cached in `data/`; delete a file there to refetch it. Each script
writes its results to `build/out/`, and `build_site.py` inlines them into
`site/template.html` to produce `index.html`.

## Definitions

- *Majority renewable* — renewables supplied at least 50% of electricity
  **generation** in that year.
- *Latest year* — 2024 or 2025, depending on what the country reports; the chart
  and the table view both say which.
- *Wages* — average hourly earnings, total private. An economy-wide average, not a
  household measure.
- *Learning rate* — 1 − 2^slope, from an OLS fit of log price on log cumulative
  installed capacity.

## Caveats these briefs state themselves

- Brief 01 counts hydro as renewable. That is the point of the finding, not an
  oversight: the leavers were hydro-dependent and the arrivals are not.
- Brief 02's wage comparison is aggregate, not household-level. Regional prices,
  basket composition and median income all differ from the national series.
- Brief 03's module price excludes installation, land and financing, which have
  fallen more slowly.
