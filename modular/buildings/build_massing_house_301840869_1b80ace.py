import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "audit" / "sigma_kappa" / "sources" / "purdue_gis_fid780_raw.json"
OUT = ROOT / "modular" / "buildings" / "massing_house_301840869_1b80ace.blend"
PREVIEW = ROOT / "audit" / "sigma_kappa" / "preview.png"

feature = json.loads(RAW.read_text(encoding="utf-8-sig"))["features"][0]
attrs = feature["attributes"]
assert attrs["FID"] == 780 and attrs["BUILDING_N"] == "Sigma Kappa"
ring = feature["geometry"]["rings"][0][:-1]
lat0, lon0 = 40.4274, -86.9137
xy = [
    ((lon - lon0) * 111412.84 * math.cos(math.radians(lat0)), (lat - lat0) * 111040.0)
    for lon, lat in ring
]
assert len(xy) == 21

# Local design axes: s north, t west. The facade is illustratively oriented toward
# Russell Street; the source photograph/illustration is not georeferenced.
origin = xy[0]
u, n = (0.0, 1.0), (-1.0, 0.0)
local = [((x-origin[0])*u[0] + (y-origin[1])*u[1], (x-origin[0])*n[0] + (y-origin[1])*n[1]) for x,y in xy]
smin, smax = min(p[0] for p in local), max(p[0] for p in local)
tmin, tmax = min(p[1] for p in local), max(p[1] for p in local)
smid, tmid = (smin+smax)/2, (tmin+tmax)/2

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    if col.users == 0:
        bpy.data.collections.remove(col)
scene = bpy.context.scene
scene.name = "Building_massing_house_301840869_1b80ace"
asset = bpy.data.collections.new("Asset_massing_house_301840869_1b80ace")
scene.collection.children.link(asset)

def material(name, color, roughness=0.82):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    return m

brick = material("Sigma Kappa red brick", (0.48, 0.24, 0.19))
roof = material("Dark slate roof", (0.20, 0.22, 0.25))
trim = material("Portico and window trim", (0.91, 0.88, 0.79))
glass = material("Blue-gray window glass", (0.10, 0.18, 0.22), 0.28)
door = material("Deep maroon entry door", (0.16, 0.045, 0.055))
foundation = material("Foundation stone", (0.42, 0.39, 0.35))
materials = [brick, roof, trim, glass, door, foundation]
verts, faces, mat_ids = [], [], []

def world(s, t, z):
    return (origin[0] + u[0]*s + n[0]*t, origin[1] + u[1]*s + n[1]*t, z)

def face(points, mat_id):
    ids = []
    for s,t,z in points:
        ids.append(len(verts))
        verts.append(world(s,t,z))
    faces.append(ids)
    mat_ids.append(mat_id)

def box(s, t, z, ds, dt, dz, mat_id):
    s0,s1 = s-ds/2, s+ds/2
    t0,t1 = t-dt/2, t+dt/2
    z0,z1 = z-dz/2, z+dz/2
    p = [(s0,t0,z0),(s1,t0,z0),(s1,t1,z0),(s0,t1,z0),
         (s0,t0,z1),(s1,t0,z1),(s1,t1,z1),(s0,t1,z1)]
    for ids in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        face([p[i] for i in ids], mat_id)

def column(s, t, z0, z1, radius=0.22, mat_id=2, segments=12):
    lower, upper = [], []
    for i in range(segments):
        a = 2*math.pi*i/segments
        lower.append((s+radius*math.cos(a), t+radius*math.sin(a), z0))
        upper.append((s+radius*math.cos(a), t+radius*math.sin(a), z1))
    face(list(reversed(lower)), mat_id)
    face(upper, mat_id)
    for i in range(segments):
        j = (i+1) % segments
        face([lower[i],lower[j],upper[j],upper[i]], mat_id)

def window(s, t, z, width=1.55, height=1.75):
    box(s,t-0.13,z,width,0.10,height,3)
    for ss in (s-width/2-0.12,s+width/2+0.12):
        box(ss,t-0.23,z,0.20,0.14,height+0.28,2)
    for zz in (z-height/2-0.12,z+height/2+0.12):
        box(s,t-0.23,zz,width+0.44,0.14,0.20,2)
    box(s,t-0.31,z,0.09,0.10,height,2)
    box(s,t-0.31,z,width,0.10,0.08,2)

