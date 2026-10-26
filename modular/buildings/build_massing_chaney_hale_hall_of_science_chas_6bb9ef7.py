"""Build the CHAS massing library from its official Purdue GIS footprint.

The footprint and building identity come from Purdue GIS FID 945. Height and
facade treatments are illustrative estimates based on the cited photographs.
Run with Blender 4.5: blender -b --python this_file.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_chaney_hale_hall_of_science_chas_6bb9ef7"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "chaney_hale_hall_of_science_chas" / "sources" / "purdue_gis_fid945_live.json"
EVIDENCE_DIR = ROOT / "audit" / "chaney_hale_hall_of_science_chas"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
OBJECT_NAME = "Chaney-Hale Hall of Science (CHAS)"
HEIGHT_M = 16.0  # Four stories; estimate only, based on photos and prior massing.
OVERHANG_M = 0.72  # Visually estimated from Purdue/contractor exterior photos.
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137


def local_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def make_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.75) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def append_quad(verts: list[tuple[float, float, float]], faces: list[tuple[int, ...]], mats: list[int], points, mat_index: int) -> None:
    start = len(verts)
    verts.extend(tuple(float(c) for c in p) for p in points)
    faces.append(tuple(range(start, start + len(points))))
    mats.append(mat_index)


def render_preview(scene: bpy.types.Scene, mesh_obj: bpy.types.Object) -> None:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.30, 0.35, 0.42, 1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.035, 0.045, 0.06)

    center = Vector((sum(v.co.x for v in mesh_obj.data.vertices) / len(mesh_obj.data.vertices),
                     sum(v.co.y for v in mesh_obj.data.vertices) / len(mesh_obj.data.vertices),
                     HEIGHT_M / 2))
    camera_data = bpy.data.cameras.new("CHAS preview camera")
    camera = bpy.data.objects.new("CHAS preview camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((118, -143, 12))
    direction = center - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera_data.lens = 90
    scene.camera = camera

    light_data = bpy.data.lights.new("CHAS preview key", "AREA")
    light = bpy.data.objects.new("CHAS preview key", light_data)
    scene.collection.objects.link(light)
    light.location = center + Vector((-65, -95, 110))
    light_data.energy = 36000
    light_data.shape = "DISK"
    light_data.size = 75
    light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
    sun_data = bpy.data.lights.new("CHAS preview sun", "SUN")
    sun = bpy.data.objects.new("CHAS preview sun", sun_data)
    scene.collection.objects.link(sun)
    sun_data.energy = 2.5
    sun.rotation_euler = (center - (center + Vector((70, -80, 100)))).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(EVIDENCE_DIR / "preview.png")
    bpy.ops.render.render(write_still=True)

    camera.location = center + Vector((0, 0, 160))
    camera.rotation_euler = (0, 0, 0)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 92
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.filepath = str(EVIDENCE_DIR / "topdown.png")
    bpy.ops.render.render(write_still=True)


def build() -> None:
    with SOURCE_PATH.open("r", encoding="utf-8") as f:
        response = json.load(f)
    feature = next(f for f in response["features"] if f["attributes"].get("FID") == 945)
    assert feature["attributes"]["BLDG_ABBR"] == "CHAS"
    assert feature["attributes"]["BUILDING_N"] == "Chaney-Hale Hall of Science"
    ring = feature["geometry"]["rings"][0]
    footprint = [local_xy(lon, lat) for lon, lat in ring]
    if footprint[0] == footprint[-1]:
        footprint.pop()
    assert len(footprint) > 10
    area2 = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(footprint, footprint[1:] + footprint[:1]))
    centroid = (sum(p[0] for p in footprint) / len(footprint), sum(p[1] for p in footprint) / len(footprint))

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset_collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset_collection)
    default = bpy.data.collections.get("Collection")
    if default and len(default.objects) == 0:
        bpy.data.collections.remove(default)

    mats = [
        make_material("CHAS - red brick", (0.36, 0.105, 0.060, 1)),
        make_material("CHAS - dark ground brick", (0.12, 0.14, 0.15, 1)),
        make_material("CHAS - blue gray glazing", (0.10, 0.24, 0.31, 1), 0.22),
        make_material("CHAS - limestone bands", (0.67, 0.62, 0.51, 1)),
        make_material("CHAS - wood soffit and roof", (0.22, 0.12, 0.065, 1)),
    ]
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    indices: list[int] = []
    n = len(footprint)
    outward_sign = 1 if area2 > 0 else -1

    # Full footprint shell, split into floor bands so the massing remains solid.
    floor_levels = [0.0, 3.8, 7.8, 11.8, HEIGHT_M - 0.48]
    for i, (a, b) in enumerate(zip(footprint, footprint[1:] + footprint[:1])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 1e-6:
            continue
        nx, ny = outward_sign * dy / length, outward_sign * -dx / length
        for low, high in zip(floor_levels, floor_levels[1:]):
            append_quad(verts, faces, indices,
                       [(a[0], a[1], low), (b[0], b[1], low),
                        (b[0], b[1], high), (a[0], a[1], high)],
                       1 if low == 0.0 else 0)

        # Architectural photos show a dark transparent ground floor and glass
        # upper teaching floors, separated by brick piers and pale belt courses.
        if length >= 7.0:
            for low, high in [(0.42, 3.46), (4.15, 7.38), (8.16, 11.38), (12.17, HEIGHT_M - 0.88)]:
                usable = max(0.0, length - 1.0)
                bay = 2.45
                count = max(1, int(usable // (bay + 0.42)))
                total = count * bay + (count - 1) * 0.42
                start = (length - total) / 2
                for j in range(count):
                    s0 = start + j * (bay + 0.42)
                    s1 = s0 + bay
                    p0 = (a[0] + dx * s0 / length + nx * 0.05, a[1] + dy * s0 / length + ny * 0.05)
                    p1 = (a[0] + dx * s1 / length + nx * 0.05, a[1] + dy * s1 / length + ny * 0.05)
                    append_quad(verts, faces, indices,
                               [(p0[0], p0[1], low), (p1[0], p1[1], low),
                                (p1[0], p1[1], high), (p0[0], p0[1], high)], 2)

            # Pale horizontal bands visible in the 2020 exterior photos.
            for z in [3.72, 7.72, 11.72, HEIGHT_M - 0.54]:
                p0 = (a[0] + nx * 0.10, a[1] + ny * 0.10)
                p1 = (b[0] + nx * 0.10, b[1] + ny * 0.10)
                append_quad(verts, faces, indices,
                           [(p0[0], p0[1], z - 0.12), (p1[0], p1[1], z - 0.12),
                            (p1[0], p1[1], z + 0.12), (p0[0], p0[1], z + 0.12)], 3)

    # Thin, slightly oversized flat roof cap and fascia model the deep timber
    # soffit visible in the official Purdue and project-contractor photographs.
    cap = []
    for x, y in footprint:
        vx, vy = x - centroid[0], y - centroid[1]
        d = math.hypot(vx, vy) or 1.0
        cap.append((x + vx / d * OVERHANG_M, y + vy / d * OVERHANG_M))
    z0, z1 = HEIGHT_M - 0.5, HEIGHT_M
    for i, (a, b) in enumerate(zip(cap, cap[1:] + cap[:1])):
        oa, ob = footprint[i], footprint[(i + 1) % n]
        append_quad(verts, faces, indices,
                   [(oa[0], oa[1], z0), (ob[0], ob[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], 4)
    start = len(verts)
    verts.extend((x, y, z1) for x, y in cap)
    faces.append(tuple(range(start, start + n)))
    indices.append(4)

    mesh = bpy.data.meshes.new(f"{ASSET_ID}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    mesh.update()
    for poly, material_index in zip(mesh.polygons, indices):
        poly.material_index = material_index
    obj = bpy.data.objects.new(OBJECT_NAME, mesh)
    asset_collection.objects.link(obj)
    obj["asset_id"] = ASSET_ID
    obj["footprint_source"] = "Purdue BuildingShapesZip4 FID 945, EPSG:4326, converted with project local approximation"
    obj["height_status"] = "16 m illustrative estimate; Purdue identifies four stories, but no elevation/height source found"
    obj["facade_status"] = "photo-based massing cues; exact bay dimensions and hidden elevations unverified"

    # Save portable asset first. Preview-only camera and light are kept outside
    # the exported library collection and removed before the final save.
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    render_preview(scene, obj)
    bpy.data.objects.remove(scene.camera, do_unlink=True)
    for object_name in ["CHAS preview key", "CHAS preview sun"]:
        o = bpy.data.objects.get(object_name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))


if __name__ == "__main__":
    build()
