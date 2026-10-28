import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

HERE=os.path.dirname(__file__)
with open(os.path.join(HERE,'build_config.json'),encoding='utf8') as f: cfg=json.load(f)
with open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf8') as f: feature=json.load(f)['features'][0]
obj=bpy.data.objects.get(cfg['object_name']); coll=bpy.data.collections.get(cfg['collection_name'])
if not obj or not coll or obj not in coll.objects[:]: raise RuntimeError('Manifest asset structure mismatch')
if len(coll.objects)!=1: raise RuntimeError('Expected stable single-object export collection')
old=obj.data
obj.data=None
old.materials.clear()
for stale in list(bpy.data.materials):
    if stale.name.startswith('ALPHAPHI_') and stale.users==0:
        bpy.data.materials.remove(stale)
attrs=feature['attributes']; ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
# Source feature geometry is Web Mercator (WKID 102100/latestWkid 3857).
R=6378137.0; lat0=cfg['coordinate_origin']['latitude']; lon0=cfg['coordinate_origin']['longitude']
points=[]
for mx,my in ring:
    lon=(mx/R)*180.0/math.pi; lat=(2.0*math.atan(math.exp(my/R))-math.pi/2.0)*180.0/math.pi
    points.append(Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0,0)))
area2=sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))
sign=1.0 if area2>0 else -1.0

