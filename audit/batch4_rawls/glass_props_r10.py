import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_rawls\rawls_hall_r10_candidate.blend')
m=bpy.data.materials['RAWL_CurtainWall_Glass']; print('mat',m.name,m.diffuse_color[:],m.use_nodes)
for n in m.node_tree.nodes:
 if n.type=='BSDF_PRINCIPLED': print([(i.name, tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if i.name in ['Base Color','Alpha','Roughness','Metallic','Transmission Weight','IOR','Coat Weight','Specular IOR Level']])
