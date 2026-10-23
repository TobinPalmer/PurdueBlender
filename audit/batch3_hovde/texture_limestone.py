import bpy
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); path=P/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
mat=bpy.data.materials['Bedford_Indiana_Limestone']; mat.use_nodes=True
nt=mat.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial');out.location=(700,0)
bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.location=(450,0);bs.inputs['Roughness'].default_value=.72
geo=nt.nodes.new('ShaderNodeNewGeometry');geo.location=(-700,100)
noise=nt.nodes.new('ShaderNodeTexNoise');noise.location=(-460,100);noise.inputs['Scale'].default_value=8.0;noise.inputs['Detail'].default_value=2.0;noise.inputs['Roughness'].default_value=.62
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.location=(-180,130)
ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(.76,.735,.675,1)
ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.84,.81,.74,1)
bump=nt.nodes.new('ShaderNodeBump');bump.location=(170,-120);bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0008
nt.links.new(geo.outputs['Position'],noise.inputs['Vector']);nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']);nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
mat.diffuse_color=(.82,.79,.72,1)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
assert len(bpy.data.collections['Asset_hovde_hall'].all_objects)==638
assert bpy.data.materials['Bedford_Indiana_Limestone'].node_tree.nodes.get('Noise Texture')
print('SAVED_REOPENED',len(bpy.data.collections['Asset_hovde_hall'].all_objects))