materials=[]
def mat(name,color,rough=0.8,metal=0.0):
    m=bpy.data.materials.new('ALPHAPHI_'+name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    materials.append(m); return len(materials)-1
def brick_mat():
    m=bpy.data.materials.new('ALPHAPHI_Weathered_Red_Brick'); m.diffuse_color=(*cfg['palette']['brick'],1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); ns=nt.nodes; links=nt.links
    out=ns.new('ShaderNodeOutputMaterial'); bs=ns.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value=0.88
    tex=ns.new('ShaderNodeTexCoord'); brick=ns.new('ShaderNodeTexBrick')
    brick.inputs['Color1'].default_value=(0.34,0.085,0.04,1); brick.inputs['Color2'].default_value=(0.22,0.045,0.022,1); brick.inputs['Mortar'].default_value=(0.56,0.48,0.38,1)
    brick.inputs['Brick Width'].default_value=0.45; brick.inputs['Row Height'].default_value=0.19; brick.inputs['Mortar Size'].default_value=0.012
    bump=ns.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.16; bump.inputs['Distance'].default_value=0.009
    links.new(tex.outputs['UV'],brick.inputs['Vector']); links.new(brick.outputs['Color'],bs.inputs['Base Color']); links.new(brick.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal']); links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    materials.append(m); return len(materials)-1
def roof_mat():
    m=bpy.data.materials.new('ALPHAPHI_Mottled_Clay_Composite_Shingle'); m.diffuse_color=(*cfg['palette']['roof'],1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); ns=nt.nodes; links=nt.links
    out=ns.new('ShaderNodeOutputMaterial'); bs=ns.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value=0.86
    tex=ns.new('ShaderNodeTexCoord'); brick=ns.new('ShaderNodeTexBrick')
    brick.inputs['Color1'].default_value=(0.18,0.055,0.026,1); brick.inputs['Color2'].default_value=(0.30,0.105,0.05,1); brick.inputs['Mortar'].default_value=(0.10,0.04,0.025,1)
    brick.inputs['Brick Width'].default_value=0.5; brick.inputs['Row Height'].default_value=0.22; brick.inputs['Mortar Size'].default_value=0.018
    bump=ns.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.22; bump.inputs['Distance'].default_value=0.018
    links.new(tex.outputs['UV'],brick.inputs['Vector']); links.new(brick.outputs['Color'],bs.inputs['Base Color']); links.new(brick.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal']); links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    materials.append(m); return len(materials)-1
brick=brick_mat(); stone=mat('Limestone',(0.73,0.66,0.53)); glass=mat('Blue_Glass',cfg['palette']['glass'],0.24,0.06); roof=roof_mat(); copper=mat('Aged_Copper',(0.30,0.17,0.085),0.4,0.55); wood=mat('Entry_Oak',cfg['palette']['wood'],0.65); darkwood=mat('Dark_Wood',(0.09,0.035,0.018),0.68)
plaster=mat('Interior_Warm_Plaster',(0.76,0.69,0.58)); floor=mat('Interior_Oak_Floor',(0.36,0.20,0.09),0.83); carpet=mat('Interior_Bordeaux_Carpet',(0.24,0.045,0.075),0.95); linen=mat('Bed_Linen',(0.85,0.79,0.65),0.94); furniture=mat('Interior_Furniture',(0.27,0.12,0.045),0.75); accent=mat('Alpha_Phi_Bordeaux',(0.32,0.015,0.055),0.72); foliage=mat('Shrub_Green',(0.08,0.23,0.09),0.94)
verts=[]; faces=[]; mids=[]
def face(ids,mi): faces.append(tuple(ids)); mids.append(mi)
def poly3(points3,mi):
    k=len(verts); verts.extend(tuple(v) for v in points3); face(tuple(range(k,k+len(points3))),mi)
def tri(a,b,c,mi): poly3((a,b,c),mi)
def quad(a,b,c,d,mi): poly3((a,b,c,d),mi)
def box(center,t,n,w,d,h,mi):
    c=Vector(center); t=Vector((t.x,t.y,0)).normalized(); n=Vector((n.x,n.y,0)).normalized(); z=Vector((0,0,1))
    offsets=[(-w/2,-d/2,-h/2),(w/2,-d/2,-h/2),(w/2,d/2,-h/2),(-w/2,d/2,-h/2),(-w/2,-d/2,h/2),(w/2,-d/2,h/2),(w/2,d/2,h/2),(-w/2,d/2,h/2)]
    k=len(verts); verts.extend(tuple(c+t*u+n*v+z*q) for u,v,q in offsets)
    for inds in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face(tuple(k+j for j in inds),mi)
def point_in_poly(x,y):
    inside=False; j=len(points)-1
    for i,pi in enumerate(points):
        pj=points[j]
        if ((pi.y>y)!=(pj.y>y)) and x<(pj.x-pi.x)*(y-pi.y)/(pj.y-pi.y)+pi.x: inside=not inside
        j=i
    return inside
def fits(c,t,n,w,d):
    c3=Vector((c.x,c.y,0))
    return all(point_in_poly(*(c3+Vector((t.x,t.y,0))*a+Vector((n.x,n.y,0))*b)[:2]) for a in (-w/2,w/2) for b in (-d/2,d/2))
edges=[]; base=0.0; H=float(cfg['estimated_wall_height_m']); story=H/2.0; plinth=0.58
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]; delta=b-a; L=delta.length
    if L<0.2: continue
    t=Vector((delta.x/L,delta.y/L,0)); n=Vector((t.y,-t.x,0))*sign; edges.append((i,a,b,L,t,n))
    quad(Vector((a.x,a.y,0)),Vector((b.x,b.y,0)),Vector((b.x,b.y,plinth)),Vector((a.x,a.y,plinth)),stone)
    quad(Vector((a.x,a.y,plinth)),Vector((b.x,b.y,plinth)),Vector((b.x,b.y,H)),Vector((a.x,a.y,H)),brick)

# Floor plates and interior cutaway modules. Exact room placement is not published;
# these are illustrative room types, not a claimed as-built floor plan.
floor_levels=(0.18,story+0.12,H-0.12)
for z in floor_levels:
    for triidx in tessellate_polygon([points]):
        p=[Vector((points[int(k)].x,points[int(k)].y,z)) for k in triidx]; poly3(p,floor)
tc=Vector((cfg['principal_axis_xy'][0],cfg['principal_axis_xy'][1],0)).normalized(); nc=Vector((-tc.y,tc.x,0))
center=Vector((cfg['interior_module_center_xy'][0],cfg['interior_module_center_xy'][1],0))
def interior_room(c,z,double=False):
    w=5.0 if not double else 6.0; d=5.6; t=tc; n=nc
    if not fits(c,t,n,w,d): return False
    box((c.x,c.y,z+0.10),t,n,w-0.15,d-0.15,0.12,carpet)
    # Three room partitions and a doorway opening on the hall side.
    wallh=2.65; thick=0.12
    for s in (-1,1): box(Vector((c.x,c.y,z))+n*(s*(d/2-thick/2))+Vector((0,0,wallh/2+0.12)),t,n,w,thick,wallh,plaster)
    for s in (-1,1): box(Vector((c.x,c.y,z))+t*(s*(w/2-thick/2))+Vector((0,0,wallh/2+0.12)),n,t,d,thick,wallh,plaster)
    # Bed(s), linen, writing desk, chair, dresser; generic furnishings based on common residence use.
    beds=(-0.95,0.95) if double else (-0.55,)
    for off in beds:
        bc=Vector((c.x,c.y,z))+t*off+n*0.55
        box(bc+Vector((0,0,0.24)),t,n,1.15,2.15,0.30,furniture)
        box(bc+Vector((0,0,0.44)),t,n,1.05,2.02,0.16,linen)
        box(bc+n*0.94+Vector((0,0,0.65)),t,n,0.98,0.13,0.86,wood)
        box(bc+n*0.60+Vector((0,0,0.54)),t,n,0.65,0.36,0.07,linen)
    dc=Vector((c.x,c.y,z))-n*1.70
    box(dc+Vector((0,0,0.78)),t,n,1.4,0.68,0.11,wood)
    for u in (-0.55,0.55): box(dc+t*u+Vector((0,0,0.38)),t,n,0.08,0.08,0.70,copper)
    chair=dc+n*0.56
    box(chair+Vector((0,0,0.48)),t,n,0.48,0.46,0.12,furniture)
    box(chair-n*0.18+Vector((0,0,0.77)),t,n,0.46,0.1,0.52,wood)
    box(Vector((c.x,c.y,z))+t*1.75+n*1.75+Vector((0,0,0.58)),t,n,0.74,0.75,1.16,furniture)
    return True
interior_room(center+tc*(-4.0),story+0.18,False)
interior_room(center+tc*(5.0),story+0.18,True)
# Schematic public lounge: carpet island, sofas, coffee table, bookshelf, and dining table.
lounge=center+tc*(-1.0)+nc*(5.5)
if fits(lounge,tc,nc,10.0,8.0):
    box(Vector((lounge.x,lounge.y,0.16)),tc,nc,9.5,7.5,0.14,carpet)
    for off in (-2.7,2.7):
        sofa=Vector((lounge.x,lounge.y,0))+tc*off+nc*1.0
        box(sofa+Vector((0,0,0.45)),tc,nc,2.7,0.82,0.62,furniture)
        box(sofa+nc*0.34+Vector((0,0,0.82)),tc,nc,2.7,0.18,0.72,wood)
    box(Vector((lounge.x,lounge.y,0.52))+tc*0.0-nc*0.15,tc,nc,2.4,1.2,0.15,wood)
    # dining table and compact chairs
    dining=Vector((lounge.x,lounge.y,0))+tc*0.0+nc*(-2.25)
    box(dining+Vector((0,0,0.78)),tc,nc,3.0,1.25,0.14,wood)
    for u in (-1.1,-0.4,0.4,1.1):
        chair=dining+tc*u+nc*(-0.85)
        box(chair+Vector((0,0,0.48)),tc,nc,0.42,0.42,0.12,furniture)
        box(chair+nc*(-0.18)+Vector((0,0,0.76)),tc,nc,0.42,0.10,0.48,wood)

# Courtyard/street entry candidate: edge 13 is a recessed long wall segment; exact
# entrance position is inferred from the plan and the labeled Purdue house illustration.
ei=int(cfg['entry_edge_index_estimated']); entry=next((e for e in edges if e[0]==ei),max(edges,key=lambda e:e[3]))
idx,a,b,L,t,n=entry; p=(a+b)*0.5
door_w=2.0; door_h=2.55; zc=door_h/2+0.08
box(Vector((p.x,p.y,zc))+n*0.12,t,n,door_w+0.32,0.12,door_h+0.16,stone)
for s in (-1,1):
    box(Vector((p.x,p.y,door_h/2))+n*0.20+t*(s*0.49),t,n,0.92,0.08,door_h-0.16,wood)
    box(Vector((p.x,p.y,door_h/2))+n*0.255+t*(s*0.49),t,n,0.70,0.025,door_h-0.42,glass)
    box(Vector((p.x,p.y,1.05))+n*0.30+t*(s*0.09),t,n,0.035,0.06,0.25,copper)
box(Vector((p.x,p.y,door_h+0.17))+n*0.20,t,n,2.55,0.28,0.26,stone)
for s in (-1,1): box(Vector((p.x,p.y,door_h/2))+n*0.2+t*(s*1.20),t,n,0.22,0.30,door_h+0.2,stone)
# Covered porch, squared columns, pediment and three broad stone steps.
front=Vector((p.x,p.y,0))+n*0.45; depth=2.0
for s in (-1,1):
    col=front+t*(s*1.75)+n*depth
    box(col+Vector((0,0,1.58)),t,n,0.30,0.30,3.16,stone)
    box(col+Vector((0,0,0.18)),t,n,0.54,0.52,0.32,stone)
    box(col+Vector((0,0,3.12)),t,n,0.58,0.52,0.30,stone)
box(front+n*depth+Vector((0,0,3.28)),t,n,4.15,3.05,0.24,stone)
tri(front-t*2.10+n*0.45+Vector((0,0,3.40)),front+t*2.10+n*0.45+Vector((0,0,3.40)),front+n*(depth+0.50)+Vector((0,0,4.55)),brick)
for w,d,z in ((4.4,2.7,0.18),(3.8,1.8,0.38),(3.0,1.1,0.58)):
    box(Vector((p.x,p.y,z))+n*(depth*0.70),t,n,w,d,0.20,stone)
for step in range(3):
    box(Vector((p.x,p.y,0.12+step*0.13))+n*(depth+0.65+step*0.34),t,n,3.15+step*0.28,0.45,0.24,stone)

# Plaque geometry and raised Alpha/Phi strokes above the doorway; Greek letters are graphic signage.
plaque=Vector((p.x,p.y,4.35))+n*0.24
box(plaque,t,n,2.1,0.16,0.72,stone)
def front_bar(u,z,w,h,material,depth=0.18): box(plaque+t*u+Vector((0,0,z-4.35))+n*depth,t,n,w,0.065,h,material)
# Alpha: two uprights and crossbar; Phi: oval ring and central staff.
front_bar(-0.54,4.39,0.11,0.46,darkwood); front_bar(-0.12,4.39,0.11,0.46,darkwood); front_bar(-0.33,4.36,0.42,0.085,darkwood)
for j in range(18):
    ang=2*math.pi*j/18; ang2=2*math.pi*(j+1)/18
    q0=plaque+t*(0.40+0.19*math.cos(ang))+Vector((0,0,0.05+0.23*math.sin(ang)))+n*0.19
    q1=plaque+t*(0.40+0.19*math.cos(ang2))+Vector((0,0,0.05+0.23*math.sin(ang2)))+n*0.19
    q2=plaque+t*(0.40+0.11*math.cos(ang2))+Vector((0,0,0.05+0.15*math.sin(ang2)))+n*0.19
    q3=plaque+t*(0.40+0.11*math.cos(ang))+Vector((0,0,0.05+0.15*math.sin(ang)))+n*0.19
    quad(q0,q1,q2,q3,darkwood)
box(plaque+t*0.40+Vector((0,0,0.05))+n*0.19,t,n,0.07,0.07,0.52,darkwood)

# Repeated facade bays. Window rhythm, trim and colors are modeled as plausible design
# details from the labeled drawing, not measured elevations.
for idx,a,b,L,t,n in edges:
    if L<6.0: continue
    count=max(1,int(L//4.2)); spacing=L/(count+1); ww=min(1.55,spacing*0.68)
    for fl in range(2):
        z=plinth+story*(fl+0.5); wh=1.55
        for bay in range(count):
            offset=spacing*(bay+1)
            if idx==ei and fl==0 and abs(offset-L/2)<2.0: continue
            q=a.lerp(b,offset/L); c=Vector((q.x,q.y,z))+n*0.075
            box(c,t,n,ww,0.075,wh,glass)
            # limestone surround, sill, header, vertical jambs and central sash.
            box(c+Vector((0,0,wh/2+0.095)),t,n,ww+0.24,0.18,0.14,stone)
            box(c-Vector((0,0,wh/2+0.095)),t,n,ww+0.34,0.24,0.16,stone)
            for s in (-1,1): box(c+t*(s*(ww/2+0.08)),t,n,0.14,0.18,wh+0.18,stone)
            box(c,t,n,0.055,0.10,wh*0.94,stone); box(c,t,n,ww,0.10,0.06,stone)
            # Dark shutters add scale and an identifiable domestic/chapter-house rhythm.
            for s in (-1,1): box(c+t*(s*(ww/2+0.25)),t,n,0.18,0.08,wh*0.86,darkwood)
    # Limestone floor belt and broad eave/string trim.
    for zz in (story,): box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,zz))+n*0.03,t,n,L,0.11,0.12,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.08))+n*0.07,t,n,L+0.12,0.20,0.22,stone)

