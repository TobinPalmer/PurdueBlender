"""Build the Circle K station library from OSM, Indiana lidar footprints, and site photos.

Coordinates follow the Purdue modular project convention (X east, Y north, Z up;
meters, origin 40.4274/-86.9137). The store shell follows OSM way 345144282.
The attached Mobil fuel canopy is a separately named appurtenance placed from
2026-10-26 orthophoto interpretation; its dimensions and height are estimates.
"""
from pathlib import Path
import bpy
import math
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_circle_k_fa39c23.blend"
PREVIEW = ROOT / "audit" / "circle_k" / "circle_k_preview_2026-10-26.png"
PREVIEW_TOP = ROOT / "audit" / "circle_k" / "circle_k_top_preview_2026-10-26.png"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LON_M = 84810.60416539927
LAT_M = 111040.0

OSM_LONLAT = [
    (-86.9138746, 40.4317488),
    (-86.9138715, 40.4318444),
    (-86.9141178, 40.4318490),
    (-86.9141209, 40.4317535),
]
FOOTPRINT = [((lon - ORIGIN_LON) * LON_M, (lat - ORIGIN_LAT) * LAT_M) for lon, lat in OSM_LONLAT]
X0, X1 = min(p[0] for p in FOOTPRINT), max(p[0] for p in FOOTPRINT)
Y0, Y1 = min(p[1] for p in FOOTPRINT), max(p[1] for p in FOOTPRINT)
XC, YC = (X0 + X1) / 2, (Y0 + Y1) / 2


