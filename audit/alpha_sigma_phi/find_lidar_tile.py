"""Find Indiana's 2018 SPW lidar tile intersecting Alpha Sigma Phi."""
import concurrent.futures
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import time

BASE = "https://giselevationingov.s3.us-east-2.amazonaws.com/"
PREFIX = "las/statewide/2016/SPW/ql2/15"
TARGET = (-86.9257435, 40.4350934)
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
query = urllib.parse.urlencode({"list-type": "2", "prefix": PREFIX, "max-keys": "1000"})
root = ET.fromstring(urllib.request.urlopen(BASE + "?" + query).read())
keys = [el.text for el in root.findall("s3:Contents/s3:Key", NS) if el.text.endswith("_footprint.geojson")]

def read_key(key):
    url = BASE + urllib.parse.quote(key, safe="/")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=25) as response:
                return key, json.loads(response.read())
        except Exception:
            if attempt == 4:
                raise
            time.sleep(0.3 * (attempt + 1))

matches = []
near = []
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for key, doc in pool.map(read_key, keys):
        ring = doc["features"][0]["geometry"]["coordinates"][0]
        xs, ys = [pt[0] for pt in ring], [pt[1] for pt in ring]
        if min(xs) <= TARGET[0] <= max(xs) and min(ys) <= TARGET[1] <= max(ys):
            matches.append({"key": key.replace("_footprint.geojson", ".las"), "footprint": doc})
        gapx=max(min(xs)-TARGET[0],0,TARGET[0]-max(xs))
        gapy=max(min(ys)-TARGET[1],0,TARGET[1]-max(ys))
        near.append((gapx*gapx+gapy*gapy,key,min(xs),max(xs),min(ys),max(ys)))
near.sort()
print(json.dumps({"tile_count_checked": len(keys), "matches": matches, "closest": near[:4]}, indent=2))
