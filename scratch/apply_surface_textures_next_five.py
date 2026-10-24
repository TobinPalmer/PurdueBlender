import bpy, os, math
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
OUT=r'C:\Users\Tobin\Documents\Blender\PurdueMap\renders\material_review_next'
os.makedirs(OUT,exist_ok=True)
FILES=['rawls_hall.blend','stanley_coulter_hall.blend','wiley_hall.blend','winifred_parker_hall.blend','benjamin_harrison_hall.blend']

def linked(nt,node,sock): return any(l.to_node==node and l.to_socket.name==sock for l in nt.links)
def has_out(nt,node): return any(l.from_node==node for l in nt.links)
def tune_existing(m,kind):
 nt=m.node_tree
 if not nt: return False
 changed=False; name=m.name.lower()
 brick_like=('brick' in name or ('paver' in name and 'terrazzo' not in name))
 for n in nt.nodes:
  if n.type=='BUMP':
   # Keep existing tile/aggregate nodes and color chain; reduce overscaled physical relief.
   if brick_like and any(l.to_node==n and l.from_node.type=='TEX_BRICK' for l in nt.links):
    if n.inputs['Distance'].default_value>0.0018:
     n.inputs['Distance'].default_value=0.0025; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.28); changed=True
   elif brick_like and n.name=='Bump.001' and n.inputs['Distance'].default_value>0.0008:
    n.inputs['Distance'].default_value=0.00045; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.14); changed=True
   elif kind=='stone' and n.inputs['Distance'].default_value>0.002:
    n.inputs['Distance'].default_value=0.0012; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.045); changed=True
   elif kind=='roof' and n.inputs['Distance'].default_value>0.003:
    n.inputs['Distance'].default_value=0.0015; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.07); changed=True
   elif kind=='concrete' and n.inputs['Distance'].default_value>0.002:
    n.inputs['Distance'].default_value=0.001; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.08); changed=True
   elif kind=='floor' and n.inputs['Distance'].default_value>0.002:
    n.inputs['Distance'].default_value=0.0008; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.08); changed=True
   elif kind=='grass' and n.inputs['Distance'].default_value>0.02:
    n.inputs['Distance'].default_value=0.01; n.inputs['Strength'].default_value=min(n.inputs['Strength'].default_value,0.12); changed=True
 return changed

def add_finish(m,kind):
 nt=m.node_tree; nodes=nt.nodes; links=nt.links; p=nodes.get('Principled BSDF')
 if not p or any(n.get('codex_surface_finish') for n in nodes): return False
 tc=nodes.new('ShaderNodeTexCoord'); tc.name='Surface Detail Coordinates'; tc.label='Object space • meter scale'; tc.location=(-720,60)
 noise=nodes.new('ShaderNodeTexNoise'); noise.name='Surface Finish Variation'; noise.label='Subtle meter-scale finish'; noise.location=(-490,60)
 noise.inputs['Scale'].default_value={'stone':4.5,'concrete':7.0,'roof':8.0,'metal':16.0,'glass':12.0,'floor':18.0,'grass':2.2,'panel':8.0}.get(kind,6.0)
 noise.inputs['Detail'].default_value=2.0; noise.inputs['Roughness'].default_value=0.55
 links.new(tc.outputs['Object'],noise.inputs['Vector'])
 created=[tc,noise]
 if not linked(nt,p,'Base Color'):
  base=tuple(p.inputs['Base Color'].default_value); variation={'stone':0.04,'concrete':0.035,'roof':0.05,'metal':0.018,'glass':0.012,'floor':0.045,'grass':0.045,'panel':0.025}.get(kind,0.03)
  ramp=nodes.new('ShaderNodeValToRGB'); ramp.name='Subtle Finish Color'; ramp.label='Preserves authored base tone'; ramp.location=(-250,160)
  ramp.color_ramp.elements[0].position=0.18; ramp.color_ramp.elements[1].position=0.82
  ramp.color_ramp.elements[0].color=tuple(c*(1-variation) for c in base[:3])+(base[3],)
  ramp.color_ramp.elements[1].color=tuple(min(1.0,c*(1+variation)) for c in base[:3])+(base[3],)
  links.new(noise.outputs['Fac'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],p.inputs['Base Color']); created.append(ramp)
 if not linked(nt,p,'Roughness'):
  orig=float(p.inputs['Roughness'].default_value); spread={'stone':0.03,'concrete':0.025,'roof':0.03,'metal':0.025,'glass':0.012,'floor':0.025,'grass':0.035,'panel':0.02}.get(kind,0.025)
  rg=nodes.new('ShaderNodeMapRange'); rg.name='Finish Roughness Variation'; rg.label='Subtle roughness drift'; rg.location=(-245,-80)
  rg.inputs['From Min'].default_value=0; rg.inputs['From Max'].default_value=1; rg.inputs['To Min'].default_value=max(0.02,orig-spread); rg.inputs['To Max'].default_value=min(1,orig+spread)
  links.new(noise.outputs['Fac'],rg.inputs['Value']); links.new(rg.outputs['Result'],p.inputs['Roughness']); created.append(rg)
 if kind in {'stone','concrete','roof','floor','grass'} and not linked(nt,p,'Normal'):
  bump=nodes.new('ShaderNodeBump'); bump.name='Subtle Finish Relief'; bump.label='Fine surface grain'; bump.location=(-20,-240)
  bump.inputs['Strength'].default_value={'stone':0.08,'concrete':0.07,'roof':0.06,'floor':0.045,'grass':0.08}[kind]
  bump.inputs['Distance'].default_value={'stone':0.00055,'concrete':0.00035,'roof':0.00045,'floor':0.0002,'grass':0.0015}[kind]
  links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal']); created.append(bump)
 for n in created: n['codex_surface_finish']=True
 return True

