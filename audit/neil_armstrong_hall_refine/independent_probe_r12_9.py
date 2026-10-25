import bpy, hashlib, json
from pathlib import Path
ASSET = Path(r"C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\modular\\buildings\\neil_armstrong_hall.blend")
EXPECTED = "d8c78374b047fa1248d6d304db0cba1e7f39ff97d133ccc06d774eabf7558bf7"
OUT = Path(r"C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap\\audit\\neil_armstrong_hall_refine\\independent_reopen_r12_9.json")
asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if asset_hash != EXPECTED:
    raise RuntimeError(f"Current file hash mismatch: {asset_hash}")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col = bpy.data.collections.get("Asset_neil_armstrong_hall")
if col is None:
    raise RuntimeError("Expected export collection is missing")
objs = list(col.all_objects)
meshes = [o for o in objs if o.type == "MESH"]
root = bpy.data.objects.get("AssetRoot_neil_armstrong_hall")
missing = []
for im in bpy.data.images:
    if im.source == "FILE" and im.filepath:
        path = Path(bpy.path.abspath(im.filepath))
        if not path.exists(): missing.append(str(path))
materialless = [o.name for o in meshes if len(o.data.materials)==0]
null_slots = [o.name for o in meshes if any(m is None for m in o.data.materials)]
result = {
  "asset": str(ASSET), "sha256": asset_hash, "blender_version": bpy.app.version_string,
  "collection": col.name, "collection_object_count": len(objs), "scene_object_count": len(bpy.context.scene.objects),
  "mesh_count": len(meshes), "root_location": list(root.location) if root else None,
  "root_matrix_world": [list(row) for row in root.matrix_world] if root else None,
  "materialless_meshes": materialless, "null_material_slots": null_slots,
  "missing_external_images": missing,
  "collection_objects_not_scene": [o.name for o in objs if o.name not in bpy.context.scene.objects],
}
if not root or result["root_location"] != [0.0,0.0,0.0] or len(objs)!=446 or len(meshes)!=416 or materialless or null_slots or missing:
    raise RuntimeError(json.dumps(result, indent=2))
OUT.write_text(json.dumps(result, indent=2)+"\\n", encoding="utf-8")
print(json.dumps(result, indent=2))
