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
        # Fine plaster and asphalt variation keeps large planes from reading as flat gray.
        if name.endswith('_Exterior'):
            nt=m.node_tree; tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=165.0; tex.inputs['Detail'].default_value=2.0
            bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.12; bump.inputs['Distance'].default_value=0.018
            nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
        elif name.endswith('_Roof'):
            nt=m.node_tree; tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=48.0; tex.inputs['Detail'].default_value=3.0
            bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.22; bump.inputs['Distance'].default_value=0.035
            nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    mats.append(m); return len(mats)-1
wall=make_mat(tag+'_Exterior',cfg['wall_color']); stone=make_mat(tag+'_Limestone',cfg['stone_color']); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_mat(tag+'_Roof',cfg['roof_color'],0.88); metal=make_mat(tag+'_Metal',cfg['metal_color'],0.38,0.45); shutter=make_mat(tag+'_Shutters',(.045,.045,.05),0.72); interior=make_mat(tag+'_Interior_Partitions',(.78,.75,.68)); floor_mat=make_mat(tag+'_Interior_Floors',(.44,.38,.29)); vent_mat=make_mat(tag+'_Gable_Vents',(.035,.04,.05),0.48); ac_mat=make_mat(tag+'_Window_AC',(.43,.44,.44),0.55)
verts=[]; faces=[]; mi=[]
def face(ids,mat): faces.append(tuple(ids)); mi.append(mat)
def quad(ps,mat):
    k=len(verts); verts.extend(tuple(p) for p in ps); face((k,k+1,k+2,k+3),mat)
def box(center,tangent,normal,w,d,h,mat):
    c=Vector(center); t=Vector((tangent.x,tangent.y,0)).normalized(); n=Vector((normal.x,normal.y,0)).normalized(); z=Vector((0,0,1)); hw=w/2; hd=d/2; hh=h/2
    offsets=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]; k=len(verts)
    verts.extend(tuple(c+t*a+n*b+z*v) for a,b,v in offsets)
    for f0 in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face(tuple(k+j for j in f0),mat)
H=float(cfg['roof_eaves_m']); roof_peak=float(cfg['ridge_height_m']); F=int(cfg['modeled_floors']); base=0.0; plinth=min(0.72,H*0.09); story=H/max(1,F)
cx=sum(p.x for p in points)/len(points); cy=sum(p.y for p in points)/len(points); center=Vector((cx,cy))
angle=math.radians(float(cfg['gable_axis_angle_degrees'])); axis=Vector((math.cos(angle),math.sin(angle))); cross=Vector((-axis.y,axis.x))
uv=[(float((p-center).dot(axis)),float((p-center).dot(cross))) for p in points]
vmin=min(p[1] for p in uv); vmax=max(p[1] for p in uv); ridge_v=(vmin+vmax)/2.0
edge=[]
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]; delta=b-a; L=delta.length
    if L<0.05: continue
    t=Vector((delta.x/L,delta.y/L,0)); n=Vector((t.y,-t.x,0))*sign; edge.append((a,b,L,t,n))
    a0=Vector((a.x,a.y,base)); b0=Vector((b.x,b.y,base)); a1=Vector((a.x,a.y,plinth)); b1=Vector((b.x,b.y,plinth)); at=Vector((a.x,a.y,H)); bt=Vector((b.x,b.y,H))
    quad((a0,b0,b1,a1),stone); quad((a1,b1,bt,at),wall)
# The owner photograph shows one broad two-storey gable end with a long ridge.
# Split the actual GIS roof outline on the inferred ridge line; the outline stays
# source-accurate while height and gable placement remain explicitly estimated.
gb=cfg['gable_bounds_uv_m']; u0=float(gb['min_axis']); u1=float(gb['max_axis']); v0=float(gb['min_cross']); v1=float(gb['max_cross']); ridge_v=(v0+v1)/2.0
def inside_uv(x,y):
    inside=False
    for i,(ax,ay) in enumerate(uv):
        bx,by=uv[i-1]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax: inside=not inside
    return inside
