import bpy, json, math, os
from mathutils import Vector

ASSET_ID = 'massing_hawkins_hall_282335f'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET_PATH = os.path.join(os.path.dirname(__file__), ASSET_ID + '.blend')
EVIDENCE_DIR = os.path.join(ROOT, 'audit', ASSET_ID)
SOURCE_PATH = os.path.join(EVIDENCE_DIR, 'sources', 'purdue_building_shapes_fid83_full_2026-10-26.json')
PREVIEW_PATH = os.path.join(EVIDENCE_DIR, 'preview_exterior.png')
COLLECTION_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID

# Plan geometry is the current Purdue BuildingShapes GIS polygon for Hawkins Hall
# (FID 83 / BLDG_ABBR HAWK). Convert WGS84 vertices with modular/AGENT.md's
# documented local campus approximation; preserve the manifest's world placement.
feature = json.load(open(SOURCE_PATH, encoding='utf-8-sig'))['features'][0]
assert feature['attributes']['BLDG_ABBR'] == 'HAWK' and feature['attributes']['BUILDING_N'] == 'George A. Hawkins Hall'
raw_ring = feature['geometry']['rings'][0]
ring = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0) for lon, lat in raw_ring]
if ring[0] == ring[-1]: ring = ring[:-1]
# Drop almost-duplicate drafting vertices while preserving all meaningful corners.
clean=[]
for p in ring:
    if not clean or math.dist(p, clean[-1]) > 0.025: clean.append(p)
if math.dist(clean[0], clean[-1]) <= 0.025: clean.pop()
ring=clean

# The official Purdue OEP plan says the east wing has 13 floors, west wing 10,
# joined by a central area. Purdue GIS gives 140 ft extrusion (42.672 m). Model
# that maximum height and an estimated, lower 10-floor west/connector height by
# dividing the GIS height evenly over the 13 east-wing floors.
TOTAL_HEIGHT = 140.0 * 0.3048
FLOOR_COUNT_EAST = 13
FLOOR_COUNT_WEST = 10
FLOOR_HEIGHT_EST = TOTAL_HEIGHT / FLOOR_COUNT_EAST
WEST_HEIGHT_EST = FLOOR_COUNT_WEST * FLOOR_HEIGHT_EST

# GIS footprint segment for the east wing, traced from FID 83's ring. The split
# follows the visible/repeated north-south tower on the east side; the exact
# architectural demarcation is an approximation because no public plan set was found.
east_ring = [
    (183.026, -491.687), (198.053, -492.491), (198.358, -495.671),
    (198.790, -547.670), (200.930, -547.650), (200.960, -550.540),
    (198.820, -550.560), (198.870, -557.060), (183.540, -557.180),
    (183.150, -508.650)
]

