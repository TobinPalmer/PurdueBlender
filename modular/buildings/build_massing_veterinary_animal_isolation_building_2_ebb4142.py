"""Build the isolated detailed VA2 library from its preserved Purdue GIS footprint.

Run from any working directory with Blender 5.x:
  blender --background --python modular/buildings/build_massing_veterinary_animal_isolation_building_2_ebb4142.py

Campus placement is intentionally omitted from this source library. Tobin's master
integration supplies it with Placement_<id> at the documented GIS bbox center.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ID = "massing_veterinary_animal_isolation_building_2_ebb4142"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ID}.blend"
AUDIT = ROOT / "audit" / "veterinary_animal_isolation_building_2"
SOURCE = AUDIT / "sources" / "purdue_va2_fid942.geojson"
COLLECTION_NAME = f"Asset_{ID}"
SCENE_NAME = f"Building_{ID}"

LAT0 = 40.4274
LON0 = -86.9137
COS_LAT = math.cos(math.radians(LAT0))
ANCHOR_XY = (-201.17001685170442, -948.4519000771968)
WALL_TOP = 4.35            # estimated; interstitial HVAC is included above occupied rooms
ROOF_TOP = 4.62            # estimated; the source GIS vertical attributes lack documented units


def campus_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon - LON0) * 111412.84 * COS_LAT,
            (lat - LAT0) * 111040.0)


def make_material(name, base, roughness=0.8, noise_scale=None, bump_strength=0.1,
                  metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*base, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*base, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if noise_scale:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = noise_scale
        noise.inputs["Detail"].default_value = 3.0
        noise.inputs["Roughness"].default_value = 0.68
        ramp = nodes.new("ShaderNodeValToRGB")
        span = 0.08
        ramp.color_ramp.elements[0].position = 0.5 - span
        ramp.color_ramp.elements[0].color = (*(c * 0.84 for c in base), 1.0)
        ramp.color_ramp.elements[1].position = 0.5 + span
        ramp.color_ramp.elements[1].color = (*(min(1.0, c * 1.12) for c in base), 1.0)
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.025
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return mat


def box(name, loc, dims, material, rotation=0.0, bevel=0.025, collection=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    (collection or ASSET).objects.link(obj)
    if material:
        obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("Small softened manufactured edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
    return obj


def cylinder(name, loc, radius, depth, material, collection=None, vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=loc)
    obj = bpy.context.object
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    (collection or ASSET).objects.link(obj)
    if material:
        obj.data.materials.append(material)
    bevel = obj.modifiers.new("Edge glint", "BEVEL")
    bevel.width = min(radius * 0.1, 0.025)
    bevel.segments = 2
    return obj


def mesh_prism(name, ring, z0, z1, material, collection=None):
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    me = bpy.data.meshes.new(name + "Mesh")
    me.from_pydata(verts, [], faces)
    me.materials.append(material)
    me.update()
    obj = bpy.data.objects.new(name, me)
    (collection or ASSET).objects.link(obj)
    return obj


def edge_box(name, a, b, s0, s1, z0, z1, depth, material, offset=0.0, bevel=0.02):
    """Place a box following a GIS polygon edge; s values are meters from edge start."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    along = (s0 + s1) * 0.5
    center = (a[0] + ux * along + nx * offset,
              a[1] + uy * along + ny * offset,
              (z0 + z1) * 0.5)
    return box(name, center, (s1 - s0, depth, z1 - z0), material,
               rotation=math.atan2(dy, dx), bevel=bevel)


