import bpy,os,json
p=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=p)
# Keep measured 8 cm reveal offset; make pane surface a lighter, lightly reflective blue-gray.
m=bpy.data.materials['RAWL_CurtainWall_Glass'];m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.38,.55,.64,1);bs.inputs['Roughness'].default_value=.18;bs.inputs['Metallic'].default_value=.04;bs.inputs['Transmission Weight'].default_value=.05;bs.inputs['Alpha'].default_value=1;bs.inputs['IOR'].default_value=1.45
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.42;bs.inputs['Coat Roughness'].default_value=.12
if 'Emission Color' in bs.inputs:bs.inputs['Emission Color'].default_value=(.26,.39,.47,1);bs.inputs['Emission Strength'].default_value=.10
m.diffuse_color=(.38,.55,.64,1)
mb=bpy.data.materials['RAWL_Dark_Bronze_Metal'];bsb=next(n for n in mb.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsb.inputs['Base Color'].default_value=(.30,.22,.14,1);bsb.inputs['Roughness'].default_value=.32;bsb.inputs['Metallic'].default_value=.55;mb.diffuse_color=(.30,.22,.14,1)
bpy.ops.wm.save_as_mainfile(filepath=p)
print('saved visible glass material')
