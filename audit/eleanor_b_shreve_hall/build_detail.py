import bpy, bmesh, json, math, os, sys
from pathlib import Path
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
wall=make_mat(tag+'_Exterior',cfg['wall_color']); stone=make_mat(tag+'_Limestone',cfg['stone_color']); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_mat(tag+'_Roof',cfg['roof_color'],0.88); metal=make_mat(tag+'_Metal',cfg['metal_color'],0.38,0.45)
interior=make_mat(tag+'_Interior_Paint',(0.73,0.70,0.62),0.9); floor_mat=make_mat(tag+'_Interior_Floor',(0.47,0.43,0.36),0.88); corridor_mat=make_mat(tag+'_Corridor_Tile',(0.36,0.34,0.30),0.84); carpet=make_mat(tag+'_Room_Carpet',(0.35,0.30,0.25),0.94); furniture=make_mat(tag+'_Furniture_Wood',(0.31,0.19,0.11),0.72); linen=make_mat(tag+'_Bedding',(0.74,0.76,0.71),0.86)
verts=[]; faces=[]; mi=[]
def face(ids,mat): faces.append(tuple(ids)); mi.append(mat)
def quad(ps,mat):
    k=len(verts); verts.extend(tuple(p) for p in ps); face((k,k+1,k+2,k+3),mat)
def box(center,tangent,normal,w,d,h,mat):
    c=Vector(center); t=Vector((tangent.x,tangent.y,0)).normalized(); n=Vector((normal.x,normal.y,0)).normalized(); z=Vector((0,0,1)); hw=w/2; hd=d/2; hh=h/2
    offsets=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]; k=len(verts)
    verts.extend(tuple(c+t*a+n*b+z*v) for a,b,v in offsets)
    for f0 in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face(tuple(k+j for j in f0),mat)
H=float(cfg['height_m']); F=int(cfg['modeled_floors']); base=0.0; plinth=min(0.72,H*0.09); story=(H-plinth)/max(1,F)
edge=[]
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]; delta=b-a; L=delta.length
    if L<0.05: continue
    t=Vector((delta.x/L,delta.y/L,0)); n=Vector((t.y,-t.x,0))*sign; edge.append((a,b,L,t,n))
    a0=Vector((a.x,a.y,base)); b0=Vector((b.x,b.y,base)); a1=Vector((a.x,a.y,plinth)); b1=Vector((b.x,b.y,plinth))
    quad((a0,b0,b1,a1),stone)
# Flat structural roof follows the official polygon; no height claim is inferred from the map outline.
for tri in tessellate_polygon([points]):
    k=len(verts)
    for idx in tri:
        p=points[int(idx)]; verts.append((p.x,p.y,H))
    face((k,k+1,k+2),roof)
# Reserve a west-facing opening for the documented entrance. Its campus orientation
# and exact location are approximate because the exterior reference is not georeferenced.
entry_index=max((i for i,e in enumerate(edge) if e[4].x < -0.7 and e[2]>5),key=lambda i:edge[i][2],default=None)
entry=edge[entry_index] if entry_index is not None else None
# Cut the wall panels around the documented entrance and each glazed window bay. This keeps
# glass from sitting over solid brick and lets the schematic internal floors be seen through it.
def wall_panel(a,b,t,n,s0,s1,z0,z1,mat):
    if s1-s0 < 0.015 or z1-z0 < 0.015: return
    quad((Vector((a.x,a.y,z0))+t*s0,Vector((a.x,a.y,z0))+t*s1,
          Vector((a.x,a.y,z1))+t*s1,Vector((a.x,a.y,z1))+t*s0),mat)