if not (u0<u1 and v0<ridge_v<v1 and roof_peak>H): raise RuntimeError('Invalid gable configuration')
def roof_point(u,v,z):
    q=center+axis*u+cross*v
    return Vector((q.x,q.y,z))
# Clip the official polygon at the ridge to make two pitched roof planes.
uv_poly=list(uv)
def clip_side(poly,keep_positive):
    out=[]
    for i,cur in enumerate(poly):
        prev=poly[i-1]; cv=cur[1]-ridge_v; pv=prev[1]-ridge_v
        cin=cv>=0 if keep_positive else cv<=0; pin=pv>=0 if keep_positive else pv<=0
        if cin != pin:
            t=(ridge_v-prev[1])/(cur[1]-prev[1]); out.append((prev[0]+t*(cur[0]-prev[0]),ridge_v))
        if cin: out.append(cur)
    return out
def roof_z(v): return H+(roof_peak-H)*max(0.0,1.0-abs(v-ridge_v)/max(abs(v1-v0)/2.0,0.1))
for half in (False,True):
    poly=clip_side(uv_poly,half)
    if len(poly)<3: continue
    # Use UV-space tessellation, then lift each vertex onto the corresponding pitch.
    uv_vectors=[Vector((u,v,0)) for u,v in poly]
    for tri in tessellate_polygon([uv_vectors]):
        ids=[]
        for idx in tri:
            u,v=poly[int(idx)]; p=roof_point(u,v,roof_z(v)); ids.append(len(verts)); verts.append(tuple(p))
        face(ids,roof)
# Gable infill at the two ends (wall-colored triangular faces under the roof).
for end_u in (min(u for u,v in uv),max(u for u,v in uv)):
    lower=[(u,v) for u,v in uv if abs(u-end_u)<0.15]
    if len(lower)>=2:
        left=min(lower,key=lambda q:q[1]); right=max(lower,key=lambda q:q[1]); peak=(end_u,ridge_v)
        ids=[]
        for u,v in (left,right,peak): ids.append(len(verts)); verts.append(tuple(roof_point(u,v,H if (u,v)!=peak else roof_peak)))
        face(ids,wall)
# The operator photograph shows a porch wrapping one end corner; its campus
# orientation is not georeferenced, so retain the best west-side candidate.
entry_index=max((i for i,e in enumerate(edge) if e[4].x < -0.7 and e[2]>5),key=lambda i:edge[i][2],default=None)
entry=edge[entry_index] if entry_index is not None else None
# Window bays use repeated facade rhythm; dark shutters echo the operator photo.
for edge_index,(a,b,L,t,n) in enumerate(edge):
    if L<4.0: continue
    if edge_index==entry_index: continue
    count=3 if L>=10.5 else max(1,int((L-1.5)//4.0)); spacing=L/(count+1); w=min(float(cfg.get('window_width_m',1.65)),spacing*0.63); pane_h=min(1.72,story*0.61)
    for floor in range(F):
        z=plinth+story*(floor+0.5)
        if z+pane_h/2>H-0.1: continue
        for bay in range(count):
            p=a.lerp(b,spacing*(bay+1)/L); c=Vector((p.x,p.y,z))+n*0.07
            box(c,t,n,w*0.74,0.06,pane_h,glass)
            framec=c+n*0.045; fw=0.09
            box(framec+Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone); box(framec-Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone)
            box(framec-t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone); box(framec+t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone)
            # A visible central meeting rail and sill match the operator reference's sash windows.
            box(framec+Vector((0,0,0.02)),t,n,w*0.78,0.09,0.065,stone)
            box(framec-Vector((0,0,pane_h/2+0.055)),t,n,w+0.16,0.22,0.11,stone)
            shutter_w=min(0.28,w*0.22)
            box(framec-t*(w/2+shutter_w/2),t,n,shutter_w,0.12,pane_h,shutter)
            box(framec+t*(w/2+shutter_w/2),t,n,shutter_w,0.12,pane_h,shutter)
    for z in [plinth+story*k for k in range(1,F)]: box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.025,t,n,L+0.02,0.10,0.10,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.16))+n*0.05,t,n,L+0.12,0.28,0.32,stone)
