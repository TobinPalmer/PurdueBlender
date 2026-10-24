import bpy,os
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(r'modular/buildings/university_hall.blend'))
for mn in ['Univ_Weathered_Red_Brick','Univ_Slate_Roof']:
 m=bpy.data.materials[mn]; print('\n',mn)
 for n in m.node_tree.nodes: print(n.name,n.type)
