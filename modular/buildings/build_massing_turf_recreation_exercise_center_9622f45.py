"""Build the Purdue Turf Recreation Exercise Center (TREC) library.

The wall footprint comes from Purdue CampusBuilding GIS feature (OBJECTID 312,
ABBR=TREC). Campus coordinates use the project approximation. The 2018 Indiana
QL2 LiDAR return profile informs estimated eave and ridge heights; these are not
surveyed dimensions. A July 2023 TREC-specific Google Street View panorama
supports visible east/northeast facade materials and feature types, while exact
component stationing and dimensions remain visual estimates. The visible roof
perimeter remains in conflict with the older OSM outline.
"""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


BUILDING_ID = "massing_turf_recreation_exercise_center_9622f45"
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
SCENE_NAME = f"Building_{BUILDING_ID}"
ROOT = Path(__file__).resolve().parents[2]
GIS_PATH = ROOT / "audit" / BUILDING_ID / "sources" / "purdue_gis_trec_oid312_2026-10-26.geojson"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
PREVIEW_PATH = ROOT / "audit" / BUILDING_ID / "preview.png"
PREVIEW_TOP_PATH = ROOT / "audit" / BUILDING_ID / "preview_top.png"
PREVIEW_NORTH_PATH = ROOT / "audit" / BUILDING_ID / "preview_north_gable.png"
PREVIEW_EAST_PATH = ROOT / "audit" / BUILDING_ID / "preview_east_entry.png"
EVIDENCE_PATH = ROOT / "audit" / BUILDING_ID / "evidence.json"

LAT0 = 40.4274
LON0 = -86.9137
WALL_HEIGHT_M = 9.7       # LiDAR-derived profile estimate, not surveyed
RIDGE_HEIGHT_M = 14.4     # LiDAR-derived profile estimate, not surveyed
ROOF_OVERHANG_M = 0.55    # generic construction allowance
ENTRY_WIDTH_M = 2.4       # approximate glazed entrance width, estimated from July 2023 panorama
ENTRY_HEIGHT_M = 2.4      # approximate door height, estimated from July 2023 panorama


def world_xy(lon, lat):
    x = (lon - LON0) * 111412.84 * math.cos(math.radians(LAT0))
    y = (lat - LAT0) * 111040.0
    return x, y


def material(name, color, metallic=0.0, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def make_mesh(name, vertices, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def box(name, center, dimensions, mat, collection):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def polygon_area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1] -
                   points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) / 2.0)


def load_footprint():
    data = json.loads(GIS_PATH.read_text(encoding="utf-8-sig"))
    feature = data["features"][0]
    props = feature["properties"]
    assert props["OBJECTID"] == 312 and props["ABBR"] == "TREC"
    assert props["Name"] == "Turf Recreation Exercise Center"
    rings = feature["geometry"]["coordinates"]
    ring = rings[0]
    points = [world_xy(lon, lat) for lon, lat in ring[:-1]]
    return points, props


def clear_scene(scene):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name == COLLECTION_NAME:
            bpy.data.collections.remove(collection)
    for other in list(bpy.data.scenes):
        if other != scene:
            bpy.data.scenes.remove(other)


