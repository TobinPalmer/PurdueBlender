import bpy
for n in ['HAAS_GooglePhotos_RedClayTiles_estimated','Purdue_Red_Brick.001','HAAS_Photo_DarkRoof_estimated']:
 m=bpy.data.materials.get(n);print('\n',n,'diff',tuple(m.diffuse_color));
 for no in m.node_tree.nodes:
  if no.type=='BSDF_PRINCIPLED':print('base',tuple(no.inputs['Base Color'].default_value),'links',[(x.from_node.name,x.from_socket.name) for x in no.inputs['Base Color'].links]);
  elif no.type=='TEX_BRICK':print('brick',no.inputs['Color1'].default_value[:],no.inputs['Color2'].default_value[:],no.inputs['Mortar'].default_value[:], 'links',[(x.from_node.name,x.from_socket.name) for x in no.inputs['Vector'].links])
for o in bpy.data.objects:
 if o.name.startswith('HAAS_Photo_') and 'Roof' in o.name: print(o.name,[m.name if m else None for m in o.data.materials])
