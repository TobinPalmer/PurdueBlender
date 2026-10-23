import bpy,json
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend';bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_elliott_hall_of_music']
allobjs=list(bpy.context.scene.objects)
report={'scene_objects':len(allobjs),'collection_objects':len(c.all_objects),'outside_export':[o.name for o in allobjs if o.name not in {x.name for x in c.all_objects}],'images':[{'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images],'materials':[{'name':m.name,'use_nodes':m.use_nodes,'nodes':[n.bl_idname for n in m.node_tree.nodes] if m.use_nodes and m.node_tree else []} for m in c.all_objects if False]}
mat={}
for o in c.all_objects:
 if o.type=='MESH':
  for m in o.data.materials:
   if m and m.name not in mat:
    mat[m.name]={'nodes':[n.bl_idname for n in m.node_tree.nodes] if m.use_nodes and m.node_tree else [],'image_nodes':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes and m.node_tree else []}
report['materials']=mat
print(json.dumps(report,indent=2))