# Approximate two-level covered porch/balcony from the visible operator photograph.
if entry:
    a,b,L,t,n=entry; p=(a+b)*0.5; porch_w=min(float(cfg['porch_width_m']),L*0.6); porch_d=float(cfg['porch_depth_m']); zdeck=story
    box(Vector((p.x,p.y,zdeck))+n*(porch_d*0.42),t,n,porch_w,porch_d,0.18,stone)
    for side in (-1,1):
        c=Vector((p.x,p.y,story/2))+n*(porch_d*0.86)+t*(side*(porch_w/2-0.18))
        box(c,t,n,0.22,0.22,story-0.08,wall)
    rail_z=story+0.62
    box(Vector((p.x,p.y,rail_z))+n*(porch_d*0.86),t,n,porch_w,0.10,0.10,metal)
    box(Vector((p.x,p.y,story+0.12))+n*(porch_d*0.86),t,n,porch_w,0.10,0.10,metal)
    for i in range(1,8):
        box(Vector((p.x,p.y,story+0.38))+n*(porch_d*0.86)+t*(-porch_w/2+porch_w*i/8),t,n,0.07,0.07,0.52,metal)
    for side in (-1,1):
        c=Vector((p.x,p.y,rail_z))+t*(side*(porch_w/2-0.04))+n*(porch_d*0.45)
        box(c,t,n,0.10,porch_d*0.82,0.10,metal)
    # Shallow covered porch canopy, visible in the operator reference.
    box(Vector((p.x,p.y,story+2.55))+n*(porch_d*0.45),t,n,porch_w+0.55,porch_d+0.6,0.16,roof)
    box(Vector((p.x,p.y,story+2.42))+n*(porch_d*0.45),t,n,porch_w+0.65,porch_d+0.7,0.08,stone)
    door_c=Vector((p.x,p.y,1.4))+n*0.08
    box(door_c,t,n,1.8,0.08,2.65,glass)
    box(Vector((p.x,p.y,2.78))+n*0.12,t,n,2.1,0.14,0.14,stone)
# Three small circular attic vents documented in the operator's front-gable photo.
gable_edge=min((e for e in edge if e[2]>10),key=lambda e:abs(abs(math.degrees(math.atan2(e[3].y,e[3].x)))-38.56),default=None)
if gable_edge:
    a,b,L,t,n=gable_edge; mid=(a+b)*0.5; gable_center=Vector((mid.x,mid.y,H))+n*0.09
    # The operator photo shows window AC units on the main gable facade.
    spacing=L/4.0; bay=a.lerp(b,2.0*spacing/L)
    for floor in range(F):
        z=plinth+story*(floor+0.5); c=Vector((bay.x,bay.y,z-0.34))+n*0.19
        box(c,t,n,0.74,0.34,0.46,ac_mat)
        box(c+n*0.19+Vector((0,0,-0.06)),t,n,0.46,0.06,0.07,metal)
    def disk(center,r,depth,mat):
        c=Vector(center); normal=Vector((n.x,n.y,0)).normalized(); side=Vector((t.x,t.y,0)).normalized(); up=Vector((0,0,1)); seg=16; base_i=len(verts)
        for i in range(seg):
            ang=math.tau*i/seg; p=c+side*(r*math.cos(ang))+up*(r*math.sin(ang)); verts.append(tuple(p))
        face(tuple(base_i+i for i in range(seg)),mat)
    for du,dz in ((-0.22,0.65),(0.0,1.0),(0.22,0.65)):
        disk(gable_center+t*du+Vector((0,0,dz)),0.12,0.04,vent_mat)
