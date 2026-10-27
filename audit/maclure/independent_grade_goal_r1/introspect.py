import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
blend=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\maclure_cooperative.blend')
bpy.ops.wm.open_mainfile(filepath=str(blend))
col=bpy.data.collections.get('Asset_maclure_cooperative')
print('SCENE',bpy.context.scene.name,'COLLECTION',col.name if col else None,'OBJECTS',len(col.objects) if col else -1)
dg=bpy.context.evaluated_depsgraph_get()
for o in col.objects if col else []:
    ob=o.evaluated_get(dg)
    bb=[ob.matrix_world @ Vector(v) for v in ob.bound_box] if o.type in {'MESH','CURVE','FONT'} else []
    bounds=[[round(min(v[i] for v in bb),3),round(max(v[i] for v in bb),3)] for i in range(3)] if bb else None
    mats=[m.name for m in o.data.materials] if getattr(o,'data',None) and hasattr(o.data,'materials') else []
    print(json.dumps({'name':o.name,'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'parent':o.parent.name if o.parent else None,'bounds':bounds,'verts':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'mats':mats,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'custom':{k:o.get(k) for k in o.keys()}},default=str))
print('LIBRARIES',len(bpy.data.libraries))
for im in bpy.data.images:
 if im.source in {'FILE','TILED'}: print('IMAGE',im.name,im.filepath,im.source)
for m in bpy.data.materials: print('MAT',m.name,'nodes',m.use_nodes)