openings_by_edge=[]
for edge_index,(a,b,L,t,n) in enumerate(edge):
    count=max(1,int((L-1.5)//4.0)); spacing=L/(count+1); frame_w=min(float(cfg.get('window_width_m',2.15)),spacing*0.63); pane_h=min(1.55,story*0.55)
    edge_openings=[]
    for floor in range(F):
        z0=plinth+story*floor; z1=plinth+story*(floor+1); zc=z0+story*0.5
        for bay in range(count):
            s=spacing*(bay+1); p=a.lerp(b,s/L)
            if floor==0 and edge_index==entry_index and abs(s-L/2)<float(cfg['entry_canopy_width_m'])/2+0.5: continue
            opening_w=frame_w*0.74
            edge_openings.append((floor,s-opening_w/2,s+opening_w/2,zc-pane_h/2,zc+pane_h/2,'window'))
        if floor==0 and edge_index==entry_index:
            door_w=float(cfg['entry_width_m']); door_h=2.65
            edge_openings.append((floor,L/2-door_w/2,L/2+door_w/2,plinth,plinth+door_h,'door'))
    openings_by_edge.append(edge_openings)
    for floor in range(F):
        z0=plinth+story*floor; z1=plinth+story*(floor+1)
        openings=sorted((o for o in edge_openings if o[0]==floor),key=lambda o:o[1])
        cursor=0.0
        for _,s0,s1,oz0,oz1,kind in openings:
            s0=max(cursor,s0); s1=min(L,s1)
            wall_panel(a,b,t,n,cursor,s0,z0,z1,wall)
            wall_panel(a,b,t,n,s0,s1,z0,oz0,wall)
            wall_panel(a,b,t,n,s0,s1,oz1,z1,wall)
            cursor=s1
        wall_panel(a,b,t,n,cursor,L,z0,z1,wall)

# Window bays use repeated facade rhythm; exterior frames surround the new openings.
for edge_index,(a,b,L,t,n) in enumerate(edge):
    if L<4.0: continue
    count=max(1,int((L-1.5)//4.0)); spacing=L/(count+1); w=min(float(cfg.get('window_width_m',2.15)),spacing*0.63); pane_h=min(1.55,story*0.55)
    for floor in range(F):
        z=plinth+story*(floor+0.5)
        if z+pane_h/2>H-0.4: continue
        for bay in range(count):
            p=a.lerp(b,spacing*(bay+1)/L); c=Vector((p.x,p.y,z))+n*0.07
            if floor==0 and edge_index==entry_index and abs((p-(a+b)*0.5).dot(Vector((t.x,t.y))))<float(cfg['entry_canopy_width_m'])/2+0.5: continue
            box(c,t,n,w*0.74,0.06,pane_h,glass)
            framec=c+n*0.045; fw=0.09
            box(framec+Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone); box(framec-Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone)
            box(framec-t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone); box(framec+t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone)
    for z in [plinth+story*k for k in range(1,F)]: box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.025,t,n,L+0.02,0.10,0.10,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.16))+n*0.05,t,n,L+0.12,0.28,0.32,stone)
# Photo-referenced glass entry, broad canopy, columns and raised stair approach.
if entry:
    a,b,L,t,n=entry; p=(a+b)*0.5; entry_w=float(cfg['entry_width_m']); canopy_w=float(cfg['entry_canopy_width_m']); canopy_d=float(cfg['entry_canopy_depth_m'])
    # Double doors and sidelights fill the wall opening; the location remains approximate.
    for side in (-1,1):
        box(Vector((p.x,p.y,1.33))+n*0.12+t*(side*entry_w*0.26),t,n,entry_w*0.48,0.07,2.65,glass)
        box(Vector((p.x,p.y,1.33))+n*0.19+t*(side*entry_w*0.02),t,n,0.055,0.11,2.45,metal)
    box(Vector((p.x,p.y,2.64))+n*0.14,t,n,entry_w,0.12,0.09,metal)
    box(Vector((p.x,p.y,3.65))+n*(canopy_d*0.42),t,n,canopy_w,canopy_d,0.28,stone)
    for side in (-1,1):
        c=Vector((p.x,p.y,1.8))+n*(canopy_d*0.82)+t*(side*(canopy_w/2-0.22))
        box(c,t,n,0.28,0.28,3.6,stone)
    landing_z=0.76
    box(Vector((p.x,p.y,landing_z))+n*0.25,t,n,entry_w+0.6,0.50,0.12,stone)
    for step in range(4):
        step_height=0.18*(4-step); step_distance=0.38+step*0.48
        box(Vector((p.x,p.y,step_height/2))+n*step_distance,t,n,entry_w+0.9,0.52,step_height,stone)

# Schematic but dimension-aware residential interior. Purdue's published standard room is
# 11.5 x 16 ft (3.51 x 4.88 m); this creates a 2.1 m corridor, room dividers at 3.5 m
# intervals, floor plates, stair/elevator cores, and modest furniture. Exact floor layouts
# are not published in the cited references, so these are clearly documented estimates.
minx=min(p.x for p in points); maxx=max(p.x for p in points); miny=min(p.y for p in points); maxy=max(p.y for p in points)
def in_polygon(x,y):
    inside=False
    for i,(ax,ay) in enumerate((p.x,p.y) for p in points):
        bx,by=points[(i+1)%len(points)].x,points[(i+1)%len(points)].y
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax: inside=not inside
    return inside
def intervals_x(y):
    hits=[]
    for i,a in enumerate(points):
        b=points[(i+1)%len(points)]
        if (a.y>y)!=(b.y>y): hits.append(a.x+(y-a.y)*(b.x-a.x)/(b.y-a.y))
    hits.sort(); return [(hits[i],hits[i+1]) for i in range(0,len(hits)-1,2)]
def intervals_y(x):
    hits=[]
    for i,a in enumerate(points):
        b=points[(i+1)%len(points)]
        if (a.x>x)!=(b.x>x): hits.append(a.y+(x-a.x)*(b.y-a.y)/(b.x-a.x))
    hits.sort(); return [(hits[i],hits[i+1]) for i in range(0,len(hits)-1,2)]
def room_wall(x0,y0,x1,y1,z,h=2.35,mat=interior):
    dx=x1-x0; dy=y1-y0; length=math.hypot(dx,dy)
    h=min(h,H-z-0.10)
    if h<0.35: return
    if length<0.25: return
    # Clip candidate partitions to intervals actually inside the official concave footprint.
    steps=max(2,int(length/0.4)); runs=[]; active=None
    for k in range(steps+1):
        f=k/steps; xx=x0+dx*f; yy=y0+dy*f
        ok=in_polygon(xx,yy)
        if ok and active is None: active=(f,f)
        elif ok: active=(active[0],f)
        elif active is not None: runs.append(active); active=None
    if active is not None: runs.append(active)
    for f0,f1 in runs:
        if (f1-f0)*length<0.4: continue
        cx=x0+dx*(f0+f1)*0.5; cy=y0+dy*(f0+f1)*0.5
        tangent=Vector((dx,dy,0)).normalized(); normal=Vector((-tangent.y,tangent.x,0))
        box(Vector((cx,cy,z+h/2)),tangent,normal,(f1-f0)*length,0.10,h,mat)

wing_intervals=intervals_x(miny+5.0)
if len(wing_intervals)<2: wing_intervals=intervals_x(maxy-5.0)
mid_x=(minx+maxx)*0.5; center_bar=intervals_y(mid_x)
center_y=sum(center_bar[0])/2 if center_bar else (miny+maxy)*0.5
hall_w=2.1; module=3.5
for floor in range(F):
    level=plinth+story*floor+0.035
    # Floors fill only the official concave building outline; the outer court gaps remain open.
    for tri in tessellate_polygon([points]):
        k=len(verts)
        for idx in tri:
            pp=points[int(idx)]; verts.append((pp.x,pp.y,level))
        face((k,k+1,k+2),floor_mat)
    ztop=plinth+story*floor+0.12
    for xa,xb in wing_intervals:
        cx=(xa+xb)*0.5
        # Longitudinal resident corridor, paired corridor walls, and regularly sized room bays.
        box(Vector((cx,center_y,level+0.025)),Vector((1,0,0)),Vector((0,1,0)),hall_w,maxy-miny-3.0,0.05,corridor_mat)
        room_centers=[miny+3.0+i*module+module/2 for i in range(max(0,int((maxy-miny-4.0)//module)))]
        for sx in (cx-hall_w/2,cx+hall_w/2):
            cursor=miny+1.5
            for yc in room_centers:
                # Door openings from each corridor into the room modules.
                room_wall(sx,cursor,sx,yc-0.48,ztop,h=2.3)
                cursor=yc+0.48
            room_wall(sx,cursor,sx,maxy-1.5,ztop,h=2.3)
        y=miny+2.0
        while y<maxy-1.0:
            if abs(y-center_y)>hall_w*0.65:
                # Leave a single doorway at each corridor end of the bedroom divider.
                room_wall(xa+0.35,y,cx-hall_w/2-0.55,y,ztop,h=2.3)
                room_wall(cx+hall_w/2+0.55,y,xb-0.35,y,ztop,h=2.3)
            y+=module
        # Two illustrative beds, desks and wardrobes per double room bay. Furniture is low
        # contrast so it reads through the glazing without turning the elevation into clutter.
        for y0 in [miny+3.0+i*module for i in range(max(0,int((maxy-miny-4.0)//module)))]:
            if abs(y0-center_y)<hall_w: continue
            for side in (-1,1):
                depth=abs((xb-xa)-hall_w)/2
                room_cx=cx+side*(hall_w/2+depth/2)
                if not in_polygon(room_cx,y0+module/2): continue
                box(Vector((room_cx,y0+module/2,level+0.018)),Vector((1,0,0)),Vector((0,1,0)),max(0.8,depth-0.28),module-0.18,0.025,carpet)
                for bed_side in (-1,1):
                    bedx=room_cx+side*0.55
                    bedy=y0+module*(0.28 if bed_side<0 else 0.72)
                    box(Vector((bedx,bedy,level+0.34)),Vector((1,0,0)),Vector((0,1,0)),2.0,0.93,0.46,furniture)
                    box(Vector((bedx,bedy,level+0.60)),Vector((1,0,0)),Vector((0,1,0)),1.88,0.83,0.06,linen)
                    deskx=room_cx-side*0.60
                    box(Vector((deskx,bedy,level+0.40)),Vector((1,0,0)),Vector((0,1,0)),1.05,0.55,0.75,furniture)
    # The cross-wing connector has a broad central hall and small rooms along its north/south sides.
    box(Vector((mid_x,center_y,level+0.025)),Vector((1,0,0)),Vector((0,1,0)),maxx-minx-5.0,hall_w,0.05,corridor_mat)
    for sy in (center_y-hall_w/2,center_y+hall_w/2):
        cursor=minx+2.5
        for x in [minx+4.0+i*module for i in range(max(0,int((maxx-minx-8.0)//module)))]:
            if any(a0-0.5<x<b0+0.5 for a0,b0 in wing_intervals): continue
            room_wall(cursor,sy,x-0.48,sy,ztop,h=2.3)
            cursor=x+0.48
        room_wall(cursor,sy,maxx-2.5,sy,ztop,h=2.3)
    for x in [minx+4.0+i*module for i in range(max(0,int((maxx-minx-8.0)//module)))]:
        if any(a0-0.5<x<b0+0.5 for a0,b0 in wing_intervals): continue
        room_wall(x,miny+0.5,x,center_y-hall_w/2-0.55,ztop,h=2.3)
        room_wall(x,center_y+hall_w/2+0.55,x,maxy-0.5,ztop,h=2.3)
        for side, ymid in ((-1, (miny+center_y-hall_w/2)/2), (1, (center_y+hall_w/2+maxy)/2)):
            if in_polygon(x+module/2,ymid):
                box(Vector((x+module/2,ymid,level+0.018)),Vector((1,0,0)),Vector((0,1,0)),module-0.18,max(0.8,abs(ymid-(center_y+side*hall_w/2))-0.25),0.025,carpet)
    # Central stair/elevator core, modeled as a compact service volume on each upper floor.
    core=(mid_x+4.0,center_y+5.0)
    if in_polygon(*core):
        for sx in (-1,1): room_wall(core[0]+sx*1.2,core[1]-1.4,core[0]+sx*1.2,core[1]+1.4,ztop,h=2.5)
        for sy in (-1,1): room_wall(core[0]-1.2,core[1]+sy*1.4,core[0]+1.2,core[1]+sy*1.4,ztop,h=2.5)

# Small amenity cues from Purdue's current Shreve description: a front-desk counter,
# study/recreation furniture, and a game table. Their exact rooms are not geolocated.
if entry:
    a,b,L,t,n=entry; p=(a+b)*0.5; desk_xy=Vector((p.x,p.y,0))-Vector((n.x,n.y,0))*3.4
    if in_polygon(desk_xy.x,desk_xy.y):
        box(Vector((desk_xy.x,desk_xy.y,plinth+0.52)),t,n,2.5,0.72,1.04,furniture)
        box(Vector((desk_xy.x,desk_xy.y,plinth+1.08)),t,n,2.65,0.82,0.12,stone)
        for side in (-1,1):
            box(Vector((desk_xy.x,desk_xy.y,plinth+0.38))+t*(side*2.2),t,n,1.6,0.72,0.74,furniture)
lounge_level=plinth+story+0.035
lounge_xy=(mid_x-8.0,center_y+7.0)
if in_polygon(*lounge_xy):
    tx,ty=lounge_xy
    box(Vector((tx,ty,lounge_level+0.78)),Vector((1,0,0)),Vector((0,1,0)),2.74,1.525,0.09,furniture)
    box(Vector((tx,ty,lounge_level+0.84)),Vector((1,0,0)),Vector((0,1,0)),0.035,1.5,0.10,metal)
    for dx in (-1.15,1.15):
        for dy in (-0.55,0.55):
            box(Vector((tx+dx,ty+dy,lounge_level+0.39)),Vector((1,0,0)),Vector((0,1,0)),0.08,0.08,0.78,furniture)
old=obj.data; old_name=old.name; mesh=bpy.data.meshes.new(old_name+'_detail'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for poly,m in zip(mesh.polygons,mi): poly.material_index=m
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); obj.data=mesh
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=old_name; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
# Reuse the repository's CC0 Poly Haven red-brick maps at their published 1.4 m tile size.
# All texture paths are saved relative to this library file so the asset remains portable.
repo_root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(repo_root))
from materials import pbr_upgrade
pbr_upgrade.metric_uv(obj,tile_m=1.4)
pbr_upgrade.upgrade_brick(mats[wall],tint=(0.65,0.30,0.18,1.0),tile_m=1.4,texture_set='red_brick')
brick_hsv=next(n for n in mats[wall].node_tree.nodes if n.type=='HUE_SAT')
brick_hsv.inputs['Saturation'].default_value=0.95
brick_hsv.inputs['Value'].default_value=0.86
pbr_upgrade.upgrade_surface(mats[stone],'stone',color=(*cfg['stone_color'],1.0))
pbr_upgrade.upgrade_surface(mats[glass],'glass')
if hasattr(mats[glass],'surface_render_method'): mats[glass].surface_render_method='BLENDED'
glass_bsdf=next(n for n in mats[glass].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
glass_bsdf.inputs['Alpha'].default_value=0.38
pbr_upgrade.upgrade_surface(mats[metal],'metal')
pbr_upgrade.pack_textures()
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
result={'asset_id':cfg['asset_id'],'source_fid':attrs['FID'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'official_ring_vertices':len(points),'official_extrusion_attribute':attrs.get('Extrution'),'official_levels_attribute':attrs.get('NUM_LEVELS'),'height_m':H,'height_status':cfg['height_status'],'interior_floor_plates':F,'interior_levels':F,'room_module_m':module,'room_dimensions_reference_m':[3.5052,4.8768],'material_sources':['https://polyhaven.com/a/red_brick'],'collection_objects':len(coll.objects)}
print('BUILD_RESULT_JSON='+json.dumps(result))
