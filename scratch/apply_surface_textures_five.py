import bpy, os, math
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
OUT=r'C:\Users\Tobin\Documents\Blender\PurdueMap\renders\material_review'
os.makedirs(OUT,exist_ok=True)
FILES=['math_sciences.blend','neil_armstrong_hall.blend','owen_hall.blend','purdue_memorial_union.blend','ross_ade.blend']

def is_connected(tree,node,socket_name):
 return any(l.to_node==node and l.to_socket.name==socket_name for l in tree.links)
def add_surface_finish(m,kind):
 if not m.use_nodes: m.use_nodes=True
 nt=m.node_tree; nodes=nt.nodes; links=nt.links
 p=nodes.get('Principled BSDF')
 if not p: return 'no principled'
 if any(n.get('codex_surface_finish') for n in nodes): return 'already textured'
 # Use the object's local XYZ at physical meter scale.
 tc=nodes.new('ShaderNodeTexCoord'); tc.name='Surface Detail Coordinates'; tc.label='Object space • meters'; tc.location=(-700,80)
 noise=nodes.new('ShaderNodeTexNoise'); noise.name='Subtle Surface Variation'; noise.label='Meter-scale material variation'; noise.location=(-470,80)
 noise.inputs['Scale'].default_value={'stone':4.5,'concrete':7.0,'roof':8.0,'metal':16.0,'glass':12.0,'paver':12.0,'floor':24.0}.get(kind,6.0)
 noise.inputs['Detail'].default_value=2.0; noise.inputs['Roughness'].default_value=0.55
 links.new(tc.outputs['Object'],noise.inputs['Vector'])
 # Low contrast mineral/coating color variation around each material's authored base tone.
 base=tuple(p.inputs['Base Color'].default_value)
 mul={'stone':0.045,'concrete':0.035,'roof':0.05,'metal':0.018,'glass':0.012,'paver':0.065,'floor':0.04}.get(kind,0.03)
 ramp=nodes.new('ShaderNodeValToRGB'); ramp.name='Subtle Finish Color'; ramp.label='Preserves base material tone'; ramp.location=(-210,180)
 ramp.color_ramp.elements[0].position=0.18; ramp.color_ramp.elements[1].position=0.82
 dark=tuple(max(0.0,min(1.0,c*(1.0-mul))) for c in base[:3])+(base[3],)
 light=tuple(max(0.0,min(1.0,c*(1.0+mul))) for c in base[:3])+(base[3],)
 ramp.color_ramp.elements[0].color=dark; ramp.color_ramp.elements[1].color=light
 links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
 links.new(ramp.outputs['Color'],p.inputs['Base Color'])
 # Small roughness drift helps large surfaces catch light without looking wet or noisy.
 orig=float(p.inputs['Roughness'].default_value)
 rg=nodes.new('ShaderNodeMapRange'); rg.name='Finish Roughness Drift'; rg.label='Subtle roughness variation'; rg.location=(-200,-80)
 spread={'stone':0.035,'concrete':0.025,'roof':0.03,'metal':0.025,'glass':0.012,'paver':0.025,'floor':0.025}.get(kind,0.025)
 rg.inputs['From Min'].default_value=0.0; rg.inputs['From Max'].default_value=1.0
 rg.inputs['To Min'].default_value=max(0.02,orig-spread); rg.inputs['To Max'].default_value=min(1.0,orig+spread)
 links.new(noise.outputs['Fac'],rg.inputs['Value']); links.new(rg.outputs['Result'],p.inputs['Roughness'])
 # Relief only for matte materials. Polished glazing and metals remain smooth.
 if kind in {'stone','concrete','roof','paver','floor'}:
  bump=nodes.new('ShaderNodeBump'); bump.name='Fine Surface Relief'; bump.label='Subtle physical grain'; bump.location=(-10,-260)
  bump.inputs['Strength'].default_value={'stone':0.12,'concrete':0.08,'roof':0.07,'paver':0.08,'floor':0.05}[kind]
  bump.inputs['Distance'].default_value={'stone':0.00055,'concrete':0.0003,'roof':0.00035,'paver':0.00025,'floor':0.00012}[kind]
  links.new(noise.outputs['Fac'],bump.inputs['Height'])
  if is_connected(nt,p,'Normal'):
   # Don't disturb a pre-existing normal network.
   nodes.remove(bump)
  else:
   links.new(bump.outputs['Normal'],p.inputs['Normal'])
 for n in [tc,noise,ramp,rg]: n['codex_surface_finish']=True
 return f'added {kind}'

