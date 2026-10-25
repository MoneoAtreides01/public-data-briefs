import io
import pandas as pd
import requests

S = requests.Session()
S.headers.update({"User-Agent": "research-portfolio/1.0"})

print("=== BLS QCEW: Sound Recording Industries (NAICS 5122) ===")
for url in [
    "https://data.bls.gov/cew/data/api/2024/a/industry/5122.csv",
    "https://data.bls.gov/cew/data/api/2023/a/industry/5122.csv",
]:
    try:
        r = S.get(url, timeout=60)
        print(f"{url.split('/')[-3]}/{url.split('/')[-2]}: HTTP {r.status_code}, {len(r.content)} bytes")
        if r.status_code == 200:
            df = pd.read_csv(io.StringIO(r.text))
            print("  cols:", list(df.columns)[:14])
            print("  rows:", len(df))
            st = df[df["agglvl_code"] == 51] if "agglvl_code" in df else df.head(0)
            if len(st):
                cols = [c for c in ["area_fips", "annual_avg_estabs", "annual_avg_emplvl",
                                    "total_annual_wages", "avg_annual_pay"] if c in df.columns]
                print(st.sort_values("annual_avg_emplvl", ascending=False)[cols].head(8).to_string(index=False))
    except Exception as e:
        print("  FAIL", type(e).__name__, e)

print("\n=== FRED: admissions / entertainment CPI candidates ===")
for sid in ["CUSR0000SS62031", "CUUR0000SS62031", "CUSR0000SERA", "CUSR0000SEEB"]:
    try:
        r = S.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=45)
        head = r.text.strip().split("\n")[0]
        print(f"  {sid}: HTTP {r.status_code}  {head}  last={r.text.strip().splitlines()[-1]}")
    except Exception as e:
        print(f"  {sid}: FAIL {type(e).__name__}")

print("\n=== MusicBrainz: release counts by year (test) ===")
try:
    r = S.get("https://musicbrainz.org/ws/2/release",
              params={"query": "date:2020", "fmt": "json", "limit": 1}, timeout=45)
    print("  HTTP", r.status_code, "count:", r.json().get("count") if r.status_code == 200 else r.text[:120])
except Exception as e:
    print("  FAIL", type(e).__name__, e)
