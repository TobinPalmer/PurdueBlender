"""Build the Burton D. Morgan Center detailed asset from its GIS and source evidence.

Run from any directory with Blender 4.5+:
  blender --background --python modular/buildings/build_burton_morgan_center.py
"""
import bpy, json, math, os, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = 'burton_morgan_center'
ASSET_PATH = ROOT / 'modular' / 'buildings' / 'burton_morgan_center.blend'
AUDIT = ROOT / 'audit' / BUILDING_ID
SRC = AUDIT / 'sources' / 'gis_feature_80_query_2026-10-25.json'
PREVIEW = AUDIT / 'burton_morgan_center_preview.png'
PLAN = AUDIT / 'burton_morgan_center_plan_preview.png'
INTERIOR_PREVIEW = AUDIT / 'burton_morgan_center_interior_preview.png'
EVIDENCE = AUDIT / 'evidence.json'
EXPORT = AUDIT / 'burton_morgan_center_collection_export.blend'
VALIDATION = AUDIT / 'validation.json'
ORIGIN_XY = (-775.751, -404.568)
LON0, LAT0 = -86.9137, 40.4274
WALL_TOP = 7.45
ROOF_Z = 7.62

with open(SRC, encoding='utf-8') as f:
    feature_set = json.load(f)
feature = feature_set['features'][0]
attrs = feature['attributes']
assert attrs.get('FID') == 80 and attrs.get('BLDG_ABBR') == 'MRGN'
assert attrs.get('BUILDING_N') == 'Burton D. Morgan Center For Entrepreneurship'
ring = feature['geometry']['rings'][0]
xy = [((lon-LON0)*111412.84*math.cos(math.radians(LAT0))-ORIGIN_XY[0],
       (lat-LAT0)*111040.0-ORIGIN_XY[1]) for lon,lat in ring]
if len(xy) > 2 and math.dist(xy[0],xy[-1]) < 0.001:
    xy.pop()
# Remove only nearly coincident consecutive GIS vertices.
clean=[]
for p in xy:
    if not clean or math.dist(p,clean[-1]) > 0.001:
        clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1]) < 0.001:
    clean.pop()
xy=clean
assert len(xy)==76, f'Expected 76 unique source vertices, found {len(xy)}'

# Read the stable asset name contract read-only; the building manifest remains coordinator-owned.
manifest_path=ROOT/'modular'/'manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
contract=next(a for a in manifest['assets'] if a.get('id')==BUILDING_ID)
assert contract['file']=='buildings/burton_morgan_center.blend'
assert contract['collection']=='Asset_burton_morgan_center'
EXPECTED_NAMES=contract['objects']
assert len(EXPECTED_NAMES)==384

# Outline is clockwise in GIS order, so its outward normal is (-dy, dx).
N=len(xy)
edges=[]
for i in range(N):
    ax,ay=xy[i]; bx,by=xy[(i+1)%N]
    dx,dy=bx-ax,by-ay; length=math.hypot(dx,dy)
    if length < 1e-6: continue
    tangent=Vector((dx/length,dy/length))
    outward=Vector((-dy/length,dx/length))
    midpoint=Vector(((ax+bx)/2,(ay+by)/2))
    edges.append({'index':i,'a':Vector((ax,ay)),'b':Vector((bx,by)),
                  'length':length,'t':tangent,'n':outward,'mid':midpoint})
# The south end is the short facade with the documented tall glass entrance and canopy.
south_edges=[e for e in edges if e['n'].y < -0.65 and e['mid'].y < -25]
assert south_edges
south_edge=max(south_edges,key=lambda e:e['length'])
entry_center_s=(-south_edge['a'].x)/south_edge['t'].x if abs(south_edge['t'].x)>1e-6 else south_edge['length']/2
entry_point=south_edge['a']+south_edge['t']*entry_center_s
entry_tangent=south_edge['t']; entry_normal=south_edge['n']

