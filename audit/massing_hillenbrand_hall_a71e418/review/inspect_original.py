import bpy,json,math
from mathutils import Vector
p=r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\modular\buildings\massing_hillenbrand_hall_a71e418.blend'
bpy.ops.wm.open_mainfile(filepath=p)
out={'file':bpy.data.filepath,'scenes':[s.name for s in bpy.data.scenes],'collections':[c.name for c in bpy.data.collections],'objects':[]}
for o in bpy.data.objects:
 if o.type=='MESH':
  b=[o.matrix_world @ Vector(c) for c in o.bound_box]
  out['objects'].append({'name':o.name,'type':o.type,'verts':len(o.data.vertices),'faces':len(o.data.polygons),'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'bounds':[[min(v[i] for v in b),max(v[i] for v in b)] for i in range(3)],'materials':[m.name for m in o.data.materials]})
print(json.dumps(out,indent=2))