def classify(name):
 s=name.lower()
 if 'brick' in s: return 'brick'
 if any(k in s for k in ['limestone','granite','stone']): return 'stone'
 if any(k in s for k in ['concrete','asphalt','pavement','walkway','walk |','paving']): return 'concrete'
 if any(k in s for k in ['roof','membrane','gravel','slate']): return 'roof'
 if any(k in s for k in ['glass','glazing']): return 'glass'
 if any(k in s for k in ['metal','steel','aluminum','bronze','copper','mullion','louver']): return 'metal'
 if any(k in s for k in ['terrazzo','paver','parquet','granite paver']): return 'floor'
 if any(k in s for k in ['lawn','grass','turf']): return 'grass'
 if any(k in s for k in ['enamel','spandrel','wall ivory','plaster']): return 'panel'
 return None

for fn in FILES:
 path=os.path.join(ROOT,fn); bpy.ops.wm.open_mainfile(filepath=path); bpy.context.preferences.filepaths.save_version=0
 edits=[]
 for m in bpy.data.materials:
  if not m.use_nodes or not m.node_tree.nodes.get('Principled BSDF'): continue
  kind=classify(m.name)
  if not kind: continue
  if kind=='brick' or ('paver' in m.name.lower() and any(n.type=='TEX_BRICK' for n in m.node_tree.nodes)):
   if tune_existing(m,'brick'): edits.append(m.name+': reduced tile relief')
   continue
  tuned=tune_existing(m,kind)
  added=add_finish(m,kind)
  if tuned or added: edits.append(m.name+': '+('tuned existing relief; ' if tuned else '')+('added subtle finish detail' if added else 'preserved existing finish'))
 print('\n',fn,'changes',len(edits)); [print(' ',x) for x in edits]
 bpy.ops.wm.save_as_mainfile(filepath=path)
 # Neutral QA render with a temporary camera/light, not saved to the source asset.
 scene=bpy.context.scene; pts=[]
 for o in bpy.data.objects:
  if o.type=='MESH':
   try: pts.extend(o.matrix_world@Vector(c) for c in o.bound_box)
   except: pass
 if not pts: continue
 mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts))); center=(mn+mx)*0.5; dims=mx-mn; span=max(dims)
 print('bounds m',tuple(round(v,2) for v in dims))
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
 camd=bpy.data.cameras.new('Material QA Camera'); cam=bpy.data.objects.new('Material QA Camera',camd); scene.collection.objects.link(cam); cam.location=center+Vector((span*0.92,-span*1.35,span*0.75)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=span*1.55; scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('Material QA World')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.22,0.27,0.34,1); bg.inputs['Strength'].default_value=0.5
 ld=bpy.data.lights.new('Material QA Sun','SUN'); lo=bpy.data.objects.new('Material QA Sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(24),math.radians(-18),math.radians(-35)); ld.energy=2.2; ld.angle=math.radians(12)
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1000; scene.render.resolution_y=720; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,fn.replace('.blend','_after.png')); scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
 bpy.ops.render.render(write_still=True)
