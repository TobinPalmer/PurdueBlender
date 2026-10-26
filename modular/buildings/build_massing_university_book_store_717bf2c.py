"""Detailed, source-backed model for Purdue's University Book Store at 360 W State St."""
from __future__ import annotations

import json
import math
import os

import bpy
from mathutils import Vector


ASSET_ID = "massing_university_book_store_717bf2c"
ASSET_COLLECTION = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT = os.path.join(PROJECT_ROOT, "modular", "buildings", f"{ASSET_ID}.blend")
EVIDENCE_DIR = os.path.join(PROJECT_ROOT, "audit", "purdue_university_book_store")
OSM_FILE = os.path.join(EVIDENCE_DIR, "osm_way_117396621_full.json")

# Project-local campus plane conversion (metres), documented in modular/AGENTS.md.
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
METRES_PER_LON = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
METRES_PER_LAT = 111040.0
ANCHOR_LAT, ANCHOR_LON = 40.4242313, -86.9100869  # Nominatim address point for way 117396621
ANCHOR_X = (ANCHOR_LON - ORIGIN_LON) * METRES_PER_LON
ANCHOR_Y = (ANCHOR_LAT - ORIGIN_LAT) * METRES_PER_LAT


def local_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon - ORIGIN_LON) * METRES_PER_LON - ANCHOR_X,
            (lat - ORIGIN_LAT) * METRES_PER_LAT - ANCHOR_Y)


