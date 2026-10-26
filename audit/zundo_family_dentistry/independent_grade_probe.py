import bpy, json, math, os
from mathutils import Vector
p=os.path.abspath('modular/buildings/zundo_family_dentistry.blend')
bpy.ops.wm.open_mainfile(filepath=p)
col=bpy.data.collections.get('Asset_massing_zundo_family_dentistry_f840e2b')
print('PROBE',json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'collection_count':len(col.objects),'objects':[{'name':o.name,'type':o.type,'mats':[m.name for m in o.data.materials] if getattr(o,'data',None) and hasattr(o.data,'materials') else [],'faces':len(o.data.polygons) if o.type=='MESH' else None} for o in col.objects]}))
print('SCENES',[(s.name,len(s.objects)) for s in bpy.data.scenes])
print('MATERIALS',[(m.name,m.users) for m in bpy.data.materials if m.users])
