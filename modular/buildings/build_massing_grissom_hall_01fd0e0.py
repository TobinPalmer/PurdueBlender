"""Procedurally detail the Rossen-assigned Grissom Hall library asset.

Run from the repository root with Blender 4.5+ and the assigned .blend open.
The original official-GIS shell perimeter and campus coordinates are preserved.
The assigned footprint is Purdue BuildingShapesZip4 FID 236 (not generalized
campus MapServer OID 180). Vertical GIS field units are undocumented; the
three-story height is therefore modeled from an explicitly inferred feet
interpretation and remains provisional. Façade bay spacing is estimated.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path.cwd()
ID = "massing_grissom_hall_01fd0e0"
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
GIS = ROOT / "audit" / ID / "sources" / "official_feature_236.json"
PREVIEWS = ROOT / "audit" / ID / "previews"
PREVIEWS.mkdir(parents=True, exist_ok=True)
SCENE = bpy.data.scenes.get(f"Building_{ID}") or bpy.context.scene
COLLECTION = bpy.data.collections.get(f"Asset_{ID}")
SHELL = (bpy.data.objects.get("Grissom Hall") or
         bpy.data.objects.get("Grissom Hall | source footprint shell"))
if COLLECTION is None or SHELL is None or SHELL.type != "MESH":
    raise RuntimeError("Assigned Grissom scene, collection, or shell is missing")

def mat(name, color, roughness=0.72):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = roughness
    return m

BRICK = mat("Grissom | red brick", (0.44, 0.115, 0.072))
STONE = mat("Grissom | limestone", (0.78, 0.72, 0.61))
GLASS = mat("Grissom | glazing", (0.055, 0.13, 0.18), 0.24)
FRAME = mat("Grissom | pale window frame", (0.82, 0.79, 0.70))
DOOR = mat("Grissom | entry glass", (0.10, 0.22, 0.26), 0.22)
for m in (BRICK, STONE, GLASS, FRAME, DOOR):
    if m.name not in [x.name for x in SHELL.data.materials]:
        SHELL.data.materials.append(m)
SHELL.data.materials[0] = BRICK
for p in SHELL.data.polygons:
    p.material_index = 0
SHELL.name = "Grissom Hall"
for obj in list(COLLECTION.objects):
    if obj.name.startswith("Grissom detail |"):
        bpy.data.objects.remove(obj, do_unlink=True)

with GIS.open(encoding="utf-8") as f:
    src = json.load(f)
feat = src["features"][0]
attrs = feat["attributes"]
if attrs.get("FID") != 236 or attrs.get("BLDG_ABBR") != "GRIS" or attrs.get("BUILDING_N") != "Grissom Hall":
    raise RuntimeError("GIS query returned the wrong building")
lat0 = 40.4274
ring = feat["geometry"]["rings"][0]
# Facade features follow the exact pre-existing 3D shell boundary. Recover its
# perimeter from vertical side faces, so the preserved historic entry projection
# is not lost when we compare against a newer simplified GIS feature.
mesh = SHELL.data
original_height = max(float(v.co.z) for v in mesh.vertices)
boundary_edges = []
for poly in mesh.polygons:
    low = [v for v in poly.vertices if abs(mesh.vertices[v].co.z) < 1e-4]
    high = [v for v in poly.vertices if abs(mesh.vertices[v].co.z - original_height) < 1e-4]
    if len(poly.vertices) == 4 and len(low) == 2 and len(high) == 2:
        boundary_edges.append(tuple(low))
adj = {}
for a,b in boundary_edges:
    adj.setdefault(a, []).append(b)
    adj.setdefault(b, []).append(a)
if not adj or any(len(v) != 2 for v in adj.values()):
    raise RuntimeError("Expected one closed ground-perimeter loop in shell")
start = min(adj)
coords, previous, current = [], None, start
while True:
    v = mesh.vertices[current].co
    coords.append((float(v.x), float(v.y)))
    nxt = adj[current][0] if adj[current][0] != previous else adj[current][1]
    previous, current = current, nxt
    if current == start:
        break
    if len(coords) > len(adj):
        raise RuntimeError("Could not close shell perimeter")
gis_coords = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(lat0)),
               (lat - lat0) * 111040.0) for lon, lat in ring]
sb = (min(p[0] for p in coords), max(p[0] for p in coords),
      min(p[1] for p in coords), max(p[1] for p in coords))
gb = (min(p[0] for p in gis_coords), max(p[0] for p in gis_coords),
      min(p[1] for p in gis_coords), max(p[1] for p in gis_coords))
# FID 236 is the exact manifest-linked assigned outline. Match every unique
# vertex to the original shell; the separate live OID 180 service is generalized.
def unique_points(points, tol=1e-5):
    out=[]
    for p in points:
        if not any(math.dist(p,q) < tol for q in out): out.append(p)
    return out
source_points = unique_points(gis_coords)
shell_points = unique_points(coords)
def directed_max(a,b):
    return max(min(math.dist(p,q) for q in b) for p in a)
footprint_error = max(directed_max(shell_points,source_points), directed_max(source_points,shell_points))
if len(source_points) != len(shell_points) or footprint_error > 0.02:
    raise RuntimeError(f"Assigned Purdue FID 236 footprint mismatch: {footprint_error:.4f} m")
ccw = sum(coords[i][0] * coords[(i+1) % len(coords)][1] -
          coords[(i+1) % len(coords)][0] * coords[i][1] for i in range(len(coords))) > 0

# Batch hundreds of trim/window solids into one mesh per material.
buffers = {m.name: ([], []) for m in (STONE, GLASS, FRAME, DOOR)}
def add_box(material, center, tangent, normal, width, depth, height):
    verts, faces = buffers[material.name]
    t = Vector((tangent[0], tangent[1], 0)).normalized()
    n = Vector((normal[0], normal[1], 0)).normalized()
    c = Vector(center)
    start = len(verts)
    for zs in (-0.5, 0.5):
        for ns, ts in ((-1,-1),(-1,1),(1,1),(1,-1)):
            q = c + t * ts * width/2 + n * ns * depth/2
            q.z = c.z + zs * height
            verts.append(tuple(q))
    faces.extend([(start+0,start+3,start+2,start+1), (start+4,start+5,start+6,start+7),
                  (start+0,start+1,start+5,start+4), (start+1,start+2,start+6,start+5),
                  (start+2,start+3,start+7,start+6), (start+3,start+0,start+4,start+7)])

def mesh_group(material):
    verts, faces = buffers[material.name]
    if not faces:
        return
    mesh = bpy.data.meshes.new("Grissom " + material.name)
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    obj = bpy.data.objects.new("Grissom detail | " + material.name, mesh)
    COLLECTION.objects.link(obj)

# GIS exposes Extrution=48 and R=47.2, but no unit metadata. Their likely feet
# interpretation is supported by Elevation=615.5 matching local ground elevation
# convention; retain as inferred, not verified. Roof field R gives 14.38656 m.
GIS_FEET_TO_M = 0.3048
roof_z = float(attrs["R"]) * GIS_FEET_TO_M
height = float(attrs["Extrution"]) * GIS_FEET_TO_M
if height < roof_z:
    height = roof_z
for v in mesh.vertices:
    if abs(v.co.z - original_height) < 1e-4:
        v.co.z = height
SHELL.data.update()
levels = (2.8, float(attrs["F02"]) * GIS_FEET_TO_M, float(attrs["F03"]) * GIS_FEET_TO_M + 1.4)
for i, p0 in enumerate(coords):
    p1 = coords[(i+1) % len(coords)]
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    length = math.hypot(dx, dy)
    if length < 1.2:
        continue
    t = (dx/length, dy/length)
    n = (t[1], -t[0]) if ccw else (-t[1], t[0])
    mid = ((p0[0]+p1[0])/2, (p0[1]+p1[1])/2)
    # Limestone belt courses and a broad cornice echo the photographed masonry.
    for z, bh, d in ((float(attrs["F02"])*GIS_FEET_TO_M,0.16,0.18),
                     (float(attrs["F03"])*GIS_FEET_TO_M,0.18,0.20),
                     (roof_z-0.22,0.20,0.28)):
        add_box(STONE, (mid[0]+n[0]*0.1,mid[1]+n[1]*0.1,z),t,n,length+0.08,d,bh)
    if length < 5.4:
        continue
    count = max(1, int((length-2.2)//4.2))
    spacing = (length-2.0)/count
    ww = min(1.72,spacing*0.48)
    for j in range(count):
        dist = 1.0 + spacing*(j+0.5)
        x = p0[0]+t[0]*dist+n[0]*0.09
        y = p0[1]+t[1]*dist+n[1]*0.09
        for level,z in enumerate(levels):
            wh = 2.22 if level < 2 else 1.82
            add_box(GLASS,(x,y,z),t,n,ww,0.13,wh)
            fw,ft = 0.11,0.13
            for side in (-1,1):
                add_box(FRAME,(x+t[0]*side*(ww+fw)/2,y+t[1]*side*(ww+fw)/2,z),t,n,fw,ft,wh+0.22)
                add_box(FRAME,(x,y,z+side*(wh+fw)/2),t,n,ww+2*fw,ft,fw)
            add_box(FRAME,(x,y,z),t,n,0.055,ft,wh*0.92)
            add_box(FRAME,(x,y,z+0.12),t,n,ww*0.94,ft,0.055)
for m in (STONE,GLASS,FRAME,DOOR):
    mesh_group(m)

# West-facing stone-framed entry and monumental columns are visible in Purdue's
# exterior photo. Column count, bay spacing and exact placement are estimates.
front_x = min(p[0] for p in coords) - 0.05
front_y = -125.6
def relink_asset(obj, name, material):
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COLLECTION.objects.link(obj)
    obj.data.materials.append(material)
    return obj

def cylinder(name, loc, radius, depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=loc)
    return relink_asset(bpy.context.object,name,STONE)

portico_height = 9.7
for i,off in enumerate((-4.5,-1.5,1.5,4.5),1):
    y=front_y+off
    cylinder(f"Grissom detail | portico column {i}",(front_x-0.48,y,portico_height/2),0.28,portico_height)
    for z,r,d in ((0.28,0.48,0.24),(portico_height-0.07,0.46,0.22),(portico_height+0.16,0.58,0.24)):
        cylinder(f"Grissom detail | portico profile {i}",(front_x-0.48,y,z),r,d)

def world_box(name, loc, dims, material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return relink_asset(o,name,material)

arch_z=portico_height+0.35
world_box("Grissom detail | portico architrave",(front_x-0.53,front_y,arch_z),(1.35,12.1,0.45),STONE)
# The source photo supports a broad stone entablature and monumental columns,
# but does not clearly show a triangular pediment; do not invent one.
world_box("Grissom detail | entry doors",(front_x-0.08,front_y,1.42),(0.12,2.45,2.84),DOOR)
for y in (front_y-1.31,front_y+1.31,front_y,front_y-0.62,front_y+0.62):
    world_box("Grissom detail | entry frame",(front_x-0.18,y,1.44),(0.16,0.12,2.98),STONE if y != front_y else FRAME)

# Reproducible view and plan previews; camera remains outside exported collection.
def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
old_cam=bpy.data.objects.get("Grissom preview camera")
if old_cam:
    bpy.data.objects.remove(old_cam,do_unlink=True)
center=((sb[0]+sb[1])/2,(sb[2]+sb[3])/2,height/2)
camdata=bpy.data.cameras.new("Grissom preview camera")
cam=bpy.data.objects.new("Grissom preview camera",camdata); SCENE.collection.objects.link(cam)
cam.location=(center[0]-105,center[1]-76,center[2]+75); aim(cam,center)
camdata.type="ORTHO"; camdata.ortho_scale=105; SCENE.camera=cam
SCENE.render.engine="BLENDER_WORKBENCH"
SCENE.display.shading.light="STUDIO"; SCENE.display.shading.studio_light="paint.sl"
SCENE.display.shading.color_type="MATERIAL"; SCENE.display.shading.show_shadows=True
SCENE.display.shading.show_cavity=True; SCENE.display.shading.cavity_type="BOTH"
SCENE.display.shading.curvature_ridge_factor=1.4; SCENE.display.shading.curvature_valley_factor=0.8
SCENE.render.resolution_x=1500; SCENE.render.resolution_y=1100; SCENE.render.resolution_percentage=100
SCENE.render.image_settings.file_format="PNG"
SCENE.render.filepath=str(PREVIEWS/"grissom_exterior_axonometric.png")
bpy.ops.render.render(write_still=True)
cam.location=(center[0],center[1],center[2]+145); aim(cam,center); camdata.ortho_scale=112
SCENE.render.filepath=str(PREVIEWS/"grissom_plan.png")
bpy.ops.render.render(write_still=True)
# Dedicated west elevation view makes the source-backed portico legible.
cam.location=(front_x-58,front_y-4,center[2]+11); aim(cam,(front_x,front_y,4.7))
camdata.ortho_scale=46
SCENE.render.filepath=str(PREVIEWS/"grissom_west_entry.png")
bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("Saved Grissom asset:", ASSET)
