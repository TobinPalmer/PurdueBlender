import bpy, json, math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
import bmesh

ROOT = r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET = ROOT + r"\modular\buildings\life_science_plant_and_soils_laboratory.blend"
GIS = ROOT + r"\audit\batchC_life_science_plant_soils_official_footprint.json"
EVIDENCE = ROOT + r"\audit\batchC_life_science_plant_soils_evidence.json"
bpy.ops.wm.open_mainfile(filepath=ASSET)

with open(GIS, encoding="utf-8") as f:
    snapshot = json.load(f)
features = snapshot.get("features", [])
feature = next(f for f in features if f.get("attributes", {}).get("FID") == 917)
ring = feature["geometry"]["rings"][0][:-1]
evidence = json.load(open(EVIDENCE, encoding="utf-8"))
origin_x, origin_y = evidence["coordinate_method"]["build_bbox_origin_xy_m"]
poly_xy = []
for lon, lat in ring:
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)) - origin_x
    y = (lat - 40.4274) * 111040.0 - origin_y
    poly_xy.append((x, y))
bbox = [(min(p[0] for p in poly_xy), min(p[1] for p in poly_xy)),
        (max(p[0] for p in poly_xy), max(p[1] for p in poly_xy))]
assert abs(bbox[0][0] + 30.998) < 0.01 and abs(bbox[1][0] - 30.998) < 0.01
assert abs(bbox[0][1] + 17.804) < 0.01 and abs(bbox[1][1] - 17.804) < 0.01

def exact_gis_prism(obj):
    points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    z0 = min(p.z for p in points)
    z1 = max(p.z for p in points)
    poly = [Vector((x, y, 0.0)) for x, y in poly_xy]
    lut = {(round(x, 6), round(y, 6)): i for i, (x, y) in enumerate(poly_xy)}
    tris = tessellate_polygon([poly])
    tri_ids = [tuple(int(v) for v in tri) if isinstance(tri[0], int) else
        tuple(lut[(round(v.x, 6), round(v.y, 6))] for v in tri) for tri in tris]
    n = len(poly_xy)
    verts = [(x, y, z0) for x, y in poly_xy] + [(x, y, z1) for x, y in poly_xy]
    faces = []
    for tri in tri_ids:
        faces.append(tuple(reversed(tri)))
        faces.append(tuple(i + n for i in tri))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    mesh = bpy.data.meshes.new(obj.name + " | clipped to official GIS ring")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh); bm.free()
    old = obj.data
    slots = list(obj.data.materials)
    obj.data = mesh
    for mat in slots: mesh.materials.append(mat)
    obj.location = (0, 0, 0); obj.rotation_euler = (0, 0, 0); obj.scale = (1, 1, 1)
    if old.users == 0: bpy.data.meshes.remove(old)
    obj["footprint_source"] = "Purdue BuildingShapesZip4 FeatureServer layer 0, FID 917, retrieved 2026-10-24"
    obj["footprint_method"] = "Triangulated and extruded exact 12-vertex GIS ring in the asset local coordinate transform"
    obj["placement_status"] = "GIS plan geometry; projection remains a local approximation, not surveyed control"

for name in [
    "Life Science Plant and Soils Laboratory | official GIS footprint ground floor",
    "LSPS | level 1 interior floor plate",
    "LSPS | level 2 interior floor plate",
    "LSPS | level 3 interior floor plate",
]:
    obj = bpy.data.objects.get(name)
    if obj:
        exact_gis_prism(obj)

interior = bpy.data.collections.get("LSPS_Interior")
assert interior is not None
for obj in list(interior.objects):
    if obj.name.startswith("LSPS R2 | "):
        bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, roughness=0.55, metallic=0.0, emission=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if emission is not None:
        shader.inputs["Emission Color"].default_value = (*emission, 1)
        shader.inputs["Emission Strength"].default_value = 1.2
    return mat