# Interior floor plates and simple room/hall divisions. The owner documents ten
# rooms, a foyer, study, living/meeting room and dining room; exact partitions
# are not published, so this is a legible but explicitly schematic interpretation.
def uvpoint(u,v,z): return roof_point(u,v,z)
def floor_polygon(z):
    for tri in tessellate_polygon([points]):
        ids=[]
        for idx in tri: p=points[int(idx)]; ids.append(len(verts)); verts.append((p.x,p.y,z))
        face(ids,floor_mat)
floor_polygon(0.18); floor_polygon(story+0.10)
axis3=Vector((axis.x,axis.y,0)); cross3=Vector((cross.x,cross.y,0))
def partition(u0,u1,v,z0,z1,mat=interior):
    if u1-u0<0.15: return
    c=uvpoint((u0+u1)/2,v,(z0+z1)/2); box(c,axis,cross,u1-u0,0.11,z1-z0,mat)
def cross_partition(u,v0_,v1_,z0,z1):
    # Each room opens to the corridor through an illustrative 0.82 m doorway.
    door_c=(-hall_half-0.55) if v1_<=0 else (hall_half+0.55); door_w=0.82
    left_end=min(v1_,door_c-door_w/2); right_start=max(v0_,door_c+door_w/2)
    if left_end-v0_>0.15:
        c=uvpoint(u,(v0_+left_end)/2,(z0+z1)/2); box(c,cross,axis,left_end-v0_,0.11,z1-z0,interior)
    if v1_-right_start>0.15:
        c=uvpoint(u,(right_start+v1_)/2,(z0+z1)/2); box(c,cross,axis,v1_-right_start,0.11,z1-z0,interior)
u_lo=max(min(u for u,v in uv)+0.5,-8.0); u_hi=min(max(u for u,v in uv)-0.5,13.0); v_lo=-7.2; v_hi=7.2; hall_half=0.9
def line_intervals(vertical,coordinate):
    vals=[]
    for i,(u_a,v_a) in enumerate(uv):
        u_b,v_b=uv[(i+1)%len(uv)]
        a,b=(u_a,u_b) if vertical else (v_a,v_b); va,vb=(v_a,v_b) if vertical else (u_a,u_b)
        if (a<=coordinate<b) or (b<=coordinate<a):
            t=(coordinate-a)/(b-a); vals.append(va+t*(vb-va))
    vals.sort(); return [(vals[i]+0.25,vals[i+1]-0.25) for i in range(0,len(vals)-1,2) if vals[i+1]-vals[i]>1.0]
for floor_index in range(F):
    z0=0.3+floor_index*story; z1=min(z0+2.45,(floor_index+1)*story-0.05)
    if z1<=z0: continue
    # central circulation with private-room bays on both sides
    for v in (-hall_half,hall_half):
        for a_u,b_u in line_intervals(False,v): partition(a_u,b_u,v,z0,z1)
    for u in (-5.2,-1.7,1.8,5.3,8.8):
        for a_v,b_v in line_intervals(True,u):
            if a_v < -hall_half: cross_partition(u,a_v,min(b_v,-hall_half),z0,z1)
            if b_v > hall_half: cross_partition(u,max(a_v,hall_half),b_v,z0,z1)
    # Common rooms occupy the end zones on level one; the second floor reads as bedrooms.
# Wide opening bands through the gable-facing rail where a covered porch meets the wall.
old=obj.data; old_name=old.name; mesh=bpy.data.meshes.new(old_name+'_detail'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for poly,m in zip(mesh.polygons,mi): poly.material_index=m
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); obj.data=mesh
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=old_name; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
result={'asset_id':cfg['asset_id'],'source_fid':attrs['FID'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'official_ring_vertices':len(points),'official_extrusion_attribute':attrs.get('Extrution'),'official_levels_attribute':attrs.get('NUM_LEVELS'),'wall_eaves_m':H,'ridge_height_m':roof_peak,'height_status':cfg['height_status'],'collection_objects':len(coll.objects)}
print('BUILD_RESULT_JSON='+json.dumps(result))
