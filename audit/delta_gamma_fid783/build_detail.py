import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

HERE=os.path.dirname(__file__)
with open(os.path.join(HERE,'build_config.json'),encoding='utf-8') as f: cfg=json.load(f)
with open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf-8-sig') as f: feature=json.load(f)['features'][0]
obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if obj is None or coll is None or obj not in coll.objects[:]: raise RuntimeError('Stable asset object/collection missing')
if len(coll.objects)!=1: raise RuntimeError('Expected single-object asset collection')
old=obj.data; obj.data=None
old.materials.clear()
for stale in list(bpy.data.materials):
    if stale.name.startswith('DELTAGAMMA_') and stale.users==0: bpy.data.materials.remove(stale)

raw_ring=feature['geometry']['rings'][0]
if raw_ring[0]==raw_ring[-1]: raw_ring=raw_ring[:-1]
R=6378137.0; lat0=cfg['coordinate_origin']['latitude']; lon0=cfg['coordinate_origin']['longitude']
points=[]
for mx,my in raw_ring:
    lon=mx/R*180.0/math.pi; lat=(2.0*math.atan(math.exp(my/R))-math.pi/2.0)*180.0/math.pi
    points.append(Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0)))
area2=sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))
sign=1.0 if area2>0 else -1.0

materials=[]
def mat(name,color,rough=0.8,metal=0.0):
    m=bpy.data.materials.new('DELTAGAMMA_'+name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    materials.append(m); return len(materials)-1
brick=mat('Interpretive_Red_Brick',cfg['palette']['brick_interpretive'],0.87)
stone=mat('Interpretive_Light_Stone',cfg['palette']['stone_interpretive'],0.8)
glass=mat('Blue_Glass',cfg['palette']['glass_interpretive'],0.22,0.08)
roof=mat('Estimated_Slate_Roof',cfg['palette']['roof_interpretive'],0.85)
wood=mat('Entry_Wood',cfg['palette']['wood_interpretive'],0.7)
dark=mat('Dark_Metal',(.085,.075,.065),0.45,0.55)
trim=mat('Warm_Trim',(.84,.81,.73),0.7)
floor=mat('Interior_Wood_Floor',cfg['palette']['interior_floor'],0.85)
carpet=mat('Schematic_Bordeaux_Carpet',(.37,.065,.10),0.94)
linen=mat('Schematic_Bedding',cfg['palette']['bedding'],0.95)
furn=mat('Schematic_Wood_Furniture',(.30,.16,.08),0.82)
plaster=mat('Schematic_Interior_Plaster',(.79,.72,.61),0.9)

verts=[]; faces=[]; mids=[]
def poly3(ps,mi):
    base=len(verts); verts.extend(tuple(Vector(p)) for p in ps); faces.append(tuple(range(base,base+len(ps)))); mids.append(mi)
def tri(a,b,c,mi): poly3((a,b,c),mi)
def quad(a,b,c,d,mi): poly3((a,b,c,d),mi)
def box(center,t,n,w,d,h,mi):
    c=Vector(center); t=Vector((t.x,t.y,0)).normalized(); n=Vector((n.x,n.y,0)).normalized(); z=Vector((0,0,1))
    offsets=[(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]
    k=len(verts); verts.extend(tuple(c+t*u+n*v+z*q) for u,v,q in offsets)
    for inds in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): faces.append(tuple(k+j for j in inds)); mids.append(mi)
def stroke3(p0,p1,width,depth,normal,mi):
    p0=Vector(p0); p1=Vector(p1); axis=(p1-p0).normalized(); n=Vector(normal).normalized(); side=axis.cross(n).normalized()
    mid=(p0+p1)*0.5; half=(p1-p0).length/2; dw=depth/2; sw=width/2
    corners=[mid+axis*a+n*b+side*c for a,b,c in ((-half,-dw,-sw),(half,-dw,-sw),(half,dw,-sw),(-half,dw,-sw),(-half,-dw,sw),(half,-dw,sw),(half,dw,sw),(-half,dw,sw))]
    k=len(verts); verts.extend(tuple(v) for v in corners)
    for inds in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): faces.append(tuple(k+j for j in inds)); mids.append(mi)
