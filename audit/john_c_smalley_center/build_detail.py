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
def make_brick_mat(name):
    color=cfg['wall_color']; m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); nodes=nt.nodes; links=nt.links
    out=nodes.new('ShaderNodeOutputMaterial'); out.location=(100,80)
    bsdf=nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location=(-60,80)
    bsdf.inputs['Roughness'].default_value=0.86
    bsdf.inputs['Base Color'].default_value=(*color,1)
    texcoord=nodes.new('ShaderNodeTexCoord'); texcoord.location=(-620,80)
    brick=nodes.new('ShaderNodeTexBrick'); brick.location=(-400,100)
    brick.inputs['Color1'].default_value=(0.32,0.14,0.085,1)
    brick.inputs['Color2'].default_value=(0.23,0.085,0.050,1)
    brick.inputs['Mortar'].default_value=(0.46,0.39,0.31,1)
    brick.inputs['Scale'].default_value=1.0
    brick.inputs['Brick Width'].default_value=0.42
    brick.inputs['Row Height'].default_value=0.085
    brick.inputs['Mortar Size'].default_value=0.012
    links.new(texcoord.outputs['UV'],brick.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump'); bump.location=(-150,-80)
    bump.inputs['Strength'].default_value=0.22; bump.inputs['Distance'].default_value=0.012
    links.new(brick.outputs['Fac'],bump.inputs['Height']); links.new(brick.outputs['Color'],bsdf.inputs['Base Color']); links.new(bump.outputs['Normal'],bsdf.inputs['Normal']); links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
    mats.append(m); return len(mats)-1
wall=make_brick_mat(tag+'_Exterior_Brick'); stone=make_mat(tag+'_Limestone',cfg['stone_color']); glass=make_mat(tag+'_Glazing',cfg['glass_color'],0.2,0.08); roof=make_mat(tag+'_Roof',cfg['roof_color'],0.88); metal=make_mat(tag+'_Metal',cfg['metal_color'],0.38,0.45)
floor_mat=make_mat(tag+'_Interior_Floor',(0.49,0.47,0.42),0.88)
partition_mat=make_mat(tag+'_Interior_Partition',(0.74,0.71,0.64),0.91)
wood_mat=make_mat(tag+'_Interior_Wood',(0.34,0.21,0.13),0.72)
ceiling_mat=make_mat(tag+'_Interior_Ceiling',(0.80,0.78,0.72),0.93)
office_mat=make_mat(tag+'_Interior_Office_Equipment',(0.29,0.32,0.33),0.74)
fabric_mat=make_mat(tag+'_Interior_Seating',(0.20,0.24,0.25),0.86)
plant_mat=make_mat(tag+'_Interior_Planter',(0.16,0.27,0.16),0.9)
verts=[]; faces=[]; mi=[]
def face(ids,mat): faces.append(tuple(ids)); mi.append(mat)
def quad(ps,mat):
    k=len(verts); verts.extend(tuple(p) for p in ps); face((k,k+1,k+2,k+3),mat)
def box(center,tangent,normal,w,d,h,mat):
    c=Vector(center); t=Vector((tangent.x,tangent.y,0)).normalized(); n=Vector((normal.x,normal.y,0)).normalized(); z=Vector((0,0,1)); hw=w/2; hd=d/2; hh=h/2
    offsets=[(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]; k=len(verts)
    verts.extend(tuple(c+t*a+n*b+z*v) for a,b,v in offsets)
    for f0 in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): face(tuple(k+j for j in f0),mat)
def interior_box(center,dx,dy,dz,mat):
    box(center,Vector((1,0,0)),Vector((0,1,0)),dx,dy,dz,mat)
def inside_poly(x,y):
    inside=False; j=len(points)-1
    for i,pi in enumerate(points):
        pj=points[j]
        if ((pi.y>y)!=(pj.y>y)) and x < (pj.x-pi.x)*(y-pi.y)/(pj.y-pi.y)+pi.x: inside=not inside
        j=i
    return inside
def partition(a,b,z,door_at=0.5):
    a=Vector((a[0],a[1],0)); b=Vector((b[0],b[1],0)); delta=b-a; L=Vector((delta.x,delta.y)).length
    if L<2.4: return
    if any(not inside_poly(a.x+delta.x*t,a.y+delta.y*t) for t in [i/ max(1,int(L/0.25)) for i in range(max(1,int(L/0.25))+1)]): return
    t=Vector((delta.x/L,delta.y/L,0)); n=Vector((t.y,-t.x,0)); door_w=0.96; gap=door_w/2+0.03
    center=a.lerp(b,door_at); left=center-t*gap; right=center+t*gap
    for p0,p1 in ((a,left),(right,b)):
        length=(p1-p0).length
        if length>0.28:
            box(Vector(((p0.x+p1.x)/2,(p0.y+p1.y)/2,z+1.38)),t,n,length,0.12,2.76,partition_mat)
    # Simple wood doors are set just inside the partition opening; their placement is conceptual.
    box(Vector((center.x,center.y,z+1.04))+n*0.03,t,n,0.84,0.055,2.08,wood_mat)
def furniture(center,kind='desk'):
    x,y,z=center
    if kind=='table':
        interior_box((x,y,z+0.76),2.25,1.0,0.10,wood_mat)
        for ox in (-0.90,0.90):
            for oy in (-0.34,0.34): interior_box((x+ox,y+oy,z+0.38),0.09,0.09,0.76,metal)
    elif kind=='reception':
        interior_box((x,y,z+0.62),2.4,0.72,1.24,wood_mat)
    else:
        interior_box((x,y,z+0.73),1.6,0.72,0.10,wood_mat)
        for ox in (-0.62,0.62):
            for oy in (-0.25,0.25): interior_box((x+ox,y+oy,z+0.36),0.08,0.08,0.72,metal)
def workstation(center,reverse=False):
    x,y,z=center; sy=1 if reverse else -1
    furniture(center,'desk')
    # Monitor, compact keyboard, upholstered task chair, and a low file cabinet.
    interior_box((x,y+sy*0.16,z+1.02),0.62,0.075,0.38,office_mat)
    interior_box((x,y+sy*0.28,z+0.80),0.42,0.19,0.035,metal)
    interior_box((x,y-sy*0.73,z+0.48),0.54,0.53,0.12,fabric_mat)
    interior_box((x,y-sy*0.95,z+0.82),0.52,0.12,0.56,fabric_mat)
    interior_box((x+0.98,y+0.28,z+0.53),0.38,0.56,1.06,office_mat)
    for drawer in range(3):
        interior_box((x+0.98,y+0.28,z+0.22+drawer*0.29),0.39,0.58,0.025,metal)
def meeting_place(center):
    x,y,z=center
    furniture(center,'table')
    for px in (-1.55,1.55):
        for py in (-0.68,0.68):
            interior_box((x+px,y+py,z+0.48),0.48,0.48,0.10,fabric_mat)
            interior_box((x+px,y+py+0.18,z+0.77),0.46,0.12,0.52,fabric_mat)
def planter(center):
    x,y,z=center
    interior_box((x,y,z+0.26),0.48,0.48,0.50,wood_mat)
    # Compact stylized foliage kept at furniture scale.
    for dx,dy,h in ((0,0,0.76),(-0.14,0.04,0.62),(0.13,-0.08,0.68)):
        interior_box((x+dx,y+dy,z+0.48+h/2),0.10,0.10,h,plant_mat)
H=float(cfg['height_m']); F=int(cfg['modeled_floors']); base=0.0; plinth=min(0.72,H*0.09); story=H/max(1,F)
edge=[]
for i,a in enumerate(points):
    b=points[(i+1)%len(points)]; delta=b-a; L=delta.length
    if L<0.05: continue
    t=Vector((delta.x/L,delta.y/L,0)); n=Vector((t.y,-t.x,0))*sign; edge.append((a,b,L,t,n))
    a0=Vector((a.x,a.y,base)); b0=Vector((b.x,b.y,base)); a1=Vector((a.x,a.y,plinth)); b1=Vector((b.x,b.y,plinth)); at=Vector((a.x,a.y,H)); bt=Vector((b.x,b.y,H))
    quad((a0,b0,b1,a1),stone)
# Flat structural roof follows the official polygon; no height claim is inferred from the map outline.
for tri in tessellate_polygon([points]):
    k=len(verts)
    for idx in tri:
        p=points[int(idx)]; verts.append((p.x,p.y,H))
    face((k,k+1,k+2),roof)
# Generic office interiors are intentionally schematic: the available sources establish two
# levels and the administrative use, but do not publish an as-built floor plan.
floor_z=[0.12,story]
for fz in floor_z:
    for tri in tessellate_polygon([points]):
        k=len(verts)
        for idx in tri:
            p=points[int(idx)]; verts.append((p.x,p.y,fz))
        face((k,k+1,k+2),floor_mat)
# Two internal circulation spines and office dividers are placed only where they fit within
# the official concave footprint. The west wing carries the main north/south corridor.
for z in floor_z:
    for y in (-47.5,-41.5,-35.5,-29.5):
        if all(inside_poly(x,y) for x in (-828.3,-826.0,-820.0,-814.0,-808.5,-806.4)):
            partition((-828.3,y),(-806.4,y),z,door_at=0.48)
    for x in (-824.0,-818.0,-812.0):
        if all(inside_poly(x,y) for y in (-48.0,-44.0,-39.0,-34.0,-29.0)):
            partition((x,-48.0),(x,-29.0),z,door_at=0.56)
    # Smaller eastern offices and the south/east wing are connected to a second corridor.
    for y in (-51.5,-46.5,-41.5):
        if all(inside_poly(x,y) for x in (-798.5,-794.0,-789.0,-786.8)):
            partition((-798.5,y),(-786.8,y),z,door_at=0.50)
    for x in (-795.0,-790.5):
        if all(inside_poly(x,y) for y in (-54.8,-50.0,-45.0,-40.0)):
            partition((x,-54.8),(x,-40.0),z,door_at=0.52)
# Interior furnishings read as occupied administrative workspace while remaining deliberately
# generic. Locations are illustrative props only; the public sources do not show room plans.
for z in floor_z:
    furniture((-822.0,-45.0,z),'reception' if z==floor_z[0] else 'table')
    meeting_place((-816.0,-38.5,z))
    workstation((-810.0,-32.5,z))
    workstation((-824.0,-38.5,z),True)
    workstation((-818.0,-32.5,z))
    workstation((-812.0,-46.5,z),True)
    meeting_place((-792.5,-48.5,z))
    workstation((-790.0,-43.0,z),True)
    workstation((-798.0,-51.0,z))
    planter((-824.7,-30.8,z))
    planter((-789.5,-50.5,z))
    # Additional desks keep the broad administrative wing from reading as vacant;
    # their open-office arrangement is a visual placeholder, not an inferred floor plan.
    for x,y,flip in [
        (-827.0,-44.0,False),(-821.0,-44.0,True),(-815.0,-44.0,False),
        (-809.0,-44.0,True),(-803.0,-44.0,False),(-827.0,-38.0,True),
        (-821.0,-32.0,False),(-815.0,-38.0,True),(-809.0,-38.0,False),
        (-803.0,-32.0,True),(-797.0,-43.0,False),(-797.0,-37.0,True),
        (-792.0,-38.0,False),(-792.0,-32.0,True)]:
        if inside_poly(x,y): workstation((x,y,z),flip)
# Rebuild facade surfaces around actual window openings. The opening cadence is a
# presentation approximation; the GIS and archival sources do not provide elevations.
entry=max((e for e in edge if e[4].x < -0.7 and e[2]>5),key=lambda e:e[2],default=None)
entry_mid=(entry[0]+entry[1])*0.5 if entry else None
def wall_panel(a,b,t,n,s0,s1,z0,z1,mat=wall):
    if s1-s0<0.03 or z1-z0<0.03: return
    p0=a.lerp(b,s0); p1=a.lerp(b,s1)
    quad((Vector((p0.x,p0.y,z0)),Vector((p1.x,p1.y,z0)),Vector((p1.x,p1.y,z1)),Vector((p0.x,p0.y,z1))),mat)

# Window bays use a regular but restrained rhythm, with brick piers and recessed glazing.
# One west-facing first-floor opening is reserved for the likely 1225 Third Street entry.
for a,b,L,t,n in edge:
    if L<4.0:
        wall_panel(a,b,t,n,0.0,1.0,plinth,H)
        continue
    count=max(1,int((L-1.5)//4.0)); spacing=L/(count+1); w=min(float(cfg.get('window_width_m',2.15)),spacing*0.63); pane_h=min(1.55,story*0.55)
    centers=[spacing*(bay+1)/L for bay in range(count)]
    for floor in range(F):
        z0=plinth+story*floor; z1=min(H,plinth+story*(floor+1))
        zc=plinth+story*(floor+0.5); wb=zc-pane_h*0.5; wt=zc+pane_h*0.5
        if wt>z1-0.24: wt=z1-0.24; wb=wt-pane_h
        # Cut an entry-sized gap out of the main west-facing ground-floor wall.
        door_center=None
        if floor==0 and entry and a==entry[0] and b==entry[1]: door_center=0.5
        cuts=[]
        for s in centers:
            left=max(0.0,s-w/(2*L)); right=min(1.0,s+w/(2*L))
            is_entry=door_center is not None and abs(s-door_center)<(w/L*1.6)
            if is_entry:
                cuts.append((max(0.0,door_center-1.05/L),min(1.0,door_center+1.05/L),plinth,plinth+2.55,'door'))
            else:
                cuts.append((left,right,wb,wt,'window'))
        cuts.sort(key=lambda q:q[0])
        cursor=0.0
        for left,right,low,high,kind in cuts:
            wall_panel(a,b,t,n,cursor,left,z0,z1)
            wall_panel(a,b,t,n,left,right,z0,low)
            wall_panel(a,b,t,n,left,right,high,z1)
            p=a.lerp(b,(left+right)/2); center=Vector((p.x,p.y,(low+high)/2))+n*0.055
            if kind=='window':
                box(center,t,n,(right-left)*L*0.94,0.045,high-low,glass)
                framec=center+n*0.07; fw=0.075
                box(framec+Vector((0,0,(high-low)/2)),t,n,(right-left)*L,0.12,fw,stone)
                box(framec-Vector((0,0,(high-low)/2)),t,n,(right-left)*L,0.12,fw,stone)
                box(framec-t*((right-left)*L/2-fw/2),t,n,fw,0.12,high-low,stone)
                box(framec+t*((right-left)*L/2-fw/2),t,n,fw,0.12,high-low,stone)
                # A narrow center mullion prevents the long repeated panes reading as empty voids.
                box(framec,t,n,0.045,0.10,high-low,metal)
            else:
                # Recessed double-leaf entrance with divided sidelights and a visible transom.
                box(center+n*0.015,t,n,(right-left)*L*0.72,0.06,2.12,glass)
                door_leaf=0.78
                box(center-t*0.40+n*0.09,t,n,door_leaf,0.08,2.08,metal)
                box(center+t*0.40+n*0.09,t,n,door_leaf,0.08,2.08,metal)
                box(center+n*0.11,t,n,0.055,0.09,2.08,stone)
                box(center+Vector((0,0,2.28))+n*0.08,t,n,(right-left)*L,0.12,0.10,stone)
                box(center-t*0.34+n*0.15+Vector((0,0,0.10)),t,n,0.035,0.035,0.24,stone)
                box(center+t*0.34+n*0.15+Vector((0,0,0.10)),t,n,0.035,0.035,0.24,stone)
            cursor=right
        wall_panel(a,b,t,n,cursor,1.0,z0,z1)
    for z in [plinth+story*k for k in range(1,F)]: box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,z))+n*0.025,t,n,L+0.02,0.10,0.10,stone)
    box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,H-0.16))+n*0.05,t,n,L+0.12,0.28,0.32,stone)
