"""Rebuild the Alpha Gamma Rho Delta chapter house (stable asset 792).

The plan trace is OSM way 301841253 (address 607 N University Street), kept in
PurdueMap's campus world coordinates. Shell heights and room plan are estimates;
architect KJG's 2018 project page documents four levels and approximately 24,100
square feet, but supplies no measured elevations or construction drawings.
"""
from __future__ import annotations
import bpy, json, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET_ID = 'massing_house_301841253_f0b3be3'
COLLECTION_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
ASSET_PATH = os.path.join(os.path.dirname(__file__), ASSET_ID + '.blend')
EVIDENCE_DIR = os.path.join(ROOT, 'audit', 'alpha_gamma_rho')
OSM_PATH = os.path.join(EVIDENCE_DIR, 'sources', 'osm_way_301841253_2026-10-26.json')
LAT0, LON0 = 40.4274, -86.9137

with open(OSM_PATH, 'r', encoding='utf-8-sig') as f:
    osm = json.load(f)
way = next(e for e in osm['elements'] if e.get('type') == 'way' and e.get('id') == 301841253)
nodes = {e['id']: e for e in osm['elements'] if e.get('type') == 'node'}
outline = []
for node_id in way['nodes'][:-1]:
    n = nodes[node_id]
    outline.append(((n['lon']-LON0)*111412.84*math.cos(math.radians(LAT0)), (n['lat']-LAT0)*111040.0))
if len(outline) < 4:
    raise RuntimeError('OSM outline is not a closed polygon with sufficient nodes')

# Start with a clean, deterministic asset file; retain the source and export names.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset)
review = bpy.data.collections.new('Review_Setup_Alpha_Gamma_Rho')
scene.collection.children.link(review)

def mat(name, color, rough=0.76, metallic=0.0, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m

BRICK = mat('AGR | warm red running bond brick', (0.43,0.16,0.105), .86)
BRICK_DARK = mat('AGR | brick shadow courses', (.28,.085,.06), .9)
STONE = mat('AGR | pale limestone and pediment', (.78,.75,.67), .7)
STONE2 = mat('AGR | light stone trim', (.9,.88,.8), .62)
ROOF = mat('AGR | charcoal dimensional shingles', (.13,.16,.2), .85)
BLUE = mat('AGR | blue gray louvered shutters', (.13,.22,.31), .62)
GLASS = mat('AGR | blue tinted window glass', (.1,.24,.33), .2, .18)
WOOD = mat('AGR | dark stained entry doors', (.19,.09,.045), .48)
METAL = mat('AGR | aged bronze hardware', (.19,.16,.11), .38, .72)
FLOOR = mat('AGR | interior warm terrazzo', (.58,.54,.45), .62)
PLASTER = mat('AGR | interior warm ivory plaster', (.84,.81,.72), .9)
CARPET = mat('AGR | interior green corridor carpet', (.13,.26,.18), .94)
OAK = mat('AGR | furniture natural oak', (.49,.29,.13), .62)
BED = mat('AGR | dorm bedding muted navy', (.16,.28,.39), .88)
COUNTER = mat('AGR | kitchen stone counters', (.29,.33,.32), .38)

parts=[]
def mesh(name, verts, faces, material, collection=asset):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    o=bpy.data.objects.new(name,me); collection.objects.link(o); parts.append(o)
    return o

def box(name, center, size, material, bevel=0, collection=asset, rotation_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o=bpy.context.object; o.name=name; o.rotation_euler[2]=rotation_z; o.dimensions=size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o); o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('softened edges','BEVEL'); b.width=bevel; b.segments=2
        o.modifiers.new('weighted face normals','WEIGHTED_NORMAL')
    parts.append(o); return o

def slab(name, polygon, z0,z1, material):
    n=len(polygon); v=[(x,y,z) for z in (z0,z1) for x,y in polygon]
    f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,v,f,material)

def face(name, points, material):
    return mesh(name,points,[tuple(range(len(points)))],material)

def beam_between(name,a,b,width,depth,material):
    mid=(Vector(a)+Vector(b))/2; v=Vector(b)-Vector(a)
    o=box(name,mid,(width,depth,v.length),material,.02)
    o.rotation_mode='QUATERNION'; o.rotation_quaternion=v.to_track_quat('Z','Y')
    return o

