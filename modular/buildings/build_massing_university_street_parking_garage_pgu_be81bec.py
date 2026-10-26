import bpy, json, math, os
from mathutils import Vector
from math import radians, cos
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ID = 'massing_university_street_parking_garage_pgu_be81bec'
AUDIT = os.path.join(ROOT, 'audit', 'university_street_garage_pgu')
ASSET = os.path.join(ROOT, 'modular', 'buildings', ID + '.blend')
SRC = os.path.join(AUDIT, 'purdue_building_FID260.geojson')
COLL = 'Asset_' + ID
SCENE = 'Building_' + ID
# Official footprint source in EPSG:4326. Campus local conversion is defined in modular/AGENTS.md.
feat=json.load(open(SRC,encoding='utf-8'))['features'][0]
ring=feat['geometry']['coordinates'][0]
lon0=(min(p[0] for p in ring)+max(p[0] for p in ring))/2
lat0=(min(p[1] for p in ring)+max(p[1] for p in ring))/2
origin=( (lon0+86.9137)*111412.84*cos(radians(40.4274)), (lat0-40.4274)*111040.0 )
poly=[((lon+86.9137)*111412.84*cos(radians(40.4274))-origin[0], (lat-40.4274)*111040.0-origin[1]) for lon,lat in ring[:-1]]
# reset to an isolated, portable scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
root=bpy.context.scene.collection
for c in list(root.children): root.children.unlink(c)
asset=bpy.data.collections.new(COLL); root.children.link(asset)
# Named scene and asset hierarchy only.
for sc in list(bpy.data.scenes):
    if sc != bpy.context.scene: bpy.data.scenes.remove(sc)
