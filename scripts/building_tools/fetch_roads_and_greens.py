import urllib.request
import urllib.parse
import json

def fetch_overpass(query, filepath):
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({'data': query}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'User-Agent': 'PurdueDigitalTwinBot/1.0 (Academic/Blender Twin)'}
    )
    print(f"Fetching to {filepath}...", flush=True)
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print(f"Elements: {len(res.get('elements', []))}", flush=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(res, f)

if __name__ == "__main__":
    # Query major roads and pedestrian ways
    q_roads = """[out:json][timeout:50];
(
  way["highway"~"primary|secondary|tertiary|residential|service|footway|path"](40.418,-86.932,40.442,-86.908);
);
out body;
>;
out skel qt;
"""
    fetch_overpass(q_roads, r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin\purdue_roads.json")