xs=[p[0] for p in outline]; ys=[p[1] for p in outline]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
cx,cy=(minx+maxx)/2,(miny+maxy)/2
# Source mapped footprint is north-south, with the named 607 N University
# address on its eastern edge; the main entrance is placed on that east front.
GROUND=0.0; BASEMENT=-1.25; WALL_TOP=10.35; ROOF_RIDGE=13.8
FLOORS=[-0.95,2.55,5.55,8.5]
slab('AGR | continuous basement and foundation',outline,BASEMENT,GROUND,STONE)
# Exterior brick shell, divided by wall belts at floor levels.
slab('AGR | principal brick envelope',outline,GROUND,WALL_TOP,BRICK)
for z in (0.38,3.45,6.45,9.35):
    # Slight projecting belt around the house; these are trim, not footprint walls.
    for i,a in enumerate(outline):
        b=outline[(i+1)%len(outline)]
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length<1: continue
        nx,ny=dy/length,-dx/length
        box(f'AGR | stone belt {z:.2f} edge {i}',((a[0]+b[0])/2+nx*.035,(a[1]+b[1])/2+ny*.035,z),(length,.12,.18),STONE2,.025,rotation_z=math.atan2(dy,dx))

# Two continuous pitched roof planes follow the irregular footprint. Each side
# is clipped at the north-south ridge before the concave plan is made planar.
ridge_x=cx
def clip_x(poly, keep_left):
    out=[]
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)]
        pin=(p[0] <= ridge_x) if keep_left else (p[0] >= ridge_x)
        qin=(q[0] <= ridge_x) if keep_left else (q[0] >= ridge_x)
        if pin: out.append(p)
        if pin != qin:
            t=(ridge_x-p[0])/(q[0]-p[0])
            out.append((ridge_x,p[1]+t*(q[1]-p[1])))
    return out
half_span=max(maxx-ridge_x,ridge_x-minx)
# One continuous longitudinal gable roof matches the long residential frontage
# and keeps the overhang seated on the perimeter walls without sliver facets.
x0,x1=minx-.55,maxx+.55; y0,y1=miny-.55,maxy+.55
face('AGR | continuous west charcoal roof slope',[(x0,y0,WALL_TOP),(ridge_x,y0,ROOF_RIDGE),(ridge_x,y1,ROOF_RIDGE),(x0,y1,WALL_TOP)],ROOF)
face('AGR | continuous east charcoal roof slope',[(ridge_x,y0,ROOF_RIDGE),(x1,y0,WALL_TOP),(x1,y1,WALL_TOP),(ridge_x,y1,ROOF_RIDGE)],ROOF)
# Close both gable ends so the roof seats into brickwork instead of reading as
# a floating lid. The triangle is a characteristic dormered-house end profile.
face('AGR | south brick gable infill',[(x0,y0+.08,WALL_TOP),(ridge_x,y0+.08,ROOF_RIDGE),(x1,y0+.08,WALL_TOP)],BRICK)
face('AGR | north brick gable infill',[(x0,y1-.08,WALL_TOP),(x1,y1-.08,WALL_TOP),(ridge_x,y1-.08,ROOF_RIDGE)],BRICK)
box('AGR | long roof ridge', (ridge_x,cy,ROOF_RIDGE),(.32,y1-y0,.22),ROOF,.05)
# Four roof dormers with pale gable cheeks and louvered face; source rendering.
for j,y in enumerate((miny+8.0,miny+15.0,maxy-15.0,maxy-8.0),1):
    # The photographed dormers face the main east front, so each has a true
    # forward gable, blue louver, and white cheeks rising above the roof.
    x=maxx-4.1
    roof_z=ROOF_RIDGE-(ROOF_RIDGE-WALL_TOP)*abs(x-ridge_x)/half_span
    base=roof_z-.12
    box(f'AGR | dormer {j} white cheek',(x,y,base+.80),(.85,2.35,1.65),STONE2,.055)
    box(f'AGR | dormer {j} blue louver',(x+.47,y,base+.77),(.08,1.25,1.15),BLUE,.025)
    face(f'AGR | dormer {j} white gabled face',[(x+.47,y-1.25,base+.1),(x+.47,y,base+1.72),(x+.47,y+1.25,base+.1)],STONE2)
    beam_between(f'AGR | dormer {j} blue rake left',(x+.50,y-1.38,base+.03),(x+.50,y,base+1.83),.12,.14,BLUE)
    beam_between(f'AGR | dormer {j} blue rake right',(x+.50,y,base+1.83),(x+.50,y+1.38,base+.03),.12,.14,BLUE)

