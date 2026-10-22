import urllib.request
import urllib.parse
import json
import time

def fetch_overpass(query, retries=3):
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({'data': query}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'User-Agent': 'PurdueDigitalTwinBot/1.0 (Academic/Blender Twin)'}
    )
    for attempt in range(retries):
        try:
            print(f"Querying Overpass API (attempt {attempt+1})...")
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None

if __name__ == "__main__":
    # Test query for Wabash River
    q_water = """[out:json][timeout:30];
(
  way["waterway"="river"](40.40,-86.92,40.46,-86.88);
  relation["waterway"="river"](40.40,-86.92,40.46,-86.88);
  way["natural"="water"](40.40,-86.92,40.46,-86.88);
);
out body;
>;
out skel qt;
"""
    res = fetch_overpass(q_water)
    if res:
        print("Success! Elements count:", len(res.get("elements", [])))
        with open("wabash_river.json", "w") as f:
            json.dump(res, f)
