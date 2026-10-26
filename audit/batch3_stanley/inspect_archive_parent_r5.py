import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for name in ['AssetRoot_stanley_coulter_hall','SC_Unverified_Architectural_Options_R5','SC_Dormer_North_0_Cheeks_and_Roof','SC_Dormer_North_0_Limestone_Sill','SC_Historic_Slate_Roof']:
 o=bpy.data.objects.get(name)
 if o:
  p=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type=='MESH' else []
  print(name,'parent',o.parent.name if o.parent else None,'loc',list(o.location),'mw',list(o.matrix_world.translation),'bound',[[min(q[i] for q in p) for i in range(3)],[max(q[i] for q in p) for i in range(3)]] if p else None,'cols',[c.name for c in o.users_collection] if hasattr(o,'users_collection') else None)
print('scene root children',[c.name for c in bpy.context.scene.collection.children])
