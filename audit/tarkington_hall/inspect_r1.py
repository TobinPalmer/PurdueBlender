import bpy, json
from pathlib import Path
p=Path(bpy.data.filepath)
cols=[]
for c in bpy.data.collections:
    objs=list(c.objects)
    if objs:
        cols.append({'name':c.name,'objects':len(objs),'types':{t:sum(1 for o in objs if o.type==t) for t in set(o.type for o in objs)},'direct_objects':[o.name for o in objs[:12]]})
objs=list(bpy.data.objects)
mesh_objs=[o for o in objs if o.type=='MESH']
coords=[]
for o in mesh_objs:
    for v in o.bound_box:
        coords.append(o.matrix_world @ __import__('mathutils').Vector(v))
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)] if coords else None
mats=[]
for m in bpy.data.materials:
    if m.users: mats.append({'name':m.name,'users':m.users,'nodes':[(n.type,n.name) for n in m.node_tree.nodes] if m.use_nodes and m.node_tree else []})
print(json.dumps({'filepath':str(p),'scenes':[s.name for s in bpy.data.scenes],'object_count':len(objs),'types':{t:sum(1 for o in objs if o.type==t) for t in set(o.type for o in objs)},'bounds_world':bounds,'collections':cols,'materials':mats},indent=2))
