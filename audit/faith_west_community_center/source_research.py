import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).parent
USER_AGENT = "PurdueCampusMap building research"

def get_json(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read())

# Geocode the postal address to establish the correct site near Northwestern Ave.
params = {"SingleLine": "1920 Northwestern Avenue, West Lafayette, Indiana", "f": "json", "outFields": "*"}
geocode_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?" + urllib.parse.urlencode(params)
geocode = get_json(geocode_url)
(OUT / "geocode_1920_northwestern.json").write_text(json.dumps(geocode, indent=2), encoding="utf-8")
candidate = geocode["candidates"][0]
lon, lat = candidate["location"]["x"], candidate["location"]["y"]

# Collect OSM building outlines near the geocoded Faith West property for comparison.
south, west, north, east = lat - 0.00065, lon - 0.00075, lat + 0.00065, lon + 0.00075
overpass = f'[out:json];(way["building"]({south},{west},{north},{east});relation["building"]({south},{west},{north},{east}););out geom;'
req_data = urllib.parse.urlencode({"data": overpass}).encode()
osm = get_json("https://overpass-api.de/api/interpreter", req_data)
(OUT / "osm_buildings_near_faith_west.json").write_text(json.dumps(osm, indent=2), encoding="utf-8")

summary = {
    "geocode_url": geocode_url,
    "geocode_address": candidate.get("address"),
    "geocode_location_lon_lat": [lon, lat],
    "geocode_score": candidate.get("score"),
    "overpass_url": "https://overpass-api.de/api/interpreter",
    "overpass_query_bbox_s_w_n_e": [south, west, north, east],
    "osm_element_count": len(osm.get("elements", [])),
    "osm_elements": [{"type": x.get("type"), "id": x.get("id"), "tags": x.get("tags", {}), "node_count": len(x.get("geometry", []))} for x in osm.get("elements", [])],
}
(OUT / "source_research_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
