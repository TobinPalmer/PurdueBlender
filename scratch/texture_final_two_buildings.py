import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.')
ASSET=os.path.join(ROOT,'modular','buildings')
OUT=os.path.join(ROOT,'audit','texture_final_two'); os.makedirs(OUT,exist_ok=True)

def principal(m): return next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
def add_finish(m,kind):
 nt=m.node_tree; nodes=nt.nodes; links=nt.links; bs=principal(m)
 if not bs: return 'skip:no principled'
 if any(n.get('texture_final_two') for n in nodes): return 'skip:already handled'
 base=bs.inputs['Base Color']; prior=next((l.from_socket for l in base.links),None); rgba=tuple(base.default_value)
 factors={'stone':(.035,3.8,.00038),'concrete':(.04,6.5,.00025),'roof':(.035,3.2,.0003),'metal':(.018,12,.0001),'plaster':(.025,5,.0002),'terracotta':(.035,4,.0003),'turf':(.075,2.4,.0006),'floor':(.035,10,.00013),'paint':(.02,9,.00008),'wood':(.025,6,.0002)}
 amount,scale,bumpdist=factors[kind]
 coord=nodes.new('ShaderNodeTexCoord'); coord.label='Fine finish • object-space meters'; coord.location=(-850,120)
 noise=nodes.new('ShaderNodeTexNoise'); noise.label=kind.title()+' surface grain'; noise.location=(-640,120); noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=2; noise.inputs['Roughness'].default_value=.56
 links.new(coord.outputs['Object'],noise.inputs['Vector'])
 remap=nodes.new('ShaderNodeMapRange'); remap.label='Low contrast color range'; remap.location=(-420,180); remap.clamp=True
 remap.inputs['From Min'].default_value=.16; remap.inputs['From Max'].default_value=.84; remap.inputs['To Min'].default_value=1-amount; remap.inputs['To Max'].default_value=1+amount
 links.new(noise.outputs['Fac'],remap.inputs['Value'])
 mult=nodes.new('ShaderNodeVectorMath'); mult.operation='SCALE'; mult.label='Preserve authored base color'; mult.location=(-170,180)
 if prior: links.new(prior,mult.inputs[0])
 else: mult.inputs[0].default_value=rgba[:3]
 links.new(remap.outputs['Result'],mult.inputs['Scale'])
 for l in list(base.links): links.remove(l)
 links.new(mult.outputs['Vector'],base)
 rough=bs.inputs['Roughness']
 if not rough.is_linked:
  rg=nodes.new('ShaderNodeMapRange'); rg.label='Subtle roughness drift'; rg.location=(-390,-30); rg.clamp=True
  rg.inputs['From Min'].default_value=.12; rg.inputs['From Max'].default_value=.88
  r0=float(rough.default_value); spread={'metal':.018,'roof':.03,'stone':.035,'concrete':.03,'floor':.025,'turf':.025}.get(kind,.025)
  rg.inputs['To Min'].default_value=max(.02,r0-spread); rg.inputs['To Max'].default_value=min(1,r0+spread)
  links.new(noise.outputs['Fac'],rg.inputs['Value']); links.new(rg.outputs['Result'],rough)
 normal=bs.inputs.get('Normal')
 if normal and not normal.is_linked and kind in {'stone','concrete','roof','plaster','terracotta','turf','floor','wood'}:
  bump=nodes.new('ShaderNodeBump'); bump.label='Subtle physical grain'; bump.location=(-130,-200)
  bump.inputs['Strength'].default_value={'turf':.12,'stone':.09,'concrete':.08,'roof':.06,'plaster':.055,'terracotta':.07,'floor':.05,'wood':.06}[kind]
  bump.inputs['Distance'].default_value=bumpdist
  links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],normal)
 for n in (coord,noise,remap,mult): n['texture_final_two']=True
 m['texture_finish_final_two']=f'{kind}: object-space {scale:.1f}/m subtle grain, hue-preserving color variation; micro relief {bumpdist*1000:.2f} mm where applicable.'
 return 'finished:'+kind

