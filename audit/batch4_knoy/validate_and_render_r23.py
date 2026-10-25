import ast
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/knoy_hall.blend"
OUT = ROOT / "audit/batch4_knoy"
BUILDER = ROOT / "modular/buildings/build_knoy_hall.py"
GIS_SNAPSHOT = OUT / "purdue_campus_knoy_feature189_r23.json"

def mesh_world_hash():
    rows = {}
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        row = {"type": obj.type, "world": [[round(float(v), 7) for v in line] for line in obj.matrix_world]}
        if obj.type == "MESH":
            row["verts"] = [[round(float(c), 7) for c in vertex.co] for vertex in obj.data.vertices]
            row["faces"] = [list(poly.vertices) for poly in obj.data.polygons]
        rows[obj.name] = row
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def bounds_world(obj):
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[round(min(point[axis] for point in coords), 4), round(max(point[axis] for point in coords), 4)] for axis in range(3)]

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
root = bpy.data.objects.get("AssetRoot_knoy_hall")
shell = bpy.data.objects.get("KNOY_Exterior_Masonry_Walls")
l5 = bpy.data.objects.get("KNOY_FloorSlab_L5")
assert root and shell and l5
before_hash = mesh_world_hash()

scene["source_supported_numbered_levels"] = 4
scene["purdue_campus_gis_objectid"] = 189
scene["purdue_campus_buildingidlong"] = 75
scene["gis_id_reconciliation"] = "Knoy cache row FID 243 in target_buildings_gis.json; Purdue campus MapServer layer 0 record OBJECTID 189 / buildingidlong 75."
scene["level_count_status"] = (
    "Purdue's 2018 Gateway Formation Study labels existing Levels 1-4 at 14 ft 8 in floor-to-floor. "
    "The separate cached project record FID 243 reports five levels; this does not resolve whether the modeled L5 slab is an occupied story or roof slab."
)
l5["geometry_status"] = "UNVERIFIED / SOURCE CONFLICT: 2018 Purdue planning elevations label only Levels 1-4; separate project-cache FID 243 reports five levels but does not resolve occupied L5 versus roof slab."
notes = bpy.data.texts.get("EVIDENCE_AND_INTERIOR_NOTES.txt")
if notes is None:
    notes = bpy.data.texts.new("EVIDENCE_AND_INTERIOR_NOTES.txt")
existing = notes.as_string()
addition = (
    "\n\nROUND 23 — GIS ID AND LEVEL METADATA CLARIFICATION\n"
    "------------------------------------------------------------\n"
    "Purdue's live campus GIS MapServer layer 0 identifies Knoy as OBJECTID 189 / buildingidlong 75; its raw EPSG:4326 response was retrieved 2026-10-25 and is saved at audit/batch4_knoy/purdue_campus_knoy_feature189_r23.json. The separate project cache target_buildings_gis.json identifies the same Knoy row as FID 243 and reports five levels plus a 48 ft extrusion. These identifier schemes are distinct, and the live campus service response has no levels or extrusion fields. The saved footprint wire matches the cached project polygon within 0.000012 m after local translation; two adjacent points in the live service polygon differ by up to 0.177865 m while the remaining points match within 0.001 m. This source mismatch may be due to edits or separate digitization and is not a basis for an unverified shape correction. The 2018 Purdue Gateway Formation Study explicitly labels existing Levels 1-4 at 14 ft 8 in floor-to-floor. The asset retains its inherited L5 slab and datum as UNVERIFIED / SOURCE CONFLICT because accessible evidence does not resolve an occupied fifth story versus a roof slab. No geometry, material, or transform changed.\n"
)
r23_start = existing.find("ROUND 23 —")
if r23_start >= 0:
    existing = existing[:r23_start].rstrip()
notes.clear()
notes.write(existing + addition)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

# Reopen the saved file so validation describes disk state, not the in-memory edit.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
root = bpy.data.objects["AssetRoot_knoy_hall"]
shell = bpy.data.objects["KNOY_Exterior_Masonry_Walls"]
l5 = bpy.data.objects["KNOY_FloorSlab_L5"]
wire = bpy.data.objects["KNOY_Footprint_Reference_Wire"]
after_hash = mesh_world_hash()
assert before_hash == after_hash, (before_hash, after_hash)
root_identity = all(abs(root.matrix_world[i][j] - (1.0 if i == j else 0.0)) < 1e-6 for i in range(4) for j in range(4))
assert root_identity
assert scene.get("source_supported_numbered_levels") == 4
assert "UNVERIFIED / SOURCE CONFLICT" in l5.get("geometry_status", "")
unpacked = [image.filepath for image in bpy.data.images if image.source == "FILE" and image.filepath and not image.packed_file]

