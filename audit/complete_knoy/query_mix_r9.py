import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
m=bpy.data.materials['KNOY_Precast_Concrete'];n=next(x for x in m.node_tree.nodes if x.type=='MIX')
for i,s in enumerate(n.inputs):
 try: print(i,s.name,repr(s.default_value))
 except: pass
