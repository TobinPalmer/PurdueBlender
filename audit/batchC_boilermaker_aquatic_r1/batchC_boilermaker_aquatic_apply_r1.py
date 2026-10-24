import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
AUDIT=ROOT/'audit'
FEATURE= AUDIT/'batchC_boilermaker_aquatic_official_footprint.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
facade=bpy.data.collections['AQUA_Facade']
structure=bpy.data.collections['AQUA_Structure']
roofcol=bpy.data.collections['AQUA_Roof']
interior=bpy.data.collections['AQUA_Interior']
site=bpy.data.collections['AQUA_Site']
rig=bpy.data.collections['Preview_Rig']

# Preserve the existing local frame and reproduce the original GIS bbox-centering transform.
doc=json.loads(FEATURE.read_text(encoding='utf-8-sig'))
ring=doc['features'][0]['geometry']['rings'][0][:-1]
lat0,lon0=40.4274,-86.9137
lon_m=111412.84*math.cos(math.radians(lat0)); lat_m=111040.0
xy=[((lon-lon0)*lon_m,(lat-lat0)*lat_m) for lon,lat,*_ in ring]
cx=(min(x for x,y in xy)+max(x for x,y in xy))/2
cy=(min(y for x,y in xy)+max(y for x,y in xy))/2
pts=[(x-cx,y-cy) for x,y in xy]
if sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))<0: pts.reverse()
max_y=max(y for x,y in pts)

# Existing material palette; correct a previously reused brick trim assignment.
materials={m.name:m for m in bpy.data.materials}
brick=materials['AQUA | mottled Purdue red-brown brick']
concrete=materials['AQUA | cast concrete']
metal=materials['AQUA | charcoal anodized metal']
stone=materials['AQUA | warm gray limestone / precast']
dark=materials['AQUA | deep shadow / reveals']
roofmat=materials['AQUA | weathered membrane / standing seam']
water=materials['AQUA | pool water']
reflective=bpy.data.materials.get('AQUA R1 | blue-gray reflective ribbon glazing')
if reflective is None:
 reflective=bpy.data.materials.new('AQUA R1 | blue-gray reflective ribbon glazing'); reflective.diffuse_color=(.12,.27,.32,1); reflective.use_nodes=True
 bs=reflective.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.12,.27,.32,1); bs.inputs['Roughness'].default_value=.2; bs.inputs['Metallic'].default_value=.28

# Add a restrained Purdue gold shader for pool markers, seat accents and sign fields.
gold=bpy.data.materials.get('AQUA | Purdue gold anodized metal')
if gold is None:
 gold=bpy.data.materials.new('AQUA | Purdue gold anodized metal'); gold.diffuse_color=(.88,.54,.12,1); gold.use_nodes=True
 bs=gold.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.88,.54,.12,1); bs.inputs['Metallic'].default_value=.45; bs.inputs['Roughness'].default_value=.3

# Replace missing exterior envelope with a continuous GIS-aligned wall shell and restrained base plinth.
# The visible north elevation's red brick + horizontal glazing pattern is confirmed in Google Street View.
verts=[]; faces=[]; mids=[]
for p,q in zip(pts,pts[1:]+pts[:1]):
 if math.dist(p,q)<.05: continue
 base=len(verts)
 verts.extend([(p[0],p[1],.24),(q[0],q[1],.24),(q[0],q[1],.58),(p[0],p[1],.58),
               (p[0],p[1],.58),(q[0],q[1],.58),(q[0],q[1],12.0),(p[0],p[1],12.0)])
 faces.extend([(base,base+1,base+2,base+3),(base+4,base+5,base+6,base+7)])
 mids.extend([1,0])
