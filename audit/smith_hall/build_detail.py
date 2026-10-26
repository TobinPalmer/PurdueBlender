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
wall=make_mat(tag+'_Exterior',cfg['wall_color']); stone=make_mat(tag+'_Limestone',cfg['stone_color']); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_mat(tag+'_Roof',cfg['roof_color'],0.88); metal=make_mat(tag+'_Metal',cfg['metal_color'],0.38,0.45)
verts=[]; faces=[]; mi=[]
def face(ids,mat): faces.append(tuple(ids)); mi.append(mat)
def quad(ps,mat):
    k=len(verts); verts.extend(tuple(p) for p in ps); face((k,k+1,k+2,k+3),mat)
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
# Flat structural roof follows the official polygon; no height claim is inferred from the map outline.
for tri in tessellate_polygon([points]):
    k=len(verts)
    for idx in tri:
        p=points[int(idx)]; verts.append((p.x,p.y,H))
    face((k,k+1,k+2),roof)
entry=max((e for e in edge if e[4].x < -0.7 and e[2]>5),key=lambda e:e[2],default=None)
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
            if is_entry_edge and floor==0 and abs((p-(a+b)*0.5).dot(t))<1.9: continue
            c=Vector((p.x,p.y,z))+n*0.07
            box(c,t,n,w*0.74,0.06,pane_h,glass)
            framec=c+n*0.045; fw=0.09
            box(framec+Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone); box(framec-Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone)
            box(framec-t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone); box(framec+t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone)
    for z in [plinth+story*k for k in range(1,F)]: box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.025,t,n,L+0.02,0.10,0.10,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.16))+n*0.05,t,n,L+0.12,0.28,0.32,stone)
# Small west-facing entry marker, based on orientation rather than an undocumented exact door location.
if entry:
    a,b,L,t,n=entry; p=(a+b)*0.5
    # Entrance reference shows double doors below a broad inscribed limestone lintel.
    for offset in (-0.66,0.66): box(Vector((p.x,p.y,1.45))+n*0.13+t*offset,t,n,1.20,0.08,2.86,glass)
    box(Vector((p.x,p.y,1.45))+n*0.20,t,n,0.09,0.16,2.90,stone)
    box(Vector((p.x,p.y,1.51))+n*0.20-t*1.34,t,n,0.16,0.26,3.02,stone)
    box(Vector((p.x,p.y,1.51))+n*0.20+t*1.34,t,n,0.16,0.26,3.02,stone)
    box(Vector((p.x,p.y,3.06))+n*0.21,t,n,3.45,0.28,0.28,stone)
    box(Vector((p.x,p.y,3.52))+n*0.18,t,n,1.70,0.18,0.42,stone)
    for width,depth,z in [(3.7,0.65,0.20),(3.3,0.42,0.41)]: box(Vector((p.x,p.y,z))+n*(depth*0.52),t,n,width,depth,0.20,stone)
old=obj.data; old_name=old.name; mesh=bpy.data.meshes.new(old_name+'_detail'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for poly,m in zip(mesh.polygons,mi): poly.material_index=m
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); obj.data=mesh
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=old_name; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
result={'asset_id':cfg['asset_id'],'source_fid':attrs['FID'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'official_ring_vertices':len(points),'official_extrusion_attribute':attrs.get('Extrution'),'official_levels_attribute':attrs.get('NUM_LEVELS'),'height_m':H,'height_status':cfg['height_status'],'collection_objects':len(coll.objects)}
print('BUILD_RESULT_JSON='+json.dumps(result))

