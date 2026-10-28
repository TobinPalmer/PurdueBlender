import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
cfg_path = os.path.join(os.path.dirname(__file__), 'build_config.json')
with open(cfg_path, encoding='utf-8-sig') as f: cfg=json.load(f)
blend_path=bpy.data.filepath
obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if not blend_path or obj is None or coll is None or obj not in coll.objects[:]: raise RuntimeError('Target asset structure mismatch')
if len(coll.objects)!=1: raise RuntimeError('Expected exactly one object in assigned exported collection')
with open(os.path.join(os.path.dirname(__file__),cfg['source_feature_file']),encoding='utf-8-sig') as f: feature=json.load(f)
attrs=feature['attributes']; ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
origin_lat=40.4274; origin_lon=-86.9137
points=[Vector(((lon-origin_lon)*111412.84*math.cos(math.radians(origin_lat)),(lat-origin_lat)*111040.0)) for lon,lat in ring]
if len(points)<3: raise RuntimeError('Bad official footprint ring')
# Orient ring consistently so facade props sit on the exterior side.
area2=sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))
sign=1.0 if area2>0 else -1.0
tag=cfg['asset_id'].upper().replace('MASSING_','')
mats=[]
def make_mat(name,color,rough=0.78,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(*color,1); bsdf.inputs['Roughness'].default_value=rough; bsdf.inputs['Metallic'].default_value=metal
    mats.append(m); return len(mats)-1
def make_surface_brick(name,color):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); nodes=nt.nodes; links=nt.links
    out=nodes.new('ShaderNodeOutputMaterial'); out.location=(260,80)
    bs=nodes.new('ShaderNodeBsdfPrincipled'); bs.location=(40,80); bs.inputs['Roughness'].default_value=0.86
    uv=nodes.new('ShaderNodeTexCoord'); uv.location=(-680,120)
    brick=nodes.new('ShaderNodeTexBrick'); brick.location=(-450,150)
    brick.inputs['Color1'].default_value=(0.25,0.075,0.045,1); brick.inputs['Color2'].default_value=(0.18,0.045,0.025,1)
    brick.inputs['Mortar'].default_value=(0.37,0.28,0.22,1); brick.inputs['Brick Width'].default_value=0.42; brick.inputs['Row Height'].default_value=0.18; brick.inputs['Mortar Size'].default_value=0.015
    links.new(uv.outputs['UV'],brick.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump'); bump.location=(-180,-60); bump.inputs['Strength'].default_value=0.18; bump.inputs['Distance'].default_value=0.012
    links.new(brick.outputs['Color'],bs.inputs['Base Color']); links.new(brick.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal']); links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    mats.append(m); return len(mats)-1
def make_tile_roof(name,color):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); nodes=nt.nodes; links=nt.links
    out=nodes.new('ShaderNodeOutputMaterial'); out.location=(260,60)
    bs=nodes.new('ShaderNodeBsdfPrincipled'); bs.location=(40,60); bs.inputs['Roughness'].default_value=0.78
    uv=nodes.new('ShaderNodeTexCoord'); uv.location=(-680,100)
    tile=nodes.new('ShaderNodeTexBrick'); tile.location=(-450,130)
    tile.inputs['Color1'].default_value=(0.22,0.055,0.02,1); tile.inputs['Color2'].default_value=(0.34,0.095,0.035,1)
    tile.inputs['Mortar'].default_value=(0.055,0.04,0.03,1); tile.inputs['Brick Width'].default_value=0.34; tile.inputs['Row Height'].default_value=0.18; tile.inputs['Mortar Size'].default_value=0.018
    links.new(uv.outputs['UV'],tile.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump'); bump.location=(-170,-60); bump.inputs['Strength'].default_value=0.24; bump.inputs['Distance'].default_value=0.025
    links.new(tile.outputs['Color'],bs.inputs['Base Color']); links.new(tile.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal']); links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    mats.append(m); return len(mats)-1
def make_epdm(name):
    m=bpy.data.materials.new(name); m.diffuse_color=(0.10,0.12,0.14,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); nodes=nt.nodes; links=nt.links
    out=nodes.new('ShaderNodeOutputMaterial'); bs=nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value=0.88
    tex=nodes.new('ShaderNodeTexCoord'); noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=36.0; noise.inputs['Detail'].default_value=2.0
    ramp=nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=0.22; ramp.color_ramp.elements[0].color=(0.025,0.032,0.038,1); ramp.color_ramp.elements[1].position=0.78; ramp.color_ramp.elements[1].color=(0.085,0.10,0.115,1)
    bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.12; bump.inputs['Distance'].default_value=0.012
    links.new(tex.outputs['Generated'],noise.inputs['Vector']); links.new(noise.outputs['Fac'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],bs.inputs['Base Color']); links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal']); links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    mats.append(m); return len(mats)-1
wall=make_surface_brick(tag+'_Exterior_Brick',cfg['wall_color']); stone=make_mat(tag+'_Indiana_Limestone',cfg['stone_color']); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_epdm(tag+'_EPDM_Flat_Roof'); tile_roof=make_tile_roof(tag+'_Clay_Tile_Roof',cfg['roof_color']); metal=make_mat(tag+'_Copper_Details',(0.25,0.14,0.08),0.38,0.62); sculpture=make_mat(tag+'_Lion_Relief',(0.55,0.29,0.065),0.72)
interior_floor=make_mat(tag+'_Interior_Slate_and_Tile',(0.18,0.21,0.21),0.8)
plaster=make_mat(tag+'_Interior_Plaster',(0.78,0.75,0.68),0.93)
oak=make_mat(tag+'_Quarter_Sawn_Oak',(0.24,0.095,0.035),0.64)
dark_wood=make_mat(tag+'_Tudor_Timber',(0.11,0.065,0.04),0.68)
carpet=make_mat(tag+'_Room_Carpet',(0.12,0.16,0.16),0.93)
bed_mat=make_mat(tag+'_Dorm_Bed_Linen',(0.86,0.82,0.70),0.93)
furniture_mat=make_mat(tag+'_Dorm_Furniture',(0.17,0.085,0.035),0.77)
accent_mat=make_mat(tag+'_Interior_Accent',(0.035,0.23,0.27),0.88)
tile_light=make_mat(tag+'_Lobby_Mosaic_Light',(0.72,0.61,0.44),0.78)
tile_dark=make_mat(tag+'_Lobby_Mosaic_Dark',(0.24,0.29,0.30),0.82)
verts=[]; faces=[]; mi=[]
def face(ids,mat): faces.append(tuple(ids)); mi.append(mat)
def quad(ps,mat):
    k=len(verts); verts.extend(tuple(p) for p in ps); face((k,k+1,k+2,k+3),mat)
def triangle(ps,mat):
    k=len(verts); verts.extend(tuple(p) for p in ps); face((k,k+1,k+2),mat)
def box(center,tangent,normal,w,d,h,mat):
    c=Vector(center); t=Vector((tangent.x,tangent.y,0)).normalized(); n=Vector((normal.x,normal.y,0)).normalized(); z=Vector((0,0,1)); hw=w/2; hd=d/2; hh=h/2
    offsets=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]; k=len(verts)
    verts.extend(tuple(c+t*a+n*b+z*v) for a,b,v in offsets)
    for f0 in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face(tuple(k+j for j in f0),mat)
H=float(cfg['height_m']); F=int(cfg['modeled_floors']); base=0.0; plinth=min(0.72,H*0.09); story=H/max(1,F)
edge=[]
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]; delta=b-a; L=delta.length
    if L<0.05: continue
    t=Vector((delta.x/L,delta.y/L,0)); n=Vector((t.y,-t.x,0))*sign; edge.append((a,b,L,t,n))
    a0=Vector((a.x,a.y,base)); b0=Vector((b.x,b.y,base)); a1=Vector((a.x,a.y,plinth)); b1=Vector((b.x,b.y,plinth)); at=Vector((a.x,a.y,H)); bt=Vector((b.x,b.y,H))
    quad((a0,b0,b1,a1),stone); quad((a1,b1,bt,at),wall)
def inside_poly(x,y):
    inside=False; j=len(points)-1
    for i,pi in enumerate(points):
        pj=points[j]
        if ((pi.y>y)!=(pj.y>y)) and x < (pj.x-pi.x)*(y-pi.y)/(pj.y-pi.y)+pi.x: inside=not inside
        j=i
    return inside
# Flat roof deck follows the full GIS footprint. Public 2023 roof-replacement documents
# specify clay tile, copper and EPDM systems; three conservative gabled tile ranges and
# copper trim are added while the remaining roof stays an EPDM-like flat section.
for tri in tessellate_polygon([points]):
    k=len(verts)
    for idx in tri:
        p=points[int(idx)]; verts.append((p.x,p.y,H))
    face((k,k+1,k+2),roof)

def gable_roof(center,tangent,normal,length,width,rise=2.65):
    c=Vector((center[0],center[1],0)); t=Vector((tangent[0],tangent[1],0)).normalized(); n=Vector((normal[0],normal[1],0)).normalized()
    z0=H-0.08; zr=H+rise
    e0=c-t*length/2-n*width/2+Vector((0,0,z0)); e1=c+t*length/2-n*width/2+Vector((0,0,z0))
    e2=c+t*length/2+n*width/2+Vector((0,0,z0)); e3=c-t*length/2+n*width/2+Vector((0,0,z0))
    r0=c-t*length/2+Vector((0,0,zr)); r1=c+t*length/2+Vector((0,0,zr))
    quad((e0,e1,r1,r0),tile_roof); quad((r0,r1,e2,e3),tile_roof)
    triangle((e0,e3,r0),wall); triangle((e1,r1,e2),wall)
    # Restrained dark timber ties and king posts on the visible gable ends echo the documented Tudor style.
    for end,sgn in ((c-t*length/2,-1),(c+t*length/2,1)):
        box(end+Vector((0,0,H+0.55)),n,t,width*0.78,0.12,0.16,dark_wood)
        box(end+Vector((0,0,H+1.05)),n,t,0.16,0.12,1.55,dark_wood)
        # Limestone verge/coping and copper flashing details at the lower roof edge.
        box(end+Vector((0,0,H+0.12))+n*(width*0.46),n,t,0.14,0.11,0.12,stone)
    # Copper eaves at both long sides, kept in scale with the roof.
    box(c-n*width/2+Vector((0,0,H-0.03)),t,n,length,0.11,0.12,metal)
    box(c+n*width/2+Vector((0,0,H-0.03)),t,n,length,0.11,0.12,metal)

gable_roofs=[
    # Three long, aligned clay-tile wings follow the GIS U-plan: north cross-wing
    # and the two diagonal arms. Their modest overhangs leave visible dark EPDM
    # valleys/field zones between roof runs instead of isolated short roof islands.
    ((-589.5,-139.0),(1,0),(0,1),25.5,8.0),
    ((-615.0,-156.0),(0.7071,0.7071),(-0.7071,0.7071),27.0,7.0),
    ((-575.0,-156.0),(0.7071,-0.7071),(0.7071,0.7071),27.0,7.0),
]
for gc,gt,gn,gl,gw in gable_roofs: gable_roof(gc,gt,gn,gl,gw,rise=3.1)

def oriented_box(center,tangent,normal,w,d,h,material):
    t=Vector((tangent[0],tangent[1],0)) if isinstance(tangent,(tuple,list)) else tangent
    n=Vector((normal[0],normal[1],0)) if isinstance(normal,(tuple,list)) else normal
    box(center,t,n,w,d,h,material)
def corners_fit(center,tangent,normal,w,d):
    c=Vector((center[0],center[1],0)); t=Vector((tangent[0],tangent[1],0)).normalized(); n=Vector((normal[0],normal[1],0)).normalized()
    return all(inside_poly((c+t*a+n*b).x,(c+t*a+n*b).y) for a in (-w/2,w/2) for b in (-d/2,d/2))

# GIS reports five above-ground levels and Purdue Residence Life publishes Windsor
# single/double layouts at approximately 14 x 16 feet. Interior examples use those
# dimensions and are repeated as schematic modules; exact room locations are unknown.
room_t=(0.7071,0.7071); room_n=(-0.7071,0.7071)
single_center=(-610.0,-152.0); double_center=(-582.0,-148.0)
floor_levels=[0.16,3.04,6.08,9.12,12.16]
room_w=4.267; room_d=4.877
for fz in floor_levels:
    for tri0 in tessellate_polygon([points]):
        k=len(verts)
        for idx in tri0:
            p=points[int(idx)]; verts.append((p.x,p.y,fz))
        face((k,k+1,k+2),interior_floor)

def room_module(center,z,double=False):
    c=Vector((center[0],center[1],z)); t=Vector((room_t[0],room_t[1],0)).normalized(); n=Vector((room_n[0],room_n[1],0)).normalized()
    if not corners_fit(center,room_t,room_n,room_w,room_d): return False
    oriented_box(c+Vector((0,0,0.08)),t,n,room_w-0.08,room_d-0.08,0.10,carpet)
    wh=2.55; thick=0.12; door_w=0.92
    # Two side walls, one exterior-facing wall, and a corridor-side wall with a door gap.
    for side in (-1,1):
        oriented_box(c+n*(side*(room_d/2-thick/2))+Vector((0,0,wh/2+0.12)),t,n,room_w,thick,wh,plaster)
    for side in (-1,1):
        oriented_box(c+t*(side*(room_w/2-thick/2))+Vector((0,0,wh/2+0.12)),n,t,room_d,thick,wh,plaster)
    for side in (-1,1):
        seg=(room_w-door_w)/2
        loc=c-n*(room_d/2-thick/2)+t*(side*(door_w/2+seg/2))+Vector((0,0,wh/2+0.12))
        oriented_box(loc,t,n,seg,thick,wh,plaster)
    oriented_box(c-n*(room_d/2-0.04)+Vector((0,0,1.08)),t,n,door_w-0.08,0.055,2.04,oak)
    if double:
        beds=[-0.82,0.82]
    else: beds=[-0.88]
    for off in beds:
        bc=c+t*off+n*(-0.55)
        oriented_box(bc+Vector((0,0,0.22)),t,n,0.96,2.05,0.30,furniture_mat)
        oriented_box(bc+Vector((0,0,0.43)),t,n,0.90,1.96,0.16,bed_mat)
        oriented_box(bc+n*1.00+Vector((0,0,0.58)),t,n,0.86,0.12,0.86,oak)
        oriented_box(bc+n*0.62+Vector((0,0,0.53)),t,n,0.62,0.36,0.07,bed_mat)
    desks=([0.8,-0.95] if double else [0.88])
    for off in desks:
        dc=c+t*off+n*1.55
        oriented_box(dc+Vector((0,0,0.76)),t,n,1.05,0.58,0.10,oak)
        for dx in (-0.40,0.40): oriented_box(dc+t*dx+Vector((0,0,0.39)),t,n,0.07,0.07,0.74,metal)
        chair=dc-n*0.50
        oriented_box(chair+Vector((0,0,0.48)),t,n,0.48,0.46,0.12,furniture_mat)
        oriented_box(chair-n*0.19+Vector((0,0,0.78)),t,n,0.46,0.10,0.54,oak)
        for dx in (-0.18,0.18):
            for dy in (-0.16,0.16): oriented_box(chair+t*dx+n*dy+Vector((0,0,0.24)),t,n,0.055,0.055,0.48,furniture_mat)
        # A small dark book/reading device provides a clear desk object at preview scale.
        oriented_box(dc+Vector((0,0,0.84)),t,n,0.34,0.25,0.055,accent_mat)
    oriented_box(c+t*1.62+n*(-1.30)+Vector((0,0,0.55)),t,n,0.65,0.72,1.10,furniture_mat)
    return True

# Representative room modules on each residential level; one published single layout
# and one published double layout, with documented beds, desks and dressers.
for fz in floor_levels[1:]:
    room_module(single_center,fz,False)
    room_module(double_center,fz,True)

# First-floor public lobby: mosaic tile, oak casework, wainscot, and limestone fireplace
# are documented in the 2010 A2SO4 renovation summary. Exact room position is schematic.
lobby=(-595.0,-143.0); lobby_t=(1,0); lobby_n=(0,1)
if corners_fit(lobby,lobby_t,lobby_n,3.6,3.6):
    for ix in range(8):
        for iy in range(8):
            x=lobby[0]-1.4+ix*0.4; y=lobby[1]-1.4+iy*0.4
            tile=tile_light if (ix+iy)%2==0 else tile_dark
            oriented_box((x,y,0.24),lobby_t,lobby_n,0.38,0.38,0.045,tile)
    # Oak bookcase with shelves and selected book spines.
    oriented_box((-597.1,-142.0,1.15),lobby_t,lobby_n,2.20,0.28,2.20,oak)
    for zz in (0.35,0.82,1.29,1.76,2.15): oriented_box((-597.1,-141.82,zz),lobby_t,lobby_n,2.12,0.08,0.07,stone)
    for ix in range(9):
        col=accent_mat if ix%3==0 else dark_wood
        oriented_box((-598.0+ix*0.23,-141.76,0.58),lobby_t,lobby_n,0.12,0.07,0.40,col)
    # Limestone fireplace surround, hearth, and oak mantel.
    oriented_box((-592.2,-142.0,0.18),lobby_t,lobby_n,2.0,0.55,0.18,stone)
    oriented_box((-592.2,-142.0,0.95),lobby_t,lobby_n,1.8,0.22,1.48,stone)
    oriented_box((-592.2,-141.84,0.80),lobby_t,lobby_n,0.98,0.08,1.02,metal)
    oriented_box((-592.2,-141.82,1.82),lobby_t,lobby_n,2.12,0.34,0.20,stone)
    oriented_box((-592.2,-141.62,1.99),lobby_t,lobby_n,2.30,0.42,0.18,oak)

# Documented dining-room-to-study conversion, shown only as a generic first-floor room.
study=(-610.0,-152.0)
if corners_fit(study,room_t,room_n,6.5,6.5):
    st=Vector((room_t[0],room_t[1],0)); sn=Vector((room_n[0],room_n[1],0)); sc=Vector((study[0],study[1],0))
    oriented_box(sc+Vector((0,0,0.23)),st,sn,6.2,6.2,0.12,interior_floor)
    for u in (-2.3,-0.8,0.8,2.3):
        for v in (-2.2,2.2):
            oriented_box(sc+st*u+sn*v+Vector((0,0,1.48)),st,sn,0.24,0.24,2.85,stone)
    oriented_box(sc+Vector((0,0,0.88)),st,sn,3.3,1.1,0.14,oak)
    for u in (-1.7,-0.6,0.6,1.7):
        for v in (-0.9,0.9):
            oriented_box(sc+st*u+sn*v+Vector((0,0,0.48)),st,sn,0.48,0.48,0.10,accent_mat)

# The archive describes lobby doors through the aligned Windsor halls. The GIS concavity
# at the courtyard-facing center is the strongest entrance candidate for this footprint.
entry=max((e for e in edge if e[4].y < -0.9 and e[2]>5.5),key=lambda e:e[2],default=None)
# Window bays use repeated facade rhythm. All added pieces remain part of this one building object.
for a,b,L,t,n in edge:
    if L<4.0: continue
    count=max(1,int((L-1.5)//4.0)); spacing=L/(count+1); w=min(float(cfg.get('window_width_m',2.15)),spacing*0.63); pane_h=min(1.55,story*0.55)
    is_entry_edge=entry is not None and a==entry[0] and b==entry[1]
    for floor in range(F):
        z=plinth+story*(floor+0.5)
        if z+pane_h/2>H-0.4: continue
        for bay in range(count):
            p=a.lerp(b,spacing*(bay+1)/L)
            if is_entry_edge and floor==0 and abs((p-(a+b)*0.5).dot(t))<1.8: continue
            c=Vector((p.x,p.y,z))+n*0.07
            box(c,t,n,w*0.74,0.06,pane_h,glass)
            if cfg.get('facade_style')=='tudor':
                # Small stone-framed, multi-light windows suit the documented Tudor brick-and-limestone hall.
                box(c+n*0.055,t,n,0.055,0.075,pane_h*0.94,stone)
                box(c+n*0.058,t,n,w*0.70,0.075,0.055,stone)
            framec=c+n*0.045; fw=0.09
            box(framec+Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone); box(framec-Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone)
            box(framec-t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone); box(framec+t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone)
    for z in [plinth+story*k for k in range(1,F)]: box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.025,t,n,L+0.02,0.10,0.10,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.16))+n*0.05,t,n,L+0.12,0.28,0.32,stone)
