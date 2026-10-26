import bpy, json, math, os, sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_purdue_drug_discovery_facility_fc72a4a'
ASSET_PATH = ROOT / 'modular/buildings/massing_purdue_drug_discovery_facility_fc72a4a.blend'
GEOJSON = ROOT / 'audit/purdue_drug_discovery_facility/sources/arcgis_feature_893_2026-10-26.geojson'
OUT_DIR = ROOT / 'audit/purdue_drug_discovery_facility'
COLLECTION_NAME = 'Asset_' + ASSET_ID
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
METERS_PER_DEG_LAT, METERS_PER_DEG_LON_AT_ORIGIN = 111040.0, 111412.84 * math.cos(math.radians(ORIGIN_LAT))

# Extract source polygon in documented local campus coordinates.
feature = json.loads(GEOJSON.read_text(encoding='utf-8'))['features'][0]
assert feature['properties']['FID'] == 893 and feature['properties']['BLDG_ABBR'] == 'DRUG'
rings_ll = feature['geometry']['coordinates']
def project(lon, lat):
    return ((lon - ORIGIN_LON) * METERS_PER_DEG_LON_AT_ORIGIN, (lat - ORIGIN_LAT) * METERS_PER_DEG_LAT)
rings = [[project(lon, lat) for lon,lat,*_ in ring[:-1]] for ring in rings_ll]
outer, holes = rings[0], rings[1:]
all_pts = [p for r in rings for p in r]
min_x,max_x=min(p[0] for p in all_pts),max(p[0] for p in all_pts)
min_y,max_y=min(p[1] for p in all_pts),max(p[1] for p in all_pts)
center_x,center_y=(min_x+max_x)/2,(min_y+max_y)/2

# Simplify noisy CAD-derived boundary samples by no more than 0.24 m for facade construction.
def rdp(points,eps):
    if len(points)<=2:return points
    ax,ay=points[0]; bx,by=points[-1]; dx=bx-ax;dy=by-ay; den=dx*dx+dy*dy
    md=-1; idx=0
    for i,(x,y) in enumerate(points[1:-1],1):
        t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/den)) if den else 0
        d=math.hypot(x-(ax+t*dx),y-(ay+t*dy))
        if d>md:md=d;idx=i
    if md>eps:return rdp(points[:idx+1],eps)[:-1]+rdp(points[idx:],eps)
    return [points[0],points[-1]]
def simplify_closed(points,eps=.24):
    q=points[:-1]; far=max(range(1,len(q)),key=lambda i:math.dist(q[i],q[0]))
    return rdp(q[:far+1],eps)[:-1]+rdp(q[far:]+[q[0]],eps)[:-1]
rings_model=[simplify_closed(r,.24) for r in rings]
# The longest straight west-side structural wall segments locate the public entry facade.
west_runs=[]
for i,a in enumerate(rings[0]):
    b=rings[0][(i+1)%len(rings[0])]; dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
    if length>1.2 and abs(dx)<.10 and (a[0]+b[0])/2<min_x+1.2:
        west_runs.append(((a[1]+b[1])/2,length))
entry_y=(sum(y*l for y,l in west_runs)/sum(l for _,l in west_runs)) if west_runs else center_y

