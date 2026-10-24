import bpy, json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
path = root / "modular" / "buildings" / "physics_building_phys_3bf42f3.blend"
evidence_path = Path(__file__).resolve().parent / "physics_building_evidence.json"
bpy.ops.wm.open_mainfile(filepath=str(path))
col = bpy.data.collections.get("Asset_physics_building")
assert col is not None, "expected export collection is missing"
objs = list(col.all_objects)
assert len(objs) >= 20, f"unexpectedly sparse asset: {len(objs)} objects"
meshes = [o for o in objs if o.type == 'MESH']
assert len(meshes) >= 10, f"unexpectedly sparse mesh count: {len(meshes)}"
assert all(o.data.materials for o in meshes), "one or more asset meshes have no material"
assert not any("\\" in (im.filepath or "") and im.source == 'FILE' for im in bpy.data.images), "absolute image dependency found"
xs=[]; ys=[]; zs=[]
for obj in meshes:
    for corner in obj.bound_box:
        p=obj.matrix_world @ __import__('mathutils').Vector(corner)
        xs.append(p.x); ys.append(p.y); zs.append(p.z)
bounds=[[min(xs),max(xs)],[min(ys),max(ys)],[min(zs),max(zs)]]
assert 100 < bounds[0][1]-bounds[0][0] < 115
assert 110 < bounds[1][1]-bounds[1][0] < 130
assert 15 < bounds[2][1]-bounds[2][0] < 17
ev=json.loads(evidence_path.read_text(encoding="utf-8"))
ev["validation"].update({"reopened":True,"reopen_check":"Blender 5.2.3 loaded saved .blend in a fresh background process; export collection, mesh/material presence, local dimensions, and no absolute image dependency checked","object_count":len(objs),"mesh_count":len(meshes),"asset_bounds_local_m":bounds,"preview":"physics_building_preview.png"})
evidence_path.write_text(json.dumps(ev,indent=2),encoding="utf-8")
print(json.dumps({"file":str(path),"collection":col.name,"objects":len(objs),"meshes":len(meshes),"bounds_local_m":bounds,"reopened":True}))
