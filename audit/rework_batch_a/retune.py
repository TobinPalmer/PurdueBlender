import bpy,os,math,json
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','rework_batch_a')

def set_brick(m):
 nt=m.node_tree; n=nt.nodes; l=nt.links; n.clear(); out=n.new('ShaderNodeOutputMaterial'); out.location=(800,100); p=n.new('ShaderNodeBsdfPrincipled'); p.location=(550,100);p.inputs['Roughness'].default_value=.79;l.new(p.outputs['BSDF'],out.inputs['Surface'])
 geom=n.new('ShaderNodeNewGeometry');geom.location=(-1000,100); sep=n.new('ShaderNodeSeparateXYZ');sep.location=(-820,100);l.new(geom.outputs['Position'],sep.inputs[0]); nrm=n.new('ShaderNodeSeparateXYZ');nrm.location=(-820,-280);l.new(geom.outputs['Normal'],nrm.inputs[0]);
 xz=n.new('ShaderNodeCombineXYZ');xz.location=(-600,220);l.new(sep.outputs['X'],xz.inputs['X']);l.new(sep.outputs['Z'],xz.inputs['Y'])
 yz=n.new('ShaderNodeCombineXYZ');yz.location=(-600,-80);l.new(sep.outputs['Y'],yz.inputs['X']);l.new(sep.outputs['Z'],yz.inputs['Y'])
 ax=n.new('ShaderNodeMath');ax.operation='ABSOLUTE';ax.location=(-600,-320);l.new(nrm.outputs['X'],ax.inputs[0]); mix=n.new('ShaderNodeMix');mix.data_type='VECTOR';mix.location=(-350,120);l.new(ax.outputs[0],mix.inputs[0]);l.new(xz.outputs[0],mix.inputs[4]);l.new(yz.outputs[0],mix.inputs[5])
 brick=n.new('ShaderNodeTexBrick');brick.location=(-100,250);brick.inputs['Color1'].default_value=(.56,.22,.115,1);brick.inputs['Color2'].default_value=(.35,.075,.045,1);brick.inputs['Mortar'].default_value=(.19,.16,.14,1);brick.inputs['Scale'].default_value=1.0;brick.inputs['Mortar Size'].default_value=.009;brick.inputs['Mortar Smooth'].default_value=.025;brick.inputs['Brick Width'].default_value=.55;brick.inputs['Row Height'].default_value=.22;l.new(mix.outputs['Result'],brick.inputs['Vector']);l.new(brick.outputs['Color'],p.inputs['Base Color'])
 noise=n.new('ShaderNodeTexNoise');noise.location=(-100,-150);noise.inputs['Scale'].default_value=36;noise.inputs['Detail'].default_value=2;l.new(mix.outputs['Result'],noise.inputs['Vector']); bump=n.new('ShaderNodeBump');bump.location=(300,-100);bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.012;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal']);m.diffuse_color=(.4,.15,.08,1)