# Material helpers.
def material(name, color, roughness=.7, metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metallic
    return m

def brick_material():
    m=material('Drug Discovery • Purdue red-brown brick',(.40,.115,.073),.78)
    n=m.node_tree.nodes; l=m.node_tree.links
    bsdf=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    tex=n.new('ShaderNodeTexCoord'); brick=n.new('ShaderNodeTexBrick'); brick.inputs['Scale'].default_value=1.0
    brick.inputs['Color1'].default_value=(.37,.095,.058,1); brick.inputs['Color2'].default_value=(.53,.17,.105,1)
    brick.inputs['Mortar'].default_value=(.24,.19,.16,1); brick.inputs['Mortar Size'].default_value=.018
    brick.inputs['Brick Width'].default_value=.55; brick.inputs['Row Height'].default_value=.20
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=4.0; noise.inputs['Detail'].default_value=2
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.035
    l.new(tex.outputs['UV'],brick.inputs['Vector']); l.new(brick.outputs['Color'],bsdf.inputs['Base Color'])
    l.new(tex.outputs['UV'],noise.inputs['Vector']); l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    return m

mat_brick=brick_material()
mat_brick_dark=material('Drug Discovery • dark brick base',(.26,.071,.052),.82)
mat_concrete=material('Drug Discovery • warm limestone precast',(.68,.64,.56),.7)
mat_metal=material('Drug Discovery • bronze anodized aluminum',(.16,.105,.063),.34,.72)
mat_mullion=material('Drug Discovery • champagne structural metal',(.54,.42,.25),.32,.7)
mat_glass=material('Drug Discovery • cool reflective laboratory glass',(.20,.39,.49),.18,.28)
p=next(n for n in mat_glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Transmission Weight'].default_value=.12; p.inputs['IOR'].default_value=1.45
mat_spandrel=material('Drug Discovery • warm gray window spandrel',(.48,.45,.40),.5,.1)
mat_roof=material('Drug Discovery • flat roof membrane',(.36,.37,.35),.88)
mat_interior=material('Drug Discovery • warm lobby stone',(.73,.67,.55),.72)
mat_lobby_glass=material('Drug Discovery • vestibule glazing',(.15,.32,.39),.15,.16)

# Reset the old massing while preserving the file's scene and named library collection.
col=bpy.data.collections.get(COLLECTION_NAME)
if col is None:
    col=bpy.data.collections.new(COLLECTION_NAME); bpy.context.scene.collection.children.link(col)
for obj in list(col.objects):
    bpy.data.objects.remove(obj,do_unlink=True)

# Mesh aggregation by material keeps the exported collection compact and easy to link.
class MeshBucket:
    def __init__(self,name,mats): self.name=name; self.mats=mats; self.v=[]; self.f=[]; self.mi=[]; self.uv=[]
    def quad(self,pts,mat_index):
        k=len(self.v); self.v.extend(tuple(p) for p in pts); self.f.append((k,k+1,k+2,k+3)); self.mi.append(mat_index)
        L=math.dist(pts[0],pts[1]); H=math.dist(pts[0],pts[3]); self.uv.append(((0,0),(L,0),(L,H),(0,H)))
    def tri(self,pts,mat_index):
        k=len(self.v); self.v.extend(tuple(p) for p in pts); self.f.append((k,k+1,k+2)); self.mi.append(mat_index)
        L=math.dist(pts[0],pts[1]); H=math.dist(pts[0],pts[2]); self.uv.append(((0,0),(L,0),(0,H)))
    def obj(self):
        if not self.f:return None
        me=bpy.data.meshes.new(self.name+'Mesh'); me.from_pydata(self.v,[],self.f); me.materials.clear()
        for m in self.mats:me.materials.append(m)
        me.update(); ob=bpy.data.objects.new(self.name,me); col.objects.link(ob)
        for poly,idx in zip(me.polygons,self.mi):poly.material_index=idx
        uv=me.uv_layers.new(name='UVMap')
        for poly,coords in zip(me.polygons,self.uv):
            for loop_index,coord in zip(poly.loop_indices,coords): uv.data[loop_index].uv=coord
        return ob

# Surfaces: exact GIS footprint, including its documented inner courtyard ring.
def polygon_tris(z):
    input_rings=[[Vector((x,y,0)) for x,y in r] for r in rings]
    tris=tessellate_polygon(input_rings)
    flat=[p for r in input_rings for p in r]
    return [[(flat[i].x,flat[i].y,z) for i in tri] for tri in tris]

# Main shell. Purdue source describes the building as three stories; facilities GIS has roof marker R=56 ft.
ROOF_Z=56.0*0.3048       # GIS roof marker: 17.0688 m above local grade
PARAPET_Z=14.65          # roofline parapet at the third occupied floor
MAIN_WALL_TOP=14.28
FLOORS=[0.0,4.88,9.75,14.63]
wall=MeshBucket('DRUG | GIS footprint walls, three-storey brick and glazing',[mat_brick,mat_brick_dark,mat_glass,mat_concrete])
for ridx,ring in enumerate(rings_model):
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]
        # On south-facing outer wall only, set the central bay to glazing, matching Purdue's facade photo.
        midx=(a[0]+b[0])/2; midy=(a[1]+b[1])/2; dx=b[0]-a[0];dy=b[1]-a[1]
        is_front_atrium=(ridx==0 and a[0]<min_x+.8 and b[0]<min_x+.8 and abs(dx)<.22 and entry_y-8.5<midy<entry_y+8.5 and abs(dy)>1.0)
        mi=2 if is_front_atrium else 0
        wall.quad([(a[0],a[1],.25),(b[0],b[1],.25),(b[0],b[1],MAIN_WALL_TOP),(a[0],a[1],MAIN_WALL_TOP)],mi)
        # Discrete continuous lintel / floor bands maintain the photo's strong horizontal brick rhythm.
        for z in (4.70,9.57,14.12):
            wall.quad([(a[0],a[1],z),(b[0],b[1],z),(b[0],b[1],z+.16),(a[0],a[1],z+.16)],3 if z==14.12 else 0)
wall.obj()

# Brick plinth wraps all outer and courtyard edges.
plinth=MeshBucket('DRUG | dark brick plinth',[mat_brick_dark])
for ring in rings_model:
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]
        plinth.quad([(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],.58),(a[0],a[1],.58)],0)
