"""Build a source-backed, portable FSTC asset in campus coordinates.

Run with Blender 5.x in background mode. The official Purdue GIS FID 664 outline
is used for the structural footprint. Architectural details are explicitly
estimated from Purdue housing information and the dated exterior photo noted in
the accompanying building audit.
"""
import bpy, json, math, os, hashlib
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ID = 'massing_first_street_towers_central_fstc_929924d'
ASSET = os.path.join(ROOT, 'modular', 'buildings', ID + '.blend')
EVID = os.path.join(ROOT, 'audit', 'first_street_towers_central_fstc_929924d')
GEO = os.path.join(EVID, 'sources', 'purdue_building_shapes_fstc_2026-10-26.geojson')
SCENE_NAME = 'Building_' + ID
COLL_NAME = 'Asset_' + ID
OBJ_NAME = 'First Street Towers, Central (FSTC)'
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137

with open(GEO, encoding='utf-8') as f: feature = json.load(f)['features'][0]
ring = feature['geometry']['coordinates'][0]
def project(lon, lat):
    return ((lon-ORIGIN_LON)*111412.84*math.cos(math.radians(ORIGIN_LAT)), (lat-ORIGIN_LAT)*111040.0)
poly = [project(p[0], p[1]) for p in ring[:-1]]
# Remove near-duplicate GIS vertices while retaining the full surveyed perimeter.
clean=[]
for p in poly:
    if not clean or math.dist(p,clean[-1]) > .035: clean.append(p)
if math.dist(clean[0],clean[-1]) < .035: clean.pop()
# Iteratively remove only points that lie within 6 cm of their adjacent chord.
changed=True
while changed and len(clean)>20:
    changed=False; out=[]; n=len(clean)
    for i,p in enumerate(clean):
        a,b=clean[(i-1)%n],clean[(i+1)%n]
        dx,dy=b[0]-a[0],b[1]-a[1]
        den=math.hypot(dx,dy) or 1
        err=abs(dx*(a[1]-p[1])-(a[0]-p[0])*dy)/den
        if err < .06: changed=True
        else: out.append(p)
    if len(out)<20: break
    clean=out
poly=clean
area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2
if area < 0: poly.reverse()

# Retain the expected scene/collection/object names and remove the old simple massing.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.name=SCENE_NAME
coll=bpy.data.collections.new(COLL_NAME); scene.collection.children.link(coll)
materials=[]
def mat(name, color, rough=.72, brick=False):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    if brick:
        tex=m.node_tree.nodes.new('ShaderNodeTexBrick'); tex.inputs['Color1'].default_value=(.33,.075,.04,1); tex.inputs['Color2'].default_value=(.48,.14,.075,1); tex.inputs['Mortar'].default_value=(.30,.27,.23,1); tex.inputs['Scale'].default_value=1.0; tex.inputs['Mortar Size'].default_value=.025; tex.inputs['Mortar Smooth'].default_value=.008; tex.inputs['Brick Width'].default_value=.5; tex.inputs['Row Height'].default_value=.25
        tc=m.node_tree.nodes.new('ShaderNodeTexCoord'); m.node_tree.links.new(tc.outputs['UV'],tex.inputs['Vector']); m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        bump=m.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.20; bump.inputs['Distance'].default_value=.012; m.node_tree.links.new(tex.outputs['Color'],bump.inputs['Height']); m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    materials.append(m); return len(materials)-1
