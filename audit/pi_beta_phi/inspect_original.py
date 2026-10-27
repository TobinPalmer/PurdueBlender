import bpy
import json
from mathutils import Vector

path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301838781_891384f.blend"
bpy.ops.wm.open_mainfile(filepath=path)
scene = bpy.context.scene
out = {"file": bpy.data.filepath, "scene": scene.name, "collections": [], "objects": []}
for coll in bpy.data.collections:
    out["collections"].append({"name": coll.name, "objects": [o.name for o in coll.objects]})
for obj in bpy.data.objects:
    row = {"name": obj.name, "type": obj.type, "location": list(obj.location), "rotation": list(obj.rotation_euler), "scale": list(obj.scale), "materials": [m.name if m else None for m in obj.data.materials] if obj.type == "MESH" else []}
    if obj.type == "MESH":
        pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
        if pts:
            row["bounds"] = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
        row["vertex_count"] = len(obj.data.vertices)
        row["polygon_count"] = len(obj.data.polygons)
    out["objects"].append(row)
print(json.dumps(out, indent=2))
