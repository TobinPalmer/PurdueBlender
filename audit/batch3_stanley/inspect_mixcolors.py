import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for mn in ['Bedford_Indiana_Limestone','Historic_Slate_Roof_Procedural']:
 n=bpy.data.materials[mn].node_tree.nodes['Mix']
 print(mn,tuple(n.inputs[6].default_value),tuple(n.inputs[7].default_value),n.inputs[0].default_value)
