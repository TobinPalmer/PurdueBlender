import bpy
import math
from pathlib import Path

PROJECT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = PROJECT / "modular/buildings/hovde_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
root = bpy.data.objects["HOVD_Root"]
collection = bpy.data.collections["Asset_hovde_hall"]

# Remove the prior round-10 detail pass, if this reproducible edit is rerun.
for obj in list(bpy.data.objects):
    if obj.name.startswith("HOVD_R10_"):
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            if data.__class__.__name__ == "Mesh":
                bpy.data.meshes.remove(data)
            elif data.__class__.__name__ == "Curve":
                bpy.data.curves.remove(data)

limestone = bpy.data.materials["Bedford_Indiana_Limestone"]
trim = bpy.data.materials["Hovde_Limestone_Trim"]
bronze = bpy.data.materials["Hovde_Bronze_Metal"]

def mesh_object(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.location = (0, 0, 0)
    return obj

def add_box(verts, faces, center, dims):
    x, y, z = center
    dx, dy, dz = (d / 2 for d in dims)
    base = len(verts)
    verts.extend([
        (x-dx,y-dy,z-dz), (x+dx,y-dy,z-dz), (x+dx,y+dy,z-dz), (x-dx,y+dy,z-dz),
        (x-dx,y-dy,z+dz), (x+dx,y-dy,z+dz), (x+dx,y+dy,z+dz), (x-dx,y+dy,z+dz),
    ])
    faces.extend([
        (base,base+3,base+2,base+1), (base+4,base+5,base+6,base+7),
        (base,base+1,base+5,base+4), (base+1,base+2,base+6,base+5),
        (base+2,base+3,base+7,base+6), (base+3,base,base+4,base+7),
    ])

def uv_sphere(name, center, radii, material):
    verts, faces = [], []
    rings, segments = 8, 12
    for j in range(rings + 1):
        phi = math.pi * j / rings
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            verts.append((
                center[0] + radii[0] * math.sin(phi) * math.cos(theta),
                center[1] + radii[1] * math.sin(phi) * math.sin(theta),
                center[2] + radii[2] * math.cos(phi),
            ))
    for j in range(rings):
        for i in range(segments):
            a = j * segments + i
            b = j * segments + (i + 1) % segments
            c = (j + 1) * segments + (i + 1) % segments
            d = (j + 1) * segments + i
            faces.append((a, b, c, d))
    return mesh_object(name, verts, faces, material)

def frustum(name, center, radius_bottom, radius_top, height, material):
    verts, faces = [], []
    segments = 24
    for z, radius in ((-height / 2, radius_bottom), (height / 2, radius_top)):
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((center[0] + radius * math.cos(a), center[1] + radius * math.sin(a), center[2] + z))
    faces.append(tuple(reversed(range(segments))))
    faces.append(tuple(range(segments, 2 * segments)))
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
    return mesh_object(name, verts, faces, material)

def torus_yz(name, center, major, minor, material):
    verts, faces = [], []
    major_segments, minor_segments = 20, 8
    for i in range(major_segments):
        u = 2 * math.pi * i / major_segments
        for j in range(minor_segments):
            v = 2 * math.pi * j / minor_segments
            rr = major + minor * math.cos(v)
            verts.append((center[0] + minor * math.sin(v),
                          center[1] + rr * math.cos(u),
                          center[2] + rr * math.sin(u)))
    for i in range(major_segments):
        ni = (i + 1) % major_segments
        for j in range(minor_segments):
            nj = (j + 1) % minor_segments
            faces.append((i*minor_segments+j, ni*minor_segments+j,
                          ni*minor_segments+nj, i*minor_segments+nj))
    return mesh_object(name, verts, faces, material)

def curve_line(name, points, radius, material):
    data = bpy.data.curves.new(name + "Curve", type="CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (co[0], co[1], co[2], 1)
    data.materials.append(material)
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.parent = root
    return obj

# Slim the supports toward the slender proportions visible in the photo.
# Keep the six positions, height, and local frame from round 9.
def fit_xy(obj, target):
    dx = max(v.co.x for v in obj.data.vertices) - min(v.co.x for v in obj.data.vertices)
    dy = max(v.co.y for v in obj.data.vertices) - min(v.co.y for v in obj.data.vertices)
    obj.scale.x = target / dx
    obj.scale.y = target / dy

for i in range(1, 7):
    shaft = bpy.data.objects[f"HOVD_Classical_Column_{i}"]
    fit_xy(shaft, 0.79)
    base = bpy.data.objects[f"HOVD_Column_Base_{i}"]
    fit_xy(base, 1.24)
    capital = bpy.data.objects[f"HOVD_Column_Capital_{i}"]
    fit_xy(capital, 1.2)
    capital.scale.z = 0.55
    capital.location.z = 10.42
    for prefix in ("HOVD_Column_FluteCollar_Base_", "HOVD_Column_FluteCollar_Capital_"):
        fit_xy(bpy.data.objects[prefix + str(i)], 0.97)

    x, y = shaft.location.x, shaft.location.y
    # A flared echinus and abacus make the photo-supported scroll capital legible.
    frustum(f"HOVD_R10_Capital_Echinus_{i}", (x, y, 10.39), 0.41, 0.59, 0.28, limestone)
    av, af = [], []
    add_box(av, af, (x, y, 10.54), (1.22, 1.22, 0.15))
    mesh_object(f"HOVD_R10_Capital_Abacus_{i}", av, af, trim)
    for side in (-1, 1):
        # Paired circular volutes and leaf bosses on the visible facade face.
        torus_yz(f"HOVD_R10_Capital_Volute_{i}_{side}", (x + 0.57, y + side * 0.30, 10.41), 0.15, 0.038, trim)
        uv_sphere(f"HOVD_R10_Capital_Leaf_{i}_{side}", (x + 0.56, y + side * 0.30, 10.22), (0.075, 0.10, 0.16), limestone)

# Photo-scale entablature: a taller frieze, clear cornice shelf, and pediment
# rising close to the roofline. Dimensions remain approximate image estimates.
entablature = bpy.data.objects["HOVD_Portico_Entablature"]
entablature.scale.z = 0.49
entablature.location.z = 11.08
cornice = bpy.data.objects["HOVD_Portico_Cornice"]
cornice.scale.z = 0.85
cornice.location.z = 11.62
pediment = bpy.data.objects["HOVD_Portico_Pediment_Base"]
pediment.scale.z = 1.5625
pediment.location.z = 14.30   # approx base 11.8 m, apex 16.8 m
crown = bpy.data.objects["HOVD_Portico_Pediment_Crown"]
crown.scale.z = 0.40
crown.location.z = 11.72
plaque = bpy.data.objects.get("HOVD_Sign_Plaque")
lettering = bpy.data.objects.get("HOVD_Gold_Letters")
for obj in (plaque, lettering):
    if obj:
        obj.location.z = 11.08

# Raking limestone moldings and a small apex acroterion follow the photograph.
front_x = 14.22
left_y, center_y, right_y = -9.2, -0.255, 8.7
base_z, apex_z = 11.80, 16.80
curve_line("HOVD_R10_Pediment_Raking_Cornice",
           [(front_x, left_y, base_z), (front_x, center_y, apex_z), (front_x, right_y, base_z)], 0.105, trim)
curve_line("HOVD_R10_Pediment_Base_Molding",
           [(front_x, left_y, base_z), (front_x, right_y, base_z)], 0.09, trim)
uv_sphere("HOVD_R10_Acroterion_Center", (front_x, center_y, 16.93), (0.14, 0.24, 0.40), trim)
uv_sphere("HOVD_R10_Acroterion_Left", (front_x, center_y - 0.19, 16.84), (0.12, 0.18, 0.26), limestone)
uv_sphere("HOVD_R10_Acroterion_Right", (front_x, center_y + 0.19, 16.84), (0.12, 0.18, 0.26), limestone)

# Fine dentils below the projecting cornice, evenly spaced across the frieze.
dv, df = [], []
for i in range(37):
    y = -8.65 + i * (17.0 / 36)
    add_box(dv, df, (14.25, y, 11.49), (0.22, 0.25, 0.14))
mesh_object("HOVD_R10_Entablature_Dentils", dv, df, trim)

# Recessed stone window surrounds and slim muntins add real facade depth.
wv, wf, mv, mf = [], [], [], []
for side in (1, -1):
    x = side * 10.88
    for y in range(-30, 31, 5):
        for z in (2.6, 6.4, 10.5, 14.6):
            # Two jambs and a restrained lintel sit outside the recessed glazing.
            for yy in (y - 1.045, y + 1.045):
                add_box(wv, wf, (x, yy, z), (0.15, 0.12, 2.18))
            add_box(wv, wf, (x, y, z + 1.105), (0.15, 2.18, 0.13))
            # Fine, cool stone/metal crossbars divide the reflected glazing.
            add_box(mv, mf, (side * 10.91, y, z), (0.035, 0.035, 2.04))
            add_box(mv, mf, (side * 10.91, y, z), (0.035, 1.88, 0.035))
mesh_object("HOVD_R10_Window_Stone_Reveals", wv, wf, trim)
mesh_object("HOVD_R10_Window_Muntins", mv, mf, bronze)

# Give the clay-tile roof a mapped, shallow-relief tile pattern and richer
# terracotta color; the existing six-vertex hipped roof silhouette is retained.
roof_mat = bpy.data.materials["Hovde_Roof_Membrane"]
roof_mat.diffuse_color = (0.42, 0.12, 0.035, 1)
roof_mat.use_nodes = True
nt = roof_mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
out.location = (800, 100)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (560, 100)
bsdf.inputs["Roughness"].default_value = 0.62
bsdf.inputs["Base Color"].default_value = (0.42, 0.12, 0.035, 1)
coords = nt.nodes.new("ShaderNodeTexCoord")
coords.location = (-800, 120)
mapping = nt.nodes.new("ShaderNodeVectorMath")
mapping.operation = "MULTIPLY"
mapping.location = (-580, 120)
mapping.inputs[1].default_value = (42.0, 56.0, 1.0)
nt.links.new(coords.outputs["Generated"], mapping.inputs[0])
tiles = nt.nodes.new("ShaderNodeTexBrick")
tiles.location = (-340, 180)
tiles.inputs["Color1"].default_value = (0.48, 0.155, 0.045, 1)
tiles.inputs["Color2"].default_value = (0.39, 0.105, 0.028, 1)
tiles.inputs["Mortar"].default_value = (0.20, 0.065, 0.025, 1)
tiles.inputs["Scale"].default_value = 1.0
tiles.inputs["Brick Width"].default_value = 0.50
tiles.inputs["Row Height"].default_value = 0.28
tiles.inputs["Mortar Size"].default_value = 0.018
tiles.inputs["Mortar Smooth"].default_value = 0.006
nt.links.new(mapping.outputs["Vector"], tiles.inputs["Vector"])
bump = nt.nodes.new("ShaderNodeBump")
bump.location = (300, -60)
bump.inputs["Strength"].default_value = 0.14
bump.inputs["Distance"].default_value = 0.0012
nt.links.new(tiles.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
nt.links.new(tiles.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# A low tile edge sits just over the stone eaves, visible in the near-frontal
# photo while staying within the low-pitched roof silhouette.
ev, ef = [], []
add_box(ev, ef, (10.72, 0.0, 16.82), (0.18, 70.2, 0.18))
add_box(ev, ef, (-10.72, 0.0, 16.82), (0.18, 70.2, 0.18))
mesh_object("HOVD_R10_Roof_Eave_Tile_Lips", ev, ef, roof_mat)

# Subtle variation in the brick surface, preserving the established course scale.
brick = bpy.data.materials["Purdue_Red_Brick"]
if brick.use_nodes:
    for node in brick.node_tree.nodes:
        if node.type == "TEX_BRICK":
            node.inputs["Color1"].default_value = (0.31, 0.078, 0.039, 1)
            node.inputs["Color2"].default_value = (0.275, 0.063, 0.032, 1)
            node.inputs["Mortar"].default_value = (0.15, 0.105, 0.078, 1)
        elif node.type == "BUMP":
            node.inputs["Strength"].default_value = 0.09
            node.inputs["Distance"].default_value = 0.00035

# Existing low-pitch hip geometry remains source-photo-consistent. Keep its
# approximate 0.9 m ridge rise and document that this is image interpretation.
# The previous standalone roof penthouse protruded as a bare red box in the
# geotagged frontal photo. Remove that unsupported mass and keep a continuous
# low-pitch tile silhouette; no roof plan was found to justify a rooftop box.
for name in ("HOVD_Penthouse_Louvers", "HOVD_Penthouse"):
    obj = bpy.data.objects.get(name)
    if obj:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)
bpy.context.view_layer.update()
assert len([bpy.data.objects.get(f"HOVD_Classical_Column_{i}") for i in range(1, 7)]) == 6
assert all(bpy.data.objects.get(f"HOVD_R10_Capital_Abacus_{i}") for i in range(1, 7))
assert tuple(round(v, 3) for v in root.location) == (-62.85, 93.0, 0.0)
assert round(root.rotation_euler.z, 6) == 0.689754
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("ROUND10_SAVED", ASSET)
print("Six slimmer supports with photo-inspired scroll capitals; layered entablature, taller pediment, eaves, window reveals, and terracotta roof tiles added.")
