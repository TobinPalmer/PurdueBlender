import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
facade=bpy.data.collections['AQUA_Facade']; structure=bpy.data.collections['AQUA_Structure']; interior=bpy.data.collections['AQUA_Interior']; rig=bpy.data.collections['Preview_Rig']
wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope']

def mat(n): return bpy.data.materials[n]
brick=mat('AQUA | mottled Purdue red-brown brick'); concrete=mat('AQUA | cast concrete'); metal=mat('AQUA | charcoal anodized metal'); stone=mat('AQUA | warm gray limestone / precast'); dark=mat('AQUA | deep shadow / reveals'); gold=mat('AQUA | Purdue gold anodized metal'); glass=mat('AQUA R1 | blue-gray reflective ribbon glazing'); roofmat=mat('AQUA | weathered membrane / standing seam')
# More tactile, restrained surface response without external image files.
def add_noise_bump(material, scale, detail, strength, distance):
 material.use_nodes=True; nt=material.node_tree; nodes=nt.nodes; links=nt.links
 bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=detail; noise.inputs['Roughness'].default_value=.72
 bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=strength; bump.inputs['Distance'].default_value=distance
 links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 return bs,noise
bs,noise=add_noise_bump(brick,5.2,3.0,.16,.035)
bs.inputs['Base Color'].default_value=(.36,.105,.055,1); bs.inputs['Roughness'].default_value=.82
ramp=brick.node_tree.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=(.19,.045,.025,1); ramp.color_ramp.elements[1].position=.78; ramp.color_ramp.elements[1].color=(.48,.16,.085,1)
brick.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); brick.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
bs2,_=add_noise_bump(concrete,8.0,2.0,.08,.012); bs2.inputs['Base Color'].default_value=(.37,.38,.36,1); bs2.inputs['Roughness'].default_value=.82
bs3,_=add_noise_bump(roofmat,16.0,2.0,.12,.009); bs3.inputs['Base Color'].default_value=(.16,.18,.18,1); bs3.inputs['Metallic'].default_value=.45; bs3.inputs['Roughness'].default_value=.42
bs4,_=add_noise_bump(glass,3.0,1.5,.025,.003); bs4.inputs['Base Color'].default_value=(.08,.19,.24,1); bs4.inputs['Metallic'].default_value=.38; bs4.inputs['Roughness'].default_value=.2
if 'Coat Weight' in bs4.inputs: bs4.inputs['Coat Weight'].default_value=.35
# Raised joints and a restrained north elevation bay rhythm. Photograph confirms brick wall, lower ribbon windows, central entry; side/rear repetition is marked as extrapolated.
def cube(name,loc,size,material,collection=facade):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection): c.objects.unlink(o)
 collection.objects.link(o); o.data.materials.clear(); o.data.materials.append(material); return o
# north elevation (y positive): pier rhythm, base course, upper lintel band, and window frame depth.
for i,x in enumerate([-27,-20.25,-13.5,-6.75,6.75,13.5,20.25,27]):
 cube(f'AQUA R2 | north brick pilaster {i+1}',(x,51.34,4.45),(.32,.22,8.05),brick)
# North wall courses with intentional shadow lines; these are architectural detailing, not dimension survey.
cube('AQUA R2 | north concrete water table',(0,51.34,.46),(59.9,.26,.34),concrete)
cube('AQUA R2 | north upper brick belt course',(0,51.34,8.75),(59.9,.20,.30),stone)
cube('AQUA R2 | north roof eave fascia',(0,51.34,9.15),(60.1,.28,.22),metal)
# Add thin mullion/reveal frames around all existing ribbon panes; each pane retains inherited footprint alignment.
windows=[o for o in list(asset.all_objects) if o.type=='MESH' and o.name.startswith('AQUA | facade bay') and o.name.endswith('glazing')]
frame_count=0
for i,o in enumerate(windows):
 b=[o.matrix_world@Vector(c) for c in o.bound_box]
 x0,x1=min(v.x for v in b),max(v.x for v in b); y0,y1=min(v.y for v in b),max(v.y for v in b); z0,z1=min(v.z for v in b),max(v.z for v in b)
 if y1-y0 > x1-x0: # north/south wall window: horizontal span is x
  yc=(y0+y1)/2 + (0.12 if (y0+y1)/2>0 else -0.12); depth=.08
  cube(f'AQUA R2 | ribbon jamb {i+1}a',(x0-.055,yc,(z0+z1)/2),(.09,depth,z1-z0+.20),metal); cube(f'AQUA R2 | ribbon jamb {i+1}b',(x1+.055,yc,(z0+z1)/2),(.09,depth,z1-z0+.20),metal)
  cube(f'AQUA R2 | ribbon head {i+1}',((x0+x1)/2,yc,z1+.055),(x1-x0+.20,depth,.09),stone); cube(f'AQUA R2 | ribbon sill {i+1}',((x0+x1)/2,yc,z0-.055),(x1-x0+.20,depth,.09),stone)
 else: # east/west wall: horizontal span is y
  xc=(x0+x1)/2 + (0.12 if (x0+x1)/2>0 else -0.12); depth=.08
  cube(f'AQUA R2 | ribbon jamb {i+1}a',(xc,y0-.055,(z0+z1)/2),(depth,.09,z1-z0+.20),metal); cube(f'AQUA R2 | ribbon jamb {i+1}b',(xc,y1+.055,(z0+z1)/2),(depth,.09,z1-z0+.20),metal)
  cube(f'AQUA R2 | ribbon head {i+1}',(xc,(y0+y1)/2,z1+.055),(depth,y1-y0+.20,.09),stone); cube(f'AQUA R2 | ribbon sill {i+1}',(xc,(y0+y1)/2,z0-.055),(depth,y1-y0+.20,.09),stone)
 frame_count+=4