scene=bpy.context.scene; scene.name=SCENE
# Materials
def mat(name,color,rough=0.78,noise=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    if noise:
        n=m.node_tree.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=noise[0]; n.inputs['Detail'].default_value=2
        ramp=m.node_tree.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.25; ramp.color_ramp.elements[0].color=(*noise[1],1); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(*noise[2],1)
        m.node_tree.links.new(n.outputs['Fac'],ramp.inputs[0]); m.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    return m
concrete=mat('Warm gray precast concrete',(.49,.47,.42),.86,(32,(.34,.33,.29),(.61,.59,.53)))
panel=mat('Light concrete spandrel',(.68,.66,.59),.8,(24,(.56,.54,.48),(.76,.74,.68)))
brick=mat('Purdue red-brown brick piers',(.28,.095,.054),.88,(18,(.19,.055,.031),(.38,.13,.075)))
asphalt=mat('Dark traffic coating',(.075,.083,.083),.9,(6,(.045,.05,.05),(.12,.13,.12)))
shadow=mat('Open deck shadow',(.035,.045,.048),.98)
metal=mat('Dark steel guard rails',(.12,.15,.16),.55)
glass=mat('Stair glazing',(.16,.26,.3),.35)
line=mat('Parking bay marking',(.84,.76,.48),.7)
# helpers
def link_obj(obj,name,material):
    obj.name=name; asset.objects.link(obj)
    if material: obj.data.materials.append(material)
    return obj
def box(name,loc,dim,material,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    link_obj(o,name,material)
    if bev:
        mod=o.modifiers.new('Soft cast edges','BEVEL'); mod.width=bev; mod.segments=2
    return o
def mesh_obj(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update(); ob=bpy.data.objects.new(name,me); asset.objects.link(ob); return ob
def prism(name,z0,z1,material):
    n=len(poly); verts=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): j=(i+1)%n; faces.append((i,j,n+j,n+i))
    return mesh_obj(name,verts,faces,material)
# GIS polygon area plates; six parking levels supported by source's NUM_LEVELS=6.
W=max(x for x,y in poly)-min(x for x,y in poly); D=max(y for x,y in poly)-min(y for x,y in poly)
base_z=0; floor_h=2.85; deck_t=.32
# base asphalt podium/deck and 5 upper decks, approximate level height guided by GIS 47ft extrusion and six floors
for k in range(6):
    z=k*floor_h
    prism(f'Parking deck {k+1} | official GIS outline',z-deck_t if k else z-.15,z,asphalt if k==0 else concrete)
    # thin bright outer fascia wrapping the official perimeter
    prism(f'Precast perimeter fascia {k+1}',z,z+.66,panel)
# top roof layer
prism('Rooftop traffic coating',5*floor_h,5*floor_h+.10,asphalt)
# Structural grid approximate: parking garage column rhythm, explicitly inferred in evidence.
# Interior grid falls inside the surveyed outline; visual line of sight remains open.
xmin,xmax=min(x for x,y in poly),max(x for x,y in poly); ymin,ymax=min(y for x,y in poly),max(y for x,y in poly)
for ix,x in enumerate([xmin+8+i*9 for i in range(max(1,int((W-16)//9)))]):
  for iy,y in enumerate([ymin+8+j*9 for j in range(max(1,int((D-16)//9)))]):
    for k in range(5): box(f'Concrete support column {ix+1}-{iy+1} level {k+1}',(x,y,k*floor_h+1.25),(.48,.48,2.5),concrete,.025)
# Windowless open garage elevations: shadowed openings + parapet band; brick piers rhythmically punctuate the perimeter.
for ei,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if length<1: continue
    ux,uy=dx/length,dy/length; nx,ny=-uy,ux
    # Open dark reveal behind broad parapet strips. Keep gaps at each level for ventilation.
    segments=max(1,int(length//13))
    for j in range(segments):
        mid=(j+.5)*length/segments
        cx=a[0]+ux*mid; cy=a[1]+uy*mid
        for k in range(5):
            z=k*floor_h
            # back-set dark ventilation opening
            bay=box(f'Open-air deck bay E{ei+1}-{j+1} L{k+1}',(cx-nx*.12,cy-ny*.12,z+1.80),(length/segments-1.1,.10,.86),shadow); bay.rotation_euler[2]=math.atan2(dy,dx)
        # brick piers extend continuously through decks at bay divisions
    for j in range(segments+1):
        s=max(.35,min(length-.35,j*length/segments)); cx=a[0]+ux*s; cy=a[1]+uy*s
        box(f'Brick facade pier E{ei+1}-{j+1}',(cx,cy,7.1),(.78,.78,14.2),brick,.035)
    # Spandrel top course at each level along each edge (leave ventilation ribbon)
    for k in range(5):
       z=k*floor_h+.73; mid=length/2
       band=box(f'Precast parapet band E{ei+1} L{k+1}',(a[0]+ux*mid,a[1]+uy*mid,z),(length,.22,.54),panel,.02); band.rotation_euler[2]=math.atan2(dy,dx)
# Four reinforced brick stair/elevator towers on corner zones, with blue-gray vertical glazing and roof caps.
for ti,(x,y) in enumerate([(xmin+5,ymin+5),(xmax-5,ymin+5),(xmin+5,ymax-5),(xmax-5,ymax-5)]):
    box(f'Brick stair and elevator core {ti+1}',(x,y,7.35),(6.2,6.2,14.7),brick,.04)
    # vertical inset glazed slots on two exposed faces
    box(f'Core glazing {ti+1}A',(x+3.13,y,7.35),(.05,1.35,12.8),glass)
    box(f'Core glazing {ti+1}B',(x,y-3.13,7.35),(1.35,.05,12.8),glass)
    box(f'Core roof cap {ti+1}',(x,y,14.82),(6.55,6.55,.18),concrete,.03)
# Two inferred switchback ramp ribbons at opposite ends; ramp slope is a visual circulation cue, exact route unverified.
def ramp_flight(name,x,y,z0,z1,length,width):
    ob=box(name,(x,y,(z0+z1)/2),(length,width,deck_t),concrete)
    ob.rotation_euler[1]=math.atan2(z1-z0,length)
# Paired ramp runs on north and south edges between levels, compact and clearly legible inside envelope.
for k in range(5):
    z0=k*floor_h+.05; z1=(k+1)*floor_h-.05
    ramp_flight(f'Inferred one-way ramp north L{k+1}-{k+2}',-W*.22, y+0 if False else (ymax-20),z0,z1,20,5.0)
    ramp_flight(f'Inferred return ramp south L{k+1}-{k+2}',W*.22,ymin+20,z1,z0,20,5.0)
# Parking stall stripes in representative ground and rooftop decks (not an asserted exact layout)
for k in (0,5):
  z=k*floor_h+.025
  for x in range(int(xmin+14),int(xmax-10),5):
    for y in (ymin+15,ymax-17):
      box(f'Parking stall stripe L{k+1}',(x,y,z),(0.055,4,.018),line)
# Entry/exit portals on south edge per official access location and city address, exact opening positions approximate.
# Provide two open portal slots at the centroid of each long southern boundary segment.
# Signs are small physical panels; text is evidence-supported by source photo and official site.
for idx,x in enumerate((xmin+W*.34,xmin+W*.68)):
    y=ymin+.12
    box(f'Entry exit portal shadow {idx+1}',(x,y,.9),(10,.16,1.8),shadow)
    label='ENTER  P1' if idx==0 else 'EXIT'
    cu=bpy.data.curves.new('Garage wayfinding '+str(idx+1),'FONT'); cu.body=label; cu.size=.62; cu.extrude=.008
    ob=bpy.data.objects.new('Garage wayfinding sign '+str(idx+1),cu); asset.objects.link(ob); ob.location=(x-2.4,y-.19,1.7); ob.rotation_euler[0]=radians(90); cu.materials.append(panel)
# scene presentation camera and lighting; all presentation objects live outside the exported asset collection.
pres=bpy.data.collections.new('Presentation'); scene.collection.children.link(pres)
def move_pres(o):
  for c in list(o.users_collection): c.objects.unlink(o)
  pres.objects.link(o); return o
cam_data=bpy.data.cameras.new('Garage hero camera'); cam=bpy.data.objects.new('Garage hero camera',cam_data); pres.objects.link(cam)
cam.location=(W*.95,-D*1.45,39); target=Vector((0,0,7)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=max(W,D)*1.7; scene.camera=cam
ld=bpy.data.lights.new('Large softbox','AREA'); lo=bpy.data.objects.new('Large softbox',ld); pres.objects.link(lo); lo.location=(0,-60,75); ld.energy=35000; ld.size=65
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.36,.39,.43,1); scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
scene.view_settings.view_transform='AgX'
scene.render.filepath=os.path.join(AUDIT,'pgu_hero.png')
# Set origin/metadata for reliable campus instancing; geometry is already centered about local origin.
asset['building_id']=ID; asset['placement_origin_xy_m']=list(origin); asset['source_feature_id']=260; asset['units']='meters; local X east, Y north, Z up'
scene['building_id']=ID; scene['placement_origin_xy_m']=list(origin)
# Select asset collection and set sane viewport.
bpy.ops.object.select_all(action='DESELECT')
# save file
os.makedirs(os.path.dirname(ASSET),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.render.render(write_still=True)
print('PGU_BUILD_OK',ASSET,'origin',origin,'bounds',W,D,'area',feat['properties'].get('Shape__Area'))


