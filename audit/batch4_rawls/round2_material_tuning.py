import bpy,os
p=os.path.abspath('modular/buildings/rawls_hall.blend');bpy.ops.wm.open_mainfile(filepath=p)
g=bpy.data.materials['RAWL_CurtainWall_Glass'];bs=next(n for n in g.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.44,.57,.62,1);bs.inputs['Roughness'].default_value=.20;bs.inputs['Metallic'].default_value=.16;bs.inputs['Transmission Weight'].default_value=0.0
if 'Coat Weight' in bs.inputs:bs.inputs['Coat Weight'].default_value=.42
if 'Coat Roughness' in bs.inputs:bs.inputs['Coat Roughness'].default_value=.14
g.diffuse_color=(.44,.57,.62,1)
# Fine plaster variation on the source-derived interior partitions.
w=bpy.data.materials.get('RAWL_Interior_WarmWhite')
if w and w.use_nodes:
 bs=next(n for n in w.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 nt=w.node_tree.nodes;links=w.node_tree.links
 if not any(n.label=='Subtle plaster grain R2' for n in nt):
  tc=nt.new('ShaderNodeTexCoord');noise=nt.new('ShaderNodeTexNoise');noise.label='Subtle plaster grain R2';noise.inputs['Scale'].default_value=20;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.55
  ramp=nt.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.73,.72,.68,1);ramp.color_ramp.elements[1].color=(.81,.80,.76,1)
  bump=nt.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.045;bump.inputs['Distance'].default_value=.0004
  links.new(tc.outputs['Object'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],bs.inputs['Base Color']);links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
  w['evidence_note']='Subtle plaster variation is a render-scale surface cue; the 2024 plan provides no finish specification.'
bpy.ops.wm.save_as_mainfile(filepath=p);print('saved glass',list(g.diffuse_color),'interior wall texture enhanced')
