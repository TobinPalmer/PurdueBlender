import bpy,json
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.all_objects:
 if o.type=='MESH':
  w=[o.matrix_world@Vector(corner) for corner in o.bound_box]
  mn=[min(v[i] for v in w) for i in range(3)]; mx=[max(v[i] for v in w) for i in range(3)]
  if any(k in o.name for k in ['Wall','Roof','Envelope','Brick','Cupola']):print(o.name, 'dim', [round(mx[i]-mn[i],2) for i in range(3)],'center',[round((mx[i]+mn[i])/2,2) for i in range(3)], 'mat',[m.name if m else None for m in o.data.materials])
