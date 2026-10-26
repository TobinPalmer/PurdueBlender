import bpy,json,os,hashlib
from mathutils import Vector
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
blend=os.path.join(root,'modular','buildings','massing_farmhouse_fraternity_purdue_chapter_0b8908b.blend')
out=os.path.join(root,'audit','farmhouse_fraternity_purdue_chapter_independent_grade')
bpy.ops.wm.open_mainfile(filepath=blend)
sc=bpy.context.scene
objs=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  objs.append({'name':o.name,'verts':len(o.data.vertices),'polys':len(o.data.polygons),'bounds':[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)],'materials':[m.name for m in o.data.materials if m]})
data={'scene':sc.name,'camera':sc.camera.name if sc.camera else None,'objects_total':len(bpy.data.objects),'meshes':objs,'collections':[c.name for c in bpy.data.collections],'libraries':[l.filepath for l in bpy.data.libraries],'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images],'materials':[{'name':m.name,'image_nodes':sum(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) if m.use_nodes and m.node_tree else 0} for m in bpy.data.materials]}
with open(os.path.join(out,'revision2_blender_probe.json'),'w') as f:json.dump(data,f,indent=2)
if sc.camera:
 sc.render.filepath=os.path.join(out,'revision2_fresh_open_render.png')
 bpy.ops.render.render(write_still=True)
print(json.dumps({'scene':sc.name,'objects':len(bpy.data.objects),'meshes':len(objs),'materials':len(bpy.data.materials),'render':sc.render.filepath},indent=2))
