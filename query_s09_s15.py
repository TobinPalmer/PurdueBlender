import json

with open("purdue_30_sector_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

for s in manifest["sectors"]:
    if s["sector_id"] in ["S_09", "S_15"]:
        print("="*60)
        print(f"Sector {s['sector_id']}: {s['name']}")
        print(f"Grid Col: {s['grid_col']}, Row: {s['grid_row']}")
        print(f"Bounds XY: {s['bounds_xy']}")
        print(f"Bounds LatLon: {s['bounds_latlon']}")
        print(f"Key Landmarks: {s['key_landmarks']}")

with open("sector_audit_report.json", "r", encoding="utf-8") as f:
    audit = json.load(f)

for s in audit["sectors"]:
    if s["sector_id"] in ["S_09", "S_15"]:
        print("="*60)
        print(f"Audit {s['sector_id']}: Object count = {s['object_count']}, Score = {s['fidelity_score']}, Status = {s['status']}")
        print("Sample objects:", s["sample_objects"])