steel = material("LSPS | R2 enamelled laboratory appliance", (0.64, 0.68, 0.67), 0.36, 0.16)
dark = material("LSPS | R2 appliance shadow and vents", (0.065, 0.082, 0.078), 0.68)
display = material("LSPS | R2 small instrument display", (0.04, 0.20, 0.22), 0.25, 0.12, (0.04, 0.26, 0.30))
stainless = material("LSPS | R2 stainless sample grinder", (0.50, 0.56, 0.57), 0.28, 0.62)

def append_box(verts, faces, mids, center, size, mat_index):
    cx, cy, cz = center; sx, sy, sz = [v * 0.5 for v in size]
    base = len(verts)
    verts.extend([(cx+sx,cy+sy,cz+sz),(cx+sx,cy+sy,cz-sz),(cx+sx,cy-sy,cz+sz),(cx+sx,cy-sy,cz-sz),
                  (cx-sx,cy+sy,cz+sz),(cx-sx,cy+sy,cz-sz),(cx-sx,cy-sy,cz+sz),(cx-sx,cy-sy,cz-sz)])
    boxfaces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    for f in boxfaces:
        faces.append(tuple(base+i for i in f)); mids.append(mat_index)

def appliance(name, components, mats):
    verts, faces, ids = [], [], []
    for center, size, mat_index in components: append_box(verts, faces, ids, center, size, mat_index)
    mesh = bpy.data.meshes.new(name + " mesh"); mesh.from_pydata(verts, [], faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(mesh); bm.free()
    for mat in mats: mesh.materials.append(mat)
    for poly, idx in zip(mesh.polygons, ids): poly.material_index = idx
    ob = bpy.data.objects.new(name, mesh); interior.objects.link(ob)
    ob["evidence_status"] = "schematic illustrative placement; overall equipment count based on Purdue Agronomy facility report"
    return ob

# The 2021 Purdue Agronomy report describes fifteen large sample dryers and four grinding units.
# Their documented quantities are modeled as equipment groups; no room position is asserted as surveyed.
for row in range(3):
    for col in range(5):
        x = 12.0 + (col - 2) * 1.02
        y = 2.7 + (row - 1) * 1.02
        zc = 0.99
        components = [
            ((x,y,zc), (0.70,0.76,1.78), 0),                         # cabinet
            ((x,y-0.392,zc+0.08), (0.52,0.018,1.12), 1),             # dark glazed door
            ((x-0.205,y-0.408,zc+0.64), (0.11,0.015,0.07), 2),       # status display
            ((x,y-0.415,zc-0.37), (0.40,0.016,0.30), 1),             # intake grille
            ((x+0.20,y-0.418,zc+0.08), (0.018,0.03,0.21), 0),        # pull handle
            ((x,y,zc+0.91), (0.52,0.56,0.035), 0),                   # top lip
        ]
        appliance(f"LSPS R2 | sample dryer {row*5+col+1:02d}", components, [steel,dark,display])

for i in range(4):
    x = -18.0 + (i % 2) * 2.4
    y = -0.5 + (i // 2) * 2.4
    zc = 0.83
    components = [
        ((x,y,zc), (0.78,0.70,1.35), 0),
        ((x,y,zc+0.83), (0.48,0.50,0.32), 0),
        ((x,y-0.39,zc+0.08), (0.30,0.025,0.62), 1),
        ((x,y,zc+1.25), (0.36,0.36,0.48), 3),
        ((x,y,zc+1.55), (0.22,0.22,0.20), 3),
        ((x,y-0.01,zc+1.80), (0.58,0.56,0.09), 0),
        ((x,y,zc+1.92), (0.10,0.10,0.18), 1),
    ]
    appliance(f"LSPS R2 | soil grinding unit and dust arrester {i+1}", components, [steel,dark,display,stainless])

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("Saved R2 structural footprint and schematic lab equipment", len(interior.objects))