# A modest entry canopy and approach make the street-facing entrance legible without
# implying a specific historic design detail.
if entry:
    a,b,L,t,n=entry; p=(a+b)*0.5
    box(Vector((p.x,p.y,2.78))+n*0.82,t,n,3.2,1.55,0.16,roof)
    box(Vector((p.x,p.y,2.67))+n*0.82,t,n,3.25,1.58,0.10,stone)
    for side in (-1,1):
        box(Vector((p.x,p.y,1.32))+n*1.36+t*(side*1.38),t,n,0.15,0.15,2.64,stone)
    # Two shallow approach treads, centered on the entry and kept outside the wall plane.
    for step in range(2):
        box(Vector((p.x,p.y,0.09+step*0.08))+n*(1.05+step*0.36),t,n,2.35,0.40,0.18,stone)
old=obj.data; old_name=old.name; mesh=bpy.data.meshes.new(old_name+'_detail'); mesh.from_pydata(verts,[],faces)
for m in mats: mesh.materials.append(m)
mesh.update()
for poly,m in zip(mesh.polygons,mi): poly.material_index=m
bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update(); obj.data=mesh
uv=mesh.uv_layers.new(name='Facade brick course mapping')
for poly in mesh.polygons:
    if poly.material_index!=wall: continue
    for loop_index in poly.loop_indices:
        v=mesh.vertices[mesh.loops[loop_index].vertex_index].co
        if abs(poly.normal.x)>abs(poly.normal.y): uv.data[loop_index].uv=(v.y,v.z)
        else: uv.data[loop_index].uv=(v.x,v.z)
mesh.update()
if old.users==0: bpy.data.meshes.remove(old)
mesh.name=old_name; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
result={'asset_id':cfg['asset_id'],'source_fid':attrs['FID'],'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'official_ring_vertices':len(points),'official_extrusion_attribute':attrs.get('Extrution'),'official_levels_attribute':attrs.get('NUM_LEVELS'),'height_m':H,'height_status':cfg['height_status'],'collection_objects':len(coll.objects)}
print('BUILD_RESULT_JSON='+json.dumps(result))