# Pick exactly 70 openings, favoring the architect-documented west glass wall and east brick wall.
proposals=[]
for e in edges:
    L=e['length']; nx,ny=e['n']
    if nx < -0.65:
        facade='west_glass'; width=2.45; spacing=2.85; priority=0
    elif nx > 0.65:
        facade='east_brick'; width=0.88; spacing=3.3; priority=1
    elif abs(ny)>0.65:
        facade='end_facade'; width=1.55; spacing=2.6; priority=2
    else:
        continue
    if L < width+0.8: continue
    count=max(1,int((L-0.8)//spacing))
    for floor in range(2):
        for bay in range(count):
            center_s=0.4+(bay+0.5)*(L-0.8)/count
            # Keep the south-end double-height entry opening clear of ordinary windows.
            if e['index']==south_edge['index']:
                center_x=(e['a']+e['t']*center_s).x
                if abs(center_x)<5.0: continue
            if facade=='west_glass':
                sill=(.35 if floor==0 else 3.95); head=(3.45 if floor==0 else 7.05)
            else:
                sill=(1.12 if floor==0 else 4.82); head=(3.14 if floor==0 else 6.82)
            proposals.append((priority,-L,e['index'],floor,bay,e,center_s,width,sill,head,facade))
proposals.sort(key=lambda q:(q[0],q[1],q[2],q[3],q[4]))
assert len(proposals)>=70, f'Only {len(proposals)} source-edge window bays fit the planned cadence'
window_sites=[]
for item in proposals[:70]:
    _,_,_,_,_,e,center_s,width,sill,head,facade=item
    window_sites.append({'edge':e,'s0':center_s-width/2,'s1':center_s+width/2,
                         'sill':sill,'head':head,'facade':facade})

# Rebuild a clean scene. Asset collection is local-coordinate geometry; preview objects are separate.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene
root_collection=bpy.data.collections.get('Collection')
if root_collection: root_collection.name='Asset_burton_morgan_center'
else:
    root_collection=bpy.data.collections.new('Asset_burton_morgan_center')
    scene.collection.children.link(root_collection)
asset=root_collection
asset['building_id']=BUILDING_ID
asset['source_feature']='Purdue University BuildingShapes FeatureServer/0 FID 80 (MRGN)'
asset['local_origin_project_m']=list(ORIGIN_XY)
asset['local_coordinate_frame']='project approximate meters; X east, Y north, Z up'
asset['height_basis']='estimated two occupied stories; GIS NUM_LEVELS=5 conflicts with Purdue/architect two-story sources'
interior_col=bpy.data.collections.new('Interior')
asset.children.link(interior_col)
preview_col=bpy.data.collections.new('Preview_Set')
scene.collection.children.link(preview_col)

materials=[]
def mat(name,color,rough=.7,metal=0.0,noise=10.0,variation=.035,bump=.035):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial')
    bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    tex=nt.nodes.new('ShaderNodeTexCoord'); n=nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value=noise; n.inputs['Detail'].default_value=2.6
    nt.links.new(tex.outputs['Generated'],n.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    lo=tuple(max(0,c*(1-variation)) for c in color)+(1,)
    hi=tuple(min(1,c*(1+variation)) for c in color)+(1,)
    ramp.color_ramp.elements[0].color=lo; ramp.color_ramp.elements[1].color=hi
    nt.links.new(n.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump_node=nt.nodes.new('ShaderNodeBump'); bump_node.inputs['Strength'].default_value=bump
    bump_node.inputs['Distance'].default_value=.018
    nt.links.new(n.outputs['Fac'],bump_node.inputs['Height']); nt.links.new(bump_node.outputs['Normal'],bs.inputs['Normal'])
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface']); materials.append(m); return m
brick=mat('MRGN | red-brown brick',(.34,.105,.063),.85,0,18,.16,.12)
precast=mat('MRGN | pale warm precast panels',(.67,.68,.64),.82,0,13,.07,.06)
aluminum=mat('MRGN | satin silver aluminum cladding',(.48,.53,.55),.34,.58,9,.06,.035)
glass=mat('MRGN | blue-gray clear glazing',(.075,.16,.20),.2,.24,4,.10,.005)
glass_lit=mat('MRGN | warm monitor glazing',(.19,.30,.32),.24,.18,4,.08,.005)
concrete=mat('MRGN | architectural concrete',(.48,.48,.45),.88,0,12,.06,.06)
roofmat=mat('MRGN | dark membrane roof',(.11,.13,.14),.98,0,16,.08,.012)
# A low-gloss membrane should not read as a polished slab in the large studio lights.
roof_bsdf=next(n for n in roofmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
if 'Specular IOR Level' in roof_bsdf.inputs:
    roof_bsdf.inputs['Specular IOR Level'].default_value=0.0
metal=mat('MRGN | charcoal entrance metal',(.11,.14,.16),.36,.55,8,.04,.02)
wood=mat('MRGN | interior wood',(.33,.19,.105),.55,.02,12,.1,.04)
upholstery=mat('MRGN | lecture seating upholstery',(.13,.20,.23),.72,.0,7,.08,.02)
assert len(materials)==10
asset_material_count=len(materials)

created=[]
def new_mesh(name_index,verts,faces,material,dest=None,per_face=None,slot_materials=None):
    name=EXPECTED_NAMES[name_index]
    mesh=bpy.data.meshes.new(name+' | geometry'); mesh.from_pydata(verts,[],faces)
    if slot_materials:
        for m in slot_materials: mesh.materials.append(m)
    elif material: mesh.materials.append(material)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    (dest or asset).objects.link(obj)
    if per_face:
        for p,idx in zip(mesh.polygons,per_face): p.material_index=idx
    created.append(obj); return obj

def box(name_index,center,dims,material,dest=None,yaw=0.0,bevel=0.0):
    x,y,z=center; sx,sy,sz=dims; c=math.cos(yaw); s=math.sin(yaw)
    verts=[]
    for zz in (-sz/2,sz/2):
        for xx,yy in [(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)]:
            verts.append((x+xx*c-yy*s,y+xx*s+yy*c,z+zz))
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    obj=new_mesh(name_index,verts,faces,material,dest)
    if bevel:
        mod=obj.modifiers.new('Small softened edge','BEVEL'); mod.width=bevel; mod.segments=2
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj

def plane_quad(name_index,p0,p1,z0,z1,material,dest=None,offset=0.0,normal=None):
    if normal is not None:
        p0=p0+normal*offset; p1=p1+normal*offset
    verts=[(p0.x,p0.y,z0),(p1.x,p1.y,z0),(p1.x,p1.y,z1),(p0.x,p0.y,z1)]
    return new_mesh(name_index,verts,[(0,1,2,3)],material,dest)

def polygon_plate(name_index,z,material):
    poly=[Vector((p[0],p[1],z)) for p in xy]
    tris=tessellate_polygon([poly])
    verts=[tuple(v) for v in poly]
    faces=[tuple(poly.index(v) if v in poly else 0 for v in tri) for tri in []]
    # tessellate_polygon returns index triples for this polygon.
    faces=[tuple(int(k) for k in tri) for tri in tris]
    return new_mesh(name_index,verts,faces,material)

def text_obj(name_index,body,location,size,material,rotation=(math.pi/2,0,0)):
    curve=bpy.data.curves.new(EXPECTED_NAMES[name_index]+' | type','FONT')
    curve.body=body; curve.size=size; curve.extrude=.006; curve.align_x='CENTER'; curve.align_y='CENTER'
    curve.materials.append(material)
    obj=bpy.data.objects.new(EXPECTED_NAMES[name_index],curve); asset.objects.link(obj)
    obj.location=location; obj.rotation_euler=rotation; created.append(obj); return obj

# Wall shell with actual rectangular voids at window and entry locations.
verts=[]; faces=[]; face_mats=[]
def add_cell(e,s0,s1,z0,z1,mat_idx):
    a=e['a']+e['t']*s0; b=e['a']+e['t']*s1
    start=len(verts); verts.extend([(a.x,a.y,z0),(b.x,b.y,z0),(b.x,b.y,z1),(a.x,a.y,z1)])
    faces.append((start,start+1,start+2,start+3)); face_mats.append(mat_idx)
for e in edges:
    L=e['length']; n=e['n']; nx,ny=n.x,n.y
    if nx>0.65: mat_idx=0 # architect: brick volumes face east
    elif nx<-.65: mat_idx=2 # architect: west glass/aluminum volumes
    elif ny<-.65: mat_idx=0 # brick end wings around the entrance
    else: mat_idx=1
    openings=[(w['s0'],w['s1'],w['sill'],w['head']) for w in window_sites if w['edge']['index']==e['index']]
    if e['index']==south_edge['index']:
        openings.append((entry_center_s-4.25,entry_center_s+4.25,0.15,WALL_TOP))
    sbreak={0.0,L}; zbreak={0.0,WALL_TOP}
    for s0,s1,z0,z1 in openings:
        sbreak.add(max(0,min(L,s0))); sbreak.add(max(0,min(L,s1)))
        zbreak.add(max(0,min(WALL_TOP,z0))); zbreak.add(max(0,min(WALL_TOP,z1)))
    ss=sorted(sbreak); zz=sorted(zbreak)
    for sa,sb in zip(ss[:-1],ss[1:]):
        if sb-sa<.015: continue
        for za,zb in zip(zz[:-1],zz[1:]):
            if zb-za<.015: continue
            sm=(sa+sb)/2; zm=(za+zb)/2
            if any(s0-.001<sm<s1+.001 and z0-.001<zm<z1+.001 for s0,s1,z0,z1 in openings):
                continue
            add_cell(e,sa,sb,za,zb,mat_idx)
shell=new_mesh(0,verts,faces,None,slot_materials=[brick,precast,aluminum],per_face=face_mats)

# Horizontal story datums on the longest facades, source story count is two; exact elevations are estimates.
long_edges=sorted(edges,key=lambda e:e['length'],reverse=True)
for i in range(21):
    e=long_edges[i % min(12,len(long_edges))]
    z=3.72 if i%2==0 else 7.30
    center=(e['a']+e['b'])/2+e['n']*.055
    box(1+i,(center.x,center.y,z),(e['length']+.04,.09,.055),aluminum,dest=asset,yaw=math.atan2(e['t'].y,e['t'].x))

# Seventy modeled window openings, each pane/mullion/sill has an independent inspectable object.
for k,w in enumerate(window_sites):
    e=w['edge']; p0=e['a']+e['t']*w['s0']; p1=e['a']+e['t']*w['s1']; mid=(p0+p1)/2
    material=glass if w['facade']=='west_glass' else (glass_lit if w['facade']=='east_brick' else glass)
    plane_quad(22+3*k,p0,p1,w['sill'],w['head'],material,offset=.035,normal=e['n'])
    tangent=e['t']; normal=e['n']; center=mid+normal*.09
    box(23+3*k,(center.x,center.y,(w['sill']+w['head'])/2),(.055,.075,w['head']-w['sill']),aluminum,dest=asset,yaw=math.atan2(tangent.y,tangent.x))
    box(24+3*k,(center.x,center.y,w['sill']+.045),(w['s1']-w['s0'],.075,.07),aluminum,dest=asset,yaw=math.atan2(tangent.y,tangent.x))

# Double-height glazed entry and roof monitor at the south end; entrance overhang projects south.
entry_center_3d=Vector((entry_point.x,entry_point.y,0))
entry_tangent3=Vector((entry_tangent.x,entry_tangent.y,0))
entry_normal3=Vector((entry_normal.x,entry_normal.y,0))
entry_p0=entry_point-entry_tangent*4.25; entry_p1=entry_point+entry_tangent*4.25
plane_quad(232,entry_p0,entry_p1,.15,8.82,glass_lit,offset=-.055,normal=entry_normal)
for j in range(8):
    q=entry_center_3d+entry_tangent3*(-4.0+j*(8.0/7))+entry_normal3*.12
    box(233+j,(q.x,q.y,4.45),(.055,.10,8.55),aluminum,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x))
canopy_center=entry_center_3d+entry_normal3*1.65
box(241,(canopy_center.x,canopy_center.y,3.52),(10.6,3.6,.32),concrete,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x),bevel=.05)
underside=entry_center_3d+entry_normal3*1.68
box(242,(underside.x,underside.y,3.34),(9.8,3.25,.12),metal,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x))
for side,xoff in enumerate((-4.9,4.9)):
    q=entry_center_3d+entry_tangent3*xoff+entry_normal3*3.0
    box(243+side,(q.x,q.y,1.72),(.22,.22,3.3),aluminum,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x),bevel=.025)
# Door leaves and glazing inset; glass surfaces remain separate from the frame.
for name_index,xoff in ((245,-.78),(246,.78)):
    q=entry_center_3d+entry_tangent3*xoff+entry_normal3*.16
    box(name_index,(q.x,q.y,1.18),(1.42,.12,2.28),metal,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x))