def gable_roof(a, b, tfront, tback, eave, ridge):
    mid = (a+b)/2
    face([(a,tfront,eave),(a,tback,eave),(mid,tback,ridge),(mid,tfront,ridge)],1)
    face([(mid,tfront,ridge),(mid,tback,ridge),(b,tback,eave),(b,tfront,eave)],1)
    face([(a,tfront,eave),(b,tfront,eave),(mid,tfront,ridge)],0)
    face([(a,tback,eave),(mid,tback,ridge),(b,tback,eave)],0)
    # Pale rake boards make the two front gable outlines legible.
    for s1,z1,s2,z2 in ((a,eave,mid,ridge),(mid,ridge,b,eave)):
        d = math.hypot(s2-s1,z2-z1)
        off_s, off_z = -(z2-z1)*0.11/d, (s2-s1)*0.11/d
        face([(s1+off_s,tfront-0.05,z1+off_z),(s2+off_s,tfront-0.05,z2+off_z),
              (s2-off_s,tfront-0.05,z2-off_z),(s1-off_s,tfront-0.05,z1-off_z)],2)

# Footprint-exact shell. GIS ring vertices are retained at both the base and wall top.
def prism(poly, z0, z1):
    for i, a in enumerate(poly):
        b = poly[(i+1) % len(poly)]
        face([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)],0)
    face([(s,t,z1) for s,t in poly],0)
    face([(s,t,z0) for s,t in reversed(poly)],5)

prism(local, 0.0, 0.55)
prism(local, 0.55, 3.65)
prism(local, 3.65, 3.95)
prism(local, 3.95, 7.15)

# Main roof: twin end gables and a lower central ridge with four small dormers,
# following the non-scaled Sigma Kappa house illustration.
roof_overhang = 0.22
front = tmax + roof_overhang
back = tmin - roof_overhang
width = smax-smin
wing = min(9.0, width*0.25)
gable_roof(smin-roof_overhang, smin+wing, front, back, 7.15, 11.65)
gable_roof(smax-wing, smax+roof_overhang, front, back, 7.15, 11.65)
ca, cb = smin+wing-0.35, smax-wing+0.35
cm = (ca+cb)/2
ridge_t = tmid
face([(ca,front,7.15),(ca,back,7.15),(cm,back,9.75),(cm,front,9.75)],1)
face([(cm,front,9.75),(cm,back,9.75),(cb,back,7.15),(cb,front,7.15)],1)
face([(ca,front,7.15),(cb,front,7.15),(cm,front,9.75)],0)
face([(ca,back,7.15),(cm,back,9.75),(cb,back,7.15)],0)

# Chimney at the right end and four small paired-window dormers on the central roof.
chimney_s = smax - 5.2
box(chimney_s, tmid-1.0, 11.6, 1.5, 1.8, 7.0, 0)
box(chimney_s, tmid-1.0, 15.15, 1.7, 2.0, 0.30, 2)

# The drawing shows a centered columned portico and symmetrical two-story wings.
port_w = min(12.5, width*0.36)
port_d = 3.0
porch_t = front + port_d
column_bottom, column_top = 0.58, 7.28
for ss in (smid-port_w*0.40, smid-port_w*0.14, smid+port_w*0.14, smid+port_w*0.40):
    column(ss, porch_t-0.12, column_bottom, column_top, 0.24, 2)
box(smid, porch_t-0.12, 7.32, port_w+0.75, 0.48, 0.34, 2)
# triangular pediment face and its stone outline
face([(smid-port_w/2-0.35,porch_t-0.42,7.48),(smid+port_w/2+0.35,porch_t-0.42,7.48),(smid,porch_t-0.42,9.25)],2)
box(smid, porch_t-0.16, 7.52, port_w+0.90, 0.52, 0.20, 2)
box(smid, porch_t-0.16, 9.28, 0.42, 0.48, 0.26, 2)

