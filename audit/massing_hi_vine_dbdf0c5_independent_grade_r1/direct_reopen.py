import bpy, json
from mathutils import Vector
asset=r'modular/buildings/massing_hi_vine_dbdf0c5.blend'
bpy.ops.wm.open_mainfile(filepath=asset)
scene=bpy.context.scene
objects=[]
for o in scene.objects:
    bb=[o.matrix_world @ Vector(v) for v in o.bound_box]
    bounds=[[float(min(v[i] for v in bb)), float(max(v[i] for v in bb))] for i in range(3)] if bb else None
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()) if o.type=='MESH' else o
    mesh=ev.to_mesh() if o.type=='MESH' else None
    eval_count=len(mesh.vertices) if mesh else None
    if mesh: ev.to_mesh_clear()
    objects.append({'name':o.name,'type':o.type,'bounds_world_m':bounds,'vertex_count':len(o.data.vertices) if o.type=='MESH' else None,'face_count':len(o.data.polygons) if o.type=='MESH' else None,'evaluated_vertex_count':eval_count,'modifiers':[m.name for m in o.modifiers],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []})
result={'opened_directly':True,'asset':asset,'active_scene':scene.name,'scenes':[s.name for s in bpy.data.scenes],'collections':[c.name for c in bpy.data.collections],'scene_collection_children':[c.name for c in scene.collection.children],'objects':objects,'library_links':[l.filepath for l in bpy.data.libraries],'unpacked_external_images':[i.filepath for i in bpy.data.images if i.filepath and not i.packed_file]}
with open(r'audit/massing_hi_vine_dbdf0c5_independent_grade_r1/direct_reopen.json','w') as f: json.dump(result,f,indent=2)
