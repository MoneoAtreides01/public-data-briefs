import re
import requests

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 research-portfolio"})

for q in ["sound recording", "musical instrument", "audio equipment", "record store",
          "performing arts", "music publisher", "recording studio"]:
    try:
        r = S.get("https://fred.stlouisfed.org/search", params={"st": q}, timeout=45)
        # pair each series id with the title text near it
        blocks = re.findall(r"/series/([A-Z0-9]{8,24})[^>]*>(.{0,90}?)</a>", r.text, re.S)
        out = []
        seen = set()
        for sid, txt in blocks:
            if sid in seen:
                continue
            seen.add(sid)
            t = re.sub(r"<[^>]+>", "", txt)
            t = re.sub(r"\s+", " ", t).strip()
            if t:
                out.append(f"{sid}: {t[:72]}")
        print(f"\n### {q}  ({len(out)} hits)")
        for line in out[:6]:
            print("   ", line)
    except Exception as e:
        print(f"{q}: FAIL {type(e).__name__}")