# Resize sign to a legible plaque with gold lettering; photo confirms centered name above entry, not exact dimensions.
text=bpy.data.objects['AQUA R1 | north facade building name']; text.data.size=.58; text.data.extrude=.018; text.location=(0,51.53,6.15); text.data.materials.clear(); text.data.materials.append(gold)
try: text.data.font=bpy.data.fonts.load(r'C:\Windows\Fonts\arialbd.ttf')
except Exception: pass
plaque=cube('AQUA R2 | north entrance dark sign plaque',(0,51.39,6.15),(24.0,.12,1.45),dark)
plaque['evidence_note']='Readable backing scale is a presentation improvement; lettering location supported by Street View, exact plaque dimensions estimated.'
# Roof form stays a shallow gable due unresolved section; add building-scale cap/eaves and seams, not a new unsupported roof profile.
cube('AQUA R2 | continuous roof ridge cap',(0,0,12.28),(.75,99.5,.22),metal,structure)
for side in (-1,1):
 x=side*28.85
 # gutter tube following the long gable eave.
 curve=bpy.data.curves.new(f'AQUA R2 | eaves gutter curve {side}','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.085; curve.bevel_resolution=3
 spl=curve.splines.new('POLY'); spl.points.add(1); spl.points[0].co=(x,-49.4,9.08,1); spl.points[1].co=(x,49.4,9.08,1)
 ob=bpy.data.objects.new(f'AQUA R2 | continuous eaves gutter {side}',curve); structure.objects.link(ob); ob.data.materials.append(metal)
# Rework the inherited schematic stand into visibly individual spectator seating rows and an upper mezzanine viewing edge.
for o in list(asset.all_objects):
 if o.name.startswith('AQUA | schematic spectator bleacher tier') or o.name.startswith('AQUA | schematic spectator seat accent'):
  bpy.data.objects.remove(o,do_unlink=True)
# East long-side stand. 12 rows of 25 visible seat blocks = 300 representative seats; official total is 625, exact arrangement unknown.
seatmat=gold
seatverts=[]; seatfaces=[]
def append_box(x0,y0,z0,dx,dy,dz):
 b=len(seatverts); seatverts.extend([(x0,y0,z0),(x0+dx,y0,z0),(x0+dx,y0+dy,z0),(x0,y0+dy,z0),(x0,y0,z0+dz),(x0+dx,y0,z0+dz),(x0+dx,y0+dy,z0+dz),(x0,y0+dy,z0+dz)])
 seatfaces.extend([(b,b+1,b+2,b+3),(b+4,b+7,b+6,b+5),(b,b+4,b+5,b+1),(b+1,b+5,b+6,b+2),(b+2,b+6,b+7,b+3),(b+3,b+7,b+4,b)])
for row in range(12):
 x=15.6+row*.68; z=.5+row*.28
 # stepped concrete support
 cube(f'AQUA R2 | east grandstand step {row+1}',(x+.28,0,z+.12),(.56,42.0,.24),concrete,interior)
 for seat in range(25):
  y=-20.0+seat*1.65
  # separate compact seat shell with backrest
  append_box(x-.05,y-.20,z+.27,.42,.40,.14)
  append_box(x+.30,y-.20,z+.39,.12,.40,.44)
# Single joined mesh for compact repeated seats, efficient for asset import.
me=bpy.data.meshes.new('AQUA R2 | repeated individual spectator seat geometry'); me.from_pydata(seatverts,[],seatfaces); me.materials.append(seatmat); seats=bpy.data.objects.new('AQUA R2 | 300 individual schematic spectator seats',me); interior.objects.link(seats); seats['documented_capacity']=625; seats['modeled_count']=300; seats['layout_status']='Representative seat bank only; exact plan and full capacity distribution are not sourced.'
# Mezzanine edge and access stairs are schematic in location; the existence is documented by Purdue RecWell.
cube('AQUA R2 | schematic east mezzanine gallery',(24.15,0,4.75),(1.6,42.0,.22),stone,interior)
for y in (-21.0,21.0): cube('AQUA R2 | mezzanine guardrail post',(24.15,y,5.28),(.12,.12,1.0),metal,interior)
cube('AQUA R2 | mezzanine continuous guardrail',(24.15,0,5.78),(.10,42,.10),metal,interior)
# Access stair flights at both ends: repeated treads and two handrails.
for ybase in (-17.0,17.0):
 for step in range(12): cube(f'AQUA R2 | schematic mezzanine stair tread {ybase}_{step}',(23.0-step*.23,ybase+step*.24,1.0+step*.31),(.9,.30,.10),concrete,interior)
 for side in (-1,1):
  curve=bpy.data.curves.new(f'AQUA R2 | mezzanine stair rail curve {ybase}_{side}','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.035; curve.bevel_resolution=2; sp=curve.splines.new('POLY'); sp.points.add(1); sp.points[0].co=(22.0,ybase+side*.48,.9,1); sp.points[1].co=(19.4,ybase+2.9,4.7,1); ob=bpy.data.objects.new(f'AQUA R2 | mezzanine stair handrail {ybase}_{side}',curve); interior.objects.link(ob); ob.data.materials.append(metal)
# Lighter, clearer daylight and indoor pool illumination; preview equipment remains outside exported asset collection.
scene=bpy.context.scene
# Remove prior R2 lighting if rerun.
for o in list(rig.objects):
 if o.name.startswith('AQUA R2 |'):
  bpy.data.objects.remove(o,do_unlink=True)
# Ground plane and walk strip for exterior framing only.
site_mat=bpy.data.materials.get('AQUA R2 | neutral campus ground') or bpy.data.materials.new('AQUA R2 | neutral campus ground'); site_mat.diffuse_color=(.22,.27,.24,1); site_mat.use_nodes=True; site_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.22,.27,.24,1); site_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.94
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,-.22)); ground=bpy.context.object; ground.name='AQUA R2 | preview ground plane'; ground.dimensions=(185,210,1); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for c in list(ground.users_collection): c.objects.unlink(ground)
rig.objects.link(ground); ground.data.materials.append(site_mat)
# Sidewalk centered along north approach.
cube('AQUA R2 | preview north entry walk',(0,58.5,-.13),(24,10,.12),concrete,rig)
# Grounded exterior 3/4 camera shows massing; interior camera is moved toward long-side stands.
def camera(name,loc,target,lens):
 d=bpy.data.cameras.new(name); d.lens=lens; o=bpy.data.objects.new(name,d); rig.objects.link(o); o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); return o
