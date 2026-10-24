import bpy,json
rows=[]
for m in bpy.data.materials:
 if 'glass' in m.name.lower() or 'glazing' in m.name.lower():
  bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
  rows.append({'name':m.name,'alpha':m.diffuse_color[3],'transmission':bs.inputs['Transmission Weight'].default_value if bs and 'Transmission Weight' in bs.inputs else None,'roughness':bs.inputs['Roughness'].default_value if bs else None,'render_method':str(m.surface_render_method)})
print(json.dumps(rows,indent=2))
