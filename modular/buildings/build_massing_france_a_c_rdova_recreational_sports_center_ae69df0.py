"""Build the CREC source asset from Purdue GIS and photo evidence.

Only the stable CREC asset is edited. Geometry keeps the existing campus-world
coordinate frame and exported collection contract.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
ASSET_ID='massing_france_a_c_rdova_recreational_sports_center_ae69df0'
ASSET=ROOT/'modular'/'buildings'/(ASSET_ID+'.blend')
AUDIT=ROOT/'audit'/'france_a_cordova_rec_center'
GIS_FILE=AUDIT/'purdue_crec_feature_315.json'
COLLECTION_NAME='Asset_'+ASSET_ID
SCENE_NAME='Building_'+ASSET_ID
LAT0=40.4274; LON0=-86.9137
feature=json.loads(GIS_FILE.read_text(encoding='utf-8'))['features'][0]
src=feature['geometry']['rings'][0]
ring=[((lon-LON0)*111412.84*math.cos(math.radians(LAT0)),(lat-LAT0)*111040.0) for lon,lat in src]
if len(ring)>1 and math.dist(ring[0],ring[-1])<1e-6: ring=ring[:-1]

def inside(p,poly=ring):
    x,y=p;c=False
    for (x1,y1),(x2,y2) in zip(poly,poly[1:]+poly[:1]):
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-15)+x1:c=not c
    return c
signed=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))
clockwise=signed<0

scene=bpy.context.scene
asset_coll=bpy.data.collections.get(COLLECTION_NAME)
if asset_coll is None:
    asset_coll=bpy.data.collections.new(COLLECTION_NAME);scene.collection.children.link(asset_coll)
for ob in list(asset_coll.objects):bpy.data.objects.remove(ob,do_unlink=True)
asset_coll['stable_asset_id']=ASSET_ID
asset_coll['source_feature_id']=315
asset_coll['coordinate_frame']='project campus-world meters, preserved legacy direct-link contract'
PRESENTATION='CREC | presentation only'
pres=bpy.data.collections.get(PRESENTATION)
if pres is None:pres=bpy.data.collections.new(PRESENTATION);scene.collection.children.link(pres)
for ob in list(pres.objects):bpy.data.objects.remove(ob,do_unlink=True)

def material(name,color,rough=.5,metal=0.0,noise=None,bump=.08):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    ns=m.node_tree.nodes;ls=m.node_tree.links;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    if noise:
        tex=ns.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=noise[0];tex.inputs['Detail'].default_value=4
        cr=ns.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(*noise[1],1);cr.color_ramp.elements[1].color=(*noise[2],1)
        ls.new(tex.outputs['Fac'],cr.inputs['Fac']);ls.new(cr.outputs['Color'],bs.inputs['Base Color'])
        bn=ns.new('ShaderNodeBump');bn.inputs['Strength'].default_value=bump;bn.inputs['Distance'].default_value=.025
        ls.new(tex.outputs['Fac'],bn.inputs['Height']);ls.new(bn.outputs['Normal'],bs.inputs['Normal'])
    return m,bs

brick,_=material('CREC | procedural Purdue red-brown brick',(.34,.065,.038),.82,noise=(13,(.19,.035,.025),(.44,.11,.065)),bump=.24)
stone,_=material('CREC | warm limestone and precast panels',(.55,.46,.34),.48,noise=(6,(.38,.31,.23),(.66,.56,.43)))
concrete,_=material('CREC | architectural concrete',(.48,.49,.47),.62,noise=(7,(.35,.37,.36),(.58,.58,.54)))
glass,glass_bs=material('CREC | blue-gray fritted curtainwall glass',(.075,.21,.31),.13,.62);glass_bs.inputs['Coat Weight'].default_value=.48;glass_bs.inputs['Coat Roughness'].default_value=.08
metal,_=material('CREC | dark bronze anodized aluminum',(.105,.13,.14),.26,.78)
roof,_=material('CREC | pale white-gray roof membrane',(.48,.51,.49),.72,.05,noise=(4,(.39,.41,.39),(.57,.60,.57)),bump=.07)
roof_legacy,_=material('CREC | legacy gym roof tone',(.23,.27,.26),.78)
roof_gym,_=material('CREC | recreation wing roof tone',(.38,.41,.38),.72)
roof_connector,_=material('CREC | atrium connector roof tone',(.29,.33,.33),.74)
dark,_=material('CREC | charcoal roof edge',(.13,.15,.16),.4,.48)
floor,_=material('CREC | interior terrazzo and concrete',(.56,.55,.50),.58,noise=(5,(.43,.43,.40),(.67,.65,.59)),bump=.06)
white,_=material('CREC | warm white interior wall',(.76,.75,.70),.78)
gold,_=material('CREC | Purdue gold track',(.78,.39,.055),.43)
maple,_=material('CREC | maple sports floor',(.66,.40,.20),.42)
water,wbs=material('CREC | blue recreation pool water',(.045,.32,.43),.12,.16);wbs.inputs['Transmission Weight'].default_value=.18
lane,_=material('CREC | pool and court line markings',(.9,.9,.83),.3,.1)
climb,cb=material('CREC | climbing wall panels',(.51,.49,.41),.72,noise=(4,(.39,.4,.37),(.62,.59,.52)))
red,_=material('CREC | Purdue red wayfinding',(.59,.12,.075),.44)

class Batch:
    def __init__(self,name,mats):self.name=name;self.mats=mats;self.v=[];self.f=[];self.mi=[]
    def poly(self,pts,mi=0):
        if len(pts)<3:return
        i=len(self.v);self.v.extend([tuple(p) for p in pts]);self.f.append(tuple(range(i,i+len(pts))));self.mi.append(mi)
    def quad(self,a,b,c,d,mi=0):self.poly([a,b,c,d],mi)
    def create(self):
        if not self.f:return None
        me=bpy.data.meshes.new(self.name+' | mesh');me.from_pydata(self.v,[],self.f)
        for m in self.mats:me.materials.append(m)
        me.update();ob=bpy.data.objects.new(self.name,me);asset_coll.objects.link(ob)
        for p,mi in zip(me.polygons,self.mi):p.material_index=mi
        ob['building_asset_id']=ASSET_ID;return ob

def mesh_obj(name,verts,faces,mat,coll=asset_coll):
    me=bpy.data.meshes.new(name+' | mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    ob=bpy.data.objects.new(name,me);coll.objects.link(ob);ob['building_asset_id']=ASSET_ID;return ob
def box(name,center,size,mat,coll=asset_coll,rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.dimensions=size;o.rotation_euler.z=rot
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    coll.objects.link(o);o.data.materials.append(mat);o['building_asset_id']=ASSET_ID;return o
def wall_quad(batch,a,b,z0,z1,n,mi=0,offset=.02,margin=0):
    ax,ay=a;bx,by=b;dx=bx-ax;dy=by-ay;L=math.hypot(dx,dy)
    if L<.08 or z1<=z0:return
    ux,uy=dx/L,dy/L;q0=(ax+ux*margin+n[0]*offset,ay+uy*margin+n[1]*offset);q1=(bx-ux*margin+n[0]*offset,by-uy*margin+n[1]*offset)
    batch.quad((q0[0],q0[1],z0),(q1[0],q1[1],z0),(q1[0],q1[1],z1),(q0[0],q0[1],z1),mi)
def height_at(x,y):
    if x>-705 and 78<y<149:return 15.65
    if y>166 and x>-766:return 14.8
    if x<-776 and 42<y<155:return 11.8
    if y<36:return 12.15
    if y<72 and x<-759:return 10.9
    if x>-720 and 140<y<166:return 13.6
    return 13.25

# Audit reference: every perimeter vertex follows Purdue Campus GIS feature 315.
ref=bpy.data.meshes.new('CREC | GIS perimeter reference mesh')
ref.from_pydata([(x,y,.035) for x,y in ring],[(i,(i+1)%len(ring)) for i in range(len(ring))],[]);ref.update()
rob=bpy.data.objects.new('CREC | source footprint reference (nonrendering)',ref);asset_coll.objects.link(rob)
rob.hide_render=True;rob.display_type='WIRE';rob['provider']='Purdue University Libraries GIS';rob['feature_id']=315;rob['source_crs']='EPSG:4326';rob['local_conversion']='documented Purdue project tangent-plane approximation'

# Exterior perimeter shell and facade, with historic brick wings and the light-filled east atrium.
walls=Batch('CREC | GIS-matched structural perimeter and facade', [brick,stone,concrete,glass,metal,dark])
bands=Batch('CREC | facade mullions, floor bands and reveals',[metal,stone,concrete,dark])
for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    ax,ay=a;bx,by=b;dx=bx-ax;dy=by-ay;L=math.hypot(dx,dy)
    if L<.12:continue
    mx=(ax+bx)/2;my=(ay+by)/2;h=height_at(mx,my);ux,uy=dx/L,dy/L
    n=(-uy,ux) if clockwise else (uy,-ux)
    east=n[0]>.5;west=n[0]<-.5;north=n[1]>.5;south=n[1]<-.5
    modern=east or (north and mx>-762) or (south and mx>-747 and my<56)
    base=1 if modern else 0
    atrium=east and mx>-706 and 78<my<141
    wall_quad(walls,a,b,0,3.22,n,base,.008)
    wall_quad(bands,a,b,0,.30,n,1 if modern else 0,.035)
    for lo in [3.25,6.48,9.71,12.94]:
        if lo>=h-.05:continue
        hi=min(lo+3.18,h)
        wall_quad(walls,a,b,lo,hi,n,base,.008)
        if L>3.2:
            margin=min(.56,L*.16)
            if atrium and hi-lo>2.4:
                # Preserve opaque stone spandrels and broad blue-gray fritted glazing between bronze piers.
                wall_quad(walls,a,b,lo+.18,hi-.18,n,3,.075,margin)
                bays=max(1,int((L-2*margin)/2.6))
                for k in range(bays+1):
                    t=margin+(L-2*margin)*k/bays;p=(ax+ux*t,ay+uy*t)
                    half=.055;z0=lo+.18;z1=hi-.18
                    e0=(p[0]-uy*half+n[0]*.11,p[1]+ux*half+n[1]*.11)
                    e1=(p[0]+uy*half+n[0]*.11,p[1]-ux*half+n[1]*.11)
                    bands.quad((e0[0],e0[1],z0),(e1[0],e1[1],z0),(e1[0],e1[1],z1),(e0[0],e0[1],z1),0)
                wall_quad(bands,a,b,lo+.08,lo+.19,n,0,.11,margin)
                wall_quad(bands,a,b,hi-.16,hi-.05,n,0,.11,margin)
            else:
                # Regular window bays; brick and stone retain strong piers rather than becoming a glazed box.
                z0=lo+.76;z1=min(hi-.53,lo+2.34)
                if z1>z0:
                    wall_quad(walls,a,b,z0,z1,n,3,.065,margin)
                    bays=max(1,int((L-2*margin)/2.55))
                    for k in range(bays+1):
                        t=margin+(L-2*margin)*k/bays;p=(ax+ux*t,ay+uy*t);half=.055
                        p0=(p[0]-uy*half+n[0]*.105,p[1]+ux*half+n[1]*.105)
                        p1=(p[0]+uy*half+n[0]*.105,p[1]-ux*half+n[1]*.105)
                        bands.quad((p0[0],p0[1],z0),(p1[0],p1[1],z0),(p1[0],p1[1],z1),(p0[0],p0[1],z1),0)
                    wall_quad(bands,a,b,z1-.06,z1+.06,n,0,.11,margin)
        # Readable floor bands, parapet fascia and service louvers on athletic wings.
        wall_quad(bands,a,b,lo-.08,lo+.08,n,1 if modern else 2,.04)
        if L>4.3 and (west or south) and lo>=6.0:
            for s in range(4):wall_quad(bands,a,b,lo+.62+s*.34,lo+.71+s*.34,n,0,.09,min(.78,L*.2))
    wall_quad(bands,a,b,h-.40,h,n,1 if modern else 3,.06)
walls.create();bands.create()

# GIS roof field cap: height bands are estimated from the official five-level program and orthophoto silhouette.
tris=tessellate_polygon([[Vector((x,y,0)) for x,y in ring]])
index={(round(x,5),round(y,5)):i for i,(x,y) in enumerate(ring)};faces=[]
for tri in tris:
    ids=[]
    for v in tri:
        if isinstance(v,int):
            ids.append(v);continue
        k=(round(v.x,5),round(v.y,5))
        if k not in index:k=min(index,key=lambda q:(q[0]-v.x)**2+(q[1]-v.y)**2)
        ids.append(index[k])
    if len(set(ids))==3:faces.append(tuple(reversed(ids)))
roofverts=[(x,y,height_at(x,y)) for x,y in ring]
roofobj=mesh_obj('CREC | GIS-footprint roof outline',roofverts,faces,roof)
for m in [roof_legacy,roof_gym,roof_connector]:roofobj.data.materials.append(m)
roofobj['height_status']='Estimated from the five-level published program and roof silhouette; no surveyed roof elevations.'

# Major stepped roof volumes digitized from current orthophoto. Each corner was checked against the GIS polygon.
zones=[
 ('north recreation wing',[(-765,168),(-704,168),(-704,201),(-765,201)],14.85),
 ('west legacy gym',[(-780,120),(-751,120),(-751,161),(-780,161)],12.45),
 ('central fitness wing',[(-750,120),(-718,120),(-718,160),(-750,160)],13.95),
 ('east glazed atrium',[(-718,82),(-702,82),(-702,150),(-718,150)],15.65),
 ('south activity gym',[(-755,26),(-718,26),(-718,116),(-755,116)],13.15),
 ('northeast connector',[(-720,158),(-702,158),(-702,183),(-720,183)],14.1),
]
for polyface in roofobj.data.polygons:
    c=polyface.center;pt=(c.x,c.y);selected=None
    for name,poly,top in zones:
        if inside(pt,poly):selected=name;break
    if selected:
        polyface.material_index=1 if 'legacy' in selected else (3 if 'central' in selected or 'atrium' in selected or 'connector' in selected else 2)
roofvol=Batch('CREC | orthophoto-guided stepped roof masses',[brick,stone,concrete,glass,roof,dark,roof_legacy,roof_gym,roof_connector])
for name,poly,top in zones:
    if not all(inside(p) for p in poly):raise RuntimeError(f'Roof zone extends outside GIS footprint: {name}')
    bottom=11.0;n=len(poly)
    for a,b in zip(poly,poly[1:]+poly[:1]):
        roofvol.quad((a[0],a[1],bottom),(b[0],b[1],bottom),(b[0],b[1],top),(a[0],a[1],top),1)
    topmi=6 if 'legacy' in name else (8 if 'central' in name or 'atrium' in name or 'connector' in name else 7)
    i=len(roofvol.v);roofvol.v.extend([(x,y,top) for x,y in poly]);roofvol.f.append(tuple(range(i,i+n)));roofvol.mi.append(topmi)
    for a,b in zip(poly,poly[1:]+poly[:1]):
        dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);nn=(-dy/L,dx/L)
        wall_quad(roofvol,a,b,top-.05,top+.06,nn,5,.08)
roofvol.create()
# Roof plants, skylight curbs and mechanical housings are schematic; no roof survey identifies these components.
for j,(x,y,sx,sy,z,h) in enumerate([
 (-744,185,3.4,1.8,14.9,.9),(-730,175,2.5,2.1,14.9,1.1),(-758,145,2.0,1.5,12.5,.9),
 (-738,141,2.2,1.6,14.0,.8),(-708,132,1.8,1.8,15.65,.35),(-734,104,3.0,1.4,13.2,.8),
 (-741,66,2.3,1.7,13.2,1.0),(-725,48,2.7,1.8,13.2,.9),(-750,32,2.0,1.4,13.2,.75)]):
    box(f'CREC | rooftop mechanical housing {j+1}',(x,y,z+h/2),(sx,sy,h),dark)
    box(f'CREC | rooftop louver detail {j+1}',(x+sx/2+.04,y,z+h*.55),(.08,sy*.72,h*.45),metal)

# Interior floors and recognizable sports program, visible through the atrium and selected bays.
def floor_plate(name,poly,z,mat):
    verts=[(x,y,z) for x,y in poly]
    face=list(range(len(verts)))
    return mesh_obj(name,verts,[face],mat)
for name,poly,z,mat in [
 ('atrium lobby', [(-715,87),(-703,87),(-703,143),(-715,143)],.24,floor),
 ('west gym floor',[(-777,123),(-753,123),(-753,157),(-777,157)],.22,maple),
 ('north courts',[(-763,171),(-707,171),(-707,198),(-763,198)],.22,maple),
 ('south courts',[(-751,32),(-721,32),(-721,112),(-751,112)],.22,maple),
 ('central fitness floor',[(-748,122),(-721,122),(-721,157),(-748,157)],.22,floor)]:
    floor_plate('CREC | interior '+name,poly,z,mat)

inside_geo=Batch('CREC | interior courts, fitness bays and wayfinding', [lane,red,white,gold,climb,water,metal,stone])
def line2(a,b,z=.28,w=.09,mi=0):
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    if L<.01:return
    nx=-dy/L*w/2;ny=dx/L*w/2
    inside_geo.quad((a[0]+nx,a[1]+ny,z),(b[0]+nx,b[1]+ny,z),(b[0]-nx,b[1]-ny,z),(a[0]-nx,a[1]-ny,z),mi)
def rect_lines(x1,y1,x2,y2,z=.28,mi=1):
    line2((x1,y1),(x2,y1),z,.22,mi);line2((x2,y1),(x2,y2),z,.22,mi)
    line2((x2,y2),(x1,y2),z,.22,mi);line2((x1,y2),(x1,y1),z,.22,mi)
# Recognizable multi-court basketball layouts with hardwood, perimeter lines, keys and center circles.
for x1,y1,x2,y2 in [(-775,125,-755,155),(-761,173,-738,196),(-733,173,-710,196),(-750,35,-722,58),(-750,61,-722,84),(-750,87,-722,110)]:
    rect_lines(x1,y1,x2,y2)
    cx=(x1+x2)/2;cy=(y1+y2)/2
    rect_lines(cx-2.0,cy-3.1,cx+2.0,cy+3.1,.29,1)
    # Center-circle ring approximated with 32 short strips.
    pts=[(cx+1.8*math.cos(k*math.tau/32),cy+1.8*math.sin(k*math.tau/32)) for k in range(33)]
    for a,b in zip(pts,pts[1:]):line2(a,b,.29,.12,1)
# Central swimming and aquatics zone; edge tiles, four lanes, lane ropes and deck.
pool_poly=[(-743,88),(-727,88),(-727,112),(-743,112)]
floor_plate('CREC | aquatics pool deck', [(-747,84),(-723,84),(-723,116),(-747,116)],.25,stone)
floor_plate('CREC | lap pool basin',pool_poly,.29,water)
for y in [92,98,104,110]:line2((-741.5,y),(-728.5,y),.34,.18,1)
for x in [-741,-738,-735,-732,-729]:
    box('CREC | pool lane float',(x,100,.39),(.16,22,.12),lane)
# Climbing wall panel and colored holds, placed in north-central recreation hall.
inside_geo.quad((-729,162,.5),(-713,162,.5),(-713,162,10.8),(-729,162,10.8),4)
for row in range(7):
    for col in range(5):
        x=-727.5+col*3.0;y=161.72;z=1.1+row*1.35+(col%2)*.35
        box('CREC | climbing wall hold', (x,y,z),(.28,.18,.24),[red,gold,stone][(row+col)%3])
# Atrium interior monumental stair flight and landings, layered at the connector.
for k in range(18):
    z=.3+k*.17;y=96+k*.53
    box(f'CREC | atrium stair tread {k+1}',(-710.4,y,z), (4.0,.63,.16),stone)
for z,y in [(3.4,107),(6.7,119),(10.0,131)]:
    box('CREC | atrium stair landing',(-710.4,y,z),(4.0,3.0,.22),concrete)
# Slim glazed curtainwall mullion rhythm on the east atrium frontage.
facade=Batch('CREC | east atrium mullions and translucent spandrels',[metal,glass,stone])
for y in [84,87,90,93,96,99,102,105,108,111,114,117,120,123,126,129,132,135,138,141,144,147]:
    facade.quad((-702.8,y,.35),(-702.8,y,15.3),(-702.62,y,15.3),(-702.62,y,.35),0)
for z in [3.25,6.48,9.71,12.94]:
    facade.quad((-703.0,82,z),(-703.0,150,z),(-702.58,150,z),(-702.58,82,z+.16),2)
facade.create()
# The source photographs identify a dominant, three-storey glazed corner. Place the
# curtain wall just outside the GIS outline so it remains a legible facade volume.
atr_x=-691.70;atr_y0=88.0;atr_y1=132.0;atr_z0=.55;atr_z1=15.28
atr=Batch('CREC | dominant three-storey atrium curtain wall',[glass,metal,stone])
atr.quad((atr_x,atr_y0,atr_z0),(atr_x,atr_y1,atr_z0),(atr_x,atr_y1,atr_z1),(atr_x,atr_y0,atr_z1),0)
for y in [atr_y0,atr_y1]+[atr_y0+k*3.0 for k in range(1,15)]:
    atr.quad((atr_x+.08,y-.075,atr_z0),(atr_x+.08,y+.075,atr_z0),(atr_x+.08,y+.075,atr_z1),(atr_x+.08,y-.075,atr_z1),1)
for z in [atr_z0,5.35,10.1,14.75,atr_z1]:
    atr.quad((atr_x+.09,atr_y0,z-.075),(atr_x+.09,atr_y1,z-.075),(atr_x+.09,atr_y1,z+.075),(atr_x+.09,atr_y0,z+.075),1)
# Return walls wrap the two atrium corners, producing a deep glazed volume.
for y,sign in [(atr_y0,-1),(atr_y1,1)]:
    yy=y+sign*.08
    atr.quad((-716,yy,atr_z0),(atr_x,yy,atr_z0),(atr_x,yy,atr_z1),(-716,yy,atr_z1),0)
    for x in [-713,-709,-705,-701,-697,-693]:
        atr.quad((x-.06,yy+sign*.08,atr_z0),(x+.06,yy+sign*.08,atr_z0),(x+.06,yy+sign*.08,atr_z1),(x-.06,yy+sign*.08,atr_z1),1)
    for z in [5.35,10.1,14.75]:
        atr.quad((-716,yy+sign*.09,z-.06),(atr_x,yy+sign*.09,z-.06),(atr_x,yy+sign*.09,z+.06),(-716,yy+sign*.09,z+.06),1)
# Warm stone corner piers frame the clear glass, echoing the photographed cream facade.
for y in [atr_y0-.34,atr_y1+.34]:
    box('CREC | atrium stone end pier',(atr_x+.10,y,7.8),(.52,.68,15.2),stone)
atr.create()
# Tall projecting roof eyebrow crowns the atrium corner; the soffit reads clearly against glass.
box('CREC | monumental atrium roof eyebrow',(-692.52,110,15.52),(10.0,50.0,.86),stone)
box('CREC | atrium eyebrow bronze soffit',(-692.48,110,15.02),(9.6,49.4,.13),dark)
# The neighboring east-facing brick recreation wing has true red masonry and broad ventilation louvers.
box('CREC | east brick recreation wing',(-691.58,150.5,6.25),(.24,27.0,12.4),brick)
for z in [3.4,7.0,10.4]:
    box('CREC | east brick wing ventilation louver',(-691.39,150.5,z),(.08,3.5,1.05),metal)
# Ground-level entry is a distinct glazed portal below the tall atrium.
box('CREC | east entry dark portal frame',(-690.93,110,1.85),(.28,14.0,3.55),dark)
for y in [104.5,107.2,110.0,112.8,115.5]:
    box('CREC | east entry glazed door',( -690.73,y,1.65),(.10,2.55,2.8),glass)
    box('CREC | east entry bronze door stile',(-690.66,y,1.65),(.12,.07,2.8),metal)
box('CREC | entry nameplate',(-690.62,110,4.15),(.18,22,.78),dark)
label=bpy.data.curves.new('CREC | entry sign lettering','FONT');label.body='FRANCE A. CÓRDOVA  •  RECREATIONAL SPORTS CENTER';label.size=.34;label.extrude=.008
label_obj=bpy.data.objects.new('CREC | entry sign lettering',label);asset_coll.objects.link(label_obj)
label_obj.location=(-690.50,99.5,3.98);label_obj.rotation_euler=(math.pi/2,0,math.pi/2);label_obj.data.materials.append(lane)
box('CREC | entry lower canopy',(-691.05,110,4.65),(3.5,26.0,.38),stone)
box('CREC | entry lower canopy dark soffit',(-691.0,110,4.40),(3.2,25.8,.10),dark)
# Orthophoto-guided roof panel joints stay within each stepped roof zone.
for zone_name,poly,top in zones:
    x1=min(p[0] for p in poly);x2=max(p[0] for p in poly)
    y1=min(p[1] for p in poly);y2=max(p[1] for p in poly)
    for y in range(int(y1+5),int(y2-2),8):
        box('CREC | roof membrane panel seam',( (x1+x2)/2,y,top+.02),(x2-x1-.6,.045,.04),concrete)
inside_geo.create()

# East entrance: projecting pale stone canopy, glazing vestibule, flanking brickwork, sign and doors.
box('CREC | entry vestibule awning',(-702.5,114,4.65),(2.9,28.0,.34),stone)
box('CREC | vestibule awning soffit',(-702.46,114,4.43),(2.75,27.8,.08),dark)
box('CREC | entry vestibule sill',(-701.6,114,.45),(2.4,49,.34),stone)
for y in [91,97,103,109,115,121,127,133,139]:
    box('CREC | entry door leaf',(-702.2,y,1.7),(.12,2.05,2.8),glass)
    box('CREC | door bronze stile',(-702.28,y-1.0,1.7),(.10,.08,2.8),metal)
box('CREC | entry nameplate',(-702.06,114,11.95),(.16,24,.8),dark)
label=bpy.data.curves.new('CREC | entry sign lettering','FONT');label.body='FRANCE A. CÓRDOVA  •  RECREATIONAL SPORTS CENTER';label.size=.39;label.extrude=.006
label_obj=bpy.data.objects.new('CREC | entry sign lettering',label);asset_coll.objects.link(label_obj)
label_obj.location=(-701.93,102.5,11.78);label_obj.rotation_euler=(math.pi/2,0,math.pi/2);label_obj.data.materials.append(lane)

# Localized plazas and accessible east entry steps; site surfaces stay within the building setting.
box('CREC | east entry arrival terrace',(-697.1,114,.04),(8.0,65,.08),concrete)
for k in range(5):
    box(f'CREC | east entry broad stair {k+1}',(-699.4-k*.34,114,.10+k*.16),(.72,20,.18),stone)
for y in range(73,155,5):
    box('CREC | plaza paving joint',(-695.2,y,.081),(.018,.08,.01),dark)

# Metadata captures provenance and uncertainty in the asset itself for downstream review.
asset_coll['source_summary']='Purdue campus GIS feature 315; Historic Building Database; Purdue RecWell facility fact sheet; Moody Nolan project page; geotagged Julian Herzog Wikimedia photo; Indiana Current Imagery orthophoto.'
asset_coll['interpretation']='Exterior massing follows the GIS footprint. The east glass atrium, pale entrance canopy, brick legacy wings and sports interiors are photo/program-informed reconstructions.'
asset_coll['uncertainties']='Roof step heights and internal partitions are approximate; official sources establish a five-level, multi-gym/pool/climbing facility but no measured floor plan or elevation was found. Orthophoto date/resolution are not a survey.'

# Cameras/lights live in the presentation collection, separate from the exported asset collection.
def aim(obj,point):obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,lens=48):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);pres.objects.link(o);o.location=loc;aim(o,target);d.lens=lens;return o
def area(name,loc,target,power,color,size):
    d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);pres.objects.link(o);o.location=loc;aim(o,target);d.energy=power;d.color=color;d.shape='DISK';d.size=size
area('CREC | warm east-entry key',(-650,72,50),(-710,114,7),1400,(1.0,.79,.59),45)
area('CREC | cool sky fill',(-745,260,62),(-740,105,7),900,(.62,.76,1.0),65)
area('CREC | south facade fill',(-824,-26,45),(-745,85,7),550,(1.0,.88,.72),48)
# Neutral ground connects the roof study and anchors the entry view; presentation only.
box('CREC | context ground, presentation only',(-740,110,-.18),(380,420,.36),concrete,pres)
cam=camera('CREC | east atrium oblique street view',(-635,35,10),(-697,110,8),50)
scene.camera=cam
# Labels are in the presentation collection only. They appear in the roof-off
# program diagram to distinguish research-supported functions from measured plans.
for label_text,x,y in [
 ('WEST COURTS',-777,145),('NORTH COURTS',-758,190),('FITNESS',-746,144),
 ('AQUATICS',-741,92),('ACTIVITY COURTS',-749,42),('CLIMBING',-728,169)]:
    curve=bpy.data.curves.new('CREC | cutaway label','FONT');curve.body=label_text;curve.size=2.0;curve.extrude=0
    obj=bpy.data.objects.new('CREC | program label | '+label_text,curve);pres.objects.link(obj)
    obj.location=(x-7.5,y-1.0,.74);obj.data.materials.append(lane)
    box('CREC | cutaway label plate | '+label_text,(x,y,.64),(17.0,3.6,.10),dark,pres)
scene.render.engine='CYCLES';scene.cycles.samples=36
scene.render.resolution_x=1500;scene.render.resolution_y=920;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world.color=(.11,.14,.20)
scene.world.use_nodes=True
background=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs['Color'].default_value=(.13,.18,.25,1)
background.inputs['Strength'].default_value=.28
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.6
scene.render.filepath=str(AUDIT/'crec_east_entry.png')
bpy.ops.render.render(write_still=True)

# Second evidence view emphasizes GIS footprint and orthophoto-matched roof stepping.
cam2=camera('CREC | orthophoto roof study',(-761,113,275),(-739,113,2),55)
cam2.data.type='ORTHO';cam2.data.ortho_scale=300
scene.camera=cam2;scene.render.resolution_x=1000;scene.render.resolution_y=1000
scene.render.filepath=str(AUDIT/'crec_roof_overview.png');bpy.ops.render.render(write_still=True)

# Program evidence: a roof-off top-down cutaway makes schematic, source-supported activity zones visible.
roof_objects=[o for o in asset_coll.objects if o.name in {
 'CREC | GIS-footprint roof outline','CREC | orthophoto-guided stepped roof masses'}]
saved_hide={o.name:o.hide_render for o in roof_objects}
for o in roof_objects:o.hide_render=True
cam3=camera('CREC | schematic interior program cutaway',(-739,113,260),(-739,113,0),50)
cam3.data.type='ORTHO';cam3.data.ortho_scale=235
scene.camera=cam3;scene.render.resolution_x=1250;scene.render.resolution_y=1050
scene.render.filepath=str(AUDIT/'crec_interior_cutaway.png');bpy.ops.render.render(write_still=True)
for o in roof_objects:o.hide_render=saved_hide[o.name]

# Final saved source opens focused on the front door view; original path and collection are retained.
scene.camera=cam;scene.render.resolution_x=1500;scene.render.resolution_y=920
scene.render.filepath='//crec_east_entry.png'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('CREC_BUILD_OK',ASSET, 'objects=',len(asset_coll.objects),'gis_vertices=',len(ring))

