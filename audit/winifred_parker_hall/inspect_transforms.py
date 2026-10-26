import bpy,json
from pathlib import Path
from mathutils import Vector
for n in ['AssetRoot_winifred_parker_hall','Parker_EastWing_MainMass','Parker_EastWing_MainMass_North','Parker_EastWing_MainMass_South','Parker_EastWing_MainMass_Upper']:
 o=bpy.data.objects.get(n)
 if o:
  print(n,'type',o.type,'parent',o.parent.name if o.parent else None,'loc',list(o.location),'scale',list(o.scale),'dim',list(o.dimensions),'worldloc',list(o.matrix_world.translation),'localmat',[[round(v,4) for v in row] for row in o.matrix_local])
print('collections')
for c in bpy.data.collections:
 if 'Winifred' in c.name or c.name.startswith('27_') or c.name.startswith('28_') or c.name.startswith('29_') or 'Asset_winifred' in c.name:
  print(c.name,len(c.objects),'children',[x.name for x in c.children])