import bpy, json
from mathutils import Vector
path = bpy.data.filepath
out = {"file": path, "scenes": [], "objects": []}
for scene in bpy.data.scenes:
    out["scenes"].append(scene.name)
for obj in bpy.data.objects:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    out["objects"].append({"name": obj.name, "type": obj.type, "location": list(obj.location), "dimensions": list(obj.dimensions), "world_bounds": [[min(p[i] for p in corners) for i in range(3)], [max(p[i] for p in corners) for i in range(3)]], "vertices": len(obj.data.vertices) if obj.type == 'MESH' else None, "materials": [m.name for m in obj.data.materials] if obj.type == 'MESH' else []})
print("FAITH_WEST_SOURCE_ASSET " + json.dumps(out))