# Main gable roof aligned with the long axis of the GIS plan, with clay/shingle texture.
C=Vector((sum(q.x for q in points[:-1])/len(points[:-1]),sum(q.y for q in points[:-1])/len(points[:-1]),0)); t=tc; n=nc
roof_eave=H-0.08; ridge=cfg['estimated_roof_ridge_height_m']; length=28.4; width=23.5
e0=C-t*length/2-n*width/2+Vector((0,0,roof_eave)); e1=C+t*length/2-n*width/2+Vector((0,0,roof_eave))
e2=C+t*length/2+n*width/2+Vector((0,0,roof_eave)); e3=C-t*length/2+n*width/2+Vector((0,0,roof_eave))
r0=C-t*length/2+Vector((0,0,ridge)); r1=C+t*length/2+Vector((0,0,ridge))
quad(e0,e1,r1,r0,roof); quad(r0,r1,e2,e3,roof)
tri(e0,e3,r0,brick); tri(e1,r1,e2,brick)
# Rake boards, ridge cap and eaves; entry porch canopy remains distinct below the main roof.
box(C+Vector((0,0,ridge+0.04)),t,n,length,0.20,0.16,copper)
for side in (-1,1): box(C+n*(side*width/2)+Vector((0,0,roof_eave)),t,n,length+0.35,0.18,0.18,copper)
for end in (-1,1):
    q=C+t*(end*length/2)+Vector((0,0,roof_eave+0.12))
    box(q,n,t,width*0.92,0.16,0.16,stone)
