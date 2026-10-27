"""Fresh-process validation for the standalone Kappa Delta library."""
from pathlib import Path
import bpy, json

root=Path(__file__).resolve().parents[2]
asset_path=root/"modular"/"buildings"/"kappa_delta.blend"
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
asset=bpy.data.collections.get("Asset_kappa_delta")
assert asset is not None, "asset collection missing after reopening"
assert bpy.context.scene.name=="Building_kappa_delta"
objects=list(asset.all_objects)
meshes=[o for o in objects if o.type=="MESH"]
assert len(objects)>1000 and len(meshes)>1000
materials={m.name for o in objects for m in o.data.materials if m}
assert len(materials)>=10
missing=[]
for m in bpy.data.materials:
    if m.users and m.use_nodes and not m.node_tree:
        missing.append(m.name)
assert not missing, f"materials missing node trees: {missing}"
images=[im.filepath for im in bpy.data.images if im.users and im.source=="FILE"]
assert not images, f"external image references found: {images}"
worldverts=[]
for obj in meshes:
    for v in obj.data.vertices:
        worldverts.append(obj.matrix_world@v.co)
mins=[min(v[i] for v in worldverts) for i in range(3)]
maxs=[max(v[i] for v in worldverts) for i in range(3)]
assert all(maxs[i]>mins[i] for i in range(3))
assert maxs[2] > 15.0 and maxs[2] < 18.0
report={"asset":str(asset_path),"reopened":True,"scene":bpy.context.scene.name,"asset_collection":"Asset_kappa_delta","objects":len(objects),"mesh_objects":len(meshes),"materials":len(materials),"external_image_references":len(images),"world_bounds_m":{"min":mins,"max":maxs}}
(root/"audit"/"kappa_delta"/"fresh_open_validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("KAPPA_DELTA_FRESH_OPEN_VALIDATION_PASS",json.dumps(report))
