import bpy,json
for name in ['Beering_Purdue_Red_Brick','Beering_Roof_Membrane','Indiana_Bedford_Limestone']:
 m=bpy.data.materials[name]; nt=m.node_tree
 print('\nMATERIAL',name)
 for n in nt.nodes:
  if n.type in {'BSDF_PRINCIPLED','VALTORGB','MIX','MIX_RGB','RGB','TEX_NOISE','TEX_COORD','TEX_BRICK','BUMP'}:
   print(n.name,n.type)
   if n.type=='VALTORGB':
    for e in n.color_ramp.elements: print(' elem',e.position,tuple(e.color))
   elif n.type=='MIX': print('factor',n.inputs[0].default_value)
   elif n.type=='BSDF_PRINCIPLED':
    for i in ['Base Color','Roughness','Metallic']: print(i,'default',tuple(n.inputs[i].default_value) if hasattr(n.inputs[i].default_value,'__len__') else n.inputs[i].default_value)
    print('connections',[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in nt.links if l.to_node==n])
   elif n.type=='TEX_NOISE': print('scale',n.inputs.get('Scale').default_value,'detail',n.inputs.get('Detail').default_value)
for o in bpy.data.objects:
 if o.type=='MESH' and ('Roof_Membrane' in o.name): print('ROOF_OBJ',o.name,[m.name if m else None for m in o.data.materials],o.hide_render)
