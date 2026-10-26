import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
EVIDENCE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'audit', 'frances_m_shealy_residence_hall'))
cfg_path = os.path.join(EVIDENCE, 'build_config.json')
with open(cfg_path, encoding='utf-8-sig') as f: cfg=json.load(f)
blend_path=bpy.data.filepath
obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if not blend_path or obj is None or coll is None or obj not in coll.objects[:]: raise RuntimeError('Target asset structure mismatch')
if len(coll.objects)!=1: raise RuntimeError('Expected exactly one object in assigned exported collection')
with open(os.path.join(EVIDENCE,cfg['source_feature_file']),encoding='utf-8-sig') as f: feature=json.load(f)
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
wall=make_mat(tag+'_Exterior',cfg['wall_color']); stone=make_mat(tag+'_Limestone',cfg['stone_color']); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_mat(tag+'_Roof',cfg['roof_color'],0.88); metal=make_mat(tag+'_Metal',cfg['metal_color'],0.38,0.45); sculpture=make_mat(tag+'_LionRelief',cfg.get('sculpture_color',cfg['stone_color']),0.88)
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
# Sloped roof planes rise from the GIS outline toward a smaller continuous ridge cap.
# The archival image supports pitched slate roof form; exact pitch, ridge path and height are estimates.
roof_center=Vector((sum(p.x for p in points)/len(points),sum(p.y for p in points)/len(points),0))
roof_rise=3.8; roof_inset=0.44
inner_roof=[Vector((roof_center.x+(p.x-roof_center.x)*roof_inset,
                    roof_center.y+(p.y-roof_center.y)*roof_inset,H+roof_rise)) for p in points]
for i,p in enumerate(points):
    q=points[(i+1)%len(points)]; ri=inner_roof[i]; rj=inner_roof[(i+1)%len(points)]
    quad((Vector((p.x,p.y,H)),Vector((q.x,q.y,H)),rj,ri),roof)
for tri in tessellate_polygon([inner_roof]):
    k=len(verts)
    for idx in tri: verts.append(tuple(inner_roof[int(idx)]))
    face((k,k+1,k+2),roof)
entry=max((e for e in edge if e[4].x < -0.7 and e[2]>5),key=lambda e:e[2],default=None)
entry_fraction=0.22
entry_point=entry[0].lerp(entry[1],entry_fraction) if entry else None
# The Purdue archive photograph shows a large Tudor gable over the entrance and
# smaller gabled dormers along the slate roof. Their dimensions remain estimates.
def gable(center, tangent, outward, width, rise, depth, base_z):
    c=Vector(center); t=Vector((tangent.x,tangent.y,0)).normalized(); n=Vector((outward.x,outward.y,0)).normalized()
    left=Vector((c.x-t.x*width/2,c.y-t.y*width/2,base_z)); right=Vector((c.x+t.x*width/2,c.y+t.y*width/2,base_z))
    peak=Vector((c.x,c.y,base_z+rise)); back=Vector((-n.x*depth,-n.y*depth,0))
    back_left=left+back; back_right=right+back; back_peak=peak+back
    # Nudge the gable face just beyond the wall plane so its brick triangle stays visible.
    face((len(verts),len(verts)+1,len(verts)+2),wall); verts.extend((tuple(left+n*0.14),tuple(right+n*0.14),tuple(peak+n*0.14)))
    quad((left,peak,back_peak,back_left),roof); quad((peak,right,back_right,back_peak),roof)
    # A small, source-inspired gable opening; its exact shape and dimensions are schematic.
    box(Vector((c.x,c.y,base_z+rise*0.48))+n*0.08,t,n,min(width*0.25,1.6),0.08,1.35,glass)

