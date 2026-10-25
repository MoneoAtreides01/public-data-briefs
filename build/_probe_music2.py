import re
import io
import pandas as pd
import requests

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 research-portfolio"})

for q in ["recorded music", "music"]:
    try:
        r = S.get("https://fred.stlouisfed.org/search", params={"st": q}, timeout=45)
        ids = re.findall(r"/series/([A-Z0-9]{6,20})", r.text)
        seen, uniq = set(), []
        for i in ids:
            if i not in seen:
                seen.add(i); uniq.append(i)
        print(f"search '{q}': HTTP {r.status_code}, {len(uniq)} ids -> {uniq[:18]}")
    except Exception as e:
        print(f"search '{q}': FAIL {type(e).__name__} {e}")

print("\n=== series values ===")
for sid in ["CUSR0000SS62031", "CUSR0000SERA", "CPIAUCSL"]:
    r = S.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=45)
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", "v"]
    df["date"] = pd.to_datetime(df["date"])
    df["v"] = pd.to_numeric(df["v"], errors="coerce")
    df = df.dropna()
    def at(year):
        s = df[(df.date >= f"{year}-01-01") & (df.date < f"{year}-02-15")]
        return round(float(s.v.iloc[0]), 1) if len(s) else None
    print(f"{sid}: start {df.date.min().date()}  "
          f"2000={at(2000)} 2010={at(2010)} 2019={at(2019)} 2026={round(float(df.v.iloc[-1]),1)}")