# Courtyard-facing central entry inferred from the U-shaped footprint and the archive note
# that Windsor lobby doors align through Duhme, Shealy, Warren and Vawter.
if entry:
    a,b,L,t,n=entry; p=(a+b)*0.5
    # Limestone portal with glazed double doors and a small gabled clay-tile hood.
    box(Vector((p.x,p.y,1.42))+n*0.14,t,n,2.35,0.10,2.84,glass)
    for side in (-1,1):
        box(Vector((p.x,p.y,1.31))+n*0.24+t*(side*0.53),t,n,0.94,0.09,2.55,oak)
        box(Vector((p.x,p.y,1.32))+n*0.30+t*(side*0.53),t,n,0.70,0.025,2.28,glass)
        box(Vector((p.x,p.y,1.15))+n*0.36+t*(side*0.12),t,n,0.035,0.06,0.26,metal)
    box(Vector((p.x,p.y,2.98))+n*0.20,t,n,3.15,0.26,0.24,stone)
    box(Vector((p.x,p.y,1.54))+n*0.21-t*1.27,t,n,0.17,0.27,3.08,stone)
    box(Vector((p.x,p.y,1.54))+n*0.21+t*1.27,t,n,0.17,0.27,3.08,stone)
    front=Vector((p.x,p.y,0))+n*0.31; outer=Vector((p.x,p.y,0))+n*1.48
    gl=front-t*1.78+Vector((0,0,3.16)); gr=front+t*1.78+Vector((0,0,3.16)); gp=front+Vector((0,0,4.50))
    glb=outer-t*1.78+Vector((0,0,3.16)); grb=outer+t*1.78+Vector((0,0,3.16)); gpb=outer+Vector((0,0,4.50))
    triangle((gl,gr,gp),plaster)
    quad((gl,gp,gpb,glb),tile_roof); quad((gp,gr,grb,gpb),tile_roof)
    box(front+Vector((0,0,3.30)),t,n,3.48,0.16,0.14,dark_wood)
    box(front+Vector((0,0,3.70)),t,n,0.14,0.16,0.72,dark_wood)
    for width,depth,z in [(3.65,0.72,0.20),(3.10,0.48,0.40)]:
        box(Vector((p.x,p.y,z))+n*(depth*0.52),t,n,width,depth,0.20,stone)
    # Purdue Archives records a lion holding a shield above the front entrance.
    # The relief is intentionally schematic; its exact sculpted form and entry position are unmeasured.
    # Place the emblem on the projecting entrance gable face, away from upper windows.
    # Archives support the lion/shield motif; this exact position and size are estimated.
    shield_center=Vector((p.x,p.y,4.00))+n*1.62
    shield=[(-0.44,0.29),(0.44,0.29),(0.44,-0.09),(0.0,-0.46),(-0.44,-0.09)]
    back=[]; front=[]
    for tangent_offset,z_offset in shield:
        q=shield_center+t*tangent_offset+Vector((0,0,z_offset))
        back.append(len(verts)); verts.append(tuple(q+n*0.08))
        front.append(len(verts)); verts.append(tuple(q+n*0.18))
    face(tuple(front),stone); face(tuple(reversed(back)),stone)
    for j in range(len(shield)): face((front[j],back[j],back[(j+1)%len(shield)],front[(j+1)%len(shield)]),stone)
    inner=[(-0.30,0.18),(0.30,0.18),(0.30,-0.07),(0.0,-0.33),(-0.30,-0.07)]
    face_ids=[]
    for tangent_offset,z_offset in inner:
        q=shield_center+t*tangent_offset+Vector((0,0,z_offset))+n*0.225
        face_ids.append(len(verts)); verts.append(tuple(q))
    face(tuple(face_ids),accent_mat)
    def relief_ellipsoid(center,w,d,h,material,segments=10,rings=6):
        center=Vector(center); base=len(verts)
        for ri in range(rings+1):
            phi=math.pi*ri/rings
            for si in range(segments):
                theta=2*math.pi*si/segments
                q=center+t*(0.5*w*math.sin(phi)*math.cos(theta))+n*(0.5*d*math.sin(phi)*math.sin(theta))+Vector((0,0,0.5*h*math.cos(phi)))
                verts.append(tuple(q))
        for ri in range(rings):
            for si in range(segments):
                a0=base+ri*segments+si; b0=base+ri*segments+(si+1)%segments
                c0=base+(ri+1)*segments+(si+1)%segments; d0=base+(ri+1)*segments+si
                face((a0,b0,c0,d0),material)
    lc=shield_center+n*0.31
    relief_ellipsoid(lc+Vector((0,0,0.00)),0.32,0.13,0.18,sculpture) # torso
    relief_ellipsoid(lc+t*0.10+Vector((0,0,0.16)),0.19,0.14,0.18,sculpture) # head/mane
    # Four raised legs and a curling tail read as a compact heraldic lion relief.
    for side in (-1,1):
        box(lc+t*(side*0.11)+Vector((0,0,-0.10)),t,n,0.06,0.10,0.20,sculpture)
        box(lc+t*(side*0.11)+Vector((0,0,0.08)),t,n,0.06,0.10,0.17,sculpture)
    box(lc-t*0.18+Vector((0,0,0.06)),t,n,0.055,0.10,0.20,sculpture)
    # Small raised snout/eye accents and a curved tail clarify the heraldic lion profile.
    relief_ellipsoid(lc+t*0.22+Vector((0,0,0.16)),0.10,0.11,0.095,stone,segments=8,rings=4)
    for side in (-1,1):
        relief_ellipsoid(lc+t*(0.13+side*0.045)+Vector((0,0,0.23)),0.035,0.08,0.035,stone,segments=6,rings=3)
    for off,z in [(-0.20,0.08),(-0.25,0.16),(-0.19,0.23)]:
        box(lc+t*off+Vector((0,0,z)),t,n,0.06,0.09,0.08,sculpture)
