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
wall=make_mat(tag+'_Exterior',cfg['wall_color']); stone=make_mat(tag+'_Limestone',cfg['stone_color']); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_mat(tag+'_Roof',cfg['roof_color'],0.88); metal=make_mat(tag+'_Metal',cfg['metal_color'],0.38,0.45); shutter=make_mat(tag+'_Shutters',(.12,.10,.085),0.72)
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
# Low roof over the remaining source footprint, with the photo-referenced gable
# modeled over an approximate main block. The rest of the roof plan is unverified.
for tri in tessellate_polygon([points]):
    k=len(verts)
    for idx in tri:
        p=points[int(idx)]; verts.append((p.x,p.y,H))
    face((k,k+1,k+2),roof)
gb=cfg['gable_bounds_uv_m']; u0=float(gb['min_axis']); u1=float(gb['max_axis']); v0=float(gb['min_cross']); v1=float(gb['max_cross']); ridge_v=(v0+v1)/2.0
def inside_uv(x,y):
    inside=False
    for i,(ax,ay) in enumerate(uv):
        bx,by=uv[i-1]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax: inside=not inside
    return inside
if not (u0<u1 and v0<ridge_v<v1 and roof_peak>H): raise RuntimeError('Invalid gable configuration')
for corner in ((u0,v0),(u0,v1),(u1,v0),(u1,v1)):
    if not inside_uv(*corner): raise RuntimeError(f'Estimated gable bounds leave source footprint at {corner}')
def roof_point(u,v,z):
    q=center+axis*u+cross*v
    return Vector((q.x,q.y,z))
r0=roof_point(u0,ridge_v,roof_peak); r1=roof_point(u1,ridge_v,roof_peak)
s0=roof_point(u0,v0,H); s1=roof_point(u1,v0,H); n0=roof_point(u0,v1,H); n1=roof_point(u1,v1,H)
quad((s0,r0,r1,s1),roof); quad((r0,n0,n1,r1),roof)
face_start=len(verts); verts.extend((tuple(s0),tuple(n0),tuple(r0))); face((face_start,face_start+1,face_start+2),wall)
face_start=len(verts); verts.extend((tuple(s1),tuple(r1),tuple(n1))); face((face_start,face_start+1,face_start+2),wall)
# The operator photo shows a corner porch/balcony. Its campus orientation is not
# georeferenced; the established west-side entry placement remains approximate.
entry_index=max((i for i,e in enumerate(edge) if e[4].x < -0.7 and e[2]>5),key=lambda i:edge[i][2],default=None)
entry=edge[entry_index] if entry_index is not None else None
# Window bays use repeated facade rhythm; dark shutters echo the operator photo.
for edge_index,(a,b,L,t,n) in enumerate(edge):
    if L<4.0: continue
    if edge_index==entry_index: continue
    count=max(1,int((L-1.5)//4.0)); spacing=L/(count+1); w=min(float(cfg.get('window_width_m',2.15)),spacing*0.63); pane_h=min(1.55,story*0.55)
    for floor in range(F):
        z=plinth+story*(floor+0.5)
        if z+pane_h/2>H-0.4: continue
        for bay in range(count):
            p=a.lerp(b,spacing*(bay+1)/L); c=Vector((p.x,p.y,z))+n*0.07
            box(c,t,n,w*0.74,0.06,pane_h,glass)
            framec=c+n*0.045; fw=0.09
            box(framec+Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone); box(framec-Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone)
            box(framec-t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone); box(framec+t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone)
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
    door_c=Vector((p.x,p.y,1.4))+n*0.08
    box(door_c,t,n,1.8,0.08,2.65,glass)
    box(Vector((p.x,p.y,2.78))+n*0.12,t,n,2.1,0.14,0.14,stone)
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
