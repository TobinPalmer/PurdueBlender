import bpy, json, math, os
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_harrison_street_parking_garage_823c7d2.blend'
EVID=ROOT/'audit/massing_harrison_street_parking_garage_823c7d2'
SRC=EVID/'sources/purdue_gis_FID892.json'
REND=EVID/'renders'
REND.mkdir(parents=True,exist_ok=True)
A=json.loads(SRC.read_text(encoding='utf-8-sig'))['feature']
ring=A['geometry']['rings'][0]
xy=[]
for lon,lat in ring:
    x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
    y=(lat-40.4274)*111040.0
    p=(x,y)
    if not xy or math.dist(xy[-1],p)>0.001: xy.append(p)
if math.dist(xy[0],xy[-1])<0.001: xy.pop()
# GIS ring winding may vary; retain original boundary and use Blender tessellation.
footprint_ccw=sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))/2>0

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
# Remove unreferenced startup/render materials so rebuilt libraries do not retain
# stale default or TEMP preview materials from previous builder runs.
for m in list(bpy.data.materials):
    if m.users == 0: bpy.data.materials.remove(m)
scene=bpy.context.scene
scene.name='Building_massing_harrison_street_parking_garage_823c7d2'
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1.0
coll=bpy.data.collections.new('Asset_massing_harrison_street_parking_garage_823c7d2')
scene.collection.children.link(coll)
# Remove default collection if now empty.
for c in list(bpy.data.collections):
    if c.name=='Collection' and not c.objects: bpy.data.collections.remove(c)

# Materials: cast-in-place concrete, precast fascia, brick veneer, dark openings, glazing.
def mat(name,color,rough=.8,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
concrete=mat('Cast-in-place concrete | warm gray',(0.53,.51,.46),.9)
precast=mat('Architectural precast | light limestone',(0.72,.69,.61),.82)
brick=mat('Brick veneer | Purdue red-brown',(.36,.15,.10),.9)
shadow=mat('Parking bay shadow',(.075,.085,.085),.96)
glass=mat('Stair core glazing',(.14,.28,.32),.3,.12)
metal=mat('Perforated metal screen',(.28,.32,.32),.52,.5)
plantermat=mat('Planter concrete',(.48,.48,.43),.9)
# assign to collection robustly
def move_obj(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    coll.objects.link(obj)

def mesh_obj(name,verts,faces,material):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); return ob

def prism(name,poly,z0,z1,material):
    n=len(poly); verts=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    faces=[]
    # cap tessellation, maintain polygon boundary shape
    tess=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])
    for tri in tess:
        ids=list(tri)
        if len(set(ids))==3:
            faces.append(tuple(ids)); faces.append(tuple(i+n for i in reversed(ids)))
    for i in range(n): j=(i+1)%n; faces.append((i,j,j+n,i+n))
    return mesh_obj(name,verts,faces,material)

def box_between(name,p0,p1,width,z0,z1,material):
    dx=p1[0]-p0[0]; dy=p1[1]-p0[1]; L=math.hypot(dx,dy)
    if L<.01: return None
    nx=-dy/L*width/2; ny=dx/L*width/2
    verts=[(p0[0]+nx,p0[1]+ny,z0),(p1[0]+nx,p1[1]+ny,z0),(p1[0]-nx,p1[1]-ny,z0),(p0[0]-nx,p0[1]-ny,z0),
           (p0[0]+nx,p0[1]+ny,z1),(p1[0]+nx,p1[1]+ny,z1),(p1[0]-nx,p1[1]-ny,z1),(p0[0]-nx,p0[1]-ny,z1)]
    return mesh_obj(name,verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],material)

def square_post(name,p,width,z0,z1,material):
    x,y=p; h=width/2
    return prism(name,[(x-h,y-h),(x+h,y-h),(x+h,y+h),(x-h,y+h)],z0,z1,material)

# Continuous six-level parking shell: one level below grade plus five above.
floor_z=[-3.2,0.0,3.2,6.4,9.6,12.8]
for i,z in enumerate(floor_z):
    prism('Parking deck %02d | structural slab'%(i+1),xy,z-.24,z,concrete)
# Roof slab and low perimeter parapet, keeping total above-grade envelope about 16 m.
prism('Roof deck | cast-in-place',xy,15.65,15.95,concrete)
# Repeated open garage facade: deep cast-in-place piers and precast horizontal spandrels.
# Build posts at regular arc-length intervals along the exact GIS perimeter.
edge_lengths=[math.dist(xy[i],xy[(i+1)%len(xy)]) for i in range(len(xy))]
perim=sum(edge_lengths); spacing=6.0; d=0.0; targets=[]
while d<perim:
    targets.append(d); d+=spacing