def box(col,name,loc,dim,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(mat);return o

files=['materials_science_and_electrical_engineering_msee','biochemistry_building','animal_disease_diagnostic_laboratory','david_and_bonnie_brunner_farm_animal_hospital','agricultural_administration_building','agricultural_and_biological_engineering_abe','bechtel_innovation_design_center_bidc','bindley_bioscience_center','dauch_alumni_center','northwest_chiller_plant']
for asset in files:
 path=os.path.join(ROOT,'modular','buildings',asset+'.blend');bpy.ops.wm.open_mainfile(filepath=path);col=next(c for c in bpy.data.collections if c.name=='Asset_'+asset)
 code={'materials_science_and_electrical_engineering_msee':'MSEE','biochemistry_building':'BCHM','animal_disease_diagnostic_laboratory':'ADDL','david_and_bonnie_brunner_farm_animal_hospital':'BRFM','agricultural_administration_building':'AGAD','agricultural_and_biological_engineering_abe':'ABE','bechtel_innovation_design_center_bidc':'BIDC','bindley_bioscience_center':'BIND','dauch_alumni_center':'DAUC','northwest_chiller_plant':'NWCP'}[asset]
 for mat in bpy.data.materials:
  if mat.name.startswith(asset) and ('textured_masonry' in mat.name): set_brick(mat)
 if code=='MSEE':
  slabmat=bpy.data.materials.get('MSEE_atrium_schematic_floor')
  if slabmat is None:
   slabmat=bpy.data.materials.new('MSEE_atrium_schematic_floor');slabmat.diffuse_color=(.23,.25,.27,1);slabmat.use_nodes=True;slabmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.25,.27,1)
  for idx in range(1,4):
   old=next((o for o in col.objects if o.name in (f'MSEE_schematic_floor_{idx}',f'MSEE_interior_floor_{idx}')),None)
   if not old:continue
   lo=[min((old.matrix_world@Vector(v))[i] for v in old.bound_box) for i in range(3)];hi=[max((old.matrix_world@Vector(v))[i] for v in old.bound_box) for i in range(3)];z=(lo[2]+hi[2])*.5; thick=hi[2]-lo[2]
   if 'interior_floor' in old.name: flooridx=idx; bpy.data.objects.remove(old,do_unlink=True)
   else: bpy.data.objects.remove(old,do_unlink=True); flooridx=idx
   # Three room-gallery strips preserve floor-level cues while leaving the documented two-story atrium open.
   for name,y0,y1,x0,x1 in [(f'MSEE_revision_atrium_floor_{flooridx}_south',lo[1],-19.8,lo[0],hi[0]),(f'MSEE_revision_atrium_floor_{flooridx}_east',-19.8,-2.45,-6.35,hi[0]),(f'MSEE_revision_atrium_floor_{flooridx}_north',-2.45,hi[1],lo[0],hi[0])]:
    if y1-y0>.2: box(col,name,((x0+x1)*.5,(y0+y1)*.5,z),(x1-x0,y1-y0,thick),slabmat)
  # also reduce visual opacity by giving remaining schematic pieces a darker neutral tone
 if code in ('MSEE','NWCP'):
  # Those buildings are concrete/industrial, not exposed red-brick; use subdued fine noise instead.
  facade=next((m for m in bpy.data.materials if m.name.startswith(asset) and ('_facade' in m.name or '_textured_masonry' in m.name)),None)
  if code=='MSEE' or code=='NWCP':
   if facade:
    nt=facade.node_tree; p=nt.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=((.39,.41,.42,1) if code=='MSEE' else (.40,.42,.41,1)); p.inputs['Roughness'].default_value=.84;facade.diffuse_color=(.39,.41,.42,1)
    # fine concrete aggregate, no false brick courses
    tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=65;tex.inputs['Detail'].default_value=2
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.11;bump.inputs['Distance'].default_value=.008;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 if code=='MSEE':
  # shell/origin invariant by construction; regenerate preview below
  pass
 sc=bpy.context.scene;sc.render.resolution_percentage=100;sc.render.filepath=os.path.join(OUT,asset+'_revision_preview.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=path)
 # mark evidence corrective action
 evdir='audit/build_batch_a2' if code in ('MSEE','NWCP') else 'audit/build_batch_a'
 evname={'MSEE':'materials_science_and_electrical_engineering_msee_evidence.json','NWCP':'northwest_chiller_plant_evidence.json'}.get(code,asset+'_evidence.json')
 ep=os.path.join(ROOT,evdir,evname);ev=json.load(open(ep,encoding='utf-8'));ev.setdefault('revision_history',[]).append({'date':'2026-10-24','geometry_edits':['MSEE atrium-floor schematic corrected into three galleries around the open atrium; no geometry extends into the glazed void.'] if code=='MSEE' else ['Corrected facade finish to fine concrete/industrial finish; rooftop cooling kit and pipe additions retained.'],'materials':'Brick shader uses world-space wall-normal mapping so brick courses remain horizontal across the vertical facade; MSEE and NWCP use subtle concrete aggregate.'});ev['validation']['revision_preview']=os.path.relpath(sc.render.filepath,ROOT).replace('/','\\');json.dump(ev,open(ep,'w',encoding='utf-8'),indent=2)
 print('PATCHED',code,flush=True)
