import bpy
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
print('mat',tuple(m.diffuse_color))
for n in m.node_tree.nodes:
 print(n.name,n.type)
 if n.type=='TEX_BRICK':print('tile',tuple(n.inputs['Color1'].default_value),tuple(n.inputs['Color2'].default_value),tuple(n.inputs['Mortar'].default_value))
 if n.type=='BSDF_PRINCIPLED':print('base',tuple(n.inputs['Base Color'].default_value),'links',[(l.from_node.name,l.from_socket.name) for l in n.inputs['Base Color'].links])
for name in ['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 o=bpy.data.objects[name];print(name,[(m.name if m else None) for m in o.data.materials],len(o.data.polygons))