old=obj.data; old_name=old.name; mesh=bpy.data.meshes.new(old_name+'_detail'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for poly,m in zip(mesh.polygons,mi): poly.material_index=m
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); obj.data=mesh
uv=mesh.uv_layers.new(name='Masonry and roof material mapping')
for poly in mesh.polygons:
    if poly.material_index==wall:
        for loop_index in poly.loop_indices:
            v=mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(poly.normal.x)>abs(poly.normal.y): uv.data[loop_index].uv=(v.y,v.z)
            else: uv.data[loop_index].uv=(v.x,v.z)
    elif poly.material_index==tile_roof:
        longest=None; longest_len=0.0
        ids=[mesh.loops[i].vertex_index for i in poly.loop_indices]
        for j in range(len(ids)):
            p0=mesh.vertices[ids[j]].co; p1=mesh.vertices[ids[(j+1)%len(ids)]].co
            d=Vector((p1.x-p0.x,p1.y-p0.y,0))
            if d.length>longest_len: longest=d.normalized(); longest_len=d.length
        if longest is None: longest=Vector((1,0,0))
        for loop_index in poly.loop_indices:
            v=mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv=(v.x*longest.x+v.y*longest.y,v.z)
mesh.update()
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=old_name; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
result={'asset_id':cfg['asset_id'],'source_fid':attrs['FID'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'official_ring_vertices':len(points),'official_extrusion_attribute':attrs.get('Extrution'),'official_levels_attribute':attrs.get('NUM_LEVELS'),'height_m':H,'height_status':cfg['height_status'],'collection_objects':len(coll.objects)}
print('BUILD_RESULT_JSON='+json.dumps(result))