# Window assemblies repeat on every long facade wall edge. They remain separate
# from walls for readable facade detail and are reviewed against photographs.
for floor,zcenter in enumerate((1.65,4.65,7.65),1):
  for i,a in enumerate(outline):
    b=outline[(i+1)%len(outline)]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if L<4.8: continue
    n=int(L//4.5)
    # Source facade rhythm: regular sash windows; avoid the main east entrance.
    for k in range(n):
      t=(k+.5)/n; px=a[0]+t*dx; py=a[1]+t*dy
      if (abs(px-maxx)<1.0 and 340<py<350 and floor==1): continue
      # window is a dark glazed rectangle with stone reveal and paired shutters
      w,h=1.45,1.65
      vx,vy=dy/L,-dx/L # outward normal for CCW ring
      c=(px+vx*.18,py+vy*.18,zcenter)
      ang=math.atan2(dy,dx)
      box(f'AGR | floor {floor} sash glass edge {i} bay {k}',c,(w,.10,h),GLASS,.025,rotation_z=ang)
      for side in (-1,1):
        sx,sy=px+dx/L*side*.94+vx*.19,py+dy/L*side*.94+vy*.19
        box(f'AGR | blue shutter floor {floor} edge {i} bay {k} side {side}',(sx,sy,zcenter),(.34,.12,h*.95),BLUE,.018,rotation_z=ang)
      # stone lintel/sill bands and muntins
      box(f'AGR | stone lintel floor {floor} edge {i} bay {k}',(px+vx*.2,py+vy*.2,zcenter+h/2+.08),(w+.35,.16,.16),STONE2,.02,rotation_z=ang)
      box(f'AGR | stone sill floor {floor} edge {i} bay {k}',(px+vx*.2,py+vy*.2,zcenter-h/2-.08),(w+.35,.18,.16),STONE2,.02,rotation_z=ang)
      box(f'AGR | sash mullion floor {floor} edge {i} bay {k}',(px+vx*.26,py+vy*.26,zcenter),(.07,.06,h),STONE2,.008,rotation_z=ang)
      box(f'AGR | sash rail floor {floor} edge {i} bay {k}',(px+vx*.26,py+vy*.26,zcenter), (w,.06,.06),STONE2,.008,rotation_z=ang)
# Main east entrance porch and unmistakable wide classical portico.
porch_x=maxx+2.2; entry_y=cy
box('AGR | entrance landing',(maxx+1.0,entry_y,.42),(3.0,10.8,.55),STONE,.05)
box('AGR | broad entry stair',(maxx+2.25,entry_y,.18),(3.4,7.2,.28),STONE2,.04)
box('AGR | pediment frieze',(porch_x,entry_y,9.35),(1.15,11.2,.58),STONE2,.035)
for y in (entry_y-4.3,entry_y-1.45,entry_y+1.45,entry_y+4.3):
    box(f'AGR | fluted white portico column {y:.2f}',(maxx+3.5,y,4.95),(.75,.75,8.8),STONE2,.08)
    box(f'AGR | portico column base {y:.2f}',(maxx+3.5,y,.65),(1.0,1.0,.35),STONE,.04)
    box(f'AGR | portico capital {y:.2f}',(maxx+3.5,y,9.35),(1.2,1.2,.4),STONE2,.05)
# Gabled portico roof joins the brick wall and fronts east. The front is a
# broad white triangular panel, framed with saturated blue fascia as in photos.
face('AGR | south pitched portico roof',[(maxx+.05,entry_y-5.6,9.65),(maxx+6.0,entry_y-5.6,9.65),(maxx+6.0,entry_y,12.45),(maxx+.05,entry_y,12.45)],ROOF)
face('AGR | north pitched portico roof',[(maxx+.05,entry_y,12.45),(maxx+6.0,entry_y,12.45),(maxx+6.0,entry_y+5.6,9.65),(maxx+.05,entry_y+5.6,9.65)],ROOF)
face('AGR | white triangular portico gable',[(maxx+6.05,entry_y-5.6,9.65),(maxx+6.05,entry_y,12.5),(maxx+6.05,entry_y+5.6,9.65)],STONE2)
beam_between('AGR | blue fascia south rake',(maxx+6.1,entry_y-5.8,9.55),(maxx+6.1,entry_y,12.6),.42,.42,BLUE)
beam_between('AGR | blue fascia north rake',(maxx+6.1,entry_y,12.6),(maxx+6.1,entry_y+5.8,9.55),.42,.42,BLUE)
beam_between('AGR | blue portico eave',(maxx+6.1,entry_y-5.8,9.55),(maxx+6.1,entry_y+5.8,9.55),.42,.42,BLUE)
# Add a contrasting sign plaque and Greek letters proud of the pediment face.
box('AGR | stone white sign panel',(maxx+6.23,entry_y,10.72),(.12,5.25,1.5),STONE,.035)
t=bpy.data.curves.new('AGR | Alpha Gamma Rho raised letters','FONT'); t.body='ΑΓΡ'; t.align_x='CENTER'; t.align_y='CENTER'; t.size=1.7; t.extrude=.045
obj=bpy.data.objects.new('AGR | green Alpha Gamma Rho sign',t); asset.objects.link(obj); obj.location=(maxx+6.32,entry_y,10.72); obj.rotation_euler=(math.pi/2,0,math.pi/2); t.materials.append(mat('AGR | fraternity green lettering',(.035,.35,.13),.42)); parts.append(obj)
# Front entrance at east wall: paneled double doors, arched transom, lanterns.
box('AGR | cream stone entry surround',(maxx+.21,entry_y,2.02),(.24,3.2,4.15),STONE2,.04)
box('AGR | dark stained double entry door',(maxx+.36,entry_y,1.48),(.2,2.5,2.9),WOOD,.04)
for y in (entry_y-.54,entry_y+.54): box('AGR | inset entry door panel',(maxx+.19,y,1.55),(.05,.72,2.15),OAK,.025)
# Curved transom fan and limestone voussoirs form the arched door head.
arch=[]
for i in range(13):
    a=math.pi*i/12
    arch.append((maxx+.47,entry_y+math.cos(a)*1.25,2.95+math.sin(a)*1.02))
arch += [(maxx+.47,entry_y+1.25,2.95),(maxx+.47,entry_y-1.25,2.95)]
face('AGR | arched glazed entry transom',arch,GLASS)
for i in range(12):
    beam_between(f'AGR | limestone arch voussoir {i}',arch[i],arch[i+1],.18,.20,STONE2)
for y in (entry_y-5.5,entry_y+5.5):
    box('AGR | bronze portico wall lantern',(maxx+.35,y,3.6),(.3,.32,.68),METAL,.05)

# Four occupied levels: floor plates, room partitions and visible furnishing
# volumes. Interior arrangement is programmatically plausible, not survey data.
for level,zfloor in enumerate(FLOORS,0):
    slab(f'AGR | occupied floor plate L{level}',outline,zfloor,zfloor+.18,FLOOR)
    # North-south hall and cross walls are kept inset from outer shell.
    hall_w=2.3; xh=cx
    box(f'AGR | central corridor carpet L{level}',(xh,cy,zfloor+.20),(5.0,maxy-miny-3.0,.035),CARPET,.02)
    for y in (miny+7,miny+14,cy,maxy-14,maxy-7):
        # low partition wall segments with generous door openings
        box(f'AGR | interior room partition L{level} south/east {y:.1f}',(cx+5,y,zfloor+1.45),(8,.16,2.9),PLASTER,.015)
        box(f'AGR | interior room partition L{level} north/west {y:.1f}',(cx-5,y,zfloor+1.45),(8,.16,2.9),PLASTER,.015)
    # Beds in paired rooms on floors 2-4, and common furniture at ground floor.
    if level>=1:
        for ri,y in enumerate((miny+10,miny+19,maxy-19,maxy-10),1):
            for side in (-1,1):
                x=cx+side*7.3
                box(f'AGR | L{level} bedroom {ri} bed frame {side}',(x,y,zfloor+.62),(2.0,3.5,.44),OAK,.08)
                box(f'AGR | L{level} bedroom {ri} mattress {side}',(x,y,zfloor+.92),(1.86,3.28,.18),BED,.06)
                box(f'AGR | bedroom {ri} night table',(x+side*1.5,y-1.0,zfloor+.52),(.65,.65,.75),OAK,.04)
                box(f'AGR | bedroom {ri} wardrobe',(x+side*1.6,y+2.3,zfloor+1.25),(.65,1.1,2.3),WOOD,.04)
    else:
        # Residential common dining and chapter lounge on the first occupied floor.
        for i,y in enumerate((cy-5,cy,cy+5),1):
            box(f'AGR | dining table {i}',(cx+6,y,zfloor+.88),(2.3,3.8,.14),OAK,.05)
            for side in (-1,1):
                for j in (-1,0,1): box(f'AGR | dining chair {i}-{side}-{j}',(cx+6+side*1.55,y+j*1.15,zfloor+.5),(.55,.55,.95),WOOD,.04)
        box('AGR | kitchen island',(cx-7,cy,zfloor+1.0),(2.3,7,.3),COUNTER,.06)
        box('AGR | common room sectional sofa',(cx+8,cy-9,zfloor+.5),(2.6,5.0,1.0),OAK,.12)
        box('AGR | coffee table',(cx+8,cy-5.5,zfloor+.55),(1.5,2,.16),OAK,.04)
# Main stair in a central east/west corridor and a stair core through all four levels.
for level,z in enumerate((.2,3.2,6.2),1):
    for step in range(12):
        x=cx-1.3+step*.22; zz=z+step*.22
        box(f'AGR | stair flight {level} tread {step+1}',(x,cy,zz),(1.3,2.5,.16),STONE2,.015)
    box(f'AGR | stair landing {level}',(cx+1.3,cy,z+1.32),(2.2,3.0,.2),STONE,.025)
# Discreet lower-level basement windows reinforce four-level/partial-basement reading.
for i,a in enumerate(outline):
    b=outline[(i+1)%len(outline)]; L=math.dist(a,b)
    if L<8: continue
    dx,dy=b[0]-a[0],b[1]-a[1]; n=max(1,int(L//8))
    for k in range(n):
        x=a[0]+(k+.5)/n*dx; y=a[1]+(k+.5)/n*dy; nx,ny=dy/L,-dx/L
        box(f'AGR | basement hopper window edge {i} {k}',(x+nx*.12,y+ny*.12,-.48),(1.0,.08,.52),GLASS,.02)

# Keep the camera, lighting and stage outside the exported collection.
# Orthographic angle from east-south shows the entrance and long north/south wing.
def aim(o,point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
world=bpy.data.worlds.new('AGR neutral review world'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.22,.28,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
cam_data=bpy.data.cameras.new('AGR Hero Camera'); cam=bpy.data.objects.new('AGR Hero Camera',cam_data); review.objects.link(cam)
cam.location=(maxx+62,miny-42,39); aim(cam,(cx,cy,4.7)); cam.data.type='ORTHO'; cam.data.ortho_scale=58; scene.camera=cam
for name,loc,power,size in [('Key',(-cx+cx+30,cy-30,48),5200,26),('Fill',(cx-35,cy-5,28),3500,22),('Rim',(cx+5,cy+34,35),4200,20)]:
    ld=bpy.data.lights.new('AGR '+name,'AREA'); lo=bpy.data.objects.new('AGR '+name,ld); review.objects.link(lo); lo.location=loc; ld.energy=power; ld.shape='DISK'; ld.size=size; aim(lo,(cx,cy,5))
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
scene.render.filepath=os.path.join(EVIDENCE_DIR,'renders','alpha_gamma_rho_hero.png')
os.makedirs(os.path.dirname(scene.render.filepath),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)
# A second, deliberately stripped-back first-floor plan preview makes the
# internally modeled dining, kitchen, common room, partitions, and stair legible.
for ob in asset.objects:
    keep = any(token in ob.name for token in (
        'occupied floor plate L0','central corridor carpet L0','interior room partition L0',
        'dining table','dining chair','kitchen island','common room sectional','coffee table',
        'stair flight 1','stair landing 1'))
    ob.hide_render = not keep
plan_cam_data=bpy.data.cameras.new('AGR Interior Plan Camera')
plan_cam=bpy.data.objects.new('AGR Interior Plan Camera',plan_cam_data); review.objects.link(plan_cam)
plan_cam.location=(cx,cy,70); aim(plan_cam,(cx,cy,0)); plan_cam.data.type='ORTHO'; plan_cam.data.ortho_scale=48
scene.camera=plan_cam; scene.render.resolution_x=1200; scene.render.resolution_y=1200
scene.render.filepath=os.path.join(EVIDENCE_DIR,'renders','alpha_gamma_rho_first_floor_interior.png')
bpy.ops.render.render(write_still=True)
