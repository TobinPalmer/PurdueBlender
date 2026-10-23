import bpy,json
from mathutils import Vector
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_elliott_hall_of_music']
out=[]
for o in c.all_objects:
 b=[o.matrix_world @ Vector(v) for v in o.bound_box] if o.type=='MESH' else []
 out.append({'name':o.name,'type':o.type,'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'bounds':[[min(v[i] for v in b),max(v[i] for v in b)] for i in range(3)] if b else None,'mats':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []})
print(json.dumps(out,indent=2))
