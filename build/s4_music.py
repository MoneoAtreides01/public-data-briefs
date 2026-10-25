"""Sample 4 - What the catalogue says about the format wars.

Source: MusicBrainz web service (public, no key). Counts of releases catalogued
per year, split by the format they were issued on.

Caveat that the brief states openly: MusicBrainz is a community catalogue, not a
market census. Its coverage grows over time and skews toward certain genres and
regions. Shares between formats in the same year are the defensible measure;
absolute counts are not.
"""
from __future__ import annotations

import pathlib
import time

import pandas as pd
import requests

from common import DATA, OUT, write_json

YEARS = range(1990, 2025)
FORMATS = ["CD", "Vinyl", "Cassette", "Digital Media"]
CACHE = DATA / "mb_format_counts.csv"

S = requests.Session()
S.headers.update({"User-Agent": "research-portfolio/1.0 (data brief sample)"})


def load_cache() -> pd.DataFrame:
    if CACHE.exists():
        return pd.read_csv(CACHE)
    return pd.DataFrame(columns=["year", "format", "count"])


def fetch(year: int, fmt: str) -> int | None:
    q = f'date:{year} AND format:"{fmt}"' if " " in fmt else f"date:{year} AND format:{fmt}"
    for attempt in range(5):
        try:
            r = S.get("https://musicbrainz.org/ws/2/release",
                      params={"query": q, "fmt": "json", "limit": 1}, timeout=60)
            if r.status_code == 200:
                return int(r.json().get("count", 0))
            if r.status_code == 503:
                time.sleep(3 * (attempt + 1))
                continue
            print(f"  {year} {fmt}: HTTP {r.status_code}")
            return None
        except Exception as exc:
            print(f"  {year} {fmt}: {type(exc).__name__}")
            time.sleep(3 * (attempt + 1))
    return None


def main() -> None:
    df = load_cache()
    have = {(int(r.year), r.format) for r in df.itertuples()}
    todo = [(y, f) for y in YEARS for f in FORMATS if (y, f) not in have]
    print(f"cached={len(df)}  to fetch={len(todo)}")

    rows = df.to_dict("records")
    for i, (y, f) in enumerate(todo, 1):
        c = fetch(y, f)
        if c is not None:
            rows.append({"year": y, "format": f, "count": c})
        if i % 10 == 0:
            pd.DataFrame(rows).to_csv(CACHE, index=False)
            print(f"  {i}/{len(todo)} done")
        time.sleep(1.1)

    df = pd.DataFrame(rows).drop_duplicates(subset=["year", "format"], keep="last")
    df = df.sort_values(["year", "format"])
    df.to_csv(CACHE, index=False)
    print(f"total rows: {len(df)}")

    wide = df.pivot(index="year", columns="format", values="count").sort_index()
    wide = wide.reindex(columns=FORMATS)
    wide["physical"] = wide[["CD", "Vinyl", "Cassette"]].sum(axis=1, min_count=1)
    wide["vinyl_share_physical"] = (wide["Vinyl"] / wide["physical"] * 100).round(1)

    print("\n=== counts by year (every 5th) ===")
    print(wide.iloc[::5].to_string())
    print("\n=== peaks ===")
    for f in FORMATS:
        s = wide[f].dropna()
        if len(s):
            print(f"{f:14s} peak {int(s.max()):>7,} in {int(s.idxmax())}   "
                  f"1990={int(s.iloc[0]) if 1990 in s.index else '-':>7}   "
                  f"latest {int(s.iloc[-1]):>7,} in {int(s.index[-1])}")
    print("\nvinyl share of physical:")
    print(wide["vinyl_share_physical"].dropna().iloc[::5].to_string())

    write_json("s4_music.json", {
        "meta": {
            "source": "MusicBrainz web service - release counts by year and format",
            "years": f"{min(YEARS)}-{max(YEARS)}",
            "caveat": "Community catalogue, not a market census; shares are the defensible measure.",
        },
        "series": [
            {"year": int(y), **{f: (None if pd.isna(wide.loc[y, f]) else int(wide.loc[y, f]))
                                for f in FORMATS},
             "physical": None if pd.isna(wide.loc[y, "physical"]) else int(wide.loc[y, "physical"]),
             "vinyl_share": None if pd.isna(wide.loc[y, "vinyl_share_physical"]) else float(wide.loc[y, "vinyl_share_physical"])}
            for y in wide.index
        ],
    })


if __name__ == "__main__":
    main()
