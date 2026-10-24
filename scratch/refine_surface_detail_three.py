import bpy, os
ROOT=os.path.abspath('.')
files=['hovde_hall','hansen_life_sciences','knoy_hall']
for f in files:
 path=os.path.join(ROOT,'modular','buildings',f+'.blend'); bpy.ops.wm.open_mainfile(filepath=path)
 touched=[]
 for m in bpy.data.materials:
  if not m.use_nodes: continue
  nt=m.node_tree; tagged=[n for n in nt.nodes if n.get('surface_detail_pass')=='campus_2026_10']
  if not tagged: continue
  noise=next((n for n in tagged if n.type=='TEX_NOISE'),None)
  tex=next((n for n in tagged if n.type=='TEX_COORD'),None)
  if noise:
   noise.inputs['Scale'].default_value=1.25
   noise.inputs['Detail'].default_value=1.0
   noise.inputs['Roughness'].default_value=0.52
  # Force the assigned pass onto uniform local object-space coordinates.
  if noise and tex:
   for link in list(noise.inputs['Vector'].links): nt.links.remove(link)
   nt.links.new(tex.outputs['Object'],noise.inputs['Vector'])
  # Reduce the added micro-relief to a faint matte variation. Existing color/geometry stays intact.
  for n in tagged:
   if n.type=='BUMP':
    n.inputs['Strength'].default_value=0.018
    n.inputs['Distance'].default_value=0.006
    # Discard empty added bump nodes where an existing authored normal chain is already active.
    if not n.outputs['Normal'].is_linked:
     nt.nodes.remove(n)
  # Lower the added normal-combiner nodes created on top of authored normal maps.
  for n in nt.nodes:
   if n.label=='Preserve existing relief':
    n.inputs['Strength'].default_value=0.025
    n.inputs['Distance'].default_value=0.006
  m['surface_detail']='Subtle object-space meter-scale noise; original base color, texture and geometry preserved.'
  touched.append(m.name)
 print('CORRECTED',f,', '.join(touched))
 bpy.ops.wm.save_as_mainfile(filepath=path)
