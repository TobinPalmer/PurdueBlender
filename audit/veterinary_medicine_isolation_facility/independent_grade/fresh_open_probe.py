import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET_ID = "massing_veterinary_medicine_isolation_facility_66d1305"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / "veterinary_medicine_isolation_facility"
OUT = AUDIT / "independent_grade" / "fresh_open_probe.json"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

scene = bpy.data.scenes.get(SCENE_NAME)
collection = bpy.data.collections.get(COLLECTION_NAME)
assert scene is not None, "Expected building scene is missing"
assert collection is not None, "Expected exported asset collection is missing"
meshes = [obj for obj in collection.objects if obj.type == "MESH"]
assert meshes and len(meshes) == len(collection.objects), "Unexpected non-mesh objects in exported collection"
assert not any(obj.library is not None for obj in collection.objects), "Asset collection contains linked objects"

world_vertices = [obj.matrix_world @ vert.co for obj in meshes for vert in obj.data.vertices]
bounds = [[min(v[i] for v in world_vertices), max(v[i] for v in world_vertices)] for i in range(3)]
material_slots = sum(len(obj.material_slots) for obj in meshes)
missing_material_slots = [obj.name for obj in meshes if not obj.material_slots or any(slot.material is None for slot in obj.material_slots)]
external_images = [img.filepath for img in bpy.data.images if img.source == "FILE"]
external_libraries = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
shell = bpy.data.objects.get("GIS footprint exterior wall shell")
assert shell is not None and shell.type == "MESH", "GIS footprint shell is missing"
feature = json.loads((AUDIT / "purdue_gis_VMIF_feature.json").read_text(encoding="utf-8"))
ring = feature["geometry"]["rings"][0][:-1]
lat0, lon0 = 40.4274, -86.9137
mxlon = 111412.84 * math.cos(math.radians(lat0))
mlat = 111040.0
source_xy = [((lon-lon0)*mxlon, (lat-lat0)*mlat) for lon, lat in ring]
def centroid(points):
    area2 = cx = cy = 0.0
    for i,(x,y) in enumerate(points):
        x2,y2=points[(i+1)%len(points)]
        cross=x*y2-x2*y
        area2+=cross; cx+=(x+x2)*cross; cy+=(y+y2)*cross
    return (cx/(3*area2),cy/(3*area2))
anchor = centroid(source_xy)
source_local = sorted((x-anchor[0],y-anchor[1]) for x,y in source_xy)
shell_local = sorted(set((round(float(v.co.x),8),round(float(v.co.y),8)) for v in shell.data.vertices))
source_local_rounded = sorted((round(x,8),round(y,8)) for x,y in source_local)
assert len(shell_local) == len(source_local_rounded), f"Shell vertex count mismatch: {len(shell_local)} vs {len(source_local_rounded)}"
footprint_vertex_error = max(math.hypot(a[0]-b[0],a[1]-b[1]) for a,b in zip(shell_local,source_local_rounded))
anchor_saved = list(scene.get("anchor_campus_xy_m", []))
anchor_error = math.hypot(anchor_saved[0]-anchor[0],anchor_saved[1]-anchor[1])

report = {
    "fresh_open": True,
    "blender_version": bpy.app.version_string,
    "asset": str(ASSET.relative_to(ROOT)),
    "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "scene": scene.name,
    "collection": collection.name,
    "collection_object_count": len(collection.objects),
    "mesh_count": len(meshes),
    "vertex_count": sum(len(obj.data.vertices) for obj in meshes),
    "polygon_count": sum(len(obj.data.polygons) for obj in meshes),
    "local_bounds_m": bounds,
    "gis_footprint_shell_vertices": len(shell_local),
    "gis_footprint_max_vertex_xy_error_m": footprint_vertex_error,
    "gis_centroid_anchor_xy_m": list(anchor),
    "saved_scene_anchor_xy_m": anchor_saved,
    "anchor_error_m": anchor_error,
    "material_slot_count": material_slots,
    "objects_missing_material_assignments": missing_material_slots,
    "external_file_images": external_images,
    "external_libraries": external_libraries,
    "checks": [
        "opened from saved blend in a fresh Blender process",
        "expected scene and exported asset collection present",
        "export collection contains only local mesh objects",
        "GIS perimeter shell vertices compared directly to the saved feature polygon",
        "saved campus anchor compared to computed GIS polygon centroid",
        "external image and library dependencies enumerated",
    ],
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
