"""Evidence-driven Lyles-Porter Hall library builder (Blender background script).

Rebuilds a detailed local-coordinate asset from Purdue GIS footprint FID 891.
Run with Blender 5.x: blender -b --python modular/buildings/build_lyles_porter_hall.py
"""
import bpy, json, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIT = os.path.join(ROOT, 'audit', 'lyles_porter_hall')
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'lyles_porter_hall.blend')
PREVIEW = os.path.join(AUDIT, 'lyles_porter_hall_preview.png')
PREVIEW_ENTRY = os.path.join(AUDIT, 'lyles_porter_hall_entry_detail.png')
GIS = os.path.join(ROOT, 'audit', 'official_purdue_buildings_wgs84.json')
os.makedirs(AUDIT, exist_ok=True)

LAT0, LON0 = 40.4274, -86.9137
LON_M = 111412.84 * math.cos(math.radians(LAT0))
LAT_M = 111040.0
STORY = 4.572  # 15 ft from Purdue facility record
ROOF_Z = 13.716  # 45 ft record value; 3 above-grade floors, estimated shell height
BASEMENT_Z = -4.2  # partial basement from assignment; exact extent/elevation unverified
SIMPLIFY_TOL = 0.40

with open(GIS, encoding='utf-8') as f:
    dataset = json.load(f)
feature = next(x for x in dataset['features'] if x['attributes'].get('FID') == 891)
assert feature['attributes'].get('BLDG_ABBR') == 'LYLE'
raw_ring = feature['geometry']['rings'][0]
world_xy = [((p[0]-LON0)*LON_M, (p[1]-LAT0)*LAT_M) for p in raw_ring]
world_xy = world_xy[:-1] if world_xy[0] == world_xy[-1] else world_xy
raw_ring_area=abs(sum(world_xy[i][0]*world_xy[(i+1)%len(world_xy)][1]-world_xy[(i+1)%len(world_xy)][0]*world_xy[i][1] for i in range(len(world_xy)))/2)
minx, maxx = min(p[0] for p in world_xy), max(p[0] for p in world_xy)
miny, maxy = min(p[1] for p in world_xy), max(p[1] for p in world_xy)
ORIGIN = ((minx+maxx)/2, (miny+maxy)/2)

def point_line_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = dx*dx + dy*dy
    if den < 1e-12:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy)

ring = [p[:] for p in world_xy]
while len(ring) > 3:
    distances = [(point_line_distance(ring[i], ring[i-1], ring[(i+1)%len(ring)]), i) for i in range(len(ring))]
    d, i = min(distances)
    if d > SIMPLIFY_TOL:
        break
    ring.pop(i)
ring = [(x-ORIGIN[0], y-ORIGIN[1]) for x, y in ring]

