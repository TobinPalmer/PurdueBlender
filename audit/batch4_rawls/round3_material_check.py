import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');m=bpy.data.materials['RAWL_CurtainWall_Glass'];print('blend',m.surface_render_method,'diffuse',list(m.diffuse_color));
for n in m.node_tree.nodes: print(n.name,n.type,{i.name:tuple(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value for i in n.inputs if i.name in ['Alpha','Base Color','Transmission Weight','Emission Color','Emission Strength']})
