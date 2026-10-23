import bpy
P=bpy.data.filepath;C=bpy.data.collections['Asset_felix_haas_hall']
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
m.diffuse_color=(.025,.003,.001,1)
for n in m.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.035,.004,.0015,1)
  n.inputs['Color2'].default_value=(.019,.002,.0008,1)
  n.inputs['Mortar'].default_value=(.012,.002,.0008,1)
g=bpy.data.materials['HAAS_Photo_BlueGlass'];g.diffuse_color=(.07,.12,.14,1)
g.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.07,.12,.14,1)
lm=bpy.data.materials['HAAS_Plan_Label_Charcoal'];lm.diffuse_color=(.045,.055,.06,1)
lm.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.045,.055,.06,1)
for o in C.objects:
 if o.name.startswith('HAAS_Plan_Label_'):
  o.location.z=4.25
  o.data.size=.9
bpy.ops.wm.save_as_mainfile(filepath=P)
