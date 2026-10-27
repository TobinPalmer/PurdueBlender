"""Build a source-backed detailed library for Pi Kappa Phi, Omega Chapter.

Footprint and campus coordinates come from Purdue GIS FID 799 (EPSG:4326),
transformed with the project approximation documented in modular/AGENTS.md.
Exterior massing and the west-facing entrance composition are estimates based
on the post-1987 house shown in the chapter's 2019 and 2023 photographs.
"""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular" / "buildings" / "massing_pi_kappa_phi_50e4645.blend"
EVIDENCE = ROOT / "audit" / "pi_kappa_phi"
GIS_PATH = EVIDENCE / "sources" / "purdue_gis_FID799_wgs84.json"
COLLECTION_NAME = "Asset_massing_pi_kappa_phi_50e4645"
SCENE_NAME = "Building_massing_pi_kappa_phi_50e4645"

LAT0 = 40.4274
LON0 = -86.9137


def campus_xy(lon, lat):
    return (
        (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
        (lat - 40.4274) * 111040.0,
    )


def material(name, color, roughness=0.82):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def mesh_obj(name, vertices, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def box(name, center, size, mat, collection):
    cx, cy, cz = center
    sx, sy, sz = size
    verts = [
        (cx - sx / 2, cy - sy / 2, cz - sz / 2),
        (cx + sx / 2, cy - sy / 2, cz - sz / 2),
        (cx + sx / 2, cy + sy / 2, cz - sz / 2),
        (cx - sx / 2, cy + sy / 2, cz - sz / 2),
        (cx - sx / 2, cy - sy / 2, cz + sz / 2),
        (cx + sx / 2, cy - sy / 2, cz + sz / 2),
        (cx + sx / 2, cy + sy / 2, cz + sz / 2),
        (cx - sx / 2, cy + sy / 2, cz + sz / 2),
    ]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_obj(name, verts, faces, mat, collection)


def gable_roof(name, x0, x1, y0, y1, eave_z, ridge_z, mat, collection, overhang=0.22, gable_mat=None):
    """A pitched roof with its ridge running east-west and gable ends facing west/east."""
    x0 -= overhang
    x1 += overhang
    y0 -= overhang
    y1 += overhang
    ym = (y0 + y1) / 2
    verts = [
        (x0, y0, eave_z), (x0, y1, eave_z), (x0, ym, ridge_z),
        (x1, y0, eave_z), (x1, y1, eave_z), (x1, ym, ridge_z),
    ]
    faces = [(0, 3, 5, 2), (2, 5, 4, 1), (0, 2, 1), (3, 4, 5), (0, 1, 4, 3)]
    obj = mesh_obj(name, verts, faces, mat, collection)
    if gable_mat:
        obj.data.materials.append(gable_mat)
        for poly in obj.data.polygons:
            if poly.index in (2, 3):
                poly.material_index = 1
    return obj


def arch_panel(name, x, y_center, z_bottom, width, straight_height, mat, collection, depth=0.035):
    """Shallow arched facade panel in the west-facing elevation (YZ plane)."""
    radius = width / 2
    points = [(-radius, 0), (-radius, straight_height)]
    for i in range(1, 13):
        angle = math.pi - math.pi * i / 12
        points.append((radius * math.cos(angle), straight_height + radius * math.sin(angle)))
    points.append((radius, 0))
    verts = []
    for xx in (x, x + depth):
        verts.extend((xx, y_center + dy, z_bottom + dz) for dy, dz in points)
    n = len(points)
    faces = [tuple(range(n)), tuple(range(n, 2 * n))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    return mesh_obj(name, verts, faces, mat, collection)


def window(name, x, y, z, width, height, glass, trim, collection, depth=0.07):
    # Four separate trim bars leave the dark glazing visible in the center.
    box(name + " glazing", (x - depth * 0.58, y, z), (0.035, width, height), glass, collection)
    bar = 0.10
    box(name + " frame left", (x, y - width / 2 - bar / 2, z), (depth, bar, height + 2 * bar), trim, collection)
    box(name + " frame right", (x, y + width / 2 + bar / 2, z), (depth, bar, height + 2 * bar), trim, collection)
    box(name + " frame sill", (x, y, z - height / 2 - bar / 2), (depth, width, bar), trim, collection)
    box(name + " frame lintel", (x, y, z + height / 2 + bar / 2), (depth, width, bar), trim, collection)
    box(name + " mullion V", (x - depth * 0.82, y, z), (0.045, 0.055, height), trim, collection)
    box(name + " mullion H", (x - depth * 0.83, y, z), (0.045, width, 0.055), trim, collection)


def set_material_slots(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def render_view(scene, out_path, camera_location, target, lens=52):
    camera_data = bpy.data.cameras.new("_preview_camera_data")
    camera = bpy.data.objects.new("_preview_camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = camera_location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens
    scene.camera = camera

    light_data = bpy.data.lights.new("_preview_area_data", "AREA")
    light = bpy.data.objects.new("_preview_area", light_data)
    scene.collection.objects.link(light)
    light.location = (306, -79, 27)
    light.data.energy = 5000
    light.data.shape = "DISK"
    light.data.size = 19

    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(out_path)
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    background = nodes.get("Background")
    output = nodes.get("World Output")
    scene.world.node_tree.links.clear()
    scene.world.node_tree.links.new(background.outputs[0], output.inputs[0])
    background.inputs["Color"].default_value = (0.62, 0.66, 0.70, 1.0)
    background.inputs["Strength"].default_value = 0.9
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.2
    scene.view_settings.gamma = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    bpy.ops.render.render(write_still=True)

    scene.camera = None
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.objects.remove(light, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    bpy.data.lights.remove(light_data)


def main():
    with open(GIS_PATH, "r", encoding="utf-8") as f:
        gis = json.load(f)
    feature = gis["features"][0]
    attrs = feature["attributes"]
    assert attrs["FID"] == 799 and attrs["BUILDING_N"] == "Pi Kappa Phi"
    assert attrs["ADDRESS"].lower().startswith("330 n grant")

    scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
    bpy.context.window.scene = scene
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(collection)
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    stone = material("Pi Kappa Phi | pale limestone", (0.42, 0.40, 0.35))
    stone_trim = material("Pi Kappa Phi | limestone trim", (0.55, 0.52, 0.45))
    stone_joint = material("Pi Kappa Phi | stone joint shadow", (0.31, 0.30, 0.27))
    slate = material("Pi Kappa Phi | charcoal slate", (0.075, 0.09, 0.10))
    glass = material("Pi Kappa Phi | dark glazing", (0.018, 0.035, 0.045), 0.28)
    dark = material("Pi Kappa Phi | recessed entrance", (0.025, 0.033, 0.037), 0.45)

    ring = feature["geometry"]["rings"][0]
    footprint = [campus_xy(lon, lat) for lon, lat in ring]
    min_x = min(x for x, y in footprint)
    max_x = max(x for x, y in footprint)
    min_y = min(y for x, y in footprint)
    max_y = max(y for x, y in footprint)
    west, east = min_x, max_x
    south, north = min_y, max_y
    width_x, length_y = east - west, north - south
    wall_top = 9.4  # Estimated from current exterior photographs; no measured elevation found.

    # Perimeter walls follow the GIS polygon exactly; the concave footprint is preserved.
    vertices = []
    for x, y in footprint:
        vertices.append((x, y, 0.0))
    for x, y in footprint:
        vertices.append((x, y, wall_top))
    n = len(footprint)
    faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n - 1)]
    walls = mesh_obj("Pi Kappa Phi", vertices, faces, stone, collection)
    walls["source_feature_id"] = 799
    walls["vertical_height_status"] = "estimated from chapter photographs; not surveyed"

    # The rebuilt chapter house has two main occupied levels, a visible attic level,
    # slate gables and a central parapet/dormer roof section in the official photos.
    # These segments are a photo-guided approximation; exact roof framing is unknown.
    center_y0 = south + length_y * 0.32
    center_y1 = south + length_y * 0.70
    gable_roof("Pi Kappa Phi | south front gable", west, min(east, west + width_x * 0.67), south, center_y0 + 0.4, wall_top, 14.0, slate, collection, gable_mat=stone)
    gable_roof("Pi Kappa Phi | north front gable", west, min(east, west + width_x * 0.67), center_y1 - 0.35, north, wall_top, 12.4, slate, collection, gable_mat=stone)
    gable_roof("Pi Kappa Phi | east wing gable", west + width_x * 0.64, east, south + 1.2, north - 1.2, wall_top, 13.4, slate, collection, gable_mat=stone)
    box("Pi Kappa Phi | center roof parapet", (west + width_x * 0.34, (center_y0 + center_y1) / 2, 10.0), (width_x * 0.69, center_y1 - center_y0, 1.2), stone_trim, collection)
    box("Pi Kappa Phi | central flat roof", (west + width_x * 0.34, (center_y0 + center_y1) / 2, 10.75), (width_x * 0.74, center_y1 - center_y0 + 0.45, 0.28), slate, collection)

    # Four dormer forms rise above the central parapet, matching the chapter photo.
    for i, y in enumerate([center_y0 + 0.85, center_y0 + 2.4, center_y1 - 2.4, center_y1 - 0.85], 1):
        x = west + 0.45
        box(f"Pi Kappa Phi | dormer {i} stone", (x, y, 11.55), (0.75, 0.95, 1.55), stone, collection)
        window(f"Pi Kappa Phi | dormer {i}", x - 0.40, y, 11.65, 0.56, 0.86, glass, stone_trim, collection, 0.05)
        gable_roof(f"Pi Kappa Phi | dormer {i} roof", x - 0.48, x + 0.5, y - 0.58, y + 0.58, 12.3, 12.85, slate, collection, 0.08)

    # West-facing entrance: paired round-headed stone portals, shown in the 2019 photo.
    front_x = west - 0.11
    entrance_y = (south + north) / 2
    for i, offset in enumerate((-0.92, 0.92), 1):
        yc = entrance_y + offset
        arch_panel(f"Pi Kappa Phi | entrance arch {i}", front_x, yc, 0.2, 1.72, 2.12, stone_trim, collection)
        arch_panel(f"Pi Kappa Phi | recessed door {i}", front_x - 0.045, yc, 0.32, 1.34, 1.92, dark, collection, 0.025)
        box(f"Pi Kappa Phi | portal jamb left {i}", (front_x - 0.08, yc - 0.82, 1.2), (0.16, 0.15, 2.05), stone_trim, collection)
        box(f"Pi Kappa Phi | portal jamb right {i}", (front_x - 0.08, yc + 0.82, 1.2), (0.16, 0.15, 2.05), stone_trim, collection)

    # Repeated dark rectangular glazing, with the central entrances kept clear.
    facade_y = [south + 1.25, south + 4.2, south + 7.0, south + 10.0,
                south + 15.0, south + 18.2, north - 1.4]
    for idx, y in enumerate(facade_y, 1):
        if abs(y - entrance_y) < 2.15:
            continue
        window(f"Pi Kappa Phi | west ground window {idx}", front_x, y, 4.0, 1.12, 1.75, glass, stone_trim, collection)
        window(f"Pi Kappa Phi | west upper window {idx}", front_x, y, 7.15, 1.12, 1.68, glass, stone_trim, collection)

    # Side and inner-courtyard windows add the rhythm visible in the 2023 side view.
    east_front = east + 0.07
    for idx, y in enumerate([south + 3.0, south + 6.4, south + 9.8, south + 13.2, south + 16.6, north - 3.0], 1):
        window(f"Pi Kappa Phi | east ground window {idx}", east_front, y, 4.0, 1.05, 1.65, glass, stone_trim, collection)
        window(f"Pi Kappa Phi | east upper window {idx}", east_front, y, 7.15, 1.05, 1.6, glass, stone_trim, collection)

    # Light stone bands echo the horizontal courses and floor lines in the photos.
    for z in (0.55, 3.35, 6.55, 9.35):
        box(f"Pi Kappa Phi | west course at {z:.2f}m", (front_x + 0.005, (south + north) / 2, z), (0.10, length_y - 0.35, 0.075), stone_trim, collection)

    # Fine, shallow joints suggest the visible ashlar courses without claiming a
    # surveyed stone module. Windows and portals sit forward of these seams.
    joint_vertices = []
    joint_faces = []

    def append_joint(cx, cy, cz, dx, dy, dz):
        base = len(joint_vertices)
        x0, x1 = cx - dx / 2, cx + dx / 2
        y0, y1 = cy - dy / 2, cy + dy / 2
        z0, z1 = cz - dz / 2, cz + dz / 2
        joint_vertices.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                               (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        joint_faces.extend([tuple(base + i for i in face) for face in
                            ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))])

    joint_x = west - 0.025
    joint_length = length_y - 0.35
    rows = [0.85 + i * 0.56 for i in range(15)]
    for row, z in enumerate(rows):
        append_joint(joint_x, (south + north) / 2, z, 0.025, joint_length, 0.018)
        offset = 0.55 if row % 2 else 0.0
        for y in [south + 0.6 + offset + i * 1.1 for i in range(22)]:
            if y < north - 0.35:
                append_joint(joint_x, y, z + 0.27, 0.025, 0.016, 0.52)
    mesh_obj("Pi Kappa Phi | photo-guided ashlar joints", joint_vertices, joint_faces, stone_joint, collection)

    # Add simple gable attic lights on the visible front gables.
    for i, y in enumerate((south + (center_y0 - south) * 0.53, center_y1 + (north - center_y1) * 0.47), 1):
        window(f"Pi Kappa Phi | front attic window {i}", front_x - 0.10, y, 11.05, 0.82, 1.1, glass, stone_trim, collection, 0.05)

    # Simple threshold and understated foundation courses.
    box("Pi Kappa Phi | front entrance stoop", (front_x - 0.35, entrance_y, 0.14), (0.72, 4.2, 0.28), stone_trim, collection)
    box("Pi Kappa Phi | foundation plinth west", (west + 0.03, (south + north) / 2, 0.3), (0.12, length_y - 0.15, 0.45), stone_trim, collection)

    # Project output must remain a directly linked campus-coordinate massing library.
    for obj in collection.objects:
        obj["building_id"] = "massing_pi_kappa_phi_50e4645"
    scene.render.resolution_percentage = 100
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    render_view(scene, EVIDENCE / "preview_front.png", (west - 33, (south + north) / 2, 11.5), ((west + east) / 2, (south + north) / 2, 6.2), 48)
    render_view(scene, EVIDENCE / "preview_aerial.png", (east + 27, south + 27, 33), ((west + east) / 2, (south + north) / 2, 5.5), 52)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    print("PI_KAPPA_PHI_BUILD", json.dumps({"collection": collection.name, "object_count": len(collection.objects), "bbox": [west, east, south, north, 0.0, 14.0], "gis_area_m2_planar_approx": None}))


if __name__ == "__main__":
    main()
