import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector
asset_path = Path(bpy.data.filepath).resolve()
collection = bpy.data.collections.get("Asset_niswonger_aviation_tech")
if collection is None:
    raise RuntimeError("Expected export collection is missing")
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
root = bpy.data.objects.get("AssetRoot_niswonger_aviation_tech")
materialless = [o.name for o in meshes if not o.data.materials]
missing = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        path = Path(bpy.path.abspath(image.filepath))
        if not path.exists(): missing.append(str(image.filepath))
cache = {}
def world_matrix(obj):
    if obj in cache: return cache[obj]
    m = obj.matrix_local.copy()
    if obj.parent is not None: m = world_matrix(obj.parent) @ m
    cache[obj] = m
    return m
points = [world_matrix(o) @ Vector(c) for o in objects if o.type in {"MESH","CURVE","FONT"} for c in o.bound_box]
bounds = [[min(float(p[i]) for p in points), max(float(p[i]) for p in points)] for i in range(3)]
out = {
    "asset_path": str(asset_path),
    "sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
    "collection": collection.name,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "root_location": list(root.location) if root else None,
    "local_bounds_m": bounds,
    "materialless_meshes": materialless,
    "missing_external_images": missing,
    "r4_hvac_cluster_present": "NISW_R4_Roof_HVAC_Cluster" in {o.name for o in objects},
    "roof_shell_visibility": {n: (bpy.data.objects.get(n).hide_render if bpy.data.objects.get(n) else None) for n in ["NISW_R2_Roof_Brick_Wing","NISW_R2_Roof_Classroom_Wing","NISW_Photographic_Sloping_Roof","NISW_Flat_Roof_Membrane"]},
}
Path("audit/niswonger_aviation_tech_refine/independent_reopen_r4.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
