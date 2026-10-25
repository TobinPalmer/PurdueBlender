import bpy, json
from mathutils import Vector

path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\south_hall.blend"
bpy.ops.wm.open_mainfile(filepath=path)
scene = bpy.context.scene
asset = bpy.data.collections.get("Asset_south_hall")
rows = []
for ob in (asset.all_objects if asset else scene.objects):
    if ob.type not in {"MESH", "CURVE", "FONT", "EMPTY"}:
        continue
    bounds = [ob.matrix_world @ Vector(c) for c in ob.bound_box] if ob.type != "EMPTY" else [ob.matrix_world.translation]
    if bounds:
        mn = [min(p[i] for p in bounds) for i in range(3)]
        mx = [max(p[i] for p in bounds) for i in range(3)]
    else:
        mn = mx = list(ob.matrix_world.translation)
    rows.append({"name": ob.name, "type": ob.type, "loc": list(ob.location), "dim": list(ob.dimensions), "bounds": [mn, mx], "parent": ob.parent.name if ob.parent else None, "parent_matrix": [list(r) for r in ob.parent.matrix_world] if ob.parent else None, "matrix_world": [list(r) for r in ob.matrix_world], "materials": [m.name for m in ob.data.materials] if getattr(ob, "data", None) else [], "verts": len(ob.data.vertices) if ob.type == "MESH" else None, "faces": len(ob.data.polygons) if ob.type == "MESH" else None})
result = {"file": path, "scene": scene.name, "asset_collection": asset.name if asset else None, "asset_count": len(rows), "objects": rows, "materials": [m.name for m in bpy.data.materials], "world": scene.world.name if scene.world else None, "camera": scene.camera.name if scene.camera else None}
out = r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\south_hall_refine\probe_asset.json"
with open(out, "w", encoding="utf-8") as f: json.dump(result, f, indent=2)
print("PROBE", len(rows), "materials", len(bpy.data.materials), "scene", scene.name)