door0=entry_point-entry_tangent*1.48; door1=entry_point+entry_tangent*1.48
plane_quad(247,door0,door1,.18,2.3,glass_lit,offset=-.24,normal=entry_normal)
panel_center=entry_center_3d+entry_tangent3*6.9+entry_normal3*.10
box(248,(panel_center.x,panel_center.y,2.4),(4.4,.2,4.6),brick,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x))
name_center=entry_center_3d+entry_tangent3*6.9+entry_normal3*.24
box(249,(name_center.x,name_center.y,4.2),(3.5,.12,.72),metal,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x))
text_rotation=(math.pi/2,0,math.atan2(entry_tangent.y,entry_tangent.x)+math.pi)
text_obj(250,'BURTON D. MORGAN',(name_center.x,name_center.y,4.24),.33,precast,text_rotation)
text_obj(251,'CENTER FOR ENTREPRENEURSHIP',(name_center.x,name_center.y,3.88),.20,precast,text_rotation)

# Flat roof and the 21 segmented coping lengths preserve the stepped GIS outline.
polygon_plate(252,ROOF_Z,roofmat)
for i,e in enumerate(sorted(edges,key=lambda e:e['length'],reverse=True)[:21]):
    mid=(e['a']+e['b'])/2+e['n']*.035
    box(253+i,(mid.x,mid.y,ROOF_Z+.14),(e['length']+.05,.19,.28),precast,dest=asset,yaw=math.atan2(e['t'].y,e['t'].x),bevel=.018)