if entry:
    a,b,L,t,n=entry; ep=a.lerp(b,entry_fraction)
    gable(ep,t,n,min(17.0,L*0.30),7.5,8.0,H-7.0)
    for fraction in (0.47,0.70,0.90):
        pp=a.lerp(b,fraction)
        gable(pp,t,n,min(6.5,L*0.12),2.4,4.0,H)
    # Two restrained brick chimneys rise above the broad roof mass.
    for fraction in (0.08,0.84):
        roof_point=a.lerp(b,fraction)
        pp=Vector((roof_point.x,roof_point.y,0))-n*3.2
        box(Vector((pp.x,pp.y,H+3.3)),t,n,1.5,1.7,3.4,wall)
        box(Vector((pp.x,pp.y,H+5.1)),t,n,1.85,2.0,0.20,stone)
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
            if is_entry_edge and floor==0 and abs((p-entry_point).dot(t))<1.8: continue
            bay_edge=L>12 and n.x < -0.7 and bay in (max(0,count//3),max(0,2*count//3)) and floor in (0,1,2)
            projection=2.2 if bay_edge else 0.0
            window_depth=0.10+projection
            pane_width=max(w*1.6,2.4) if bay_edge else w*0.74
            c=Vector((p.x,p.y,z))+n*(0.05+projection*0.52)
            box(c,t,n,pane_width,window_depth,pane_h,glass)
            if cfg.get('facade_style')=='tudor':
                # Small stone-framed, multi-light windows suit the documented Tudor brick-and-limestone hall.
                box(c+n*(window_depth*0.5+0.015),t,n,0.055,0.075,pane_h*0.94,stone)
                box(c+n*(window_depth*0.5+0.02),t,n,pane_width*0.82,0.075,0.055,stone)
            framec=c+n*(window_depth*0.5+0.025); fw=0.11
            frame_width=pane_width*(1.10 if bay_edge else 1.0)
            box(framec+Vector((0,0,pane_h/2)),t,n,frame_width,0.14,fw,stone); box(framec-Vector((0,0,pane_h/2)),t,n,frame_width,0.14,fw,stone)
            box(framec-t*(frame_width/2-fw/2),t,n,fw,0.14,pane_h,stone); box(framec+t*(frame_width/2-fw/2),t,n,fw,0.14,pane_h,stone)
    for z in [plinth+story*k for k in range(1,F)]: box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.025,t,n,L+0.02,0.10,0.10,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.16))+n*0.05,t,n,L+0.12,0.28,0.32,stone)
# Small west-facing entry marker, based on orientation rather than an undocumented exact door location.
if entry:
    a,b,L,t,n=entry; p=entry_point
    # Approximate entrance: stone portal, recessed double doors, and two shallow approach steps.
    box(Vector((p.x,p.y,1.65))+n*0.14,t,n,2.00,0.12,3.30,glass)
    box(Vector((p.x,p.y,3.40))+n*0.22,t,n,3.35,0.36,0.38,stone)
    box(Vector((p.x,p.y,1.78))+n*0.24-t*1.22,t,n,0.34,0.38,3.56,stone)
    box(Vector((p.x,p.y,1.78))+n*0.24+t*1.22,t,n,0.34,0.38,3.56,stone)
    box(Vector((p.x,p.y,1.70))+n*0.30,t,n,0.10,0.10,3.22,metal)
    for width,depth,z in [(3.35,0.62,0.20),(2.90,0.42,0.39)]:
        box(Vector((p.x,p.y,z))+n*(depth*0.52),t,n,width,depth,0.20,stone)
    # Purdue Archives records a lion holding a shield above the front entrance.
    # The relief is intentionally schematic; its exact sculpted form and entry position are unmeasured.
    shield_center=Vector((p.x,p.y,4.0))+n*0.24
    shield=[(-0.42,0.42),(0.42,0.42),(0.42,-0.10),(0.0,-0.50),(-0.42,-0.10)]
    back=[]; front=[]
    for tangent_offset,z_offset in shield:
        q=shield_center+t*tangent_offset+Vector((0,0,z_offset))
        back.append(len(verts)); verts.append(tuple(q+n*0.08))
        front.append(len(verts)); verts.append(tuple(q+n*0.18))
    face(tuple(front),stone); face(tuple(reversed(back)),stone)
    for j in range(len(shield)): face((front[j],back[j],back[(j+1)%len(shield)],front[(j+1)%len(shield)]),stone)
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
    lc=shield_center+n*0.205
    relief_ellipsoid(lc+Vector((0,0,0.03)),0.48,0.15,0.27,sculpture) # torso
    relief_ellipsoid(lc+t*0.10+Vector((0,0,0.25)),0.29,0.18,0.28,sculpture) # head/mane
    # Four raised legs and a curling tail read as a compact heraldic lion relief.
    for side in (-1,1):
        box(lc+t*(side*0.15)+Vector((0,0,-0.16)),t,n,0.09,0.16,0.30,sculpture)
        box(lc+t*(side*0.15)+Vector((0,0,0.14)),t,n,0.09,0.16,0.27,sculpture)
    box(lc-t*0.28+Vector((0,0,0.08)),t,n,0.09,0.16,0.35,sculpture)
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