signed_area = sum(ring[i][0]*ring[(i+1)%len(ring)][1] - ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
ccw = signed_area > 0

# Reset scene and create the isolated export collection.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection':
        bpy.data.collections.remove(c)
root = bpy.context.scene.collection
for c in list(root.children):
    root.children.unlink(c)
asset_col = bpy.data.collections.new('Asset_lyles_porter_hall')
root.children.link(asset_col)
stage_col = bpy.data.collections.new('Preview_Stage')
root.children.link(stage_col)
CURRENT = asset_col

def link_obj(obj, collection=None):
    collection = collection or CURRENT
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def make_mat(name, color, rough=0.65, metallic=0.0, texture=True, bump_strength=0.12):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    if texture:
        tex = nt.nodes.new('ShaderNodeTexNoise')
        tex.name = name + ' restrained procedural surface variation'
        tex.inputs['Scale'].default_value = 5.0 if 'Brick' in name else 12.0
        tex.inputs['Detail'].default_value = 3.0
        tex.inputs['Roughness'].default_value = 0.68
        coord = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(coord.outputs['Object'], tex.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.22
        ramp.color_ramp.elements[1].position = 0.80
        base = bsdf.inputs['Base Color'].default_value
        ramp.color_ramp.elements[0].color = (base[0]*0.78, base[1]*0.78, base[2]*0.78, 1)
        ramp.color_ramp.elements[1].color = (min(1,base[0]*1.12), min(1,base[1]*1.12), min(1,base[2]*1.12), 1)
        nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.035 if 'Brick' in name else 0.012
        nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        tex.location = (-560, 60); coord.location = (-800,60); ramp.location=(-300,120); bump.location=(-280,-120); bsdf.location=(0,100)
        if 'Brick' in name:
            brick=nt.nodes.new('ShaderNodeTexBrick')
            brick.name='Running-bond brick courses at approximate real scale'
            brick.inputs['Color1'].default_value=(.39,.135,.085,1)
            brick.inputs['Color2'].default_value=(.30,.085,.055,1)
            brick.inputs['Mortar'].default_value=(.18,.055,.04,1)
            brick.inputs['Scale'].default_value=2.0
            brick.inputs['Brick Width'].default_value=.48
            brick.inputs['Row Height'].default_value=.14
            brick.inputs['Mortar Size'].default_value=.012
            brick.inputs['Mortar Smooth'].default_value=.08
            nt.links.new(coord.outputs['Object'],brick.inputs['Vector'])
            nt.links.new(brick.outputs['Color'],bsdf.inputs['Base Color'])
            nt.links.new(brick.outputs['Fac'],bump.inputs['Height'])
            bump.inputs['Strength'].default_value=.18
            bump.inputs['Distance'].default_value=.025
            brick.location=(-540,360)
    return m

MAT_BRICK = make_mat('Lyles Porter | warm red-brown modular brick', (0.31,0.105,0.070), .82, 0, True, .16)
MAT_CONC = make_mat('Lyles Porter | pale gray architectural precast', (.56,.55,.50), .72, 0, True, .11)
MAT_CONC_DARK = make_mat('Lyles Porter | darker exposed foundation concrete', (.34,.34,.31), .8, 0, True, .14)
MAT_GLASS = make_mat('Lyles Porter | blue-gray low-e glazing', (.31,.40,.42), .24, .04, True, .012)
glass_bsdf=MAT_GLASS.node_tree.nodes.get('Principled BSDF')
glass_bsdf.inputs['Alpha'].default_value=.40
glass_bsdf.inputs['Transmission Weight'].default_value=.32
try:
    MAT_GLASS.surface_render_method='BLENDED'
except Exception:
    pass
MAT_FRAME = make_mat('Lyles Porter | dark bronze anodized aluminum', (.10,.12,.12), .3, .65, True, .025)
MAT_ROOF = make_mat('Lyles Porter | charcoal single-ply roof membrane', (.095,.105,.105), .82, 0, True, .16)
MAT_METAL = make_mat('Lyles Porter | rooftop galvanized mechanical metal', (.34,.37,.37), .43, .72, True, .035)
MAT_WOOD = make_mat('Lyles Porter | warm oak lobby furniture', (.38,.22,.11), .56, 0, True, .08)
MAT_INT = make_mat('Lyles Porter | warm interior wall and floor', (.58,.53,.44), .76, 0, True, .06)
MAT_EMIT = bpy.data.materials.new('Lyles Porter | warm lobby lighting')
MAT_EMIT.use_nodes=True
em=MAT_EMIT.node_tree.nodes.get('Principled BSDF')
em.inputs['Base Color'].default_value=(1.0,.73,.42,1)
em.inputs['Emission Color'].default_value=(1.0,.61,.28,1)
em.inputs['Emission Strength'].default_value=1.4

def bevel(obj, amount=.04, segments=2):
    if amount <= 0: return
    mod=obj.modifiers.new('Small architectural edge softening','BEVEL')
    mod.width=amount; mod.segments=segments
    obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')

def box(name, loc, dims, mat, angle=0.0, bevel_size=0.0, collection=None):
    # Build directly without bpy.ops; dozens of facade modules make operator-driven
    # cube creation needlessly quadratic in background Blender sessions.
    hx,hy,hz=(d*.5 for d in dims)
    ca,sa=math.cos(angle),math.sin(angle)
    verts=[]
    for x,y,z in ((-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
                  (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)):
        verts.append((loc[0]+x*ca-y*sa,loc[1]+x*sa+y*ca,loc[2]+z))
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); link_obj(o,collection)
    if mat: o.data.materials.append(mat)
    if bevel_size>=.05 and max(dims)>=1.0:
        bevel(o,min(bevel_size,.08))
    return o

def ring_extrusion(name, pts, z0, z1, mat):
    n=len(pts)
    verts=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
    faces=[]
    faces.append(tuple(range(n-1,-1,-1)) if ccw else tuple(range(n)))
    faces.append(tuple(range(n,2*n)) if ccw else tuple(range(2*n-1,n-1,-1)))
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(mat); mesh.update()
    obj=bpy.data.objects.new(name,mesh); link_obj(obj)
    return obj

def ring_shell_with_openings(name, pts, height, mat, openings_by_edge):
    """Extrude an exact simplified footprint while leaving real punched window bays."""
    verts=[]; faces=[]; n=len(pts)
    bottom=[]; top=[]
    for x,y in pts:
        bottom.append(len(verts)); verts.append((x,y,0.0))
    for x,y in pts:
        top.append(len(verts)); verts.append((x,y,height))
    faces.append(tuple(reversed(bottom)) if ccw else tuple(bottom))
    faces.append(tuple(top) if ccw else tuple(reversed(top)))
    for i,a in enumerate(pts):
        b=pts[(i+1)%n]; L=math.dist(a,b)
        specs=openings_by_edge.get(i,[])
        xcuts={0.0,L}; zcuts={0.0,height}
        for t,z,w,h,_tag in specs:
            xcuts.add(max(0.0,t-w*.5)); xcuts.add(min(L,t+w*.5))
            zcuts.add(max(0.0,z-h*.5)); zcuts.add(min(height,z+h*.5))
        xs=sorted(xcuts); zs=sorted(zcuts)
        dx,dy=b[0]-a[0],b[1]-a[1]; tx,ty=dx/L,dy/L
        for x0,x1 in zip(xs,xs[1:]):
            if x1-x0<.015: continue
            for z0,z1 in zip(zs,zs[1:]):
                if z1-z0<.015: continue
                cx=(x0+x1)*.5; cz=(z0+z1)*.5
                if any(abs(cx-t)<w*.5-.015 and abs(cz-z)<h*.5-.015 for t,z,w,h,_ in specs):
                    continue
                q=[]
                for t,z in ((x0,z0),(x1,z0),(x1,z1),(x0,z1)):
                    q.append(len(verts)); verts.append((a[0]+tx*t,a[1]+ty*t,z))
                faces.append(tuple(q if ccw else reversed(q)))
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(mat); mesh.update()
    obj=bpy.data.objects.new(name,mesh); link_obj(obj)
    return obj

def ext_normal(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    L=max(1e-8,math.hypot(dx,dy)); tx,ty=dx/L,dy/L
    return (ty,-tx) if ccw else (-ty,tx)

def segment_box(name,a,b,z,thick,height,offset,mat, length_pad=0.0):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); angle=math.atan2(dy,dx)
    nx,ny=ext_normal(a,b)
    center=((a[0]+b[0])/2+nx*offset,(a[1]+b[1])/2+ny*offset,z)
    return box(name,center,(L+length_pad,thick,height),mat,angle,0.015)

def window(a,b,center_t,z,w,h,edge_name,tag):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    tx,ty=dx/L,dy/L; nx,ny=ext_normal(a,b)
    x=a[0]+tx*center_t+nx*.10; y=a[1]+ty*center_t+ny*.10
    # dark frame jacket and a recessed blue-gray glass infill
    box(f'{edge_name}_{tag}_frame',(x,y,z),(w+.22,.19,h+.20),MAT_FRAME,math.atan2(dy,dx),.025)
    box(f'{edge_name}_{tag}_glass',(x-nx*.085,y-ny*.085,z),(w,.055,h),MAT_GLASS,math.atan2(dy,dx),.012)
    # fine center mullion, plus a horizontal transom
    box(f'{edge_name}_{tag}_vertical_mullion',(x-nx*.118,y-ny*.118,z),(.055,.04,h),MAT_FRAME,math.atan2(dy,dx),.006)
    box(f'{edge_name}_{tag}_transom',(x-nx*.12,y-ny*.12,z),(w,.04,.045),MAT_FRAME,math.atan2(dy,dx),.004)

# Find the longest frontage along the north side of the GIS envelope for the clinic arrival.
north_main_edge=None; north_score=-1e9
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if abs(dx)>abs(dy) and L>8:
        midy=(a[1]+b[1])/2
        if midy>north_score:
            north_score=midy; north_main_edge=(i,a,b,L)

entry_i=north_main_edge[0] if north_main_edge else -1
window_specs_by_edge={}
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    specs=[]
    if L>=4.2:
        modules=max(1,int(L//2.75)); pitch=L/(modules+1)
        for floor in range(3):
            zmid=(floor+.5)*STORY
            ww=min(1.45,pitch*.52); wh=1.42 if floor==0 else .86
            if i==entry_i and floor==0 and L>18:
                center_t=L*.52; entry_w=min(9.5,L*.38)
                specs.append((center_t,zmid+.05,entry_w,2.9,'arrival_lobby_curtainwall'))
                specs.append((center_t,zmid+.05,1.75,2.55,'vestibule_doors'))
            for m in range(modules):
                t=pitch*(m+1)
                if i==entry_i and floor==0 and abs(t-L*.52)<(min(9.5,L*.38)/2+.65):
                    continue
                specs.append((t,zmid,ww,wh,f'floor{floor+1}_bay{m+1}'))
    window_specs_by_edge[i]=specs

# Construct the walls with actual voids at the windows, allowing visible interior cues.
shell=ring_shell_with_openings('LPH structural wall shell with punched windows | GIS FID 891',ring,ROOF_Z,MAT_BRICK,window_specs_by_edge)
shell['source_feature']='Purdue FeatureServer/0 FID 891, BLDG_ABBR LYLE'
shell['approximate_height_m']=ROOF_Z
shell['height_status']='GIS vertical record R=45 ft used as approximate top; not survey-measured'
shell['wall_openings']='Generated from repeated facade bays; not design-plan exact.'

# Interior floor plates and partially below-grade service floor.
for i,z in enumerate((.14,STORY,STORY*2)):
    ring_extrusion(f'LPH interior floor slab {i+1}',ring,z,z+.18,MAT_CONC)

# Repeated long facade bays with dark glazing and restrained precast ribbons.
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if L<2.5: continue
    edge_name=f'LPH_facade_edge_{i:02d}'
    angle=math.atan2(dy,dx)
    nx,ny=ext_normal(a,b)
    # broad light architectural plinth below the brick, matching Street View
    if L>4:
        segment_box(edge_name+'_precast_base',a,b,1.15,.24,2.15,.08,MAT_CONC,0)
        # light horizontal ribbon at story divisions; joints are fine and not over-scaled
        for z in (3.25,STORY,STORY*2,ROOF_Z-.28):
            segment_box(edge_name+f'_light_belt_{z:.1f}',a,b,z,.18,.13,.12,MAT_CONC,.12)
    # vertical pale corner piers mark structural bays
    if L>6:
        segment_box(edge_name+'_brick_side_belt',a,b,ROOF_Z-.64,.13,.14,.075,MAT_CONC,0)
    if L<4.2: continue
    modules=max(1,int(L//2.75))
    pitch=L/(modules+1)
    for center_t,zmid,w,h,tag in window_specs_by_edge.get(i,[]):
        # Glass is mounted in true shell openings; sightlines reach the interior room cues.
        window(a,b,center_t,zmid,w,h,edge_name,tag)
    if i==entry_i and L>18:
        center_t=L*.52; entry_w=min(9.5,L*.38)
        # cantilevered precast canopy with two slender bronze supports
        x=(a[0]+b[0])/2; y=(a[1]+b[1])/2
        box('LPH main clinic entrance | projecting precast canopy',(x+nx*1.15,y+ny*1.15,3.30),(entry_w+1.0,2.45,.32),MAT_CONC,angle,.055)
        for side in (-1,1):
            t=center_t+side*(entry_w*.43)
            px=a[0]+math.cos(angle)*t+nx*1.85
            py=a[1]+math.sin(angle)*t+ny*1.85
            box(f'LPH canopy post {side:+d}',(px,py,1.60),(.14,.14,3.1),MAT_FRAME,angle,.018)

# Add a clear entry identity plate on north facade, placed in the frontage glass canopy area.
if north_main_edge:
    i,a,b,L=north_main_edge; nx,ny=ext_normal(a,b); angle=math.atan2(b[1]-a[1],b[0]-a[0])
    center_t=L*.52
    x=a[0]+math.cos(angle)*center_t+nx*.33; y=a[1]+math.sin(angle)*center_t+ny*.33
    plaque=box('LPH entrance nameplate',(x,y,3.78),(4.2,.10,.32),MAT_CONC,angle,.02)
    text=bpy.data.curves.new('Lyles-Porter Hall signage','FONT'); text.body='LYLES-PORTER HALL'; text.size=.23; text.extrude=.004
    obj=bpy.data.objects.new('LPH engraved entrance letters',text); link_obj(obj)
    obj.location=(x-math.sin(angle)*.035,y+math.cos(angle)*.035,3.68)
    obj.rotation_euler=(math.pi/2,0,angle)
    text.materials.append(MAT_FRAME)

# Roof parapet and coping around every wall edge; flat low-slope roof reads as membrane.
ring_extrusion('LPH flat roof membrane',ring,ROOF_Z-.05,ROOF_Z+.10,MAT_ROOF)
for i,a in enumerate(ring):
    b=ring[(i+1)%len(ring)]
    if math.dist(a,b)>1.8:
        segment_box(f'LPH roof parapet cap {i:02d}',a,b,ROOF_Z+.38,.30,.56,.02,MAT_CONC,.10)

# Light precast mechanical screen and believable packaged rooftop HVAC equipment.
mx,my=-2.0,5.0
box('LPH rooftop mechanical screen',(mx,my,ROOF_Z+1.12),(15,7,.92),MAT_CONC,math.radians(4),.08)
box('LPH rooftop screen louver',(mx,my-3.56,ROOF_Z+1.18),(12,.10,.53),MAT_METAL,math.radians(4),.015)
for idx,(x,y,w,d,h) in enumerate(((-7,4,3.0,2.2,1.5),(-2,4,3.4,2.4,1.7),(4,4,3.0,2.0,1.35),(-3,-1,2.2,1.8,1.2))):
    z=ROOF_Z+.2+h/2
    box(f'LPH rooftop packaged air handler {idx+1}',(x,y,z),(w,d,h),MAT_METAL,math.radians((idx%2)*3),.065)
    for side in (-1,1):
        box(f'LPH HVAC unit {idx+1} fan grille {side}',(x+side*w*.30,y-d*.505,z+.02),(w*.25,.025,h*.55),MAT_FRAME,0,.005)
    box(f'LPH HVAC unit {idx+1} access panel',(x,y+d*.505,z),(w*.65,.035,h*.70),MAT_CONC,0,.015)
for i,(x,y,h) in enumerate(((-11,-5,1.1),(11,3,1.8),(12,-8,.8),(-11,8,.95))):
    box(f'LPH roof exhaust stack {i+1}',(x,y,ROOF_Z+.2+h/2),(.65,.65,h),MAT_METAL,0,.04)
    box(f'LPH exhaust rain cap {i+1}',(x,y,ROOF_Z+.2+h+.08),(.95,.95,.16),MAT_CONC,0,.02)

# A compact reception glimpse behind the arrival curtain wall.
CURRENT=asset_col
if north_main_edge:
    i,a,b,L=north_main_edge; nx,ny=ext_normal(a,b); ang=math.atan2(b[1]-a[1],b[0]-a[0]); t=L*.52
    cx=a[0]+math.cos(ang)*t-nx*2.25; cy=a[1]+math.sin(ang)*t-ny*2.25
    # glazed lobby floor, welcome desk, stools, suspended light, and a few glass partitions
    box('LPH visible reception lobby floor',(cx,cy,.27),(8.3,4.3,.18),MAT_INT,ang,.025)
    box('LPH reception desk wood counter',(cx,cy-ny*.25,1.15),(3.0,.72,1.05),MAT_WOOD,ang,.04)
    box('LPH reception desk pale transaction top',(cx,cy-ny*.25,1.70),(3.18,.80,.10),MAT_CONC,ang,.025)
    for j in (-1,1):
        x=cx+math.cos(ang)*j*2.45; y=cy+math.sin(ang)*j*2.45
        box(f'LPH lobby waiting chair seat {j}',(x,y,.72),(.72,.72,.14),MAT_WOOD,ang,.06)
        box(f'LPH lobby waiting chair back {j}',(x,y-ny*.26,1.08),(.72,.13,.68),MAT_WOOD,ang,.06)
    box('LPH lobby suspended warm light',(cx,cy,3.52),(3.2,.25,.06),MAT_EMIT,ang,.015)
    box('LPH lobby interior glass partition',(cx+math.cos(ang)*3.25,cy+math.sin(ang)*3.25,2.2),(.06,3.4,3.7),MAT_GLASS,ang,.01)

# Discrete exam-room / research fixtures visible from repeated upper windows.
for floor in (1,2):
    z=floor*STORY+.85
    for idx,(x,y) in enumerate(((-14,12),(6,-12),(16,5))):
        box(f'LPH level {floor+1} research bench {idx+1}',(x,y,z),(2.4,.68,.12),MAT_WOOD,0,.025)
        box(f'LPH level {floor+1} clinic privacy partition {idx+1}',(x+1.05,y,z+.92),(.10,1.8,1.8),MAT_INT,0,.018)
        box(f'LPH level {floor+1} examination lamp {idx+1}',(x,y,z+2.6),(.45,.45,.06),MAT_EMIT,0,.015)

# Facility-specific interior cues: outpatient exam room and an acoustic test booth.
exam_z=1.05
box('LPH representative clinical exam table',(11,9,exam_z),(2.05,.76,.72),MAT_INT,math.radians(90),.055)
box('LPH exam table cushion',(11,9,exam_z+.39),(1.82,.68,.12),MAT_CONC,math.radians(90),.055)
box('LPH clinic wall diagnostic display',(9.8,9.1,2.25),(.12,.10,.65),MAT_FRAME,0,.015)
booth_x,booth_y=5.5,-7.5
box('LPH acoustic hearing booth | floor',(booth_x,booth_y,STORY*2+.12),(2.8,2.5,.14),MAT_CONC,0,.015)
for idx,(x,y,dx,dy) in enumerate(((booth_x,booth_y-1.22,2.8,.12),(booth_x,booth_y+1.22,2.8,.12),(booth_x-1.36,booth_y,.12,2.4),(booth_x+1.36,booth_y,.12,2.4))):
    box(f'LPH acoustic sound booth insulated panel {idx+1}',(x,y,STORY*2+1.52),(dx,dy,2.65),MAT_INT,0,.02)
box('LPH sound booth observation glazing',(booth_x,booth_y-1.30,STORY*2+1.63),(.72,.055,.78),MAT_GLASS,0,.01)
box('LPH audiology test desk',(booth_x+2.25,booth_y-1.0,STORY*2+1.0),(1.4,.65,.76),MAT_WOOD,0,.03)
box('LPH cardio equipment silhouette | Ismail Center',( -18,10,1.0),(2.1,.82,1.15),MAT_FRAME,math.radians(-8),.045)
box('LPH cardio equipment display',(-18,10,1.7),(.48,.12,.30),MAT_EMIT,math.radians(-8),.015)

# A few basement corridor partitions and service rooms, fully below surrounding grade.
box('LPH partial basement utility room floor',(7,-8,BASEMENT_Z+.16),(22,16,.16),MAT_CONC_DARK,0,.02)
for idx,(x,y,dx,dy) in enumerate(((0,-16,18,.18),(15,-8,.18,16),(-11,-6,.18,12))):
    box(f'LPH basement partition {idx+1}',(x,y,BASEMENT_Z+1.7),(dx,dy,3.2),MAT_CONC_DARK,0,.015)

# Consolidate repeated facade boxes into one mesh per material for efficient linking.
def merge_asset_meshes_by_material():
    groups={}
    depsgraph=bpy.context.evaluated_depsgraph_get()
    for obj in list(asset_col.objects):
        if obj.type!='MESH': continue
        mat=obj.data.materials[0] if obj.data.materials else None
        if mat is None: continue
        ev=obj.evaluated_get(depsgraph)
        mesh=ev.to_mesh()
        group=groups.setdefault(mat,{'verts':[],'faces':[],'sources':[]})
        offset=len(group['verts'])
        group['verts'].extend([tuple(ev.matrix_world @ v.co) for v in mesh.vertices])
        group['faces'].extend([tuple(offset+i for i in poly.vertices) for poly in mesh.polygons])
        group['sources'].append(obj.name)
        ev.to_mesh_clear()
        bpy.data.objects.remove(obj,do_unlink=True)
    for mat,g in groups.items():
        mesh=bpy.data.meshes.new('LPH merged '+mat.name+' mesh')
        mesh.from_pydata(g['verts'],[],g['faces']); mesh.materials.append(mat); mesh.update()
        short={'Lyles Porter | warm red-brown modular brick':'shell and brick facade','Lyles Porter | blue-gray low-e glazing':'glazing and mullions','Lyles Porter | pale gray architectural precast':'precast trim and floor plates'}.get(mat.name,mat.name)
        obj=bpy.data.objects.new('LPH merged '+short,mesh)
        asset_col.objects.link(obj); obj['merged_source_mesh_count']=len(g['sources'])
        obj['merged_source_names']=json.dumps(g['sources'])
merge_asset_meshes_by_material()

# Render-only stage is kept outside exported asset collection.
CURRENT=stage_col
ground=make_mat('Preview | neutral matte ground',(.23,.26,.24),.93,0,True,.12)
box('Preview ground',(0,0,-.225),(150,130,.45),ground,0,0,stage_col)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=PREVIEW
scene.world.color=(.32,.32,.32)
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.32,.42,.56,1); bg.inputs['Strength'].default_value=.38

def aim(obj, point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()

# Camera looks at north-side lobby from the northeast corner, high enough to read the winged plan.
cam_data=bpy.data.cameras.new('LPH preview camera'); cam=bpy.data.objects.new('LPH preview camera',cam_data); stage_col.objects.link(cam)
cam.location=(91,88,35); aim(cam,(0,0,6.0)); cam_data.lens=48; scene.camera=cam
sun_data=bpy.data.lights.new('Warm architectural key','AREA'); sun=bpy.data.objects.new('Warm architectural key',sun_data); stage_col.objects.link(sun)
sun.location=(30,-24,42); sun_data.energy=32000; sun_data.shape='DISK'; sun_data.size=18; aim(sun,(0,0,3))
fill_data=bpy.data.lights.new('Soft cool fill','AREA'); fill=bpy.data.objects.new('Soft cool fill',fill_data); stage_col.objects.link(fill)
fill.location=(-30,45,28); fill_data.energy=14000; fill_data.size=25; aim(fill,(0,0,5))
for idx,z in enumerate((2.8,7.2,11.6)):
    ld=bpy.data.lights.new(f'Preview interior wash {idx+1}','AREA')
    lo=bpy.data.objects.new(f'Preview interior wash {idx+1}',ld); stage_col.objects.link(lo)
    lo.location=(0,0,z); ld.energy=1500; ld.shape='DISK'; ld.size=8
    aim(lo,(0,1,z-.5))
scene.view_settings.view_transform='AgX'
scene.render.image_settings.color_mode='RGBA'

# Ensure the exported asset is inspectable; hide preview-only stage from library.
stage_col.hide_viewport=True
scene.render.filepath=PREVIEW
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
stage_col.hide_viewport=False
bpy.ops.render.render(write_still=True)
if north_main_edge:
    ei,ea,eb,eL=north_main_edge
    etx,ety=(eb[0]-ea[0])/eL,(eb[1]-ea[1])/eL
    enx,eny=ext_normal(ea,eb)
    ecx=ea[0]+etx*eL*.52; ecy=ea[1]+ety*eL*.52
    cam.location=(ecx+enx*29,ecy+eny*29,16.5); aim(cam,(ecx,ecy,5.5)); cam_data.lens=52
    scene.render.filepath=PREVIEW_ENTRY
    bpy.ops.render.render(write_still=True)

evidence={
  'building':'Lyles-Porter Hall','building_code':'LYLE','asset_file':'modular/buildings/lyles_porter_hall.blend',
  'collection':'Asset_lyles_porter_hall','feature_service':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0',
  'feature_id':891,'feature_name':'Lyles-Porter Hall','retrieval_date':'2026-10-24','source_crs':'EPSG:4326 (WGS 84; live GIS GeoJSON snapshot in audit/lyles_porter_hall/gis_live_response.geojson)',
  'transform':'project local approximation: X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040.0; envelope center becomes local (0,0)',
  'placement_origin_campus_xy_m':[round(ORIGIN[0],3),round(ORIGIN[1],3)],
  'coordinate_origin_description':'center of transformed GIS feature envelope; local source geometry must be placed at campus XY [-257.675, -717.457] m; Z ground datum 0',
  'footprint_area_m2_from_transformed_raw_ring':round(raw_ring_area,2),'footprint_area_m2_after_simplification':round(abs(signed_area),2),'simplification_area_delta_m2':round(abs(abs(signed_area)-raw_ring_area),2),'original_ring_vertex_count':len(raw_ring),'simplified_ring_vertex_count':len(ring),'simplification_tolerance_m':SIMPLIFY_TOL,
  'height':'13.716 m approximate (GIS F01=15 ft, F02=30 ft, R=45 ft; three above-grade levels); wall roof elevation not survey-verified',
  'partial_basement':'represented at z=-4.2 m under partial footprint/utility zone; extent, floor elevation, and grade visibility unverified',
  'geometry_edits':['Replaced one-object coarse massing proxy geometry with simplified official GIS shell polygon and three-story envelope.','Added repeated brick facade bays, dark window frames and low-e glass, broad precast base, horizontal precast belts, main entrance curtainwall/canopy/signage, visible reception furnishings, exam/research-room cues, partial basement walls and roof/facility mechanicals.','Original massing library was not edited or deleted.'],
  'sources':[
   {'provider':'Purdue University GIS / ArcGIS REST FeatureServer','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':'FID 891, BLDG_ABBR LYLE, Lyles-Porter Hall','retrieved':'2026-10-24','crs':'EPSG:4326','use':'Footprint polygon and facility attributes (story/height fields).','uncertainty':'Shape footprint is a general building footprint; wall height, roof form and grade are not surveyed by this record.'},
   {'provider':'Google Maps Street View','url':'https://www.google.com/maps/@40.4204053,-86.9167997,190a,75y,252.76h,90t/data=!3m7!1e1!3m5!1scraEdjX45J0M0g014PXkxg!2e0','capture_date':'March 2026','retrieved':'2026-10-24','crs':'WGS 84 coordinate in pano URL; Google internal panorama orientation/position, not survey','use':'Harrison Street south-side view of three-story red brick, broad light precast bands and facade rhythm.'},
   {'provider':'Google Maps Street View','url':'https://www.google.com/maps/@40.4214516,-86.9172083,191a,75y,271.71h,90t/data=!3m7!1e1!3m5!1s6IcuOQm2eUwtkI_nVNDBWg!2e0','capture_date':'August 2018','retrieved':'2026-10-24','crs':'WGS 84 coordinate in panorama URL; Google internal panorama orientation/position, not survey','use':'Clinic Drive view at 720 Clinic Dr of brick wings, pale concrete base/bands, repeated window details, recessed entry/service edge and projecting roof overhang.'},
   {'provider':'Purdue University News','url':'https://www.purdue.edu/newsroom/archive/releases/2014/Q3/purdue-dedicates-building-for-health-research,-training,-patient-services.html','published':'2014-09-26','retrieved':'2026-10-24','crs':'N/A','use':'Three-story scale, location, research labs, 30 sound booths, clinics, simulation suite, first floor reception and fitness/nursing/nutrition centers; two- and first-floor program arrangement.'},
   {'provider':'Design 27 project portfolio','url':'https://design27.com/projects/purdue-university-lyles-porter-hall/','published':'page describes Aug 2014 completion; access date 2026-10-24','retrieved':'2026-10-24','crs':'N/A','use':'112,000 sq ft gross area and healthcare-focused design description.'},
   {'provider':'Purdue University Events / Localist building image','url':'https://events.purdue.edu/lyles-porter_hall','photo_url':'https://localist-images.azureedge.net/photos/40176482694176/huge/5424a53b4c04e51e6af0d6683757390274567db6.jpg','retrieved':'2026-10-24','crs':'N/A','use':'Additional published campus facade reference; photo date not stated.'},
   {'provider':'IU School of Medicine blog','url':'https://medicine.iu.edu/blogs/spirit-of-medicine/iu-and-purdue-team-up-to-train-new-physicians-in-west-lafayette','photo_url':'https://mc-34647c8d-0ad3-4e6c-832a-7092-cdn.azureedge.net/-/media/blogs/2021/lyle-outside-2014/lyle-porter-hall-2014.jpg?rev=e41a291e65b94ec6849dfb5163e7ca92','published':'2021; photo 2014 per filename','retrieved':'2026-10-24','crs':'N/A','use':'Independent published exterior view and building/program context.'}
  ],
  'limitations':['Exact architectural plans, floor-to-floor dimensions, roof slopes and mechanical arrangement were unavailable; these are informed estimates.','GIS Shape__Area is 6084.586 in the source field but the transformed WGS84 ring area is 3520.26 square meters; source field units/method are undocumented, so the footprint geometry itself was used and this discrepancy remains open.','The GIS shell polygon is generalized and does not provide verified courtyard, wall thickness or roof-height evidence; compare the footprint top-down before replacing the original massing.','The Google Street View source is dated 2018 for Clinic Drive and March 2026 for Harrison Street; facade match is strong but portions are occluded and branch/corner attribution is approximate.','The interior is schematic; modeled cues include reception, fitness equipment, audiology sound booth and clinic exam table, but room layouts are not detailed construction plans.'],
  'source_massing_comparison':None,
  'geometry_summary':{'local_bounds_xy_m':[[round(min(p[0] for p in ring),3),round(max(p[0] for p in ring),3)],[round(min(p[1] for p in ring),3),round(max(p[1] for p in ring),3)]],'z_bounds_m':[BASEMENT_Z,ROOF_Z+1.9],'approx_story_count_above_grade':3,'source_polygon_ccw':ccw}
}
manifest_path=os.path.join(ROOT,'modular','manifest.json')
try:
    with open(manifest_path,encoding='utf-8') as mf:
        man=json.load(mf)
    mass=next(x for x in man['assets'] if x['id']=='massing_lyles_porter_hall_lyle_604c08e')
    mb=mass.get('bounds_world_m') or mass.get('source_bounds_world_m')
    gis_bounds=[[min(p[0] for p in world_xy),max(p[0] for p in world_xy)],[min(p[1] for p in world_xy),max(p[1] for p in world_xy)]]
    mass_center=[(mb[0][0]+mb[0][1])/2,(mb[1][0]+mb[1][1])/2]
    evidence['source_massing_comparison']={
      'asset_id':mass['id'],'source_file':mass['file'],'original_world_bounds_xy_m':mb[:2],
      'GIS_feature_world_bounds_xy_m':gis_bounds,
      'original_mass_center_minus_GIS_envelope_center_m':[round(mass_center[0]-ORIGIN[0],3),round(mass_center[1]-ORIGIN[1],3)],
      'interpretation':'Existing proxy extent is close but smaller/slightly offset; source massing file remains unchanged. GIS envelope center defines this detailed asset local origin.'
    }
except Exception as exc:
    evidence['source_massing_comparison']={'status':'unverified','reason':str(exc)}
evidence['sources'][0]['query_url']='https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D891&outFields=*&returnGeometry=true&outSR=4326&f=geojson'
with open(os.path.join(AUDIT,'evidence.json'),'w',encoding='utf-8') as f:
    json.dump(evidence,f,indent=2,ensure_ascii=False)
print('LPH_BUILD_DONE',json.dumps({'asset':ASSET,'collection':asset_col.name,'origin':evidence['placement_origin_campus_xy_m'],'local_xy_bounds':evidence['geometry_summary']['local_bounds_xy_m'],'preview':PREVIEW,'ring_points':len(ring)}))
