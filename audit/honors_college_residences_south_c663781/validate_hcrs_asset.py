"""Fresh-open validation for the standalone HCRS South library."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_honors_college_and_residences_south_c663781"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS = ROOT / "audit" / "honors_college_residences_south_c663781" / "sources" / "purdue_gis_fid905.json"
OUT = ROOT / "audit" / "honors_college_residences_south_c663781" / "validation.json"

def xy(x, y):
    r = 6378137.0
    lon = math.degrees(x/r)
    lat = math.degrees(2*math.atan(math.exp(y/r))-math.pi/2)
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040.0)

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
expected = "Asset_" + ASSET_ID
collection = bpy.data.collections.get(expected)
assert collection is not None, f"Missing export collection {expected}"
assert bpy.context.scene.name == "Building_" + ASSET_ID
shell = bpy.data.objects.get("HCRS | Purdue GIS footprint, six-story shell")
assert shell is not None
feature = json.loads(GIS.read_text(encoding="utf-8"))["feature"]
ring = feature["geometry"]["rings"][0][:-1]
source_points = [xy(x,y) for x,y in ring]
source_bbox = [[min(p[0] for p in source_points),max(p[0] for p in source_points)],
               [min(p[1] for p in source_points),max(p[1] for p in source_points)]]
shell_points = [(v.co.x,v.co.y) for v in shell.data.vertices[:len(source_points)]]
shell_bbox = [[min(p[0] for p in shell_points),max(p[0] for p in shell_points)],
              [min(p[1] for p in shell_points),max(p[1] for p in shell_points)]]
max_vertex_error = max(math.dist(a,b) for a,b in zip(source_points,shell_points))
materials = {m.name for o in collection.objects if o.type == "MESH" for m in o.data.materials if m}
image_nodes = []
for mat in bpy.data.materials:
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image:
                image_nodes.append({"material":mat.name,"filepath":node.image.filepath})
schematic = [o.name for o in collection.objects if o.name.startswith("SCHEMATIC INTERIOR")]
result = {
    "status": "fresh_open_validated",
    "blender_version": bpy.app.version_string,
    "asset_path": str(ASSET.relative_to(ROOT)).replace("\\","/"),
    "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "scene": bpy.context.scene.name,
    "collection": collection.name,
    "collection_object_count": len(collection.objects),
    "gis_feature_id": feature["attributes"]["FID"],
    "source_ring_vertices": len(source_points),
    "source_footprint_bounds_m": source_bbox,
    "shell_footprint_bounds_m": shell_bbox,
    "max_shell_vertex_difference_m": max_vertex_error,
    "material_names": sorted(materials),
    "image_texture_nodes": image_nodes,
    "schematic_interior_object_count": len(schematic),
    "schematic_interior_objects": schematic,
    "checks": {
        "expected_scene_and_export_collection": True,
        "GIS_shell_vertices_match_transformed_source_ring_within_0.001m": max_vertex_error < 0.001,
        "geometry_is_in_campus_xy_frame": shell_bbox[0][0] < 0 and shell_bbox[1][0] < 0,
        "procedural_materials_no_external_image_dependencies": len(image_nodes) == 0,
        "schematic_interior_labels_present": bool(schematic)
    },
    "uncertainty": "Height is estimated; published South elevations are unavailable. GIS level count conflicts with official Purdue story description. Interior is schematic."
}
assert all(v for k,v in result["checks"].items()), result["checks"]
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("HCRS_VALIDATION="+json.dumps(result,sort_keys=True))
