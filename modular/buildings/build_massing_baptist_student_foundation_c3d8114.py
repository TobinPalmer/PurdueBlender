"""Build the source-backed Baptist Student Foundation library asset.

Run from any working directory with Blender's background Python. The footprint
comes from Indiana's 2016-2020 LiDAR-derived buildings layer (feature 441814).
The asset intentionally stays in the manifest's existing campus coordinate
frame until the coordinator promotes it to a local-coordinate detailed asset.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


BUILDING_ID = "massing_baptist_student_foundation_c3d8114"
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
SCENE_NAME = f"Building_{BUILDING_ID}"
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "audit" / "baptist_student_foundation" / "sources"
FEATURE_PATH = SOURCES / "indiana_lidar_building_footprints_near_bsf_2026-10-25.geojson"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
PREVIEW_PATH = ROOT / "audit" / "baptist_student_foundation" / "preview.png"
TOP_PREVIEW_PATH = ROOT / "audit" / "baptist_student_foundation" / "roof_plan_view.png"
FEATURE_ID = 441814

# Vertical values are estimates from the Foundation's 2017 exterior photo and
# its 2023 roof imagery; no surveyed elevation or height field is published.
MAIN_EAVE_Z = 7.1
MAIN_RIDGE_Z = 8.9
ANNEX_EAVE_Z = 4.1
WALL_BASE_Z = 0.0


def mat(name: str, color: tuple[float, float, float, float], roughness=0.8):
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def add_mesh(name, verts, faces, material, collection, bevel=0.0, triangulate=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    if triangulate:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(mesh)
        bm.free()
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if bevel:
        mod = obj.modifiers.new("Soft masonry edges", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    return obj


def box(name, center, dims, material, collection, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def local_xy(web_mercator_xy):
    mx, my = web_mercator_xy
    radius = 6378137.0
    lon = math.degrees(mx / radius)
    lat = math.degrees(2.0 * math.atan(math.exp(my / radius)) - math.pi / 2.0)
    # Project rule: approximate meters east/north from 40.4274 N, 86.9137 W.
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    return (x, y)


def footprint_ring():
    raw = json.loads(FEATURE_PATH.read_text(encoding="utf-8"))
    feature = next(f for f in raw["features"] if f["properties"].get("objectid") == FEATURE_ID)
    ring = feature["geometry"]["coordinates"][0]
    xy = [local_xy(pt) for pt in ring]
    if xy[0] == xy[-1]:
        xy.pop()
    # Preserve source winding and registration; geometry is already close to
    # the source asset's centroid, so no fit-to-box scaling is applied.
    return xy


def create_walls(ring, collection, brick, interior):
    verts, faces, material_ids = [], [], []
    for i, (x1, y1) in enumerate(ring):
        x2, y2 = ring[(i + 1) % len(ring)]
        mid_y = (y1 + y2) * 0.5
        # Aerial plan shows a southern projecting stem. The 2017 exterior
        # photo shows a taller principal wing with a lower attached wing.
        top = ANNEX_EAVE_Z if mid_y < -104.5 else MAIN_EAVE_Z
        base = len(verts)
        verts.extend([(x1, y1, WALL_BASE_Z), (x2, y2, WALL_BASE_Z),
                      (x2, y2, top), (x1, y1, top)])
        faces.append((base, base + 1, base + 2, base + 3))
        material_ids.append(0)
    obj = add_mesh("Red brick exterior walls from LiDAR outline", verts, faces, brick, collection)
    # The orthophoto outline is T-shaped. The taller north wing continues over
    # the lower south stem, leaving a measured shared line rather than an open
    # notch; close the exposed second-storey face above the lower roof.
    add_mesh("Second-storey connector wall over south annex",
             [(-441.25, -104.39, ANNEX_EAVE_Z + 0.15),
              (-428.38, -102.20, ANNEX_EAVE_Z + 0.15),
              (-428.38, -102.20, MAIN_EAVE_Z),
              (-441.25, -104.39, MAIN_EAVE_Z)],
             [(0, 1, 2, 3)], brick, collection)
    return obj


def clip_polygon_y(poly, limit, keep_lower):
    """Clip a polygon to one side of a horizontal ridge line."""
    result = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ay, by = a[1], b[1]
        ain = ay <= limit if keep_lower else ay >= limit
        bin = by <= limit if keep_lower else by >= limit
        if ain:
            result.append(a)
        if ain != bin:
            t = (limit - ay) / (by - ay)
            result.append((a[0] + t * (b[0] - a[0]), limit))
    return result


def make_gable_roof(collection, roof_mat, ring):
    # Split the exact main-wing outline at an east-west ridge. This keeps the
    # roof footprint within the measured polygon despite its indented T shape.
    # The lower projecting south stem receives its own shallow roof.
    main = [ring[i] for i in (2, 3, 4, 5, 6, 7)]
    ridge_y = -96.9
    main_south, main_north = min(y for _, y in main), max(y for _, y in main)
    for name, polygon in (("South gable plane", clip_polygon_y(main, ridge_y, True)),
                          ("North gable plane", clip_polygon_y(main, ridge_y, False))):
        verts = []
        for x, y in polygon:
            if abs(y - ridge_y) < 1e-5:
                z = MAIN_RIDGE_Z
            else:
                edge_y = main_south if y < ridge_y else main_north
                z = MAIN_EAVE_Z + (MAIN_RIDGE_Z - MAIN_EAVE_Z) * abs(y - edge_y) / abs(ridge_y - edge_y)
            verts.append((x, y, z))
        add_mesh(name, verts, [tuple(range(len(verts)))], roof_mat, collection, triangulate=True)

    annex = [ring[i] for i in (0, 1, 2, 7)]
    verts = [(x, y, ANNEX_EAVE_Z + max(0.0, (y + 112.5)) * 0.025) for x, y in annex]
    add_mesh("Lower annex roof", verts, [tuple(range(len(verts)))], roof_mat, collection, triangulate=True)

    # The photographed principal volume has a gable end at either end of its
    # long ridge; close those wall triangles instead of leaving open roof voids.
    west, east = min(x for x, _ in main), max(x for x, _ in main)
    for name, x in (("West gable end", west), ("East gable end", east)):
        add_mesh(name, [(x, main_south, MAIN_EAVE_Z), (x, main_north, MAIN_EAVE_Z),
                        (x, ridge_y, MAIN_RIDGE_Z)], [(0, 1, 2)],
                 mat("Gable brick", (0.34, 0.12, 0.075, 1)), collection)


def add_window(collection, center, width, height, tangent_angle, brick_trim, glass, muntin):
    x, y, z = center
    angle = tangent_angle
    nx, ny = math.sin(angle), -math.cos(angle)
    # Thick pale stone trim and dark glass sit just outside the wall plane.
    box("Window stone surround", (x + nx * 0.04, y + ny * 0.04, z), (width + 0.24, 0.16, height + 0.24),
        brick_trim, collection, angle)
    box("Window glazing", (x + nx * 0.14, y + ny * 0.14, z), (width, 0.05, height),
        glass, collection, angle)
    box("Window vertical mullion", (x + nx * 0.18, y + ny * 0.18, z), (0.045, 0.045, height),
        muntin, collection, angle)
    box("Window horizontal mullion", (x + nx * 0.18, y + ny * 0.18, z), (width, 0.045, 0.045),
        muntin, collection, angle)


def decorate_facades(ring, collection, trim, glass, metal, door_mat):
    # Projecting rectangular windows are evenly spaced along each documented
    # facade length. Facade count/size is an illustrative reading of the dated
    # exterior photo, not a measured schedule.
    for i, (a, b) in enumerate(zip(ring, ring[1:] + ring[:1])):
        x1, y1 = a; x2, y2 = b
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length < 5.2:
            continue
        angle = math.atan2(dy, dx)
        # Outward normal for the counterclockwise footprint outline.
        nx, ny = dy / length, -dx / length
        mid_y = (y1 + y2) * 0.5
        low_wing = mid_y < -104.5
        count = max(1, min(7, int(length // 3.5)))
        for row_z in ([1.55] if low_wing else [1.55, 4.55]):
            for j in range(count):
                t = (j + 1) / (count + 1)
                px = x1 + dx * t + nx * 0.10
                py = y1 + dy * t + ny * 0.10
                add_window(collection, (px, py, row_z), 1.2, 1.45, angle, trim, glass, metal)

    # Two upper windows in the wall overlooking the low attached stem.
    for x in (-437.3, -432.1):
        add_window(collection, (x, -103.85, 5.65), 1.25, 1.45, 0.0, trim, glass, metal)

    # West-facing primary entrance with a small canopy, inset double doors,
    # steps and side lights; the entrance location is estimated from the 2017
    # street photograph because no dimensioned plan is publicly available.
    west_x = min(x for x, _ in ring)
    door_y = -99.3
    entry_angle = math.pi / 2
    box("Stone entry surround", (west_x - 0.04, door_y, 1.42), (2.45, 0.24, 2.84), trim, collection, entry_angle)
    box("Recessed double entrance doors", (west_x - 0.18, door_y, 1.32), (1.78, 0.09, 2.58), door_mat, collection, entry_angle)
    for dy in [-0.48, 0.48]:
        box("Door glass lite", (west_x - 0.235, door_y + dy, 1.85), (0.54, 0.035, 1.12), glass, collection, entry_angle)
    box("Entry canopy", (west_x - 0.85, door_y, 2.9), (3.1, 1.55, 0.16), metal, collection, entry_angle)
    for step in range(3):
        box("Entry step", (west_x - 0.38 - step * 0.35, door_y, 0.12 + step * 0.22),
            (2.45 + step * 0.32, 0.55, 0.20), trim, collection, entry_angle)


def setup_and_render(collection, scene, brick, trim, roof):
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.23, 0.25, 0.28, 1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.45
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    center = Vector((-433.6, -101.1, 0))
    bpy.ops.object.camera_add(location=(center.x - 50, center.y - 58, 37))
    camera = bpy.context.object
    camera.name = "Preview camera"
    camera.rotation_euler = (Vector((center.x, center.y, 3.5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 58
    scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(center.x - 10, center.y - 30, 35))
    key = bpy.context.object; key.name = "Preview key"; key.data.energy = 14500; key.data.shape = "DISK"; key.data.size = 30
    bpy.ops.object.light_add(type="AREA", location=(center.x + 32, center.y + 10, 20))
    fill = bpy.context.object; fill.name = "Preview fill"; fill.data.energy = 6500; fill.data.size = 20
    scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    camera.location = (center.x, center.y, 58)
    camera.rotation_euler = (0.0, 0.0, 0.0)
    camera.data.ortho_scale = 38
    scene.render.filepath = str(TOP_PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    for obj in (camera, key, fill):
        bpy.data.objects.remove(obj, do_unlink=True)


def main():
    # Clean a default Blender startup file and create only the assigned asset.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        if coll.name != "Collection":
            bpy.data.collections.remove(coll)
    coll = bpy.data.collections.get(COLLECTION_NAME) or bpy.data.collections.new(COLLECTION_NAME)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    for scene in list(bpy.data.scenes):
        if scene != bpy.context.scene:
            bpy.data.scenes.remove(scene)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    # Only remove default Collection after making sure it is empty.
    default = bpy.data.collections.get("Collection")
    if default and not default.objects and not default.children:
        bpy.data.collections.remove(default)

    brick = mat("Warm red-brown brick (estimated)", (0.34, 0.12, 0.075, 1))
    trim = mat("Light stone trim (estimated)", (0.68, 0.62, 0.50, 1))
    roof = mat("Dark gray shingle roof (estimated)", (0.13, 0.15, 0.17, 1))
    glass = mat("Blue gray window glass", (0.07, 0.13, 0.17, 1), 0.23)
    metal = mat("Painted dark metal", (0.15, 0.18, 0.20, 1))
    door_mat = mat("Dark entry doors", (0.16, 0.10, 0.065, 1))

    ring = footprint_ring()
    create_walls(ring, coll, brick, trim)
    make_gable_roof(coll, roof, ring)
    decorate_facades(ring, coll, trim, glass, metal, door_mat)

    scene.render.resolution_percentage = 75
    setup_and_render(coll, scene, brick, trim, roof)
    # Keep the preview full size even though render setup uses percentage for
    # faster deterministic output in this validation workflow.
    scene.render.resolution_percentage = 100
    scene.render.filepath = "//"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    print(f"Saved {ASSET_PATH} with {len(coll.objects)} objects")


if __name__ == "__main__":
    main()