def kind_for(name,building):
 s=name.lower()
 if building=='mccutcheon_hall':
  if 'purdue_red_brick' in s: return None # retain authored brick/grout shader
  if 'limestone' in s: return 'stone'
  if 'roof_membrane' in s: return 'roof'
  if 'concrete' in s or 'pavement' in s or 'plinth' in s: return 'concrete'
  if 'aluminum' in s or 'steel' in s or 'bronze' in s or 'louver' in s or 'mullion' in s: return 'metal'
  if 'enamel_spandrel' in s or 'ribbon_glass' in s: return 'paint'
  if 'planting_green' in s: return 'turf'
 else:
  if 'purdue_red_brick' in s: return None # retain authored brick/grout shader
  if 'limestone' in s or 'foundation_concrete' in s or 'apron_concrete' in s or 'plaza_concrete' in s: return 'stone' if 'limestone' in s else 'concrete'
  if 'roof_membrane' in s or 'standingseam_roof' in s: return 'roof'
  if 'photographic_terracotta' in s: return 'terracotta'
  if 'offwhite_plaster' in s: return 'plaster'
  if 'composite_metal' in s or 'metal' in s or 'louver' in s or 'mullion' in s or 'frame' in s: return 'metal'
  if 'campus_turf' in s: return 'turf'
  if 'terrazzo' in s: return 'floor'
  if 'lecture_desk_laminate' in s: return 'wood'
 return None

def bounds(objects):
 pts=[]
 for o in objects:
  if o.type!='MESH' or o.hide_render: continue
  try: pts.extend(o.matrix_world@Vector(c) for c in o.bound_box)
  except: pass
 if not pts: return None
 mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
 return mn,mx,(mn+mx)*.5,mx-mn

def qa_render(tag, target_objs, filepath, zoom=False):
 scene=bpy.context.scene; b=bounds(target_objs)
 if not b: raise RuntimeError('No bounds '+tag)
 mn,mx,center,dims=b; span=max(dims.x,dims.y,dims.z)
 # Isolated material QA with consistent neutral sky and soft studio daylight.
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
 camdata=bpy.data.cameras.new('QA Camera '+tag); cam=bpy.data.objects.new('QA Camera '+tag,camdata); scene.collection.objects.link(cam)
 if zoom:
  # Frame the roof planes at a steep three-quarter angle, retaining enough fascia for scale.
  center.z=max(center.z,mn.z+dims.z*.76)
  diag=max(dims.x,dims.y,2.0)
  cam.location=center+Vector((diag*.85,-diag*1.1,diag*1.15)); camdata.type='ORTHO'; camdata.ortho_scale=max(dims.x,dims.y)*1.32
 else:
  cam.location=center+Vector((span*1.12,-span*1.55,span*1.12)); camdata.type='ORTHO'; camdata.ortho_scale=span*1.78
 cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('QA World')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.24,.30,.38,1); bg.inputs['Strength'].default_value=.48
 sun_data=bpy.data.lights.new('QA soft sun','SUN'); sun=bpy.data.objects.new('QA soft sun',sun_data); scene.collection.objects.link(sun); sun.rotation_euler=(math.radians(24),math.radians(-18),math.radians(-35)); sun_data.energy=2.0; sun_data.angle=math.radians(15)
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=850; scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'; scene.render.filepath=filepath
 scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=.1; scene.view_settings.gamma=1
 bpy.ops.render.render(write_still=True); print('RENDER',filepath)
 # Remove QA camera/sun in-memory for subsequent next-file open; saved original asset predates both.
 bpy.data.objects.remove(cam,do_unlink=True); bpy.data.cameras.remove(camdata)
 bpy.data.objects.remove(sun,do_unlink=True); bpy.data.lights.remove(sun_data)

for key in ('mccutcheon_hall','niswonger_aviation_tech'):
 path=os.path.join(ASSET,key+'.blend'); bpy.ops.wm.open_mainfile(filepath=path); bpy.context.preferences.filepaths.save_version=0
 edits=[]
 for m in bpy.data.materials:
  if not m.node_tree: continue
  kind=kind_for(m.name,key)
  if kind:
   result=add_finish(m,kind)
   if result.startswith('finished'): edits.append((m.name,result))
 print('\nASSET',key,'materials_finished',len(edits))
 for e in edits: print('EDIT',e[0],e[1])
 bpy.ops.wm.save_as_mainfile(filepath=path); print('SAVED',path)
 all_mesh=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render]
 qa_render(key+' overview',all_mesh,os.path.join(OUT,key+'_overview.png'))
 # focus on roof-related meshes, but also retain broad material textures in view
 roofs=[o for o in all_mesh if any(t in o.name.lower() for t in ('roof','parapet','rtu_unit'))]
 qa_render(key+' roof close',roofs or all_mesh,os.path.join(OUT,key+'_roof_close.png'),True)