def point_in_poly(x,y):
    inside=False; j=len(points)-1
    for i,pi in enumerate(points):
        pj=points[j]
        if ((pi.y>y)!=(pj.y>y)) and x<(pj.x-pi.x)*(y-pi.y)/(pj.y-pi.y)+pi.x: inside=not inside
        j=i
    return inside
def fits(c,t,n,w,d):
    c=Vector((c.x,c.y,0))
    return all(point_in_poly(*(c+t*a+n*b)[:2]) for a in (-w/2,w/2) for b in (-d/2,d/2))

# Slab plates follow the complete 14-vertex official feature ring. These are
# visual architectural plates, not measured floor plans.
H=float(cfg['estimated_wall_eave_height_m']); story=float(cfg['estimated_story_height_m']); ridge=float(cfg['estimated_roof_ridge_height_m'])
floor_levels=(0.18,story,2*story)
for z in floor_levels:
    for triidx in tessellate_polygon([points]):
        poly3([Vector((points[int(k)].x,points[int(k)].y,z)) for k in triidx],floor)

# Exact source-ring wall base with illustrative two-story facade.
edges=[]; plinth=0.48; window_h=1.65
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]; delta=b-a; L=delta.length
    if L<0.2: continue
    t=Vector((delta.x/L,delta.y/L,0)); n=Vector((t.y,-t.x,0))*sign; edges.append((i,a,b,L,t,n))
    quad(Vector((a.x,a.y,0)),Vector((b.x,b.y,0)),Vector((b.x,b.y,plinth)),Vector((a.x,a.y,plinth)),stone)
    quad(Vector((a.x,a.y,plinth)),Vector((b.x,b.y,plinth)),Vector((b.x,b.y,H)),Vector((a.x,a.y,H)),brick)

# Principal-axis reference for an estimated shallow gable. It follows the plan
# orientation, but the source set contains no measured roof or ridge evidence.
mx=sum(p.x for p in points)/len(points); my=sum(p.y for p in points)/len(points)
cov_xx=sum((p.x-mx)**2 for p in points); cov_xy=sum((p.x-mx)*(p.y-my) for p in points); cov_yy=sum((p.y-my)**2 for p in points)
# The ring contains many short stepped vertices on its east side, which bias a
# vertex-weighted PCA. Use the longer projected axis-aligned dimension as a
# conservative ridge direction; it remains an estimate without a roof plan.
span_x=max(p.x for p in points)-min(p.x for p in points); span_y=max(p.y for p in points)-min(p.y for p in points)
ang=math.pi/2 if span_y>=span_x else 0.0; t=Vector((math.cos(ang),math.sin(ang),0)); n=Vector((-t.y,t.x,0))
proj_t=[(p.x-mx)*t.x+(p.y-my)*t.y for p in points]; proj_n=[(p.x-mx)*n.x+(p.y-my)*n.y for p in points]
length=max(proj_t)-min(proj_t)-0.6; width=max(proj_n)-min(proj_n)-0.6; C=Vector((mx,my,0)); z_eave=H-0.03
e0=C-t*length/2-n*width/2+Vector((0,0,z_eave)); e1=C+t*length/2-n*width/2+Vector((0,0,z_eave))
e2=C+t*length/2+n*width/2+Vector((0,0,z_eave)); e3=C-t*length/2+n*width/2+Vector((0,0,z_eave))
r0=C-t*length/2+Vector((0,0,ridge)); r1=C+t*length/2+Vector((0,0,ridge))
quad(e0,e1,r1,r0,roof); quad(r0,r1,e2,e3,roof)
tri(e0,e3,r0,brick); tri(e1,r1,e2,brick)
for side in (-1,1): box(C+n*(side*width/2)+Vector((0,0,z_eave)),t,n,length+0.35,0.18,0.18,stone)
box(C+Vector((0,0,ridge+0.04)),t,n,length,0.18,0.14,dark)