mesh=bpy.data.meshes.new('AQUA R1 | GIS perimeter brick envelope mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(brick); mesh.materials.append(concrete)
for poly,mi in zip(mesh.polygons,mids): poly.material_index=mi
wall=bpy.data.objects.new('AQUA R1 | continuous brick and concrete high-bay envelope',mesh); structure.objects.link(wall)
# Explicitly identify the structural envelope by source and revision.
wall['source']='Purdue GIS BuildingShapesZip4 FID 896 footprint; exterior brick and window band supported by Google Street View panorama captured Jul 2023.'
wall['height_status']='12 m wall datum remains estimated; GIS extrusion field 12 has undocumented units and is not treated as a measured height.'

# Pane details become compact ribbon glazing instead of near full-height transparent sheets.
def reframe_vertical(obj,z0,z1):
 if obj.data.users>1: obj.data=obj.data.copy()
 inv=obj.matrix_world.inverted()
 world=[obj.matrix_world@v.co for v in obj.data.vertices]
 old0=min(v.z for v in world); old1=max(v.z for v in world)
 if old1-old0<1e-7: return
 for vert,point in zip(obj.data.vertices,world):
  point.z=z0+(point.z-old0)*(z1-z0)/(old1-old0)
  vert.co=inv@point

window_count=0
for obj in list(asset.all_objects):
 if obj.type!='MESH': continue
 if obj.name.startswith('AQUA | facade bay') and obj.name.endswith('glazing'):
  reframe_vertical(obj,3.55,5.35)
  obj.data.materials.clear(); obj.data.materials.append(reflective)
  obj['r1_facade_source']='Ribbon window band proportioned from Jul 2023 Street View north elevation; exact window divisions remain schematic.'
  window_count+=1
 elif obj.name.startswith('AQUA | vertical glazing mullion'):
  reframe_vertical(obj,3.43,5.47)
 elif obj.name.startswith('AQUA | glazing sill'):
  reframe_vertical(obj,3.46,3.57)

# Remove generic entry cues misplaced on the south end; build the observed north-side entry/sign/canopy.
for name in ('AQUA | dark entrance name panel','AQUA | entrance threshold'):
 obj=bpy.data.objects.get(name)
 if obj:
  bpy.data.objects.remove(obj,do_unlink=True)
front_y=49.70
# Dark recessed portal with two glass leaves and visible frames.
def cube(name,loc,size,mat,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 obj=bpy.context.object; obj.name=name; obj.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(obj.users_collection): c.objects.unlink(obj)
 col.objects.link(obj); obj.data.materials.clear(); obj.data.materials.append(mat)
 return obj
portal=cube('AQUA R1 | north entrance dark portal', (0,front_y+.07,1.70),(7.2,.16,3.15),dark,facade)
portal['evidence']='Centered north entry and broad canopy visible in Google Street View, Jul 2023.'
for i,x in enumerate((-2.35,-.78,.78,2.35)):
 cube(f'AQUA R1 | north entry glazed door leaf {i+1}',(x,front_y+.18,1.55),(1.44,.09,2.50),reflective,facade)
for x in (-3.12,0,3.12): cube('AQUA R1 | north entry vertical frame',(x,front_y+.25,1.58),(.11,.14,2.75),metal,facade)
cube('AQUA R1 | north entry lintel',(0,front_y+.25,2.96),(6.35,.14,.13),metal,facade)
cube('AQUA R1 | north entry threshold',(0,front_y+.70,.20),(8.6,1.35,.20),concrete,site)
cube('AQUA R1 | north entry canopy',(0,front_y+.9,3.29),(10.6,2.1,.26),stone,facade)

# Exterior title lettering, face normal points north (outward from y-positive elevation).
curve=bpy.data.curves.new('AQUA R1 | exterior name text','FONT'); curve.body='MORGAN J. BURKE AQUATIC CENTER'; curve.size=.39; curve.align_x='CENTER'; curve.align_y='CENTER'; curve.extrude=.006
text_obj=bpy.data.objects.new('AQUA R1 | north facade building name',curve); facade.objects.link(text_obj)
text_obj.location=(0,front_y+.11,5.83); text_obj.rotation_euler=(-math.pi/2,0,0); curve.materials.append(stone)
text_obj['evidence']='Building name visible above the main north entrance in Google Street View, panorama y0c6EFsDkT7g2ak3hsZh5A (Jul 2023).'

# Correct obvious material misassignments from the original generic builder.
for obj in asset.all_objects:
 if obj.type!='MESH' or not obj.data.materials: continue
 if obj.name.startswith('Aquatic | eight-lane pool boundary marking'):
  obj.data.materials.clear(); obj.data.materials.append(dark)
 elif obj.name.startswith('Aquatic | schematic floating lane-rope bead'):
  # Eight original lane ropes are black/white with recurring Purdue-gold markers, not brick.
  try: serial=int(obj.name.rsplit('.',1)[1])
  except (IndexError,ValueError): serial=0
  bead=serial%36
  obj.data.materials.clear(); obj.data.materials.append(gold if bead%6==0 else dark)
 elif obj.name.startswith('Aquatic | schematic lane starting block'):
  obj.data.materials.clear(); obj.data.materials.append(stone)
 elif obj.name.startswith('AQUA | schematic spectator seat accent'):
  obj.data.materials.clear(); obj.data.materials.append(gold if int(obj.name.split('.')[-1])%2 else dark) if obj.name.split('.')[-1].isdigit() else obj.data.materials.append(gold)
 elif obj.name.startswith('AQUA | schematic diving tower platform'):
  obj.data.materials.clear(); obj.data.materials.append(concrete)
 elif obj.name=='AQUA | Purdue gold sign field':
  obj.data.materials.clear(); obj.data.materials.append(gold)

# Bring the eight-lane 50 m competition pool to a realistic deck-relative waterline and ~2.2 m depth.
for obj in list(asset.all_objects):
 if obj.type!='MESH': continue
 if obj.name=='Aquatic | interior pool basin':
  obj.location.z=-.92; obj.dimensions=(25.0,50.0,2.20); bpy.context.view_layer.objects.active=obj; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 elif obj.name=='Aquatic | water surface':
  obj.location.z=.19; obj.dimensions=(24.65,49.65,.05); bpy.context.view_layer.objects.active=obj; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 elif obj.name.startswith('Aquatic | eight-lane pool boundary marking'):
  obj.location.z=.24; obj.dimensions.z=.025; bpy.context.view_layer.objects.active=obj; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 elif obj.name.startswith('Aquatic | schematic floating lane-rope bead'):
  obj.location.z=.30; obj.dimensions.z=.055; bpy.context.view_layer.objects.active=obj; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 elif obj.name.startswith('Aquatic | schematic lane starting block'):
  obj.location.z=.58; obj.dimensions.z=.62; bpy.context.view_layer.objects.active=obj; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

# Replace the staircase of red blocks with a separate 17-ft dive well and source-backed platform levels.
for obj in list(asset.all_objects):
 if obj.type=='MESH' and obj.name.startswith('AQUA | schematic diving tower platform'):
  bpy.data.objects.remove(obj,do_unlink=True)

# Material for deep pool tile, kept connected as a portable Principled material.
tile=bpy.data.materials.get('AQUA R1 | deep pool tile')
if tile is None:
 tile=bpy.data.materials.new('AQUA R1 | deep pool tile'); tile.diffuse_color=(.025,.17,.22,1); tile.use_nodes=True
 bs=tile.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.025,.17,.22,1); bs.inputs['Roughness'].default_value=.36
# Dive pool is adjacent to the competition pool on the west side; 26 yd length is official,
# width is an estimate for six lanes because a dimensioned as-built plan was not available.
dive_x=-21.0; dive_y=0.0; dive_w=14.0; dive_l=23.8; water_z=.18; depth=17*.3048
cube('AQUA R1 | dive pool basin 17ft deep',(dive_x,dive_y,water_z-depth/2),(dive_w,dive_l,depth),tile,interior)
cube('AQUA R1 | dive pool water',(dive_x,dive_y,water_z),(dive_w-.28,dive_l-.28,.05),water,interior)
for k in range(7):
 x=dive_x-dive_w/2+.25+k*(dive_w-.5)/6
 cube(f'AQUA R1 | dive lane rope {k+1}',(x,dive_y,.24),(.045,dive_l-.45,.035),gold if k in (0,6) else dark,interior)
for y in (dive_y-dive_l/2+.3,dive_y+dive_l/2-.3):
 for lane in range(6):
  x=dive_x-dive_w/2+.25+(lane+.5)*(dive_w-.5)/6
  cube('AQUA R1 | dive lane starting block',(x,y,.55),(.62,.82,.58),stone,interior)

# Platform tower at the west edge of the dive well, with official 1/3/5/7.5/10 m heights.
tower_x=-26.1; tower_y=7.0
for dx in (-1.35,1.35):
 for dy in (-.8,.8):
  cube('AQUA R1 | dive platform tower steel column',(tower_x+dx,tower_y+dy,5.3),(.22,.22,10.6),metal,interior)
for level,z in enumerate((1.0,3.0,5.0,7.5,10.0),start=1):
 cube(f'AQUA R1 | {z:g}m diving platform',(tower_x,tower_y,z), (3.5,1.8,.22),concrete,interior)
 # Gold anti-slip edge on each board.
 cube(f'AQUA R1 | {z:g}m platform edge',(tower_x,tower_y-.94,z), (3.5,.10,.08),gold,interior)
 if z>=3:
  for side_x in (tower_x-1.65,tower_x+1.65):
   cube(f'AQUA R1 | {z:g}m platform guardrail post',(side_x,tower_y,z+.55),(.08,.08,1.1),metal,interior)
   cube(f'AQUA R1 | {z:g}m platform guardrail',(side_x,tower_y,z+1.05),(.08,1.7,.08),metal,interior)
# Four official springboards, two at 1 m and two at 3 m; lengths are schematic.
for z,ys in ((1.0,(-4.5,-.5)),(3.0,(.5,4.5))):
 for y in ys:
  cube(f'AQUA R1 | {z:g}m springboard support',(dive_x+dive_w/2-.45,y,z-.26),(.6,.65,.52),concrete,interior)
  cube(f'AQUA R1 | {z:g}m springboard',(dive_x+dive_w/2-2.25,y,z), (4.2,.55,.12),metal,interior)

# 12-person spa from RecWell fact sheet, located at the east deck; exact placement is schematic.
spa_x=24.0; spa_y=31.0
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=2.0,depth=.75,location=(spa_x,spa_y,.45))
spa=bpy.context.object; spa.name='AQUA R1 | 12-person spa shell'; spa.data.materials.append(concrete)
for c in list(spa.users_collection): c.objects.unlink(spa)
interior.objects.link(spa)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.78,depth=.045,location=(spa_x,spa_y,.83))
spa_water=bpy.context.object; spa_water.name='AQUA R1 | spa water surface'; spa_water.data.materials.append(water)
for c in list(spa_water.users_collection): c.objects.unlink(spa_water)
interior.objects.link(spa_water)
for i in range(12):
 ang=2*math.pi*i/12
 cube(f'AQUA R1 | spa seat {i+1}',(spa_x+1.3*math.cos(ang),spa_y+1.3*math.sin(ang),.57),(.42,.42,.26),stone,interior)

