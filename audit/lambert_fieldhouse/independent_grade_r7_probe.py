import bpy,json
c=bpy.data.collections.get('Asset_lambert_fieldhouse')
objs=set(c.all_objects) if c else set()
materials={m for o in objs if o.type=='MESH' for m in o.data.materials if m}
print(json.dumps({'file':bpy.data.filepath,'collection':c.name if c else None,'objects':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'material_names':sorted(m.name for m in materials),'image_nodes':[{'material':m.name,'images':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]} for m in materials if m.use_nodes and m.node_tree and any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes)],'missing_material_meshes':[o.name for o in objs if o.type=='MESH' and not o.data.materials][:20]},indent=2))