def tune_existing(m):
 nt=m.node_tree
 if not nt: return None
 changed=False
 # Existing brick chains have the right visual structure but excessive relief; keep color and tile design.
 for n in nt.nodes:
  if n.type=='BUMP':
   if n.name=='Bump' and any(l.to_node==n and l.from_node.type=='TEX_BRICK' for l in nt.links) and n.inputs.get('Distance') and n.inputs['Distance'].default_value>0.001:
    n.inputs['Distance'].default_value=0.0025; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.28); changed=True
   elif n.name=='Bump.001' and n.inputs.get('Distance') and n.inputs['Distance'].default_value>0.0008:
    n.inputs['Distance'].default_value=0.00045; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.14); changed=True
   elif m.name=='MATH_2026_Roof_Membrane':
    n.inputs['Strength'].default_value=0.045; n.inputs['Distance'].default_value=0.00035; changed=True
  if n.type=='TEX_NOISE' and m.name=='MATH_2026_Roof_Membrane':
   if not any(l.to_node==n and l.to_socket.name=='Vector' for l in nt.links):
    tc=nt.nodes.get('Surface Detail Coordinates') or nt.nodes.new('ShaderNodeTexCoord'); tc.name='Surface Detail Coordinates'; tc.label='Object space • meters'; tc.location=(-500,40)
    nt.links.new(tc.outputs['Object'],n.inputs['Vector']); changed=True
  if n.type=='TEX_NOISE' and m.name=='MATH_2026_Library_Carpet':
   if not any(l.to_node==n and l.to_socket.name=='Vector' for l in nt.links):
    tc=nt.nodes.get('Surface Detail Coordinates') or nt.nodes.new('ShaderNodeTexCoord'); tc.name='Surface Detail Coordinates'; tc.label='Object space • meters'; tc.location=(-500,40)
    nt.links.new(tc.outputs['Object'],n.inputs['Vector']); changed=True
 # Existing brick networks use object-space mapping; retain their color and tile chains.
 return changed

def classify(name):
 s=name.lower()
 if any(k in s for k in ['brick','masonry']): return 'brick'
 if any(k in s for k in ['limestone','granite','stone']): return 'stone'
 if any(k in s for k in ['concrete','precast','boardform']): return 'concrete'
 if any(k in s for k in ['roof','membrane','gravel','slate']): return 'roof'
 if any(k in s for k in ['glass','glazing']): return 'glass'
 if any(k in s for k in ['metal','steel','aluminum','bronze']): return 'metal'
 if any(k in s for k in ['paver','terrazzo','parquet']): return 'floor' if 'terrazzo' in s or 'parquet' in s else 'paver'
 return None
for fn in FILES:
 path=os.path.join(ROOT,fn); bpy.ops.wm.open_mainfile(filepath=path)
 print('\n==',fn)
 bpy.context.preferences.filepaths.save_version=0
 edits=[]
 for m in bpy.data.materials:
  if not m.use_nodes or not m.node_tree.nodes.get('Principled BSDF'): continue
  kind=classify(m.name)
  if not kind: continue
  if kind=='brick':
   if tune_existing(m): edits.append(m.name+': toned brick relief')
   continue
  result=add_surface_finish(m,kind)
  if result.startswith('added'): edits.append(m.name+': '+result)
  elif result not in ('already textured',): print(m.name,result)
 print('materials changed:',len(edits)); [print(' ',e) for e in edits]
 bpy.ops.wm.save_as_mainfile(filepath=path)
 # Render separate neutral QA view after saving, so the source render settings remain untouched.
 scene=bpy.context.scene
 deps=bpy.context.evaluated_depsgraph_get()
 pts=[]
 for o in bpy.data.objects:
  if o.type=='MESH':
   try:
    pts.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
   except: pass
 if not pts: continue
 mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
 center=(mn+mx)*0.5; dims=mx-mn; span=max(dims.x,dims.y,dims.z); print('bounds',tuple(round(v,2) for v in dims),'center',tuple(round(v,2) for v in center))
 # Hide existing lamps only for neutral review; they return from the untouched saved blend on next open.
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
 camdata=bpy.data.cameras.new('Material QA Camera'); cam=bpy.data.objects.new('Material QA Camera',camdata); scene.collection.objects.link(cam)
 cam.location=center+Vector((span*0.92,-span*1.35,span*0.75)); direction=center-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=span*1.55; scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('Material QA World')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.22,0.27,0.34,1); bg.inputs['Strength'].default_value=0.5
 ld=bpy.data.lights.new('Material QA Sun','SUN'); lo=bpy.data.objects.new('Material QA Sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(24),math.radians(-18),math.radians(-35)); ld.energy=2.2; ld.angle=math.radians(12)
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1050; scene.render.resolution_y=760; scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,fn.replace('.blend','_after.png'))
 scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
 bpy.ops.render.render(write_still=True)