# Main entry and window rhythm. Facade details are estimates from the drawing;
# exact facade bearing is unverified because the illustration has no geolocation.
door_width, door_height = 2.15, 2.85
box(smid, front+0.10, 2.15, door_width, 0.14, door_height, 4)
for ss in (smid-door_width/2-0.15, smid+door_width/2+0.15):
    box(ss, front+0.02, 2.15, 0.22, 0.30, 3.18, 2)
box(smid, front+0.02, 3.76, door_width+0.52, 0.30, 0.22, 2)
box(smid, front+0.02, 3.62, 0.08, 0.10, 0.24, 2)

available = [smin+2.6+i*((width-5.2)/7) for i in range(8)]
for ss in available:
    if abs(ss-smid) < port_w*0.55:
        continue
    window(ss, front-0.01, 2.25, 1.65, 1.75)
    window(ss, front-0.01, 5.35, 1.65, 1.75)

# Four dormers across the central roof, each with a pale gable surround and glazing.
for i in range(4):
    ss = ca + (cb-ca)*(i+0.5)/4
    t = front - (front-back)*0.43
    z = 8.65
    box(ss,t,z,2.25,1.35,1.25,0)
    box(ss,t+0.69,z,0.14,0.16,1.52,2)
    box(ss,t+0.69,z+0.68,2.35,0.18,0.14,2)
    box(ss,t+0.69,z,1.72,0.12,0.94,3)

# Steps, intentionally decorative and projecting just beyond the front wall.
for j in range(4):
    box(smid, front+0.65+j*0.45, 0.16+j*0.10, 4.4, 0.95, 0.32+j*0.20, 5)

mesh = bpy.data.meshes.new("Sigma Kappa FID 780 footprint and illustration-based detail")
mesh.from_pydata(verts, [], faces)
mesh.update()
obj = bpy.data.objects.new("House_301840869", mesh)
asset.objects.link(obj)
for mat in materials:
    mesh.materials.append(mat)
for poly, idx in zip(mesh.polygons, mat_ids):
    poly.material_index = idx
obj.location = (0,0,0)
obj.rotation_euler = (0,0,0)
obj.scale = (1,1,1)
obj["building_name"] = "Sigma Kappa, Beta Sigma Chapter"
obj["source_fid"] = 780
obj["official_address"] = "427 N Russell St"
obj["footprint_source"] = "Purdue BuildingShapesZip4 FID 780"
obj["floor_status"] = "Two exterior stories plus attic dormers estimated from a non-scaled house illustration; GIS NUM_LEVELS=1 is undocumented"
obj["height_status"] = "Estimated: 7.15 m eaves, 11.65 m gable ridge, 15.3 m chimney; GIS Extrution=12 has unknown semantics"
obj["front_status"] = "Illustratively oriented toward Russell Street; source illustration is not georeferenced"

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 820
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.34,0.37,0.41,1)
background.inputs["Strength"].default_value = 0.45

def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

cam_data = bpy.data.cameras.new("Sigma Kappa preview camera")
cam = bpy.data.objects.new("Sigma Kappa preview camera", cam_data)
scene.collection.objects.link(cam)
cam.location = world(smid-4.0, front+54.0, 23.0)
aim(cam, world(smid, tmid, 6.1))
cam.data.type = "ORTHO"
cam.data.ortho_scale = max(width+16.0, 52.0)
scene.camera = cam

light_data = bpy.data.lights.new("Sigma Kappa preview area", "AREA")
light = bpy.data.objects.new("Sigma Kappa preview area", light_data)
scene.collection.objects.link(light)
light.location = world(smid-16.0, front+26.0, 29.0)
light.data.energy = 7600
light.data.shape = "DISK"
light.data.size = 24
aim(light, world(smid,tmid,5.0))
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
scene.render.filepath = str(PREVIEW)

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True)
bpy.data.objects.remove(light, do_unlink=True)
bpy.data.cameras.remove(cam_data)
bpy.data.lights.remove(light_data)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print("SAVED", OUT, "vertices", len(mesh.vertices), "faces", len(mesh.polygons), "gis_ring", len(local), "bounds", smin,smax,tmin,tmax)
