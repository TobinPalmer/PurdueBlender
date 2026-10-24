import bpy, math
from pathlib import Path
from mathutils import Matrix
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
PRE=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; interior=bpy.data.collections['AQUA_Interior']; rig=bpy.data.collections['Preview_Rig']; scene=bpy.context.scene
# The old full-footprint slab passed through both basins and hid their water once placed at the deck level.
old=bpy.data.objects.get('Aquatic | continuous pool deck')
if old: bpy.data.objects.remove(old,do_unlink=True)
plinth=bpy.data.objects.get('Morgan J. Burke Boilermaker Aquatic Center | official GIS footprint interior plinth')
if plinth: bpy.data.objects.remove(plinth,do_unlink=True)
brick=bpy.data.materials['AQUA | mottled Purdue red-brown brick']
for gable in [o for o in asset.all_objects if o and o.type=='MESH' and 'gable end infill' in o.name]:
 gable.data.materials.clear(); gable.data.materials.append(brick)
doc=__import__('json').loads((ROOT/'audit/batchC_boilermaker_aquatic_official_footprint.json').read_text(encoding='utf-8-sig'))
ring=doc['features'][0]['geometry']['rings'][0][:-1]
lat0,lon0=40.4274,-86.9137
lon_m=111412.84*math.cos(math.radians(lat0)); lat_m=111040
xy=[((lon-lon0)*lon_m,(lat-lat0)*lat_m) for lon,lat,*_ in ring]
cx=(min(x for x,y in xy)+max(x for x,y in xy))/2; cy=(min(y for x,y in xy)+max(y for x,y in xy))/2
poly=[(x-cx,y-cy) for x,y in xy]
if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))<0: poly.reverse()
def clip_axis(points,axis,bound,greater):
 if not points:return []
 out=[]
 def inside(p): return p[axis]>=bound-1e-8 if greater else p[axis]<=bound+1e-8
 for a,b in zip(points,points[1:]+points[:1]):
  ia,ib=inside(a),inside(b)
  if ia and ib: out.append(b)
  elif ia and not ib:
   t=(bound-a[axis])/(b[axis]-a[axis]); out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
  elif not ia and ib:
   t=(bound-a[axis])/(b[axis]-a[axis]); out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]))); out.append(b)
 return out
def clip_rect(points,x0,x1,y0,y1):
 for axis,bound,greater in ((0,x0,True),(0,x1,False),(1,y0,True),(1,y1,False)): points=clip_axis(points,axis,bound,greater)
 return points
regions=[
 ('north_end',-31,31,25.0,53),('south_end',-31,31,-53,-25.0),
 ('east_side',12.5,31,-25,25),
 ('west_margin',-31,-28,-11.9,11.9),
 ('west_south_deck',-31,-12.5,-25,-11.9),('west_north_deck',-31,-12.5,11.9,25),
 ('inter_pool_walkway',-14,-12.5,-11.9,11.9),
]
concrete=bpy.data.materials['AQUA | cast concrete']
for label,x0,x1,y0,y1 in regions:
 pts=clip_rect(poly,x0,x1,y0,y1)
 if len(pts)<3: continue
 # A clipped concave outline becomes a single surface within each chosen footprint region.
 me=bpy.data.meshes.new(f'AQUA R1 | {label} deck mesh'); me.from_pydata([(x,y,.24) for x,y in pts],[],[tuple(range(len(pts)))]); me.materials.append(concrete)
 ob=bpy.data.objects.new(f'AQUA R1 | {label} deck section',me); interior.objects.link(ob)
# Reorient the north-facing text so its horizontal and vertical axes read correctly from the street.
label=bpy.data.objects['AQUA R1 | north facade building name']
label.rotation_mode='QUATERNION'; label.rotation_quaternion=Matrix(((-1,0,0),(0,0,1),(0,1,0))).to_quaternion()
# Softer frontal fill light warms the red masonry and avoids the near-silhouette baseline.
for o in list(rig.objects):
 if o.name=='AQUA R1 | facade softbox': bpy.data.objects.remove(o,do_unlink=True)
ld=bpy.data.lights.new('AQUA R1 | facade softbox','AREA'); ld.energy=18500; ld.shape='DISK'; ld.size=32
light=bpy.data.objects.new('AQUA R1 | facade softbox',ld); rig.objects.link(light); light.location=(-15,95,33); light.rotation_euler=(0,0,0)
light.rotation_euler=(__import__('mathutils').Vector((0,49,5))-light.location).to_track_quat('-Z','Y').to_euler()
# Keep a little more sky illumination around the sun-lit facade.
world=scene.world; bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs['Strength'].default_value=.75
# Update/re-save, then create new saved-file renders.
scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=80
scene.camera=bpy.data.objects['AQUA R1 | North Street View Camera']; scene.render.filepath=str(PRE/'aquatic_r1_north_exterior.png'); bpy.ops.render.render(write_still=True,scene=scene.name)
# Hide shell and overhead trusses for an uncluttered plan cutaway preview only; restore before saving.
toggles=[]
for o in asset.all_objects:
 if o and o.type=='MESH' and (o.name=='AQUA R1 | continuous brick and concrete high-bay envelope' or 'pitched roof planes' in o.name or 'standing seam roof ribs' in o.name or 'gable end infill' in o.name or 'schematic clear-span roof truss' in o.name):
  toggles.append((o,o.hide_render)); o.hide_render=True
scene.render.resolution_x=1100; scene.render.resolution_y=1350; scene.render.resolution_percentage=80
scene.camera=bpy.data.objects['AQUA R1 | Interior Cutaway Camera']; scene.camera.data.type='ORTHO'; scene.camera.data.ortho_scale=133; scene.render.filepath=str(PRE/'aquatic_r1_interior_cutaway.png'); bpy.ops.render.render(write_still=True,scene=scene.name)
for o,v in toggles:o.hide_render=v
scene.camera=bpy.data.objects['AQUA R1 | North Street View Camera']
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('AQUA_R1_DECK_AND_PRESENTATION_FIX',len(regions),'deck patches')

