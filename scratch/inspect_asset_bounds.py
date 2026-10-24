import bpy, json
from mathutils import Vector

name = bpy.context.scene.get("inspect_collection", "Asset_american_railway_building")
col = bpy.data.collections.get(name)
if col is None:
    raise RuntimeError(f"missing collection {name}")
def bound(objects, matrix_attr):
    points=[]
    for obj in objects:
        if obj.type not in {'MESH','CURVE','FONT'}:
            continue
        matrix=getattr(obj,matrix_attr)
        points.extend(matrix @ Vector(corner) for corner in obj.bound_box)
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
all_objs=list(col.all_objects)
direct=list(col.objects)
large=[]
for obj in all_objs:
    if obj.type not in {'MESH','CURVE','FONT'}: continue
    vals=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    if max(abs(v.x) for v in vals)>30 or max(abs(v.y) for v in vals)>30:
        large.append({"name":obj.name,"parent":obj.parent.name if obj.parent else None,"collection_names":[c.name for c in obj.users_collection],"world":[[min(v[i] for v in vals),max(v[i] for v in vals)] for i in range(3)],"local":[[min((obj.matrix_local @ Vector(corner))[i] for corner in obj.bound_box),max((obj.matrix_local @ Vector(corner))[i] for corner in obj.bound_box)] for i in range(3)]})
print(json.dumps({"path":bpy.data.filepath,"collection":name,"direct_count":len(direct),"all_count":len(all_objs),"direct_world_bounds":bound(direct,'matrix_world'),"all_world_bounds":bound(all_objs,'matrix_world'),"all_local_bounds":bound(all_objs,'matrix_local'),"large_objects":large[:20]},indent=2))
