import bpy, os
ROOT=os.path.abspath('.')
ASSET=os.path.join(ROOT,'modular','buildings','materials_science_and_electrical_engineering_msee.blend')
OUT=os.path.join(ROOT,'audit','rework_batch_a')
bpy.ops.wm.open_mainfile(filepath=ASSET)
mat=bpy.data.materials['materials_science_and_electrical_engineering_msee_facade']
nt=mat.node_tree; nodes=nt.nodes; links=nt.links
brick=next(n for n in nodes if n.type=='TEX_BRICK')
geom=next(n for n in nodes if n.type=='NEW_GEOMETRY')
brick.inputs['Color1'].default_value=(0.17,0.046,0.032,1)
brick.inputs['Color2'].default_value=(0.25,0.079,0.054,1)
brick.inputs['Mortar'].default_value=(0.072,0.064,0.057,1)
brick.inputs['Mortar Size'].default_value=.03
# Derive the horizontal axis from each wall normal, so brick courses stay level on rotated faces.
for n in list(nodes):
 if n.name.startswith('R5 course '): nodes.remove(n)
pos=next(n for n in nodes if n.type=='NEW_GEOMETRY')
normal=nodes.new('ShaderNodeVectorMath'); normal.operation='CROSS_PRODUCT'; normal.name='R5 course tangent'; normal.label='Wall tangent from normal'; normal.location=(-620,0); normal.inputs[1].default_value=(0,0,1)
unit=nodes.new('ShaderNodeVectorMath'); unit.operation='NORMALIZE'; unit.name='R5 course unit'; unit.location=(-430,0)
dot=nodes.new('ShaderNodeVectorMath'); dot.operation='DOT_PRODUCT'; dot.name='R5 course coordinate'; dot.location=(-220,0)
sep=nodes.new('ShaderNodeSeparateXYZ'); sep.name='R5 course elevation'; sep.location=(-430,-200)
comb=nodes.new('ShaderNodeCombineXYZ'); comb.name='R5 wall-aligned brick coordinates'; comb.location=(-20,30)
links.new(pos.outputs['Normal'],normal.inputs[0]); links.new(normal.outputs['Vector'],unit.inputs[0]); links.new(pos.outputs['Position'],dot.inputs[0]); links.new(unit.outputs['Vector'],dot.inputs[1]); links.new(pos.outputs['Position'],sep.inputs[0]); links.new(dot.outputs['Value'],comb.inputs['X']); links.new(sep.outputs['Z'],comb.inputs['Y']); links.new(comb.outputs['Vector'],brick.inputs['Vector'])
# Slightly more restrained bump avoids the vertical fluting caused by the previous unaligned projection.
bump=next((n for n in nodes if n.type=='BUMP'),None)
if bump:
 bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.0025
scene=bpy.context.scene
scene.render.filepath=os.path.join(OUT,'materials_science_and_electrical_engineering_msee_revision5_preview.png')
scene.render.engine='CYCLES'; scene.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print('R5 wall course projection updated; source saved, collection object count:',len(bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee'].all_objects))