BRICK=mat('FSTC | variegated red-brown running bond brick',(.38,.1,.055),brick=True)
STONE=mat('FSTC | warm limestone and precast trim',(.76,.71,.61))
GLASS=mat('FSTC | blue-gray reflective glazing',(.10,.20,.25),.2)
METAL=mat('FSTC | dark bronze aluminum',(.075,.09,.09),.35)
ROOF=mat('FSTC | charcoal membrane roof',(.12,.14,.15),.85)
INTWALL=mat('FSTC | interior warm neutral',(.72,.66,.55))
FLOOR=mat('FSTC | interior floor tile',(.43,.40,.35))
WOOD=mat('FSTC | interior wood furnishings',(.35,.19,.085))
WHITE=mat('FSTC | sign and lettering',(.9,.86,.72),.45)
verts=[]; faces=[]; mids=[]
def face(ids, mi): faces.append(ids); mids.append(mi)
def box(center, size, mi, angle=0):
    cx,cy,cz=center; sx,sy,sz=(v/2 for v in size); c,s=math.cos(angle),math.sin(angle); start=len(verts)
    for x,y,z in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]: verts.append((cx+c*x-s*y,cy+s*x+c*y,cz+z))
    for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]: face(tuple(start+i for i in ids),mi)
def prism(poly2,z0,z1,mi):
    n=len(poly2); st=len(verts)
    verts.extend((x,y,z0) for x,y in poly2); verts.extend((x,y,z1) for x,y in poly2)
    face(tuple(st+i for i in range(n-1,-1,-1)),mi); face(tuple(st+n+i for i in range(n)),mi)
    for i in range(n): j=(i+1)%n; face((st+i,st+j,st+n+j,st+n+i),mi)

zbase=0; floors=7; story=3.42; parapet=.9; ztop=floors*story
# The seven-floor silhouette is assembled as floor plates and perimeter wall bays,
# leaving real window apertures so the schematic furnishings are visible from outside.
for fl in range(floors):
    z=fl*story
    prism(poly,z,z+.18,FLOOR)
prism(poly,ztop,ztop+.22,ROOF)
# Visible parapet lip and floor belt courses, segmented to follow the GIS perimeter.
for level in range(1,floors):
    z=level*story
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
        if L<.55: continue
        ang=math.atan2(dy,dx); mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2; nx,ny=dy/L,-dx/L
        box((mx+nx*.055,my+ny*.055,z),(L+.03,.16,.11),STONE,ang)
for i,a in enumerate(poly):
    b=poly[(i+1)%len(poly)]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if L<.8: continue
    ang=math.atan2(dy,dx); mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2; nx,ny=dy/L,-dx/L
    box((mx+nx*.06,my+ny*.06,ztop+.62),(L+.08,.2,.24),STONE,ang)

# Repeated punched windows, with pale stone surrounds and dark metal frames.
window_count=0; segments=[]
# The address is on First Street along the south side. Prefer the south-facing long
# facade for the photographed main door instead of an arbitrary maximum-length wall.
south_limit=min(p[1] for p in poly)+10.0
front_candidates=[i for i,a in enumerate(poly) if (a[1]+poly[(i+1)%len(poly)][1])/2 <= south_limit and math.dist(a,poly[(i+1)%len(poly)])>3.0]
front_i=max(front_candidates,key=lambda i: math.dist(poly[i],poly[(i+1)%len(poly)])) if front_candidates else max(range(len(poly)),key=lambda i: math.dist(poly[i],poly[(i+1)%len(poly)]))
for i,a in enumerate(poly):
    b=poly[(i+1)%len(poly)]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if L<2.2: continue
    segments.append((a,b,L,math.atan2(dy,dx),dy/L,-dx/L))
    n=max(1,int(L/3.35))
    for k in range(n):
        t=(k+.5)/n; x=a[0]+dx*t; y=a[1]+dy*t; ang=math.atan2(dy,dx); nx,ny=dy/L,-dx/L
        # GIS ring is CCW; right-hand normal faces outward.
        for fl in range(floors):
            z=fl*story+1.95
            if i==front_i and fl==0 and abs(t-.5)<.095: continue
            box((x+nx*.075,y+ny*.075,z),(.95,.08,1.38),STONE,ang)
            box((x+nx*.125,y+ny*.125,z),(.77,.065,1.20),METAL,ang)
            box((x+nx*.17,y+ny*.17,z),(.65,.045,1.04),GLASS,ang)
            box((x+nx*.20,y+ny*.20,z),(.035,.04,1.04),STONE,ang)
            box((x+nx*.20,y+ny*.20,z),(.65,.04,.035),STONE,ang)
            box((x+nx*.20,y+ny*.20,z+.05),(.65,.04,.035),STONE,ang)
            window_count+=1

