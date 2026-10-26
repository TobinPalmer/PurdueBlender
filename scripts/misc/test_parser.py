import json

def test_parse():
    with open(r"C:\Users\Tobin\.gemini\antigravity\scratch\purdue_digital_twin\purdue_campus_buildings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = {elem["id"]: (elem["lat"], elem["lon"]) for elem in data["elements"] if elem["type"] == "node"}
    ways = [elem for elem in data["elements"] if elem["type"] == "way"]
    
    print(f"Total nodes: {len(nodes)}, Total ways: {len(ways)}")
    valid_buildings = 0
    campus_buildings = []
    houses = []
    
    for w in ways:
        tags = w.get("tags", {})
        if "building" not in tags:
            continue
        w_nodes = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
        if len(w_nodes) < 3:
            continue
        valid_buildings += 1
        name = tags.get("name", "")
        b_type = tags.get("building", "")
        if name or b_type in ["university", "dormitory", "civic", "school"]:
            campus_buildings.append((name, len(w_nodes)))
        else:
            houses.append((b_type, len(w_nodes)))
            
    print(f"Valid building polygons: {valid_buildings}")
    print(f"Identified campus/named buildings: {len(campus_buildings)}")
    print(f"Identified residential/surrounding houses: {len(houses)}")

if __name__ == "__main__":
    test_parse()
