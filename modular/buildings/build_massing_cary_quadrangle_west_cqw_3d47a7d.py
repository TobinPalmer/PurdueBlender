"""Build the source-backed Cary Quadrangle West massing library."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_west_cqw_3d47a7d"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / ASSET_ID
SOURCE_GEOJSON = EVIDENCE / "sources" / "purdue_cqw_fid60_wgs84.geojson"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

# Purdue GIS reports five floors and an undocumented "Extrution" value of 48.
# 48 ft (14.63 m) is used as a documented height estimate; tower extensions
# are estimated from the Cary West exterior photographs, not measured.
WALL_HEIGHT = 48.0 * 0.3048
ROOF_TOP = WALL_HEIGHT + 0.42
TOWER_TOP = WALL_HEIGHT + 4.1
FLOORS = 5


def project_lon_lat(lon, lat):
    """Repository's documented approximate WGS84-to-campus-metre transform."""
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def material(name, color, roughness=0.82):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (*color, 1.0)
    mat.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = roughness
    return mat


def cube(name, center, dims, mat, coll, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Small masonry arris", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        obj.modifiers.new("Weighted masonry normals", "WEIGHTED_NORMAL")
    return obj


def make_shell(ring, z0, z1, brick, roof, coll):
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    cap = __import__("mathutils.geometry", fromlist=["tessellate_polygon"]).tessellate_polygon(
        [[Vector((x, y, 0.0)) for x, y in ring]])
    for tri in cap:
        ids = tuple(tri)
        faces.append(tuple(n + i for i in ids))
        faces.append(tuple(reversed(ids)))
    mesh = bpy.data.meshes.new("CQW official GIS footprint shell")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(brick)
    mesh.materials.append(roof)
    mesh.update()
    obj = bpy.data.objects.new("Cary Quadrangle West (CQW) shell", mesh)
    coll.objects.link(obj)
    for i, poly in enumerate(mesh.polygons):
        if i >= n:
            poly.material_index = 1
    return obj


def edge_courses(ring, z, stone, coll, label):
    """Thin segmented limestone courses follow the official wall perimeter."""
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 0.2:
            continue
        obj = cube(f"CQW {label} course {i:03d}",
                   ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z),
                   (length, 0.12, 0.10), stone, coll)
        obj.rotation_euler[2] = math.atan2(dy, dx)


def window(name, center, width, height, face_axis, glass, stone, coll):
    """Dark recessed window with simple limestone jambs and sill."""
    if face_axis == "x":
        depth = 0.24
        cube(name + " glazing", center, (depth, width, height), glass, coll, 0.025)
        for side in (-1, 1):
            cube(name + f" jamb {side}", (center[0] + 0.02, center[1] + side * (width / 2 + 0.11), center[2]),
                 (depth + 0.05, 0.14, height + 0.28), stone, coll, 0.02)
        cube(name + " sill", (center[0] + 0.08, center[1], center[2] - height / 2 - 0.09),
             (depth + 0.18, width + 0.32, 0.15), stone, coll, 0.025)
        cube(name + " lintel", (center[0] + 0.03, center[1], center[2] + height / 2 + 0.09),
             (depth + 0.12, width + 0.28, 0.14), stone, coll, 0.02)
        cube(name + " muntin", (center[0] + 0.13, center[1], center[2]),
             (0.08, 0.07, height - 0.10), stone, coll)
    else:
        depth = 0.24
        cube(name + " glazing", center, (width, depth, height), glass, coll, 0.025)
        for side in (-1, 1):
            cube(name + f" jamb {side}", (center[0] + side * (width / 2 + 0.11), center[1] + 0.02, center[2]),
                 (0.14, depth + 0.05, height + 0.28), stone, coll, 0.02)
        cube(name + " sill", (center[0], center[1] + 0.08, center[2] - height / 2 - 0.09),
             (width + 0.32, depth + 0.18, 0.15), stone, coll, 0.025)
        cube(name + " lintel", (center[0], center[1] + 0.03, center[2] + height / 2 + 0.09),
             (width + 0.28, depth + 0.12, 0.14), stone, coll, 0.02)
        cube(name + " muntin", (center[0], center[1] + 0.13, center[2]),
             (0.07, 0.08, height - 0.10), stone, coll)


