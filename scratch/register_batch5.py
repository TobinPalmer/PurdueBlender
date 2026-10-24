"""Register the five audited batch-5 libraries in the modular master manifest."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "modular" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

records = [
    ("american_railway_building", "American Railway Building", "RAIL", [107, 110], [83.03792572, 60.04324341]),
    ("brown_laboratory_of_chemistry", "Brown Laboratory of Chemistry", "BRWN", [247], [145.5986824, -90.6512413]),
    ("peirce_hall", "Peirce Hall", "PRCE", [216], [-115.170644, -85.321301]),
    ("psychological_sciences", "Psychological Sciences Building", "PSYC", [239], [-106.6966, -48.2750]),
    ("wetherill_laboratory_of_chemistry", "R. B. Wetherill Laboratory of Chemistry", "WTHR", [257], [51.0402793884, -103.1483306885]),
]

new_records = []
for asset_id, display_name, code, feature_ids, origin in records:
    manifest["assets"] = [a for a in manifest["assets"] if a.get("id") != asset_id]
    new_records.append({
        "id": asset_id,
        "kind": "detailed",
        "display_name": display_name,
        "file": f"buildings/{asset_id}.blend",
        "collection": f"Asset_{asset_id}",
        "scene": f"Building_{asset_id}",
        "objects": [],
        "object_count": 0,
        "official_feature_ids": feature_ids,
        "official_code": code,
        "accuracy_status": "Detailed illustrative asset; GIS footprint and placement origin recorded, while elevations and interior details retain the specific uncertainties documented in its audit report.",
        "placement_transform": "master collection-instance marker translates local geometry to placement_origin_xy_m",
        "placement_origin_xy_m": origin,
        "local_coordinates": True,
    })

# Insert only the new records before the first site/massing record, preserving every
# pre-existing record's order and content.
insert_at = next((i for i, a in enumerate(manifest["assets"]) if a.get("kind") != "detailed"), len(manifest["assets"]))
manifest["assets"][insert_at:insert_at] = new_records
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

rebuild_path = ROOT / "modular" / "rebuild_linked_master.py"
source = rebuild_path.read_text(encoding="utf-8")
needle = '    "massing_knoy_hall_knoy_f598616": "knoy_hall",\n'
addition = (
    '    "massing_american_railway_building_rail_fc0f9a2": "american_railway_building",\n'
    '    "massing_brown_laboratory_of_chemistry_brwn_aed3885": "brown_laboratory_of_chemistry",\n'
    '    "massing_pierce_hall_prce_e5f59eb": "peirce_hall",\n'
    '    "massing_psychological_sciences_building_psyc_34efd04": "psychological_sciences",\n'
    '    "massing_r_b_wetherill_laboratory_of_chemistry_wthr_1577024": "wetherill_laboratory_of_chemistry",\n'
)
if addition.splitlines()[0] not in source:
    if needle not in source:
        raise RuntimeError("Could not find superseded-map insertion point")
    source = source.replace(needle, needle + addition, 1)
    rebuild_path.write_text(source, encoding="utf-8")

print(json.dumps({"registered": [r[0] for r in records], "manifest_asset_count": len(manifest["assets"])}))
