import urllib.request
import ssl
import json
import html

ctx = ssl._create_unverified_context()

for i in range(1, 250):
    url = f'https://collections.lib.purdue.edu/campus/buildings/{i}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=2) as r:
            text = r.read().decode('utf-8', errors='ignore')
            idx = text.find('<building-detail-page :building="')
            if idx != -1:
                end_idx = text.find('">', idx)
                raw_json = text[idx + len('<building-detail-page :building="'):end_idx]
                unescaped = html.unescape(raw_json)
                b_info = json.loads(unescaped)
                name = b_info.get('name', '')
                abbr = b_info.get('abbreviation', '')
                if 'harrison' in name.lower() or abbr == 'HARR':
                    print(f"FOUND ID {i}: {name} ({abbr})")
                    print(json.dumps(b_info, indent=2))
                    break
    except Exception as e:
        pass
