import bpy, json
from mathutils import Vector
p=r'modular/buildings/massing_joyful_journeys_abaf5c3.blend'
bpy.ops.wm.open_mainfile(filepath=p)
scene=bpy.context.scene
out=[]
for o in scene.objects:
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    bounds=[[float(min(v[i] for v in bb)),float(max(v[i] for v in bb))] for i in range(3)]
    out.append({'name':o.name,'type':o.type,'bounds':bounds,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'faces':len(o.data.polygons) if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'properties':{k:o[k] for k in o.keys()}})
res={'scene':scene.name,'scenes':[s.name for s in bpy.data.scenes],'collections':[c.name for c in bpy.data.collections],'scene_children':[c.name for c in scene.collection.children],'objects':out,'libraries':[l.filepath for l in bpy.data.libraries],'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]}
open(r'audit/massing_joyful_journeys_abaf5c3/review/direct_reopen_before.json','w').write(json.dumps(res,indent=2))