# Define main entrance at the midpoint of the longest footprint facade edge.
front=next((s for s in segments if s[0]==poly[front_i]),max(segments,key=lambda x:x[2])); a,b,L,ang,nx,ny=front; dx,dy=b[0]-a[0],b[1]-a[1]; ex,ey=dx/L,dy/L; cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2
# Brick/stone wall bays around each window opening; door opening interrupts the ground floor.
for i,(a,b,L,ang,nx,ny) in enumerate(segments):
    dx,dy=b[0]-a[0],b[1]-a[1]; ex,ey=dx/L,dy/L; n=max(1,int(L/3.35)); step=L/n; is_front=(a==poly[front_i])
    for fl in range(floors):
        z0=fl*story+.18; zwin0=fl*story+1.26; zwin1=fl*story+2.64; z1=(fl+1)*story
        for k in range(n):
            lo=k*step; hi=(k+1)*step; mid=(lo+hi)/2; wx=step*.5; gap=max(0,(step-wx)/2)
            px=a[0]+ex*mid-nx*.08; py=a[1]+ey*mid-ny*.08
            if not (is_front and fl==0 and abs(mid-L/2)<3.0):
                box((px,py,(z0+zwin0)/2),(step+.02,.25,zwin0-z0),BRICK,ang)
                box((px,py,(zwin1+z1)/2),(step+.02,.25,z1-zwin1),BRICK,ang)
            # Brick piers separate the vertical window openings.
            if gap>.07:
                for side in (-1,1):
                    off=side*(wx/2+gap/2)
                    if is_front and fl==0 and abs(mid-L/2)<3.0 and abs(mid+off)<3.0: continue
                    box((px+ex*off,py+ey*off,(zwin0+zwin1)/2),(gap+.02,.25,zwin1-zwin0),BRICK,ang)
for offset in (-5.2,5.2):
    box((cx+ex*offset+nx*.14,cy+ey*offset+ny*.14,1.35),(1.8,.34,2.7),STONE,ang)
# Recessed, glazed entrance and stone portal.
box((cx+nx*.11,cy+ny*.11,1.25),(5.7,.22,2.5),STONE,ang)
box((cx+nx*.25,cy+ny*.25,1.22),(4.3,.11,2.15),GLASS,ang)
for off in (-1.05,0,1.05): box((cx+ex*off+nx*.34,cy+ey*off+ny*.34,1.18),(.075,.08,2.05),METAL,ang)
box((cx+nx*.38,cy+ny*.38,.18),(4.1,.36,.22),STONE,ang)
# Shallow curved canopy, sampled into pale fascia segments to evoke the photographed arch.
for j in range(25):
    u0=math.pi*j/25; u1=math.pi*(j+1)/25; um=(u0+u1)/2
    x0,x1=2.85*math.cos(u0),2.85*math.cos(u1); z0,z1=2.45+1.20*math.sin(u0),2.45+1.20*math.sin(u1)
    box((cx+ex*(x0+x1)/2+nx*.5,cy+ey*(x0+x1)/2+ny*.5,(z0+z1)/2), (math.hypot(x1-x0,z1-z0)+.04,.28,.24),STONE,ang+math.atan2(z1-z0,x1-x0))
# Building name plaque above the entry; real text converted into the joined export mesh.
plaque=(cx+nx*.25,cy+ny*.25,5.03)
box(plaque,(9.4,.28,.72),BRICK,ang)
cu=bpy.data.curves.new('FSTC lettering','FONT'); cu.body='FIRST STREET TOWERS'; cu.align_x='CENTER'; cu.size=.43; cu.extrude=.006
txt=bpy.data.objects.new('FSTC lettering',cu); coll.objects.link(txt); txt.location=(cx+nx*.43,cy+ny*.43,5.03); txt.rotation_euler=(math.pi/2,0,ang)
cu.materials.append(materials[WHITE])