def material(name, color, roughness=0.65, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


WALL = material("Circle K | warm light beige cladding", (0.68, 0.63, 0.54))
RED = material("Circle K | red fascia", (0.76, 0.025, 0.035), 0.45)
WHITE = material("Circle K | white trim", (0.91, 0.90, 0.84), 0.43)
GLASS = material("Circle K | smoked storefront glazing", (0.075, 0.16, 0.20), 0.20, 0.12)
FRAME = material("Circle K | dark storefront frames", (0.16, 0.17, 0.16), 0.48, 0.10)
ROOF = material("Circle K | charcoal shingle roof", (0.18, 0.19, 0.19), 0.88)
BLUE = material("Mobil | blue canopy edge", (0.02, 0.08, 0.68), 0.38)
PUMP = material("Fuel dispenser | light body", (0.87, 0.87, 0.82), 0.42)
BLACK = material("Fuel dispenser | screen and hose", (0.045, 0.055, 0.06), 0.34)
ASPHALT = material("Preview ground | asphalt", (0.12, 0.13, 0.13), 0.94)


def mesh_object(name, verts, faces, collection, mats):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def box(name, center, size, collection, mat):
    x, y, z = center
    sx, sy, sz = (v / 2 for v in size)
    verts = [(x + a * sx, y + b * sy, z + c * sz)
             for a, b, c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                             (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return mesh_object(name, verts, faces, collection, [mat])


def text_label(name, body, location, size, collection, mat, rotation=(math.pi/2, 0, 0)):
    curve = bpy.data.curves.new(name + "Text", "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.003
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    return obj


def make_shell(collection):
    # OSM polygon is a four-sided, slightly skewed single-store footprint.
    floor_z, eave_z, ridge_z = 0.12, 3.55, 4.75
    n = len(FOOTPRINT)
    verts = [(x, y, z) for z in (floor_z, eave_z) for x, y in FOOTPRINT]
    faces = [tuple(range(n - 1, -1, -1))]
    faces += [tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    body = mesh_object("Circle K", verts, faces, collection, [WALL])
    body["footprint_source"] = "OpenStreetMap way 345144282; coordinate-transformed to Purdue local meters"
    body["height_status"] = "estimated; 1 level is tagged in OSM, eave and ridge heights inferred from site photo"
    body["footprint_status"] = "OSM store shell polygon; excludes separate fuel canopy"

    # Low hip roof visible in the site's orthophoto and oblique store photo.
    ex = [p[0] for p in FOOTPRINT]
    ey = [p[1] for p in FOOTPRINT]
    left, right = min(ex) - 0.30, max(ex) + 0.30
    south, north = min(ey) - 0.30, max(ey) + 0.30
    ridge_left, ridge_right = left + 4.0, right - 4.0
    mid_y = (south + north) / 2
    roof_verts = [
        (left, south, eave_z), (right, south, eave_z),
        (right, north, eave_z), (left, north, eave_z),
        (ridge_left, mid_y, ridge_z), (ridge_right, mid_y, ridge_z),
    ]
    roof_faces = [(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5)]
    roof_obj = mesh_object("Circle K hipped shingle roof", roof_verts, roof_faces, collection, [ROOF])
    roof_obj["form_basis"] = "hipped low-pitch roof interpreted from Circle K site orthophoto and oblique photo"
    roof_obj["height_status"] = "estimated from photograph; no elevation drawing located"

    # South-facing retail frontage: bays and entry follow the exact-site photo.
    front_y = min(ey) - 0.09
    facade_width = right - left
    # Continuous red fascia and its white lower stripe.
    box("Circle K red storefront fascia", (XC, front_y - 0.10, 3.15), (facade_width + 0.55, 0.22, 0.72), collection, RED)
    box("Circle K white fascia pinstripe", (XC, front_y - 0.225, 2.77), (facade_width + 0.55, 0.06, 0.10), collection, WHITE)
    # Six glass bays with dark mullions; panels sit on the opaque wall as relief.
    door_x = X0 + 5.7
    bay_centers = [X0 + 1.9, X0 + 4.0, X0 + 7.9, X0 + 11.0, X0 + 14.2, X0 + 17.5]
    for i, cx in enumerate(bay_centers):
        width = 1.75 if abs(cx - door_x) > 1.1 else 1.05
        box(f"Circle K storefront glass {i+1}", (cx, front_y - 0.095, 1.62), (width, 0.10, 1.85), collection, GLASS)
        for dx in (-width / 2, width / 2):
            box(f"Circle K storefront jamb {i+1} {dx:+.2f}", (cx + dx, front_y - 0.16, 1.62), (0.07, 0.06, 1.92), collection, FRAME)
        box(f"Circle K storefront sill {i+1}", (cx, front_y - 0.16, 0.70), (width, 0.06, 0.08), collection, FRAME)
    # Entry leaf and handle at the west half of the long facade.
    box("Circle K entrance glass door", (door_x, front_y - 0.18, 1.55), (0.92, 0.09, 2.12), collection, GLASS)
    box("Circle K entrance frame left", (door_x - 0.50, front_y - 0.25, 1.55), (0.08, 0.08, 2.22), collection, FRAME)
    box("Circle K entrance frame right", (door_x + 0.50, front_y - 0.25, 1.55), (0.08, 0.08, 2.22), collection, FRAME)
    box("Circle K entrance frame head", (door_x, front_y - 0.25, 2.66), (1.08, 0.08, 0.08), collection, FRAME)
    box("Circle K door pull", (door_x + 0.33, front_y - 0.31, 1.56), (0.035, 0.04, 0.42), collection, WHITE)

    # Small square logo panel shown above the storefront in the site photograph.
    sign_x = X0 + 8.3
    box("Circle K red square logo sign", (sign_x, front_y - 0.28, 4.03), (1.28, 0.16, 1.20), collection, RED)
    text_label("Circle K logo letter", "K", (sign_x - 0.23, front_y - 0.38, 3.80), 0.70, collection, WHITE)
    text_label("Circle K storefront wordmark", "CIRCLE K", (X0 + 10.5, front_y - 0.25, 3.02), 0.38, collection, WHITE)

    # Bare beige side walls, matching the photo; no unsupported window pattern is added.
    box("Circle K west side trim", (X0 - 0.08, YC, 3.07), (0.12, 1.6, 0.16), collection, WHITE)
    box("Circle K east side trim", (X1 + 0.08, YC, 3.07), (0.12, 1.6, 0.16), collection, WHITE)
    return body


def make_fuel_canopy(collection):
    # Separate accessory to the store, positioned south from the orthophoto.
    # Size and elevation are estimates from the imagery; six pump positions are
    # consistent with the exact-site storefront photo and store review.
    cx, cy = XC + 0.3, YC - 19.2
    width, depth = 22.6, 7.6
    canopy_z, cap = 5.15, 0.72
    box("Circle K | Mobil fuel canopy roof", (cx, cy, canopy_z), (width, depth, 0.38), collection, WHITE)
    box("Mobil blue canopy fascia", (cx, cy - depth/2 + 0.04, canopy_z - 0.24), (width, 0.13, 0.55), collection, BLUE)
    box("Mobil canopy red pinstripe", (cx, cy - depth/2 - 0.035, canopy_z - 0.48), (width, 0.035, 0.07), collection, RED)
    # Four slim columns along the canopy sides.
    for i, x in enumerate((cx - width*0.39, cx + width*0.39)):
        for j, y in enumerate((cy - depth*0.35, cy + depth*0.35)):
            box(f"Mobil canopy column {i+1}-{j+1}", (x, y, canopy_z/2), (0.26, 0.28, canopy_z), collection, WHITE)
    # Three double-sided islands, six pumps total.
    for i, x in enumerate((cx - 6.2, cx, cx + 6.2)):
        for j, y in enumerate((cy - 1.55, cy + 1.55)):
            box(f"Mobil fuel dispenser {i+1}-{j+1}", (x, y, 1.22), (0.76, 0.64, 1.72), collection, PUMP)
            box(f"Mobil dispenser screen {i+1}-{j+1}", (x, y - 0.333, 1.62), (0.49, 0.04, 0.37), collection, BLACK)
            box(f"Mobil pump hose {i+1}-{j+1}", (x + 0.48, y - 0.10, 1.10), (0.10, 0.11, 0.84), collection, BLACK)
        box(f"Mobil pump island {i+1}", (x, cy, 0.20), (1.45, 1.42, 0.40), collection, WHITE)
    # Mobil wordmark on the visible south fascia, with red 'o'.
    label_y = cy - depth/2 - 0.12
    text_label("Mobil fascia M", "M", (cx - 1.65, label_y, canopy_z - 0.42), 0.43, collection, WHITE)
    text_label("Mobil fascia o", "o", (cx - 1.30, label_y, canopy_z - 0.42), 0.43, collection, RED)
    text_label("Mobil fascia bil", "bil", (cx - 1.02, label_y, canopy_z - 0.42), 0.43, collection, WHITE)
    obj = bpy.data.objects.get("Circle K | Mobil fuel canopy roof")
    obj["location_basis"] = "separate canopy visible south of store in dated orthophoto mosaic"
    obj["dimensions_status"] = "estimated from orthophoto; not part of OSM building footprint"
    obj["height_status"] = "estimated; no surveyed elevation available"


def make_preview(scene):
    # Temporary preview rig, removed before saving the library.
    preview = bpy.data.collections.new("__PreviewOnly")
    scene.collection.children.link(preview)
    plane = box("__Preview asphalt", (XC, YC - 10.5, -0.20), (58, 62, 0.25), preview, ASPHALT)
    bpy.context.view_layer.objects.active = plane
    plane.select_set(True)
    bpy.ops.object.shade_smooth()
    plane.select_set(False)
    cam_data = bpy.data.cameras.new("__PreviewCameraData")
    cam = bpy.data.objects.new("__PreviewCamera", cam_data)
    preview.objects.link(cam)
    cam.location = (XC - 34, YC - 48, 23)
    target = Vector((XC, YC - 9, 1.8))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 52
    scene.camera = cam
    for name, loc, energy, size in [
        ("__PreviewKey", (XC-16, YC-25, 31), 7800, 24),
        ("__PreviewFill", (XC+20, YC-5, 22), 5200, 20),
    ]:
        ld = bpy.data.lights.new(name, "AREA")
        lo = bpy.data.objects.new(name, ld)
        preview.objects.link(lo)
        lo.location = loc
        ld.energy = energy
        ld.shape = "DISK"
        ld.size = size
        lo.rotation_euler = (Vector((XC, YC-10, 1.5)) - lo.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.34, 0.34, 0.34, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.view_settings.exposure = 1.1
    scene.render.filepath = str(PREVIEW)
    bpy.ops.render.render(write_still=True)
    # A separate top view makes the OSM shell and accessory placement inspectable.
    top_data = bpy.data.cameras.new("__PreviewTopCameraData")
    top_cam = bpy.data.objects.new("__PreviewTopCamera", top_data)
    preview.objects.link(top_cam)
    top_cam.location = (XC, YC - 8, 55)
    top_cam.rotation_euler = (0, 0, 0)
    top_cam.data.type = "ORTHO"
    top_cam.data.ortho_scale = 56
    scene.camera = top_cam
    scene.render.filepath = str(PREVIEW_TOP)
    bpy.ops.render.render(write_still=True)
    # Keep the asset library clean of the preview plane/camera/lights.
    scene.camera = None
    for obj in list(preview.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(preview)


def main():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        if col.name == "Asset_massing_circle_k_fa39c23":
            bpy.data.collections.remove(col)
    scene = bpy.data.scenes.get("Building_massing_circle_k_fa39c23") or bpy.context.scene
    scene.name = "Building_massing_circle_k_fa39c23"
    asset = bpy.data.collections.new("Asset_massing_circle_k_fa39c23")
    scene.collection.children.link(asset)
    make_shell(asset)
    make_fuel_canopy(asset)
    make_preview(scene)
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET), compress=True)
    print("CIRCLE_K_BUILD_OK", ASSET)
    print("STORE_FOOTPRINT_M", X1-X0, Y1-Y0, "WORLD_CENTER_M", XC, YC)
    print("OBJECT_COUNT", len(asset.objects))


if __name__ == "__main__":
    main()
