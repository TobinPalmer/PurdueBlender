import bpy, os
from mathutils import Vector
root=os.getcwd()
blender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
configs={
 'modular/buildings/hicks_library.blend':{
  'Mat_HIKS_Indiana_Limestone':(34,.045,.22,.035), 'Mat_HIKS_Purdue_Red_Brick':(48,.035,.2,.045),
  'Mat_HIKS_Plaza_Paver_Concrete':(76,.025,.16,.03), 'Mat_HIKS_Roof_Gravel_Ballast':(110,.018,.3,.04),
  'Mat_HIKS_Subterranean_Concrete':(65,.025,.16,.025), 'Mat_HIKS_Interior_Terrazzo':(58,.018,.18,.035),
  'Mat_HIKS_Site_Lawn':(24,.04,.22,.05)},
 'modular/buildings/lawson_hall.blend':{
  'LWSN_Bedford_Limestone':(34,.045,.22,.035), 'LWSN_Purdue_Red_Brick':(48,.035,.2,.045),
  'LWSN_Plaza_Pavers':(76,.025,.16,.03), 'LWSN_Roof_Gravel':(110,.018,.3,.04), 'LWSN_Site_Lawn':(24,.04,.22,.05),
  'LWSN_Interior_Painted_Plaster':(28,.012,.12,.025), 'LWSN_Terrazzo_Floor':(58,.018,.18,.035)},
 'modular/buildings/krannert_building.blend':{
  'KRAN_Indiana_Limestone':(34,.045,.22,.035), 'Purdue_Red_Brick':(48,.035,.2,.045), 'KRAN_Plaza_Paving':(76,.025,.16,.03),
  'KRAN_Roof_Membrane':(110,.018,.3,.04), 'KRAN_Concrete_Slab':(65,.025,.16,.025), 'KRAN_Dark_Base_Granite':(58,.035,.2,.035)} }
for path,mats in configs.items():
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,path))
 touched=[]
 for name,(scale,bump_distance,bump_strength,color_amt) in mats.items():
  mat=bpy.data.materials.get(name)
  if not mat or not mat.use_nodes: continue
  nt=mat.node_tree; bsdf=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bsdf: continue
  # do not stack texture on a previously authored texture network
  if any(n.get('purdue_surface_detail') for n in nt.nodes): continue
  tex=nt.nodes.new('ShaderNodeTexCoord'); tex.label='Object-space surface coordinates'
  noise=nt.nodes.new('ShaderNodeTexNoise'); noise.label='Subtle material-scale variation'; noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=2.0; noise.inputs['Roughness'].default_value=.62
  nt.links.new(tex.outputs['Generated'],noise.inputs['Vector'])
  bump=nt.nodes.new('ShaderNodeBump'); bump.label='Fine surface relief'; bump.inputs['Strength'].default_value=bump_strength; bump.inputs['Distance'].default_value=bump_distance
  nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
  # preserve existing normal chain if present; use output normal of bump and preserve bump's own base if prior normal exists
  old=bsdf.inputs['Normal'].links[0].from_socket if bsdf.inputs['Normal'].is_linked else None
  if old: nt.links.new(old,bump.inputs['Normal'])
  nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
  # subtle albedo mottling, constrained around original base color
  color_input=bsdf.inputs['Base Color']
  base=tuple(color_input.default_value)
  ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.label='Restrained tonal variation'
  a=list(base); b=list(base)
  for i in range(3): a[i]=max(0,min(1,base[i]*(1-color_amt))); b[i]=max(0,min(1,base[i]*(1+color_amt)))
  ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=tuple(a)
  ramp.color_ramp.elements[1].position=.82; ramp.color_ramp.elements[1].color=tuple(b)
  nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],color_input)
  for n in (tex,noise,bump,ramp): n['purdue_surface_detail']=True
  touched.append(name)
 print('UPDATED',path, touched)
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,path))
