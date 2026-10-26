"""Build the Agricultural Administration Building from its matched Purdue GIS footprint.

Run with Blender 4.2+ in background mode:
  blender --background --python build_agricultural_administration_building.py

The building is exported as one local-coordinate collection. Campus placement
belongs to Placement_agricultural_administration_building in the master.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "agricultural_administration_building"
COLLECTION_NAME = "Asset_agricultural_administration_building"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE_DIR = ROOT / "audit" / ASSET_ID
SOURCES_DIR = EVIDENCE_DIR / "sources"
GIS_PATH = SOURCES_DIR / "agricultural_administration_gis_feature_267_current.json"
MASTER_ORIGIN_LAT = 40.4274
MASTER_ORIGIN_LON = -86.9137
LON_TO_M = 111412.84 * math.cos(math.radians(MASTER_ORIGIN_LAT))
LAT_TO_M = 111040.0

# The plan shell is sourced from GIS. No measured current vertical survey is
# available. GIS level counts are preserved, while height and band spacing are
# explicitly diagrammatic estimates rather than survey dimensions.
ESTIMATED_HEIGHT_M = 17.2
ESTIMATED_FLOORS = 5
FLOOR_HEIGHT_M = ESTIMATED_HEIGHT_M / ESTIMATED_FLOORS
CAMERA_COLLECTION = "AGAD_Preview_Only"
PREFIX = "AGAD"
_BOXES = {}

def require_source():
    manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
    asset = next((a for a in manifest["assets"] if a.get("id") == ASSET_ID), None)
    assert asset, f"Manifest ID missing: {ASSET_ID}"
    assert asset["file"].replace("\\", "/") == f"buildings/{ASSET_ID}.blend"
    assert asset["collection"] == COLLECTION_NAME
    assert GIS_PATH.is_file(), f"Preserved GIS feature missing: {GIS_PATH}"
    snapshot = json.loads(GIS_PATH.read_text(encoding="utf-8"))
    if "error" in snapshot:
        raise RuntimeError(f"GIS query failed: {snapshot['error']}")
    features = snapshot.get("features", [])
    feature = next(
        (f for f in features if int(f.get("attributes", {}).get("FID", -1)) == 267),
        None,
    )
    assert feature, "Purdue GIS query did not return feature 267"
    attrs = feature["attributes"]
    assert attrs.get("BLDG_ABBR") == "AGAD"
    assert attrs.get("BUILDING_N") == "Agricultural Administration Building"
    ring = feature["geometry"]["rings"][0]
    assert len(ring) >= 5
    return snapshot, feature, [tuple(p[:2]) for p in ring[:-1]]

def local_footprint(ring_lonlat):
    """Reproject WGS84 lon/lat using the project-prescribed local approximation."""
    world = [
        ((lon - MASTER_ORIGIN_LON) * LON_TO_M, (lat - MASTER_ORIGIN_LAT) * LAT_TO_M)
        for lon, lat in ring_lonlat
    ]
    twice_area = 0.0
    cx_sum = cy_sum = 0.0
    for i, (x, y) in enumerate(world):
        u, v = world[(i + 1) % len(world)]
        cross = x * v - u * y
        twice_area += cross
        cx_sum += (x + u) * cross
        cy_sum += (y + v) * cross
    assert abs(twice_area) > 1.0, "Invalid GIS shell polygon"
    cx = cx_sum / (3.0 * twice_area)
    cy = cy_sum / (3.0 * twice_area)
    return [(x - cx, y - cy) for x, y in world], (cx, cy), abs(twice_area) / 2.0

def material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat

def brick_material():
    mat = material(f"{ASSET_ID}_red_brown_brick", (0.28, 0.085, 0.052), 0.83)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    texcoord = nodes.new("ShaderNodeTexCoord")
    brick = nodes.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value = (0.34, 0.105, 0.067, 1)
    brick.inputs["Color2"].default_value = (0.22, 0.06, 0.038, 1)
    brick.inputs["Mortar"].default_value = (0.14, 0.11, 0.095, 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.025
    brick.inputs["Mortar Smooth"].default_value = 0.04
    brick.inputs["Brick Width"].default_value = 0.52
    brick.inputs["Row Height"].default_value = 0.22
    links.new(texcoord.outputs["Object"], brick.inputs["Vector"])
    links.new(brick.outputs["Color"], shader.inputs["Base Color"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.1
    noise.inputs["Detail"].default_value = 2.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.035
    links.new(texcoord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return mat

def cube(name, loc, dims, mat, coll, rotation=0.0, bevel=0.0):
    _BOXES.setdefault((coll.name, mat.name if mat else "_none"), []).append(
        (name, tuple(loc), tuple(dims), mat, float(rotation)))
    return None

def flush_boxes(collection):
    for (collection_name, mat_name), boxes in list(_BOXES.items()):
        if collection_name != collection.name or not boxes:
            continue
        mat = boxes[0][3]
        verts, faces, labels = [], [], []
        for name, (cx, cy, cz), (dx, dy, dz), _material, angle in boxes:
            start = len(verts)
            ca, sa = math.cos(angle), math.sin(angle)
            for sx, sy, sz in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                               (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
                x, y = sx * dx * 0.5, sy * dy * 0.5
                verts.append((cx + ca*x - sa*y, cy + sa*x + ca*y, cz + sz*dz*0.5))
            faces.extend(tuple(start + j for j in f) for f in (
                (0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)))
            labels.append(name)
        mesh = bpy.data.meshes.new(f"{PREFIX}_{collection_name}_{mat_name}_mesh")
        mesh.from_pydata(verts, [], faces)
        if mat:
            mesh.materials.append(mat)
        mesh.update()
        obj = bpy.data.objects.new(f"{PREFIX}_{mat_name}_details", mesh)
        collection.objects.link(obj)
        obj["geometry_component_count"] = len(boxes)
        obj["component_names"] = json.dumps(labels)
        del _BOXES[(collection_name, mat_name)]

def extruded_footprint(name, polygon, z0, z1, mat, coll):
    n = len(polygon)
    verts = [(x, y, z0) for x, y in polygon] + [(x, y, z1) for x, y in polygon]
    faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    # Tessellate cap triangles so this remains valid for the source's concave shell.
    cap_vectors = [Vector((x, y, 0.0)) for x, y in polygon]
    for tri in tessellate_polygon([cap_vectors]):
        # Blender returns source vertex indices for these cap triangles.
        faces.append(tuple(int(i) + n for i in tri))
    mesh = bpy.data.meshes.new(f"{PREFIX}_{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(f"{PREFIX}_{name}", mesh)
    coll.objects.link(obj)
    return obj

def bounds(poly):
    return (min(x for x, y in poly), max(x for x, y in poly),
            min(y for x, y in poly), max(y for x, y in poly))

def make_shell(polygon, height, coll, brick, stone, roof):
    obj = extruded_footprint("GIS_outline_primary_shell", polygon, 0.0, height, brick, coll)
    obj["role"] = "Structural shell extruded from the matched Purdue GIS footprint"
    obj["source_feature_id"] = 267
    obj["source_footprint_crs"] = "WGS84/EPSG:4326 converted to approximate campus-local meters"
    # A robust limestone base and story courses express the photographed masonry
    # character; all face details are visual cues, not surveyed dimensions.
    n = len(polygon)
    ccw = sum(
        polygon[i][0] * polygon[(i + 1) % n][1] -
        polygon[(i + 1) % n][0] * polygon[i][1]
        for i in range(n)
    ) > 0
    for i, (x, y) in enumerate(polygon):
        u, v = polygon[(i + 1) % n]
        length = math.hypot(u - x, v - y)
        if length < 3.0:
            continue
        angle = math.atan2(v - y, u - x)
        # Outward normal for the polygon orientation.
        nx, ny = ((math.sin(angle), -math.cos(angle)) if ccw
                  else (-math.sin(angle), math.cos(angle)))
        mx, my = (x + u) / 2, (y + v) / 2
        cube(f"limestone_plinth_{i}", (mx + nx * 0.055, my + ny * 0.055, 1.65),
             (length, 0.11, 3.3), stone, coll, angle, 0.015)
        cube(f"limestone_floor_belt_{i}", (mx + nx * 0.11, my + ny * 0.11, 3.38),
             (length, 0.20, 0.22), stone, coll, angle, 0.015)
        for floor in range(1, ESTIMATED_FLOORS):
            z = floor * FLOOR_HEIGHT_M
            if z > 4.0:
                cube(f"limestone_story_belt_{i}_{floor}", (mx + nx * 0.08, my + ny * 0.08, z),
                     (length, 0.14, 0.10), stone, coll, angle, 0.008)
        cube(f"limestone_cornice_{i}", (mx + nx * 0.15, my + ny * 0.15, height - 0.10),
             (length, 0.28, 0.20), stone, coll, angle, 0.015)
    # A restrained, flat concealed roof is intentionally schematic because
    # contemporary roof geometry is not established by available sources.
    roof_obj = extruded_footprint("roof_membrane", polygon, height - 0.08, height + 0.02, roof, coll)
    roof_obj["roof_status"] = "Current roof not visible in source photo; neutral flat cap is a constrained placeholder. Tile roof is documented for the original 1908 state only."
    return obj, (nx, ny)

def add_window(name, center, tangent, outward, width, sill, height, coll, glass, frame, stone):
    # All dimensions are visually estimated; these windows establish the
    # tall, punched openings visible in Purdue's current and archival photos.
    tx, ty = tangent
    nx, ny = outward
    ang = math.atan2(ty, tx)
    depth = 0.22
    px, py, z = center
    # dark recessed surround and glazing
    cube(f"{name}_frame", (px + nx * 0.13, py + ny * 0.13, z),
         (width + 0.20, depth, height + 0.18), frame, coll, ang)
    cube(f"{name}_glass", (px + nx * 0.255, py + ny * 0.255, z),
         (width, 0.06, height), glass, coll, ang)
    # pale stone head and sill, consistent with historical records/photos
    cube(f"{name}_stone_sill", (px + nx * 0.20, py + ny * 0.20, z - height / 2 - 0.10),
         (width + 0.24, 0.30, 0.12), stone, coll, ang, 0.01)
    cube(f"{name}_stone_lintel", (px + nx * 0.20, py + ny * 0.20, z + height / 2 + 0.10),
         (width + 0.24, 0.28, 0.12), stone, coll, ang, 0.01)
    cube(f"{name}_mullion", (px + nx * 0.30, py + ny * 0.30, z),
         (0.055, 0.08, height), frame, coll, ang)

def add_facade(polygon, coll, glass, frame, stone, steel):
    n = len(polygon)
    twice_area = sum(
        polygon[i][0] * polygon[(i + 1) % n][1] -
        polygon[(i + 1) % n][0] * polygon[i][1]
        for i in range(n)
    )
    ccw = twice_area > 0
    min_y = min(y for x, y in polygon)
    edges = []
    for i, (x, y) in enumerate(polygon):
        u, v = polygon[(i + 1) % n]
        length = math.hypot(u - x, v - y)
        if length < 6.0:
            continue
        tx, ty = (u - x) / length, (v - y) / length
        nx, ny = ((ty, -tx) if ccw else (-ty, tx))
        edges.append((i, x, y, u, v, length, tx, ty, nx, ny))

    # Glazing rhythm follows only straight shell edges long enough for repeated bays.
    for i, x, y, u, v, length, tx, ty, nx, ny in edges:
        if length < 10.0:
            continue
        count = max(2, int((length - 2.5) // 4.0))
        margin = (length - count * 3.55) / (count + 1)
        for floor in range(ESTIMATED_FLOORS):
            z = floor * FLOOR_HEIGHT_M + (1.65 if floor == 0 else FLOOR_HEIGHT_M * 0.60)
            window_height = 1.65 if floor == 0 else 1.48
            window_width = 1.08 if floor == 0 else 1.22
            for q in range(count):
                along = margin + q * (window_width + margin) + window_width / 2
                # Leave the public door opening in the likely south street face.
                # This placement is an estimate because the source has no door GIS.
                south_front = ((y + v) / 2 < min_y + 3.0 and abs(ty) < 0.25)
                if floor == 0 and south_front and abs(along - length / 2) < 2.0:
                    continue
                cx, cy = x + tx * along, y + ty * along
                add_window(f"window_edge{i}_floor{floor}_bay{q}",
                           (cx, cy, z), (tx, ty), (nx, ny),
                           window_width, z - window_height / 2, window_height,
                           coll, glass, frame, stone)
    # The 2023 Purdue photo shows a narrow, tall glazed portal with a stone
    # surround: lower entry doors below a stack of glazed panels. Its scale and
    # exact location are interpreted from an uncalibrated photograph; GIS has
    # no doorway point. Keep it as a photo-matched visual feature, not a survey.
    south = [e for e in edges if (e[2] + e[4]) / 2 < min_y + 3.0 and abs(e[6]) > 0.85]
    if south:
        edge = max(south, key=lambda e: e[5])
        _, x, y, u, v, length, tx, ty, nx, ny = edge
        along = length / 2
        cx, cy = x + tx * along, y + ty * along
        ang = math.atan2(ty, tx)
        portal_w, portal_h, portal_z = 2.05, 5.15, 2.72
        portal_depth = 0.22
        # Three-sided pale masonry frame, kept separate from the glazing so the
        # photo's full-height dark glass remains visible in a close render.
        cube("entrance_limestone_left_jamb",
             (cx - tx * (portal_w / 2 + 0.19) + nx * 0.20,
              cy - ty * (portal_w / 2 + 0.19) + ny * 0.20, portal_z),
             (0.32, portal_depth, portal_h + 0.42), stone, coll, ang)
        cube("entrance_limestone_right_jamb",
             (cx + tx * (portal_w / 2 + 0.19) + nx * 0.20,
              cy + ty * (portal_w / 2 + 0.19) + ny * 0.20, portal_z),
             (0.32, portal_depth, portal_h + 0.42), stone, coll, ang)
        cube("entrance_limestone_lintel",
             (cx + nx * 0.20, cy + ny * 0.20, portal_z + portal_h / 2 + 0.20),
             (portal_w + 0.68, portal_depth, 0.42), stone, coll, ang)
        # Dark metal perimeter and five vertically stacked panes. Lower panes
        # form paired entry doors; upper panels match the tall light above them.
        cube("entrance_glazing_dark_perimeter",
             (cx + nx * 0.34, cy + ny * 0.34, portal_z),
             (portal_w, 0.10, portal_h), frame, coll, ang)
        glass_w, glass_h = portal_w - 0.12, portal_h - 0.12
        cube("entrance_glazing_full_height",
             (cx + nx * 0.405, cy + ny * 0.405, portal_z),
             (glass_w, 0.045, glass_h), glass, coll, ang)
        for z_offset in (-0.82, 0.05, 0.92):
            cube(f"entrance_glazing_horizontal_mullion_{z_offset:+.2f}",
                 (cx + nx * 0.445, cy + ny * 0.445, portal_z + z_offset),
                 (glass_w, 0.075, 0.065), frame, coll, ang)
        cube("entrance_glazing_vertical_mullion",
             (cx + nx * 0.45, cy + ny * 0.45, portal_z),
             (0.065, 0.075, glass_h), frame, coll, ang)
        # Paired lower leaves are legible against the same continuous tall glass
        # composition; the photograph does not expose measured leaf dimensions.
        door_h = 2.12
        cube("entrance_door_pair_lower_rail",
             (cx + nx * 0.47, cy + ny * 0.47, 1.05),
             (glass_w, 0.07, 0.055), frame, coll, ang)
        for side in (-1, 1):
            cube(f"entrance_door_leaf_stile_{side:+d}",
                 (cx + tx * side * (glass_w / 4) + nx * 0.48,
                  cy + ty * side * (glass_w / 4) + ny * 0.48, 1.10),
                 (0.045, 0.07, door_h), frame, coll, ang)
        cube("entrance_stone_threshold",
             (cx + nx * 0.40, cy + ny * 0.40, 0.08),
             (portal_w + 0.70, 0.42, 0.16), stone, coll, ang)
        # Small level landing/approach; the photo documents an access walk/ramp
        # in this frontage, while the exact grade and extent are unknown.
        cube("entry_landing", (cx + nx * 1.65, cy + ny * 1.65, 0.08),
             (4.6, 3.5, 0.16), stone, coll, math.atan2(ty, tx), 0.04)
        for side in (-1, 1):
            rx, ry = cx + tx * side * 1.55 + nx * 3.0, cy + ty * side * 1.55 + ny * 3.0
            cube(f"entry_ramp_rail_post_{side}", (rx, ry, 0.55), (0.06, 0.06, 1.0),
                 steel, coll, math.atan2(ty, tx))
    return edges

def camera_look(name, location, target, scene, tools):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    tools.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    data.lens = 50
    return obj

def set_render_scene(polygon):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("AGAD_Render_World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.42, 0.45, 0.50, 1.0)
    bg.inputs["Strength"].default_value = 0.65
    scene.render.image_settings.file_format = "PNG"
    preview = bpy.data.collections.new(CAMERA_COLLECTION)
    scene.collection.children.link(preview)
    floor = cube("render_ground_not_exported", (0, 0, -0.28), (300, 300, 0.4),
                 material(f"{ASSET_ID}_render_ground", (0.35, 0.38, 0.42), 1.0),
                 preview)
    area = bpy.data.lights.new("AGAD_Preview_Area", "AREA")
    lamp = bpy.data.objects.new(area.name, area)
    preview.objects.link(lamp)
    lamp.location = (45, -60, 75)
    area.energy = 28000
    area.shape = "DISK"
    area.size = 55
    cx, cy = 0, 0
    cam = camera_look("AGAD_Preview_Overview", (72, -92, 70), (cx, cy, 8), scene, preview)
    cam.data.lens = 50
    scene.camera = cam
    flush_boxes(preview)
    return scene, preview, (cam, lamp, floor)

def create_building(snapshot, feature, ring_lonlat):
    # Start with a clean scene so the .blend has no leftover or unrelated objects.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    coll = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(coll)
    footprint, origin_world, gis_area = local_footprint(ring_lonlat)
    red_brick = brick_material()
    pale_limestone = material(f"{ASSET_ID}_pale_limestone", (0.63, 0.58, 0.49), 0.78)
    dark_frame = material(f"{ASSET_ID}_dark_metal_window_frames", (0.075, 0.09, 0.095), 0.44, 0.45)
    glass = material(f"{ASSET_ID}_blue_gray_glazing", (0.13, 0.25, 0.31), 0.24, 0.18)
    roof = material(f"{ASSET_ID}_roof_membrane_unverified", (0.14, 0.16, 0.17), 0.78)
    steel = material(f"{ASSET_ID}_dark_steel", (0.12, 0.14, 0.15), 0.45, 0.68)
    shell, _ = make_shell(footprint, ESTIMATED_HEIGHT_M, coll, red_brick,
                          pale_limestone, roof)
    shell["estimated_height_m"] = ESTIMATED_HEIGHT_M
    shell["height_status"] = "diagrammatic 17.2 m envelope; no measured current elevation located"
    shell["modeled_level_count"] = ESTIMATED_FLOORS
    shell["level_count_status"] = "Purdue GIS NUM_LEVELS and CountOfFLO both equal 5; floor use, datum and spacing are not defined in service metadata"
    edges = add_facade(footprint, coll, glass, dark_frame, pale_limestone, steel)
    scene, preview_coll, preview_tools = set_render_scene(footprint)
    flush_boxes(coll)
    scene["building_id"] = ASSET_ID
    scene["asset_collection"] = COLLECTION_NAME
    scene["coordinate_frame"] = "local meters; X east, Y north, Z up"
    scene["local_origin_world_xy_m"] = list(origin_world)
    scene["footprint_source_feature_id"] = 267
    scene["footprint_area_computed_m2"] = gis_area
    scene["roof_status"] = "current roof not visible in sources; neutral flat cap is a constrained placeholder; 1908 archive records tile roof only for original design"
    scene["interior_status"] = "not modeled; no verified floor plan sourced"

    # Set camera/world lighting and save the source before rendering previews.
    scene.render.filepath = str(EVIDENCE_DIR / f"{ASSET_ID}_overview.png")
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    # Close elevated doorway view aligned with the source photograph, using the
    # inferred south frontage. This camera stays outside the exported collection.
    min_y = min(y for x, y in footprint)
    south_edges = [e for e in edges if (e[2] + e[4]) / 2 < min_y + 3.0 and abs(e[6]) > 0.85]
    if south_edges:
        edge = max(south_edges, key=lambda e: e[5])
        _, x, y, u, v, length, tx, ty, nx, ny = edge
        midx, midy = (x + u) / 2, (y + v) / 2
        close = camera_look("AGAD_Preview_Entrance", (midx + nx * 34, midy + ny * 34, 7.2),
                            (midx, midy, 3.0), scene, preview_coll)
        scene.camera = close
        scene.render.resolution_x = 1100
        scene.render.resolution_y = 850
        scene.render.filepath = str(EVIDENCE_DIR / f"{ASSET_ID}_entrance.png")
        bpy.ops.render.render(write_still=True)

    # Record builder inputs and outputs for independent grading.
    file_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
    attrs = feature["attributes"]
    summary = {
        "building_id": ASSET_ID,
        "assigned_owner": "Rosen",
        "asset": "modular/buildings/agricultural_administration_building.blend",
        "collection": COLLECTION_NAME,
        "builder_script": "modular/buildings/build_agricultural_administration_building.py",
        "date_built": date.today().isoformat(),
        "source_feature_id": int(attrs["FID"]),
        "building_code": attrs["BLDG_ABBR"],
        "building_name": attrs["BUILDING_N"],
        "source_address": attrs.get("ADDRESS"),
        "gis_source": {
            "provider": "Purdue University BuildingShapesZip4 ArcGIS FeatureServer",
            "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D267&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
            "feature_id": 267,
            "retrieved": date.today().isoformat(),
            "service_native_crs": "EPSG:3857",
            "snapshot_output_crs": "EPSG:4326",
            "snapshot": "audit/agricultural_administration_building/sources/agricultural_administration_gis_feature_267_current.json",
            "layer_metadata_snapshot": "audit/agricultural_administration_building/sources/agricultural_administration_gis_layer_metadata_2026-10-25.json",
            "measurement_method": "Exact exterior ring projected using the project-prescribed local geographic approximation and recentered at its shoelace centroid."
        },
        "gis_vertical_attributes": {
            "raw_values": {key: attrs.get(key) for key in ["Level_", "NUM_LEVELS", "CountOfFLO", "Extrution", "F01", "F02", "F03", "F04", "F05"]},
            "field_metadata": "The service describes these fields only by name and numeric type; it does not define units, datum, or vertical measurement semantics.",
            "model_use": "NUM_LEVELS=5 and CountOfFLO=5 support only five diagrammatic facade bands. Other raw values are preserved but not converted to meters or used as surveyed heights/floor datums."
        },
        "geometry_source_crs": "EPSG:4326",
        "source_snapshot": "audit/agricultural_administration_building/sources/agricultural_administration_gis_feature_267_current.json",
        "historical_photo_source": {
            "provider": "Purdue University Stories; photo credited to Purdue University Archives and Special Collections",
            "url": "https://stories.purdue.edu/app/uploads/2023/03/AGAD-OLD-side-by-side-660x825-1.jpg",
            "caption_page": "https://stories.purdue.edu/early-advocacy-paved-way-for-purdues-thriving-disability-resource-center/",
            "retrieved": date.today().isoformat(),
            "source_date": "historic photograph; original photo date not stated",
            "supports": ["brick exterior", "stone trim", "historic roof silhouette only in archival-era image"],
            "snapshot": "audit/agricultural_administration_building/sources/agad_archival_facade_2023.jpg"
        },
        "historic_vertical_and_roof_source": {
            "provider": "Purdue University Archives and Special Collections",
            "url": "https://archives.lib.purdue.edu/agents/corporate_entities/569",
            "retrieved": date.today().isoformat(),
            "source_date": "Historical information about the 1908 opening; page also notes multiple later renovations.",
            "supports": ["original building opened as two stories plus a basement", "brick and stone trim", "original tile roof", "subsequent renovations make current roof and vertical arrangement uncertain"],
            "snapshot": "audit/agricultural_administration_building/sources/purdue_archives_agad_history_2026-10-25.json"
        },
        "current_entrance_photo_source": {
            "provider": "Purdue University Stories; photo by Rebecca McElhoe",
            "url": "https://stories.purdue.edu/app/uploads/2023/03/AGAD-NEW-side-by-side-660x825-1.jpg",
            "caption_page": "https://stories.purdue.edu/early-advocacy-paved-way-for-purdues-thriving-disability-resource-center/",
            "retrieved": date.today().isoformat(),
            "source_date": "2023 article; image caption says current building, exact capture date not stated",
            "supports": ["present-day brick and limestone facade", "glazed accessible entrance", "approach walk"]
        },
        "geometry": {
            "method": "Project exact exterior ring using project local approximation: X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat-40.4274)*111040; subtract shoelace centroid for local origin; extrude only the outline.",
            "origin_world_xy_m": [round(v, 6) for v in origin_world],
            "gis_footprint_area_computed_m2": round(gis_area, 2),
            "source_shape_area_attribute_web_mercator_m2": attrs.get("Shape__Area"),
            "source_area_note": "Shape__Area is calculated in native Web Mercator; the ring is returned in geographic coordinates, so its local ground-plane area differs by the expected latitude distortion factor.",
            "footprint_vertices": len(footprint),
            "local_bounds_m": [round(v, 3) for v in bounds(footprint)],
            "model_height_m": ESTIMATED_HEIGHT_M,
            "height_status": "diagrammatic estimate only; no current measured elevation. The archival two-story-plus-basement description is dated to the 1908 opening and cannot be assumed unchanged after documented renovations.",
            "modeled_levels": ESTIMATED_FLOORS,
            "floor_height_m": round(FLOOR_HEIGHT_M, 2),
            "floor_height_status": "equal visual bands at 3.44 m are a modeling scaffold only; current GIS exposes NUM_LEVELS=5 and CountOfFLO=5 but no field units/vertical definitions, and the 1908 archive describes a different historical state.",
            "facade": "Punched vertical window bays, dark metal frames, brick field, limestone plinth/belts/cornice, and a tall stacked-glass portal composition matching the 2023 Purdue photo. Bay positions and dimensions are visual estimates from uncalibrated photos.",
            "entry_location": "Estimated at the midpoint of the longest south-facing segment; photo identifies the glazed entrance but GIS contains no doorway location.",
            "roof": "Simple neutral flat cap, explicitly a constrained placeholder rather than a claim about the present roof. Purdue Archives documents a tile roof at the 1908 opening, but also documents later renovations; the current photo does not show the roof.",
            "interior": "Not modeled; no verified floor-plan source was located."
        },
        "validation": {
            "asset_sha256_after_save": file_hash,
            "exported_collection": COLLECTION_NAME,
            "expected_collection_object_count": len(coll.all_objects),
            "source_ring_and_manifest_contract_checked": True,
            "rendered_previews": [
                f"audit/{ASSET_ID}/{ASSET_ID}_overview.png",
                f"audit/{ASSET_ID}/{ASSET_ID}_entrance.png"
            ],
            "external_image_dependencies": [],
            "preview_only_camera_light_floor_collection": CAMERA_COLLECTION
        },
        "geometry_edits": [
            "New source library rebuilt from scratch as a single structural shell using GIS feature 267.",
            "Added estimated masonry base, story courses, cornice and repeated punched-window bays using photo-supported brick/limestone palette.",
            "Reworked the estimated glazed south entrance as a tall, narrow stacked-glass portal with paired lower door leaves, mullions, stone jambs and lintel, matching the composition in Purdue’s captioned 2023 entrance photograph.",
            "Kept a neutral flat roof cap and diagrammatic vertical envelope because available vertical GIS fields lack units/definitions and the present roof is not shown; recorded the documented 1908 tile roof as historical, not current.",
            "Added preview-only cameras, light and ground outside the exported building collection."
        ],
        "uncertainties": [
            "The GIS ring identifies the correct building by FID 267, AGAD code, name and address; it is a published footprint, not a boundary survey. Shape__Area is native Web Mercator area while the returned ring is WGS84 and converted to local ground meters.",
            "Purdue Archives records the 1908 opening as two stories plus a basement with a tile roof, and records later renovations. The current GIS separately reports NUM_LEVELS=5 and CountOfFLO=5; the service exposes no vertical-field units or definitions. The model's 17.2 m envelope and 3.44 m equal bands are deliberately diagrammatic, not a measured current height or floor spacing.",
            "The gray flat cap is a neutral placeholder because current roof form is not visible in the modern photo; the archive's tile roof is evidence for the original 1908 state only.",
            "The 2023 image supports the present brick/stone facade and a tall, narrow glazed entrance composition. The doorway location, height, number of panes, facade bay spacing and window dimensions remain estimated from an uncalibrated image and GIS has no doorway point.",
            "No verified floor plans, facade elevations, construction drawings, current aerial measurement, or Street View calibration were located for this build.",
            "The building outline has one exterior ring and no interior rings in the checked feature; no separate courtyard holes are represented."
        ]
    }
    (EVIDENCE_DIR / "build_evidence.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({
        "saved_asset": str(ASSET_PATH),
        "collection": COLLECTION_NAME,
        "objects": len(coll.all_objects),
        "origin": origin_world,
        "local_bounds_m": bounds(footprint),
        "previews": summary["validation"]["rendered_previews"],
        "sha256": file_hash,
    }, indent=2), flush=True)

def main():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    snapshot, feature, ring = require_source()
    create_building(snapshot, feature, ring)

if __name__ == "__main__":
    main()
