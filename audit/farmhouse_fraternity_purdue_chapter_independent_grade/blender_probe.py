import bpy, json, hashlib, os
from mathutils import Vector
p=r'modular/buildings/massing_farmhouse_fraternity_purdue_chapter_0b8908b.blend'
out=r'audit/farmhouse_fraternity_purdue_chapter_independent_grade'
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
objs=[]
for o in bpy.data.objects:
    if o.type=='MESH':
        bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
        bounds=[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)]
        mats=[m.name for m in o.data.materials if m]
        objs.append({'name':o.name,'collection':[c.name for c in o.users_collection],'verts':len(o.data.vertices),'polygons':len(o.data.polygons),'bounds':bounds,'materials':mats,'modifiers':[m.type for m in o.modifiers]})
info={'scene':sc.name,'camera':sc.camera.name if sc.camera else None,'objects_total':len(bpy.data.objects),'mesh_objects':len(objs),'collections':[c.name for c in bpy.data.collections],'materials':[{'name':m.name,'nodes':len(m.node_tree.nodes) if m.use_nodes and m.node_tree else 0,'image_nodes':sum(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) if m.use_nodes and m.node_tree else 0} for m in bpy.data.materials],'libraries':[l.filepath for l in bpy.data.libraries],'images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images],'mesh_inventory':objs}
with open(os.path.join(out,'blender_probe.json'),'w') as f: json.dump(info,f,indent=2)
# Fresh-open render of candidate with saved presentation settings
if sc.camera:
    sc.render.filepath=os.path.join(out,'fresh_open_render.png')
    bpy.ops.render.render(write_still=True)
print(json.dumps({'scene':sc.name,'objects':len(bpy.data.objects),'meshes':len(objs),'materials':len(bpy.data.materials),'render':sc.render.filepath},indent=2))
