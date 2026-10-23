import bpy,json,os
p='modular/buildings/rawls_hall.blend';c=bpy.data.collections['Asset_rawls_hall']
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]
brick=bpy.data.materials.get('RAWL_Purdue_Red_Brick')
links=[]
if brick:
 for l in brick.node_tree.links:
  if l.from_node.type in {'TEX_BRICK','MIX_RGB','MIX','GEOMETRY','SEPARATE_XYZ','COMBXYZ','TEX_COORD'} or l.to_node.type in {'TEX_BRICK','MIX_RGB','MIX','BSDF_PRINCIPLED'}:
   links.append([l.from_node.type,l.from_node.name,l.from_socket.name,l.to_node.type,l.to_node.name,l.to_socket.name])
report={'asset_file':os.path.abspath(p),'export_collection':c.name,'objects':len(c.all_objects),'mesh_objects':sum(o.type=='MESH' for o in c.all_objects),'missing_images':missing,'asset_root_parent':bpy.data.objects['AssetRoot_rawls_hall'].parent.name if bpy.data.objects['AssetRoot_rawls_hall'].parent else None,'asset_root_location':list(bpy.data.objects['AssetRoot_rawls_hall'].location),'asset_root_rotation':list(bpy.data.objects['AssetRoot_rawls_hall'].rotation_euler),'asset_root_scale':list(bpy.data.objects['AssetRoot_rawls_hall'].scale),'brick_material_links':links}
with open('audit/batch4_rawls/checks.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
