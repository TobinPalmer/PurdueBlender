import bpy
import math
from pathlib import Path

PROJECT = Path(r"C:/Users/Tobin/Documents/Blender/PurdueMap")
ASSET = PROJECT / "modular/buildings/hovde_hall.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
root = bpy.data.objects["HOVD_Root"]
collection = bpy.data.collections["Asset_hovde_hall"]
trim = bpy.data.materials["Hovde_Limestone_Trim"]
limestone = bpy.data.materials["Bedford_Indiana_Limestone"]

# Replace round-10 bead-like volutes and soft leaf bosses with restrained,
# pointed acanthus foliage that reads clearly at column scale.
for obj in list(bpy.data.objects):
    if obj.name.startswith(("HOVD_R10_Capital_Volute_", "HOVD_R10_Capital_Leaf_", "HOVD_R11_")):
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            if data.__class__.__name__ == "Mesh":
                bpy.data.meshes.remove(data)
            elif data.__class__.__name__ == "Curve":
                bpy.data.curves.remove(data)

def mesh_object(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.location = (0, 0, 0)
    return obj

def add_box(verts, faces, center, dims):
    x, y, z = center
    dx, dy, dz = (d / 2 for d in dims)
    b = len(verts)
    verts.extend([
        (x-dx,y-dy,z-dz), (x+dx,y-dy,z-dz), (x+dx,y+dy,z-dz), (x-dx,y+dy,z-dz),
        (x-dx,y-dy,z+dz), (x+dx,y-dy,z+dz), (x+dx,y+dy,z+dz), (x-dx,y+dy,z+dz),
    ])
    faces.extend([
        (b,b+3,b+2,b+1), (b+4,b+5,b+6,b+7),
        (b,b+1,b+5,b+4), (b+1,b+2,b+6,b+5),
        (b+2,b+3,b+7,b+6), (b+3,b,b+4,b+7),
    ])

def add_leaf(verts, faces, x_face, y_center, z_center, width, height):
    # A narrow lanceolate leaf with a raised midrib and gently curved edges.
    levels = (0.02, 0.22, 0.46, 0.70, 0.90, 1.0)
    widths = (0.15, 0.62, 1.0, 0.78, 0.40, 0.025)
    rows, cols = len(levels), 3
    start = len(verts)
    front, back = [], []
    for t, wf in zip(levels, widths):
        centerline = 0.025 * math.sin(math.pi * t)
        z = z_center + (t - 0.5) * height
        half = width * wf * 0.5
        for k in (-1, 0, 1):
            y = y_center + centerline + k * half
            ridge = (0.045 if k == 0 else 0.0) + 0.012 * math.sin(math.pi * t)
            front.append((x_face + ridge, y, z))
            back.append((x_face - 0.035, y, z))
    verts.extend(front)
    front_start = start
    verts.extend(back)
    back_start = start + rows * cols
    # Front and back leaf blades.
    for j in range(rows - 1):
        for k in range(cols - 1):
            a = front_start + j*cols+k
            faces.append((a, a+1, a+cols+1, a+cols))
            a = back_start + j*cols+k
            faces.append((a, a+cols, a+cols+1, a+1))
    # Thin edge surfaces close the leaf outline and preserve a readable silhouette.
    for j in range(rows - 1):
        for k in (0, cols - 1):
            f0 = front_start + j*cols+k
            f1 = front_start + (j+1)*cols+k
            b0 = back_start + j*cols+k
            b1 = back_start + (j+1)*cols+k
            faces.append((f0, b0, b1, f1))
    for k in range(cols - 1):
        for j in (0, rows - 1):
            f0 = front_start + j*cols+k
            f1 = front_start + j*cols+k+1
            b0 = back_start + j*cols+k
            b1 = back_start + j*cols+k+1
            faces.append((f0, f1, b1, b0))

# Portico projection: move the colonnade about 1.15 m forward from the doors.
# This creates a deeper sheltered threshold so the three doors read behind the
# columns, as in the photographed entrance. The shell/window positions stay put.
depth_shift = 1.15
portico_names = (
    "HOVD_Classical_Column_", "HOVD_Column_Base_", "HOVD_Column_Capital_",
    "HOVD_Column_FluteCollar_Base_", "HOVD_Column_FluteCollar_Capital_",
)
for obj in collection.all_objects:
    is_portico = obj.name.startswith(portico_names) or obj.name.startswith("HOVD_Portico_")
    is_portico = is_portico or obj.name in {"HOVD_Sign_Plaque", "HOVD_Gold_Letters"}
    is_portico = is_portico or obj.name.startswith((
        "HOVD_R10_Capital_Echinus_", "HOVD_R10_Capital_Abacus_",
        "HOVD_R10_Pediment_", "HOVD_R10_Entablature_Dentils", "HOVD_R10_Acroterion_",
    ))
    if is_portico:
        obj.location.x += depth_shift

# Six small paired leaf rows per capital, formed as one mesh per shaft.
for i in range(1, 7):
    shaft = bpy.data.objects[f"HOVD_Classical_Column_{i}"]
    x, y = shaft.location.x, shaft.location.y
    verts, faces = [], []
    front = x + 0.62
    # Lower row and upper row are staggered, each with a center and two leaves.
    for zc, spread, w, h in ((10.25, 0.29, 0.20, 0.22), (10.43, 0.31, 0.17, 0.20)):
        for dy in (-spread, 0.0, spread):
            add_leaf(verts, faces, front, y + dy, zc, w, h)
    mesh_object(f"HOVD_R11_Corinthian_Acanthus_Leaves_{i}", verts, faces, trim)

# Add a simple pale soffit behind the front beam, plus shallow cross ribs. This
# exposes the new 4 m portico depth from the close oblique evidence view without
# inventing an interior wall or changing the documented door positions.
soffit_v, soffit_f = [], []
add_box(soffit_v, soffit_f, (12.86, -0.255, 11.67), (3.88, 17.20, 0.12))
mesh_object("HOVD_R11_Portico_Soffit", soffit_v, soffit_f, trim)
ribs_v, ribs_f = [], []
for x in (11.35, 12.30, 13.25, 14.12):
    add_box(ribs_v, ribs_f, (x, -0.255, 11.73), (0.08, 16.75, 0.10))
mesh_object("HOVD_R11_Portico_Soffit_Ribs", ribs_v, ribs_f, limestone)

# Roof-specific evidence in the 2016 photo supports red clay tile and a low
# eave; round 10 already models those cues. No unsupported roof changes here.
bpy.context.view_layer.update()
assert len([bpy.data.objects.get(f"HOVD_Classical_Column_{i}") for i in range(1, 7)]) == 6
assert all(bpy.data.objects.get(f"HOVD_R11_Corinthian_Acanthus_Leaves_{i}") for i in range(1, 7))
assert tuple(round(v, 3) for v in root.location) == (-62.85, 93.0, 0.0)
assert round(root.rotation_euler.z, 6) == 0.689754
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print("ROUND11_SAVED", ASSET)
print("Six 1.15 m forward portico shift; six restrained Corinthian leaf capitals; deeper limestone soffit with shallow ribs; roof retained from round 10.")
