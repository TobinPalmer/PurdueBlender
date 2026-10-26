"""Build the evidence-backed Pi Kappa Alpha (Pike) chapter house.

The GIS polygon is the Purdue Buildings Shapes FID 790 record in
../audit/massing_house_301841252_e4f8f05/sources/purdue_gis_fid790.json.
GIS XY is EPSG:3857 and is converted to the project's documented local campus
metre approximation. The model remains in campus coordinates to preserve the
existing simple-massing manifest placement and linked-asset behavior.

The 2023 chapter-house photograph supports the brick facade, three visible
storeys, white classical portico, white shutters, entry steps and gray metal
roof. Heights and unpictured elevations remain estimates.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


BUILDING_ID = "massing_house_301841252_e4f8f05"
COLLECTION_NAME = "Asset_" + BUILDING_ID
OBJECT_NAME = "House_301841252"
ROOT = Path(__file__).resolve().parents[2]
GIS_PATH = ROOT / "audit" / BUILDING_ID / "sources" / "purdue_gis_fid790.json"
BLEND_PATH = ROOT / "modular" / "buildings" / (BUILDING_ID + ".blend")
PREVIEW_PATH = ROOT / "audit" / BUILDING_ID / "preview.png"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
EARTH_RADIUS_M = 6378137.0


def xy_3857_to_campus(x: float, y: float) -> tuple[float, float]:
    lon = math.degrees(x / EARTH_RADIUS_M)
    lat = math.degrees(2.0 * math.atan(math.exp(y / EARTH_RADIUS_M)) - math.pi / 2.0)
    local_x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    local_y = (lat - ORIGIN_LAT) * 111040.0
    return local_x, local_y


def gis_ring() -> list[tuple[float, float]]:
    record = json.loads(GIS_PATH.read_text(encoding="utf-8"))
    features = record.get("features", [])
    if len(features) != 1:
        raise RuntimeError(f"Expected one GIS FID 790 feature, got {len(features)}")
    attributes = features[0]["attributes"]
    if attributes.get("FID") != 790 or attributes.get("BUILDING_N") != "Pi Kappa Alpha":
        raise RuntimeError(f"Unexpected GIS identity: {attributes}")
    ring = features[0]["geometry"]["rings"][0]
    points = [xy_3857_to_campus(float(x), float(y)) for x, y in ring]
    if points[0] == points[-1]:
        points.pop()
    return points


def material(name: str, color: tuple[float, float, float, float], roughness: float = 0.82):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def mesh_object(name: str, vertices, faces, mat, collection, smooth=False):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.validate(clean_customdata=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    return obj


def box(name, center, size, mat, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new("Soft masonry and trim edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def cylinder(name, center, radius, depth, mat, collection, vertices=32, radius_top=None):
    if radius_top is None or abs(radius - radius_top) < 1e-5:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
        obj = bpy.context.object
    else:
        verts = []
        faces = []
        for z, r in ((-depth / 2.0, radius), (depth / 2.0, radius_top)):
            for i in range(vertices):
                a = 2.0 * math.pi * i / vertices
                verts.append((r * math.cos(a), r * math.sin(a), z))
        faces.append(tuple(range(vertices - 1, -1, -1)))
        faces.append(tuple(range(vertices, 2 * vertices)))
        for i in range(vertices):
            j = (i + 1) % vertices
            faces.append((i, j, vertices + j, vertices + i))
        obj = mesh_object(name, verts, faces, mat, collection, smooth=True)
        obj.location = center
        return obj
    obj.name = name
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def roof_mesh(points, roof_mat, collection, eave_z=9.1, ridge_z=10.7, overhang=0.28):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    ridge_start, ridge_end = min_y + 3.3, max_y - 3.3
    # Mild uniform perimeter overhang, preserving the exact GIS wall outline.
    eaves = []
    for x, y in points:
        vx, vy = x - cx, y - cy
        d = max(math.hypot(vx, vy), 1e-6)
        eaves.append((x + overhang * vx / d, y + overhang * vy / d, eave_z))

    def ridge_at(y):
        return (cx, min(max(y, ridge_start), ridge_end), ridge_z)

    verts = list(eaves)
    ridges = [ridge_at(y) for y in (ridge_start, ridge_end)]
    faces = []
    for i in range(len(eaves)):
        a, b = eaves[i], eaves[(i + 1) % len(eaves)]
        ra, rb = ridge_at(a[1]), ridge_at(b[1])
        ia, ib = len(verts), len(verts) + 1
        verts.extend((ra, rb))
        faces.append((i, (i + 1) % len(eaves), ib, ia))
    mesh_object("Roof_Hip_Planes", verts, faces, roof_mat, collection)
    box("Roof_Ridge_Cap", (cx, (ridge_start + ridge_end) / 2.0, ridge_z + 0.04),
        (0.18, ridge_end - ridge_start, 0.12), roof_mat, collection, 0.025)
    # Restrained standing-seam lines, mapped from eave to ridge on both broad slopes.
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    for k in range(1, 8):
        frac = k / 8.0
        for side_x in (xmin, xmax):
            x = side_x + (cx - side_x) * frac
            z = eave_z + (ridge_z - eave_z) * frac + 0.025
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=0.018,
                location=(x, (ridge_start + ridge_end) / 2.0, z))
            seam = bpy.context.object
            seam.name = f"Roof_Standing_Seam_{k}_{'W' if side_x == xmin else 'E'}"
            seam.dimensions = (0.035, ridge_end - ridge_start, 0.035)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            for coll in list(seam.users_collection):
                coll.objects.unlink(seam)
            collection.objects.link(seam)
            seam.data.materials.append(roof_mat)


def oriented_front_text(name, body, loc, size, mat, collection, align="CENTER"):
    data = bpy.data.curves.new(name + "_Curve", "FONT")
    data.body = body
    data.size = size
    data.align_x = align
    data.extrude = 0.012
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    # Local text X->world +Y, local Y->world +Z, local normal->world +X.
    obj.rotation_euler = (math.pi / 2.0, 0.0, math.pi / 2.0)
    obj.location = loc
    obj.data.materials.append(mat)
    return obj


def front_x(points, y):
    """Interpolate the eastern structural facade boundary from the GIS ring."""
    crossings = []
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        if abs(y2 - y1) < 1e-7:
            if abs(y - y1) < 1e-6:
                crossings.extend((x1, x2))
            continue
        if min(y1, y2) <= y <= max(y1, y2):
            t = (y - y1) / (y2 - y1)
            crossings.append(x1 + t * (x2 - x1))
    if not crossings:
        raise RuntimeError(f"No facade intersection at y={y}")
    return max(crossings)


def facade_window(name, x, y, zc, width, mat_wall, trim, glass, collection):
    # +X-facing inset and white casing; two pale shutters with louver slats.
    x_face = x + 0.035
    height = 1.65
    box(name + "_Recess", (x_face, y, zc), (0.08, width * 0.72, height * 0.88), glass, collection)
    t = 0.09
    # Window casing
    box(name + "_Trim_Left", (x_face + 0.055, y - width / 2.0, zc), (0.15, t, height + 2*t), trim, collection)
    box(name + "_Trim_Right", (x_face + 0.055, y + width / 2.0, zc), (0.15, t, height + 2*t), trim, collection)
    box(name + "_Trim_Head", (x_face + 0.055, y, zc + height / 2.0 + t/2.0), (0.15, width + 2*t, t), trim, collection)
    box(name + "_Sill", (x_face + 0.09, y, zc - height / 2.0 - 0.06), (0.3, width + 0.3, 0.14), trim, collection)
    # Center meeting rail and paired sash mullion.
    box(name + "_Center_Mullion", (x_face + 0.11, y, zc), (0.08, 0.055, height * 0.88), trim, collection)
    box(name + "_Meeting_Rail", (x_face + 0.11, y, zc), (0.08, width * 0.72, 0.045), trim, collection)
    shutter_w = 0.22
    for side in (-1, 1):
        sy = y + side * (width / 2.0 + 0.22)
        box(name + f"_Shutter_{side}", (x_face + 0.045, sy, zc), (0.11, shutter_w, height * 0.95), trim, collection)
        for row in range(7):
            sz = zc - height * 0.38 + row * (height * 0.76 / 6.0)
            box(name + f"_Louver_{side}_{row}", (x_face + 0.11, sy, sz), (0.035, shutter_w + 0.025, 0.025),
                mat_wall if row % 2 else trim, collection)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = 'Building_' + BUILDING_ID
    scene.unit_settings.system = "METRIC"
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    asset_layer = next(lc for lc in bpy.context.view_layer.layer_collection.children
                       if lc.collection == collection)
    bpy.context.view_layer.active_layer_collection = asset_layer

    brick = material("Pike_Red_Brick", (0.36, 0.085, 0.048, 1.0))
    pale_brick = material("Pike_Brick_Accent", (0.50, 0.17, 0.095, 1.0))
    white = material("Pike_White_Painted_Trim", (0.88, 0.87, 0.80, 1.0))
    door_mat = material("Pike_White_Entry_Door", (0.77, 0.77, 0.70, 1.0))
    glass = material("Pike_Dark_Window_Glass", (0.105, 0.16, 0.18, 1.0), 0.34)
    roof_mat = material("Pike_Standing_Seam_Roof", (0.31, 0.35, 0.36, 1.0), 0.68)
    concrete = material("Pike_Entry_Concrete", (0.59, 0.58, 0.54, 1.0))
    dark = material("Pike_Door_Recess", (0.075, 0.055, 0.042, 1.0))

    points = gis_ring()
    minx, maxx = min(p[0] for p in points), max(p[0] for p in points)
    miny, maxy = min(p[1] for p in points), max(p[1] for p in points)
    center_y = (miny + maxy) / 2.0
    wall_height = 9.1  # estimated from three visible storeys; no surveyed elevation found

    # Exact ring from the official Purdue GIS feature, retaining the existing
    # massing's campus coordinate frame and direct-link location.
    verts = [(x, y, z) for z in (0.0, wall_height) for x, y in points]
    n = len(points)
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2*n))]
    faces.extend((i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n))
    walls = mesh_object(OBJECT_NAME, verts, faces, brick, collection)
    walls["source_feature"] = "Purdue BuildingShapesZip4 FID 790; Pi Kappa Alpha; 629 University St"
    walls["height_status"] = "estimated: three visible storeys; wall eave 9.1 m"

    # A low foundation course follows the same footprint without changing the
    # GIS wall registration.
    base_v = [(x, y, z) for z in (-0.04, 0.42) for x, y in points]
    base_f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2*n))]
    base_f.extend((i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n))
    mesh_object("Foundation_Brick_Course", base_v, base_f, pale_brick, collection)

    # Gray shallow hipped roof. Ridge and eave dimensions are estimated from
    # the chapter's dated facade photograph, not supplied as survey values.
    roof_mesh(points, roof_mat, collection, eave_z=wall_height, ridge_z=10.75)

    # White eaves board and restrained cornice below the metal eaves.
    for y in (miny, maxy):
        box(f"End_Eaves_Board_{'N' if y > center_y else 'S'}",
            ((minx + maxx)/2.0, y, wall_height - 0.1), (maxx-minx+0.55, 0.16, 0.28), white, collection, 0.025)

    # The east elevation in the chapter's 2023 photograph has three rows of
    # shuttered windows. The GIS polygon has small step-backs, so each opening
    # is placed on its matching east-wall segment.
    y_offsets = (-18.2, -14.2, -8.5, -2.55, 2.55, 8.5, 14.2, 18.2)
    levels = (1.55, 4.55, 7.55)
    for level_i, zc in enumerate(levels, 1):
        for j, dy in enumerate(y_offsets, 1):
            y = center_y + dy
            x = front_x(points, y)
            # Front portico has paired openings at the sides of the entry;
            # keep the central doorway clear at grade.
            if abs(dy) < 3.0 and level_i == 1:
                continue
            facade_window(f"East_Window_F{level_i}_{j}", x, y, zc, 1.05, brick, white, glass, collection)

    # Conservative rear/end fenestration, with no decorative facade claims.
    for level_i, zc in enumerate(levels, 1):
        for j, dy in enumerate((-13.0, -4.5, 4.5, 13.0), 1):
            y = center_y + dy
            x = minx
            box(f"West_Window_F{level_i}_{j}_Recess", (x - 0.035, y, zc), (0.08, 0.86, 1.32), glass, collection)
            box(f"West_Window_F{level_i}_{j}_Trim", (x - 0.085, y, zc), (0.1, 1.22, 1.62), white, collection)
        for end_name, y in (("South", miny), ("North", maxy)):
            for dx_i, frac in enumerate((0.32, 0.68), 1):
                x = minx + (maxx-minx) * frac
                box(f"{end_name}_Window_F{level_i}_{dx_i}_Recess", (x, y + (0.035 if end_name == "South" else -0.035), zc),
                    (0.85, 0.08, 1.32), glass, collection)
                box(f"{end_name}_Window_F{level_i}_{dx_i}_Trim", (x, y + (0.085 if end_name == "South" else -0.085), zc),
                    (1.2, 0.1, 1.62), white, collection)

    # Central classical portico on the east elevation. Its four smooth white
    # columns, entablature and pediment are directly visible in the chapter
    # photograph and the 1965 chapter-house description.
    front = front_x(points, center_y)
    portico_x = front + 0.62
    portico_width = 11.2
    for idx, dy in enumerate((-4.25, -1.42, 1.42, 4.25), 1):
        y = center_y + dy
        box(f"Portico_Pedestal_{idx}", (portico_x, y, 0.50), (0.70, 0.70, 0.42), white, collection, 0.04)
        cylinder(f"Portico_Column_Shaft_{idx}", (portico_x, y, 4.72), 0.32, 8.02,
                 white, collection, vertices=40, radius_top=0.28)
        cylinder(f"Portico_Column_Base_{idx}", (portico_x, y, 0.78), 0.46, 0.24, white, collection, vertices=40)
        cylinder(f"Portico_Column_Capital_{idx}", (portico_x, y, 8.84), 0.44, 0.28, white, collection, vertices=40)

    entablature_z = 9.16
    box("Portico_Entablature", (portico_x + 0.03, center_y, entablature_z),
        (0.86, portico_width, 0.82), white, collection, 0.04)
    # Solid pediment triangle facing east (+X).
    ptx = portico_x + 0.05
    halfw = portico_width / 2.0
    zbase, zpeak = 9.57, 11.42
    tri_verts = [(ptx, center_y-halfw, zbase), (ptx, center_y+halfw, zbase),
                 (ptx, center_y, zpeak), (ptx+0.52, center_y-halfw, zbase),
                 (ptx+0.52, center_y+halfw, zbase), (ptx+0.52, center_y, zpeak)]
    tri_faces = [(0,1,2), (5,4,3), (0,3,4,1), (0,2,5,3), (1,4,5,2)]
    mesh_object("Portico_Triangular_Pediment", tri_verts, tri_faces, white, collection)
    # Thick white raking trim follows the pediment roofline.
    for side, sign in (("Left", -1), ("Right", 1)):
        a = Vector((ptx+0.08, center_y, zpeak+0.04))
        b = Vector((ptx+0.08, center_y+sign*halfw, zbase))
        vec = b-a
        trim_obj = box(f"Pediment_Rake_{side}", (a+b)/2.0, (0.18, vec.yz.length, 0.20), white, collection, 0.02)
        trim_obj.rotation_euler[0] = math.atan2(vec.z, vec.y)

    oriented_front_text("Portico_Front_Lettering", "PI KAPPA ALPHA",
                        (ptx + 0.57, center_y, 9.98), 0.82, brick, collection)

    # Centered white entrance and smaller Greek Revival door hood.
    door_x = front + 0.12
    box("Entry_Door_Reveal", (door_x, center_y, 1.25), (0.16, 2.0, 2.55), dark, collection)
    box("Entry_Door_Leaf", (door_x + 0.10, center_y, 1.20), (0.12, 1.65, 2.30), door_mat, collection, 0.025)
    box("Entry_Door_Upper_Glass", (door_x + 0.18, center_y, 1.82), (0.08, 1.22, 0.68), glass, collection)
    for dy in (-0.55, 0.55):
        box(f"Entry_Door_Panel_{dy}", (door_x + 0.18, center_y + dy, 0.90), (0.08, 0.48, 0.58), white, collection, 0.025)
    box("Entry_Door_Hood_Beam", (door_x + 0.68, center_y, 2.73), (0.72, 3.65, 0.24), white, collection, 0.025)
    hood_tri = [(door_x+0.60, center_y-1.85, 2.82), (door_x+0.60, center_y+1.85, 2.82),
                (door_x+0.60, center_y, 3.75), (door_x+0.95, center_y-1.85, 2.82),
                (door_x+0.95, center_y+1.85, 2.82), (door_x+0.95, center_y, 3.75)]
    mesh_object("Entry_Door_Pediment", hood_tri, [(0,1,2),(5,4,3),(0,3,4,1),(0,2,5,3),(1,4,5,2)], white, collection)
    for step_i, (x, depth, height, width) in enumerate(((front+0.58, 1.15, 0.22, 7.3),
                                                           (front+1.18, 1.05, 0.22, 8.4),
                                                           (front+1.78, 1.05, 0.22, 9.5)), 1):
        box(f"Entry_Step_{step_i}", (x, center_y, -0.11 + (step_i-1)*0.20),
            (depth, width, height), concrete, collection, 0.035)

    # Tiny chapter insignia between upper central windows, intentionally
    # abstract because the photograph does not supply vector artwork.
    emblem_y = center_y
    for i, symbol in enumerate(("Π", "Κ", "Α")):
        oriented_front_text(f"Chapter_Emblem_Letter_{i+1}", symbol,
                            (front+0.10, emblem_y + (i-1)*0.48, 6.35), 0.38, white, collection)

    # Preserve the expected source object name for manifest compatibility and
    # carry audit-friendly model metadata in the blend.
    scene["building_id"] = BUILDING_ID
    scene["gis_source"] = "Purdue BuildingShapesZip4 FeatureServer/0, FID 790"
    scene["vertical_uncertainty"] = "Wall height 9.1 m and roof ridge 10.75 m are visual estimates; not measured."
    scene["facade_source"] = "Beta Phi chapter photo gallery: Completed Chapter House Renovations, Chapter House image (uploaded 2023-09)."
    # Useful camera and lighting are embedded in the individual library so the
    # evidence preview can be regenerated with this script.
    helpers = bpy.data.collections.new("Pike_Preview_Helpers")
    scene.collection.children.link(helpers)
    helper_layer = next(lc for lc in bpy.context.view_layer.layer_collection.children
                        if lc.collection == helpers)
    bpy.context.view_layer.active_layer_collection = helper_layer
    world = bpy.data.worlds.new("Pike_Studio_World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.62, 0.69, 0.75, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    scene.world = world
    bpy.ops.object.light_add(type="AREA", location=(front+38, center_y-4, 28))
    key = bpy.context.object
    key.name = "Preview_Key_Light"
    key.data.energy = 5200
    key.data.shape = "DISK"
    key.data.size = 24
    target = Vector(((minx+maxx)/2.0, center_y, 5.5))
    key.rotation_euler = (target - key.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(front+24, center_y+18, 16))
    fill = bpy.context.object
    fill.name = "Preview_Fill_Light"
    fill.data.energy = 1700
    fill.data.size = 18
    fill.rotation_euler = (target - fill.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.camera_add(location=(front+62, center_y-30, 18))
    camera = bpy.context.object
    camera.name = "Pike_Preview_Camera"
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 58
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW_PATH)
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.camera.data.lens = 50
    scene.render.image_settings.compression = 20

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.ops.render.render(write_still=True)
    print(f"Built {BUILDING_ID} with {len(collection.objects)} asset objects")
    print(f"GIS-derived bounds: X {minx:.3f}..{maxx:.3f}; Y {miny:.3f}..{maxy:.3f}; walls 9.1m, ridge 10.75m (estimated)")


if __name__ == "__main__":
    main()





