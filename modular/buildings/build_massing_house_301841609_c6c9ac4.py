"""Build a source-grounded, deliberately conservative Circle Pines massing asset.

Run with Blender 5.x: blender --background --python this_file.py

The wall footprint and campus placement come from Purdue's FID 761 GIS feature.
No current public elevation/plan was located, so roof, floor count, height,
entry, materials and window rhythm are documented design estimates.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, geometry

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "circle_pines"
SOURCE = AUDIT / "sources" / "purdue_gis_fid761_raw.json"
OUT = ROOT / "modular" / "buildings" / "massing_house_301841609_c6c9ac4.blend"
ASSET_ID = "massing_house_301841609_c6c9ac4"
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
OBJECT_NAME = "House_301841609"
LAT0, LON0 = 40.4274, -86.9137
XS = 111412.84 * math.cos(math.radians(LAT0))
YS = 111040.0
WALL_Z = 6.4            # estimated two-storey eaves, about 3.2 m per floor
ROOF_Z = 7.3            # estimated low parapet top; not a surveyed dimension

feature = json.loads(SOURCE.read_text(encoding="utf-8-sig"))["features"][0]
assert feature["attributes"]["FID"] == 761
assert feature["attributes"]["BUILDING_N"] == "Circle Pines"
ring_ll = feature["geometry"]["rings"][0]
if ring_ll[0] == ring_ll[-1]:
    ring_ll = ring_ll[:-1]
ring = [((lon-LON0)*XS, (lat-LAT0)*YS) for lon,lat in ring_ll]
assert len(ring) == 44
signed_area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
OUTWARD_SIGN=1.0 if signed_area<0 else -1.0

def outward_point(x,y,angle,distance):
    return (x-math.sin(angle)*OUTWARD_SIGN*distance,
            y+math.cos(angle)*OUTWARD_SIGN*distance)

# The simple massing library retains campus coordinates and identity transforms.
verts, faces, face_mats = [], [], []
materials = []
def material(name, color, roughness=0.82):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    m.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=(*color,1)
    m.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value=roughness
    materials.append(m)
    return len(materials)-1

brick=material("Circle Pines | observed red-brown brick",(0.31,0.075,0.045))
roofmat=material("Circle Pines | estimated charcoal roof",(0.17,0.19,0.20))
trim=material("Circle Pines | estimated cream trim",(0.84,0.79,0.67))
glass=material("Circle Pines | dark glazing",(0.12,0.22,0.28),0.34)
door=material("Circle Pines | estimated entry door",(0.24,0.13,0.08))
foundation=material("Circle Pines | foundation",(0.28,0.29,0.28))

def add_poly(vs, fs, mi):
    start=len(verts)
    verts.extend(vs)
    faces.extend([tuple(start+i for i in f) for f in fs])
    face_mats.extend([mi]*len(fs))

def add_box(center, dims, angle, mi):
    cx,cy,cz=center; dx,dy,dz=dims
    ca,sa=math.cos(angle),math.sin(angle)
    local=[(-dx/2,-dy/2,-dz/2),(dx/2,-dy/2,-dz/2),(dx/2,dy/2,-dz/2),(-dx/2,dy/2,-dz/2),
           (-dx/2,-dy/2,dz/2),(dx/2,-dy/2,dz/2),(dx/2,dy/2,dz/2),(-dx/2,dy/2,dz/2)]
    vs=[(cx+x*ca-y*sa,cy+x*sa+y*ca,cz+z) for x,y,z in local]
    fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    add_poly(vs,fs,mi)

# Main wall shell follows every GIS boundary segment.
n=len(ring)
for i,(x1,y1) in enumerate(ring):
    x2,y2=ring[(i+1)%n]
    add_poly([(x1,y1,0),(x2,y2,0),(x2,y2,WALL_Z),(x1,y1,WALL_Z)],[(0,1,2,3)],brick)

# GIS ring is simple with no interior courtyard. Add a low parapet and flat
# roof, visually supported by current street view; height is still an estimate.
for i,(x1,y1) in enumerate(ring):
    x2,y2=ring[(i+1)%n]
    add_poly([(x1,y1,WALL_Z),(x2,y2,WALL_Z),(x2,y2,ROOF_Z),(x1,y1,ROOF_Z)],[(0,1,2,3)],brick)
poly=[Vector((x,y)) for x,y in ring]
triangles=geometry.tessellate_polygon([poly])
roof_faces=[]
for t in triangles:
    ids=tuple(int(k) for k in t)
    roof_faces.append(ids)
add_poly([(x,y,ROOF_Z) for x,y in ring],roof_faces,roofmat)
add_poly([(x,y,0) for x,y in ring],[(tuple(reversed(range(n))))],foundation)

# Cream-gray horizontal belt courses and parapet cap follow the GIS wall edge.
for i,(x1,y1) in enumerate(ring):
    x2,y2=ring[(i+1)%n]
    dx,dy=x2-x1,y2-y1
    length=math.hypot(dx,dy)
    if length < 0.8: continue
    angle=math.atan2(dy,dx)
    px=(x1+x2)/2;py=(y1+y2)/2
    bx,by=outward_point(px,py,angle,0.04)
    add_box((bx,by,3.38),(length,0.16,0.13),angle,trim)
    add_box((bx,by,6.47),(length,0.18,0.15),angle,trim)
    add_box((bx,by,7.12),(length,0.22,0.16),angle,trim)

# Repeated dark windows with narrow masonry-colored surrounds. A 3.6 m bay
# rhythm follows the current Street View's repetitive two-storey facade.
for i,(x1,y1) in enumerate(ring):
    x2,y2=ring[(i+1)%n]
    dx,dy=x2-x1,y2-y1
    length=math.hypot(dx,dy)
    if length < 2.8:
        continue
    angle=math.atan2(dy,dx)
    count=max(1,int(length//3.6))
    for j in range(count):
        t=(j+0.5)/count
        px=x1+dx*t; py=y1+dy*t
        gx,gy=outward_point(px,py,angle,0.07)
        fx,fy=outward_point(px,py,angle,0.16)
        # Thin exterior boxes are oriented with each GIS boundary edge.
        for z in (1.95,4.9):
            # Dark glazing is set just proud of the wall; slim rails frame it
            # without covering the glass as a solid backing plate would.
            add_box((gx,gy,z),(1.55,0.08,1.12),angle,glass)
            for side in (-1,1):
                rx=fx-side*math.sin(angle)*OUTWARD_SIGN*0.80
                ry=fy+side*math.cos(angle)*OUTWARD_SIGN*0.80
                add_box((rx,ry,z),(0.08,0.07,1.22),angle,trim)
            for side in (-1,1):
                add_box((fx,fy,z+side*0.60),(1.68,0.07,0.08),angle,trim)
            add_box((fx,fy,z),(0.045,0.06,1.08),angle,trim)

# A restrained illustrative entrance is placed on the north edge visible in the
# April 2026 Street View; its exact position remains approximate.
front_edges=[(i,math.hypot(ring[(i+1)%n][0]-x,ring[(i+1)%n][1]-y))
             for i,(x,y) in enumerate(ring)]
if front_edges:
    i,_=max(front_edges,key=lambda item:(ring[item[0]][1]+ring[(item[0]+1)%n][1])/2)
    x1,y1=ring[i];x2,y2=ring[(i+1)%n]
    dx,dy=x2-x1,y2-y1; length=math.hypot(dx,dy);angle=math.atan2(dy,dx)
    px=(x1+x2)/2;py=(y1+y2)/2
    tx,ty=outward_point(px,py,angle,0.08)
    dxp,dyp=outward_point(px,py,angle,0.19)
    canopy_x,canopy_y=outward_point(px,py,angle,0.45)
    add_box((tx,ty,1.35),(1.15,0.18,2.65),angle,trim)
    add_box((dxp,dyp,1.3),(0.87,0.06,2.3),angle,door)
    add_box((canopy_x,canopy_y,2.85),(2.0,0.95,0.18),angle,roofmat)

# Replace scene contents with one named mesh object in the expected collection.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    if col.name != "Collection":
        bpy.data.collections.remove(col)
scene=bpy.context.scene
scene.name=SCENE_NAME
default=bpy.data.collections.get("Collection")
if default: bpy.data.collections.remove(default)
asset=bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset)
mesh=bpy.data.meshes.new(OBJECT_NAME+"Mesh")
mesh.from_pydata(verts,[],faces)
for m in materials: mesh.materials.append(m)
mesh.update()
obj=bpy.data.objects.new(OBJECT_NAME,mesh)
asset.objects.link(obj)
for p,mi in zip(mesh.polygons,face_mats): p.material_index=mi
obj["building_id"]=ASSET_ID
obj["source_feature_id"]=761
obj["source_name"]="Circle Pines"
obj["footprint_source"]="Purdue BuildingShapesZip4 FID 761; geographic coordinates transformed using project approximation"
obj["coordinate_frame"]="Campus coordinates in meters; identity object transform"
obj["estimated_height_m"]=ROOF_Z
obj["height_status"]="estimated; public GIS Extrution=32 is undocumented and not treated as a height measurement"
obj["architecture_status"]="roof, floors, facade rhythm, entry and materials are schematic estimates; no current public elevation located"
obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)

# Presentation-only camera and lights live outside the asset collection and are
# removed before saving the portable library file after rendering.
presentation=bpy.data.collections.new("Presentation_Circle_Pines")
scene.collection.children.link(presentation)
center=Vector((sum(x for x,y in ring)/n,sum(y for x,y in ring)/n,3.8))
def presentation_obj(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    presentation.objects.link(o)

bpy.ops.object.camera_add(location=center+Vector((42,-92,29)))
camera=bpy.context.object;presentation_obj(camera);camera.name="Circle Pines preview camera"
camera.data.type="ORTHO";camera.data.ortho_scale=88
camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
scene.camera=camera
for loc,power,size in [(center+Vector((18,-38,58)),6000,35),(center+Vector((-45,25,32)),3500,28)]:
    bpy.ops.object.light_add(type="AREA",location=loc)
    light=bpy.context.object;presentation_obj(light);light.data.energy=power;light.data.shape="DISK";light.data.size=size
    light.rotation_euler=(center-light.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.light_add(type="SUN",location=center+Vector((25,-30,65)))
sun=bpy.context.object;presentation_obj(sun);sun.data.energy=2.2;sun.data.angle=math.radians(12)
sun.rotation_euler=(center-sun.location).to_track_quat("-Z","Y").to_euler()
world=bpy.data.worlds.new("Circle Pines neutral preview") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world;world.use_nodes=True
world.node_tree.nodes.get("Background").inputs["Color"].default_value=(0.48,0.52,0.58,1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value=0.55
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1500;scene.render.resolution_y=1150;scene.render.resolution_percentage=100
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=0.7
scene.render.image_settings.file_format="PNG"
preview=AUDIT/"preview.png"
scene.render.filepath=str(preview)
bpy.ops.render.render(write_still=True)
street_camera_data=bpy.data.cameras.new("Circle Pines street-level preview lens")
street_camera=bpy.data.objects.new("Circle Pines street-level preview camera",street_camera_data)
presentation.objects.link(street_camera)
street_camera.location=center+Vector((-52,60,-2.1))
street_camera.data.type="ORTHO";street_camera.data.ortho_scale=88
street_camera.rotation_euler=(center-street_camera.location).to_track_quat("-Z","Y").to_euler()
scene.camera=street_camera
scene.render.filepath=str(AUDIT/"preview_street.png")
bpy.ops.render.render(write_still=True)

# Save a clean one-object library without presentation objects.
for o in list(presentation.objects): bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(presentation)
scene.camera=None
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print(f"Saved {OUT} with {len(ring)} GIS vertices, {len(mesh.vertices)} combined vertices")
