import bpy, bmesh, json, math, os
from mathutils import Vector
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
def make_mat(name,color,rough=0.78,metal=0.0,texture=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); bsdf=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value=(*color,1); bsdf.inputs['Roughness'].default_value=rough; bsdf.inputs['Metallic'].default_value=metal; nt.links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    if texture in ('brick','tile'):
        tc=nt.nodes.new('ShaderNodeTexCoord'); br=nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Vector'].default_value=(0,0,0)
        nt.links.new(tc.outputs['UV'],br.inputs['Vector']); br.inputs['Scale'].default_value=1.0; br.inputs['Brick Width'].default_value=0.52 if texture=='brick' else 0.42; br.inputs['Row Height'].default_value=0.20 if texture=='brick' else 0.22
        br.inputs['Color1'].default_value=(0.29,0.055,0.035,1) if texture=='brick' else (0.11,0.022,0.012,1)
        br.inputs['Color2'].default_value=(0.18,0.03,0.02,1) if texture=='brick' else (0.065,0.012,0.007,1)
        br.inputs['Mortar'].default_value=(0.14,0.09,0.07,1) if texture=='brick' else (0.045,0.012,0.007,1)
        br.inputs['Mortar Size'].default_value=0.012 if texture=='brick' else 0.008
        br.inputs['Mortar Smooth'].default_value=0.004; nt.links.new(br.outputs['Color'],bsdf.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.18; bump.inputs['Distance'].default_value=0.035 if texture=='brick' else 0.018
        nt.links.new(br.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    elif texture=='stone':
        tc=nt.nodes.new('ShaderNodeTexCoord'); noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=38; noise.inputs['Detail'].default_value=2
        nt.links.new(tc.outputs['Generated'],noise.inputs['Vector']); ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=0.2; ramp.color_ramp.elements[0].color=(0.48,0.43,0.35,1)
        ramp.color_ramp.elements[1].position=0.82; ramp.color_ramp.elements[1].color=(0.82,0.77,0.67,1)
        nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.08; bump.inputs['Distance'].default_value=0.012; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    mats.append(m); return len(mats)-1
wall=make_mat(tag+'_Exterior_Running_Bond_Brick',cfg['wall_color'],texture='brick'); stone=make_mat(tag+'_Limestone',cfg['stone_color'],texture='stone'); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_mat(tag+'_Red_Clay_Tile',cfg['roof_color'],0.88,texture='tile'); metal=make_mat(tag+'_Metal',cfg['metal_color'],0.38,0.45); interior=make_mat(tag+'_Interior_Partitions',(0.48,0.45,0.40));
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
    quad((a0,b0,b1,a1),stone)
# Several shallow, intersecting tile wings replace the single broad roof plane.
# The roof junctions follow the irregular campus footprint's dominant axis and are
# architectural estimates: the available exterior image supports multiple roof
# sections but does not provide measured ridge locations.
major=max(edge,key=lambda e:e[2])[3].copy(); minor=Vector((-major.y,major.x,0))
majors=[p.dot(major) for p in points]; minors=[p.dot(minor) for p in points]
m0=min(majors)-0.35; m1=max(majors)+0.35; n0=min(minors)-0.35; n1=max(minors)+0.35; nc=(n0+n1)*0.5
rise=float(cfg.get('roof_rise_m',1.4))
def roof_point(m,n,z): return major*m+minor*n+Vector((0,0,z))
# A thin continuous membrane underneath the intersecting roof wings prevents gaps
# where the estimated sections meet and closes the roof over interior partitions.
k=len(verts); verts.extend((p.x,p.y,H-0.10) for p in points); face(tuple(k+i for i in range(len(points))),roof)
def gable_wing(ma,mb,na,nb,ridge_axis,zbase,wing_rise):
    """Two tiled slopes and end caps for a simple gable roof wing."""
    if ridge_axis=='major':
        mid=(na+nb)*0.5
        e0,e1=roof_point(ma,na,zbase),roof_point(mb,na,zbase)
        e2,e3=roof_point(mb,nb,zbase),roof_point(ma,nb,zbase)
        r0,r1=roof_point(ma,mid,zbase+wing_rise),roof_point(mb,mid,zbase+wing_rise)
        quad((e0,e1,r1,r0),roof); quad((r0,r1,e2,e3),roof)
        quad((e0,e3,r0,r0),wall) if False else None
        # Gable triangles close each exposed end below the roof slopes.
        k=len(verts);verts.extend((tuple(roof_point(ma,na,zbase)),tuple(roof_point(ma,nb,zbase)),tuple(roof_point(ma,mid,zbase+wing_rise))));face((k,k+1,k+2),wall)
        k=len(verts);verts.extend((tuple(roof_point(mb,nb,zbase)),tuple(roof_point(mb,na,zbase)),tuple(roof_point(mb,mid,zbase+wing_rise))));face((k,k+1,k+2),wall)
        box(roof_point((ma+mb)*.5,mid,zbase+wing_rise-.05),major,minor,mb-ma,.30,.12,roof)
        # Eave fascia and short gutters add depth at the roof edge.
        for nn in (na,nb): box(roof_point((ma+mb)*.5,nn,zbase-.04),major,minor,mb-ma,.20,.20,stone)
    else:
        mid=(ma+mb)*.5
        e0,e1=roof_point(ma,na,zbase),roof_point(ma,nb,zbase)
        e2,e3=roof_point(mb,nb,zbase),roof_point(mb,na,zbase)
        r0,r1=roof_point(mid,na,zbase+wing_rise),roof_point(mid,nb,zbase+wing_rise)
        quad((e0,e1,r1,r0),roof); quad((r0,r1,e2,e3),roof)
        k=len(verts);verts.extend((tuple(e0),tuple(e3),tuple(r0)));face((k,k+1,k+2),wall)
        k=len(verts);verts.extend((tuple(e2),tuple(e1),tuple(r1)));face((k,k+1,k+2),wall)
        box(roof_point(mid,(na+nb)*.5,zbase+wing_rise-.05),minor,major,nb-na,.30,.12,roof)
        for mm in (ma,mb): box(roof_point(mm,(na+nb)*.5,zbase-.04),minor,major,nb-na,.20,.20,stone)

# One narrower central gable and two transverse end wings create readable intersections.
# The planes stay shallow compared with steep residential roofs; their slight overlap
# is deliberate because no measured roof plan was available.
wing=max(10.0,min(15.0,(m1-m0)*0.29))
center0=m0+wing*.82; center1=m1-wing*.82
gable_wing(center0,center1,n0+4.5,n1-4.5,'major',H,rise)
gable_wing(m0,center0+1.15,n0+0.25,n1-0.25,'minor',H-.08,rise*.9)
gable_wing(center1-1.15,m1,n0+0.25,n1-0.25,'minor',H-.08,rise*.9)
# Window bays use repeated facade rhythm. All added pieces remain part of this one building object.
entry=max((e for e in edge if e[4].x < -0.7 and e[2]>5),key=lambda e:e[2],default=None)
for a,b,L,t,n in edge:
    count=max(1,int((L-1.0)//2.5)) if L>=4.0 else 0; spacing=L/(count+1) if count else 0; w=min(float(cfg.get('window_width_m',0.95)),spacing*0.62) if count else 0; pane_h=min(1.65,story*0.56)
    is_entry_edge=entry is not None and a==entry[0] and b==entry[1]
    # Build each story as wall panels around genuine window and door openings.
    for floor in range(F):
        z0=plinth+story*floor; z1=min(H,plinth+story*(floor+1)); zc=plinth+story*(floor+0.5)
        if z1<=z0: continue
        holes=[]
        if count and zc+pane_h/2<=H-0.4:
            for bay in range(count):
                sc=spacing*(bay+1); p=Vector((a.x,a.y,0))+t*sc
                if is_entry_edge and floor==0 and abs((p-Vector(((a.x+b.x)*0.5,(a.y+b.y)*0.5,0))).dot(t))<2.0: continue
                holes.append((max(0,sc-w/2),min(L,sc+w/2),max(z0,zc-pane_h/2),min(z1,zc+pane_h/2)))
        if is_entry_edge and floor==0:
            holes.append((max(0,L/2-1.25),min(L,L/2+1.25),z0,min(z1,2.9)))
        xs=sorted(set([0.0,L]+[v for h in holes for v in h[:2]])); zs=sorted(set([z0,z1]+[v for h in holes for v in h[2:]]))
        for si in range(len(xs)-1):
            s0,s1=xs[si],xs[si+1]
            if s1-s0<0.025: continue
            for zi in range(len(zs)-1):
                h0,h1=zs[zi],zs[zi+1]
                if h1-h0<0.025: continue
                sm,zm=(s0+s1)/2,(h0+h1)/2
                if any(h[0]<sm<h[1] and h[2]<zm<h[3] for h in holes): continue
                p0=Vector((a.x,a.y,0))+t*s0+n*0.006; p1=Vector((a.x,a.y,0))+t*s1+n*0.006
                quad((Vector((p0.x,p0.y,h0)),Vector((p1.x,p1.y,h0)),Vector((p1.x,p1.y,h1)),Vector((p0.x,p0.y,h1))),wall)
    if L<4.0: continue
    for floor in range(F):
        z=plinth+story*(floor+0.5)
        if z+pane_h/2>H-0.4: continue
        for bay in range(count):
            p0=a.lerp(b,spacing*(bay+1)/L); p=Vector((p0.x,p0.y,0))
            if is_entry_edge and floor==0 and abs((p-Vector(((a.x+b.x)*0.5,(a.y+b.y)*0.5,0))).dot(t))<2.0: continue
            c=Vector((p.x,p.y,z))+n*0.07
            box(c,t,n,w*0.68,0.06,pane_h,glass)
            framec=c+n*0.045; fw=0.09
            box(framec+Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone); box(framec-Vector((0,0,pane_h/2)),t,n,w,0.14,fw,stone)
            box(framec-t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone); box(framec+t*(w/2-fw/2),t,n,fw,0.14,pane_h,stone)
    for z in [plinth+story*k for k in range(1,F)]: box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.025,t,n,L+0.08,0.14,0.26,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.16))+n*0.05,t,n,L+0.12,0.28,0.32,stone)
# Small west-facing entry marker, based on orientation rather than an undocumented exact door location.
if entry:
    a,b,L,t,n=entry; p=(a+b)*0.5
    # Paired entrance doors, a brick-column portico with limestone bases/capitals, and a historic inscription panel.
    for offset in (-0.68,0.68): box(Vector((p.x,p.y,1.48))+n*0.14+t*offset,t,n,1.24,0.08,2.86,glass)
    box(Vector((p.x,p.y,1.48))+n*0.19,t,n,0.09,0.16,2.82,stone)
    for side in (-1,1):
        c=Vector((p.x,p.y,1.58))+n*1.65+t*(side*2.8)
        box(c,t,n,1.15,0.92,3.05,wall)
        box(Vector((p.x,p.y,0.30))+n*1.65+t*(side*2.8),t,n,1.45,1.12,0.48,stone)
        box(Vector((p.x,p.y,3.04))+n*1.65+t*(side*2.8),t,n,1.42,1.08,0.38,stone)
    # Broad, visibly supported covered entry with a deep fascia and a raised doorway surround.
    box(Vector((p.x,p.y,3.34))+n*1.72,t,n,9.4,5.0,0.42,roof)
    box(Vector((p.x,p.y,3.16))+n*0.22,t,n,4.8,0.24,0.58,stone)
    box(Vector((p.x,p.y,3.57))+n*4.15,t,n,9.7,0.24,0.22,stone)
    # Three broad stone steps lead from grade to the entry landing.
    for step in range(3):
        step_z=0.20+step*0.22
        step_depth=0.65
        step_offset=3.55-step*0.62
        step_center=Vector((p.x,p.y,step_z))+n*step_offset
        box(step_center,t,n,10.2-step*0.30,step_depth,0.24,stone)
# Schematic interior: official 2021 Purdue renovation plans document basement, first, second and third levels.
# Interior partitions simplify offices, open collaboration zones, stairs and service cores; they are schematic
# because the source plans are not dimensionally registered to the GIS polygon.
minM,maxM=min(majors),max(majors); minN,maxN=min(minors),max(minors)
def inside_poly(m,n):
    p=major*m+minor*n; hit=False
    for i,pt in enumerate(points):
        q=points[(i+1)%len(points)]
        if ((pt.y>p.y)!=(q.y>p.y)) and p.x<(q.x-pt.x)*(p.y-pt.y)/(q.y-pt.y+1e-12)+pt.x: hit=not hit
    return hit
def partition_line(axis_const,along_major,z,height=2.65):
    start,end=(minM,maxM) if along_major else (minN,maxN); step=0.45; runs=[]; active=None; samples=[]
    x=start
    while x<=end+step/2:
        m,n=(x,axis_const) if along_major else (axis_const,x); good=inside_poly(m,n)
        if good and active is None: active=x
        if not good and active is not None: runs.append((active,x-step)); active=None
        x+=step
    if active is not None: runs.append((active,end))
    tang=major if along_major else minor; norm=minor if along_major else major
    for a0,b0 in runs:
        if b0-a0<1.1: continue
        mid=(a0+b0)/2; m,n=(mid,axis_const) if along_major else (axis_const,mid); c=major*m+minor*n+Vector((0,0,z+height/2))
        box(c,tang,norm,b0-a0,0.12,height,interior)
# Main circulation and representative room divisions at each documented floor level.
floor_levels=[-2.8,0.18,4.02,7.86]
# Basement through third-floor schematic partitions remain embedded inside the opaque exterior shell.
for level,z in enumerate(floor_levels):
    partition_line((minN+maxN)/2,True,z+0.12,2.75)
    for frac in (0.24,0.48,0.72): partition_line(minM+(maxM-minM)*frac,False,z+0.12,2.65)
    # Compact vertical circulation/service core around the center of the documented plan.
    cx=(minM+maxM)/2; cy=(minN+maxN)/2; cw=min(5.0,(maxM-minM)*0.22); cd=min(4.4,(maxN-minN)*0.28)
    for dx,dy,w,d in ((-cw/2,0,0.14,cd),(cw/2,0,0.14,cd),(0,-cd/2,cw,0.14),(0,cd/2,cw,0.14)):
        c=major*(cx+dx)+minor*(cy+dy)+Vector((0,0,z+1.32)); box(c,major,minor,w,d,2.64,interior)
# Existing shell and all new details remain a single exported building object.
old=obj.data; old_name=old.name; mesh=bpy.data.meshes.new(old_name+'_detail'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for poly,m in zip(mesh.polygons,mi): poly.material_index=m
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); uv=mesh.uv_layers.new(name='FacadeUV');
for poly in mesh.polygons:
    n=poly.normal; axis=0 if abs(n.x)>=abs(n.y) and abs(n.x)>=abs(n.z) else (1 if abs(n.y)>=abs(n.z) else 2)
    for li in poly.loop_indices:
        co=mesh.vertices[mesh.loops[li].vertex_index].co
        uv.data[li].uv=(co.y,co.z) if axis==0 else ((co.x,co.z) if axis==1 else (co.x,co.y))
obj.data=mesh
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=old_name; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
result={'asset_id':cfg['asset_id'],'source_fid':attrs['FID'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'official_ring_vertices':len(points),'official_extrusion_attribute':attrs.get('Extrution'),'official_levels_attribute':attrs.get('NUM_LEVELS'),'height_m':H,'height_status':cfg['height_status'],'collection_objects':len(coll.objects)}
print('BUILD_RESULT_JSON='+json.dumps(result))
