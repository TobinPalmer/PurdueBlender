"""Fresh-process reopen checks for the Sigma Nu massing library."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_house_301841330_f58ae87.blend"
GIS = ROOT / "audit" / "sigma_nu" / "sources" / "purdue_gis_fid_758.json"
OUT = ROOT / "audit" / "sigma_nu" / "reopen_validation.json"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene_name = "Building_massing_house_301841330_f58ae87"
collection_name = "Asset_massing_house_301841330_f58ae87"
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
assert scene is not None, f"Missing scene {scene_name}"
assert collection is not None, f"Missing collection {collection_name}"
objects = list(collection.objects)
assert objects and all(obj.type == "MESH" for obj in objects)
body = bpy.data.objects.get("House_301841330")
assert body is not None and body.type == "MESH"

feature = json.loads(GIS.read_text(encoding="utf-8-sig"))
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
lat0, lon0 = 40.4274, -86.9137
x_scale = 111412.84 * math.cos(math.radians(lat0))
source_xy = [((lon-lon0)*x_scale, (lat-lat0)*111040.0) for lon,lat in ring]
base_xy = [(float(v.co.x), float(v.co.y)) for v in body.data.vertices if abs(v.co.z) < 1e-6]
ring_error = max(
    max(min(math.dist(p, q) for q in base_xy) for p in source_xy),
    max(min(math.dist(p, q) for q in source_xy) for p in base_xy),
)
world_points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
bounds = [[min(v[i] for v in world_points), max(v[i] for v in world_points)] for i in range(3)]
external_images = [img.filepath for img in bpy.data.images if img.source == "FILE"]
relative_dependencies = [
    value.filepath for value in bpy.data.libraries if value.filepath and not Path(value.filepath).is_absolute()
]
report = {
    "blender_reopened": True,
    "blender_version": bpy.app.version_string,
    "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "scene": scene.name,
    "scene_collection_present": True,
    "export_collection": collection.name,
    "export_collection_object_count": len(objects),
    "mesh_object_count": sum(obj.type == "MESH" for obj in objects),
    "body_object": body.name,
    "body_vertex_count": len(body.data.vertices),
    "base_ring_vertices": len(base_xy),
    "source_ring_vertices": len(source_xy),
    "symmetric_nearest_vertex_error_m": ring_error,
    "world_bounds_m": bounds,
    "body_modifiers": [modifier.name for modifier in body.modifiers],
    "external_file_images": external_images,
    "relative_library_dependencies": relative_dependencies,
    "source_supported_minimum_occupied_floors": 3,
    "estimated_story_division_z_m": [2.8, 5.0],
    "unresolved": [
        "Assessor and newsletter sources support parcel identity and at least three occupied floors, but not absolute height, exact floor elevations, roof form, or whether each occupied floor is above grade.",
        "GIS polygon is a roof/building outline proxy, not a surveyed structural-wall line.",
        "Facade bearing is inferred from road context; newsletter photograph is not georeferenced.",
    ],
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
