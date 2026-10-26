import json
import math

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LAT_TO_M = 111040.0
LON_TO_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))

def to_xy(lat, lon):
    x = (lon - ORIGIN_LON) * LON_TO_M
    y = (lat - ORIGIN_LAT) * LAT_TO_M
    return x, y

def test_roads():
    with open(r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin\purdue_roads.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in data["elements"] if e["type"] == "node"}
    ways = [e for e in data["elements"] if e["type"] == "way"]
    
    bike_ways = []
    arterial_ways = []
    campus_ways = []
    residential_ways = []
    
    for w in ways:
        tags = w.get("tags", {})
        hw = tags.get("highway", "")
        if not hw:
            continue
        w_nodes = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
        if len(w_nodes) < 2:
            continue
        name = tags.get("name", "")
        has_bike = any(k in tags for k in ['cycleway', 'cycleway:left', 'cycleway:right', 'cycleway:both', 'bicycle'])
        
        if has_bike:
            bike_ways.append((name, hw, len(w_nodes)))
        elif hw in ['primary', 'secondary']:
            arterial_ways.append((name, hw, len(w_nodes)))
        elif hw in ['tertiary', 'service'] and ('purdue' in name.lower() or 'mall' in name.lower() or 'street' in name.lower() or 'drive' in name.lower()):
            campus_ways.append((name, hw, len(w_nodes)))
        else:
            residential_ways.append((name, hw, len(w_nodes)))
            
    print(f"Roads categorized:")
    print(f"  Explicit Bike Infrastructure: {len(bike_ways)}")
    print(f"  Major Multi-Modal Arterials: {len(arterial_ways)}")
    print(f"  Campus Collector Streets: {len(campus_ways)}")
    print(f"  Residential / Other Roads: {len(residential_ways)}")

if __name__ == "__main__":
    test_roads()
