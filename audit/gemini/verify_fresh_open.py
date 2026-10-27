"""Fresh-process validation for the Gemini building library (run by Blender)."""
import bpy, hashlib, json, math
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / "modular" / "buildings" / "massing_gemini_cooperative_fid825.blend"
if bpy.data.filepath and Path(bpy.data.filepath).resolve() != asset.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(asset))
collection_name = "Asset_massing_gemini_cooperative_fid825"
scene_name = "Building_massing_gemini_cooperative_fid825"
collection = bpy.data.collections.get(collection_name)
assert collection is not None, "Expected exported asset collection missing"
assert bpy.data.scenes.get(scene_name) is not None, "Expected building scene missing"
objects = [o for o in collection.all_objects if o.type == "MESH"]
assert objects, "No mesh geometry found in asset collection"
assert all(o.data.materials for o in objects), "Found mesh with no material"
coords = [o.matrix_world @ v.co for o in objects for v in o.data.vertices]
bounds = {axis: [min(getattr(v, axis) for v in coords), max(getattr(v, axis) for v in coords)]
          for axis in ("x", "y", "z")}
# Confirm the low slab cap still uses the official 14-point FID 825 outline.
feature = json.loads((root / "audit" / "gemini" / "fid825.geojson").read_text(encoding="utf-8"))["features"][0]
lat0, lon0 = 40.4274, -86.9137
ring_ll = feature["geometry"]["coordinates"][0][:-1]
ring_xy = [((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0) for lon,lat,*_ in ring_ll]
area2 = sum(ring_xy[i][0]*ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[(i+1)%len(ring_xy)][0]*ring_xy[i][1] for i in range(len(ring_xy)))
cx = sum((ring_xy[i][0]+ring_xy[(i+1)%len(ring_xy)][0])*(ring_xy[i][0]*ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[(i+1)%len(ring_xy)][0]*ring_xy[i][1]) for i in range(len(ring_xy)))/(3*area2)
cy = sum((ring_xy[i][1]+ring_xy[(i+1)%len(ring_xy)][1])*(ring_xy[i][0]*ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[(i+1)%len(ring_xy)][0]*ring_xy[i][1]) for i in range(len(ring_xy)))/(3*area2)
expected = [(x-cx,y-cy) for x,y in ring_xy]
slab = collection.objects.get("Gemini | footprint ground and lower-floor slab")
assert slab is not None, "GIS footprint slab missing"
slab_coords = [slab.matrix_world @ v.co for v in slab.data.vertices]
zmin = min(v.z for v in slab_coords)
actual = sorted(set((round(v.x,6),round(v.y,6)) for v in slab_coords if abs(v.z-zmin)<1e-5))
assert len(actual) == len(expected) == 14, f"Expected 14 unique GIS ring points, found {len(actual)}"
max_footprint_error = max(min(math.hypot(x-ax,y-ay) for ax,ay in actual) for x,y in expected)
assert max_footprint_error < 1e-5, f"GIS slab outline changed: max vertex error {max_footprint_error} m"
report = {
    "fresh_open": True,
    "loaded_file": str(Path(bpy.data.filepath).resolve()),
    "asset_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
    "scene": scene_name,
    "collection": collection_name,
    "mesh_object_count": len(objects),
    "vertex_count": sum(len(o.data.vertices) for o in objects),
    "face_count": sum(len(o.data.polygons) for o in objects),
    "bounds_local_m": bounds,
    "gis_footprint_check": {"fid": 825, "unique_slab_xy_vertices": len(actual), "max_nearest_vertex_error_m": max_footprint_error},
    "all_meshes_material_assigned": True,
}
(root / "audit" / "gemini" / "fresh_open_validation.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
