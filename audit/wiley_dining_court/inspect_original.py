import bpy,json,hashlib
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_wiley_dining_court_wdct_8a6c669.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
objs=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  cs=[o.matrix_world@v.co for v in o.data.vertices]
  objs.append({'name':o.name,'verts':len(o.data.vertices),'faces':len(o.data.polygons),'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'bounds':[[min(v[i] for v in cs),max(v[i] for v in cs)] for i in range(3)] if cs else []})
print(json.dumps({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest().upper(),'scenes':[s.name for s in bpy.data.scenes],'collections':[c.name for c in bpy.data.collections],'objects':objs},indent=2))