# Schematic interiors: repeated floors, a central circulation corridor, room partitions,
# private-room furniture, and a ground-floor communal lounge/dinette. Layout is illustrative.
# Use the polygon centroid and axis-aligned footprint extents as a compact interior zone.
minx,maxx=min(p[0] for p in poly),max(p[0] for p in poly); miny,maxy=min(p[1] for p in poly),max(p[1] for p in poly)
cxp,cyp=(minx+maxx)/2,(miny+maxy)/2; W=min(42,maxx-minx-8); D=min(20,maxy-miny-7)
# Schematic room furniture only; place inside approximate central block, below facade.
for fl in range(1,floors):
    z=fl*story
    box((cxp,cyp,z-.10),(W,D,.20),FLOOR)
    box((cxp,cyp,z+1.5),(W,.12,2.9),INTWALL)
    for side in (-1,1):
        for j in range(8):
            x=cxp-W*.44+j*(W*.88/7); y=cyp+side*(D*.31)
            box((x,y,z+1.35),(2.6,.10,2.6),INTWALL)
            box((x,y+side*.9,z+.42),(1.6,1.9,.12),WOOD)
            box((x-.5,y+side*.95,z+.82),(.45,.48,.78),WOOD)
            box((x+.55,y+side*.95,z+.72),(.72,.46,.52),INTWALL)
# First-floor community lounge and dining tables are visible through entrance glazing.
for p in [(-4,-3),(-1.5,-3),(1,-3),(3.5,-3)]:
    box((cxp+p[0],cyp+p[1],.85),(1.65,.78,.12),WOOD)
    for xx in (-.62,.62):
        box((cxp+p[0]+xx,cyp+p[1],.43),(.12,.12,.78),METAL)
for xx in (-3.5,-1.8,0,1.8,3.5): box((cxp+xx,cyp+3.2,.48),(.7,.75,.16),WOOD)