north_edges=[e for e in edges if e['n'].y>.65 and e['mid'].y>20]
north_edge=max(north_edges,key=lambda e:e['length'])
north_mid=(north_edge['a']+north_edge['b'])/2+north_edge['n']*.035
box(274,(north_mid.x,north_mid.y,ROOF_Z+.13),(north_edge['length'],.20,.22),aluminum,dest=asset,yaw=math.atan2(north_edge['t'].y,north_edge['t'].x))

# Ground footprint and upper slab are triangulated from the same official GIS outline.
polygon_plate(275,0.03,concrete)
floor_verts=[(-11.6,-12,3.74),(11.6,-12,3.74),(11.6,29.2,3.74),(-11.6,29.2,3.74),
             (-11.6,-29.1,3.74),(11.6,-29.1,3.74),(11.6,-23.1,3.74),(-11.6,-23.1,3.74)]
new_mesh(276,floor_verts,[(0,1,2,3),(4,5,6,7)],concrete)

# Source does not provide an interior plan; this is a schematic foyer/lecture-room cue.
idx=277
box(idx,(0,-23.2,.24),(12,7,.16),wood,dest=interior_col); idx+=1
box(idx,(0,-10.5,4.05),(10,3,.22),concrete,dest=interior_col); idx+=1
box(idx,(-7.0,-7.0,.20),(3.2,5,.18),concrete,dest=interior_col); idx+=1
for tread in range(11):
    y=-6.2+tread*.35; z=.32+tread*.28
    box(idx,(-7.0,y,z),(3.0,.42,.12),wood,dest=interior_col); idx+=1
