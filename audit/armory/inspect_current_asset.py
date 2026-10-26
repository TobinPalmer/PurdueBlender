from pathlib import Path
import json
import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/armory.blend"
OUT = Path(__file__).resolve().parent / "prebuild_inventory.json"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection = bpy.data.collections.get("Asset_armory")
assert collection
dg = bpy.context.evaluated_depsgraph_get()
items = []
for obj in collection.all_objects:
    ev = obj.evaluated_get(dg)
    if obj.type == "MESH":
        mesh = ev.to_mesh()
        points = [ev.matrix_world @ v.co for v in mesh.vertices]
        ev.to_mesh_clear()
        bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None
    else:
        bounds = None
    items.append({"name": obj.name, "type": obj.type, "location": list(obj.location),
                  "dimensions": list(obj.dimensions), "bounds_world": bounds,
                  "parent": obj.parent.name if obj.parent else None,
                  "collections": sorted(c.name for c in obj.users_collection),
                  "hide_render": obj.hide_render, "hide_viewport": obj.hide_viewport})
OUT.write_text(json.dumps({"scene": bpy.context.scene.name, "collection_object_count": len(items),
                           "objects": items}, indent=2), encoding="utf-8")
print(str(OUT))
