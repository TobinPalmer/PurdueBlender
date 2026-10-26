"""Read-only independent reopen probe for Class of 1950 and its master placement."""
from pathlib import Path
import hashlib
import json
import math
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET = ROOT / "modular/buildings/class_of_1950.blend"
MASTER = ROOT / "purdue_campus_master.blend"
MANIFEST = ROOT / "modular/manifest.json"
GIS = ROOT / "audit/class_of_1950_evidence/arcgis_feature_230.json"
EXPECTED_SCENE = "Building_class_of_1950"
EXPECTED_COLLECTION = "Asset_class_of_1950"


def geom_bounds(collection):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in collection.all_objects:
        if obj.type not in {"MESH", "CURVE", "SURFACE", "FONT", "META"}:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        points.extend(evaluated.matrix_world @ Vector(p) for p in evaluated.bound_box)
    if not points:
        raise RuntimeError(f"No geometry in {collection.name}")
    return [[float(min(p[i] for p in points)), float(max(p[i] for p in points))] for i in range(3)]


def nearest(point, candidates):
    return min(math.hypot(point[0] - q[0], point[1] - q[1]) for q in candidates)


manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
record = next(a for a in manifest["assets"] if a.get("id") == "class_of_1950")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes.get(EXPECTED_SCENE)
collection = bpy.data.collections.get(EXPECTED_COLLECTION)
assert scene and collection
objects = sorted(collection.all_objects, key=lambda obj: obj.name)
object_names = [obj.name for obj in objects]
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
type_counts = {}
for obj in objects:
    type_counts[obj.type] = type_counts.get(obj.type, 0) + 1
bounds = geom_bounds(collection)
root = bpy.data.objects.get("AssetRoot_class_of_1950")
required_geometry = ["CL50_Corrected_GIS_Wall_Envelope", "CL50_Corrected_GIS_Roof_Slab", "CL50_Penthouse"]
missing_geometry = [name for name in required_geometry if bpy.data.objects.get(name) not in objects]
shell = bpy.data.objects["CL50_Corrected_GIS_Wall_Envelope"]
base_xy = sorted({(round(float((shell.matrix_world @ v.co).x), 3),
                   round(float((shell.matrix_world @ v.co).y), 3))
                  for v in shell.data.vertices
                  if abs(float((shell.matrix_world @ v.co).z)) < 1e-5})
gis_doc = json.loads(GIS.read_text(encoding="utf-8-sig"))
feature = gis_doc["feature"]
attributes = feature["attributes"]
ring = feature["geometry"]["rings"][0]
radius = 6378137.0
origin_x, origin_y = record["placement_origin_xy_m"]
gis_local = []
for merc_x, merc_y in ring:
    longitude = merc_x / radius * 180.0 / math.pi
    latitude = (2.0 * math.atan(math.exp(merc_y / radius)) - math.pi / 2.0) * 180.0 / math.pi
    campus_x = (longitude + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    campus_y = (latitude - 40.4274) * 111040.0
    gis_local.append((campus_x - origin_x, campus_y - origin_y))
gis_to_model = [nearest(p, base_xy) for p in gis_local]
model_to_gis = [nearest(p, gis_local) for p in base_xy]
unmaterialed = [obj.name for obj in mesh_objects
                if not obj.data.materials or all(mat is None for mat in obj.data.materials)]
external_libraries = [lib.filepath for lib in bpy.data.libraries]
images = [{"name": img.name, "filepath": img.filepath, "packed": bool(img.packed_file)}
          for img in bpy.data.images if img.source == "FILE" and not img.packed_file]
all_modifiers = sum(len(obj.modifiers) for obj in objects)
manifest_names_match = set(object_names) == set(record.get("objects", []))
manifest_count_match = len(objects) == record.get("object_count") == len(record.get("objects", []))

asset_probe = {
    "asset_file": ASSET.relative_to(ROOT).as_posix(),
    "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "asset_bytes": ASSET.stat().st_size,
    "scene_name": scene.name,
    "scene_render_engine": scene.render.engine,
    "collection_name": collection.name,
    "collection_object_count": len(objects),
    "collection_type_counts": type_counts,
    "collection_object_names": object_names,
    "manifest_object_count": record.get("object_count"),
    "manifest_names_match": manifest_names_match,
    "manifest_count_match": manifest_count_match,
    "collection_local_bounds_m": bounds,
    "manifest_local_bounds_m": record.get("local_bounds_m"),
    "manifest_placement_origin_xy_m": record.get("placement_origin_xy_m"),
    "root_empty_present": bool(root and all(abs(float(v)) < 1e-6 for v in root.location)),
    "required_geometry": required_geometry,
    "missing_geometry": missing_geometry,
    "unmaterialed_mesh_count": len(unmaterialed),
    "unmaterialed_meshes": unmaterialed,
    "external_libraries": external_libraries,
    "unpacked_file_images": images,
    "modifier_count": all_modifiers,
    "source_feature_id": attributes.get("FID"),
    "source_abbreviation": attributes.get("BLDG_ABBR"),
    "source_name": attributes.get("BUILDING_N"),
    "source_crs": gis_doc.get("spatialReference", {}),
    "source_ring_vertex_count": len(ring),
    "num_levels": attributes.get("NUM_LEVELS"),
    "count_of_floors": attributes.get("CountOfFLO"),
    "extrution_field": attributes.get("Extrution"),
    "extrution_metadata": gis_doc.get("field_metadata", {}),
    "gis_to_model_nearest_avg_m": sum(gis_to_model) / len(gis_to_model),
    "gis_to_model_nearest_max_m": max(gis_to_model),
    "model_to_gis_nearest_avg_m": sum(model_to_gis) / len(model_to_gis),
    "model_to_gis_nearest_max_m": max(model_to_gis),
    "model_lower_perimeter_vertex_count": len(base_xy),
}
HERE.joinpath("blender_probe.json").write_text(json.dumps(asset_probe, indent=2) + "\n", encoding="utf-8")

# Read-only inspect the current master marker and linked library contract.
assert MASTER.is_file(), f"Missing master file: {MASTER}"
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
markers = [obj for obj in bpy.data.objects if obj.name == "Placement_class_of_1950"]
linked_class50_collections = [
    {"name": c.name, "library": c.library.filepath if c.library else None}
    for c in bpy.data.collections if "class_of_1950" in c.name.lower()
]
marker_data = []
for marker in markers:
    marker_data.append({
        "name": marker.name,
        "type": marker.type,
        "location": [float(v) for v in marker.location],
        "rotation_degrees": [math.degrees(float(v)) for v in marker.rotation_euler],
        "scale": [float(v) for v in marker.scale],
        "instance_collection": marker.instance_collection.name if marker.instance_collection else None,
        "instance_collection_library": (marker.instance_collection.library.filepath
                                         if marker.instance_collection and marker.instance_collection.library else None),
    })
master_probe = {
    "master_file": MASTER.name,
    "placement_marker_count": len(markers),
    "markers": marker_data,
    "related_linked_collections": linked_class50_collections,
}
HERE.joinpath("master_probe.json").write_text(json.dumps(master_probe, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"asset_probe": asset_probe, "master_probe": master_probe}, indent=2))
