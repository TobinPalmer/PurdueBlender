"""Build the Stone Hall (STON) massing library from its official Purdue GIS shell.

Run from the repository root with Blender 4.5+:
  blender -b --python modular/buildings/build_massing_stone_hall_ston_d3f479a.py

The script reads the preserved GIS query in audit/massing_stone_hall_ston_d3f479a/sources.
It writes only Stone Hall's assigned asset and evidence folder.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


BUILDING_ID = "massing_stone_hall_ston_d3f479a"
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
SCENE_NAME = f"Building_{BUILDING_ID}"
OBJECT_NAME = "Stone Hall (STON)"
REPO = Path(__file__).resolve().parents[2]
AUDIT = REPO / "audit" / BUILDING_ID
SOURCE_JSON = AUDIT / "sources" / "purdue_building_gis_fid240_ston_4326.json"
ASSET_PATH = REPO / "modular" / "buildings" / f"{BUILDING_ID}.blend"
PREVIEW_PATH = AUDIT / "preview" / "stone_hall_isometric.png"
FRONT_PREVIEW_PATH = AUDIT / "preview" / "stone_hall_front.png"
TOP_PREVIEW_PATH = AUDIT / "preview" / "stone_hall_top.png"
REPORT_PATH = AUDIT / "build_validation.json"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
METERS_PER_LON_DEG = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
METERS_PER_LAT_DEG = 111040.0
GIS_EXTRUSION_FT = 45.0
FT_TO_M = 0.3048
# The source layer does not declare units for Extrution. 45 ft is a documented
# interpretation for a visualization estimate, not a verified roof elevation.
HEIGHT_M_ESTIMATE = GIS_EXTRUSION_FT * FT_TO_M


def read_source():
    with SOURCE_JSON.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if len(data.get("features", [])) != 1:
        raise RuntimeError(f"Expected exactly one GIS feature, got {len(data.get('features', []))}")
    feature = data["features"][0]
    attrs = feature["attributes"]
    if attrs.get("FID") != 240 or attrs.get("BLDG_ABBR") != "STON" or attrs.get("BUILDING_N") != "Winthrop E. Stone Hall":
        raise RuntimeError(f"GIS identity mismatch: {attrs.get('FID')}, {attrs.get('BLDG_ABBR')}, {attrs.get('BUILDING_N')}")
    ring = feature["geometry"]["rings"][0]
    points = []
    for lon, lat in ring:
        x = (lon - ORIGIN_LON) * METERS_PER_LON_DEG
        y = (lat - ORIGIN_LAT) * METERS_PER_LAT_DEG
        point = (x, y)
        if not points or math.dist(points[-1], point) > 1e-6:
            points.append(point)
    if len(points) > 2 and math.dist(points[0], points[-1]) < 1e-6:
        points.pop()
    if len(points) < 3:
        raise RuntimeError("GIS source ring has fewer than three distinct points")
    return attrs, points


def polygon_area(points):
    return 0.5 * sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points)))


def new_material(name, color, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def make_mesh_object(name, collection, materials):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for mat in materials:
        mesh.materials.append(mat)
    verts, faces, material_ids = [], [], []

    def add_box(center, tangent, normal, width, depth, height, material_id):
        c = Vector((center[0], center[1], center[2]))
        t = Vector((tangent[0], tangent[1], 0.0)).normalized()
        n = Vector((normal[0], normal[1], 0.0)).normalized()
        base = len(verts)
        for zsign in (-1, 1):
            for tsign, nsign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                p = c + t * (tsign * width * 0.5) + n * (nsign * depth * 0.5) + Vector((0, 0, zsign * height * 0.5))
                verts.append(tuple(p))
        box_faces = [(base + 0, base + 1, base + 2, base + 3),
                     (base + 4, base + 7, base + 6, base + 5),
                     (base + 0, base + 4, base + 5, base + 1),
                     (base + 1, base + 5, base + 6, base + 2),
                     (base + 2, base + 6, base + 7, base + 3),
                     (base + 3, base + 7, base + 4, base + 0)]
        faces.extend(box_faces)
        material_ids.extend([material_id] * len(box_faces))

    return obj, verts, faces, material_ids, add_box


def append_mesh(obj, verts, faces, material_ids, polygon, height, materials_count):
    n = len(polygon)
    verts.extend((x, y, 0.0) for x, y in polygon)
    verts.extend((x, y, height) for x, y in polygon)
    faces.append(tuple(range(n - 1, -1, -1)))
    material_ids.append(3)  # roof material
    faces.append(tuple(range(n, 2 * n)))
    material_ids.append(3)
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
        material_ids.append(0)  # brick shell


def build():
    attrs, polygon = read_source()
    signed_area = polygon_area(polygon)
    if signed_area < 0:
        polygon.reverse()
        signed_area = -signed_area

    # Create a clean single-building library scene. The export collection contains
    # one joined mesh; camera, lights, and preview ground stay outside it.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    staging = bpy.data.collections.new("Preview_Only_StoneHall")
    scene.collection.children.link(staging)

    brick = new_material("STON - reddish brown brick, archival-photo interpretation", (0.25, 0.16, 0.12))
    trim = new_material("STON - light stone trim, archival-photo interpretation", (0.66, 0.62, 0.53))
    glass = new_material("STON - dark glazing, archival-photo interpretation", (0.075, 0.13, 0.16), roughness=0.28, metallic=0.12)
    roof = new_material("STON - simple flat roof estimate", (0.26, 0.27, 0.27))
    materials = [brick, trim, glass, roof]
    obj, verts, faces, mids, add_box = make_mesh_object(OBJECT_NAME, collection, materials)
    append_mesh(obj, verts, faces, mids, polygon, HEIGHT_M_ESTIMATE, len(materials))

    edge_data = []
    for i, a in enumerate(polygon):
        b = polygon[(i + 1) % len(polygon)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 1e-3:
            continue
        tangent = (dx / length, dy / length)
        # polygon is CCW, so its outward normal is the right-hand normal.
        normal = (tangent[1], -tangent[0])
        midpoint = ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
        edge_data.append((length, tangent, normal, midpoint))

    # Use the four supported GIS floor elevations where they exist; the values
    # are interpreted as feet solely to make an illustrative 4-level facade.
    floor_fields = ["F01", "F02", "F03", "F04"]
    floors_ft = [float(attrs[k]) for k in floor_fields if isinstance(attrs.get(k), (int, float)) and float(attrs[k]) > 0]
    floor_levels = [v * FT_TO_M for v in floors_ft]
    if not floor_levels:
        floor_levels = [HEIGHT_M_ESTIMATE * 0.18, HEIGHT_M_ESTIMATE * 0.42, HEIGHT_M_ESTIMATE * 0.66, HEIGHT_M_ESTIMATE * 0.87]
    window_centers = [min(HEIGHT_M_ESTIMATE - 1.0, z + (1.45 if j < len(floor_levels) - 1 else 0.95)) for j, z in enumerate(floor_levels)]
    window_heights = [2.25 if j < len(window_centers) - 1 else 1.2 for j in range(len(window_centers))]
    long_edges = [edge for edge in edge_data if edge[0] >= 14.0]
    main_edge = max(long_edges, key=lambda e: e[0]) if long_edges else max(edge_data, key=lambda e: e[0])

    for length, tangent, normal, midpoint in long_edges:
        bay_count = max(3, round(length / 4.1))
        bay_spacing = length / bay_count
        for row, (window_z, window_h) in enumerate(zip(window_centers, window_heights)):
            for bay in range(bay_count):
                offset = -length * 0.5 + bay_spacing * (bay + 0.5)
                is_main_entry = (length, tangent, normal, midpoint) == main_edge and row == 0 and bay == bay_count // 2
                center_xy = (midpoint[0] + tangent[0] * offset + normal[0] * 0.08,
                            midpoint[1] + tangent[1] * offset + normal[1] * 0.08)
                width = min(1.30, bay_spacing * 0.36)
                if is_main_entry:
                    # A centered formal entrance and light-stone surround are
                    # directly visible in the Purdue Archives' 1959 photograph.
                    door_x = center_xy[0] + normal[0] * 0.14
                    door_y = center_xy[1] + normal[1] * 0.14
                    add_box((door_x, door_y, 1.95), tangent, normal, 1.85, 0.10, 2.6, 2)
                    for side in (-1, 1):
                        add_box((door_x + tangent[0] * side * 1.55, door_y + tangent[1] * side * 1.55, 1.95), tangent, normal, 0.70, 0.10, 2.6, 2)
                    frame_y = center_xy[1] + normal[1] * 0.23
                    frame_x = center_xy[0] + normal[0] * 0.23
                    for side in (-1, 1):
                        add_box((frame_x + tangent[0] * side * 2.05, frame_y + tangent[1] * side * 2.05, 2.0), tangent, normal, 0.35, 0.18, 3.8, 1)
                    add_box((frame_x, frame_y, 3.85), tangent, normal, 4.45, 0.18, 0.32, 1)
                    add_box((frame_x, frame_y, 0.35), tangent, normal, 4.45, 0.18, 0.25, 1)
                    # Broad, low entrance steps are visible in the 1959 Purdue
                    # Archives photograph; their dimensions are estimated.
                    for step in range(3):
                        distance = 0.18 + (2 - step) * 0.48
                        height = 0.20 * (step + 1)
                        center = (center_xy[0] + normal[0] * distance, center_xy[1] + normal[1] * distance, height * 0.5)
                        add_box(center, tangent, normal, 5.8, 0.48, height, 1)
                    continue
                add_box((center_xy[0], center_xy[1], window_z), tangent, normal, width, 0.12, window_h, 2)
                trim_w = 0.12
                for side in (-1, 1):
                    off2 = offset + side * (width * 0.5 + trim_w * 0.5)
                    cx = midpoint[0] + tangent[0] * off2 + normal[0] * 0.11
                    cy = midpoint[1] + tangent[1] * off2 + normal[1] * 0.11
                    add_box((cx, cy, window_z), tangent, normal, trim_w, 0.14, window_h + 0.22, 1)
                for zoff in (-window_h * 0.5 - trim_w * 0.5, window_h * 0.5 + trim_w * 0.5):
                    add_box((center_xy[0], center_xy[1], window_z + zoff), tangent, normal, width + 2 * trim_w, 0.14, trim_w, 1)

        # Repeated vertical light-stone piers, scaled to the photographed facade rhythm.
        for bay in range(bay_count + 1):
            offset = -length * 0.5 + bay_spacing * bay
            cx = midpoint[0] + tangent[0] * offset + normal[0] * 0.10
            cy = midpoint[1] + tangent[1] * offset + normal[1] * 0.10
            add_box((cx, cy, HEIGHT_M_ESTIMATE * 0.52), tangent, normal, 0.32, 0.18, HEIGHT_M_ESTIMATE * 0.94, 1)
        # Horizontal belt/course at each mapped floor break.
        for z in floor_levels:
            cx = midpoint[0] + normal[0] * 0.10
            cy = midpoint[1] + normal[1] * 0.10
            add_box((cx, cy, min(z, HEIGHT_M_ESTIMATE - 0.35)), tangent, normal, length, 0.16, 0.13, 1)

    # Eaves/parapet are deliberately reduced to a flat roof and a simple cornice.
    for length, tangent, normal, midpoint in edge_data:
        if length < 4.0:
            continue
        cx = midpoint[0] + normal[0] * 0.06
        cy = midpoint[1] + normal[1] * 0.06
        add_box((cx, cy, HEIGHT_M_ESTIMATE - 0.18), tangent, normal, length, 0.25, 0.30, 1)

    obj.data.from_pydata(verts, [], faces)
    obj.data.update()
    for polygon_face, material_id in zip(obj.data.polygons, mids):
        polygon_face.material_index = material_id
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    obj["building_id"] = BUILDING_ID
    obj["source_fid"] = int(attrs["FID"])
    obj["source_name"] = attrs["BUILDING_N"]
    obj["height_m"] = HEIGHT_M_ESTIMATE
    obj["height_status"] = "estimate; GIS Extrution=45 interpreted as feet, unit not declared"
    obj["gis_num_levels"] = int(attrs["NUM_LEVELS"])
    obj["gis_floor_fields"] = "B, G, F01-F04"
    obj["visible_facade_bands"] = len(floor_levels)
    obj["level_interpretation"] = "Four facade bands follow GIS F01-F04 fields; GIS NUM_LEVELS=6 also lists B and G, whose elevation datum/units and above/below-grade relationship are undocumented."
    obj["facade_status"] = "interpretation from Purdue Archives 1959 photographs; not a current measured survey"
    obj["footprint_source"] = "Purdue ArcGIS BuildingShapesZip4 FeatureServer/0, FID 240, STON"
    obj["footprint_area_m2"] = abs(signed_area)
    obj["footprint_ring_vertices"] = len(polygon)
    obj["crs_note"] = "Approximate campus xy conversion per modular/AGENTS.md from WGS84 latitude/longitude"

    # Preview-only ground and lighting are excluded from the exported asset collection.
    min_x = min(p[0] for p in polygon); max_x = max(p[0] for p in polygon)
    min_y = min(p[1] for p in polygon); max_y = max(p[1] for p in polygon)
    cx, cy = (min_x + max_x) * 0.5, (min_y + max_y) * 0.5
    bpy.ops.mesh.primitive_plane_add(size=max(max_x - min_x, max_y - min_y) * 1.75, location=(cx, cy, -0.08))
    ground = bpy.context.object
    ground.name = "Preview ground - excluded from asset"
    for c in list(ground.users_collection):
        c.objects.unlink(ground)
    staging.objects.link(ground)
    ground.data.materials.append(new_material("Preview ground", (0.52, 0.52, 0.50)))

    camera_data = bpy.data.cameras.new("StoneHall_Preview_Camera")
    camera = bpy.data.objects.new("StoneHall_Preview_Camera", camera_data)
    staging.objects.link(camera)
    camera.location = (cx - 78, cy - 110, HEIGHT_M_ESTIMATE * 2.7 + 25)
    target = Vector((cx, cy, HEIGHT_M_ESTIMATE * 0.42))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(max_x - min_x, max_y - min_y) * 1.75
    scene.camera = camera

    light_data = bpy.data.lights.new("StoneHall_Preview_Sun", type="AREA")
    light = bpy.data.objects.new("StoneHall_Preview_Sun", light_data)
    staging.objects.link(light)
    light.location = (cx - 35, cy - 60, HEIGHT_M_ESTIMATE * 2.6 + 30)
    light_data.energy = 12000
    light_data.shape = "DISK"
    light_data.size = 70

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("Stone Hall Preview World")
    scene.world.color = (0.8, 0.8, 0.8)
    scene.render.filepath = str(PREVIEW_PATH)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.camera.data.lens = 50

    AUDIT.joinpath("preview").mkdir(parents=True, exist_ok=True)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    scene["building_id"] = BUILDING_ID
    scene["full_stable_id"] = BUILDING_ID
    scene["source_fid"] = 240
    scene["source_name"] = "Winthrop E. Stone Hall"
    scene["height_note"] = "45 ft interpretation of GIS Extrution=45; source units undocumented; estimate only"
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Save an oblique overview, an elevation-like front view, and a top footprint view.
    camera.location = (cx - 78, cy - 110, HEIGHT_M_ESTIMATE * 2.7 + 25)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.ortho_scale = max(max_x - min_x, max_y - min_y) * 1.75
    scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    camera.location = (cx, min_y - 110, HEIGHT_M_ESTIMATE * 0.55)
    camera.rotation_euler = (Vector((cx, cy, HEIGHT_M_ESTIMATE * 0.50)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.ortho_scale = (max_x - min_x) * 1.25
    scene.render.filepath = str(FRONT_PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    camera.location = (cx, cy, 95)
    camera.rotation_euler = (0, 0, 0)
    camera_data.ortho_scale = max(max_x - min_x, max_y - min_y) * 1.35
    scene.render.filepath = str(TOP_PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    # Keep the saved camera on the oblique view.
    camera.location = (cx - 78, cy - 110, HEIGHT_M_ESTIMATE * 2.7 + 25)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.ortho_scale = max(max_x - min_x, max_y - min_y) * 1.75
    scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    # The report is emitted from the same build process; a separate reopen check follows.
    world = [tuple(obj.matrix_world @ Vector(corner)) for corner in obj.bound_box]
    bounds = [[min(v[axis] for v in world), max(v[axis] for v in world)] for axis in range(3)]
    report = {
        "building_id": BUILDING_ID,
        "asset": str(ASSET_PATH.relative_to(REPO)).replace("\\", "/"),
        "scene": SCENE_NAME,
        "collection": COLLECTION_NAME,
        "object_count_in_asset_collection": len(collection.objects),
        "object_names": [o.name for o in collection.objects],
        "source_fid": attrs["FID"],
        "source_abbreviation": attrs["BLDG_ABBR"],
        "source_name": attrs["BUILDING_N"],
        "source_crs": "EPSG:4326",
        "projection": "Approximate XY campus transform in modular/AGENTS.md; not surveyed",
        "gis_polygon_area_m2_approx": round(abs(signed_area), 3),
        "bounds_world_m": [[round(v, 3) for v in pair] for pair in bounds],
        "height": {"value_m": round(HEIGHT_M_ESTIMATE, 3), "status": "estimated", "basis": "GIS Extrution=45 interpreted as feet; units are not declared by source layer", "uncertainty": "high"},
        "floor_count": {"gis_total_levels": int(attrs["NUM_LEVELS"]), "modeled_facade_bands": len(floor_levels), "basis": "GIS NUM_LEVELS=6 with F01-F04 floor fields; B and G are included in total count but not split into additional visible window rows because the layer does not define their datum, units, or above/below-grade relationship", "measurement_status": "source attribute and explicit modeling interpretation; not independently checked against measured plans"},
        "facade": {"basis": "Purdue Archives historic photographs dated September 14, 1959 and undated, IDs 1371-1374", "status": "photo-based interpretation; exact current facade dimensions unverified"},
        "renders": [str(p.relative_to(REPO)).replace("\\", "/") for p in (PREVIEW_PATH, FRONT_PREVIEW_PATH, TOP_PREVIEW_PATH)],
        "build_date": date.today().isoformat(),
        "limitations": ["GIS polygon is an official campus GIS footprint, not a certified survey.", "Height unit is absent from GIS schema; 45 ft is an estimate, not a measurement.", "Photographic facade details are from archival 1959 views; current renovations may differ.", "No detailed elevations or certified measured drawings were found in the evidence set."],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    build()
