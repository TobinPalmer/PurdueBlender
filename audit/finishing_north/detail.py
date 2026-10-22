import bpy,json,pathlib
p=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');r={}
for id in ['elliott_hall_of_music','knoy_hall','bell_tower']:
 bpy.ops.wm.open_mainfile(filepath=str(p/'modular/buildings'/(id+'.blend')));c=bpy.data.collections['Asset_'+id];r[id]=[{'name':o.name,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'hide_render':o.hide_render,'mods':[(m.name,m.type) for m in o.modifiers]}for o in c.all_objects if id=='elliott_hall_of_music' or 'Wire' in o.name or 'Keystone' in o.name or 'Vent' in o.name];r[id+'_mat']=[{'name':m.name,'base':list(next((n.inputs['Base Color'].default_value for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),m.diffuse_color)) if m.use_nodes else list(m.diffuse_color)}for m in bpy.data.materials]
(p/'audit/finishing_north/detail.json').write_text(json.dumps(r,indent=2))
