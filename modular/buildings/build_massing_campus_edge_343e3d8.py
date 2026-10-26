"""Build a source-backed Campus Edge on Pierce library in campus coordinates.

Sources and the measurement record live in
audit/massing_campus_edge_343e3d8/. The 2018 Indiana LiDAR outline anchors the
plan; the building's measured height is not known, so the LiDAR NDHM roof
surface is used only as an approximate height reference. This is a simple
massing asset and therefore retains the manifest's campus-world coordinate
contract and exported collection name.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_campus_edge_343e3d8"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / ASSET_ID
SOURCE = EVIDENCE / "sources" / "indiana_2016_2020_building_footprints_point_query_2026-10-25.json"
NDHM_SUMMARY = EVIDENCE / "campus_edge_ndhm_analysis.json"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

# Indiana's 2018 normalized height raster gives a 36.12 m median over the
# Campus Edge outline. The roof datum is approximate; 10 levels are visually
# inferred from the official exterior image, not measured from plans.
BUILDING_HEIGHT_M = 36.12
PODIUM_HEIGHT_M = 4.8
RESIDENTIAL_FLOORS = 9
RESIDENTIAL_FLOOR_TO_FLOOR_M = (BUILDING_HEIGHT_M - PODIUM_HEIGHT_M - 1.0) / RESIDENTIAL_FLOORS
PARAPET_HEIGHT_M = 1.0
SIMPLIFY_TOLERANCE_M = 0.30
FEET_TO_METERS = 1200.0 / 3937.0


def project_lon_lat(lon, lat):
    """Project EPSG:4326 with the campus's documented local approximation."""
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    return (x, y)


def point_segment_distance(point, start, end):
    px, py = point
    ax, ay = start
    bx, by = end
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def simplify_ring(points, tolerance):
    """Remove only near-collinear vertices while preserving the outline's notches."""
    pts = list(points)
    if len(pts) > 1 and math.dist(pts[0], pts[-1]) < 1e-8:
        pts.pop()
    changed = True
    while changed and len(pts) > 4:
        changed = False
        for i, point in enumerate(pts):
            prev_point = pts[(i - 1) % len(pts)]
            next_point = pts[(i + 1) % len(pts)]
            if point_segment_distance(point, prev_point, next_point) <= tolerance:
                pts.pop(i)
                changed = True
                break
    return pts


def signed_area(points):
    return 0.5 * sum(
        points[i][0] * points[(i + 1) % len(points)][1]
        - points[(i + 1) % len(points)][0] * points[i][1]
        for i in range(len(points))
    )


def point_in_polygon(x, y, points):
    inside = False
    j = len(points) - 1
    for i, (xi, yi) in enumerate(points):
        xj, yj = points[j]
        if (yi > y) != (yj > y):
            crossing_x = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < crossing_x:
                inside = not inside
        j = i
    return inside