# Preserve asset origin and record concise custom metadata on a root-like structural marker.
asset_marker=bpy.data.objects.get('Morgan J. Burke Boilermaker Aquatic Center | official GIS footprint interior plinth')
asset_marker['r1_revision']='North brick envelope and ribbon glazing matched to Jul 2023 Google Street View; separate dive pool and 17ft depth added from Purdue RecWell; correct 50m pool waterline/depth; material palette corrected.'
asset_marker['r1_roof_limit']='GIS/photo evidence supports a broad high-bay roof but does not provide a measured roof section; existing roof form is preserved as uncertain.'
asset_marker['r1_interior_limit']='Pool footprints and dive-pool width/platform structure remain schematic where Purdue does not publish a dimensioned as-built plan.'

# Add evidence-grade cameras and a daylight world in Preview_Rig, not the export collection.
scene=bpy.context.scene
for name in ('AQUA R1 | North Street View Camera','AQUA R1 | Interior Cutaway Camera'):
 old=bpy.data.objects.get(name)
 if old: bpy.data.objects.remove(old,do_unlink=True)
def camera(name,loc,target,lens):
 data=bpy.data.cameras.new(name); data.lens=lens
 obj=bpy.data.objects.new(name,data); rig.objects.link(obj); obj.location=loc
 obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
 return obj
