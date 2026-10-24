import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for n in bpy.data.materials['KNOY_Purdue_Red_Brick'].node_tree.nodes:
 if n.type=='MIX':
  print(n.name,[(i,n.inputs[i].name,n.inputs[i].identifier,n.inputs[i].type) for i in range(len(n.inputs))])