tree = ast.parse(BUILDER.read_text(encoding="utf-8"))
gis_literal = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "GIS_POLYGON" for target in node.targets))
gis_xy = gis_literal[:-1]
area = abs(sum(gis_xy[i][0] * gis_xy[(i + 1) % len(gis_xy)][1] - gis_xy[(i + 1) % len(gis_xy)][0] * gis_xy[i][1] for i in range(len(gis_xy))) / 2)
gis_origin_xy = [(min(p[0] for p in gis_xy) + max(p[0] for p in gis_xy)) / 2, (min(p[1] for p in gis_xy) + max(p[1] for p in gis_xy)) / 2]
gis_local = [[p[0] - gis_origin_xy[0], p[1] - gis_origin_xy[1]] for p in gis_xy]
wire_local = [[float((wire.matrix_world @ v.co).x), float((wire.matrix_world @ v.co).y)] for v in wire.data.vertices]
assert len(wire_local) == len(gis_literal), (len(wire_local), len(gis_literal))
vertex_errors = [math.dist(gis_local[i], wire_local[i]) for i in range(len(gis_local))]
max_registration_error = max(vertex_errors)
assert max_registration_error < 0.002, max_registration_error
gis_record = json.loads(GIS_SNAPSHOT.read_text(encoding="utf-8"))
feature = gis_record["features"][0]
attributes = feature["attributes"]
assert attributes["OBJECTID"] == 189 and attributes["buildingidlong"] == 75
assert "Knoy" in attributes["Name"]
live_ring = feature["geometry"]["rings"][0]
assert len(live_ring) == len(gis_literal)
live_local = [[(lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)) - gis_origin_xy[0], (lat - 40.4274) * 111040.0 - gis_origin_xy[1]] for lon, lat in live_ring[:-1]]
live_vertex_errors = [math.dist(live_local[i], wire_local[i]) for i in range(len(live_local))]
live_max_residual = max(live_vertex_errors)
live_worst_indices = [i for i, error in enumerate(live_vertex_errors) if abs(error - live_max_residual) < 1e-8]
assert live_max_residual < 0.20, live_max_residual
scene["purdue_campus_gis_max_vertex_residual_m"] = round(live_max_residual, 6)

camera = bpy.data.objects.get("KNOY_Audit_Exterior")
assert camera
camera.location = (115.0, -145.0, 98.0)
camera.rotation_euler = (Vector((0.0, 0.0, 10.0)) - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera
assert scene.camera
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.filepath = str(OUT / "knoy_exterior_r23.png")
bpy.ops.render.render(write_still=True)

report = {
    "revision": 23,
    "asset": str(ASSET),
    "reopened_saved_asset": True,
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "scene_object_count": len(bpy.data.objects),
    "mesh_object_count": sum(obj.type == "MESH" for obj in bpy.data.objects),
    "asset_root_identity": root_identity,
    "exterior_shell_bounds_world_m": bounds_world(shell),
    "footprint_wire_bounds_local_m": bounds_world(wire),
    "gis_source": {
        "provider": "Purdue University Libraries Campus GIS MapServer, layer PuGeoDB.DBO.CampusBuilding (0); project cache FID 243 is modular/buildings/target_buildings_gis.json.",
        "url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0/query?where=Name%20LIKE%20%27%25Knoy%25%27&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
        "retrieval_date": "2026-10-25",
        "feature_id": {"OBJECTID": attributes["OBJECTID"], "buildingidlong": attributes["buildingidlong"], "name": attributes["Name"]},
        "source_date": "Not stated for this service record; ChangeYear is retained in the raw snapshot.",
        "source_crs": "EPSG:4326, as requested in the ArcGIS query response.",
        "comparison_crs": "Project local tangent-plane approximation: X east, Y north, Z up; origin 40.4274, -86.9137; not surveyed.",
        "measurement_method": "Transform each live Purdue GIS WGS84 ring coordinate with the documented project approximation, subtract the asset-local XY origin, then compare corresponding vertices against the reopened saved footprint wire.",
        "unique_boundary_vertex_count": len(gis_xy),
        "closed_ring_coordinate_count": len(gis_literal),
        "area_m2": round(area, 3),
        "bounds_xy_m": [[round(min(p[0] for p in gis_xy), 3), round(max(p[0] for p in gis_xy), 3)], [round(min(p[1] for p in gis_xy), 3), round(max(p[1] for p in gis_xy), 3)]],
        "campus_to_asset_local_origin_xy_m": [round(gis_origin_xy[0], 4), round(gis_origin_xy[1], 4)],
        "matched_asset_closed_ring_coordinate_count": len(wire_local),
        "project_cache_max_corresponding_vertex_residual_m": round(max_registration_error, 6),
        "live_service_max_vertex_residual_m": round(live_max_residual, 6),
        "live_service_worst_vertex_indices_zero_based": live_worst_indices,
        "live_service_vertex_residuals_m": [round(live_vertex_errors[i], 6) for i in range(len(live_vertex_errors))],
        "raw_source_snapshot": str(GIS_SNAPSHOT),
        "raw_source_snapshot_sha256": hashlib.sha256(GIS_SNAPSHOT.read_bytes()).hexdigest(),
        "uncertainty": "The project-local coordinates use an approximate geographic conversion, not survey control. The saved boundary matches the cached project polygon within rounding; two vertices in the live Purdue service differ by up to 0.178 m. This could reflect source edits or separate digitization and is not enough to infer a structural-wall offset.",
    },
    "level_evidence": {
        "cached_project_record_fid_243_reported_levels": scene.get("levels"),
        "purdue_campus_service_objectid": scene.get("purdue_campus_gis_objectid"),
        "purdue_campus_buildingidlong": scene.get("purdue_campus_buildingidlong"),
        "identifier_reconciliation": scene.get("gis_id_reconciliation"),
        "live_purdue_footprint_max_vertex_residual_m": scene.get("purdue_campus_gis_max_vertex_residual_m"),
        "source_supported_numbered_levels": scene.get("source_supported_numbered_levels"),
        "l5_status": l5.get("geometry_status"),
        "uncertainty": "L5 occupied-floor versus roof-slab interpretation remains unresolved.",
    },
    "mesh_and_world_matrix_sha256_before_metadata_edit": before_hash,
    "mesh_and_world_matrix_sha256_after_save_reopen": after_hash,
    "saved_blend_file_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "geometry_and_world_matrices_unchanged": before_hash == after_hash,
    "unpacked_external_images": unpacked,
    "render": str(OUT / "knoy_exterior_r23.png"),
    "scope": "Metadata clarification and read-only source-footprint comparison; no mesh geometry, material, object transform, master, placement marker, or shared index changed.",
}
(OUT / "validation_r23.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
