import bpy,json
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_CurtainWall_Glass','RAWL_Bedford_Limestone','RAWL_Concrete_Floor','RAWL_Roof_Membrane','RAWL_Purdue_Red_Brick']:
 m=bpy.data.materials.get(n)
 if not m:continue
 d={'name':n,'diffuse':list(m.diffuse_color),'use_nodes':m.use_nodes}
 if m.use_nodes:
  for node in m.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED':d['bsdf']={inp.name: (list(inp.default_value) if hasattr(inp.default_value,'__len__') else inp.default_value) for inp in node.inputs if inp.name in ['Base Color','Roughness','Metallic','Transmission Weight','Alpha','IOR','Coat Weight','Normal']}
 print(json.dumps(d))
o=bpy.data.objects['RAWL_Atrium_Mezzanine_Balustrades'];print('balustrade verts:',[list(v.co) for v in o.data.vertices[:30]])