for k,dist0 in enumerate(targets):
    dist=dist0
    for i,L in enumerate(edge_lengths):
        if dist<=L:
            t=dist/L if L else 0; a=xy[i]; b=xy[(i+1)%len(xy)]; p=(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])); break
        dist-=L
    # slender vertical concrete column from grade through roof overhang
    square_post('Facade concrete pier %02d'%k,p,.58,0,15.75,concrete)
# Continuous horizontal fascia bands are described as thin perimeter strips; segments follow GIS outline.
for level,z in enumerate([2.75,5.95,9.15,12.35,15.35]):
    for i,a in enumerate(xy):
        b=xy[(i+1)%len(xy)]
        # low solid spandrel band leaves the garage parking bays substantially open
        box_between('Precast spandrel L%d S%02d'%(level+1,i),a,b,.24,z-.28,z,precast)
# Perimeter parapet / rooftop screen represented by repeated low precast edge wall.
for i,a in enumerate(xy): box_between('Roof parapet segment %02d'%i,a,xy[(i+1)%len(xy)],.20,15.95,16.45,precast)
# Brick-veneered lower stair/service volume as a compact end block placed inside the polygon.
# The GIS centroid plus a verified inside point near the north end avoids assuming an unsupported exact core location.
cx=sum(p[0] for p in xy)/len(xy); cy=sum(p[1] for p in xy)/len(xy)
# Place the service core toward one end of the long campus footprint using its principal axis.
# Principal axis from covariance; center offset 24% of long-axis span.
xx=sum((x-cx)**2 for x,y in xy)/len(xy); yy=sum((y-cy)**2 for x,y in xy)/len(xy); xy_cov=sum((x-cx)*(y-cy) for x,y in xy)/len(xy)
ang=.5*math.atan2(2*xy_cov,xx-yy); ux,uy=math.cos(ang),math.sin(ang)
vx,vy=-uy,ux
proj=[(x-cx)*ux+(y-cy)*uy for x,y in xy]; half=(max(proj)-min(proj))/2
proj_v=[(x-cx)*vx+(y-cy)*vy for x,y in xy]
umin,umax=min(proj),max(proj); vmin,vmax=min(proj_v),max(proj_v)
# Aerial places the compact service enclosure toward the northwest roof edge;
# its exact offset and dimensions are estimated, not surveyed.
core_u=umin+(umax-umin)*.82; core_v=vmin+8.5
core_c=(cx+ux*core_u+vx*core_v,cy+uy*core_u+vy*core_v)
# Approximate 6x9 m service/stair volume, axis aligned to the long direction.
w,l=6,9
core=[(core_c[0]+sx*w/2*vx+sy*l/2*ux,core_c[1]+sx*w/2*vy+sy*l/2*uy) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
prism('Brick-veneered stair and service core',core,-3.0,16.5,brick)
# A glazed vertical stair/elevator slot on the core facade.
# Rectangular slim vertical slot embedded visually as dark-blue inset volume.
gc=(core_c[0]+ux*2.2,core_c[1]+uy*2.2); gw=2.1; gl=1.0
winpoly=[(gc[0]+sx*gw/2*vx+sy*gl/2*ux,gc[1]+sx*gw/2*vy+sy*gl/2*uy) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
prism('Glazed stair slot',winpoly,0,15.8,glass)

# Roof evidence from the archived Indiana current ortho shows active parking
# stalls around a raised central rectangular structure/open bay. Exact stall
# dimensions and the roof structure's height are not published; dimensions below
# are proportional estimates from the image, not surveyed/as-built measures.
def roof_point(u,v,z=15.98):
    return (cx+ux*u+vx*v, cy+uy*u+vy*v, z)

roof_mark=mat('Estimated rooftop parking markings | light concrete paint',(.84,.83,.77),.86)
mark_verts=[]; mark_faces=[]
def inside_footprint(px,py):
    inside=False
    n=len(xy)
    for i in range(n):
        ax,ay=xy[i]; bx,by=xy[(i+1)%n]
        cross=(px-ax)*(by-ay)-(py-ay)*(bx-ax)
        dot=(px-ax)*(px-bx)+(py-ay)*(py-by)
        if abs(cross)<1e-7 and dot<=1e-7: return True
        if ((ay>py)!=(by>py)) and px<(bx-ax)*(py-ay)/(by-ay)+ax: inside=not inside
    return inside

def roof_line(u0,v0,u1,v1,width=.12,z=15.98):
    du,dv=u1-u0,v1-v0; length=math.hypot(du,dv)
    if length<.01: return
    nu,nv=-dv/length*width/2,du/length*width/2
    pieces=max(1,math.ceil(length/.85))
    for i in range(pieces):
        ta,tb=i/pieces,(i+1)/pieces
        a=(u0+du*ta,v0+dv*ta); b=(u0+du*tb,v0+dv*tb)
        corners=[roof_point(a[0]+nu,a[1]+nv,z),roof_point(b[0]+nu,b[1]+nv,z),roof_point(b[0]-nu,b[1]-nv,z),roof_point(a[0]-nu,a[1]-nv,z)]
        if not all(inside_footprint(p[0],p[1]) for p in corners): continue
        k=len(mark_verts); mark_verts.extend(corners); mark_faces.append((k,k+1,k+2,k+3))

uvals=[(x-cx)*ux+(y-cy)*uy for x,y in xy]
vvals=[(x-cx)*vx+(y-cy)*vy for x,y in xy]
umin,umax=min(uvals),max(uvals); vmin,vmax=min(vvals),max(vvals)
uc=(umin+umax)/2; vc=(vmin+vmax)/2
u0,u1=umin+8.0,umax-8.0
# Four approximate stall rows: outer edges and two interior rows flanking a wide drive aisle.
parking_rows=[(vmin+3.0,vmin+8.1),(vc-11.0,vc-6.0),(vc+6.0,vc+11.0),(vmax-8.1,vmax-3.0)]
canopy_u=umin+(umax-umin)*.72
for row_i,(va,vb) in enumerate(parking_rows):
    roof_line(u0,va,u1,va); roof_line(u0,vb,u1,vb)
    u=u0
    while u<=u1+1e-6:
        # Keep the marks clear of the estimated central canopy/open bay.
        if not (abs(u-canopy_u)<7.0 and row_i in (1,2)):
            roof_line(u,va,u,vb,.11)
        u+=2.6
# End parking rows are visible in the aerial at both short ends of the roof.
for uedge in (u0,u1): roof_line(uedge,vmin+4.0,uedge,vmax-4.0)
for v in [vmin+4.0+i*2.6 for i in range(int((vmax-vmin-8.0)/2.6)+1)]:
    if abs(v-vc)<12.0: continue
    roof_line(u0,v,u0+5.0,v,.11); roof_line(u1-5.0,v,u1,v,.11)
# Direction arrows in the long drive aisles, modeled as flat markings.
arrow_verts=[]; arrow_faces=[]
for au,av,direction in [(uc-(umax-umin)*.30,vc,1),(uc+(umax-umin)*.30,vc,-1),(uc-(umax-umin)*.30,vc-15,1),(uc+(umax-umin)*.30,vc+15,-1)]:
    tri=[(au+direction*1.25,av),(au-direction*.9,av-0.8),(au-direction*.9,av+0.8)]
    k=len(arrow_verts); arrow_verts.extend(roof_point(u,v,15.985) for u,v in tri); arrow_faces.append((k,k+1,k+2))
if mark_faces: mesh_obj('Roof parking stalls | estimated from aerial',mark_verts,mark_faces,roof_mark)
if arrow_faces: mesh_obj('Roof circulation arrows | estimated',arrow_verts,arrow_faces,roof_mark)

# Open-sided raised canopy/roof-access structure. The aerial supports the form
# and central placement, but its dimensions, height, and function are unverified.
canopy_center=roof_point(canopy_u,vc,15.95)
canopy_width=19.0; canopy_length=9.0
canopy_poly=[(canopy_center[0]+sx*canopy_width/2*vx+sy*canopy_length/2*ux,
              canopy_center[1]+sx*canopy_width/2*vy+sy*canopy_length/2*uy)
             for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
for i,(uoff,voff) in enumerate([(-canopy_length/2,-canopy_width/2),(canopy_length/2,-canopy_width/2),(canopy_length/2,canopy_width/2),(-canopy_length/2,canopy_width/2)]):
    p=roof_point(canopy_u+uoff,vc+voff,0)
    square_post('Estimated central roof pavilion pier %02d'%i,(p[0],p[1]),.55,15.95,16.55,precast)
prism('Estimated central open roof pavilion canopy',canopy_poly,16.55,17.10,precast)

# Rooftop wind screen / mechanical screen implied by open-air deck structure; restrained, low.
for i,a in enumerate(xy):
    b=xy[(i+1)%len(xy)]
    box_between('Metal rooftop screen %02d'%i,a,b,.08,16.45,17.1,metal)
# Planter boxes at selected street-facing perimeter segments, reflecting contractor description of perimeter planters.
# Narrow troughs remain separate from site footprint so base GIS outline remains inspectable.
for i in range(0,len(xy),7):
    a=xy[i]; b=xy[(i+1)%len(xy)]; L=math.dist(a,b)
    if L<2: continue
    # planter modeled as shallow curb at grade, entirely inside garage edge
    mx=(a[0]+b[0])/2; my=(a[1]+b[1])/2
    nx,ny=(-(b[1]-a[1])/L,(b[0]-a[0])/L) if footprint_ccw else ((b[1]-a[1])/L,-(b[0]-a[0])/L)
    pc=[(mx+nx*.9-ux*1.8,my+ny*.9-uy*1.8),(mx+nx*.9+ux*1.8,my+ny*.9+uy*1.8),(mx+nx*2.0+ux*1.8,my+ny*2.0+uy*1.8),(mx+nx*2.0-ux*1.8,my+ny*2.0-uy*1.8)]
    # simple geometric trough; vegetation omitted as unverified detail
    prism('Perimeter planter curb %02d'%i,pc,0,.55,plantermat)

# Annotative metadata.
coll['asset_id']='massing_harrison_street_parking_garage_823c7d2'
coll['source_primary']='Purdue GIS Building Primary, FID 892 / BLDG_ABBR PGH; WGS84 polygon transformed by documented local campus approximation.'
coll['geometry_basis']='Footprint matches provider GIS polygon; six levels total including one below grade per WGI. Floor spacing and roof/parapet height are interpretive.'
coll['height_status']='Massing estimate. Purdue GIS vertical attributes have undocumented units and were not used as measured elevation.'
coll['roof_status']='Roof parking stripes, arrows and central open-sided canopy are approximate forms interpreted from archived Indiana orthophoto; exact dimensions, function and roof-level date are unverified.'
scene['source_record']='audit/massing_harrison_street_parking_garage_823c7d2/source_record.json'
scene['build_script']='modular/buildings/build_massing_harrison_street_parking_garage_823c7d2.py'
scene['units']='meters; direct campus world coordinates'

# Render review views with temporary ground, lights and cameras; remove all non-asset objects before save.
# neutral preview ground
bpy.ops.mesh.primitive_plane_add(size=500,location=(cx,cy,-.34)); ground=bpy.context.object; ground.name='TEMP_ground'; ground.data.materials.append(mat('TEMP ground',(.24,.27,.25),.95));
# move ground out of asset collection
preview=bpy.data.collections.new('TEMP_preview'); scene.collection.children.link(preview); move_obj(ground); preview.objects.link(ground)
# setup render
def aim(obj,pt): obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
engine_ids={e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
scene.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engine_ids else 'BLENDER_EEVEE'
scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.color=(.12,.12,.12)
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.32,.35,.38,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.7
scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=1.25; scene.view_settings.gamma=1.0
# area lights
for name,loc,power,size in [('Key',(cx-90,cy-75,110),18000,65),('Fill',(cx+80,cy-15,70),10000,55),('Rim',(cx+5,cy+90,90),14000,50)]:
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new(name,ld); preview.objects.link(lo); lo.location=loc; aim(lo,(cx,cy,5))

def camera_render(filename,loc,ortho):
    cd=bpy.data.cameras.new('TEMP_camera'); cam=bpy.data.objects.new('TEMP_camera',cd); preview.objects.link(cam); cam.location=loc; cam.data.type='ORTHO'; cam.data.ortho_scale=ortho; aim(cam,(cx,cy,5)); scene.camera=cam
    scene.render.filepath=str(REND/filename); bpy.ops.render.render(write_still=True); bpy.data.objects.remove(cam,do_unlink=True)
# calculate field sizes from extents
minx=min(x for x,y in xy); maxx=max(x for x,y in xy); miny=min(y for x,y in xy); maxy=max(y for x,y in xy)
span=max(maxx-minx,maxy-miny)
camera_render('harrison_oblique_review.png',(cx-105,cy-115,88),span*2.0)
camera_render('harrison_elevation_review.png',(cx-110,cy-5,26),span*1.85)
camera_render('harrison_roof_review.png',(cx-15,cy-10,165),span*1.8)
# remove temporary scene objects and collection (no external scene props in saved asset)
scene.camera=None
for ob in list(preview.objects): bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(preview)
# Drop unused startup and preview-only materials. The exported geometry uses
# named building materials and does not depend on these render helpers.
for stale_name in ('Material','TEMP ground'):
    stale=bpy.data.materials.get(stale_name)
    if stale: bpy.data.materials.remove(stale,do_unlink=True)
# Use the version-neutral viewport renderer in the saved library. The review PNGs
# above were rendered with the local version's Eevee; Blender 4.x and 5.x use
# different Eevee engine identifiers.
scene.render.engine='BLENDER_WORKBENCH'
# ensure all asset mesh objects are in the stable collection
bpy.ops.object.select_all(action='DESELECT')
# save portable blend
ASSET.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(json.dumps({'asset':str(ASSET),'objects':len(coll.objects),'gis_vertices':len(xy),'bounds':[minx,miny,-3.24,maxx,maxy,17.1],'floors_m':floor_z,'render_dir':str(REND)},indent=2))

