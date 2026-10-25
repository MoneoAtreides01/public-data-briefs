import io
import re
import pandas as pd
import requests

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 research-portfolio"})

CAND = [
    "REVLMREF51222ALLEST", "REVLMREF51223ALLEST",
    "REVSLREF51222ALLEST", "REVSLREF51223ALLEST",
    "REVLMCEF51222ALLEST", "CUSR0000SERE03",
]

for sid in CAND:
    try:
        r = S.get(f"https://fred.stlouisfed.org/series/{sid}", timeout=45)
        title = "?"
        if r.status_code == 200:
            m = re.search(r"<title>(.*?)</title>", r.text, re.S)
            title = re.sub(r"\s+", " ", m.group(1)).strip() if m else "?"
            m2 = re.search(r"Frequency:\s*</span>.*?>\s*([A-Za-z ]+?)\s*<", r.text, re.S)
        print(f"{sid:22s} HTTP {r.status_code}  {title[:120]}")

        d = S.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=45)
        if d.status_code == 200:
            df = pd.read_csv(io.StringIO(d.text))
            df.columns = ["date", "v"]
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["v"] = pd.to_numeric(df["v"], errors="coerce")
            df = df.dropna()
            if len(df):
                print(f"    n={len(df)}  {df.date.min().date()} -> {df.date.max().date()}  "
                      f"first={df.v.iloc[0]:.0f} last={df.v.iloc[-1]:.0f}  "
                      f"min={df.v.min():.0f} max={df.v.max():.0f}")
                print("    tail:", ", ".join(
                    f"{d.year}={v:.0f}" for d, v in zip(df.date.tail(6), df.v.tail(6))))
    except Exception as e:
        print(f"{sid:22s} FAIL {type(e).__name__} {e}")
