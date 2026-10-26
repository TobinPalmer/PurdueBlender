"""Independent Blender reopen, footprint, placement, and export probe for Bindley."""
from pathlib import Path
import json
import math
import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET = ROOT / "modular" / "buildings" / "bindley_bioscience_center.blend"
MANIFEST = ROOT / "modular" / "manifest.json"
GIS = ROOT / "audit" / "bindley_bioscience_center" / "sources" / "gis_feature_605.json"
EVIDENCE = ROOT / "audit" / "bindley_bioscience_center" / "evidence.json"
EXPORT = HERE / "collection_export_probe.blend"
COLLECTION_NAME = "Asset_bindley_bioscience_center"
SHELL_NAME = "BIND_GIS_primary_shell"


def centroid(points):
    twice = sum(points[i][0] * points[(i + 1) % len(points)][1]
                - points[(i + 1) % len(points)][0] * points[i][1]
                for i in range(len(points)))
    cx = sum((points[i][0] + points[(i + 1) % len(points)][0]) *
             (points[i][0] * points[(i + 1) % len(points)][1]
              - points[(i + 1) % len(points)][0] * points[i][1])
             for i in range(len(points))) / (3 * twice)
    cy = sum((points[i][1] + points[(i + 1) % len(points)][1]) *
             (points[i][0] * points[(i + 1) % len(points)][1]
              - points[(i + 1) % len(points)][0] * points[i][1])
             for i in range(len(points))) / (3 * twice)
    return [cx, cy]


def directed_hausdorff(a, b):
    return max(min(math.dist(p, q) for q in b) for p in a)


def xy_bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)]


bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
asset = bpy.data.collections.get(COLLECTION_NAME)
assert asset is not None, f"missing collection {COLLECTION_NAME}"
objects = sorted(asset.all_objects, key=lambda obj: obj.name)
object_names = [obj.name for obj in objects]
shell = bpy.data.objects.get(SHELL_NAME)
assert shell is not None and shell.type == "MESH"

depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = shell.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
evaluated.to_mesh_clear()
zmin = min(v.z for v in vertices)
base = sorted({(round(v.x, 7), round(v.y, 7)) for v in vertices if abs(v.z - zmin) < 1e-5})
shell_bounds = [[min(v[i] for v in vertices), max(v[i] for v in vertices)] for i in range(3)]

gis_doc = json.loads(GIS.read_text(encoding="utf-8"))
feature = gis_doc["feature"]
attrs = feature["attributes"]
ring = feature["geometry"]["rings"][0]
raw_ring = ring[:-1] if ring[0] == ring[-1] else ring
lat0, lon0 = 40.4274, -86.9137
lon_m = 111412.84 * math.cos(math.radians(lat0))
lat_m = 111040.0
projected = [[(p[0] - lon0) * lon_m, (p[1] - lat0) * lat_m] for p in raw_ring]
gis_centroid = centroid(projected)
expected_local = [[p[0] - gis_centroid[0], p[1] - gis_centroid[1]] for p in projected]
gis_local_bounds = xy_bounds(expected_local)
shell_local_bounds = xy_bounds(base)
footprint_hausdorff = max(directed_hausdorff(base, expected_local),
                          directed_hausdorff(expected_local, base))
placement = None
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entry = next(item for item in manifest["assets"] if item["id"] == "bindley_bioscience_center")
placement = entry["placement_origin_xy_m"]
evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

image_files = sorted({img.filepath for img in bpy.data.images
                      if img.source == "FILE" and img.filepath})
linked_libraries = sorted(lib.filepath for lib in bpy.data.libraries)
rig_objects_in_export = sorted(obj.name for obj in objects if obj.type in {"CAMERA", "LIGHT"})
names_match = set(object_names) == set(entry.get("objects", []))
counts_match = len(objects) == entry.get("object_count") == len(entry.get("objects", []))
wall = bpy.data.objects.get("BIND_entry_name_wall")
sign_text = bpy.data.objects.get("BIND_entry_sign_text")
roof_equipment = [obj for obj in objects
                  if obj.name.startswith(("BIND_roof_plant_screen_", "BIND_roof_vent_"))]