# Exported objects remain campus/world-coordinate meshes. The collection name,
# asset ID, scene name and file path remain manifest-stable.
scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
scene.name = SCENE_NAME
coll = bpy.data.collections.get(COLLECTION_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(coll)
for obj in list(coll.objects): bpy.data.objects.remove(obj, do_unlink=True)


def material(name, color, roughness=.82, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return m

brick = material('Hawkins | red-orange brick', (.31,.075,.043), .88)
brick_alt = material('Hawkins | brick band', (.40,.13,.075), .88)
stone = material('Hawkins | pale stone trim', (.60,.53,.42), .8)
glass = material('Hawkins | blue gray glazing', (.025,.12,.17), .24,.14)
frame = material('Hawkins | dark window metal', (.065,.075,.08), .46,.3)
roof = material('Hawkins | flat roof membrane', (.21,.23,.24), .93)
concrete = material('Hawkins | entrance concrete', (.43,.42,.39), .92)


def signed_area(poly):
    return sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2


def extruded_polygon(name, poly, z0, z1, side_material, roof_material):
    n=len(poly)
    verts=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(side_material); mesh.materials.append(roof_material)
    mesh.polygons[0].material_index=0; mesh.polygons[1].material_index=1
    for p in mesh.polygons[2:]: p.material_index=0
    mesh.update()
    obj=bpy.data.objects.new(name,mesh); coll.objects.link(obj)
    return obj

# Continuous lower mass, split upper silhouette; flat roofs match the current aerial.
main = extruded_polygon('Hawkins | ten-floor lower footprint', ring, 0.0, WEST_HEIGHT_EST, brick, roof)
east = extruded_polygon('Hawkins | east wing upper three floors', east_ring, WEST_HEIGHT_EST, TOTAL_HEIGHT, brick, roof)

# Mesh builders keep repeated facade details compact and portable.
def mesh_from_faces(name, verts, faces, mats, material_indices=None):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(verts,[],faces)
    for m in mats: me.materials.append(m)
    if material_indices:
        for p,mi in zip(me.polygons,material_indices): p.material_index=mi
    me.update(); ob=bpy.data.objects.new(name,me); coll.objects.link(ob); return ob


def outward_normal(a,b,ccw):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    if length==0: return (0,0)
    return ((dy/length,-dx/length) if ccw else (-dy/length,dx/length))


def facade_details(poly, floors, z0_floor, z1_floor, prefix, start_floor=0):
    ccw=signed_area(poly)>0
    window_verts=[]; window_faces=[]; window_mi=[]
    band_verts=[]; band_faces=[]; band_mi=[]
    for edge_i,a in enumerate(poly):
        b=poly[(edge_i+1)%len(poly)]
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length<2.1: continue
        tangent=(dx/length,dy/length); normal=outward_normal(a,b,ccw)
        count=max(1,int(length/4.2))
        # Subtle continuous floor courses on the brick facade.
        for level in range(start_floor+1,floors+1):
            z=level*FLOOR_HEIGHT_EST
            if z>z1_floor+.02: continue
            off=.055; h=.13
            base=len(band_verts)
            band_verts += [
                (a[0]+normal[0]*off,a[1]+normal[1]*off,z-h/2),
                (b[0]+normal[0]*off,b[1]+normal[1]*off,z-h/2),
                (b[0]+normal[0]*off,b[1]+normal[1]*off,z+h/2),
                (a[0]+normal[0]*off,a[1]+normal[1]*off,z+h/2)]
            band_faces.append((base,base+1,base+2,base+3)); band_mi.append(0 if level%2 else 1)
        # Repetitive paired-story windows, derived from the official photo rhythm.
        for floor in range(start_floor,floors):
            zbase=floor*FLOOR_HEIGHT_EST
            if zbase+FLOOR_HEIGHT_EST>z1_floor+1e-5: continue
            center_z=zbase+1.95
            for j in range(count):
                t=(j+1)/(count+1); cx=a[0]+dx*t; cy=a[1]+dy*t
                # Avoid an unsupported doorway opening at the inferred central entrance.
                if floor==0 and math.hypot(cx-176.0,cy+531.5)<3.1: continue
                ww=min(1.52,length/(count+1)*.42); hh=1.42
                outer_off=.105
                # One outer rectangle with inset glazing; a narrow center mullion recalls the paired panes.
                def point(u,v,off=outer_off): return (cx+tangent[0]*u+normal[0]*off,cy+tangent[1]*u+normal[1]*off,v)
                x0,x1=-ww/2,ww/2; z0,z1=center_z-hh/2,center_z+hh/2
                ix0,ix1=x0+.105,x1-.105; iz0,iz1=z0+.10,z1-.10
                # Four dark frame quads around the glass aperture.
                for corners in [((x0,z0),(x1,z0),(x1,iz0),(x0,iz0)),((x0,iz1),(x1,iz1),(x1,z1),(x0,z1)),((x0,iz0),(ix0,iz0),(ix0,iz1),(x0,iz1)),((ix1,iz0),(x1,iz0),(x1,iz1),(ix1,iz1))]:
                    k=len(window_verts); window_verts.extend(point(u,v) for u,v in corners); window_faces.append((k,k+1,k+2,k+3)); window_mi.append(0)
                k=len(window_verts); window_verts.extend(point(u,v,outer_off-.012) for u,v in ((ix0,iz0),(ix1,iz0),(ix1,iz1),(ix0,iz1))); window_faces.append((k,k+1,k+2,k+3)); window_mi.append(1)
                # Middle mullion on the glass, fine at this scale.
                mw=.045; k=len(window_verts)
                window_verts.extend(point(u,v,outer_off-.006) for u,v in ((-mw/2,iz0),(mw/2,iz0),(mw/2,iz1),(-mw/2,iz1)))
                window_faces.append((k,k+1,k+2,k+3)); window_mi.append(0)
    if band_faces: mesh_from_faces(prefix+' floor courses',band_verts,band_faces,[brick_alt,stone],band_mi)
    if window_faces: mesh_from_faces(prefix+' windows and frames',window_verts,window_faces,[frame,glass,stone],window_mi)

facade_details(ring,FLOOR_COUNT_WEST,0.0,WEST_HEIGHT_EST,'Hawkins | west and shared facade')
facade_details(east_ring,FLOOR_COUNT_EAST,0.0,TOTAL_HEIGHT,'Hawkins | east wing facade',start_floor=FLOOR_COUNT_WEST)

# Approximate glazed central-area entrance and modest canopy at the curved south connector.
# This feature's exact entrance station is not dimensioned in public sources.
entry_center=(176.2,-531.2); entry_z=1.55
entry_verts=[]; entry_faces=[]; entry_mi=[]
# Simple glazed door pair oriented on a plausible south-facing central connector wall.
# The source plan confirms a central area and multiple ground exits, not this exact door position.
normal=(.12,-.99); tangent=(.99,.12); width=2.6; height=2.8; off=.18
for x0,x1 in [(-width/2,-.05),(.05,width/2)]:
    k=len(entry_verts)
    entry_verts.extend([(entry_center[0]+tangent[0]*u+normal[0]*off,entry_center[1]+tangent[1]*u+normal[1]*off,z) for u,z in ((x0,0.12),(x1,0.12),(x1,height),(x0,height))])
    entry_faces.append((k,k+1,k+2,k+3)); entry_mi.append(0)
mesh_from_faces('Hawkins | inferred central glazed entry',entry_verts,entry_faces,[glass],entry_mi)

# Scene metadata, review camera, soft lighting and ground are outside the exported collection.
scene['building_id']=ASSET_ID
scene['source_geometry']='Purdue BuildingShapes FID 83 footprint with documented local transform; 13-floor east wing / 10-floor west wing from Purdue OEP; overall extrusion 140 ft from Purdue GIS.'
scene['height_note']='140 ft maximum from official GIS attribute; east/west floor counts per 2026 OEP. West/connector height is an estimate at 10/13 of 140 ft.'
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1200; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.26,.32,.39,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
all_xy=[p for p in ring]; cx=sum(x for x,y in all_xy)/len(all_xy); cy=sum(y for x,y in all_xy)/len(all_xy)
cam_data=bpy.data.cameras.new('Hawkins review camera'); cam=bpy.data.objects.new('Hawkins review camera',cam_data); scene.collection.objects.link(cam)
cam.location=(cx-130,cy-125,84); target=Vector((cx,cy,19)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); cam.data.lens=50; scene.camera=cam
light_data=bpy.data.lights.new('Hawkins broad softbox','AREA'); light_data.energy=7000; light_data.shape='DISK'; light_data.size=105
light=bpy.data.objects.new('Hawkins broad softbox',light_data); scene.collection.objects.link(light); light.location=(cx-45,cy-45,110); light.rotation_euler=(Vector((cx,cy,18))-Vector(light.location)).to_track_quat('-Z','Y').to_euler()
ground_mesh=bpy.data.meshes.new('Hawkins preview ground mesh'); ground_mesh.from_pydata([(cx-120,cy-150,-.15),(cx+120,cy-150,-.15),(cx+120,cy+150,-.15),(cx-120,cy+150,-.15)],[],[(0,1,2,3)]); ground_mesh.materials.append(concrete)
ground=bpy.data.objects.new('Hawkins | preview ground',ground_mesh); scene.collection.objects.link(ground)
scene.view_settings.view_transform='Standard'; scene.view_settings.look='Medium High Contrast'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
os.makedirs(EVIDENCE_DIR,exist_ok=True)
scene.render.filepath=PREVIEW_PATH
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)
bpy.ops.render.render(write_still=True)
print('HAWKINS_BUILD_COMPLETE',ASSET_PATH,PREVIEW_PATH,'ring_vertices',len(ring),'floor_height_est_m',FLOOR_HEIGHT_EST)