def build():
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    clear_scene(scene)
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)

    footprint, props = load_footprint()
    xs, ys = [p[0] for p in footprint], [p[1] for p in footprint]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    width, length = maxx - minx, maxy - miny
    footprint_m2 = polygon_area(footprint)

    osm_path = ROOT / "audit" / BUILDING_ID / "sources" / "osm_trec_way_283275002_2026-10-26.json"
    osm_data = json.loads(osm_path.read_text(encoding="utf-8-sig"))
    osm_nodes = {e["id"]: e for e in osm_data["elements"] if e["type"] == "node"}
    osm_way = next(e for e in osm_data["elements"] if e["type"] == "way")
    osm_points = [world_xy(osm_nodes[n]["lon"], osm_nodes[n]["lat"]) for n in osm_way["nodes"]]
    osm_bounds = [[min(p[0] for p in osm_points), max(p[0] for p in osm_points)],
                  [min(p[1] for p in osm_points), max(p[1] for p in osm_points)]]
    osm_area_m2 = polygon_area(osm_points)
    manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
    prior_asset = next(a for a in manifest["assets"] if a.get("id") == BUILDING_ID)
    prior_bounds = prior_asset["bounds_world_m"]
    prior_center = [(prior_bounds[i][0] + prior_bounds[i][1]) / 2 for i in range(2)]
    gis_center = [cx, cy]
    imagery_report_path = ROOT / "audit" / BUILDING_ID / "footprint_imagery_comparison.json"
    imagery_report = json.loads(imagery_report_path.read_text(encoding="utf-8"))

    # The July 2023 Google Street View panorama is directly centered on TREC
    # and reveals the east-side exterior: red brick base, pale vertically ribbed
    # metal upper wall, a glazed corner entry beneath a canopy, vents, one window
    # and service doors. Their exact stationing is estimated from perspective.
    walls = material("TREC | light neutral wall backing", (0.62, 0.66, 0.67), 0.05)
    brick = material("TREC | red-brown brick base (Street View Jul 2023)", (0.34, 0.105, 0.065), 0.0, 0.84)
    metal = material("TREC | light gray vertical-rib metal (Street View Jul 2023)", (0.71, 0.73, 0.70), 0.16, 0.62)
    ribmat = material("TREC | metal panel standing ribs (Street View Jul 2023)", (0.55, 0.59, 0.58), 0.20, 0.56)
    glass = material("TREC | blue-gray glazing (Street View Jul 2023)", (0.055, 0.15, 0.27), 0.06, 0.32)
    frame = material("TREC | dark glazing frames (Street View Jul 2023)", (0.19, 0.22, 0.22), 0.38, 0.48)
    louvermat = material("TREC | dark wall louvers (Street View Jul 2023)", (0.20, 0.22, 0.22), 0.28, 0.62)
    canopy = material("TREC | light entrance canopy fascia (Street View Jul 2023)", (0.70, 0.73, 0.71), 0.16, 0.55)
    roofmat = material("TREC | light roof surface (2023 orthophoto)", (0.78, 0.81, 0.82), 0.12)
    roof_seam = material("TREC | transverse roof seam highlights (orthophoto rhythm)", (0.65, 0.69, 0.70), 0.14)
    trim = material("TREC | dark metal trim (inferred)", (0.20, 0.24, 0.25), 0.18)
    entrymat = material("TREC | glazed entry door (Street View Jul 2023)", (0.09, 0.23, 0.32), 0.22, 0.24)
    groundmat = material("TREC | interior slab", (0.68, 0.67, 0.62))

    # Flat site slab from the exact Purdue GIS perimeter, in campus coordinates.
    make_mesh("TREC_GIS_Footprint_Slab", [(x, y, 0.0) for x, y in footprint],
              [tuple(range(len(footprint)))], groundmat, asset)

    # Wall envelope follows the exact GIS ring. The facade pieces below are thin
    # overlays on the observed east side: plan placement, panel heights and
    # component spacing remain estimates because the panorama is perspective,
    # not a measured elevation.
    wall_vertices, wall_faces = [], []
    def wall_quad(a, b, z0, z1):
        base = len(wall_vertices)
        wall_vertices.extend([(a[0], a[1], z0), (b[0], b[1], z0),
                              (b[0], b[1], z1), (a[0], a[1], z1)])
        wall_faces.append((base, base + 1, base + 2, base + 3))

    east_candidates = [
        i for i in range(len(footprint))
        if abs(footprint[(i + 1) % len(footprint)][0] - footprint[i][0])
        < 0.08 * abs(footprint[(i + 1) % len(footprint)][1] - footprint[i][1])
        and (footprint[(i + 1) % len(footprint)][0] + footprint[i][0]) / 2 > cx
    ]
    east_side_index = max(
        east_candidates,
        key=lambda i: math.hypot(
            footprint[(i + 1) % len(footprint)][0] - footprint[i][0],
            footprint[(i + 1) % len(footprint)][1] - footprint[i][1]),
    )
    east_a = footprint[east_side_index]
    east_b = footprint[(east_side_index + 1) % len(footprint)]
    east_dx, east_dy = east_b[0] - east_a[0], east_b[1] - east_a[1]
    east_len = math.hypot(east_dx, east_dy)
    east_out = (east_dy / east_len, -east_dx / east_len)
    east_theta = math.atan2(east_dx, east_dy)
    glass_t0, glass_t1 = 0.86, 0.995

    def edge_xy(t):
        return (east_a[0] + east_dx * t, east_a[1] + east_dy * t)

    for i, point in enumerate(footprint):
        next_point = footprint[(i + 1) % len(footprint)]
        if i != east_side_index:
            wall_quad(point, next_point, 0.0, WALL_HEIGHT_M)
        else:
            glass_start, glass_end = edge_xy(glass_t0), edge_xy(glass_t1)
            wall_quad(point, glass_start, 0.0, WALL_HEIGHT_M)
            wall_quad(glass_start, glass_end, 0.0, 0.18)
            wall_quad(glass_start, glass_end, 8.65, WALL_HEIGHT_M)
            wall_quad(glass_end, next_point, 0.0, WALL_HEIGHT_M)
    make_mesh("TREC_Unspecified_Exterior_Wall_Envelope", wall_vertices, wall_faces, walls, asset)

    def east_point(t, z, offset=0.10):
        return (east_a[0] + east_dx * t + east_out[0] * offset,
                east_a[1] + east_dy * t + east_out[1] * offset, z)

    def facade_panel(name, t0, t1, z0, z1, mat, offset=0.10):
        verts = [east_point(t0, z0, offset), east_point(t1, z0, offset),
                 east_point(t1, z1, offset), east_point(t0, z1, offset)]
        return make_mesh(name, verts, [(0, 1, 2, 3)], mat, asset)

    facade_panel("TREC_East_Facade_Brick_Base", 0.0, 1.0, 0.02, 3.15, brick)
    facade_panel("TREC_East_Facade_Ribbed_Metal_Upper", 0.0, 1.0, 3.12, WALL_HEIGHT_M - 0.04, metal)

    # Narrow vertical ribs encode the repeated standing-seam/corrugated
    # appearance visible in the TREC panorama. Spacing is a visual estimate.
    rib_count = max(32, int(east_len / 0.48))
    for i in range(rib_count + 1):
        t = i / rib_count
        half_t = min(0.018 / east_len, 0.003)
        verts = [east_point(max(0.0, t - half_t), 3.18, 0.15),
                 east_point(min(1.0, t + half_t), 3.18, 0.15),
                 east_point(min(1.0, t + half_t), WALL_HEIGHT_M - 0.08, 0.15),
                 east_point(max(0.0, t - half_t), WALL_HEIGHT_M - 0.08, 0.15)]
        make_mesh(f"TREC_East_Facade_Vertical_Rib_{i:03d}", verts, [(0, 1, 2, 3)], ribmat, asset)

    # The close northeast-corner view shows a tall glazed entrance zone under
    # a projecting horizontal canopy. Its exact bay and measured dimensions
    # remain unknown; the modeled station and size are approximate.
    facade_panel("TREC_East_Corner_Entry_Glazing", glass_t0, glass_t1,
                 0.18, 8.65, glass, offset=0.10)
    for i, t in enumerate((glass_t0, glass_t0 + (glass_t1 - glass_t0) / 3,
                           glass_t0 + 2 * (glass_t1 - glass_t0) / 3, glass_t1)):
        verts = [east_point(max(glass_t0, t - 0.012 / east_len), 0.18, 0.25),
                 east_point(min(glass_t1, t + 0.012 / east_len), 0.18, 0.25),
                 east_point(min(glass_t1, t + 0.012 / east_len), 8.65, 0.25),
                 east_point(max(glass_t0, t - 0.012 / east_len), 8.65, 0.25)]
        make_mesh(f"TREC_Entry_Glazing_Mullion_{i}", verts, [(0, 1, 2, 3)], frame, asset)
    for j, z in enumerate((2.55, 4.25, 6.35)):
        facade_panel(f"TREC_Entry_Glazing_Horizontal_Mullion_{j}", glass_t0, glass_t1,
                     z, z + 0.08, frame, offset=0.26)
    # Double doors at grade within the photographed glazed vestibule.
    entry_t = (glass_t0 + glass_t1) / 2
    for side, delta in (("Left", -ENTRY_WIDTH_M / (4 * east_len)),
                        ("Right", ENTRY_WIDTH_M / (4 * east_len))):
        t0, t1 = entry_t + delta - ENTRY_WIDTH_M / (4 * east_len), entry_t + delta + ENTRY_WIDTH_M / (4 * east_len)
        facade_panel(f"TREC_Entry_Door_{side}", t0, t1, 0.15, ENTRY_HEIGHT_M, entrymat, offset=0.29)
    canopy_center = east_point(entry_t, 4.25, 0.72)
    canopy_obj = box("TREC_Entry_Projecting_Canopy", canopy_center,
                     (2.2, east_len * (glass_t1 - glass_t0) + 0.8, 0.34), canopy, asset)
    canopy_obj.rotation_euler.z = east_theta

    # The panorama also sees the glazed entry wrapping the northeast corner
    # from the north approach. The irregular GIS gable edge has no surveyed
    # curtain-wall breakdown, so this broad glazed return is approximate.
    north_front_y = max(p[1] for p in footprint if p[0] > cx) + 0.10
    north_glass_x0, north_glass_x1 = maxx - 9.0, maxx - 0.35
    north_glass = [
        (north_glass_x0, north_front_y, 0.18),
        (north_glass_x1, north_front_y, 0.18),
        (north_glass_x1, north_front_y, 8.65),
        (north_glass_x0, north_front_y, 8.65),
    ]
    make_mesh("TREC_North_Corner_Entry_Glazing", north_glass, [(0, 1, 2, 3)], glass, asset)
    for i in range(5):
        x = north_glass_x0 + (north_glass_x1 - north_glass_x0) * i / 4
        verts = [(x - 0.035, north_front_y + 0.04, 0.18),
                 (x + 0.035, north_front_y + 0.04, 0.18),
                 (x + 0.035, north_front_y + 0.04, 8.65),
                 (x - 0.035, north_front_y + 0.04, 8.65)]
        make_mesh(f"TREC_North_Entry_Mullion_{i}", verts, [(0, 1, 2, 3)], frame, asset)
    for i, z in enumerate((2.55, 4.25, 6.35)):
        verts = [(north_glass_x0, north_front_y + 0.05, z),
                 (north_glass_x1, north_front_y + 0.05, z),
                 (north_glass_x1, north_front_y + 0.05, z + 0.08),
                 (north_glass_x0, north_front_y + 0.05, z + 0.08)]
        make_mesh(f"TREC_North_Entry_Horizontal_Mullion_{i}", verts, [(0, 1, 2, 3)], frame, asset)
    north_canopy = box("TREC_North_Entry_Projecting_Canopy",
                       ((north_glass_x0 + north_glass_x1) / 2, north_front_y + 0.75, 4.25),
                       (north_glass_x1 - north_glass_x0 + 0.8, 2.2, 0.34), canopy, asset)

    # East-side openings visible in the panorama. Their relative stations are
    # approximate; the source is a perspective panorama, not an elevation.
    facade_panel("TREC_East_Wall_Window_Glazing", 0.48, 0.535, 1.18, 2.42, glass, offset=0.22)
    for name, t in (("WindowLeft", 0.48), ("WindowRight", 0.535)):
        facade_panel(f"TREC_{name}_Frame_Left", t, t + 0.006, 1.12, 2.48, frame, offset=0.27)
        facade_panel(f"TREC_{name}_Frame_Right", t + 0.049, t + 0.055, 1.12, 2.48, frame, offset=0.27)
    for i, t in enumerate((0.53, 0.68, 0.82)):
        facade_panel(f"TREC_East_Wall_Louver_{i}_Frame", t, t + 0.075, 6.0, 7.0, frame, offset=0.22)
        facade_panel(f"TREC_East_Wall_Louver_{i}", t + 0.006, t + 0.069, 6.08, 6.92, louvermat, offset=0.26)
        for slat in range(6):
            z = 6.12 + slat * 0.13
            facade_panel(f"TREC_East_Wall_Louver_{i}_Slat_{slat}", t + 0.009, t + 0.066,
                         z, z + 0.035, ribmat, offset=0.29)
    for i, t in enumerate((0.58, 0.76)):
        facade_panel(f"TREC_East_Service_Door_{i}", t, t + 0.045, 0.08, 2.35,
                     entrymat, offset=0.23)

    # Gable roof ridge parallels the long north-south field axis. Height uses
    # 2018 QL2 LiDAR returns compared with nearby classified ground; because
    # most roof returns are unclassified and ground is sampled nearby, both
    # values remain approximate and are not surveyed building dimensions.
    roof_width = width + 2 * ROOF_OVERHANG_M
    roof_length = length + 2 * ROOF_OVERHANG_M
    ridge_z = RIDGE_HEIGHT_M
    eave_z = WALL_HEIGHT_M
    roof_verts = [
        (cx - roof_width / 2, cy - roof_length / 2, eave_z),
        (cx, cy - roof_length / 2, ridge_z),
        (cx + roof_width / 2, cy - roof_length / 2, eave_z),
        (cx + roof_width / 2, cy + roof_length / 2, eave_z),
        (cx, cy + roof_length / 2, ridge_z),
        (cx - roof_width / 2, cy + roof_length / 2, eave_z),
    ]
    make_mesh("TREC_Gabled_Metal_Roof_ESTIMATED", roof_verts,
              [(0, 1, 4, 5), (1, 2, 3, 4)], roofmat, asset)
    # Fascia / ridge caps distinguish roof edges without adding unsupported form.
    box("TREC_Ridge_Cap_ESTIMATED", (cx, cy, ridge_z + 0.055),
        (0.25, roof_length, 0.11), trim, asset)
    # The 2023 orthophoto shows repeated pale bands running east-west across the
    # short roof dimension, perpendicular to the north-south ridge. Spacing is
    # estimated visually; no construction drawings verify exact panel width.
    half_w = roof_width / 2
    rise = ridge_z - eave_z
    transverse_count = max(24, int(roof_length / 1.8))
    band_half_width = 0.025
    band_offset = 0.025
    for i in range(1, transverse_count):
        y = cy - roof_length / 2 + roof_length * i / transverse_count
        ya, yb = y - band_half_width, y + band_half_width
        for side, sign in (("west", -1), ("east", 1)):
            eave_x = cx + sign * half_w
            eave_band_z = eave_z + band_offset
            ridge_band_z = ridge_z + band_offset
            verts = [
                (eave_x, ya, eave_band_z), (cx, ya, ridge_band_z),
                (cx, yb, ridge_band_z), (eave_x, yb, eave_band_z),
            ]
            make_mesh(f"TREC_{side}_Roof_Transverse_Seam_{i:02d}", verts,
                      [(0, 1, 2, 3)], roof_seam, asset)

    # Camera and lights are used only for the evidence render and removed before
    # saving the portable collection library.
    cam_data = bpy.data.cameras.new("TREC_Preview_Camera")
    cam = bpy.data.objects.new("TREC_Preview_Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (cx + width * 1.30, cy + length * 1.05, ridge_z * 1.02)
    target = Vector((cx, cy, ridge_z * 0.36))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(width * 2.25, length * 1.4)
    scene.camera = cam
    lights = []
    for i, (loc, power, size) in enumerate([
        ((cx - 30, cy - 45, 52), 12000, 35),
        ((cx + 38, cy + 20, 38), 8500, 30),
    ]):
        ld = bpy.data.lights.new(f"TREC_Preview_Area_{i}", "AREA")
        ld.energy, ld.shape, ld.size = power, "DISK", size
        lo = bpy.data.objects.new(ld.name, ld)
        scene.collection.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector((cx, cy, 4.0)) - lo.location).to_track_quat("-Z", "Y").to_euler()
        lights.append(lo)

    available_engines = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in available_engines else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW_PATH)
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.58, 0.64, 0.68, 1.0)
    bg.inputs["Strength"].default_value = 0.65
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.6
    scene.view_settings.gamma = 1.0
    scene.render.film_transparent = False
    # Save complementary views so the grader can assess roof plan and gable
    # profile independently of the oblique hero view.
    render_views = [
        (PREVIEW_PATH, (cx + width * 1.30, cy + length * 1.05, ridge_z * 1.02), Vector((cx, cy, ridge_z * 0.36)), max(width * 2.25, length * 1.4)),
        (PREVIEW_TOP_PATH, (cx, cy, max(length * 1.25, 95)), Vector((cx, cy, 0)), max(width * 2.4, length * 1.8)),
        (PREVIEW_NORTH_PATH, (cx, maxy + length * 1.25, ridge_z * 0.60), Vector((cx, cy, ridge_z * 0.50)), max(width * 1.55, 65)),
        (PREVIEW_EAST_PATH, (cx + width * 1.55, cy + length * 0.68, WALL_HEIGHT_M * 0.82), Vector((cx, cy, WALL_HEIGHT_M * 0.46)), max(length * 1.30, 100)),
    ]
    for render_path, location, view_target, scale in render_views:
        cam.location = location
        cam.rotation_euler = (view_target - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.data.ortho_scale = scale
        scene.render.filepath = str(render_path)
        bpy.ops.render.render(write_still=True)

    for obj in [cam, *lights]:
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.camera = None
    # The asset collection is the only geometry collection exported.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    evidence = {
        "building_id": BUILDING_ID,
        "building_name": "Turf Recreation Exercise Center (TREC)",
        "owner": "Rossen",
        "assignment_crosswalk": {
            "readme_assignment": "README.md chapter assignment row; Rossen",
            "readme_gis_feature_id": 863,
            "stable_asset_id": BUILDING_ID,
            "official_purdue_campus_gis_objectid": props["OBJECTID"],
            "official_purdue_abbr": props["ABBR"],
            "identity_note": "The official Purdue CampusBuilding feature by name and ABBR is TREC OID 312. It is not the separate Intercollegiate Athletic Sports Turf Building (official OID 1287) and not the nearby CoRec/Aquatic Center.",
        },
        "sources": [
            {
                "url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/FeatureServer/0/query?objectIds=312&outFields=*&returnGeometry=true&outSR=4326&f=geojson",
                "provider": "Purdue University Libraries GIS, Purdue CampusBuilding FeatureServer layer 0",
                "feature_id": "OBJECTID 312; ABBR TREC",
                "retrieved": "2026-10-26",
                "source_date": "Feature attributes: built 2011; construction 2010-2011; retrieved from live GIS on 2026-10-26",
                "crs": "EPSG:4326 response from source service EPSG:102100/Web Mercator",
                "measurement_method": "Polygon vertices converted with project's documented local approximation; computed ring area compared with GIS Shape__Area and squarefootage attributes, whose differing values are reported separately",
                "uncertainty": "GIS roof outline supports location and plan perimeter; it does not establish structural wall setbacks or roof overhangs.",
                "snapshot": "sources/purdue_gis_trec_oid312_2026-10-26.geojson",
            },
            {
                "url": "https://www.purdue.edu/recwell/visit/facility/fact-sheet.php",
                "provider": "Purdue Recreation & Wellness",
                "feature_id": "Turf Recreation Exercise Center (TREC)",
                "retrieved": "2026-10-26",
                "source_date": "Current webpage; fact sheet dates project opening to October 2012",
                "crs": "Not applicable",
                "measurement_method": "Published facility areas and facility-use description",
                "uncertainty": "No facade elevations, structural dimensions, floor count, or height are published on this fact sheet.",
                "snapshot": "sources/purdue_recwell_facility_fact_sheet.html",
            },
            {
                "url": "https://www.purdue.edu/recwell/visit/index.php",
                "provider": "Purdue Recreation & Wellness",
                "feature_id": "TREC facility description",
                "retrieved": "2026-10-26",
                "source_date": "Current webpage",
                "crs": "Not applicable",
                "measurement_method": "Published field dimensions and indoor-use description",
                "uncertainty": "Field dimensions describe playing surface, not building envelope or roof height.",
                "snapshot": "sources/purdue_recwell_visit.html",
            },
            {
                "url": "https://www.flickr.com/photos/127125088@N05/albums/72157674007617941",
                "provider": "AIA Columbus project album; photographer James West, JWest Productions, LLC",
                "feature_id": "France A. Cordova Recreational Sports Center Expansion & Renovation; project-wide 14-photo album",
                "retrieved": "2026-10-26",
                "source_date": "Album metadata; project is 2013 renovation/expansion",
                "crs": "Not applicable",
                "measurement_method": "Checked album attribution and photo labels for TREC-specific identification; the album names the overall CoRec expansion and does not label individual photos as TREC or provide building elevations. It is not used to assert TREC facade, openings, roof profile, or height.",
                "uncertainty": "The album covers the larger CoRec expansion/renovation. No TREC-specific caption or photo identity was established.",
                "snapshot": "sources/aia_columbus_crec_renovation_photo_album.html",
            },
            {
                "url": "https://moodynolan.com/projects/france-a-cordova-recreational-sports-center/",
                "provider": "Moody Nolan, project architect",
                "feature_id": "France A. Cordova Recreational Sports Center project page; page identifies 420,000 SF overall project",
                "retrieved": "2026-10-26",
                "source_date": "Current project page; completion year 2013",
                "crs": "Not applicable",
                "measurement_method": "Checked project page for TREC-specific imagery, elevations, and scope. Page discusses the five-level CREC/CoRec as a whole; its 420,000 SF scale and design descriptions are not applied to the separate TREC hall.",
                "uncertainty": "No TREC-specific section, height, or exterior facade specification is provided on this project page.",
                "snapshot": "Web page readable through search/open tool; direct HTML retrieval blocked by Cloudflare.",
            },
            {
                "url": "https://www.purdue.edu/bands/10-million-gift-sets-the-stage-for-new-bands-and-orchestras-building/",
                "provider": "Purdue Bands & Orchestras",
                "feature_id": "TREC expansion adjacent to Hull Field",
                "retrieved": "2026-10-26",
                "source_date": "2020-02-17 announcement; describes planned TREC expansion, not an as-built elevation",
                "crs": "Not applicable",
                "measurement_method": "Project-description cross-check for current campus use and possible expansion functions",
                "uncertainty": "The article states a planned expansion for restrooms, changing, band storage and bad-weather practice; this pass did not find as-built drawings confirming which elements were completed or their geometry.",
                "snapshot": "sources/purdue_bands_trec_expansion_2020.html",
            },
            {
                "url": "https://www.purdue.edu/campus-map/graphics/campusmap.pdf",
                "provider": "Purdue University Campus Map",
                "feature_id": "TREC, grid D6",
                "retrieved": "2026-10-26",
                "source_date": "PDF downloaded from Purdue current campus-map endpoint; PDF has no explicit issue date visible",
                "crs": "Campus grid D6, not a coordinate system",
                "measurement_method": "Name and adjacent-campus identity cross-check",
                "uncertainty": "Grid location is not a surveyed placement measure.",
                "snapshot": "sources/purdue_campus_map.pdf",
            },
            {
                "url": "https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer/exportImage?bbox=-9676470,4928260,-9676210,4928520&bboxSR=3857&imageSR=3857&size=1200,1200&format=jpg&f=image",
                "provider": "Indiana Geographic Information Office (IGIO), Indiana 2023 Orthophotography ImageServer",
                "feature_id": "TREC roof in a 260 m x 260 m orthophoto crop around 1252 Third Street",
                "retrieved": "2026-10-26",
                "source_date": "Spring 2023 orthophotography for Indiana's western acquisition tier",
                "crs": "EPSG:3857; output bbox [-9676470, 4928260, -9676210, 4928520], 1200 x 1200 pixels",
                "measurement_method": "Registered Purdue GIS and OSM outline vertices to exported orthophoto extent; aerial roof-ridge direction, pale roof and transverse east-west banding observed visually",
                "uncertainty": "Orthophoto verifies roof plan outline and direction, not wall elevations, entry positions, roof height, or precise seam spacing. CC0 statewide orthophoto product.",
                "snapshot": "sources/indiana_2023_orthophoto_trec.jpg; orthophoto_footprint_overlay.png; footprint_imagery_comparison.json",
            },
            {
                "url": "https://api.openstreetmap.org/api/0.6/way/283275002/full.json",
                "provider": "OpenStreetMap contributors",
                "feature_id": "Way 283275002; name=Turf Recreation Exercise Center; ref=TREC",
                "retrieved": "2026-10-26",
                "source_date": "Way last edited 2021-04-30; nodes included in raw snapshot",
                "crs": "WGS 84 geographic coordinates (EPSG:4326)",
                "measurement_method": "Independent name and building-footprint identity cross-check; not used to replace the Purdue campus GIS survey perimeter",
                "uncertainty": "OpenStreetMap way has building=yes and leisure=sports_centre tags but no height, levels, roof shape, or facade material tags.",
                "snapshot": "sources/osm_trec_way_283275002_2026-10-26.json",
            },
            {
                "url": "https://www.purdue.edu/recwell/visit/ada-accessibility.php",
                "provider": "Purdue Recreation & Wellness",
                "feature_id": "TREC facility entrance/access description",
                "retrieved": "2026-10-26",
                "source_date": "Current webpage",
                "crs": "Not applicable; textual facility access description",
                "measurement_method": "Page states TREC and Aquatics entrances are located on the circle drive west of CoRec and are at grade. The July 2023 Google Street View panorama independently shows the glazed entrance on the east/northeast approach facing the circle drive; facade position in the model is aligned approximately to the observed northeast/east corner.",
                "uncertainty": "Supports an at-grade TREC entrance on the circle-drive side. Exact bay, width, height, glazing grid and canopy dimensions are estimated from a perspective panorama, not published dimensions.",
                "snapshot": "sources/purdue_recwell_ada_accessibility.html",
            },
            {
                "url": "https://archives.lib.purdue.edu/repositories/2/accessions/3165",
                "provider": "Purdue University Archives and Special Collections",
                "feature_id": "Accession 2026-186, Purdue University Archives photograph collection, 2026 addition; accession inventory explicitly lists Turf Recreation Exercise Center",
                "retrieved": "2026-10-26",
                "source_date": "Creation dates 2000-2015; transferred to Archives in 2026",
                "crs": "Not applicable",
                "measurement_method": "Reviewed accession-level catalog/search-index metadata. The record describes an unprocessed digital folder of 661 files (4.07 GB) and inventory names TREC, but exposes no item-level filenames, thumbnails, captions, or individual access links. Cross-checked Campus Facilities and Buildings Historic Database record 165 (GIS OID 312), which has image_url=null and images=[].",
                "uncertainty": "The existence of TREC photographs is confirmed at accession level, but no photo content can be attributed to an exterior, entrance, roof, or specific facade. The Archives page returned HTTP 403 in the connected web reader and the folder is unprocessed. No facade details are inferred from this source.",
                "snapshot": "sources/purdue_archives_2026-186_search_index_extract.txt; sources/purdue_archives_2026-186_access_record.json",
            },
            {
                "url": "https://purduesports.com/baseball-recruiting-headquarters",
                "provider": "Purdue University Athletics, official Baseball facilities page",
                "feature_id": "TREC section; three linked photo elements labeled TRec",
                "retrieved": "2026-10-26",
                "source_date": "Image storage paths dated 2025-05-16; page copyright 2026",
                "crs": "Not applicable",
                "measurement_method": "The official page places three images alt-labeled TRec under its TREC heading and describes TREC as an indoor AstroTurf field. All three linked 300 x 198 pixel images were opened and visually inspected in Chrome. They depict indoor field views with artificial turf and overhead metal roof framing; none shows the exterior or entrance.",
                "uncertainty": "These images support an unobstructed field hall and visible interior roof framing only; no exterior facade geometry or material is inferred from them.",
                "snapshot": "sources/purdue_athletics_trec_photo_gallery_access.txt",
            },
            {
                "url": "https://www.google.com/maps/@40.428913,-86.9239926,3a,75y,206.01h,90t/data=!3m5!1e1!3m3!1sCKWL7p3cJEsDPH5hReovcw!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3DCKWL7p3cJEsDPH5hReovcw%26yaw%3D206.00749!5m1!1e1",
                "provider": "Google Maps Street View",
                "feature_id": "Pano ID CKWL7p3cJEsDPH5hReovcw; labeled place Turf Recreation Exercise Center, 1252 3rd Street",
                "retrieved": "2026-10-26",
                "source_date": "Panorama capture: July 2023 (Google Maps visible date label)",
                "crs": "WGS 84 panorama camera position 40.428913, -86.9239926; displayed heading/yaw 206.01 degrees; 75 degree horizontal field of view",
                "measurement_method": "Directly opened the Google Maps place photo into Street View and inspected the visible panorama pixels facing the TREC northeast/east corner. Observed red-brown brick lower wall, pale vertical-rib metal upper wall, corner glazing, a projecting canopy, wall vents, one window, and service doors. Facade element stationing, heights, and dimensions in the model are approximate visual estimates, not surveyed measurements.",
                "uncertainty": "One perspective panorama supports facade material/color and visible feature types on the east/northeast approach. It does not provide a rectified elevation or exact dimensions, and the far side and rear facade remain unverified. The panorama point is about 9 m northeast of the Purdue GIS northeast corner.",
                "snapshot": "sources/google_street_view_trec_search_access.txt (metadata and visual inspection log; source imagery remains at Google Maps)",
            },
            {
                "url": "https://lidar.digitalforestry.org/QL2_3DEP_LiDAR_IN_2017_2019/Tippecanoe_Co_2018_3DEP/Elev18_LAS1.4SPW_IN/copc/in2018_29951885_12.copc.laz",
                "provider": "Indiana statewide 3DEP LiDAR (Indiana Geographic Information Office / IndianaMap distribution; public tile mirror)",
                "feature_id": "COPC tile in2018_29951885_12.copc.laz; Purdue TREC roof returns within OSM way 283275002",
                "retrieved": "2026-10-26",
                "source_date": "2018 county collection; LAS tile published in the Tippecanoe County 2018 3DEP product directory",
                "crs": "EPSG:2968 NAD83(HARN) Indiana West, US survey feet; NAVD88 Geoid12B vertical, US survey feet",
                "measurement_method": "Filtered 7,529 non-ground returns inside the OSM TREC ring and compared them with 12,968 class-2 ground returns in a 60 ft surrounding window. Across-width 12-bin medians rise from 9.693 m and 9.665 m in the outer bins to a 14.373 m central-bin maximum; values are relative to the surrounding class-2 ground median of 619.28 ft. Because roof returns are class 1/unclassified and ground uses a nearby median, the modeled 9.7 m eave and 14.4 m ridge are LiDAR-derived estimates, not surveyed heights.",
                "uncertainty": "No class-6 building returns occur inside either footprint. Outermost bins include non-roof/ground returns, and nearby ground varies p05-p95 from 617.98-620.78 ft. Quantile-based profile provides a roof-height envelope, not exact eave or ridge survey measurements.",
                "snapshot": "sources/indiana_2018_lidar_trec_tile_29951885_12.copc.laz; lidar_height_analysis.json; analyze_lidar_trec.py",
            },
        ],
        "measured_geometry": {
            "campus_coordinate_frame": "project approximate local frame; meters; X east, Y north; origin 40.4274,-86.9137",
            "gis_objectid": props["OBJECTID"],
            "source_vertex_count": len(footprint),
            "bounds_m": [[minx, maxx], [miny, maxy], [0.0, RIDGE_HEIGHT_M]],
            "footprint_bounds_m": {"east_west": width, "north_south": length},
            "gis_ring_plan_area_m2_computed": footprint_m2,
            "gis_ring_plan_area_sqft_computed": footprint_m2 / 0.09290304,
            "gis_shape_area_attribute": props["Shape__Area"],
            "official_reported_squarefootage": props["squarefootage"],
            "recwell_fact_sheet_project_size_sqft": 29037,
            "area_discrepancy_note": "GIS ring area, GIS squarefootage attribute, and RecWell project-size figure differ; these may use different measurement conventions. No source found that reconciles them, so they are recorded separately and none is substituted for the GIS perimeter.",
            "roof_overhang_m": ROOF_OVERHANG_M,
            "footprint_vertex_comparison": "Model exterior wall perimeter follows all source GIS vertices; facade components intentionally do not alter the GIS ring.",
        },
        "footprint_source_comparison": {
            "official_purdue_gis_bounds_m": [[minx, maxx], [miny, maxy]],
            "official_purdue_gis_area_m2_computed": footprint_m2,
            "osm_way_id": 283275002,
            "osm_bounds_m": osm_bounds,
            "osm_area_m2_computed": osm_area_m2,
            "dimension_comparison_m": {
                "purdue_gis_east_west_width": width,
                "osm_east_west_width": osm_bounds[0][1] - osm_bounds[0][0],
                "gis_minus_osm_width": width - (osm_bounds[0][1] - osm_bounds[0][0]),
                "purdue_gis_north_south_length": length,
                "osm_north_south_length": osm_bounds[1][1] - osm_bounds[1][0],
                "gis_minus_osm_length": length - (osm_bounds[1][1] - osm_bounds[1][0]),
            },
            "reported_area_comparison_sqft": {
                "purdue_gis_ring_area_computed": footprint_m2 / 0.09290304,
                "purdue_gis_squarefootage_attribute": props["squarefootage"],
                "purdue_treasurer_building_list_oct2021": 36545.51,
                "recwell_project_size_fact_sheet": 29037,
                "status": "unresolved across four published/computed figures; likely different definitions or scopes",
            },
            "prior_manifest_bounds_m": prior_bounds,
            "official_gis_center_minus_prior_asset_center_m": [gis_center[i] - prior_center[i] for i in range(2)],
            "note": "The prior manifest bounds match the 2021 OSM way bounds exactly, while current Purdue GIS OID 312 is about 2.376 m west, 0.443 m south, and 1.212 m narrower east-west. The orthophoto shows both outlines on the same TREC roof: OSM tracks the visible roof edge more closely on the east side, while Purdue GIS is displaced west and extends beyond the visible roof on portions of the west side. This is not explained by a simple uniform roof-overhang offset; no source establishes which perimeter is the structural wall line. The rebuild retains the named current Purdue GIS polygon as the primary wall footprint, keeps the OSM outline as an explicit roof-edge alternative, and reports the position conflict for coordinator review. Ring areas are close, but four area measures differ: computed GIS ring about 34,124 sq ft, GIS squarefootage attribute 36,210 sq ft, Purdue Treasurer Oct 2021 building-list area 36,545.51 sq ft, and RecWell project-size figure 29,037 sq ft. Their definitions/scopes are unresolved.",
        },
        "orthophoto_observation": imagery_report["registration"],
        "vertical_geometry": {
            "wall_height_m": WALL_HEIGHT_M,
            "ridge_height_m": RIDGE_HEIGHT_M,
            "status": "estimated, not measured",
            "basis": "2018 Indiana QL2 LiDAR return profile inside the OSM roof ring compared with nearby classified ground. Outer-bin medians are 9.693 m and 9.665 m; central-bin median reaches 14.373 m. These support approximate 9.7 m eave and 14.4 m ridge values but do not measure a surveyed wall/eave plane because roof returns are unclassified and ground is sampled nearby.",
            "lidar_sample": {
                "source_tile": "in2018_29951885_12.copc.laz",
                "osm_ring_non_ground_returns": 7529,
                "classified_nearby_ground_returns": 12968,
                "nearby_ground_median_ft_navd88": 619.28,
                "roof_cross_section_edge_medians_m_above_nearby_ground": [9.693, 9.665],
                "central_cross_section_median_m_above_nearby_ground": 14.373,
                "class6_returns_inside_gis_or_osm": 0,
                "measurement_status": "LiDAR-derived roof-profile estimate; not surveyed building heights"
            },
        },
        "design_decisions_and_uncertainty": [
            "Purdue RecWell identifies a dedicated indoor synthetic turf field, and the official GIS identifies the separate TREC building at 1252 Third Street. The model therefore depicts one long clear-span field hall rather than the adjacent multistory CoRec or Aquatic Center.",
            "The RecWell fact sheet identifies TREC as 29,037 sq ft (25,929 sq ft turf, 2,554 sq ft locker rooms, 554 sq ft office/control), and the facility page states a 60 yd x 40 yd indoor artificial turf field. These establish use and program areas, but do not provide exterior height or room placement.",
            "The 2023 orthophoto confirms a long north-south ridge, two roof planes, a pale roof and repeated east-west bands perpendicular to the ridge. It does not reveal roof height. The model uses this observed roof plan and transverse seam rhythm on a light-gray roof surface.",
            "The AIA Columbus album and Moody Nolan page cover the larger France A. Cordova CoRec expansion/renovation, not a specifically identified TREC facade. Their imagery and design descriptions are excluded from TREC geometry/material claims.",
            "Purdue RecWell accessibility text places the at-grade TREC entry on the circle drive west of CoRec. The July 2023 TREC-specific Street View panorama shows a glazed entry at the northeast/east corner on that approach. The model adds the observed corner glazing and canopy; exact bay, dimensions and glazing grid are estimated from perspective.",
            "2018 QL2 LiDAR supports a roof profile of roughly 9.7 m at the eaves and 14.4 m at the ridge above nearby ground. These are estimates rather than surveyed building dimensions; no published TREC section or elevation was found.",
            "The red Purdue GIS ring is shifted relative to the blue OSM ring and neither one yields a consistent symmetric roof-overhang interpretation against the orthophoto. The modeled walls retain the official named GIS ring; roof-overhang and exact wall-to-roof relationship remain unresolved.",
            "Purdue Archives accession 2026-186 is an unprocessed 4.07 GB/661-file digital folder whose inventory lists TREC among photographed buildings. However, no TREC-specific filenames, captions, thumbnails, or item-level links are exposed; the accession page returned HTTP 403. The Historic Database TREC record 165 has image_url=null and images=[]. The accession confirms that photographs exist at collection level, but no visible photo can be attributed to a TREC exterior or entrance, so no facade geometry or material is inferred. See the accession search-index extract and access-record JSON in the sources folder.",
            "All three official Purdue Athletics TREC-linked photos were opened directly. They are interior field views showing artificial turf and overhead metal roof framing; no exterior is visible, so they do not support facade details.",
            "A Google Maps Street View panorama labeled from the official TREC place listing provides TREC-specific exterior pixels. Metadata: panorama CKWL7p3cJEsDPH5hReovcw, capture date July 2023, camera at 40.428913,-86.9239926, yaw 206.01 degrees. The east/northeast-facing view shows red-brown brick base, light vertically ribbed metal above, a glazed corner entry and projecting canopy, one visible window, service doors and wall louvers. The model uses these observed facade types; stationing, heights and dimensions are approximate. Only the viewed side is supported; unseen facades remain unverified. See the updated Google Street View access/inspection record in sources.",
        ],
        "validation": {
            "saved_asset": "modular/buildings/massing_turf_recreation_exercise_center_9622f45.blend",
            "preview": "preview.png",
            "rendered_views": ["preview.png", "preview_top.png", "preview_north_gable.png", "preview_east_entry.png"],
            "reopened_check": "passed; see audit/massing_turf_recreation_exercise_center_9622f45/reopen_validation.json",
            "reviewer": "Builder direct reopen in Blender 4.5.15; independent grading pending",
        },
    }
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    rebuild_record = {
        "building_id": BUILDING_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)),
        "stable_collection": COLLECTION_NAME,
        "source_feature": {"provider": "Purdue University Libraries GIS", "objectid": props["OBJECTID"], "abbr": props["ABBR"], "name": props["Name"]},
        "prior_manifest_bounds_world_m": prior_bounds,
        "new_gis_wall_footprint_bounds_m": [[minx, maxx], [miny, maxy], [0.0, WALL_HEIGHT_M]],
        "new_roof_bounds_pre_overhang_m": [[minx, maxx], [miny, maxy], [0.0, RIDGE_HEIGHT_M]],
        "old_to_new_footprint_center_shift_m": [gis_center[i] - prior_center[i] for i in range(2)],
        "footprint_metrics": {"prior_osm_area_m2": osm_area_m2, "new_purdue_gis_area_m2": footprint_m2, "prior_osm_vertices_including_closure": len(osm_points), "new_purdue_gis_vertices_excluding_closure": len(footprint)},
        "reported_area_figures_sqft": {"purdue_gis_ring_computed": footprint_m2 / 0.09290304, "purdue_gis_squarefootage_attribute": props["squarefootage"], "purdue_treasurer_building_list_oct2021": 36545.51, "recwell_project_size": 29037},
        "area_discrepancy_note": "These figures differ and are not reconciled by the sources. The rebuild follows the official Purdue GIS footprint rather than forcing geometry to fit an area statistic.",
        "imagery_source": "Indiana 2023 orthophoto and Google Street View panorama CKWL7p3cJEsDPH5hReovcw (July 2023); see footprint_imagery_comparison.json, orthophoto_footprint_overlay.png and sources/google_street_view_trec_search_access.txt",
        "geometry_change": "Rebuilt wall perimeter from the current named Purdue GIS polygon; used 2018 QL2 LiDAR profile for estimated 9.7 m eaves and 14.4 m ridge; modeled the observed light two-plane roof, north-south ridge and east-west transverse bands. Added the TREC Street View-observed east-side brick base, pale vertical-rib metal cladding, approximate glazed northeast-corner entrance and canopy, window, wall louvers and service doors. Facade component stationing and dimensions are visual estimates from one perspective panorama. Kept the GIS/OSM roof-perimeter conflict explicit rather than forcing an unsupported overhang interpretation.",
        "placement_convention": "Preserves stable asset ID/path and direct campus-coordinate collection geometry. No manifest or master placement edits were made.",
        "status": "candidate awaiting independent grade and coordinator-owned shared-index update",
    }
    (ROOT / "audit" / BUILDING_ID / "rebuild_record.json").write_text(json.dumps(rebuild_record, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build()