for nm in ('AQUA R1 | North Street View Camera','AQUA R2 | North Three Quarter Camera','AQUA R2 | Interior Seating Camera'):
 old=bpy.data.objects.get(nm)
 if old: bpy.data.objects.remove(old,do_unlink=True)
excam=camera('AQUA R2 | North Three Quarter Camera',(86,131,28),(0,0,5.4),50)
incam=camera('AQUA R2 | Interior Seating Camera',(50,73,37),(0,0,4.4),45)
# Interior area lights, positioned above the documented pool hall; the gable roof remains hidden for interior review.
for idx,(loc,power,size) in enumerate([((0,-24,8.5),2300,18),((0,0,8.5),2800,18),((0,24,8.5),2300,18),((-18,0,8.0),1400,12)]):
 ld=bpy.data.lights.new(f'AQUA R2 | interior softbox {idx+1}','AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size; lo=bpy.data.objects.new(f'AQUA R2 | interior softbox {idx+1}',ld); rig.objects.link(lo); lo.location=loc; lo.rotation_euler=(0,0,0)
# Exterior sun softening / light bounce.
ld=bpy.data.lights.new('AQUA R2 | soft exterior fill','AREA'); ld.energy=4400; ld.shape='DISK'; ld.size=32; lo=bpy.data.objects.new('AQUA R2 | soft exterior fill',ld); rig.objects.link(lo); lo.location=(5,65,35); lo.rotation_euler=(Vector((0,0,5))-lo.location).to_track_quat('-Z','Y').to_euler()
scene.camera=excam; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1700; scene.render.resolution_y=1100; scene.render.resolution_percentage=75; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
# Keep master placement metadata and collection frame unchanged.
marker=bpy.data.objects.get('Morgan J. Burke Boilermaker Aquatic Center | official GIS footprint interior plinth')
if marker: marker['r2_revision']='Brick pilaster/course depth, ribbon glazing reveals, readable north entry sign, representative documented spectator seating and schematic mezzanine, facade material depth, roof seam/eaves, preview lighting; exact roof/circulation dimensions remain uncertain.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'saved':str(ASSET),'window_panels':len(windows),'added_window_frame_pieces':frame_count,'seat_blocks':300,'r2_mezzanine':True,'master_shared_files_edited':False},indent=2))