def material(name: str, color: tuple[float, float, float, float], roughness: float = 0.72,
             metallic: float = 0.0, brick: bool = False) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if brick:
        texcoord = nodes.new("ShaderNodeTexCoord")
        tex = nodes.new("ShaderNodeTexBrick")
        tex.offset = 0.5
        tex.offset_frequency = 2
        tex.inputs["Color1"].default_value = (0.39, 0.075, 0.046, 1)
        tex.inputs["Color2"].default_value = (0.26, 0.045, 0.032, 1)
        tex.inputs["Mortar"].default_value = (0.18, 0.13, 0.11, 1)
        tex.inputs["Scale"].default_value = 4.0
        tex.inputs["Mortar Size"].default_value = 0.035
        tex.inputs["Mortar Smooth"].default_value = 0.006
        tex.inputs["Brick Width"].default_value = 0.86
        tex.inputs["Row Height"].default_value = 0.28
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Rotation"].default_value[0] = math.pi / 2
        links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        links.new(tex.outputs["Color"], shader.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.025
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return mat


def box(name: str, center, size, mat, bevel=0.0, collection=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Soft architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    if mat:
        obj.data.materials.append(mat)
    if collection:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def mesh_object(name: str, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.validate(verbose=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def polygon_prism(name: str, polygon, z0, z1, wall_mat, roof_mat, collection, omit_wall_edges=()):
    n = len(polygon)
    verts = [(x, y, z0) for x, y in polygon] + [(x, y, z1) for x, y in polygon]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        if i not in omit_wall_edges:
            faces.append((i, j, n + j, n + i))
    roof_face_start = len(faces)
    # Concave roof tessellation without filling the courtyard/notch incorrectly.
    from mathutils.geometry import tessellate_polygon
    top = tessellate_polygon([[Vector((x, y, z1)) for x, y in polygon]])
    for tri in top:
        faces.append(tuple(n + int(i) for i in tri))
    obj = mesh_object(name, verts, faces, wall_mat, collection)
    obj.data.materials.append(roof_mat)
    for poly in obj.data.polygons:
        if poly.index >= roof_face_start:
            poly.material_index = 1
    return obj


def place_text(name, body, location, size, mat, collection, align="CENTER"):
    curve = bpy.data.curves.new(name + "_Type", "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.extrude = 0.006
    curve.bevel_depth = 0.0015
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    # Text faces south, toward State Street.
    obj.rotation_euler[0] = math.radians(90)
    curve.materials.append(mat)
    return obj


def move_obj(obj, collection):
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)


def clear_collection(collection):
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_front_storefront(collection, brick, cream, glass, frame, sign_white, dark):
    # State Street is south (local -Y); the long shop face follows the mapped south edge.
    front_y = -16.66
    wall_face = front_y + 0.035
    facade_z_top = 4.22
    fascia_top = 6.15
    # Rebuild the long south wall from separate brick piers around real shopfront openings.
    # This leaves the glazing open to the schematic retail interior rather than glazing over masonry.
    front_x0, front_x1 = -11.45, 19.35
    openings = [(-10.8, -8.75), (-8.35, -6.05), (-5.45, -2.25)]
    openings = [(max(front_x0, a), min(front_x1, b)) for a, b in openings]
    box("Storefront | continuous low brick sill wall", ((front_x0+front_x1)/2, front_y, 0.34),
        (front_x1-front_x0, 0.26, 0.68), brick, 0.01, collection)
    box("Storefront | continuous upper brick band", ((front_x0+front_x1)/2, front_y, 3.90),
        (front_x1-front_x0, 0.26, 0.76), brick, 0.01, collection)
    cursor = front_x0
    for a, b in openings:
        if a > cursor:
            box("Storefront | brick pier", ((cursor+a)/2, front_y, 2.09),
                (a-cursor, 0.26, 2.78), brick, 0.01, collection)
        cursor = max(cursor, b)
    if cursor < front_x1:
        box("Storefront | brick pier", ((cursor+front_x1)/2, front_y, 2.09),
            (front_x1-cursor, 0.26, 2.78), brick, 0.01, collection)
    # Store sign field / raised continuous cream fascia.
    box("Storefront | continuous cream parapet", (0.3, front_y + 0.02, 5.17),
        (31.7, 0.62, 1.96), cream, 0.08, collection)
    # Fine inset panel reveals and vertical pilaster caps visible in the reference.
    for x in (-14.8, -4.0, 7.8, 15.4):
        box("Fascia | narrow pilaster", (x, front_y - 0.04, 5.15),
            (0.32, 0.13, 2.05), cream, 0.035, collection)
    box("Fascia | recessed horizontal panel shadow", (0.4, front_y - 0.055, 5.82),
        (29.8, 0.04, 0.045), dark, 0.008, collection)
    box("Fascia | lower reveal", (0.4, front_y - 0.06, 4.34),
        (30.3, 0.05, 0.055), cream, 0.008, collection)

    # Sloping, pale metal awning runs above the brick retail windows.
    awning_x0, awning_x1 = -11.0, 13.25
    awning_inner_y, awning_outer_y = front_y + 0.10, front_y - 2.35
    awning_inner_z, awning_outer_z = 4.22, 3.77
    awning = mesh_object("Storefront | full-length sloped metal awning",
        [(awning_x0, awning_inner_y, awning_inner_z),
         (awning_x1, awning_inner_y, awning_inner_z),
         (awning_x1, awning_outer_y, awning_outer_z),
         (awning_x0, awning_outer_y, awning_outer_z)], [(0, 1, 2, 3)], cream, collection)
    awning_solid = awning.modifiers.new("Folded sheet thickness", "SOLIDIFY")
    awning_solid.thickness = 0.08
    # Narrow raised seams form the ribbed canopy seen from the road.
    for x in [awning_x0 + i * 0.56 for i in range(44) if awning_x0 + i * 0.56 < awning_x1]:
        seam = mesh_object("Awning | raised seam", [
            (x, awning_inner_y, awning_inner_z + 0.045),
            (x + 0.035, awning_inner_y, awning_inner_z + 0.045),
            (x + 0.035, awning_outer_y, awning_outer_z + 0.045),
            (x, awning_outer_y, awning_outer_z + 0.045)], [(0, 1, 2, 3)], cream, collection)
        seam.modifiers.new("Fine seam thickness", "SOLIDIFY").thickness = 0.018

    # Glazed retail bays, three display windows and a paired entry.
    bays = [(-10.8, -8.75), (-5.45, -2.25)]
    for bay_index, (x0, x1) in enumerate(bays):
        box(f"Shopfront | recessed glazing bay {bay_index+1}",
            ((x0 + x1) / 2, wall_face - 0.06, 2.18), (x1 - x0, 0.12, 2.56), glass, 0.015, collection)
        for x in (x0, (x0+x1)/2, x1):
            box(f"Shopfront | black metal mullion {bay_index+1}", (x, wall_face - 0.16, 2.2),
                (0.085, 0.11, 2.65), frame, 0.01, collection)
        for z in (0.9, 3.48):
            box(f"Shopfront | glazing rail {bay_index+1}", ((x0+x1)/2, wall_face - 0.16, z),
                (x1-x0, 0.11, 0.085), frame, 0.01, collection)
        # Interior display shelves and Purdue-coloured apparel blocks behind the glazing.
        box(f"Interior | display shelf {bay_index+1}", ((x0+x1)/2, front_y + 2.15, 1.12),
            (x1-x0-0.4, 0.4, 0.11), dark, 0.015, collection)
        for j in range(5):
            color = [brick, cream, sign_white, dark][(j + bay_index) % 4]
            box(f"Interior | apparel/display stack {bay_index+1}-{j+1}",
                (x0 + 0.35 + j*(x1-x0-0.7)/5, front_y + 2.24, 1.72),
                (0.38, 0.13, 0.92 if j % 2 else 0.72), color, 0.025, collection)

    # Double glass entry near the western third, in a deeper storefront reveal.
    door_x = -7.2
    box("Entry | recessed double glass door", (door_x, wall_face - 0.105, 2.09),
        (2.08, 0.12, 2.65), glass, 0.015, collection)
    for x in (door_x-1.08, door_x, door_x+1.08):
        box("Entry | dark aluminium stile", (x, wall_face - 0.20, 2.12),
            (0.11, 0.11, 2.72), frame, 0.012, collection)
    box("Entry | top rail", (door_x, wall_face - 0.20, 3.46), (2.2, 0.11, 0.11), frame, 0.012, collection)
    box("Entry | push bar", (door_x, wall_face - 0.28, 1.75), (1.72, 0.07, 0.045), cream, 0.008, collection)
    for x in (door_x - 0.82, door_x + 0.82):
        box("Entry | vertical pull handle", (x, wall_face - 0.31, 2.06), (0.035, 0.04, 0.47), cream, 0.012, collection)

    # A dark engraved sign painted directly on the central brick panel.
    sign = place_text("Sign | UNIVERSITY BOOK STORE", "UNIVERSITY\nBOOK STORE",
               (4.7, front_y - 0.30, 2.40), 0.76, sign_white, collection)
    sign.scale.x = 1.7
    place_text("Sign | west window decal", "PURDUE  •  BOOKS  •  SPIRIT",
               (-9.75, front_y - 0.12, 2.35), 0.19, sign_white, collection)
    # Short cast-concrete sill/capping below the glazed bays.
    box("Storefront | continuous granite sill", (0.0, front_y - 0.08, 0.66),
        (31.3, 0.28, 0.20), cream, 0.025, collection)


def make_glass_corner(collection, cream, glass, frame):
    # Photo-backed taller glazed corner volume at the east end of the State Street face.
    # Its plan stays within the eastern extension of the OSM building polygon.
    x0, x1 = 13.7, 19.45
    y0, y1 = -16.55, -9.55
    z0, z1 = 0.12, 13.4
    # The main glazed curtain walls (front/south and east) are kept as thin panes.
    box("Corner tower | south glazing", ((x0+x1)/2, y0-0.025, (z0+z1)/2),
        (x1-x0, 0.05, z1-z0), glass, 0.008, collection)
    box("Corner tower | east glazing", (x1+0.025, (y0+y1)/2, (z0+z1)/2),
        (0.05, y1-y0, z1-z0), glass, 0.008, collection)
    # Cream vertical piers and horizontal floor lines.
    for x in (x0, (x0+x1)/2, x1):
        box("Corner tower | vertical curtain-wall mullion", (x, y0-0.10, (z0+z1)/2),
            (0.20, 0.20, z1-z0+0.16), cream, 0.025, collection)
    for y in (y0, (y0+y1)/2, y1):
        box("Corner tower | east-side mullion", (x1+0.10, y, (z0+z1)/2),
            (0.20, 0.20, z1-z0+0.16), cream, 0.025, collection)
    for z in (4.1, 7.95, 11.75, z1):
        box("Corner tower | horizontal spandrel", ((x0+x1)/2, y0-0.12, z),
            (x1-x0+0.3, 0.23, 0.20), cream, 0.025, collection)
        box("Corner tower | east horizontal spandrel", (x1+0.12, (y0+y1)/2, z),
            (0.23, y1-y0+0.3, 0.20), cream, 0.025, collection)
    # Corner portals and large cap echo the reference's heavy pale surround.
    box("Corner tower | heavy east pier", (x1+0.12, y0+0.18, 6.75), (0.42, 0.45, 13.5), cream, 0.07, collection)
    box("Corner tower | crown beam", ((x0+x1)/2, y0-0.08, 13.56), (x1-x0+0.45, 0.50, 0.42), cream, 0.06, collection)


def make_interior(collection, brick, wood, cream, dark, frame):
    # Warm interior, visible through the street-level glazing; all geometry remains local.
    floor = box("Interior | sales floor", (0, 0, 0.14), (29.0, 35.8, 0.18), cream, 0.02, collection)
    # Rear service/book room divider, kept lower than the exterior roof so it reads through glazing.
    box("Interior | rear partition", (0.2, 13.6, 2.15), (27.8, 0.18, 4.15), cream, 0.02, collection)
    # Book shelving rows with individually coloured spines and low timber bases.
    shelf_rows = [(-6.0, -10.0), (-0.4, -2.4), (5.4, 5.2), (9.7, 11.5)]
    spine_mats = [brick, wood, cream, dark]
    for row_index, (x, y) in enumerate(shelf_rows):
        length = 10.2 if row_index < 3 else 8.5
        box(f"Interior | shelving row {row_index+1} base", (x, y, 0.76), (length, 0.72, 0.24), wood, 0.03, collection)
        for z in (1.30, 1.92, 2.54):
            box(f"Interior | shelving row {row_index+1} shelf", (x, y, z), (length, 0.66, 0.06), cream, 0.01, collection)
            count = int(length / 0.30)
            for n in range(count):
                bx = x - length/2 + 0.17 + n*0.30
                bh = 0.36 + (n % 4)*0.05
                book = box(f"Interior | book {row_index+1}-{int(z*100)}-{n+1}",
                    (bx, y-0.01, z+0.06+bh/2), (0.18, 0.34, bh),
                    spine_mats[(n + row_index) % len(spine_mats)], 0.012, collection)
    # Checkout island and two display tables.
    box("Interior | central checkout counter", (1.2, -3.1, 1.06), (5.2, 1.1, 1.6), wood, 0.06, collection)
    box("Interior | pale counter top", (1.2, -3.1, 1.9), (5.36, 1.18, 0.12), cream, 0.025, collection)
    for x in (-5.4, 6.7):
        box("Interior | low merchandise display", (x, -5.8, 0.85), (3.0, 1.1, 1.35), wood, 0.05, collection)
        box("Interior | display top", (x, -5.8, 1.56), (3.15, 1.2, 0.12), cream, 0.025, collection)


def add_camera_and_lights(scene):
    bpy.ops.object.camera_add(location=(1.0, -62.0, 9.3))
    camera = bpy.context.object
    camera.name = "Preview Camera | State Street"
    target = Vector((1.2, -2.5, 5.1))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 45
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(-16.0, -28.0, 18.0))
    key = bpy.context.object
    key.name = "Preview Light | broad daylight"
    key.data.energy = 1350
    key.data.shape = "DISK"
    key.data.size = 22
    key.rotation_euler = (Vector((0, 0, 3)) - key.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(20.0, -14.0, 12.0))
    fill = bpy.context.object
    fill.name = "Preview Light | east facade fill"
    fill.data.energy = 420
    fill.data.size = 14
    fill.rotation_euler = (Vector((4, -1, 4)) - fill.location).to_track_quat("-Z", "Y").to_euler()
    # Camera and lighting are scene-level preview helpers, not linked into the asset collection.


def main():
    if not os.path.exists(OSM_FILE):
        raise FileNotFoundError(f"Missing source snapshot: {OSM_FILE}")
    with open(OSM_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    nodes = {str(item["id"]): item for item in data["elements"] if item["type"] == "node"}
    way = next(item for item in data["elements"] if item["type"] == "way" and item["id"] == 117396621)
    polygon = [local_xy(float(nodes[str(node_id)]["lon"]), float(nodes[str(node_id)]["lat"])) for node_id in way["nodes"][:-1]]

    scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.get(ASSET_COLLECTION)
    if collection is None:
        collection = bpy.data.collections.new(ASSET_COLLECTION)
        scene.collection.children.link(collection)
    clear_collection(collection)
    for c in list(bpy.data.collections):
        if c.name not in (ASSET_COLLECTION, scene.collection.name) and not c.objects and len(c.children) == 0:
            bpy.data.collections.remove(c)

    brick = material("UBS | warm red running-bond brick", (0.38, 0.075, 0.043, 1), brick=True)
    cream = material("UBS | sand-toned painted metal and cast trim", (0.70, 0.61, 0.48, 1), roughness=0.50, metallic=0.28)
    glass = material("UBS | blue-grey storefront glass", (0.12, 0.21, 0.24, 1), roughness=0.20, metallic=0.12)
    glass.node_tree.nodes.get("Principled BSDF").inputs["Transmission Weight"].default_value = 0.05
    glass.node_tree.nodes.get("Principled BSDF").inputs["Alpha"].default_value = 0.38
    glass.surface_render_method = "DITHERED"
    frame = material("UBS | charcoal aluminium frames", (0.065, 0.078, 0.077, 1), roughness=0.36, metallic=0.50)
    white = material("UBS | warm white lettering", (0.91, 0.87, 0.76, 1), roughness=0.4)
    dark = material("UBS | recessed dark shadow and membrane", (0.055, 0.065, 0.061, 1), roughness=0.58)
    wood = material("UBS | warm maple display joinery", (0.38, 0.22, 0.10, 1), roughness=0.62)

    polygon_prism("Building shell | exact OpenStreetMap footprint", polygon, 0.0, 4.28, brick, dark, collection, omit_wall_edges=(2,))
    # The exact footprint roof remains the shell's top face; no rectangular overhang is added.
    # Side and rear apertures are restrained because source photos emphasize only the south elevation.
    for x in (-12.8, -7.6, 0.2, 5.2):
        box("West/north windows | dark glazing", (x, 18.0, 2.35), (2.1, 0.12, 1.55), glass, 0.02, collection)
        for dx in (-1.08, 1.08):
            box("West/north windows | vertical frame", (x+dx, 17.90, 2.35), (0.075,0.10,1.7),frame,0.008,collection)

    make_front_storefront(collection, brick, cream, glass, frame, white, dark)
    make_glass_corner(collection, cream, glass, frame)
    make_interior(collection, brick, wood, cream, dark, frame)
    add_camera_and_lights(scene)

    # Render a portable preview; the asset itself contains no external image dependencies.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.30, 0.38, 0.47)
    scene.world.use_nodes = True
    world_bg = scene.world.node_tree.nodes.get("Background")
    if world_bg:
        world_bg.inputs["Color"].default_value = (0.30, 0.38, 0.47, 1)
        world_bg.inputs["Strength"].default_value = 0.28
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = os.path.join(EVIDENCE_DIR, "preview_state_street.png")
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    front_camera = scene.camera
    bpy.ops.object.camera_add(location=(2.5, 2.0, 72.0))
    plan_camera = bpy.context.object
    plan_camera.name = "Preview Camera | roof and footprint"
    plan_camera.data.type = "ORTHO"
    plan_camera.data.ortho_scale = 54.0
    plan_camera.rotation_euler = (0.0, 0.0, 0.0)
    scene.camera = plan_camera
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.filepath = os.path.join(EVIDENCE_DIR, "preview_roof_plan.png")
    bpy.ops.render.render(write_still=True)
    # Return to the asset view: the master controls its campus location with Placement_<id>.
    scene.camera = front_camera
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)

    # Source-backed footprint/report metadata for the coordinator and independent grader.
    local_bounds = [[min(p[i] for p in polygon), max(p[i] for p in polygon)] for i in range(2)]
    report = {
        "building": "Purdue University Book Store, 360 W State Street, West Lafayette, Indiana",
        "stable_id": ASSET_ID,
        "asset": OUTPUT.replace("\\", "/"),
        "collection": ASSET_COLLECTION,
        "scene": SCENE_NAME,
        "build_date": "2026-10-26",
        "coordinate_frame": "Building-local metres; origin at OSM/Nominatim storefront address point, campus conversion below.",
        "campus_origin": {"latitude": ORIGIN_LAT, "longitude": ORIGIN_LON},
        "placement_anchor_campus_xy_m": [ANCHOR_X, ANCHOR_Y],
        "local_osm_footprint_bounds_m": local_bounds,
        "source_footprint": {"provider": "OpenStreetMap", "feature": "way 117396621", "version": way["version"], "source_timestamp": way["timestamp"], "nodes": way["nodes"]},
        "sources": [
            {"provider": "OpenStreetMap", "url": "https://api.openstreetmap.org/api/0.6/way/117396621/full.json", "feature_id": "way/117396621", "retrieved": "2026-10-26", "source_crs": "WGS84 latitude/longitude (EPSG:4326)", "method": "Transform each ordered way node using the project local campus XY approximation; subtract the Nominatim address-point anchor. Building footprint is exact to the mapped OSM polygon, not a survey.", "uncertainty": "OSM outline and mapping date are volunteer sourced; precise wall thickness and courtyard/structural-wall boundary are not independently surveyed."},
            {"provider": "Nominatim", "url": "https://nominatim.openstreetmap.org/search?format=jsonv2&q=University%20Book%20Store%2C%20360%20W%20State%20St%2C%20West%20Lafayette%2C%20IN", "feature_id": "way/117396621", "retrieved": "2026-10-26", "source_crs": "WGS84 latitude/longitude (EPSG:4326)", "method": "Identity/address match; returned 40.4242313,-86.9100869.", "uncertainty": "Geocoder's point is a representative address point; plan centroid is derived independently from footprint."},
            {"provider": "Purdue University Book Store", "url": "https://www.purdueu.com/about-us", "feature_id": "official store location", "retrieved": "2026-10-26", "source_crs": "not applicable", "method": "Confirms main shop at 360 W State Street and across from Purdue Memorial Union.", "uncertainty": "No public elevation or as-built dimensions found."},
            {"provider": "Loc8NearMe gallery (Google photo credit, accessed through listing)", "url": "https://www.loc8nearme.com/indiana/west-lafayette/university-book-store/2957801/gallery/#id=rvc0QR9QDp.jpg", "feature_id": "Google-credited street-level storefront photo 27/27", "retrieved": "2026-10-26", "source_crs": "not applicable", "method": "Visual inspection of south-facing State Street frontage; records brick, pale parapet/trim, long ribbed awning, display glazing, west-side paired entrance, white facade sign, and glazed taller east corner.", "uncertainty": "The image metadata gives Google photo credit but no capture date or camera position; rear elevations and rooftop equipment are not verified."},
            {"provider": "Purdue University official campus shop listing", "url": "https://www.purdue.edu/trademarks-licensing/documents/Full%20Purdue%20Retailer%20List.pdf", "feature_id": "University Book Store – Main", "retrieved": "2026-10-26", "source_crs": "not applicable", "method": "Confirms University Book Store at 360 W State St, distinct from Purdue West Follett location.", "uncertainty": "No architectural dimensions."}
        ],
        "height_evidence": {"status": "estimated", "store_height_m": 6.15, "glass_corner_height_m": 13.4, "basis": "Single-storey storefront plus visibly taller multi-level glazed corner in Google-credited facade photo; no measured elevation available."},
        "interior_evidence": {"status": "schematic, unverified", "basis": "Generic book shelving, retail counter, and display items placed behind photo-confirmed shopfront glazing; interior floor plan unavailable."},
        "materials": "All shaders are procedural Blender nodes; no external textures or absolute asset paths.",
        "validation": {"asset_reopen": "pending", "geometry_review": "pending", "independent_grade": "pending"}
    }
    with open(os.path.join(EVIDENCE_DIR, "model_evidence.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