def point_on_edge(a, b, s):
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    t = s / length
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def add_window(edge_idx, a, b, center_s, width, z0, z1, mats):
    dx, dy = b[0] - a[0], b[1] - a[1]
    angle = math.atan2(dy, dx)
    length = math.hypot(dx, dy)
    center = point_on_edge(a, b, center_s)
    x, y = center
    elevation = "east" if x > 0 else "west"
    # The glazing and frames sit just outside the wall surface; the wall is split
    # around the opening, so the dark glass remains visible in a fresh render.
    nx, ny = -dy / length, dx / length
    # The GIS ring is clockwise in its emitted coordinate order, so its right
    # edge normal points outwards on both long elevations.
    outward = 0.16
    cx, cy = x + nx * outward, y + ny * outward
    box(f"VA2 {elevation} exterior window {edge_idx}-{center_s:.1f} insulated glazing",
        (cx, cy, (z0 + z1) / 2), (width - 0.12, 0.055, z1 - z0 - 0.12),
        mats["glass"], angle, 0.012)
    # Narrow aluminum jambs, head and sill.
    frame = mats["metal"]
    for side in (-1, 1):
        px = x + nx * (outward + 0.02) + ux_component(dx,dy) * side * (width / 2 - 0.035)
        py = y + ny * (outward + 0.02) + uy_component(dx,dy) * side * (width / 2 - 0.035)
        box(f"VA2 {elevation} exterior window {edge_idx}-{center_s:.1f} aluminum jamb {side}",
            (px, py, (z0 + z1) / 2), (0.07, 0.075, z1 - z0), frame, angle, 0.008)
    for z in (z0 + 0.035, z1 - 0.035):
        box(f"VA2 {elevation} exterior window {edge_idx}-{center_s:.1f} aluminum sill head {z:.2f}",
            (cx, cy, z), (width, 0.075, 0.07), frame, angle, 0.008)


def ux_component(dx, dy):
    length = math.hypot(dx, dy)
    return dx / length


def uy_component(dx, dy):
    length = math.hypot(dx, dy)
    return dy / length


def edge_openings(a, b, edge_idx, mats):
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    side_mid_x = (a[0] + b[0]) / 2
    is_long_side = length > 30.0
    door_center = length * 0.24 if is_long_side and side_mid_x > 0 else None
    side_label = "east" if is_long_side and side_mid_x > 0 else "west" if is_long_side else "end"
    windows = []
    if is_long_side:
        windows = [length * f for f in (0.17, 0.37, 0.57, 0.77, 0.91)]
    door_w = 1.25
    win_w = 0.82

    # Continuous low plinth; leave a true door opening on the east long elevation.
    openings = []
    if door_center is not None:
        openings.append((max(0.0, door_center - door_w / 2),
                         min(length, door_center + door_w / 2), "door"))
    for c in windows:
        openings.append((max(0.0, c - win_w / 2), min(length, c + win_w / 2), "window"))
    openings.sort()
    cuts = [0.0, length]
    for lo, hi, _ in openings:
        cuts.extend((lo, hi))
    cuts = sorted(set(cuts))

    def opening_at(mid):
        for lo, hi, kind in openings:
            if lo - 1e-6 <= mid <= hi + 1e-6:
                return kind
        return None

    # Concrete curb and occupied-story wall, split around door and window apertures.
    for lo, hi in zip(cuts, cuts[1:]):
        if hi - lo < 0.015:
            continue
        kind = opening_at((lo + hi) / 2)
        if kind != "door":
            edge_box(f"VA2 exterior {side_label} edge {edge_idx} concrete base panel {lo:.2f}",
                     a, b, lo, hi, 0.08, 0.72, 0.28, mats["foundation"])
            edge_box(f"VA2 exterior {side_label} edge {edge_idx} wall panel lower {lo:.2f}",
                     a, b, lo, hi, 0.72, 1.88, 0.24, mats["wall"])
        if kind != "door":
            if kind == "window":
                c = (lo + hi) / 2
                add_window(edge_idx, a, b, c, win_w, 1.88, 2.57, mats)
            else:
                edge_box(f"VA2 exterior {side_label} edge {edge_idx} wall panel window band {lo:.2f}",
                         a, b, lo, hi, 1.88, 2.57, 0.24, mats["wall"])
        # The band above the door opening is a header. Windows remain glazed below.
            edge_box(f"VA2 exterior {side_label} edge {edge_idx} wall panel upper {lo:.2f}",
                 a, b, lo, hi, 2.57, 3.22, 0.24, mats["wall"])
        edge_box(f"VA2 exterior {side_label} edge {edge_idx} structural interstitial plinth {lo:.2f}",
                 a, b, lo, hi, 3.22, 3.42, 0.26, mats["panel"])
        # HVAC interstitial: continuous pale band, with restrained ventilation slots.
        if is_long_side and kind not in ("door", "window") and hi - lo > 0.15:
            edge_box(f"VA2 exterior {side_label} edge {edge_idx} HVAC louver recess {lo:.2f}",
                     a, b, lo, hi, 3.44, 4.22, 0.17, mats["louver_dark"])
            slat_count = max(1, int((hi - lo) / 0.13))
            for j in range(slat_count):
                ss = lo + (j + 0.5) * (hi - lo) / slat_count
                edge_box(f"VA2 exterior {side_label} edge {edge_idx} HVAC horizontal louver {lo:.1f}-{j:02d}",
                         a, b, ss - min(0.04, (hi - lo) / 8),
                         ss + min(0.04, (hi - lo) / 8), 3.49, 4.17, 0.10,
                         mats["metal"], offset=0.15, bevel=0.008)
        else:
            edge_box(f"VA2 exterior {side_label} edge {edge_idx} upper interstitial panel {lo:.2f}",
                     a, b, lo, hi, 3.44, 4.22, 0.24, mats["panel"])
        edge_box(f"VA2 exterior {side_label} edge {edge_idx} roof fascia {lo:.2f}",
                 a, b, lo, hi, 4.22, WALL_TOP, 0.30, mats["panel"])

    if door_center is not None:
        p = point_on_edge(a, b, door_center)
        angle = math.atan2(b[1] - a[1], b[0] - a[0])
        nx, ny = -(b[1] - a[1]) / length, (b[0] - a[0]) / length
        sign = 1
        cx, cy = p[0] + nx * sign * 0.17, p[1] + ny * sign * 0.17
        box(f"VA2 east staff access insulated door", (cx, cy, 1.08),
            (1.12, 0.075, 2.16), mats["door"], angle, 0.035)
        # Simple metal frame and a small, source-supported building identity plate.
        plate_pos = (cx + nx * sign * 0.06, cy + ny * sign * 0.06, 2.26)
        box("VA2 discreet entry identity plaque", plate_pos, (0.55, 0.04, 0.20),
            mats["metal"], angle, 0.015)