def make_material(name, color, roughness=0.72, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return material


def create_mesh(name, vertices, faces, material, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if material:
        mesh.materials.append(material)
    return obj


def create_prism(name, points, z0, z1, side_material, roof_material, collection):
    n = len(points)
    vertices = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    faces.append(tuple(range(n, 2 * n)))
    faces.append(tuple(reversed(range(n))))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(side_material)
    mesh.materials.append(roof_material)
    for poly in mesh.polygons:
        poly.material_index = 1 if len(poly.vertices) == n and min(v for v in poly.vertices) >= n else 0
    return obj


def box_vertices(center, dimensions, angle):
    cx, cy, cz = center
    width, depth, height = dimensions
    c, s = math.cos(angle), math.sin(angle)
    verts = []
    for z in (-height / 2, height / 2):
        for y in (-depth / 2, depth / 2):
            for x in (-width / 2, width / 2):
                verts.append((cx + x * c - y * s, cy + x * s + y * c, cz + z))
    return verts


BOX_FACES = (
    (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
    (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3),
)


def add_box(buffer, center, dimensions, angle=0.0):
    verts = box_vertices(center, dimensions, angle)
    offset = len(buffer["verts"])
    buffer["verts"].extend(verts)
    buffer["faces"].extend(tuple(offset + index for index in face) for face in BOX_FACES)


def create_box_batch(name, buffer, material, collection):
    if not buffer["verts"]:
        return None
    return create_mesh(name, buffer["verts"], buffer["faces"], material, collection)


def ensure_output():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    preview_collection = bpy.data.collections.new("Campus_Edge_Preview_Setup")
    scene.collection.children.link(preview_collection)
    return scene, collection, preview_collection


def load_footprint():
    data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    feature = data["features"][0]
    ring = feature["geometry"]["coordinates"][0]
    projected = [project_lon_lat(lon, lat) for lon, lat in ring]
    return simplify_ring(projected, SIMPLIFY_TOLERANCE_M), feature


def make_building(scene, collection, points, feature):
    brick = make_material("CE_Warm_Red_Brick", (0.37, 0.13, 0.095))
    dark_brick = make_material("CE_Deep_Brick", (0.24, 0.075, 0.055))
    charcoal = make_material("CE_Graphite_Metal_Panels", (0.30, 0.34, 0.37), metallic=0.12)
    light_panel = make_material("CE_Light_Grey_Panels", (0.56, 0.60, 0.62), metallic=0.08)
    glass = make_material("CE_Blue_Grey_Glazing", (0.075, 0.16, 0.21), roughness=0.22, metallic=0.05)
    frame = make_material("CE_Aluminium_Window_Frames", (0.66, 0.68, 0.66), metallic=0.18)
    balcony_rail = make_material("CE_Balcony_Glass_Rails", (0.31, 0.43, 0.47), roughness=0.2, metallic=0.1)
    concrete = make_material("CE_Podium_Concrete", (0.52, 0.52, 0.49))
    roof = make_material("CE_Flat_Roof", (0.48, 0.50, 0.49), roughness=0.9)
    equipment = make_material("CE_Rooftop_Mechanical_Equipment", (0.72, 0.73, 0.69), roughness=0.8)

    create_prism("CE_Continuous_Brick_Podium", points, 0.0, PODIUM_HEIGHT_M, brick, roof, collection)
    upper_top = BUILDING_HEIGHT_M - PARAPET_HEIGHT_M
    create_prism("CE_Residential_Tower_Shell", points, PODIUM_HEIGHT_M, upper_top, charcoal, roof, collection)
    create_prism("CE_Roof_Parapet", points, upper_top, BUILDING_HEIGHT_M, light_panel, roof, collection)

    # Batch repeated details into a few portable meshes instead of hundreds of
    # loose objects. Each elevation remains outside the stable campus outline.
    glass_batch = {"verts": [], "faces": []}
    frame_batch = {"verts": [], "faces": []}
    brick_batch = {"verts": [], "faces": []}
    band_batch = {"verts": [], "faces": []}
    balcony_batch = {"verts": [], "faces": []}
    railing_batch = {"verts": [], "faces": []}
    store_batch = {"verts": [], "faces": []}
    equipment_batch = {"verts": [], "faces": []}

    area = signed_area(points)
    exterior_sign = 1.0 if area < 0 else -1.0
    floor_step = RESIDENTIAL_FLOOR_TO_FLOOR_M
    facade_base = PODIUM_HEIGHT_M
    window_width = 1.55
    window_height = 1.78
    spacing = 3.35
    total_windows = 0
    total_balconies = 0
    frontage_edges = []

    for edge_index, start in enumerate(points):
        end = points[(edge_index + 1) % len(points)]
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy)
        if length < 2.3:
            continue
        tangent = (dx / length, dy / length)
        normal = (-tangent[1] * exterior_sign, tangent[0] * exterior_sign)
        angle = math.atan2(tangent[1], tangent[0])
        bay_count = max(1, int((length - 1.0) / spacing))
        is_east_frontage = normal[0] > 0.70 and length > 18.0
        is_south_frontage = normal[1] < -0.75 and length > 18.0
        if is_east_frontage or is_south_frontage:
            frontage_edges.append((edge_index, start, end, tangent, normal, angle, length, bay_count))

        # Ground-floor glazing and brick piers are photo-interpreted from the
        # property exterior; their exact door/window positions are not surveyed.
        ground_modules = max(1, int((length - 1.0) / 4.0))
        for bay in range(ground_modules):
            t = (bay + 0.5) / ground_modules
            cx = start[0] + dx * t + normal[0] * 0.09
            cy = start[1] + dy * t + normal[1] * 0.09
            z = 2.45
            add_box(store_batch, (cx, cy, z), (2.35, 0.16, 2.15), angle)
            if bay % 3 == 0:
                px = start[0] + dx * (bay / ground_modules) + normal[0] * 0.18
                py = start[1] + dy * (bay / ground_modules) + normal[1] * 0.18
                add_box(brick_batch, (px, py, PODIUM_HEIGHT_M / 2), (0.55, 0.26, PODIUM_HEIGHT_M), angle)

        # Repeated residential windows, wall-panel spandrels, and occasional
        # brick accents are qualitative interpretations of the official facade.
        for floor in range(RESIDENTIAL_FLOORS):
            floor_z = facade_base + floor * floor_step
            window_z = floor_z + 1.87
            band_z = floor_z + 0.10
            add_box(band_batch,
                    ((start[0] + end[0]) / 2 + normal[0] * 0.08,
                     (start[1] + end[1]) / 2 + normal[1] * 0.08,
                     band_z),
                    (length, 0.15, 0.18), angle)
            for bay in range(bay_count):
                t = (bay + 0.5) / bay_count
                cx = start[0] + dx * t + normal[0] * 0.11
                cy = start[1] + dy * t + normal[1] * 0.11
                add_box(glass_batch, (cx, cy, window_z), (window_width, 0.17, window_height), angle)
                frame_depth = 0.23
                frame_width = 0.095
                for side in (-1, 1):
                    off = side * (window_width / 2 - frame_width / 2)
                    add_box(frame_batch,
                            (cx + tangent[0] * off, cy + tangent[1] * off, window_z),
                            (frame_width, frame_depth, window_height + 0.10), angle)
                for off_z in (-window_height / 2, window_height / 2):
                    add_box(frame_batch, (cx, cy, window_z + off_z),
                            (window_width, frame_depth, frame_width), angle)
                if bay % 4 == 0:
                    # Red-brick vertical accents match the alternating brick
                    # and graphite bays visible in the official exterior image.
                    accent_width = 0.34
                    ax = cx + tangent[0] * (window_width / 2 + 0.27) + normal[0] * 0.04
                    ay = cy + tangent[1] * (window_width / 2 + 0.27) + normal[1] * 0.04
                    add_box(brick_batch, (ax, ay, facade_base + (RESIDENTIAL_FLOORS * floor_step) / 2),
                            (accent_width, 0.18, RESIDENTIAL_FLOORS * floor_step), angle)
                total_windows += 1

                # Balcony stacks are limited to outward-facing east/south
                # elevations, following the official oblique property photo.
                in_balcony_zone = (bay_count >= 7 and 1 <= bay <= bay_count - 2
                                   and (bay_count < 15 or (bay_count * 0.20 <= bay <= bay_count * 0.62)))
                if floor >= 1 and (is_east_frontage or is_south_frontage) and in_balcony_zone and bay % 2 == 0:
                    balcony_z = floor_z + 0.22
                    balcony_width = 2.15
                    balcony_depth = 1.05
                    bx = cx + normal[0] * 0.68
                    by = cy + normal[1] * 0.68
                    add_box(balcony_batch, (bx, by, balcony_z),
                            (balcony_width, balcony_depth, 0.18), angle)
                    rail_center = (bx + normal[0] * (balcony_depth / 2 - 0.06),
                                   by + normal[1] * (balcony_depth / 2 - 0.06),
                                   balcony_z + 0.65)
                    add_box(railing_batch, rail_center, (balcony_width, 0.07, 1.05), angle)
                    for side in (-1, 1):
                        sx = bx + tangent[0] * side * (balcony_width / 2 - 0.04) + normal[0] * 0.12
                        sy = by + tangent[1] * side * (balcony_width / 2 - 0.04) + normal[1] * 0.12
                        add_box(railing_batch, (sx, sy, balcony_z + 0.65), (0.07, balcony_depth, 1.05), angle)
                    total_balconies += 1

    # The official front view shows a projecting podium canopy and a recessed
    # glazed entry; the side and exact dimensions remain qualitative.
    if frontage_edges:
        # Use the longest south-facing wall as the broad podium frontage.
        entry_edge = max((e for e in frontage_edges if e[4][1] < -0.75), key=lambda e: e[6], default=None)
        if entry_edge:
            _, start, end, tangent, normal, angle, length, _ = entry_edge
            center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
            add_box(store_batch, (center[0] + normal[0] * 0.20, center[1] + normal[1] * 0.20, 2.25),
                    (3.4, 0.20, 3.0), angle)
            add_box(band_batch, (center[0] + normal[0] * 0.78, center[1] + normal[1] * 0.78, PODIUM_HEIGHT_M - 0.05),
                    (7.0, 1.4, 0.34), angle)
            for side in (-1, 1):
                px = center[0] + tangent[0] * side * 2.4 + normal[0] * 0.9
                py = center[1] + tangent[1] * side * 2.4 + normal[1] * 0.9
                add_box(brick_batch, (px, py, PODIUM_HEIGHT_M / 2), (0.45, 0.45, PODIUM_HEIGHT_M), angle)

    create_box_batch("CE_Ground_Floor_Glazing", store_batch, glass, collection)
    create_box_batch("CE_Repeated_Window_Glass", glass_batch, glass, collection)
    create_box_batch("CE_Window_Frames", frame_batch, frame, collection)
    create_box_batch("CE_Facade_Bands_and_Entry_Canopy", band_batch, concrete, collection)
    create_box_batch("CE_Brick_Accents", brick_batch, dark_brick, collection)
    create_box_batch("CE_Balcony_Slabs", balcony_batch, concrete, collection)
    create_box_batch("CE_Balcony_Rails", railing_batch, balcony_rail, collection)

    # Orthophoto shows rooftop plant/equipment clusters. Placement and height
    # are approximate; sizes and count are not individually measured.
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    for yi in range(1, 7):
        for xi in range(1, 5):
            x = min_x + (max_x - min_x) * xi / 5
            y = min_y + (max_y - min_y) * yi / 8
            if point_in_polygon(x, y, points):
                # Leave clear setbacks at the perimeter and use a sparse roof grid.
                if min(abs(x - min_x), abs(x - max_x), abs(y - min_y), abs(y - max_y)) < 5.5:
                    continue
                add_box(equipment_batch, (x, y, BUILDING_HEIGHT_M + 0.56), (1.8, 2.4, 1.12), 0.0)
    create_box_batch("CE_Rooftop_Mechanical_Units_Approximate", equipment_batch, equipment, collection)

    collection["asset_id"] = ASSET_ID
    collection["building_name"] = "Campus Edge on Pierce"
    collection["coordinate_contract"] = "Simple massing asset in campus world coordinates; X east, Y north, Z up, meters."
    collection["building_height_status"] = "approximate roof datum from 2018 NDHM; individual floor/story heights estimated"
    collection["footprint_source"] = "Indiana 2016-2020 LiDAR-derived Building Footprints objectid 407824; cross-checked with OSM way 886359911"
    collection["source_uncertainty"] = "Horizontal outline is a public LiDAR/OSM footprint, not a survey. Facade bays, entry, balconies, and roof equipment are qualitative interpretations."

    return {
        "source_feature_id": feature["properties"].get("objectid"),
        "footprint_vertex_count_raw": len(feature["geometry"]["coordinates"][0]) - 1,
        "footprint_vertex_count_built": len(points),
        "window_count": total_windows,
        "balcony_count": total_balconies,
        "building_height_m": BUILDING_HEIGHT_M,
        "podium_height_m": PODIUM_HEIGHT_M,
        "residential_floor_count_estimated": RESIDENTIAL_FLOORS,
        "residential_floor_to_floor_m_estimated": RESIDENTIAL_FLOOR_TO_FLOOR_M,
    }


def configure_preview(scene, preview_collection, points):
    ground = make_material("CE_Preview_Ground", (0.35, 0.37, 0.37), roughness=0.95)
    center_x = sum(p[0] for p in points) / len(points)
    center_y = sum(p[1] for p in points) / len(points)
    plane_mesh = bpy.data.meshes.new("CE_PreviewGroundMesh")
    plane_mesh.from_pydata([(center_x - 400, center_y - 400, -0.15),
                            (center_x + 400, center_y - 400, -0.15),
                            (center_x + 400, center_y + 400, -0.15),
                            (center_x - 400, center_y + 400, -0.15)], [], [(0, 1, 2, 3)])
    plane_mesh.materials.append(ground)
    plane = bpy.data.objects.new("CE_Preview_Ground_Plane", plane_mesh)
    preview_collection.objects.link(plane)

    world = bpy.data.worlds.new("CE_Preview_World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.68, 0.73, 0.78, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65
    scene.world = world

    light_data = bpy.data.lights.new("CE_Preview_Key", "AREA")
    light_data.energy = 18000
    light_data.shape = "DISK"
    light_data.size = 90
    light = bpy.data.objects.new("CE_Preview_Key", light_data)
    preview_collection.objects.link(light)
    light.location = (center_x - 60, center_y - 90, 150)

    camera_data = bpy.data.cameras.new("CE_Preview_Camera")
    camera_data.lens = 48
    camera = bpy.data.objects.new("CE_Preview_Camera", camera_data)
    preview_collection.objects.link(camera)
    camera.location = (center_x + 125, center_y - 145, 92)
    target = Vector((center_x, center_y, 16.5))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = 1360
    scene.render.resolution_y = 1020
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(EVIDENCE / "campus_edge_preview.png")
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(write_still=True)

    # A top view makes the source-derived footprint easy to compare directly.
    top_data = bpy.data.cameras.new("CE_Footprint_Camera")
    top_camera = bpy.data.objects.new("CE_Footprint_Camera", top_data)
    preview_collection.objects.link(top_camera)
    top_camera.data.type = "ORTHO"
    top_camera.data.ortho_scale = max(max(p[0] for p in points) - min(p[0] for p in points),
                                      max(p[1] for p in points) - min(p[1] for p in points)) * 1.25
    top_camera.location = (center_x, center_y, 220)
    top_camera.rotation_euler = (0.0, 0.0, 0.0)
    # Looking down the local -Z axis requires no additional camera rotation.
    scene.camera = top_camera
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.filepath = str(EVIDENCE / "campus_edge_footprint_preview.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = camera


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    scene, collection, preview_collection = ensure_output()
    points, feature = load_footprint()
    build_summary = make_building(scene, collection, points, feature)
    configure_preview(scene, preview_collection, points)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    result = {
        "building_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "scene": SCENE_NAME,
        "collection": COLLECTION_NAME,
        "campus_world_coordinates_m": True,
        "footprint_conversion": "project local approximation documented in modular/README.md; source geometry in WGS84",
        "build": build_summary,
        "asset_object_count": len(collection.objects),
        "asset_mesh_object_count": sum(1 for obj in collection.objects if obj.type == "MESH"),
        "preview_setup_object_count_outside_asset": len(preview_collection.objects),
        "height_status": "approximate roof datum from 2018 NDHM; per-floor datums and eaves estimated",
        "preview": "audit/massing_campus_edge_343e3d8/campus_edge_preview.png",
        "top_preview": "audit/massing_campus_edge_343e3d8/campus_edge_footprint_preview.png",
    }
    (EVIDENCE / "build_report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