# Construct one mesh object to retain the manifest's one-object asset contract.
mesh=bpy.data.meshes.new(OBJ_NAME+' | detailed mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new(OBJ_NAME,mesh); coll.objects.link(obj)
for m in materials: mesh.materials.append(m)
for p,mi in zip(mesh.polygons,mids): p.material_index=mi
# Brick shader UVs use real-meter dimensions: half-meter brick lengths and quarter-meter courses.
uv=mesh.uv_layers.new(name='Brick bond | metric UV')
for p in mesh.polygons:
    if p.material_index != BRICK: continue
    no=p.normal; tangent=Vector((-no.y,no.x,0)).normalized() if abs(no.z)<.3 else None
    for li in p.loop_indices:
        co=mesh.vertices[mesh.loops[li].vertex_index].co
        uv.data[li].uv=(co.x*tangent.x+co.y*tangent.y,co.z) if tangent else (co.x,co.y)
# Convert lettering and join it into the primary object.
bpy.ops.object.select_all(action='DESELECT'); txt.select_set(True); bpy.context.view_layer.objects.active=txt
bpy.ops.object.convert(target='MESH'); txt=bpy.context.object
obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.object.join(); obj.name=OBJ_NAME; obj.data.name=OBJ_NAME+' | detailed mesh'
for p in obj.data.polygons: p.use_smooth=False

# Lighting/render setup for a legible documented preview. Camera is placed outward from the
# entrance facade; coordinate-based geometry remains campus aligned.
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('FSTC evidence camera'); cam=bpy.data.objects.new('FSTC evidence camera',camdat); scene.collection.objects.link(cam)
cam.location=(cx+nx*155-ex*20,cy+ny*155-ey*20,30); aim(cam,(cx,cy,12)); camdat.lens=65; scene.camera=cam
ld=bpy.data.lights.new('FSTC soft daylight','AREA'); lo=bpy.data.objects.new('FSTC soft daylight',ld); scene.collection.objects.link(lo); lo.location=(cx-35,cy-45,58); ld.energy=38000; ld.shape='DISK'; ld.size=42; aim(lo,(cx,cy,8))
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1450; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('FSTC neutral daylight world'); scene.world.color=(.22,.26,.32); scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'
scene.render.filepath=os.path.join(EVID,'fstc_exterior_preview.png')
os.makedirs(EVID,exist_ok=True)
scene.camera.data.lens=48
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
bpy.ops.render.render(write_still=True)

metadata={
 'building_id':ID,'name':'First Street Towers Central (FSTC)','asset':os.path.relpath(ASSET,ROOT).replace('\\','/'),
 'scene':SCENE_NAME,'collection':COLL_NAME,'objects':[OBJ_NAME],'geometry_vertices':len(obj.data.vertices),'geometry_faces':len(obj.data.polygons),
 'gis_feature':{'provider':'Purdue University BuildingShapes GIS FeatureServer','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':664,'retrieved':'2026-10-26','crs':'EPSG:4326 transformed to project local campus meters using AGENT.md approximate origin','original_ring_vertices':len(ring)-1,'used_outline_vertices':len(poly),'area_m2_projected':abs(area),'bounds_xy_m':[[min(p[0] for p in poly),max(p[0] for p in poly)],[min(p[1] for p in poly),max(p[1] for p in poly)]]},
 'dimensions':{'levels':7,'source':'Purdue GIS NUM_LEVELS=7 and CountOfFLO=7','story_height_m_estimate':story,'roof_height_m_estimate':ztop,'height_uncertainty':'GIS Extrution=46 has undocumented units; modeled floor-to-floor and roof heights are estimates, not surveyed values.'},
 'footprint_comparison':{'comparison':'Purdue GIS FID 664 vs OSM way 283274998 saved in osm_buildings_bbox_2026-10-26.json','gis_outline':'Official GIS outline used for structural walls. Projected area ~1481 m2; bounds recorded above.','osm_outline':'OSM polygon covers ~1720 m2 and extends farther south/west. Prior calculated intersection-over-union ~0.846 and Hausdorff distance ~4.24m.','uncertainty':'Official CAD/GIS outline and OSM roof/building outline disagree; source-specific outlines are preserved and not combined.'},
 'architecture_evidence':[{'provider':'Purdue University Residences','url':'https://www.housing.purdue.edu/my-housing/options/residence-halls/first-street.html','retrieved':'2026-10-26','supports':'Residential use, cluster rooms, central lounge/dinette and community kitchen. Bedrooms reported as 9 ft 8 in by 13 ft 9 in.'},{'provider':'Purdue University Residences photo','url':'https://www.housing.purdue.edu/images/get-reconnected-old-images/BrianTedeschi2.JPG','source_date':'2019','retrieved':'2026-10-26','supports':'Red-brown brick, pale stone entrance surround, arched entrance canopy and sign.'},{'provider':'Purdue University Emergency Preparedness','url':'https://www.purdue.edu/operations/emergency-preparedness/fst/','retrieved':'2026-10-26','supports':'Building identity and address, 1250 First Street.'}],
 'model_notes':['Portable procedural brick/stone/glass materials; no external texture dependency.','Main entrance is placed on the south-facing First Street side, based on the published address and 2019 photo; exact GIS door position is not provided and remains estimated.','Seven floors are source supported. Window spacing, wall detailing, parapet, story height and roof treatment are visual estimates.','Interior is a schematic illustration of documented room clusters and shared lounge/dinette, not an architectural plan.','Decorative facades/interior components are consolidated in the named object; expected scene and collection names preserved.'],
 'preview':'fstc_exterior_preview.png'}
with open(ASSET,'rb') as f: metadata['candidate_sha256']=hashlib.sha256(f.read()).hexdigest()
metadata['window_count_estimate']=window_count
with open(os.path.join(EVID,'evidence.json'),'w',encoding='utf-8') as f: json.dump(metadata,f,indent=2)
print('FSTC_BUILD_COMPLETE',json.dumps({'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'windows':window_count,'footprint_vertices':len(poly),'bbox':metadata['gis_feature']['bounds_xy_m'],'render':scene.render.filepath}))
