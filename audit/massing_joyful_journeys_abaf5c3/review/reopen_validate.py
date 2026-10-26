import bpy,json,math
from mathutils import Vector
p=r'modular/buildings/massing_joyful_journeys_abaf5c3.blend';bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene;obs=[]
for o in sc.objects:
 b=[o.matrix_world@Vector(v) for v in o.bound_box]
 bounds=[[float(min(v[i] for v in b)),float(max(v[i] for v in b))] for i in range(3)]
 obs.append({'name':o.name,'type':o.type,'bounds_world_m':bounds,'vertex_count':len(o.data.vertices) if o.type=='MESH' else None,'face_count':len(o.data.polygons) if o.type=='MESH' else None,'modifiers':[m.name for m in o.modifiers],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'matrix_world_translation':[float(v) for v in o.matrix_world.translation],'rotation_euler':[float(v) for v in o.rotation_euler],'scale':[float(v) for v in o.scale],'properties':{k:o[k] for k in o.keys()}})
res={'opened_directly':True,'asset':p,'scene':sc.name,'scenes':[s.name for s in bpy.data.scenes],'collections':[c.name for c in bpy.data.collections],'scene_collection_children':[c.name for c in sc.collection.children],'object_count':len(sc.objects),'objects':obs,'linked_libraries':[l.filepath for l in bpy.data.libraries],'unpacked_external_images':[{'name':i.name,'path':i.filepath} for i in bpy.data.images if i.filepath and not i.packed_file]}
open(r'audit/massing_joyful_journeys_abaf5c3/review/direct_reopen_r1.json','w').write(json.dumps(res,indent=2))