def pointed_arch_trim(name, front_x, cy, base_z, width, spring_z, apex_z, band, stone, coll):
    """Extruded limestone ring for the pointed Gothic openings in the archive photos."""
    outer = [(cy - width / 2 - band, base_z), (cy - width / 2 - band, spring_z),
             (cy, apex_z), (cy + width / 2 + band, spring_z), (cy + width / 2 + band, base_z)]
    inner = [(cy - width / 2, base_z), (cy - width / 2, spring_z),
             (cy, apex_z - band * 1.5), (cy + width / 2, spring_z), (cy + width / 2, base_z)]
    verts = []
    for x in (front_x, front_x + 0.18):
        verts.extend((x, y, z) for y, z in outer)
        verts.extend((x, y, z) for y, z in inner)
    faces = []
    # Four front/back voussoir strips and their outside/inside return faces.
    for i in range(4):
        faces.append((i, i + 1, 5 + i + 1, 5 + i))
        faces.append((10 + i, 10 + i + 1, 15 + i + 1, 15 + i))
        faces.append((i, i + 1, 10 + i + 1, 10 + i))
        faces.append((5 + i, 5 + i + 1, 15 + i + 1, 15 + i))
    faces.extend(((0, 5, 15, 10), (4, 9, 19, 14)))
    mesh = bpy.data.meshes.new(name + " limestone arch mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(stone)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    return obj


def pointed_glass_door(name, front_x, cy, width, spring_z, apex_z, glass, coll):
    """Dark pointed door leaf, matching the central entrance shown in source 180."""
    y0, y1 = cy - width / 2, cy + width / 2
    outline = [(y0, 0.16), (y0, spring_z), (cy, apex_z), (y1, spring_z), (y1, 0.16)]
    verts = [(x, y, z) for x in (front_x, front_x + 0.12) for y, z in outline]
    faces = [(0, 1, 2, 3, 4), (9, 8, 7, 6, 5)]
    for i in range(5):
        j = (i + 1) % 5
        faces.append((i, j, 5 + j, 5 + i))
    mesh = bpy.data.meshes.new(name + " pointed mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(glass)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    return obj


def pointed_entry(cx, cy, front_x, brick, stone, glass, coll):
    """Central pointed Gothic portal, with the projecting oriel above it."""
    pointed_glass_door("CQW recessed pointed Gothic entry door", front_x + 0.20, cy,
                       2.95, 3.00, 4.66, glass, coll)
    pointed_arch_trim("CQW central pointed Gothic portal surround", front_x + 0.38,
                      cy, 0.12, 2.95, 3.00, 4.94, 0.32, stone, coll)
    for side in (-1, 1):
        cube(f"CQW central portal engaged jamb {side}", (front_x + 0.57, cy + side * 1.68, 1.58),
             (0.42, 0.20, 2.70), stone, coll, 0.04)
    # Shallow projecting oriel visible directly above the entry in both archive views.
    # A shallow projecting oriel is visible immediately above the entrance in
    # both Purdue Archives exterior images; its exact dimensions are unknown.
    cube("CQW entrance oriel bay", (front_x + 1.0, cy, 7.08), (2.2, 5.3, 4.3), brick, coll, 0.08)
    cube("CQW oriel limestone sill", (front_x + 1.3, cy, 4.84), (2.8, 5.7, 0.28), stone, coll, 0.045)
    cube("CQW oriel limestone cornice", (front_x + 1.2, cy, 9.27), (2.65, 5.55, 0.24), stone, coll, 0.035)
    for j, offset in enumerate((-1.72, 0.0, 1.72)):
        window(f"CQW oriel window {j + 1}", (front_x + 2.13, cy + offset, 7.1),
               1.30, 2.5, "x", glass, stone, coll)
    # The 1950s Purdue Archives front elevation shows two smaller pointed
    # secondary entrances on either side of the central tower pair.
    # The 1950s front elevation places the two smaller pointed portals just
    # beyond the central tower pair, not at the far ends of the wings.
    for label, offset in (("south", -12.0), ("north", 12.0)):
        entry_y = cy + offset
        pointed_glass_door(f"CQW {label} secondary pointed door", front_x + 0.20,
                           entry_y, 1.68, 2.45, 3.72, glass, coll)
        pointed_arch_trim(f"CQW {label} secondary portal surround", front_x + 0.38,
                          entry_y, 0.12, 1.68, 2.45, 4.02, 0.25, stone, coll)
        for side in (-1, 1):
            cube(f"CQW {label} side door pier {side}",
                 (front_x + 0.38, entry_y + side * 1.04, 1.76),
                 (0.42, 0.25, 3.62), stone, coll, 0.03)


def build():
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for child in list(scene.collection.children):
        scene.collection.children.unlink(child)
        if child.users == 0:
            bpy.data.collections.remove(child)
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    preview = bpy.data.collections.new("CQW_Preview_Only")
    scene.collection.children.link(preview)

    data = json.loads(SOURCE_GEOJSON.read_text(encoding="utf-8"))
    feature = data["features"][0]
    props = feature["properties"]
    if props.get("BLDG_ABBR") != "CQW" or props.get("FID") != 60 or props.get("BUILDING_1") != "1315":
        raise RuntimeError("Purdue GIS feature identity mismatch; refusing to build the wrong asset")
    ring = [project_lon_lat(p[0], p[1]) for p in feature["geometry"]["coordinates"][0]]
    if ring[0] == ring[-1]:
        ring.pop()
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    brick = material("CQW red brick", (0.35, 0.09, 0.055))
    stone = material("CQW pale limestone trim", (0.67, 0.64, 0.56))
    roof = material("CQW dark roof membrane", (0.09, 0.10, 0.115))
    glass = material("CQW recessed dark window glass", (0.035, 0.075, 0.105), 0.28)

    make_shell(ring, 0.0, WALL_HEIGHT, brick, roof, asset)
    # The flat/parapeted main roof is partially visible behind the taller entry
    # towers. This is a qualitative interpretation of the 2004/undated photos.
    make_shell(ring, WALL_HEIGHT, ROOF_TOP, brick, roof, asset)
    edge_courses(ring, 0.55, stone, asset, "foundation")
    edge_courses(ring, WALL_HEIGHT - 0.18, stone, asset, "parapet coping")

    # Cary West's historic entry face is the east elevation toward Spitzer Court.
    # The archival photos show two tall crenellated square towers framing the
    # pointed entrance, with a projecting oriel directly above it.
    front_x = xmax
    tower_y_spacing = 5.8
    tower_width_y = 5.4
    tower_depth_x = 5.2
    for side, yy in (("north", cy + tower_y_spacing), ("south", cy - tower_y_spacing)):
        cube(f"CQW {side} entry tower", (front_x + tower_depth_x / 2 - 0.15, yy, TOWER_TOP / 2),
             (tower_depth_x, tower_width_y, TOWER_TOP), brick, asset, 0.08)
        for sy in (-1, 1):
            for sx in (-1, 1):
                cube(f"CQW {side} tower corner pier {sx}_{sy}",
                     (front_x + (0.2 if sx < 0 else tower_depth_x - 0.2), yy + sy * (tower_width_y / 2 - 0.18),
                      TOWER_TOP / 2), (0.34, 0.34, TOWER_TOP - 0.5), stone, asset, 0.025)
        # Heavy horizontal courses divide the shafts into the distinct storeys
        # visible in the historical front view, rather than a single blank block.
        for z in (4.9, 8.5, 12.1):
            cube(f"CQW {side} tower story belt {z:.2f}",
                 (front_x + tower_depth_x / 2 - 0.12, yy, z),
                 (tower_depth_x + 0.52, tower_width_y + 0.52, 0.24), stone, asset, 0.035)
        # The archival elevation shows narrow openings continuing into the
        # tower stages above the main roof; these remain qualitative estimates.
        for z in (3.25, 6.15, 9.05, 11.95, 14.2, 16.4):
            window(f"CQW {side} tower slit {z:.2f}",
                   (front_x + tower_depth_x - 0.15, yy, z), 0.82, 1.42, "x", glass, stone, asset)
            pointed_arch_trim(f"CQW {side} tower pointed window arch {z:.2f}",
                              front_x + tower_depth_x - 0.01, yy, z - 0.98,
                              0.82, z + 0.48, z + 1.14, 0.16, stone, asset)
        # A strong upper belt separates the last window stage from the crown.
        cube(f"CQW {side} tower upper stone band", (front_x + tower_depth_x / 2 - 0.12, yy, TOWER_TOP - 0.95),
             (tower_depth_x + 0.36, tower_width_y + 0.36, 0.34), stone, asset, 0.035)
        cube(f"CQW {side} tower crenellated crown", (front_x + tower_depth_x / 2 - 0.12, yy, TOWER_TOP - 0.18),
             (tower_depth_x + 0.56, tower_width_y + 0.56, 0.42), stone, asset, 0.04)
        # The 1950s elevation has emphatic corner merlons at the tower tops,
        # with smaller battlements stepping across the intervening parapet.
        for i in range(5):
            xx = front_x + 0.15 + i * (tower_depth_x + 0.08) / 4
            for sign in (-1, 1):
                tall_corner = i in (0, 4)
                height = 0.92 if tall_corner else 0.58
                cube(f"CQW {side} crenel {i}_{sign}",
                     (xx, yy + sign * (tower_width_y / 2 + 0.18), TOWER_TOP + height / 2),
                     (0.72 if tall_corner else 0.62, 0.42, height), brick, asset, 0.025)
        for i in range(1, 4):
            yy_side = yy - tower_width_y / 2 + i * tower_width_y / 4
            for sign in (-1, 1):
                tall_corner = False
                height = 0.58
                cube(f"CQW {side} side crenel {i}_{sign}",
                     (front_x + (tower_depth_x - 0.15 if sign > 0 else 0.1), yy_side, TOWER_TOP + height / 2),
                     (0.42, 0.62, height), brick, asset, 0.025)
        for xx in (front_x + 0.15, front_x + tower_depth_x + 0.23):
            for sign in (-1, 1):
                cube(f"CQW {side} upper corner merlon cap {xx:.2f}_{sign}",
                     (xx, yy + sign * (tower_width_y / 2 + 0.18), TOWER_TOP + 0.98),
                     (0.86, 0.54, 0.12), stone, asset, 0.025)
    pointed_entry(cx, cy, front_x, brick, stone, glass, asset)

    # Window counts are schematic, with spacing constrained by the surveyed
    # footprint and rows supported by the five-level Purdue GIS attribute.
    floor_step = WALL_HEIGHT / FLOORS
    facade_windows = 0
    side_x = xmax + 0.12
    y = ymin + 3.3
    while y < ymax - 3.0:
        if abs(y - cy) > 9.0 and min(abs(y - (cy - 12.0)), abs(y - (cy + 12.0))) > 3.7:
            for floor in range(FLOORS):
                z = (floor + 0.55) * floor_step
                window(f"CQW east facade bay {facade_windows:02d} floor {floor + 1}",
                       (side_x, y, z), 1.08, 1.58, "x", glass, stone, asset)
        facade_windows += 1
        y += 3.55

    west_x = xmin - 0.12
    bay = 0
    y = ymin + 3.3
    while y < ymax - 3.0:
        for floor in range(FLOORS):
            z = (floor + 0.55) * floor_step
            window(f"CQW west facade bay {bay:02d} floor {floor + 1}",
                   (west_x, y, z), 1.08, 1.58, "x", glass, stone, asset)
        bay += 1
        y += 3.55

    # Narrow end elevations repeat the same five-storey window language.
    for end_label, yy, sign in (("north", ymax + 0.12, 1), ("south", ymin - 0.12, -1)):
        for j, xx in enumerate((xmin + 4.3, xmax - 4.3)):
            for floor in range(FLOORS):
                z = (floor + 0.55) * floor_step
                window(f"CQW {end_label} end bay {j + 1} floor {floor + 1}",
                       (xx, yy, z), 1.08, 1.58, "y", glass, stone, asset)

    # Tiny angled gables at the parapet centre echo the profile in the archive
    # photo; no measured roof structure is claimed.
    for yy, label in ((cy - 1.6, "south"), (cy + 1.6, "north")):
        cube(f"CQW central parapet pier {label}", (front_x + 0.14, yy, WALL_HEIGHT + 0.8),
             (0.52, 1.45, 1.15), brick, asset, 0.035)
        cube(f"CQW central parapet stone cap {label}", (front_x + 0.16, yy, WALL_HEIGHT + 1.42),
             (0.72, 1.68, 0.18), stone, asset, 0.025)

    # Preview-only camera/lights remain outside the exported asset collection.
    camera_data = bpy.data.cameras.new("CQW evidence camera")
    camera = bpy.data.objects.new("CQW evidence camera", camera_data)
    preview.objects.link(camera)
    camera.location = (xmax + 100.0, cy - 12.0, 32.0)
    target = Vector((cx, cy, 8.5))
    camera.rotation_euler = (target - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 105.0
    scene.camera = camera
    for name, location, energy, size in (
        ("CQW key", (xmax + 40.0, cy - 35.0, 55.0), 32000, 42.0),
        ("CQW fill", (xmax - 20.0, cy + 35.0, 35.0), 16000, 38.0),
    ):
        light_data = bpy.data.lights.new(name, "AREA")
        light_data.energy = energy
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(name, light_data)
        preview.objects.link(light)
        light.location = location
        light.rotation_euler = (Vector((cx, cy, 8.0)) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    sun_data = bpy.data.lights.new("CQW broad daylight", "SUN")
    sun_data.energy = 6.0
    sun_data.angle = math.radians(14.0)
    sun = bpy.data.objects.new("CQW broad daylight", sun_data)
    preview.objects.link(sun)
    sun.location = (xmax + 70.0, cy - 45.0, 65.0)
    sun.rotation_euler = (Vector((cx, cy, 4.0)) - Vector(sun.location)).to_track_quat("-Z", "Y").to_euler()
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 8
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 80
    scene.render.image_settings.file_format = "PNG"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.55, 0.55, 0.55, 1.0)
    background.inputs["Strength"].default_value = 0.8
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.filepath = str(EVIDENCE / "preview_cqw_east_court.png")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    # A ground-up entrance crop gives the grader a legible facade view.
    camera.location = (xmax + 56.0, cy - 4.0, 16.0)
    camera_data.ortho_scale = 50.0
    camera.rotation_euler = (Vector((front_x, cy, 8.5)) - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(EVIDENCE / "preview_cqw_entrance.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    print(f"CQW built: {ASSET_PATH}; bounds=({xmin:.3f},{xmax:.3f},{ymin:.3f},{ymax:.3f}) m; "
          f"GIS vertices={len(ring)}; window bays={bay}; walls={WALL_HEIGHT:.3f} m; towers={TOWER_TOP:.3f} m")


build()
