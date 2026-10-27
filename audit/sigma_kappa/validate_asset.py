import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "audit" / "sigma_kappa" / "sources" / "purdue_gis_fid780_raw.json"
ASSET_PATH = ROOT / "modular" / "buildings" / "massing_house_301840869_1b80ace.blend"
REPORT = ROOT / "audit" / "sigma_kappa" / "reopen_validation.json"

feature = json.loads(RAW.read_text(encoding="utf-8-sig"))["features"][0]
ring = feature["geometry"]["rings"][0][:-1]
lat0, lon0 = 40.4274, -86.9137
gis_xy = [
    ((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0)
    for lon,lat in ring
]
collection_name = "Asset_massing_house_301840869_1b80ace"
obj_name = "House_301840869"
collection = bpy.data.collections.get(collection_name)
obj = bpy.data.objects.get(obj_name)
assert bpy.data.filepath.lower() == str(ASSET_PATH).lower()
assert collection is not None and obj is not None and obj.type == "MESH"

base_xy = sorted({(round(v.co.x,6),round(v.co.y,6)) for v in obj.data.vertices if abs(v.co.z) < 1e-5})
residuals = []
for x,y in gis_xy:
    residuals.append(min(math.hypot(x-bx,y-by) for bx,by in base_xy))

depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(depsgraph)
world_points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)]
images = [image.filepath for image in bpy.data.images if image.filepath and image.source != "GENERATED"]
collection_objects = sorted(o.name for o in collection.objects)
report = {
    "reopened": True,
    "asset_path": "modular/buildings/massing_house_301840869_1b80ace.blend",
    "collection": collection_name,
    "collection_objects": collection_objects,
    "collection_object_count": len(collection_objects),
    "object": obj.name,
    "object_type": obj.type,
    "location": list(obj.location),
    "rotation_euler": list(obj.rotation_euler),
    "scale": list(obj.scale),
    "mesh_vertices": len(obj.data.vertices),
    "mesh_faces": len(obj.data.polygons),
    "evaluated_bounds_xyz_m": bounds,
    "gis_bounds_xy_m": [
        [min(x for x,y in gis_xy), max(x for x,y in gis_xy)],
        [min(y for x,y in gis_xy), max(y for x,y in gis_xy)],
    ],
    "gis_ring_vertices": len(gis_xy),
    "base_unique_vertices": len(base_xy),
    "gis_ring_missing_at_base": sum(1 for d in residuals if d > 0.0001),
    "gis_ring_max_residual_m": max(residuals),
    "gis_ring_comparison_tolerance_m": 0.0001,
    "external_images": images,
    "checks": {
        "expected_identity": obj.get("building_name") == "Sigma Kappa, Beta Sigma Chapter",
        "expected_collection": collection_name == collection.name,
        "single_mesh_collection": len(collection_objects) == 1 and collection_objects[0] == obj_name,
        "identity_transform": all(abs(v) < 1e-7 for v in obj.location) and all(abs(v) < 1e-7 for v in obj.rotation_euler) and all(abs(v-1.0) < 1e-7 for v in obj.scale),
        "footprint_vertices_present": len(residuals) == len(gis_xy) and max(residuals) <= 0.0001,
        "portable_images": len(images) == 0,
    },
}
REPORT.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
