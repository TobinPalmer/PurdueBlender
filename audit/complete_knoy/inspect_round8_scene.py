from pathlib import Path
p=Path('modular/buildings/knoy_hall.blend')
import bpy
bpy.ops.wm.open_mainfile(filepath=str(p.resolve()))
for o in bpy.data.objects:
 if 'Roof_Evidence_Camera' in o.name or o.type=='CAMERA': print(o.name, tuple(o.location), tuple(o.rotation_euler), getattr(o.data,'type',None),getattr(o.data,'ortho_scale',None))
for c in bpy.data.collections:
 if c.name.startswith('Asset_knoy') or c.name=='Asset_knoy_hall':print('COLL',c.name,len(c.objects),len(c.children))
print('root objects',[(o.name,o.type,tuple(o.location)) for o in bpy.context.scene.collection.objects])
