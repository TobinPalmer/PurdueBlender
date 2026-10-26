"""Export saved Stanley foundation vertices plus official FID 56 source geometry."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/stanley_coulter_hall.blend"
AUDIT = ROOT / "audit/batch3_stanley"
MANIFEST = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
OFFICIAL = json.loads((ROOT / "audit/official_building_references.json").read_text(encoding="utf-8"))
record = next(a for a in MANIFEST["assets"] if a["id"] == "stanley_coulter_hall")
feature = next(a for a in OFFICIAL["buildings"] if a["fid"] == 56)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
foundation = bpy.data.objects["SC_Foundation_Limestone_Plinth"]
origin = record["placement_origin_xy_m"]
vertices = []
for v in foundation.data.vertices:
    p = foundation.matrix_world @ v.co
    vertices.append({"local_xyz_m": [float(p.x), float(p.y), float(p.z)],
                     "campus_xy_m": [float(p.x) + float(origin[0]), float(p.y) + float(origin[1])]})
asset = {"asset": str(ASSET), "collection": record["collection"], "object": foundation.name,
         "root_transform": {"location": list(bpy.data.objects['AssetRoot_stanley_coulter_hall'].location),
                            "rotation": list(bpy.data.objects['AssetRoot_stanley_coulter_hall'].rotation_euler),
                            "scale": list(bpy.data.objects['AssetRoot_stanley_coulter_hall'].scale)},
         "placement_origin_xy_m": origin, "coordinate_relation": "campus_xy_m = local_xy_m + manifest placement_origin_xy_m",
         "vertices": vertices}
(AUDIT / "asset_foundation_vertices_r3.json").write_text(json.dumps(asset, indent=2), encoding="utf-8")
snapshot = {"source": OFFICIAL["source"], "provenance": OFFICIAL["provenance"],
            "snapshot_date": OFFICIAL["snapshot_date"], "coordinate_method": OFFICIAL["coordinates"],
            "feature": feature, "retrieved_for_r3": "2026-10-25", "crs_note": "The official campus reference snapshot is stored in the project local approximate meter frame; see source metadata and modular/AGENTS.md for its local tangent-plane convention."}
(AUDIT / "source_gis_fid56_r3.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
print("saved", len(vertices), "foundation vertices and official FID", feature["fid"])
