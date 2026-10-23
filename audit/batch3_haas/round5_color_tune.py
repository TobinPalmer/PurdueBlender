import bpy
P=bpy.data.filepath
brick=bpy.data.materials['Purdue_Red_Brick.001'];brick.diffuse_color=(.13,.021,.008,1)
for n in brick.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.13,.021,.008,1);n.inputs['Color2'].default_value=(.075,.010,.003,1);n.inputs['Mortar'].default_value=(.11,.045,.02,1)
roof=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];roof.diffuse_color=(.022,.003,.001,1)
for n in roof.node_tree.nodes:
 if n.type=='TEX_BRICK':
  n.inputs['Color1'].default_value=(.022,.003,.0012,1);n.inputs['Color2'].default_value=(.012,.0015,.0005,1);n.inputs['Mortar'].default_value=(.005,.0006,.0002,1)
 if n.type=='BUMP':n.inputs['Strength'].default_value=.1;n.inputs['Distance'].default_value=.002
bpy.ops.wm.save_as_mainfile(filepath=P)
