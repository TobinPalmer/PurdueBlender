import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "audit" / "sigma_kappa" / "sources" / "purdue_gis_fid780_raw.json"
ASSET = ROOT / "modular" / "buildings" / "massing_house_301840869_1b80ace.blend"
OUT = ROOT / "audit" / "sigma_kappa" / "independent_grade" / "blender_probe.json"

feature = json.loads(RAW.read_text(encoding="utf-8-sig"))["features"][0]
ring = feature["geometry"]["rings"][0][:-1]
lat0, lon0 = 40.4274, -86.9137
gis = [((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0) for lon,lat in ring]
collection = bpy.data.collections.get("Asset_massing_house_301840869_1b80ace")
obj = bpy.data.objects.get("House_301840869")
assert obj and collection and obj.type == "MESH"
base = [(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z) < 1e-5]
residuals = [min(math.hypot(x-bx,y-by) for bx,by in base) for x,y in gis]
depsgraph = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(depsgraph)
points = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
bounds = [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
external = [i.filepath for i in bpy.data.images if i.filepath and i.source != "GENERATED"]
probe = {
    "blend_reopened": bpy.data.filepath.lower() == str(ASSET).lower(),
    "blender_version": bpy.app.version_string,
    "asset_path": "modular/buildings/massing_house_301840869_1b80ace.blend",
    "collection_exists": collection is not None,
    "collection_objects": sorted(o.name for o in collection.objects),
    "scene_objects": sorted((o.name,o.type) for o in bpy.data.objects),
    "object_name": obj.name,
    "object_type": obj.type,
    "object_location": list(obj.location),
    "object_rotation_euler": list(obj.rotation_euler),
    "object_scale": list(obj.scale),
    "mesh_vertex_count": len(obj.data.vertices),
    "mesh_face_count": len(obj.data.polygons),
    "evaluated_bounds_xyz_m": bounds,
    "gis_fid": feature["attributes"]["FID"],
    "gis_name": feature["attributes"]["BUILDING_N"],
    "gis_address": feature["attributes"]["ADDRESS"],
    "gis_unique_vertices": len(gis),
    "gis_base_match_count": sum(d <= 0.0001 for d in residuals),
    "gis_max_base_residual_m": max(residuals),
    "external_image_paths": external,
    "material_names": [m.name for m in obj.data.materials],
}
OUT.write_text(json.dumps(probe,indent=2)+"\n",encoding="utf-8")
print(json.dumps(probe,indent=2))
