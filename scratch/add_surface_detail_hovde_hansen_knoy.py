import bpy, os
ROOT=os.path.abspath('.')
BLENDER=bpy.app.version_string
# Existing opaque surfaces only. Use object-space noise so variation stays in meter-scale detail.
TARGETS={
 'modular/buildings/hovde_hall.blend': {
  'Bedford_Indiana_Limestone': (2.2,0.025,0.018),
  'Campus_Teak_Wood_Bench': (3.0,0.035,0.025),
  'Hovde_Executive_Walnut': (3.2,0.03,0.018),
  'Hovde_Granite_Steps': (5.0,0.045,0.022),
  'Hovde_Plaster_Ivory': (3.5,0.018,0.012),
  'Hovde_Roof_Membrane': (8.0,0.05,0.03),
 },
 'modular/buildings/hansen_life_sciences.blend': {
  'Architectural_Precast_Concrete': (4.0,0.025,0.018),
  'Asphalt_Driveway': (12.0,0.045,0.02),
  'Campus_Turf': (24.0,0.07,0.025),
  'Concrete_Pavement': (8.0,0.035,0.02),
  'Roof_Membrane_Gravel': (14.0,0.06,0.035),
  'Structural_Concrete_Slab': (5.0,0.028,0.018),
 },
 'modular/buildings/knoy_hall.blend': {
  'KNOY_Ground_Painted_Partitions': (3.0,0.025,0.018),
  'KNOY_Plaza_Concrete': (8.0,0.035,0.02),
  'KNOY_Precast_Concrete': (4.0,0.028,0.018),
  'KNOY_Roof_Gravel_Membrane': (14.0,0.06,0.035),
 }
}
for rel, mats in TARGETS.items():
 path=os.path.join(ROOT,rel); bpy.ops.wm.open_mainfile(filepath=path)
 changed=[]
 for name,(scale,bump_strength,bump_distance) in mats.items():
  m=bpy.data.materials.get(name)
  if not m or not m.use_nodes: raise RuntimeError(f'Missing material {name} in {rel}')
  nt=m.node_tree; nodes=nt.nodes; links=nt.links
  bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bs: raise RuntimeError(f'No Principled BSDF in {name}')
  # Preserve authored texture networks; this pass only adds restrained micro-surface response.
  if any(n.get('surface_detail_pass')=='campus_2026_10' for n in nodes): continue
  tex=nodes.new('ShaderNodeTexCoord'); tex.label='Meter-scale surface coordinates'
  noise=nodes.new('ShaderNodeTexNoise'); noise.label='Subtle natural surface variation'; noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=2.0; noise.inputs['Roughness'].default_value=0.68
  bump=nodes.new('ShaderNodeBump'); bump.label='Fine surface relief'; bump.inputs['Strength'].default_value=bump_strength; bump.inputs['Distance'].default_value=bump_distance
  links.new(tex.outputs['Object'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],bump.inputs['Height'])
  # Keep existing normal detail intact by chaining this bump after it when possible.
  old=bs.inputs['Normal'].links[0].from_socket if bs.inputs['Normal'].is_linked else None
  if old:
   chain=nodes.new('ShaderNodeBump'); chain.label='Preserve existing relief'; chain.inputs['Strength'].default_value=0.2; chain.inputs['Distance'].default_value=0.02
   # Existing normal chain is retained as base; new natural relief adds only a small perturbation.
   links.new(old,chain.inputs['Normal']); links.new(noise.outputs['Fac'],chain.inputs['Height']); links.new(chain.outputs['Normal'],bs.inputs['Normal'])
  else: links.new(bump.outputs['Normal'],bs.inputs['Normal'])
  for n in (tex,noise,bump): n['surface_detail_pass']='campus_2026_10'
  m['surface_detail']='Procedural, restrained meter-scale noise and bump; original color and authored base shader preserved.'
  changed.append(name)
 print(rel, 'updated:', ', '.join(changed))
 bpy.ops.wm.save_as_mainfile(filepath=path)
# Reopen all three and verify material nodes and asset collection survive.
for rel,mats in TARGETS.items():
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,rel))
 for name in mats:
  m=bpy.data.materials[name]
  assert any(n.get('surface_detail_pass')=='campus_2026_10' for n in m.node_tree.nodes), (rel,name)
 print('REOPEN VERIFIED',rel, 'asset collection:', any(c.name.startswith('Asset_') for c in bpy.data.collections))