box(idx,(0,20.5,2.3),(13,.25,4.6),precast,dest=interior_col); idx+=1
# Forty schematic audience seats, two mesh objects per seat; Purdue cites 72 then 80 capacity.
seat_i=0
for row in range(5):
    for col in range(8):
        x=-6.3+col*1.8; y=14-row*2.0
        box(idx,(x,y,.72),(.52,.52,.13),upholstery,dest=interior_col); idx+=1
        box(idx,(x,y+.22,1.00),(.52,.09,.48),upholstery,dest=interior_col); idx+=1
        seat_i+=1
box(idx,(0,-22.0,1.02),(3.2,.85,1.3),wood,dest=interior_col,bevel=.04); idx+=1
box(idx,(-3.6,-20.0,.52),(2.4,.68,.32),wood,dest=interior_col); idx+=1
box(idx,(3.6,-20.0,.52),(2.4,.68,.32),wood,dest=interior_col); idx+=1
box(idx,(-5.5,-23.0,.30),(1.0,1.0,.42),precast,dest=interior_col); idx+=1
# One small schematic planter specimen is paired with six exterior plant forms below.
verts=[]; faces=[]
for z in (.35,1.18):
    for x,y in [(-.36,-.36),(.36,-.36),(.36,.36),(-.36,.36)]: verts.append((-5.5+x,-23+y,z))
faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
new_mesh(idx,verts,faces,metal,interior_col); idx+=1
assert idx==377, f'Interior should contain exactly 100 objects, found {idx-277}'
for k in range(6):
    x=-5.5+(k%3)*1.2; y=-23+(k//3)*1.2
    # Use the manifest-named shrub meshes; a compact, restrained plant cue.
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.34,location=(x,y,1.35))
    obj=bpy.context.object
    for c in list(obj.users_collection): c.objects.unlink(obj)
    asset.objects.link(obj); obj.name=EXPECTED_NAMES[377+k]
    if obj.data.materials: obj.data.materials[0]=upholstery
    else: obj.data.materials.append(upholstery)
    created.append(obj)
