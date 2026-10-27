import bpy, json, math, os, hashlib
from pathlib import Path
from mathutils import Vector

ASSET = Path('modular/buildings/massing_house_1089876362_14ecd2c.blend').resolve()
AUDIT = Path('audit/kappa_delta_rho').resolve()
GEO = AUDIT/'sources/purdue_gis_fid801.geojson'
EXPORT = AUDIT/'previews'
EXPORT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
obj=bpy.data.objects.get('House_1089876362')
if obj is None: raise RuntimeError('Stable source object House_1089876362 missing')
asset_coll=bpy.data.collections.get('Asset_massing_house_1089876362_14ecd2c')
if asset_coll is None: raise RuntimeError('Stable asset collection missing')
# Remove only generated content from this building's previous local iteration.
for o in list(bpy.data.objects):
    if o.name.startswith('KDRDetail_') or o.name.startswith('KDRInterior_') or o.name.startswith('KDRPreview_'):
        bpy.data.objects.remove(o, do_unlink=True)
# Keep all scene objects in their stable collection; the collection stays the library export root.
def link_asset(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    asset_coll.objects.link(o)

# GIS FID 801 is a single ring from the Purdue BuildingShapesZip4 layer; convert WGS84 to project meters.
geo=json.loads(GEO.read_text(encoding='utf-8-sig'))['features'][0]
ring_ll=geo['geometry']['coordinates'][0]
if ring_ll[0] == ring_ll[-1]: ring_ll=ring_ll[:-1]
lat0,lon0=40.4274,-86.9137
sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
ring=[((lon-lon0)*sx,(lat-lat0)*sy) for lon,lat in ring_ll]
area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
if area < 0: ring.reverse()
xmin=min(x for x,y in ring); xmax=max(x for x,y in ring); ymin=min(y for x,y in ring); ymax=max(y for x,y in ring)
mid_x=(xmin+xmax)/2; mid_y=(ymin+ymax)/2
wall_h=7.5; eave_z=7.62; ridge_z=11.4

# Procedural, packed-in-node materials; all facade colors beyond the aerial roof tone are explicitly estimates.
def mat_principled(name,color,rough=0.75,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1.0); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value=(*color,1.0); bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal; nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m,bs,nt

brick,bs,nt=mat_principled('KDR_Red_Brick_Estimate',(0.28,0.075,0.048),0.82)
tc=nt.nodes.new('ShaderNodeTexCoord'); btex=nt.nodes.new('ShaderNodeTexBrick')
btex.inputs['Scale'].default_value=1.0; btex.inputs['Brick Width'].default_value=0.42; btex.inputs['Row Height'].default_value=0.21
btex.inputs['Mortar Size'].default_value=0.018; btex.inputs['Mortar Smooth'].default_value=0.025
btex.inputs['Color1'].default_value=(0.34,0.085,0.052,1); btex.inputs['Color2'].default_value=(0.24,0.048,0.032,1); btex.inputs['Mortar'].default_value=(0.40,0.33,0.26,1)
nt.links.new(tc.outputs['UV'],btex.inputs['Vector']); nt.links.new(btex.outputs['Color'],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.12; bump.inputs['Distance'].default_value=0.012
nt.links.new(btex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

# The NPS Photo 37 print is monochrome: it supports the contrast between pale
# wall fields and dark Tudor framing, but not the actual hue or exact wall finish.
timber,tbs,tnt=mat_principled('KDR_Tudor_Timber_Photo37_Estimate',(0.045,0.035,0.030),0.78)
wood_noise=tnt.nodes.new('ShaderNodeTexNoise'); wood_noise.inputs['Scale'].default_value=7.0; wood_noise.inputs['Detail'].default_value=2.0
wood_ramp=tnt.nodes.new('ShaderNodeValToRGB'); wood_ramp.color_ramp.elements[0].color=(0.018,0.014,0.012,1); wood_ramp.color_ramp.elements[1].color=(0.075,0.052,0.035,1)
tnt.links.new(wood_noise.outputs['Fac'],wood_ramp.inputs['Fac']); tnt.links.new(wood_ramp.outputs['Color'],tbs.inputs['Base Color'])
light_wall,lbs,lnt=mat_principled('KDR_Light_Wall_Infill_Photo37_Estimate',(0.56,0.49,0.37),0.88)
wall_noise=lnt.nodes.new('ShaderNodeTexNoise'); wall_noise.inputs['Scale'].default_value=5; wall_noise.inputs['Detail'].default_value=2
wall_ramp=lnt.nodes.new('ShaderNodeValToRGB'); wall_ramp.color_ramp.elements[0].color=(0.49,0.44,0.36,1); wall_ramp.color_ramp.elements[1].color=(0.63,0.57,0.46,1)
lnt.links.new(wall_noise.outputs['Fac'],wall_ramp.inputs['Fac']); lnt.links.new(wall_ramp.outputs['Color'],lbs.inputs['Base Color'])

slate,bs2,nt2=mat_principled('KDR_Blue_Charcoal_Slate_Roof_Estimate',(0.075,0.09,0.105),0.78)
tc2=nt2.nodes.new('ShaderNodeTexCoord'); noise=nt2.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=38; noise.inputs['Detail'].default_value=3; noise.inputs['Roughness'].default_value=0.72
ramp=nt2.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=0.22; ramp.color_ramp.elements[0].color=(0.035,0.045,0.06,1); ramp.color_ramp.elements[1].position=0.8; ramp.color_ramp.elements[1].color=(0.15,0.17,0.19,1)
nt2.links.new(tc2.outputs['Generated'],noise.inputs['Vector']); nt2.links.new(noise.outputs['Fac'],ramp.inputs['Fac']); nt2.links.new(ramp.outputs['Color'],bs2.inputs['Base Color'])
bump2=nt2.nodes.new('ShaderNodeBump'); bump2.inputs['Strength'].default_value=0.18; bump2.inputs['Distance'].default_value=0.018
nt2.links.new(noise.outputs['Fac'],bump2.inputs['Height']); nt2.links.new(bump2.outputs['Normal'],bs2.inputs['Normal'])

limestone,bs3,nt3=mat_principled('KDR_Limestone_Trim_Estimate',(0.62,0.56,0.45),0.72)
noise3=nt3.nodes.new('ShaderNodeTexNoise'); noise3.inputs['Scale'].default_value=16; noise3.inputs['Detail'].default_value=2
b3=nt3.nodes.new('ShaderNodeBump'); b3.inputs['Strength'].default_value=0.12; b3.inputs['Distance'].default_value=0.012
nt3.links.new(noise3.outputs['Fac'],b3.inputs['Height']); nt3.links.new(b3.outputs['Normal'],bs3.inputs['Normal'])
trim,bs4,nt4=mat_principled('KDR_Painted_Window_Trim_Estimate',(0.82,0.78,0.67),0.48)
glass,bs5,nt5=mat_principled('KDR_Glass_Dark_Blue',(0.045,0.09,0.13),0.16,0.18)
bs5.inputs['IOR'].default_value=1.46
wood,bs6,nt6=mat_principled('KDR_Stained_Door_Wood_Estimate',(0.105,0.035,0.018),0.55)
no=nt6.nodes.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value=5; no.inputs['Detail'].default_value=3
bu=nt6.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value=0.25; bu.inputs['Distance'].default_value=0.03
nt6.links.new(no.outputs['Fac'],bu.inputs['Height']); nt6.links.new(bu.outputs['Normal'],bs6.inputs['Normal'])
interior_floor,bs7,nt7=mat_principled('KDR_Interior_Wood_Schematic',(0.24,0.12,0.055),0.64)
no7=nt7.nodes.new('ShaderNodeTexNoise'); no7.inputs['Scale'].default_value=4.0; no7.inputs['Detail'].default_value=2
r7=nt7.nodes.new('ShaderNodeValToRGB'); r7.color_ramp.elements[0].color=(0.12,0.05,0.02,1); r7.color_ramp.elements[1].color=(0.39,0.20,0.08,1)
nt7.links.new(no7.outputs['Fac'],r7.inputs['Fac']); nt7.links.new(r7.outputs['Color'],bs7.inputs['Base Color'])
interior_wall,_,_=mat_principled('KDR_Interior_Partition_Schematic',(0.66,0.59,0.49),0.83)

# Rebuild stable object from authoritative GIS wall ring; keep its name, scene, collection, and identity.
verts=[(x,y,0.0) for x,y in ring]+[(x,y,wall_h) for x,y in ring]
n=len(ring)
faces=[]
for i in range(n): faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
faces.append(tuple(reversed(range(n))))
faces.append(tuple(range(n,2*n)))
newmesh=bpy.data.meshes.new('House_1089876362_GIS_footprint_shell')
newmesh.from_pydata(verts,[],faces); newmesh.materials.clear(); newmesh.materials.append(light_wall); newmesh.materials.append(limestone)
newmesh.update()
for i,p in enumerate(newmesh.polygons):
    p.material_index=1 if i==len(faces)-1 else 0
# Give each wall a metric UV map so the brick courses run horizontally and stay consistent
# despite the source polygon being stored in project-wide coordinates near Y=1,000 m.
uv=newmesh.uv_layers.new(name='KDR_Wall_UV_Metric')
for i,poly in enumerate(newmesh.polygons):
    if i<n:
        a=ring[i]; b=ring[(i+1)%n]; edge_len=math.hypot(b[0]-a[0],b[1]-a[1])
        coords=((0,0),(edge_len,0),(edge_len,wall_h),(0,wall_h))
    else:
        coords=tuple((verts[v][0]-xmin,verts[v][1]-ymin) for v in poly.vertices)
    for loop_index,coord in zip(poly.loop_indices,coords): uv.data[loop_index].uv=coord
obj.data=newmesh; obj.name='House_1089876362'; obj.location=(0,0,0); obj.rotation_euler=(0,0,0); obj.scale=(1,1,1); link_asset(obj)

# Batcher for many small architectural pieces; keep the resulting library compact.
class MeshBatch:
    def __init__(self,name,material): self.name=name; self.material=material; self.v=[]; self.f=[]
    def box(self,center,t,norm,width,depth,height):
        t=Vector((t[0],t[1],0)).normalized(); norm=Vector((norm[0],norm[1],0)).normalized(); c=Vector(center)
        base=len(self.v)
        for sz in (-1,1):
            for sy2 in (-1,1):
                for sx2 in (-1,1):
                    q=c+t*(sx2*width/2)+norm*(sy2*depth/2)+Vector((0,0,sz*height/2)); self.v.append(tuple(q))
        # index order: bottom BL, BR, back? two axes; outward normals recomputed below
        self.f += [(base+0,base+1,base+3,base+2),(base+4,base+6,base+7,base+5),(base+0,base+4,base+5,base+1),(base+2,base+3,base+7,base+6),(base+0,base+2,base+6,base+4),(base+1,base+5,base+7,base+3)]
    def beam(self,p1,p2,width,depth,normal):
        a=Vector(p1); b=Vector(p2); nrm=Vector((normal[0],normal[1],0)).normalized()
        tangent=(b-a).normalized(); across=tangent.cross(nrm).normalized(); center=(a+b)/2; half_len=(b-a).length/2
        base=len(self.v)
        for nside in (-1,1):
            for aside in (-1,1):
                for along in (-1,1):
                    q=center+tangent*(along*half_len)+across*(aside*width/2)+nrm*(nside*depth/2)
                    self.v.append(tuple(q))
        self.f += [(base+0,base+1,base+3,base+2),(base+4,base+6,base+7,base+5),(base+0,base+4,base+5,base+1),(base+2,base+3,base+7,base+6),(base+0,base+2,base+6,base+4),(base+1,base+5,base+7,base+3)]
    def prism(self,points):
        base=len(self.v); self.v.extend(points); k=len(points)//2
        self.f.append(tuple(base+i for i in reversed(range(k))))
        self.f.append(tuple(base+k+i for i in range(k)))
        for i in range(k): self.f.append((base+i,base+(i+1)%k,base+k+(i+1)%k,base+k+i))
    def polygon(self,points):
        base=len(self.v); self.v.extend(points); self.f.append(tuple(base+i for i in range(len(points))))
    def thick_panel(self,points,thickness=0.16):
        # Turn each inferred roof plane into a closed, thin slab. This avoids
        # leaving single-sided open surfaces in the exported roof mesh.
        pts=[Vector(p) for p in points]
        normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized()
        half=thickness/2
        self.prism([tuple(p-normal*half) for p in pts]+[tuple(p+normal*half) for p in pts])
    def create(self,collection=asset_coll):
        if not self.v: return None
        me=bpy.data.meshes.new(self.name+'_Mesh'); me.from_pydata(self.v,[],self.f); me.materials.append(self.material); me.update()
        for p in me.polygons: p.material_index=0
        o=bpy.data.objects.new(self.name,me); collection.objects.link(o)
        return o

trimB=MeshBatch('KDRDetail_Architectural_Trim',trim)
stoneB=MeshBatch('KDRDetail_Limestone',limestone)
glassB=MeshBatch('KDRDetail_Window_Glazing',glass)
woodB=MeshBatch('KDRDetail_Woodwork',wood)
roofB=MeshBatch('KDRDetail_Roof',slate)
gableB=MeshBatch('KDRDetail_Tudor_Gables',light_wall)
timberB=MeshBatch('KDRDetail_Tudor_HalfTimber',timber)
interiorB=MeshBatch('KDRInterior_Schematic_Partitions',interior_wall)
floorB=MeshBatch('KDRInterior_Schematic_Floor',interior_floor)
brickDetailB=MeshBatch('KDRDetail_Chimneys',brick)

# Structural roof inferred from the 2023 Indiana orthophoto: long north-south central ridge and hipped ends.
over=0.42; xl=xmin-over; xr=xmax+over; yb=ymin-over; yt=ymax+over; mx=(xl+xr)/2
y1=yb; y2=yt
roofB.thick_panel([(xl,yb,eave_z),(xl,yt,eave_z),(mx,y2,ridge_z),(mx,y1,ridge_z)])
roofB.thick_panel([(mx,y1,ridge_z),(mx,y2,ridge_z),(xr,yt,eave_z),(xr,yb,eave_z)])
# The directly identified Photo 37 shows a steep gable end; the opposite end
# is modeled as the corresponding simple roof closure but remains unverified.
gableB.thick_panel([(xl,yt,eave_z),(xr,yt,eave_z),(mx,yt,ridge_z)],0.22)
gableB.thick_panel([(xl,yb,eave_z),(mx,yb,ridge_z),(xr,yb,eave_z)],0.22)

# Cornice, foundation and continuous gutters follow each mapped wall edge.
for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
    if length<0.35: continue
    t=(dx/length,dy/length); outward=(dy/length,-dx/length); c=((a[0]+b[0])/2,(a[1]+b[1])/2)
    trimB.box((c[0],c[1],0.32),t,outward,length,0.16,0.34)
    trimB.box((c[0],c[1],7.32),t,outward,length,0.18,0.24)
# Roof fascia/gutter on long eaves and ridge cap.
for x in (xl,xr):
    trimB.box((x,(yb+yt)/2,eave_z-0.05),(0,1),(1 if x==xl else -1,0),0.12,0.16,0.28)
roofB.box((mx,(y1+y2)/2,ridge_z+0.08),(0,1),(1,0),0.28,0.24,0.12)

# Period Revival window pattern is a visual estimate; regular sash openings are placed on the long elevations.
def add_window(center, tangent, outward, width=1.28, height=1.82, shutter=False):
    zc=center[2]; cxy=(center[0],center[1]); off=0.09
    # dark glass, trim frame, center rails and 6-over-6 style muntins
    glassB.box((cxy[0]+outward[0]*off,cxy[1]+outward[1]*off,zc),tangent,outward,width-0.18,0.055,height-0.18)
    # perimeter casing
    for s in (-1,1):
        trimB.box((cxy[0]+outward[0]*(off+0.04)+tangent[0]*s*(width/2-0.04),cxy[1]+outward[1]*(off+0.04)+tangent[1]*s*(width/2-0.04),zc),tangent,outward,0.10,0.14,height)
    for s in (-1,1): trimB.box((cxy[0]+outward[0]*(off+0.04),cxy[1]+outward[1]*(off+0.04),zc+s*(height/2-0.04)),tangent,outward,width,0.14,0.10)
    trimB.box((cxy[0]+outward[0]*(off+0.08),cxy[1]+outward[1]*(off+0.08),zc),tangent,outward,0.07,0.16,height-0.18)
    trimB.box((cxy[0]+outward[0]*(off+0.08),cxy[1]+outward[1]*(off+0.08),zc),tangent,outward,width-0.18,0.16,0.07)
    for s in (-1,1): trimB.box((cxy[0]+outward[0]*(off+0.1),cxy[1]+outward[1]*(off+0.1),zc+s*height/4),tangent,outward,width-0.18,0.14,0.045)
    for s in (-1,1): trimB.box((cxy[0]+outward[0]*(off+0.1)+tangent[0]*s*width/6,cxy[1]+outward[1]*(off+0.1)+tangent[1]*s*width/6,zc),tangent,outward,0.04,0.14,height-0.24)
    if shutter:
        for s in (-1,1):
            scx=cxy[0]+tangent[0]*s*(width/2+0.2)+outward[0]*(off+0.02)
            scy=cxy[1]+tangent[1]*s*(width/2+0.2)+outward[1]*(off+0.02)
            woodB.box((scx,scy,zc),tangent,outward,0.27,0.08,height*0.94)
            for f in (-0.28,0,0.28):
                trimB.box((scx,scy,zc+f*height),tangent,outward,0.28,0.11,0.055)

# Select the west-facing long wall as the NPS Photo 37-facing elevation. The NPS
# caption identifies KDR at Northwestern Ave, photographed facing southeast.
edges=[]
for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
    if length<1.0: continue
    t=(dx/length,dy/length); nrm=(t[1],-t[0]); c=((a[0]+b[0])/2,(a[1]+b[1])/2)
    edges.append((i,a,b,length,t,nrm,c))
front=max((e for e in edges if e[5][0]<-0.55),key=lambda e:e[3])
front_len=front[3]; front_center=front[6]; front_t=front[4]; front_n=front[5]
door_y=front_center[1]
# Photo 37 shows the main entry near the right end of the broad visible elevation.
door_frac=0.92
door_center=(front_center[0]+front_t[0]*(door_frac-0.5)*front_len,front_center[1]+front_t[1]*(door_frac-0.5)*front_len)
# Restrained window bays, with no shutters on the Photo 37-facing elevation.
front_window_fracs=(0.13,0.34,0.55,0.72)
for floor_z in (2.05,5.18):
    for frac in front_window_fracs:
        dist=(frac-0.5)*front_len
        cx=front_center[0]+front_t[0]*dist; cy=front_center[1]+front_t[1]*dist
        add_window((cx,cy,floor_z),front_t,front_n,1.34,1.82,False)
# Photo 37 directly supports dark half-timber framing across the visible upper
# elevation. Frame around, rather than through, the estimated sash openings.
timber_y=(front_center[0]+front_n[0]*0.20,front_center[1]+front_n[1]*0.20)
for z in (3.95,7.23):
    a=(timber_y[0]+front_t[0]*(-front_len/2+0.10),timber_y[1]+front_t[1]*(-front_len/2+0.10),z)
    b=(timber_y[0]+front_t[0]*(front_len/2-0.10),timber_y[1]+front_t[1]*(front_len/2-0.10),z)
    timberB.beam(a,b,0.22,0.20,front_n)
for frac in (0.04,0.25,0.46,0.67,0.80,0.97):
    px=front_center[0]+front_t[0]*(frac-0.5)*front_len+front_n[0]*0.20
    py=front_center[1]+front_t[1]*(frac-0.5)*front_len+front_n[1]*0.20
    timberB.beam((px,py,3.95),(px,py,7.23),0.20,0.20,front_n)
# Dark timber triangle on the visible north gable, a clear Photo 37 feature.
gable_n=(0.0,1.0)
for p0,p1,w in [((xl,yt+0.14,eave_z),(xr,yt+0.14,eave_z),0.22),
                ((mx,yt+0.14,eave_z),(mx,yt+0.14,ridge_z-0.12),0.20),
                ((xl,yt+0.14,eave_z),(mx,yt+0.14,ridge_z-0.12),0.20),
                ((xr,yt+0.14,eave_z),(mx,yt+0.14,ridge_z-0.12),0.20)]:
    timberB.beam(p0,p1,w,0.20,gable_n)
# Front door and modest surround; the photograph places it toward one end.
door_w=1.45; door_h=2.65; door_z=door_h/2+0.05
woodB.box((door_center[0]+front_n[0]*0.10,door_center[1]+front_n[1]*0.10,door_z),front_t,front_n,door_w,0.12,door_h)
for s in (-1,1): stoneB.box((door_center[0]+front_n[0]*0.17+front_t[0]*s*(door_w/2+0.11),door_center[1]+front_n[1]*0.17+front_t[1]*s*(door_w/2+0.11),door_h/2),front_t,front_n,0.16,0.20,door_h+0.2)
stoneB.box((door_center[0]+front_n[0]*0.17,door_center[1]+front_n[1]*0.17,door_h+0.08),front_t,front_n,door_w+0.40,0.20,0.18)
for zoff in (0.72,1.48,2.15):
    woodB.box((door_center[0]+front_n[0]*0.19,door_center[1]+front_n[1]*0.19,zoff),front_t,front_n,door_w*0.62,0.05,0.42)
# Low, shallow entry canopy; Photo 37 does not resolve the original entry joinery.
for side in (-1,1):
    cxy=(door_center[0]+front_n[0]*0.72+front_t[0]*side*0.95,door_center[1]+front_n[1]*0.72+front_t[1]*side*0.95)
    stoneB.box((cxy[0],cxy[1],1.52),front_t,front_n,0.16,0.18,2.80)
stoneB.box((door_center[0]+front_n[0]*0.72,door_center[1]+front_n[1]*0.72,2.98),front_t,front_n,2.25,0.20,0.16)
# Portico/canopy roof remains a shallow inferred feature.
base_z=3.78; peak_z=4.62; half=1.64; depth=0.74
for side in (-1,1):
    p1=(door_center[0]+front_t[0]*side*half,door_center[1]+front_t[1]*side*half)
    p2=(door_center[0]-front_n[0]*depth,door_center[1]-front_n[1]*depth)
    ridge=(door_center[0]-front_n[0]*depth,door_center[1]-front_n[1]*depth)
    roofB.thick_panel([(p1[0]+front_n[0]*0.8,p1[1]+front_n[1]*0.8,base_z),(p2[0]+front_t[0]*side*half,p2[1]+front_t[1]*side*half,base_z),(ridge[0],ridge[1],peak_z)])
# Steps extend into the front setback, kept shallow to avoid large site assumptions.
for i in range(3):
    offset=0.35+i*0.30
    stoneB.box((door_center[0]+front_n[0]*(offset+0.38),door_center[1]+front_n[1]*(offset+0.38),0.12+i*0.20),front_t,front_n,2.55,0.82,0.24)

# Long side and end elevations receive restrained sash windows; placement is regular and estimated.
for idx,a,b,length,t,nrm,c in edges:
    if idx==front[0] or length<5.8: continue
    if length>=17:
        fracs=(0.2,0.43,0.68,0.86)
    elif length>=9:
        fracs=(0.3,0.7)
    else:
        fracs=(0.5,)
    for floor_z in (2.05,5.18):
        for frac in fracs:
            cx=a[0]+(b[0]-a[0])*frac; cy=a[1]+(b[1]-a[1])*frac
            add_window((cx,cy,floor_z),t,nrm,1.18,1.72,False)

# Roof dormers, supported by the orthophoto roof pattern; facade shapes remain schematic.
for side in (-1,):
    xfront=xl+2.15 if side<0 else xr-2.15
    inward=1.0 if side<0 else -1.0
    nrm=(-1.0,0.0) if side<0 else (1.0,0.0)
    halfy=0.92
    for yc in (ymin+5.2,mid_y,ymax-5.2):
        roof_z=eave_z+(abs(xfront-mx)/(mx-xl))*(ridge_z-eave_z)
        base=roof_z+0.06; eaves=base+1.08; peak=base+1.75; backx=xfront+inward*1.65
        # Dormer front gable (brick rectangle and triangle) facing the exterior slope.
        facepts=[(xfront,yc-halfy,base),(xfront,yc+halfy,base),(xfront,yc+halfy,eaves),(xfront,yc,peak),(xfront,yc-halfy,eaves)]
        # Encode the 2D gable with a thin prism normal to the face.
        pts2=[(xfront,yc-halfy,base),(xfront,yc+halfy,base),(xfront,yc+halfy,eaves),(xfront,yc,peak),(xfront,yc-halfy,eaves)]
        prismpts=[]
        for dx in (0,nrm[0]*0.18): prismpts += [(x+dx,y,z) for x,y,z in pts2]
        # custom 5-sided prism using triangulated gable end and side edges
        b0=len(trimB.v); trimB.v.extend(prismpts)
        trimB.f += [(b0+0,b0+1,b0+2,b0+3,b0+4),(b0+9,b0+8,b0+7,b0+6,b0+5)]
        for k in range(5): trimB.f.append((b0+k,b0+(k+1)%5,b0+5+(k+1)%5,b0+5+k))
        # dormer twin roof planes taper back into the large roof plane
        backz=eave_z+(abs(backx-mx)/(mx-xl))*(ridge_z-eave_z)+0.10
        for s in (-1,1):
            yfront=yc+s*halfy; yback=yfront
            ridge_front=(xfront,yc,peak); ridge_back=(backx,yc,backz+0.42)
            roofB.thick_panel([(xfront,yfront,eaves),(backx,yback,backz),(ridge_back[0],ridge_back[1],ridge_back[2]),(ridge_front[0],ridge_front[1],ridge_front[2])])
        # small dark glazed dormer window and cream frame
        wt=(0,1); no=(nrm[0],0)
        # Put glazing in front of the gable end so it remains visible in render.
        gc=(xfront+nrm[0]*0.24,yc,base+0.70)
        glassB.box(gc,wt,no,1.02,0.06,0.82)
        for s in (-1,1): trimB.box((gc[0]+no[0]*0.05,gc[1]+s*0.56,gc[2]),wt,no,0.08,0.13,0.95)
        for s in (-1,1): trimB.box((gc[0]+no[0]*0.05,gc[1],gc[2]+s*0.46),wt,no,1.18,0.13,0.08)
        trimB.box((gc[0]+no[0]*0.08,gc[1],gc[2]),wt,no,0.045,0.15,0.82)
# Two modest brick chimneys punctuate the roof; size/positions are visual estimates from the aerial.
for j,(cx,cy) in enumerate(((mx,mid_y+1.0),)):
    z=ridge_z+0.62
    brickDetailB.box((cx,cy,z),(1,0),(0,1),0.70,0.78,1.24)
    stoneB.box((cx,cy,z+0.62),(1,0),(0,1),0.95,1.00,0.18)

# Interior: intentionally schematic common-room / hall / dining zones because no floor plan was found.
# The evidence explicitly says these partitions do not represent surveyed room layout.
floorB.thick_panel([(x,y,0.16) for x,y in ring],thickness=0.12)
interior_h=2.8
# longitudinal hall walls create a circulation spine from the main entrance.
interiorB.box((mid_x,mid_y-1.25,0.16+interior_h/2),(1,0),(0,1),xmax-xmin-2.0,0.12,interior_h)
interiorB.box((mid_x,mid_y+1.25,0.16+interior_h/2),(1,0),(0,1),xmax-xmin-2.0,0.12,interior_h)
# partial transverse dividers, leaving door openings at the hall spine.
for yy in (ymin+8.2,ymax-7.8):
    for side in (-1,1):
        xcen=mid_x+side*(xmax-xmin)/4
        interiorB.box((xcen,yy,0.16+interior_h/2),(0,1),(1,0),max(1.0,(xmax-xmin)/2-1.2),0.12,interior_h)
# Basic schematic furnishings, subdued so exterior remains the focus.
furniture,_,_=mat_principled('KDR_Interior_Furnishings_Schematic',(0.20,0.105,0.048),0.72)
furB=MeshBatch('KDRInterior_Schematic_Furnishings',furniture)
furB.box((mid_x,mid_y+6.0,0.72),(1,0),(0,1),2.4,1.1,0.18)
for dx in (-1.15,1.15):
    for dy in (-0.95,0.95): furB.box((mid_x+dx,mid_y+6.0+dy,0.52),(1,0),(0,1),0.42,0.42,0.55)
# lounge seating block in the south schematic room
furB.box((mid_x+1.0,mid_y-6.0,0.42),(1,0),(0,1),2.3,0.8,0.62)
furB.box((mid_x+1.0,mid_y-7.25,0.35),(1,0),(0,1),1.4,0.6,0.35)

# Create compact combined detail objects in the stable exported collection.
created=[]
for batch in (trimB,stoneB,glassB,woodB,roofB,gableB,timberB,interiorB,floorB,brickDetailB,furB):
    o=batch.create();
    if o: created.append(o)

# Add a readable label as a mesh text plaque? Avoid unverified chapter signage; no text added.
# Production asset should show materials in material preview and render.
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.filepath=str(EXPORT/'kappa_delta_rho_exterior.png')
scene.render.image_settings.color_mode='RGBA'
scene.render.resolution_percentage=100
scene.render.engine='BLENDER_EEVEE'
scene.render.use_file_extension=True
scene.world.color=(0.16,0.19,0.24)
scene.render.image_settings.color_depth='8'
# Eevee settings if available.
try: scene.eevee.taa_render_samples=48
except Exception: pass
# Temporary preview rig: create, render, then remove before saving the library asset.
rig=[]
def aim(o,point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('KDRPreview_CameraData'); cam=bpy.data.objects.new('KDRPreview_Camera',cam_data); scene.collection.objects.link(cam); rig.append(cam)
cam.location=(xmin-31,mid_y+21,15.0); cam_data.type='ORTHO'; cam_data.ortho_scale=43.0; aim(cam,(mid_x,mid_y,4.2)); scene.camera=cam
world=scene.world or bpy.data.worlds.new('KDRPreview_World'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.16,0.20,0.27,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.32
for name,loc,power,size in [('KDRPreview_Key',(xmin-18,mid_y+28,29),1900,20),('KDRPreview_Fill',(xmax+14,mid_y+2,20),850,16)]:
    ld=bpy.data.lights.new(name+'_Data','AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new(name,ld); scene.collection.objects.link(lo); lo.location=loc; aim(lo,(mid_x,mid_y,3.8)); rig.append(lo)
# Preview-only ground plane and material
matgrass,_,_=mat_principled('KDRPreview_Grass',(0.105,0.17,0.085),0.95)
plane_mesh=bpy.data.meshes.new('KDRPreview_Ground_Mesh'); plane_mesh.from_pydata([(xmin-25,ymin-25,-0.08),(xmax+25,ymin-25,-0.08),(xmax+25,ymax+25,-0.08),(xmin-25,ymax+25,-0.08)],[],[(0,1,2,3)]); plane_mesh.materials.append(matgrass)
plane=bpy.data.objects.new('KDRPreview_Ground',plane_mesh); scene.collection.objects.link(plane); rig.append(plane)
# Exterior preview
scene.render.filepath=str(EXPORT/'kappa_delta_rho_exterior.png'); bpy.ops.render.render(write_still=True)
# Interior-plan preview: hide exterior shell/roof/porch temporarily; keep schematic floor/partitions/furnishings visible.
old_vis={o.name:o.hide_render for o in bpy.data.objects}
for o in (obj,): o.hide_render=True
for o in created:
    if o.name.startswith('KDRDetail_Roof') or o.name.startswith('KDRDetail_Chimneys') or o.name.startswith('KDRDetail_Architectural_Trim') or o.name.startswith('KDRDetail_Limestone') or o.name.startswith('KDRDetail_Window_Glazing') or o.name.startswith('KDRDetail_Woodwork') or o.name.startswith('KDRDetail_Tudor_Gables') or o.name.startswith('KDRDetail_Tudor_HalfTimber'):
        o.hide_render=True
cam.location=(mid_x-22,mid_y+25,22); cam_data.type='ORTHO'; cam_data.ortho_scale=38; aim(cam,(mid_x,mid_y,1.1))
# Put an explicit, camera-facing note on the interior preview. The note and
# contrast panel are temporary render overlays and are removed before save.
label_mat=bpy.data.materials.new('KDRPreview_Annotation_White'); label_mat.use_nodes=True
label_nt=label_mat.node_tree; label_nt.nodes.clear()
label_out=label_nt.nodes.new('ShaderNodeOutputMaterial'); label_em=label_nt.nodes.new('ShaderNodeEmission')
label_em.inputs['Color'].default_value=(1.0,0.94,0.70,1.0); label_em.inputs['Strength'].default_value=1.0
label_nt.links.new(label_em.outputs['Emission'],label_out.inputs['Surface'])
panel_mat=bpy.data.materials.new('KDRPreview_Annotation_Background'); panel_mat.diffuse_color=(0.018,0.025,0.035,1.0); panel_mat.use_nodes=True
panel_bsdf=next(n for n in panel_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
panel_bsdf.inputs['Base Color'].default_value=(0.018,0.025,0.035,1.0); panel_bsdf.inputs['Roughness'].default_value=1.0
panel_mesh=bpy.data.meshes.new('KDRPreview_Annotation_Panel_Mesh')
panel_mesh.from_pydata([(-17.8,-13.7,0),(-4.0,-13.7,0),(-4.0,-11.7,0),(-17.8,-11.7,0)],[],[(0,1,2,3)])
panel_mesh.materials.append(panel_mat)
panel=bpy.data.objects.new('KDRPreview_Annotation_Panel',panel_mesh); scene.collection.objects.link(panel); panel.parent=cam; panel.location=(0,0,-8.1); rig.append(panel)
label_curve=bpy.data.curves.new('KDRPreview_Annotation_Text_Curve','FONT')
label_curve.body='SCHEMATIC INTERIOR  |  NOT SURVEYED'
label_curve.size=0.72; label_curve.extrude=0.0; label_curve.bevel_depth=0.0
label=bpy.data.objects.new('KDRPreview_Annotation_Text',label_curve); scene.collection.objects.link(label)
label.parent=cam; label.location=(-17.2,-13.15,-8.0); label.rotation_euler=(0,0,0); label_curve.materials.append(label_mat); rig.append(label)
scene.render.filepath=str(EXPORT/'kappa_delta_rho_schematic_interior.png'); bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.name in old_vis: o.hide_render=old_vis[o.name]
# Remove the temporary preview rig and preview-only grass material; preserve building-specific materials and geometry.
for o in rig:
    bpy.data.objects.remove(o,do_unlink=True)
for material_name in ('KDRPreview_Grass','KDRPreview_Annotation_White','KDRPreview_Annotation_Background'):
    if bpy.data.materials.get(material_name): bpy.data.materials.remove(bpy.data.materials[material_name])
scene.camera=None
# Save only the assigned building library; no master or shared files touched.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

# Reopen this exact saved file in a separate Blender process for final verification.
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
report={'building':'Kappa Delta Rho','asset':str(ASSET),'sha256':sha,'gis_fid':801,'gis_name':geo['properties'].get('BUILDING_N'),'gis_address':geo['properties'].get('ADDRESS'),'gis_vertices':len(ring),'area_m2':abs(area),'model_bounds_xy_m':[xmin,xmax,ymin,ymax],'wall_height_m':wall_h,'roof_peak_m':ridge_z,'geometry_edit':'Preserved exact 20-vertex Purdue GIS FID 801 wall outline. Used directly identified NPS Photo 37 (caption: Kappa Delta Rho, Northwestern Ave, N, facing southeast; Jane Evans, June 2001) to refine the visible Tudor Revival facade: upper-story dark half-timbering, pale wall infill, an offset entry, steep gabled roof, three visible-slope dormers, and one visible chimney. Converted roof panels and schematic floor to closed thin slabs; retained the preview-only interior caveat.','architectural_uncertainties':['Photo 37 is monochrome; exact facade color, material hues, dimensions, and concealed elevations remain uncertain. Wall finish is labeled an estimate; NPS district-wide form materials are not treated as building-specific proof.','Photo 37 supports a 2001 view toward the visible elevation and roof profile, but not surveyed wall or ridge heights; 7.5 m wall and 11.4 m ridge remain estimates.','Interior partitions and furnishings are generic schematic common-room, hall and dining zones, not an as-built plan. Far roof slope and opposite gable end are not shown clearly in Photo 37.'],'materials':{'exterior':'procedural pale wall infill; color and exact masonry finish are estimates','roof':'procedural dark slate-like roof with subtle variation; Photo 37 supports steep dark roof appearance, exact material unverified','timber':'dark Tudor half-timbering supported on visible upper facade and north gable in NPS Photo 37','trim':'procedural limestone and painted wood; estimate','windows':'dark reflective glazing with estimated sash divisions; opening groupings follow Photo 37 broadly','interior':'schematic wood floor, plaster partitions and furnishings'},'objects_added':[o.name for o in created],'previews':[str(EXPORT/'kappa_delta_rho_exterior.png'),str(EXPORT/'kappa_delta_rho_schematic_interior.png')],'nps_photo37':{'asset_id':'d392afd2-253a-41d8-a3f6-d8faaf7d0c14','source_url':'https://npgallery.nps.gov/GetAsset/d392afd2-253a-41d8-a3f6-d8faaf7d0c14/','pdf_page_image':71,'caption_page':72,'caption_date':'June 2001','caption_author':'Jane Evans','facing_direction':'southeast','exposure_date_status':'caption states June 2001; exact exposure date not independently confirmed'},'fresh_open_status':'pending separate validation'}
(AUDIT/'build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))

