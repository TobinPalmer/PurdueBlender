import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
for name in ['ELLT_B3_Theatre_Seat_Brown_Fabric','ELLT_B3_Stage_Curtain_Red_Velour','ELLT_B3_Stage_Oak_Grain','ELLT_Roof_Red_Clay_Tile_Estimated']:
 m=bpy.data.materials[name];print(name)
 for n in m.node_tree.nodes:
  if n.type=='TEX_NOISE':print('noise',n.inputs['Scale'].default_value,n.inputs['Detail'].default_value,n.inputs['Roughness'].default_value)
  if n.type=='VALTORGB': print('ramp',[(e.position,tuple(e.color)) for e in n.color_ramp.elements])
  if n.type=='BUMP':print('bump',n.inputs['Strength'].default_value,n.inputs['Distance'].default_value)