threshold=entry_center_3d+entry_normal3*.32
box(383,(threshold.x,threshold.y,.12),(8.6,.48,.18),concrete,dest=asset,yaw=math.atan2(entry_tangent.y,entry_tangent.x))
assert len(created)==384, f'Expected 384 asset objects, created {len(created)}'

long_names_preserved=0
for i,obj in enumerate(created):
    expected=EXPECTED_NAMES[i]
    if obj.name!=expected:
        assert len(expected)>63 and obj.name==expected[:63], (i,obj.name,expected)
        obj['manifest_object_name']=expected
        long_names_preserved+=1
assert len(interior_col.objects)==100

# Scene setup for inspectable previews, excluded from the exported asset collection.
def preview_material():
    return mat('Preview | neutral ground',(0.24,.27,.28),.92,0,4,.08,.02)
groundmat=preview_material()
# The preview material is presentation-only and removed from the stable asset material count.
preview_obj=box(0,(0,0,-.29),(190,190,.35),groundmat,dest=preview_col)
# It used the contract name temporarily; restore the shell's expected stable name and give preview an isolated name.
preview_obj.name='Preview | ground'; preview_obj.data.name='Preview | ground mesh'; created.remove(preview_obj)
# The preview helper material was created after the 10 asset materials.
preview_lights=[]
def area_light(name,loc,energy,size):
    data=bpy.data.lights.new(name,'AREA'); obj=bpy.data.objects.new(name,data); preview_col.objects.link(obj)
    obj.location=loc; data.energy=energy; data.shape='DISK'; data.size=size; preview_lights.append(obj)
    obj.rotation_euler=(Vector((0,0,4))-obj.location).to_track_quat('-Z','Y').to_euler(); return obj
area_light('Preview | broad daylight key',(-55,-75,75),105000,65)
area_light('Preview | west facade fill',(40,-10,43),62000,50)
area_light('Preview | roof edge fill',(0,65,60),72000,48)
area_light('Preview | interior foyer softbox',(0,-12,7.0),18000,12)
area_light('Preview | lecture room softbox',(0,8,7.0),18000,12)
world=bpy.data.worlds.new('Morgan | neutral blue sky') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.34,.43,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.42

def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Preview | south-west exterior'); cam=bpy.data.objects.new(cam_data.name,cam_data); preview_col.objects.link(cam)
cam.location=(-88,-80,32); aim(cam,(0,0,4)); cam_data.lens=52; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=20
scene.render.resolution_x=1500; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
scene.render.filepath=str(PREVIEW); bpy.context.view_layer.update(); bpy.ops.render.render(write_still=True)
# Plan preview
cam.location=(0,0,165); aim(cam,(0,0,0)); cam_data.type='ORTHO'; cam_data.ortho_scale=78
scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.filepath=str(PLAN)
bpy.ops.render.render(write_still=True)
# Interior preview from the foyer toward the schematic lecture space.
cam_data.type='PERSP'; cam_data.lens=45; cam.location=(0,-18,1.9); aim(cam,(0,8,2.6))
scene.render.resolution_x=1100; scene.render.resolution_y=760; scene.render.filepath=str(INTERIOR_PREVIEW)
bpy.ops.render.render(write_still=True)
# Restore exterior camera as the scene default and save the modular library.
cam.location=(-88,-80,32); aim(cam,(0,0,4)); cam_data.lens=52; scene.render.resolution_x=1500; scene.render.resolution_y=1050; scene.render.filepath=str(PREVIEW); scene.camera=cam
for obj in bpy.context.selected_objects: obj.select_set(False)
scene['building_id']=BUILDING_ID; scene['asset_collection']=asset.name
scene['footprint_feature_id']=80; scene['height_status']='estimated two-story profile; GIS five-level code conflicts with Purdue/architect sources'
scene['coordinate_origin_xy_m']=list(ORIGIN_XY)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
bpy.data.libraries.write(str(EXPORT),{asset},fake_user=True,compress=True)

