import urllib.request
import urllib.parse
import json
import time

def fetch_overpass(query, filename):
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({'data': query}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'User-Agent': 'PurdueDigitalTwinBot/1.0 (Academic/Blender Twin)'}
    )
    print(f"Fetching {filename} from Overpass API...", flush=True)
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        elements = res.get("elements", [])
        print(f"Successfully fetched {filename}: {len(elements)} elements", flush=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(res, f)
        return len(elements)

if __name__ == "__main__":
    # Purdue Main Campus BBox: Lat 40.418 to 40.440, Lon -86.932 to -86.908
    q_buildings = """[out:json][timeout:50];
(
  way["building"](40.418,-86.932,40.442,-86.908);
  relation["building"](40.418,-86.932,40.442,-86.908);
);
out body;
>;
out skel qt;
"""
    fetch_overpass(q_buildings, "purdue_campus_buildings.json")
