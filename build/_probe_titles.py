import re
import requests

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 research-portfolio"})

CANDIDATES = [
    "CUSR0000SS62031", "CUSR0000SERA", "CUSR0000SEEB", "CUSR0000SEEE",
    "CUSR0000SEEF", "CUSR0000SERF", "CUSR0000SERA01", "CUSR0000SERA02",
    "CUUR0000SEEB", "CUSR0000SS61011", "CUSR0000SEEB01", "CUSR0000SS62021",
]

for sid in CANDIDATES:
    try:
        r = S.get(f"https://fred.stlouisfed.org/series/{sid}", timeout=45)
        if r.status_code != 200:
            print(f"{sid:20s} HTTP {r.status_code}")
            continue
        m = re.search(r"<title>(.*?)</title>", r.text, re.S)
        title = re.sub(r"\s+", " ", m.group(1)).strip() if m else "?"
        # units block
        u = re.search(r'id="units".*?</div>', r.text, re.S)
        print(f"{sid:20s} {title[:110]}")
    except Exception as e:
        print(f"{sid:20s} FAIL {type(e).__name__}")
