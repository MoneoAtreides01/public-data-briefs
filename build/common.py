"""Shared fetch / cache helpers for the portfolio samples.

Every figure in the portfolio is reproducible from a public source with no API key.
Raw downloads are cached in ../data so re-runs are offline and fast.
"""
from __future__ import annotations

import io
import json
import pathlib
import time

import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "build" / "out"
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

S = requests.Session()
S.headers.update({"User-Agent": "research-portfolio/1.0 (public data)"})


def _get(url: str, cache: pathlib.Path, attempts: int = 5) -> bytes:
    if cache.exists() and cache.stat().st_size > 0:
        return cache.read_bytes()
    last = None
    for i in range(attempts):
        try:
            r = S.get(url, timeout=90)
            r.raise_for_status()
            cache.write_bytes(r.content)
            return r.content
        except Exception as exc:  # SSL flakes on some hosts are transient
            last = exc
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def owid(slug: str) -> pd.DataFrame:
    raw = _get(
        f"https://ourworldindata.org/grapher/{slug}.csv",
        DATA / f"owid_{slug}.csv",
    )
    return pd.read_csv(io.StringIO(raw.decode("utf-8", "replace")))


def fred(series_id: str) -> pd.DataFrame:
    raw = _get(
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
        DATA / f"fred_{series_id}.csv",
    )
    df = pd.read_csv(io.StringIO(raw.decode("utf-8", "replace")))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna()


def worldbank(indicator: str, year: str = "2023") -> dict[str, float]:
    """ISO3 -> value for one World Bank indicator (no key required)."""
    raw = _get(
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        f"?format=json&per_page=20000&date={year}",
        DATA / f"wb_{indicator}_{year}.json",
    )
    payload = json.loads(raw.decode("utf-8", "replace"))
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    return {
        r["countryiso3code"]: r["value"]
        for r in rows
        if r.get("countryiso3code") and r.get("value") is not None
    }


def iso_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Keep real countries only - OWID aggregates carry OWID_* / regional codes."""
    code = df["Code"].astype("string")
    return df[code.notna() & (code.str.len() == 3) & code.str.fullmatch(r"[A-Z]{3}")]


def write_json(name: str, payload) -> pathlib.Path:
    path = OUT / name
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[json] {path}")
    return path