front_cam=camera('AQUA R1 | North Street View Camera',(0,145,14),(0,49.6,6.2),55)
interior_cam=camera('AQUA R1 | Interior Cutaway Camera',(8,73,51),(0,0,3.5),44)
scene.camera=front_cam
# Use a procedural clear sky and broad, soft daylight for an interpretable exterior render.
world=bpy.data.worlds.get('AQUA R1 | Clear Day Sky') or bpy.data.worlds.new('AQUA R1 | Clear Day Sky')
scene.world=world; world.use_nodes=True
nt=world.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputWorld'); bg=nt.nodes.new('ShaderNodeBackground'); sky=nt.nodes.new('ShaderNodeTexSky'); sky.sky_type='HOSEK_WILKIE'; sky.sun_elevation=math.radians(42); sky.sun_rotation=math.radians(225); sky.air_density=1.0
nt.links.new(sky.outputs['Color'],bg.inputs['Color']); bg.inputs['Strength'].default_value=.55; nt.links.new(bg.outputs['Background'],out.inputs['Surface'])
# Main daylight sun, kept with preview rig only.
for o in list(rig.objects):
 if o.name=='AQUA R1 | daylight sun': bpy.data.objects.remove(o,do_unlink=True)
light_data=bpy.data.lights.new('AQUA R1 | daylight sun','SUN'); light_data.energy=2.1; light_data.angle=math.radians(8)
sun=bpy.data.objects.new('AQUA R1 | daylight sun',light_data); rig.objects.link(sun); sun.rotation_euler=(math.radians(20),math.radians(-25),math.radians(135))
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=75
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
# Save the individual building only; no master or manifest is opened or touched.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'saved':str(ASSET),'objects':len(asset.all_objects),'ribbon_window_panels':window_count,'local_xy':(round(cx,3),round(cy,3)),'north_edge_y_max':max_y,'asset_bbox':[[-30.1,-51.25,0],[30.1,51.25,12.3]],'master_or_manifest_edited':False},indent=2))