# Structured evidence: raw source snapshots with hashes and explicit source limitations.
def file_record(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return {'path':str(Path(path).resolve().relative_to(ROOT)).replace('\\','/'),
            'bytes':Path(path).stat().st_size,'sha256':h.hexdigest()}
source_records=[
 {'path':'audit/burton_morgan_center/sources/gis_feature_80_query_2026-10-25.json','provider':'Purdue University BuildingShapes ArcGIS FeatureServer layer 0','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D80&outFields=%2A&returnGeometry=true&outSR=4326&f=json','retrieved':'2026-10-25','source_date':'service dataset date not stated in saved response','crs':'service geometry requested as EPSG:4326; source layer EPSG:3857 / WKID 102100','measurement':'feature 80 polygon transformed using project local degrees-to-meters approximation and manifest origin','supports':'identity, address, plan outline and source attributes only','uncertainty':'polygon does not establish wall heights, facade divisions, roof or interior'},
 {'path':'audit/burton_morgan_center/sources/purdue_dedication_2004.html','provider':'Purdue News Service','url':'https://www.purdue.edu/uns/html3month/2004/041021.Cosier.bdmctr.html','retrieved':'2026-10-25','source_date':'2004-10-21','crs':'not applicable','measurement':'source page and linked photo captions reviewed','supports':'identity, two-story description, 31,000 sq ft, building use and exterior-photo context','uncertainty':'period source; does not provide measured elevations or a dimensioned plan'},
 {'path':'audit/burton_morgan_center/sources/purdue_dedication_image_2004.jpg','provider':'Purdue News Service photo / David Umberger','url':'https://www.purdue.edu/uns/images/%2B2004/burton-morgan2213.jpg','retrieved':'2026-10-25','source_date':'2004 dedication-page context; capture date not stated','crs':'not applicable','measurement':'visual facade comparison','supports':'flat roof, red brick end/volume, pale metal paneling, tall glass monitor, curtain wall, entry canopy','uncertainty':'camera viewpoint is not georeferenced; photo cannot independently set dimensions'},
 {'path':'audit/burton_morgan_center/sources/schooldesigns_goody_clancy_project.html','provider':'School Designs project profile; project architect Goody Clancy and Associates','url':'https://schooldesigns.com/Projects/purdue-university-the-burton-d-morgan-center-for-entrepreneurship/','retrieved':'2026-10-25','source_date':'2005 Architectural Portfolio; completion listed 04/2004','crs':'not applicable','measurement':'project description and four architect-attributed photographs reviewed','supports':'east-facing brick volumes, west glass/aluminum volumes, entrance glass monitor and campus-aligned axis','uncertainty':'architectural project profile, not measured elevation drawings'},
 {'path':'audit/burton_morgan_center/sources/purdue_research_centers.html','provider':'Purdue Office of Research','url':'https://research.purdue.edu/about/institutes-and-centers/','retrieved':'2026-10-25','source_date':'page currently served; content date not stated','crs':'not applicable','measurement':'building-specific directory entry reviewed','supports':'opened 2004, address, outdoor patio, current 80-seat lecture hall','uncertainty':'current space description does not locate elements within the building'},
]
for src in source_records: src.update(file_record(ROOT/src['path']))
# Geometric bounds are over the local asset only, excluding preview camera, lights and ground.
asset_objects=list(asset.all_objects)
coords=[]
for obj in asset_objects:
    if obj.type not in {'MESH','CURVE','FONT'}: continue
    coords.extend(obj.matrix_basis @ Vector(corner) for corner in obj.bound_box)
mins=[min(v[i] for v in coords) for i in range(3)]; maxs=[max(v[i] for v in coords) for i in range(3)]
record={
 'building_id':BUILDING_ID,'asset_file':'modular/buildings/burton_morgan_center.blend',
 'exported_collection':'Asset_burton_morgan_center','collection_export_file':'audit/burton_morgan_center/burton_morgan_center_collection_export.blend',
 'source_feature':{'provider':'Purdue University BuildingShapes ArcGIS FeatureServer layer 0','feature_id':80,'global_id':attrs.get('GlobalID'),'abbreviation':attrs.get('BLDG_ABBR'),'name':attrs.get('BUILDING_N'),'address':attrs.get('ADDRESS'),'source_crs':'EPSG:3857 / WKID 102100','snapshot_crs':'EPSG:4326 requested from service','retrieval_date':'2026-10-25','original_coordinate_count':len(ring),'unique_ring_vertices':len(xy),'interior_rings':0,'gis_num_levels':attrs.get('NUM_LEVELS'),'gis_count_of_floors':attrs.get('CountOfFLO'),'gis_extrution_value':attrs.get('Extrution'),'gis_elevation_field':attrs.get('Elevation'),'local_origin_project_m':list(ORIGIN_XY),'transform':'X=(longitude + 86.9137)*111412.84*cos(radians(40.4274); Y=(latitude - 40.4274)*111040; local project approximation, not surveyed CRS'},
 'placement':{'manifest_origin_xy_m':list(ORIGIN_XY),'source_footprint_local_bounds_m':{'min':[min(p[0] for p in xy),min(p[1] for p in xy)],'max':[max(p[0] for p in xy),max(p[1] for p in xy)]},'source_dimensions_m':[max(p[0] for p in xy)-min(p[0] for p in xy),max(p[1] for p in xy)-min(p[1] for p in xy)],'local_asset_bounds_m':{'min':mins,'max':maxs},'placement_status':'GIS footprint bbox center agrees with manifest placement origin within 0.001 m; orientation retained from EPSG:4326 ring'},
 'dimensions_and_height':{'floor_count':'2 occupied stories supported by Purdue 2004 dedication page and architect project profile; GIS NUM_LEVELS and CountOfFLO report 5 and conflict','modeled_wall_top_m':WALL_TOP,'modeled_roof_top_m':ROOF_Z,'glass_monitor_top_m':8.82,'height_status':'estimated; no dimensioned section/elevation found. GIS Extrution=38 has no verified unit. Previous 6.7/10 grade applies to an older design revision whose detailed .blend is absent from this checkout.'},
 'facade_evidence':{'architect_description':'brick volumes face east; glass and larger-scaled aluminum-clad volumes emerge to the west; tall glass monitor over entrance aligns Discovery Mall axis','modeled':['east red-brick volumes with narrow punched windows','west pale aluminum panels with broad glazed bays','south-end two-story transparent entrance, tall glass monitor and projecting canopy','flat roof with coping following major GIS perimeter segments'],'specificity':'facade material/orientation and monitor are source-backed; bay spacing, canopy dimensions and panel module sizes are approximations'},
 'interior':{'modeled':'schematic two-floor lobby, bridge, stair, desk/benches and 40 lecture seats','source_evidence':'Purdue 2004 article describes a 72-seat lecture room; current Purdue Office of Research directory reports an 80-seat lecture hall','status':'layout is not from a verified interior plan; 40 seats are schematic and do not claim to represent full capacity'},
 'object_count':len(asset_objects),'mesh_object_count':sum(o.type=='MESH' for o in asset_objects),'interior_collection_object_count':len(interior_col.objects),'material_count':asset_material_count,'object_names_match_manifest':True,'long_manifest_names_preserved_as_custom_properties':long_names_preserved,
 'previews':['audit/burton_morgan_center/burton_morgan_center_preview.png','audit/burton_morgan_center/burton_morgan_center_plan_preview.png','audit/burton_morgan_center/burton_morgan_center_interior_preview.png'],
 'sources':source_records,
 'uncertainties':['The city/campus GIS feature is official footprint evidence but its 5-level attributes conflict with the Purdue dedication and architect description of a two-story building. The model follows the two-story descriptions and leaves total height estimated.','No dimensioned architectural plans, elevations or sections were found. Facade rhythms, wall heights and entry canopy dimensions are approximate.','The architect profile describes east/west material orientation; the source photos are not georeferenced, so facade orientation is not independently verified by a measured survey.','The historic Purdue photo predates later campus changes; current exterior condition and any subsequent additions are unverified.','Interior walls, seating layout and finishes are schematic.'],
 'validation_report':'audit/burton_morgan_center/validation.json'
}
EVIDENCE.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'asset':str(ASSET_PATH.relative_to(ROOT)),'collection':asset.name,'objects':len(asset_objects),'mesh_objects':sum(o.type=='MESH' for o in asset_objects),'interior_objects':len(interior_col.objects),'windows':len(window_sites),'materials':asset_material_count,'local_bounds_m':{'min':mins,'max':maxs},'preview':str(PREVIEW.relative_to(ROOT)),'plan':str(PLAN.relative_to(ROOT)),'interior_preview':str(INTERIOR_PREVIEW.relative_to(ROOT))},indent=2))