# One restrained chimney on the rear roof slope; estimated position and scale.
chimney=C+t*7.0+n*4.5+Vector((0,0,8.7))
box(chimney,t,n,1.1,1.0,2.0,brick); box(chimney+Vector((0,0,1.07)),t,n,1.32,1.20,0.18,stone)

# Compact native entry lanterns and foundation shrubs (symbolic, not landscape survey data).
for s in (-1,1):
    q=Vector((p.x,p.y,2.45))+t*(s*2.35)+n*0.28
    box(q,t,n,0.25,0.18,0.54,copper); box(q+Vector((0,0,0.30)),t,n,0.31,0.22,0.18,stone)
    # Low planter and rounded shrub foliage mesh; kept as simple building-entry context.
    box(Vector((p.x,p.y,0.24))+t*(s*3.0)+n*1.55,t,n,1.5,0.75,0.48,stone)
    for j in range(3):
        v=Vector((p.x,p.y,0))+t*(s*3.0+(j-1)*0.28)+n*1.55+Vector((0,0,0.82+(j%2)*0.12))
        # faceted shrub ellipsoid, merged into the one asset mesh.
        base=len(verts); rings=5; segs=9
        for ri in range(rings+1):
            phi=math.pi*ri/rings
            for si in range(segs):
                th=2*math.pi*si/segs; verts.append(tuple(v+Vector((0.32*math.sin(phi)*math.cos(th),0.32*math.sin(phi)*math.sin(th),0.42*math.cos(phi)))))
        for ri in range(rings):
            for si in range(segs):
                a0=base+ri*segs+si; b0=base+ri*segs+(si+1)%segs; c0=base+(ri+1)*segs+(si+1)%segs; d0=base+(ri+1)*segs+si; face((a0,b0,c0,d0),foliage)

