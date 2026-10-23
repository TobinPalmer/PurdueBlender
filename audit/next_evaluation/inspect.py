import bpy,json,pathlib
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); result={}
for id in ['walc','class_of_1950','potter_engineering','mechanical_engineering','electrical_engineering','knoy_hall','bell_tower','felix_haas_hall','math_sciences','elliott_hall_of_music']:
 f=p/'modular/buildings'/ (id+'.blend')
 if not f.exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(f));c=bpy.data.collections.get('Asset_'+id);obs=list(c.all_objects);mats={m for o in obs if o.type=='MESH' for m in o.data.materials if m}; rows=[]
 for m in mats:
  nodes=m.node_tree.nodes if m.use_nodes else [];br=[n for n in nodes if n.type=='TEX_BRICK'];images=[n.image for n in nodes if n.type=='TEX_IMAGE' and n.image]
  rows.append({'name':m.name,'viewport':list(m.diffuse_color),'principled':[list(n.inputs['Base Color'].default_value) for n in nodes if n.type=='BSDF_PRINCIPLED'],'brick':[{'scale':n.inputs['Scale'].default_value,'width':n.inputs['Brick Width'].default_value,'height':n.inputs['Row Height'].default_value,'vector_link':[(l.from_node.type,l.from_socket.name) for l in n.inputs['Vector'].links]}for n in br],'images':[{'path':im.filepath,'packed':bool(im.packed_file),'exists':pathlib.Path(bpy.path.abspath(im.filepath)).exists()}for im in images]})
 result[id]={'objects':len(obs),'materials':rows,'unassigned_meshes':[o.name for o in obs if o.type=='MESH' and not o.data.materials]}
(p/'audit/next_evaluation/materials.json').write_text(json.dumps(result,indent=2))
