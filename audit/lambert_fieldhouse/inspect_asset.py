import bpy, json
from mathutils import Vector
path=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lambert_fieldhouse.blend'
bpy.ops.wm.open_mainfile(filepath=path)
out=[]
for c in bpy.data.collections:
    if 'LAMB' in c.name or 'lambert' in c.name.lower() or c.name in ['Asset_lambert_fieldhouse','Interior','Preview_Rig']:
        print('COL',c.name,'objs',len(c.objects),'children', [x.name for x in c.children])
asset=bpy.data.collections.get('Asset_lambert_fieldhouse')
for o in bpy.data.objects:
    if asset and o.name not in asset.all_objects: continue
    bb=[o.matrix_world @ Vector(v) for v in o.bound_box]
    lo=[min(v[i] for v in bb) for i in range(3)]; hi=[max(v[i] for v in bb) for i in range(3)]
    mats=[m.name for m in o.data.materials] if getattr(o.data,'materials',None) else []
    out.append({'name':o.name,'type':o.type,'collection':[c.name for c in o.users_collection],'bounds':[lo,hi],'dims':list(o.dimensions),'materials':mats})
open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/lambert_fieldhouse/asset_inventory.json','w').write(json.dumps(out,indent=2))
print('SCENE',bpy.context.scene.render.engine,bpy.context.scene.camera.name if bpy.context.scene.camera else None)