# Roof-open schematic public/interior rooms are part of the library mesh, but exact
# floor-by-floor layout and room placement remain unverified.
mesh=bpy.data.meshes.new(old.name+'_alpha_phi_detail'); mesh.from_pydata(verts,[],faces)
for m in materials: mesh.materials.append(m)
mesh.update()
for p0,mi0 in zip(mesh.polygons,mids): p0.material_index=mi0
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
obj.data=mesh
uv=mesh.uv_layers.new(name='Brick and roof texture mapping')
for poly in mesh.polygons:
    mi0=poly.material_index
    for li in poly.loop_indices:
        v=mesh.vertices[mesh.loops[li].vertex_index].co
        if mi0==brick:
            # wall-scale UVs in meters; horizontal world coordinate and vertical height.
            uv.data[li].uv=(v.x+v.y,v.z)
        elif mi0==roof:
            uv.data[li].uv=(v.x*tc.x+v.y*tc.y,v.z)
mesh.update()
if old.users==0: bpy.data.meshes.remove(old)
obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
result={'asset_id':cfg['asset_id'],'source_fid':attrs['FID'],'source_way_id':cfg['source_way_id'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'official_ring_vertices':len(points),'official_area_m2':attrs.get('Shape__Area'),'official_num_levels':attrs.get('NUM_LEVELS'),'official_extrution_attribute':attrs.get('Extrution'),'wall_height_estimate_m':H,'roof_ridge_estimate_m':ridge,'collection_objects':len(coll.objects)}
print('BUILD_RESULT_JSON='+json.dumps(result))