roof_tops = {obj.name: max((obj.matrix_world @ v.co).z for v in obj.data.vertices)
             for obj in roof_equipment if obj.type == "MESH"}
all_bounds = []
for obj in objects:
    if obj.type != "MESH":
        continue
    ev = obj.evaluated_get(depsgraph)
    me = ev.to_mesh()
    all_bounds.extend(ev.matrix_world @ v.co for v in me.vertices)
    ev.to_mesh_clear()
asset_bounds = [[min(v[i] for v in all_bounds), max(v[i] for v in all_bounds)]
                for i in range(3)]

probe = {
    "asset_file": ASSET.relative_to(ROOT).as_posix(),
    "scene": scene.name,
    "building_id": asset.get("building_id"),
    "source_feature_id": asset.get("source_feature_id"),
    "collection": COLLECTION_NAME,
    "collection_object_count": len(objects),
    "collection_object_names": object_names,
    "manifest_object_count": entry.get("object_count"),
    "manifest_name_count": len(entry.get("objects", [])),
    "manifest_names_match": names_match,
    "manifest_counts_match": counts_match,
    "shell_name": SHELL_NAME,
    "shell_vertex_count": len(vertices),
    "shell_base_xy_count": len(base),
    "shell_bounds_local_m": shell_bounds,
    "shell_base_xy_bounds_local_m": shell_local_bounds,
    "shell_base_centroid_local_m": centroid(base),
    "gis_feature_id": attrs.get("FID"),
    "gis_building_abbreviation": attrs.get("BLDG_ABBR"),
    "gis_building_name": attrs.get("BUILDING_N"),
    "gis_address": attrs.get("ADDRESS"),
    "gis_num_levels": attrs.get("NUM_LEVELS"),
    "gis_ring_vertex_count": len(raw_ring),
    "gis_centroid_project_xy_m": gis_centroid,
    "manifest_placement_origin_xy_m": placement,
    "placement_centroid_residual_m": math.dist(gis_centroid, placement),
    "gis_local_bounds_xy_m": gis_local_bounds,
    "max_footprint_hausdorff_m": footprint_hausdorff,
    "model_bounds_local_m": asset_bounds,
    "dark_name_wall_present": bool(wall and wall.type == "MESH"),
    "dark_name_wall_dimensions_m": list(wall.dimensions) if wall else None,
    "sign_text_present": bool(sign_text and sign_text.type == "FONT"),
    "roof_equipment_count": len(roof_equipment),
    "roof_equipment_tops_local_m": roof_tops,
    "max_roof_equipment_top_m": max(roof_tops.values()) if roof_tops else None,
    "external_image_files": image_files,
    "linked_libraries": linked_libraries,
    "camera_or_light_objects_in_export_collection": rig_objects_in_export,
    "evidence_record_validation_object_count": evidence.get("validation", {}).get("collection_object_count"),
}
HERE.joinpath("blender_probe.json").write_text(json.dumps(probe, indent=2) + "\n", encoding="utf-8")

# Verify the named handoff collection itself can be written and reopened.
bpy.data.libraries.write(str(EXPORT), {asset}, path_remap="RELATIVE_ALL", fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(EXPORT))
exported = bpy.data.collections.get(COLLECTION_NAME)
assert exported is not None
export_objects = sorted(exported.all_objects, key=lambda obj: obj.name)
export_result = {
    "reopened_export": EXPORT.name,
    "collection": exported.name,
    "object_count": len(export_objects),
    "object_names": [obj.name for obj in export_objects],
    "camera_light_objects": [obj.name for obj in export_objects if obj.type in {"CAMERA", "LIGHT"}],
    "external_image_files": sorted({img.filepath for img in bpy.data.images
                                     if img.source == "FILE" and img.filepath}),
    "linked_libraries": sorted(lib.filepath for lib in bpy.data.libraries),
}
HERE.joinpath("export_probe.json").write_text(json.dumps(export_result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"asset_probe": probe, "export_probe": export_result}, indent=2))
