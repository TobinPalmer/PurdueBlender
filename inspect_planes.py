import bpy,os
from mathutils import Vector
for p in [r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p)); print('\n',os.path.basename(p))
 for o in bpy.data.objects:
  if o.type=='MESH':
   mats=[m.name for m in o.data.materials if m]
   if any('Roof' in m or 'roof' in m or 'concrete' in m.lower() or 'limestone' in m.lower() or 'brick' in m.lower() for m in mats):
    d=o.dimensions
    if max(d)>5 or 'Roof' in o.name or 'roof' in o.name:
     print(o.name,tuple(round(v,1) for v in d),mats[:3])