# Repeated, restrained sash windows. The sources do not resolve count, rhythm,
# material, sill heights, or elevation proportions; all such details are estimates.
entry=min(edges,key=lambda e:((e[1].y+e[2].y)/2,e[0]))
entry_i=entry[0]; entry_mid=(entry[1]+entry[2])*0.5
for idx,a,b,L,t,n in edges:
    if L<5.0: continue
    count=max(1,int(L//5.2)); spacing=L/(count+1); ww=min(1.48,spacing*0.66)
    for fl in range(2):
        z=plinth+story*(fl+0.5); wh=window_h
        for bay in range(count):
            offset=spacing*(bay+1)
            if idx==entry_i and fl==0 and abs(offset-L/2)<2.0: continue
            q=a.lerp(b,offset/L); c=Vector((q.x,q.y,z))+n*0.08
            box(c,t,n,ww,0.09,wh,glass)
            box(c+Vector((0,0,wh/2+0.08)),t,n,ww+0.20,0.16,0.12,trim)
            box(c-Vector((0,0,wh/2+0.08)),t,n,ww+0.24,0.20,0.13,trim)
            for s in (-1,1): box(c+t*(s*(ww/2+0.065)),t,n,0.11,0.16,wh+0.15,trim)
            box(c,t,n,0.045,0.11,wh*0.94,trim)
            box(c,t,n,ww,0.11,0.055,trim)

# Estimated south-facing front entrance and small columned porch; chapter source
# supports a front porch, while exact location and dimensions are unverified.
idx,a,b,L,t,n=entry; p=(a+b)*0.5
door_w=1.8; door_h=2.45
box(Vector((p.x,p.y,door_h/2))+n*0.16,t,n,door_w+0.34,0.10,door_h+0.18,stone)
for s in (-1,1):
    c=Vector((p.x,p.y,door_h/2))+n*0.22+t*(s*0.45)
    box(c,t,n,0.78,0.07,door_h-0.15,wood)
    box(c+n*0.05,t,n,0.58,0.04,door_h-0.4,glass)
    box(c+t*(s*0.30),t,n,0.035,0.05,door_h-0.45,trim)
for s in (-1,1):
    col=Vector((p.x,p.y,1.75))+n*2.15+t*(s*1.85)
    box(col,t,n,0.28,0.30,3.5,trim)
    box(col+Vector((0,0,1.74)),t,n,0.48,0.48,0.16,stone)
box(Vector((p.x,p.y,3.6))+n*2.15,t,n,4.4,3.2,0.25,trim)
for w,d,z in ((4.5,2.9,0.18),(3.8,2.1,0.38),(3.1,1.25,0.58)):
    box(Vector((p.x,p.y,z))+n*2.05,t,n,w,d,0.22,stone)
for k in range(2): box(Vector((p.x,p.y,0.12+k*0.12))+n*(3.25+k*0.38),t,n,3.0+0.28*k,0.5,0.22,stone)

# A simple high-contrast plaque and geometric Delta/Gamma glyphs.
plaque=Vector((p.x,p.y,4.45))+n*0.22
box(plaque,t,n,2.35,0.16,0.72,stone)
N=n.normalized()
def bar(a0,a1,w=0.075): stroke3(a0,a1,w,0.055,N,dark)
base=plaque+n*0.20
# Delta at the left, Gamma at the right.
da=base+t*(-0.82); db=base+t*(-0.28); dc=base+t*(-0.55)+Vector((0,0,0.43))
bar(da,db); bar(da,dc); bar(db,dc)
ga=base+t*0.12+Vector((0,0,-0.22)); gb=base+t*0.12+Vector((0,0,0.22)); gc=gb+t*0.48
bar(ga,gb); bar(gb,gc)

# Schematic interior inserts based on dated member testimony, not a measured
# current plan. Choose compact placements whose four corners fit within the FID ring.
def find_centers(w,d,exclude=()):
    candidates=[]
    x0=min(p.x for p in points); x1=max(p.x for p in points); y0=min(p.y for p in points); y1=max(p.y for p in points)
    step=2.0
    x=x0+w/2
    while x<=x1-w/2:
        y=y0+d/2
        while y<=y1-d/2:
            c=Vector((x,y,0))
            if fits(c,t,n,w,d) and all((c-e).length>min(w,d)*0.8 for e in exclude): candidates.append(c)
            y+=step
        x+=step
    candidates.sort(key=lambda c:(c.x-mx)**2+(c.y-my)**2)
    return candidates
centers=[]
for w,d in ((10.0,8.0),(7.0,6.0),(7.0,6.0)):
    cand=find_centers(w,d,centers)
    if cand: centers.append(cand[0])
def schematic_room(c,z,w,d,kind):
    box(Vector((c.x,c.y,z+0.10)),t,n,w,d,0.14,carpet)
    if kind=='bunks':
        # Four representative twin-level bunk modules, not the chapter's full bed count.
        for u in (-w*0.27,w*0.27):
            for v in (-d*0.28,d*0.28):
                q=Vector((c.x,c.y,z))+t*u+n*v
                for level in (0.32,1.35):
                    box(q+Vector((0,0,level)),t,n,1.05,2.0,0.14,furn)
                    box(q+Vector((0,0,level+0.10)),t,n,0.97,1.88,0.07,linen)
                for s in (-1,1): box(q+t*(s*0.48)+Vector((0,0,1.05)),t,n,0.07,0.07,2.0,dark)
    elif kind=='lounge':
        for u in (-w*0.25,w*0.25):
            q=Vector((c.x,c.y,z))+t*u
            box(q+n*(d*0.22)+Vector((0,0,0.48)),t,n,2.2,0.82,0.55,furn)
            box(q+n*(d*0.22)+Vector((0,0,0.78)),t,n,2.2,0.14,0.55,wood)
        box(Vector((c.x,c.y,z+0.52)),t,n,2.2,1.1,0.12,wood)
    else:
        bed=Vector((c.x,c.y,z))+n*(d*0.20)
        box(bed+Vector((0,0,0.25)),t,n,1.25,2.0,0.30,furn)
        box(bed+Vector((0,0,0.44)),t,n,1.16,1.9,0.11,linen)
        desk=Vector((c.x,c.y,z))-n*(d*0.25)
        box(desk+Vector((0,0,0.78)),t,n,1.45,0.62,0.12,wood)

if centers:
    schematic_room(centers[0],0.22,10.0,8.0,'lounge')
if len(centers)>1: schematic_room(centers[1],story+0.12,7.0,6.0,'bedroom')
if len(centers)>2: schematic_room(centers[2],story+0.12,7.0,6.0,'bunks')

mesh=bpy.data.meshes.new(old.name+'_delta_gamma_detail'); mesh.from_pydata(verts,[],faces)
for m in materials: mesh.materials.append(m)
mesh.update()
for poly,mi in zip(mesh.polygons,mids): poly.material_index=mi
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
obj.data=mesh; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
uv=mesh.uv_layers.new(name='World Scale Architectural Materials')
for poly in mesh.polygons:
    for li in poly.loop_indices:
        v=mesh.vertices[mesh.loops[li].vertex_index].co
        if poly.material_index==brick: uv.data[li].uv=(v.x+v.y,v.z)
        elif poly.material_index==roof: uv.data[li].uv=(v.x*t.x+v.y*t.y,v.z)
mesh.update()
if old.users==0: bpy.data.meshes.remove(old)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
result={'asset_id':cfg['asset_id'],'feature_id':feature['attributes']['FID'],'address':feature['attributes']['ADDRESS'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'gis_ring_vertices':len(points),'official_num_levels':feature['attributes'].get('NUM_LEVELS'),'budget_document_stories':'two stories and a basement','estimated_eave_height_m':H,'estimated_ridge_height_m':ridge,'estimated_roof_axis_degrees_from_east':math.degrees(ang)%180,'schematic_room_centers_xy_m':[[c.x,c.y] for c in centers],'collection_objects':len(coll.objects)}
print('DELTA_GAMMA_BUILD_RESULT='+json.dumps(result))