plinth.obj()

# Internal floor plates; hole remains open. 3 floors with a documented central lab/core arrangement.
slabs=MeshBucket('DRUG | story slabs and roof plane',[mat_concrete,mat_roof])
for z in (4.77,9.64,14.48):
    for tri in polygon_tris(z):slabs.tri(tri,0)
for tri in polygon_tris(14.64):slabs.tri(tri,1)
slabs.obj()

# Low roof parapet band following the whole exact perimeter.
par=MeshBucket('DRUG | roof parapet',[mat_brick_dark,mat_concrete])
for ring in rings_model:
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]
        par.quad([(a[0],a[1],MAIN_WALL_TOP),(b[0],b[1],MAIN_WALL_TOP),(b[0],b[1],PARAPET_Z),(a[0],a[1],PARAPET_Z)],0)
        par.quad([(a[0],a[1],PARAPET_Z),(b[0],b[1],PARAPET_Z),(b[0],b[1],PARAPET_Z+.14),(a[0],a[1],PARAPET_Z+.14)],1)
par.obj()

# Put window bays along simplified, measured GIS facade segments (avoids false windows on CAD tessellation noise).
windows=MeshBucket('DRUG | facade glazing and aluminum window frames',[mat_glass,mat_metal,mat_spandrel,mat_mullion])
window_count=0
for ridx,ring in enumerate(rings_model):
    path=ring
    for i,a in enumerate(path):
        b=path[(i+1)%len(path)]; dx=b[0]-a[0];dy=b[1]-a[1]; L=math.hypot(dx,dy)
        if L<3.4:continue
        tx,ty=dx/L,dy/L
        # GIS rings are clockwise for the building shell and counterclockwise for courtyard holes.
        # Left normal faces outside on the shell and into the courtyard on a hole ring.
        nx,ny=-ty,tx
        # Lobby curtain bay south-facing, centered on main campus entrance; broad mullioned glazing.
        is_atrium=(ridx==0 and (a[0]+b[0])/2<min_x+.8 and abs(dx)<.22 and entry_y-8.5<(a[1]+b[1])/2<entry_y+8.5)
        if is_atrium:
            # mullions over the continuous glass wall from each floor, expressed in source-backed 3-storey rhythm
            num=max(2,int(L/2.1))
            for j in range(1,num):
                t=j/num; x=a[0]+dx*t+nx*.045; y=a[1]+dy*t+ny*.045
                windows.quad([(x-.055*ty,y+.055*tx,.25),(x+.055*ty,y-.055*tx,.25),(x+.055*ty,y-.055*tx,MAIN_WALL_TOP),(x-.055*ty,y+.055*tx,MAIN_WALL_TOP)],3)
            for z in (4.70,9.57,14.12):
                windows.quad([(a[0]+nx*.05,a[1]+ny*.05,z),(b[0]+nx*.05,b[1]+ny*.05,z),(b[0]+nx*.05,b[1]+ny*.05,z+.13),(a[0]+nx*.05,a[1]+ny*.05,z+.13)],1)
            # Double entry doors at ground level, slightly set behind curtain wall; paired pull frames.
            c=(a[0]+b[0])/2; cy=(a[1]+b[1])/2
            doorw=min(2.6,L*.32); H=3.2
            windows.quad([(c-tx*doorw/2+nx*.09,cy-ty*doorw/2+ny*.09,.20),(c+tx*doorw/2+nx*.09,cy+ty*doorw/2+ny*.09,.20),(c+tx*doorw/2+nx*.09,cy+ty*doorw/2+ny*.09,H),(c-tx*doorw/2+nx*.09,cy-ty*doorw/2+ny*.09,H)],0)
            window_count+=1
            continue
        # Regular recessed labs/office windows; each long structural panel gets evenly spaced bays on all 3 floors.
        n=max(1,int((L-.7)//3.15))
        spacing=(L-.65)/n
        for k in range(n):
            tc=.32+(k+.5)*spacing/L
            if tc>.95:continue
            cx=a[0]+dx*tc+nx*.045; cy=a[1]+dy*tc+ny*.045
            ww=min(2.05,spacing*.70); z0=.95; z1=3.05
            for fl in range(3):
                base=FLOORS[fl]
                # Ground floor windows are taller and begin at a robust masonry sill.
                lo=base+(0.85 if fl==0 else 1.05); hi=base+(3.35 if fl==0 else 3.52)
                A=(cx-tx*ww/2+nx*.06,cy-ty*ww/2+ny*.06)
                B=(cx+tx*ww/2+nx*.06,cy+ty*ww/2+ny*.06)
                windows.quad([(A[0],A[1],lo),(B[0],B[1],lo),(B[0],B[1],hi),(A[0],A[1],hi)],0)
                # Dark sill and head frame, plus a central bronze mullion.
                for z in (lo,hi-.07):
                    windows.quad([(A[0],A[1],z),(B[0],B[1],z),(B[0],B[1],z+.07),(A[0],A[1],z+.07)],1)
                mx=cx+nx*.07; my=cy+ny*.07
                windows.quad([(mx-.035*ty,my+.035*tx,lo),(mx+.035*ty,my-.035*tx,lo),(mx+.035*ty,my-.035*tx,hi),(mx-.035*ty,my+.035*tx,hi)],3)
                # Ground-level opaque spandrel below glazing echoes brick plinth.
                if fl==0:
                    windows.quad([(A[0],A[1],.59),(B[0],B[1],.59),(B[0],B[1],lo-.05),(A[0],A[1],lo-.05)],2)
                window_count+=1
windows.obj()

# Distinctive, broad cantilevered roof canopy over the glazed south entrance, matching Purdue architectural imagery.
# Orient the canopy parallel to the south side; its size and offset are inferred from the published perspective photo.
def cuboid(name, center, dims, mat):
    cx,cy,cz=center; sx,sy,sz=[d/2 for d in dims]
    verts=[(cx+sx*ix,cy+sy*iy,cz+sz*iz) for ix,iy,iz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob
front_x=min_x-.15
canopy_w=20.5; canopy_d=6.8
cuboid('DRUG | thin cantilever entrance canopy', (front_x+canopy_d/2,entry_y,16.82), (canopy_d,canopy_w,.42),mat_concrete)
# Bronze fascia / soffit grid on the underside.
cuboid('DRUG | bronze canopy fascia', (front_x+canopy_d/2,entry_y,16.59), (canopy_d-.18,canopy_w-.15,.08),mat_metal)
# Four slender structural columns provide the open, ceremonial entrance frame seen in the reference view.
for iy,y in enumerate((entry_y-8.4,entry_y-2.8,entry_y+2.8,entry_y+8.4),1):
    cuboid('DRUG | canopy column %02d'%iy,(front_x+1.1,y,8.42),(.34,.28,16.45),mat_concrete)
# Canopy soffit slim LED slots (physical detail but no fake lighting in exterior preview).
for yoff in (-5.8,0,5.8):
    cuboid('DRUG | canopy soffit linear light',(front_x+canopy_d/2,entry_y+yoff,16.53),(canopy_d-1.0,.10,.035),mat_metal)

# Terrace / roof mechanical boxes at the central core, compact and screened below roof datum.
for i,(ox,oy,w,d,h) in enumerate([(-4,7,4.2,3.2,1.05),(4,8,3.4,2.6,.95),(-10,9,2.8,2.0,.8)],1):
    cuboid('DRUG | screened rooftop equipment %02d'%i,(center_x+ox,center_y+oy,14.66+h/2),(w,d,h),mat_roof)
    for z in (14.78,14.95):
        cuboid('DRUG | rooftop equipment louver band',(center_x+ox,center_y+oy-d/2-.015,z),(w*.76,.025,.07),mat_metal)

# Interior entrance lobby: three story slabs, vestibule, reception island and a simple welcome/sign wall.
# The room functions and lobby are documented in Purdue's floorplan and interior rendering.
for z in (4.77,9.64):
    cuboid('DRUG | lobby gallery slab',(front_x+5.4,entry_y,z),(8.0,10.4,.22),mat_interior)
# A warm light stone reception desk visible behind the glazed entrance.
cuboid('DRUG | interior reception desk',(front_x+4.4,entry_y,1.15),(.82,4.2,1.0),mat_interior)
cuboid('DRUG | reception desk dark toe kick',(front_x+4.38,entry_y,.56),(.84,4.25,.12),mat_metal)
# Back wall of the lobby uses warm interior stone and a restrained university-gold accent panel.
cuboid('DRUG | lobby feature wall',(front_x+9.0,entry_y,5.7),(.18,9.2,8.4),mat_interior)
cuboid('DRUG | lobby feature accent',(front_x+8.88,entry_y,6.4),(.06,3.8,2.0),mat_mullion)
# Small abstract study tables on the gallery level, visible only through the atrium curtainwall.
for i,oy in enumerate((-3.1,3.1),1):
    cuboid('DRUG | lobby collaboration table %d'%i,(front_x+5.2,entry_y+oy,5.25),(1.0,2.1,.10),mat_interior)
    for ly in (-.8,.8): cuboid('DRUG | lobby table support',(front_x+5.2,entry_y+oy+ly,5.0),(.08,.08,.45),mat_metal)

# Create a clean, inspectable preview scene. Temporary items are removed before the asset is saved.
scene=bpy.context.scene
scene.name='Building_'+ASSET_ID
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.render.resolution_x=1120; scene.render.resolution_y=840;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world.color=(.07,.09,.13)
# Temporarily add ground plane for preview only.
groundmat=material('temporary preview lawn',(.18,.24,.15),.95)
me=bpy.data.meshes.new('preview ground mesh');me.from_pydata([(min_x-60,min_y-80,-.10),(max_x+60,min_y-80,-.10),(max_x+60,max_y+60,-.10),(min_x-60,max_y+60,-.10)],[],[(0,1,2,3)]);me.materials.append(groundmat)
ground=bpy.data.objects.new('TEMP Preview Ground',me);scene.collection.objects.link(ground)
# Sidewalk band in front of main entrance.
walkmat=material('temporary preview concrete walk',(.52,.50,.45),.85)
cuboid('TEMP Preview walk',(front_x-2.0,entry_y,-.045),(3.4,canopy_w+16,.08),walkmat)
# Lighting and camera.
world=scene.world
world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.18,.23,.31,1);bg.inputs['Strength'].default_value=.40

def area(name,loc,power,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((center_x,center_y,7))-ob.location).to_track_quat('-Z','Y').to_euler();return ob
lights=[area('TEMP soft key',(front_x-8,entry_y-24,42),11000,26,(1.0,.80,.62)),area('TEMP cool fill',(center_x-22,entry_y-8,26),7200,22,(.67,.79,1.0)),area('TEMP roof fill',(center_x+6,entry_y+25,36),5600,20,(1,.92,.78))]
camdata=bpy.data.cameras.new('TEMP Drug Discovery preview camera');cam=bpy.data.objects.new('TEMP Drug Discovery preview camera',camdata);scene.collection.objects.link(cam)
cam.location=(front_x-64,entry_y-16,30);target=Vector((center_x,center_y,7.2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=30;scene.camera=cam
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(OUT_DIR/'preview_drug_discovery_facility_2026-10-26.png')
# Render at preview quality; if Cycles is unavailable, use the bundled workbench path.
try: bpy.ops.render.render(write_still=True)
except Exception as e:
    print('CYCLES_RENDER_WARNING',repr(e));scene.render.engine='BLENDER_EEVEE_NEXT';bpy.ops.render.render(write_still=True)

# Remove preview-only scene objects and preserve only the building library in the native asset.
for ob in [ground,cam]+lights:
    if ob and ob.name in bpy.data.objects:bpy.data.objects.remove(ob,do_unlink=True)
scene.camera=None
for ob in list(scene.objects):
    if ob.name.startswith('TEMP Preview walk'):
        bpy.data.objects.remove(ob,do_unlink=True)
# Remove Blender startup camera, cube and lamp, leaving the saved library scene with the building collection only.
col_obj_names={o.name for o in col.objects}
for ob in list(scene.objects):
    if ob.name not in col_obj_names:
        bpy.data.objects.remove(ob,do_unlink=True)

# Keep the exact asset collection and collection-linked objects; all geometry coordinates remain in project world frame.
assert bpy.data.collections.get(COLLECTION_NAME) is col
assert len(col.objects)>=15
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
print(json.dumps({'asset_id':ASSET_ID,'asset':str(ASSET_PATH),'object_count':len(col.objects),'source_rings':len(rings),'source_vertices':[len(r) for r in rings],'source_local_bounds':[min_x,max_x,min_y,max_y], 'entry_y':entry_y, 'facade_vertices':[len(r) for r in rings_model],'main_roof_z_m':MAIN_WALL_TOP,'gis_roof_datum_m':ROOF_Z,'window_bays':window_count,'preview':str(OUT_DIR/'preview_drug_discovery_facility_2026-10-26.png')}))