def add_target(a, b):
    obj = a
    obj.rotation_euler = (0.0, 0.0, 0.0)


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def build():
    AUDIT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(AUDIT / "preview_exterior.png")
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene["building_id"] = ID
    scene["origin_xy_m"] = list(ANCHOR_XY)
    scene["evidence_note"] = "Footprint is source-backed. Facade details, room layout and height are explicitly estimated."

    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    review = bpy.data.collections.new("Review_Setup | not part of exported building library")
    scene.collection.children.link(review)
    global ASSET
    ASSET = asset

    feature = json.loads(SOURCE.read_text(encoding="utf-8"))["features"][0]
    ring_geo = feature["geometry"]["coordinates"][0]
    ring_world = [campus_xy(p[0], p[1]) for p in ring_geo[:-1]]
    ring = [(x - ANCHOR_XY[0], y - ANCHOR_XY[1]) for x, y in ring_world]
    if len(ring) < 4:
        raise RuntimeError("GIS outline is unexpectedly small")

    mats = {
        "wall": make_material("VA2 | light warm-gray insulated CMU/render", (0.66, 0.64, 0.58), 0.86, 32, 0.12),
        "panel": make_material("VA2 | pale gray metal fascia and upper panels", (0.72, 0.73, 0.70), 0.63, 56, 0.08, 0.22),
        "foundation": make_material("VA2 | darker concrete foundation course", (0.42, 0.43, 0.41), 0.90, 24, 0.15),
        "roof": make_material("VA2 | light-gray mineral roof membrane", (0.60, 0.62, 0.60), 0.76, 18, 0.09),
        "roof_dark": make_material("VA2 | weathered roof service strip", (0.31, 0.33, 0.32), 0.87, 14, 0.11),
        "louver_dark": make_material("VA2 | dark recessed HVAC louvers", (0.22, 0.25, 0.25), 0.70, 38, 0.04, 0.1),
        "metal": make_material("VA2 | galvanized and powder-coated metal", (0.38, 0.42, 0.41), 0.42, 75, 0.025, 0.65),
        "glass": make_material("VA2 | limited high-level safety glazing", (0.085, 0.13, 0.14), 0.24, 9, 0.01, 0.15),
        "door": make_material("VA2 | insulated metal access door", (0.31, 0.35, 0.34), 0.56, 38, 0.04, 0.28),
        "floor": make_material("VA2 | sealed animal-care epoxy floor", (0.52, 0.56, 0.53), 0.48, 26, 0.04),
        "interior_wall": make_material("VA2 | washable interior wall coating", (0.78, 0.78, 0.73), 0.82, 48, 0.06),
        "stainless": make_material("VA2 | stainless animal-care fixtures", (0.57, 0.62, 0.61), 0.26, 95, 0.015, 0.72),
        "pen": make_material("VA2 | galvanized modular animal pen rails", (0.48, 0.54, 0.52), 0.35, 72, 0.02, 0.68),
    }

    # Source polygon is retained vertex-for-vertex in the documented local frame.
    mesh_prism("VA2 GIS footprint foundation", ring, -0.22, 0.0, mats["foundation"])
    mesh_prism("VA2 occupied floor slab | sealed washable finish", ring, 0.0, 0.16, mats["floor"])

    # Exterior wall edge segmentation leaves real apertures rather than painted-on windows.
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        edge_openings(a, b, i + 1, mats)

    # Roof/parapet follow the same GIS polygon. The modest rooftop equipment follows
    # the aerial; all units are low profile and their precise arrangement is estimated.
    mesh_prism("VA2 flat roof deck | source-aerial light membrane", ring, WALL_TOP - 0.05,
               ROOF_TOP, mats["roof"])
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        edge_box(f"VA2 roof perimeter upstand {i + 1}", a, b, 0.0,
                 math.hypot(b[0] - a[0], b[1] - a[1]), ROOF_TOP, ROOF_TOP + 0.25,
                 0.24, mats["panel"])

    # A narrow central maintenance strip and spaced low-profile exhaust/HVAC units
    # are visible in the current aerial. Details remain generic where the image is soft.
    box("VA2 central rooftop service strip", (0.0, 0.0, ROOF_TOP + 0.025),
        (2.2, 31.0, 0.055), mats["roof_dark"], 0.0, 0.025)
    for idx, y in enumerate((-12.5, -7.2, -1.9, 3.4, 8.7, 13.1), 1):
        box(f"VA2 low rooftop HVAC curb {idx}", (0.0, y, ROOF_TOP + 0.22),
            (1.35, 1.8, 0.34), mats["louver_dark"], 0.0, 0.07)
        box(f"VA2 rooftop HVAC service cap {idx}", (0.0, y, ROOF_TOP + 0.43),
            (1.18, 1.54, 0.10), mats["panel"], 0.0, 0.035)
        for slat in range(8):
            x = -0.55 + slat * 0.157
            box(f"VA2 rooftop unit {idx} intake slat {slat + 1}",
                (x, y - 0.03, ROOF_TOP + 0.20), (0.045, 1.45, 0.23),
                mats["metal"], 0.0, 0.008)
    for idx, y in enumerate((-15.4, -9.8, -4.2, 1.4, 7.0, 12.6, 16.0), 1):
        cylinder(f"VA2 roof exhaust curb {idx}", (4.0, y, ROOF_TOP + 0.15),
                 0.24, 0.30, mats["panel"])
        cylinder(f"VA2 roof exhaust cap {idx}", (4.0, y, ROOF_TOP + 0.34),
                 0.34, 0.10, mats["metal"])
    box("VA2 roof access hatch", (-4.0, -14.0, ROOF_TOP + 0.11),
        (1.0, 1.25, 0.16), mats["metal"], 0.0, 0.035)

    # Interior: the source confirms research/teaching animal rooms and HVAC above,
    # but no internal plans. These cleanable partitions and central service corridor
    # are an explicitly illustrative, non-surveyed arrangement.
    box("VA2 central staff/service corridor floor", (0.0, 0.0, 0.171),
        (1.8, 34.0, 0.018), mats["panel"], 0.0, 0.01)
    for side in (-1, 1):
        x0, x1 = (side * 1.0, side * 5.45)
        wall_x = (x0 + x1) / 2
        room_centers = (-13.8, -8.5, -3.2, 2.1, 7.4, 12.7)
        for room_idx, y in enumerate(room_centers):
            # Short dividing wall leaves each animal room open to its staff aisle.
            box(f"VA2 interior washable room partition S{side} R{room_idx + 1}",
                (wall_x, y, 1.57), (abs(x1 - x0), 0.14, 2.75),
                mats["interior_wall"], 0.0, 0.025)
            # Central corridor door opening is represented by a framed doorway at the
            # inner end; it is illustrative and not asserted to match the inaccessible plan.
            inner_x = side * 1.18
            box(f"VA2 interior room door S{side} R{room_idx + 1}",
                (inner_x, y, 1.18), (0.06, 0.90, 2.04), mats["door"], 0.0, 0.025)
            box(f"VA2 room wash station S{side} R{room_idx + 1}",
                (side * 4.75, y + 1.7, 0.68), (0.70, 0.45, 0.78),
                mats["stainless"], 0.0, 0.045)
            # Two sanitized modular pen/stall frames per room, not species-specific cages.
            for pen_idx, py in enumerate((y - 1.0, y + 0.9), 1):
                px = side * 3.0
                for dx in (-0.8, 0.8):
                    box(f"VA2 pen upright S{side} R{room_idx + 1} P{pen_idx} X{dx}",
                        (px + dx, py, 0.92), (0.055, 0.055, 1.50), mats["pen"], 0.0, 0.012)
                for z in (0.38, 0.72, 1.08, 1.40):
                    box(f"VA2 pen rail S{side} R{room_idx + 1} P{pen_idx} Z{z}",
                        (px, py, z), (1.65, 0.05, 0.05), mats["pen"], 0.0, 0.012)
                for dx in (-0.8, 0.8):
                    box(f"VA2 pen end rail S{side} R{room_idx + 1} P{pen_idx} X{dx}",
                        (px + dx, py, 0.92), (0.05, 0.05, 1.50), mats["pen"], 0.0, 0.012)
        # Longitudinal washable corridor-side partitions define the animal rooms.
        box(f"VA2 interior corridor divider S{side}", (side * 1.0, 0.0, 1.46),
            (0.13, 31.0, 2.55), mats["interior_wall"], 0.0, 0.025)
    # Small staff wash/bathroom and vestibule at the south end; the OEP confirms an
    # end-of-building bathroom but does not identify which end or its dimensions.
    box("VA2 south-end staff washroom partition", (0.0, -16.2, 1.40),
        (7.8, 0.14, 2.45), mats["interior_wall"], 0.0, 0.02)
    box("VA2 south-end washroom room block", (0.0, -16.9, 0.32),
        (2.3, 1.1, 0.62), mats["stainless"], 0.0, 0.04)
    cylinder("VA2 washroom sink basin", (1.5, -17.0, 0.86), 0.28, 0.14,
             mats["stainless"], vertices=24)
    # A few continuous service rails and ceiling-supported interstitial trusses.
    for x in (-5.2, -2.0, 2.0, 5.2):
        box(f"VA2 interior washable service rail {x}", (x, 0.0, 0.20),
            (0.055, 29.0, 0.06), mats["metal"], 0.0, 0.008)

    # Review camera/light setup stays in a separate collection, outside Asset_<id>.
    ground_mat = make_material("Review ground | neutral muted lawn", (0.20, 0.24, 0.20), 0.98, 4, 0.04)
    ground = box("Review ground plane | not exported", (0, 0, -0.38), (100, 100, 0.25), ground_mat,
                 0.0, 0.0, review)
    cam_data = bpy.data.cameras.new("VA2 exterior review camera")
    cam = bpy.data.objects.new("VA2 exterior review camera", cam_data)
    review.objects.link(cam)
    cam.location = (28.0, -33.0, 22.0)
    cam.data.lens = 50
    aim(cam, (0.0, 0.0, 2.15))
    scene.camera = cam
    sun_data = bpy.data.lights.new("VA2 broad soft sun", "AREA")
    sun = bpy.data.objects.new("VA2 broad soft sun", sun_data)
    review.objects.link(sun)
    sun.location = (4, -10, 24)
    sun.data.energy = 3200
    sun.data.shape = "DISK"
    sun.data.size = 18
    aim(sun, (0, 0, 0))
    fill_data = bpy.data.lights.new("VA2 facade fill", "AREA")
    fill = bpy.data.objects.new("VA2 facade fill", fill_data)
    review.objects.link(fill)
    fill.location = (-18, 8, 9)
    fill.data.energy = 1400
    fill.data.size = 14
    aim(fill, (0, 0, 2))
    world = bpy.data.worlds.new("VA2 review studio sky")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.33, 0.38, 0.44, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.42
    scene.world = world

    # A clean orthographic roof review view is also saved for GIS comparison.
    top_cam_data = bpy.data.cameras.new("VA2 roof review camera")
    top_cam = bpy.data.objects.new("VA2 roof review camera", top_cam_data)
    review.objects.link(top_cam)
    top_cam.location = (0, 0, 62)
    top_cam.data.type = "ORTHO"
    top_cam.data.ortho_scale = 58
    aim(top_cam, (0, 0, 2))

    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Pack procedural materials only; no image textures or external dependencies exist.
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    # Render exterior, roof and an explanatory interior cutaway. The saved source
    # remains whole; visibility changes below affect only these review renders.
    scene.camera = cam
    scene.render.filepath = str(AUDIT / "preview_exterior.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = top_cam
    scene.render.filepath = str(AUDIT / "preview_roof.png")
    bpy.ops.render.render(write_still=True)

    # For the cutaway, hide the roof and the eastern exterior wall to expose the
    # illustrative interior. Restore every object state before saving the source.
    saved_hides = {o.name: o.hide_render for o in ASSET.objects}
    for obj in ASSET.objects:
        if obj.name.startswith(("VA2 flat roof", "VA2 roof perimeter", "VA2 central rooftop",
                                "VA2 low rooftop", "VA2 rooftop HVAC", "VA2 roof exhaust",
                                "VA2 roof access")):
            obj.hide_render = True
        if obj.name.startswith(("VA2 east exterior window", "VA2 west exterior window",
                                "VA2 east staff access", "VA2 west staff access")):
            obj.hide_render = True
        if obj.name.startswith(("VA2 exterior east", "VA2 exterior west")) and any(
                token in obj.name for token in (" wall panel", " concrete base", " structural interstitial", " roof fascia", " HVAC louver", " HVAC horizontal louver", " upper interstitial panel")):
            obj.hide_render = True
    # Use a camera slightly above the long side with a long lens, aimed into the room strip.
    int_cam_data = bpy.data.cameras.new("VA2 interior explanatory camera")
    int_cam = bpy.data.objects.new("VA2 interior explanatory camera", int_cam_data)
    review.objects.link(int_cam)
    int_cam.location = (12.0, -5.0, 3.6)
    int_cam.data.lens = 40
    aim(int_cam, (0.0, 0.0, 1.5))
    scene.camera = int_cam
    scene.render.filepath = str(AUDIT / "preview_interior_cutaway.png")
    bpy.ops.render.render(write_still=True)
    for obj in ASSET.objects:
        obj.hide_render = saved_hides[obj.name]
    bpy.data.objects.remove(int_cam, do_unlink=True)
    # Camera review objects stay separate from the export collection.
    scene.camera = cam
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    return ring


if __name__ == "__main__":
    build()
