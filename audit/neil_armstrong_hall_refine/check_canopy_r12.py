import bpy, json
from mathutils import Vector
o=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
print(json.dumps({"location":list(o.location),"rotation":list(o.rotation_euler),"scale":list(o.scale),"matrix_world":[list(r) for r in o.matrix_world],"raw_min":[min(v.co[i] for v in o.data.vertices) for i in range(3)],"raw_max":[max(v.co[i] for v in o.data.vertices) for i in range(3)],"world_min":[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],"world_max":[max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]},indent=2))
