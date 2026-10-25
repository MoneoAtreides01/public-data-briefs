import time
import requests

S = requests.Session()
S.headers.update({"User-Agent": "research-portfolio/1.0 (contact: portfolio)"})

def count(query):
    r = S.get("https://musicbrainz.org/ws/2/release",
              params={"query": query, "fmt": "json", "limit": 1}, timeout=60)
    if r.status_code != 200:
        return f"HTTP {r.status_code}"
    return r.json().get("count")

for q in [
    'date:2015 AND format:CD',
    'date:2015 AND format:Vinyl',
    'date:2015 AND format:"Digital Media"',
    'date:2015 AND format:Cassette',
    'date:2005 AND format:Vinyl',
    'date:2023 AND format:Vinyl',
    'date:2023 AND format:CD',
]:
    print(f"{q:42s} -> {count(q)}")
    time.sleep(1.2)
