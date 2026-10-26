"""Build source-backed Cary Quadrangle South from official Purdue GIS."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_south_cqs_7ee2283"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / ASSET_ID
GEOJSON = EVIDENCE / "sources" / "purdue_building_shapes_fid653_cqs_2026-10-26.geojson"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

# The official polygon controls XY. Height and architecture below are visibly
# documented estimates because GIS extrusion units and exact elevations are
# not defined in the source service.
GROUND_Z = 0.0
WALL_EAVE_Z = 12.5
ROOF_Z = 16.3
TOWER_TOP_Z = 21.0


def project_lon_lat(lon, lat):
    """Repository's documented local approximation from WGS84 to campus m."""
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    return x, y


def point_line_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d2 = dx * dx + dy * dy
    if d2 < 1e-14:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / d2))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def simplify_open(points, tol):
    if len(points) <= 2:
        return points[:]
    a, b = points[0], points[-1]
    idx, maxd = -1, -1.0
    for i in range(1, len(points) - 1):
        d = point_line_distance(points[i], a, b)
        if d > maxd:
            idx, maxd = i, d
    if maxd <= tol:
        return [a, b]
    left = simplify_open(points[:idx + 1], tol)
    right = simplify_open(points[idx:], tol)
    return left[:-1] + right


def simplify_ring(points, tol=0.22):
    # Split the closed ring at a farthest point pair so Douglas-Peucker does not
    # collapse the closure edge. Re-close it after simplification.
    pts = list(points)
    if pts[0] == pts[-1]:
        pts.pop()
    i0 = max(range(len(pts)), key=lambda i: pts[i][0] + pts[i][1])
    i1 = max(range(len(pts)), key=lambda i: math.dist(pts[i], pts[i0]))
    if i0 > i1:
        i0, i1 = i1, i0
    first = pts[i0:i1 + 1]
    second = pts[i1:] + pts[:i0 + 1]
    one = simplify_open(first, tol)
    two = simplify_open(second, tol)
    result = one[:-1] + two[:-1]
    # Remove nearly collinear residual points without shifting the footprint
    # farther than the already recorded source simplification tolerance.
    changed = True
    while changed and len(result) > 8:
        changed = False
        for i, p in enumerate(result):
            if point_line_distance(p, result[i - 1], result[(i + 1) % len(result)]) < 0.045:
                result.pop(i)
                changed = True
                break
    return result


def polygon_area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1] -
                   points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) * 0.5)


def material(name, color, roughness=0.8):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (*color, 1.0)
    mat.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = roughness
    return mat


def cube_obj(name, center, dims, mat, coll, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Soft masonry arris", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        obj.modifiers.new("Weighted stone normals", "WEIGHTED_NORMAL")
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def make_body(ring, z0, z1, brick, roof, coll):
    # Segment quads provide a clean wall shell and prevent concave ngon issues.
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    # Cap using Blender's own polygon tessellator, preserving concavities.
    from mathutils.geometry import tessellate_polygon
    cap = tessellate_polygon([[Vector((x, y, 0.0)) for x, y in ring]])
    for tri in cap:
        ids = list(tri)
        faces.append(tuple(n + i for i in ids))
        faces.append(tuple(reversed(ids)))
    mesh = bpy.data.meshes.new("CQS GIS outline masonry")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(brick)
    mesh.materials.append(roof)
    mesh.update()
    obj = bpy.data.objects.new("Cary Quadrangle South (CQS)", mesh)
    coll.objects.link(obj)
    for i, p in enumerate(mesh.polygons):
        if i >= n:
            p.material_index = 1
    return obj


def make_gable_roof_rect(xmin, xmax, ymin, ymax, z_eave, z_ridge, mat, coll, ridge_axis):
    """Make an estimated roof bar without spanning the courtyard void."""
    xmin, xmax = xmin - 0.35, xmax + 0.35
    ymin, ymax = ymin - 0.35, ymax + 0.35
    if ridge_axis == "x":
        ym = (ymin + ymax) / 2
        verts = [(xmin, ymin, z_eave), (xmax, ymin, z_eave),
                 (xmax, ym, z_ridge), (xmin, ym, z_ridge),
                 (xmin, ymax, z_eave), (xmax, ymax, z_eave)]
        faces = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)]
    else:
        xm = (xmin + xmax) / 2
        verts = [(xmin, ymin, z_eave), (xmin, ymax, z_eave),
                 (xm, ymax, z_ridge), (xm, ymin, z_ridge),
                 (xmax, ymin, z_eave), (xmax, ymax, z_eave)]
        faces = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)]
    mesh = bpy.data.meshes.new("CQS gable roof wing")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(f"CQS slate gable roof {ridge_axis}", mesh)
    coll.objects.link(obj)
    return obj


def box_windows(x0, x1, yface, floors, count, floor_z, spacing, width, height, mat, coll, prefix):
    for i in range(count):
        x = x0 + (x1 - x0) * (i + 0.5) / count
        for floor in range(floors):
            z = floor_z + floor * spacing
            cube_obj(f"{prefix} window bay {i + 1:02d} floor {floor + 1}",
                     (x, yface, z), (width, 0.28, height), mat, coll, 0.06)


def pointed_arch_header(name, cx, y, z_spring, half_width, mat, coll):
    """Two pale stone diagonal voussoir masses approximate a pointed arch."""
    rise = half_width * 0.62
    length = math.hypot(half_width, rise)
    angle = math.atan2(rise, half_width)
    for side in (-1, 1):
        obj = cube_obj(f"{name} pointed arch arm {side}",
                       (cx + side * half_width / 2, y, z_spring + rise / 2),
                       (length, 0.42, 0.34), mat, coll, 0.04)
        obj.rotation_euler[1] = side * angle


def build():
    # Clear only this dedicated library scene. Keep expected scene and asset IDs.
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
    staging = bpy.data.collections.new("CQS_build_parts")
    scene.collection.children.link(staging)

    data = json.loads(GEOJSON.read_text(encoding="utf-8"))
    feature = data["features"][0]
    if feature["properties"].get("BLDG_ABBR") != "CQS" or feature["properties"].get("FID") != 653:
        raise RuntimeError("GIS feature identity mismatch; refusing to build wrong asset")
    raw_ring = feature["geometry"]["coordinates"][0]
    projected_raw = [project_lon_lat(p[0], p[1]) for p in raw_ring]
    ring = simplify_ring(projected_raw)
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    width, depth = xmax - xmin, ymax - ymin
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2

    brick = material("CQS red brick", (0.34, 0.075, 0.045))
    stone = material("CQS pale limestone trim", (0.66, 0.62, 0.52))
    slate = material("CQS dark slate roof", (0.075, 0.085, 0.10))
    glass = material("CQS recessed dark glazing", (0.045, 0.10, 0.14), 0.25)
    concrete = material("CQS foundation stone", (0.43, 0.40, 0.34))
    body = make_body(ring, GROUND_Z, WALL_EAVE_Z, brick, slate, asset)
    # The GIS outline has an open southern courtyard. The building-specific
    # photo was taken south of that opening, facing the inner face of the north
    # bar. Its frontage is approximately 31 m north of the footprint's south edge.
    face_y = ymin + 31.4
    facade_front_y = face_y - 2.0
    facade_xmin, facade_xmax = cx - width * 0.26, cx + width * 0.26
    facade_width = facade_xmax - facade_xmin
    pavilion_w = min(13.0, facade_width * 0.16)
    pavilion_d = min(9.0, depth * 0.22)
    cube_obj("CQS raised central entry pavilion", (cx, facade_front_y + pavilion_d / 2, 13.2),
             (pavilion_w, pavilion_d, 11.4), brick, asset, 0.10)
    tower_sep = min(11.0, facade_width * 0.13)
    tower_w = min(8.4, facade_width * 0.10)
    tower_d = min(9.0, depth * 0.23)
    for side, x in (("west", cx - tower_sep), ("east", cx + tower_sep)):
        cube_obj(f"CQS {side} entrance tower", (x, facade_front_y + tower_d / 2, 15.6),
                 (tower_w, tower_d, 10.8), brick, asset, 0.12)
        # pale corner piers and crenellated parapet reproduce the photo's
        # distinctive pale stone vertical bands and tower silhouettes.
        for sx in (-1, 1):
            cube_obj(f"CQS {side} tower stone pier", (x + sx * (tower_w / 2 - 0.28), facade_front_y - 0.06, 15.5),
                     (0.56, 0.36, 10.4), stone, asset, 0.04)
        cube_obj(f"CQS {side} tower cap", (x, facade_front_y + tower_d / 2, 21.0),
                 (tower_w + 0.8, tower_d + 0.8, 1.0), stone, asset, 0.08)
        for k in range(4):
            cube_obj(f"CQS {side} crenel {k + 1}", (x - tower_w * 0.34 + k * tower_w * 0.225,
                     facade_front_y + tower_d / 2, 21.8), (1.5, tower_d + 0.8, 0.65), brick, asset, 0.03)
        # Stacked, narrow tower openings.
        for floor in range(4):
            cube_obj(f"CQS {side} tower window {floor + 1}", (x, facade_front_y - 0.22, 11.2 + floor * 2.2),
                     (1.55, 0.28, 1.35), glass, asset, 0.04)
            for dx in (-1.05, 1.05):
                cube_obj(f"CQS {side} tower window trim {floor + 1}", (x + dx, facade_front_y - 0.20, 11.2 + floor * 2.2),
                         (0.18, 0.20, 1.68), stone, asset, 0.02)

    # Window rhythm on the south elevation is keyed to the documented facade
    # photograph; bays remain schematic where individual window positions are
    # occluded by the viewpoint or landscaping.
    usable_left, usable_right = facade_xmin + facade_width * 0.04, facade_xmax - facade_width * 0.04
    box_windows(usable_left, cx - tower_sep - tower_w * 0.55, facade_front_y - 0.20,
                3, 4, 3.3, 2.7, 1.9, 1.65, glass, asset, "CQS courtyard-west")
    box_windows(cx + tower_sep + tower_w * 0.55, usable_right, facade_front_y - 0.20,
                3, 4, 3.3, 2.7, 1.9, 1.65, glass, asset, "CQS courtyard-east")
    # Pale stone plinth and horizontal string courses match the source image.
    cube_obj("CQS courtyard stone plinth", (cx, facade_front_y - 0.05, 1.05), (facade_width * 0.96, 0.45, 1.15), concrete, asset, 0.06)
    for z in (4.5, 7.4, 12.5):
        cube_obj(f"CQS courtyard limestone string course {z}", (cx, facade_front_y - 0.08, z),
                 (facade_width * 0.94, 0.28, 0.24), stone, asset, 0.03)
    # Paired stone-framed side arches and the dominant central pointed arch.
    for side, x in (("west", cx - tower_sep - 10.0), ("east", cx + tower_sep + 10.0)):
        cube_obj(f"CQS {side} arched entry recess", (x, facade_front_y - 0.24, 2.6), (3.8, 0.30, 4.6), glass, asset, 0.10)
        cube_obj(f"CQS {side} entry stone jamb L", (x - 2.1, facade_front_y - 0.34, 2.6), (0.38, 0.42, 4.8), stone, asset, 0.05)
        cube_obj(f"CQS {side} entry stone jamb R", (x + 2.1, facade_front_y - 0.34, 2.6), (0.38, 0.42, 4.8), stone, asset, 0.05)
        pointed_arch_header(f"CQS {side} stone entry", x, facade_front_y - 0.42, 4.8, 1.8, stone, asset)
    cube_obj("CQS central pointed-arch entry glazing", (cx, facade_front_y - 0.32, 2.9), (3.4, 0.35, 4.5), glass, asset, 0.08)
    for side in (-1, 1):
        cube_obj(f"CQS central entry limestone jamb {side}", (cx + side * 1.95, facade_front_y - 0.44, 2.9),
                 (0.36, 0.48, 4.8), stone, asset, 0.04)
    pointed_arch_header("CQS central limestone portal", cx, facade_front_y - 0.52, 4.8, 1.9, stone, asset)
    # Add the projecting stone oriel seen between the entrance towers.
    cube_obj("CQS central limestone oriel surround", (cx, facade_front_y - 0.44, 10.2), (7.0, 0.70, 4.2), stone, asset, 0.08)
    cube_obj("CQS central oriel glazing", (cx, facade_front_y - 0.83, 10.2), (5.2, 0.18, 2.5), glass, asset, 0.04)
    cube_obj("CQS central oriel balcony sill", (cx, facade_front_y - 0.75, 7.95), (8.0, 1.2, 0.35), stone, asset, 0.05)
    for side in (-1, 1):
        for floor, z in enumerate((13.4, 16.1)):
            x = cx + side * 7.2
            cube_obj(f"CQS central pavilion upper window {side} {floor + 1}",
                     (x, facade_front_y - 0.28, z), (1.7, 0.34, 1.75), glass, asset, 0.05)
            for dx in (-1.0, 1.0):
                cube_obj(f"CQS central pavilion window stone trim {side} {floor + 1} {dx}",
                         (x + dx, facade_front_y - 0.26, z), (0.18, 0.24, 2.05), stone, asset, 0.02)
    cube_obj("CQS central pavilion stone medallion", (cx, facade_front_y - 0.30, 18.0),
             (1.8, 0.34, 1.8), stone, asset, 0.20)
    # Three separately estimated roof wings follow the U-shaped aerial outline;
    # no roof spans the open courtyard. Exact pitch and dormer positions are unknown.
    make_gable_roof_rect(facade_xmin, facade_xmax, ymin + 31.8, ymax,
                         WALL_EAVE_Z, ROOF_Z, slate, asset, "x")
    make_gable_roof_rect(xmin, facade_xmin, ymin, ymin + 34.0,
                         WALL_EAVE_Z, ROOF_Z - 0.4, slate, asset, "y")
    make_gable_roof_rect(facade_xmax, xmax, ymin, ymin + 32.5,
                         WALL_EAVE_Z, ROOF_Z - 0.4, slate, asset, "y")

    # Bring all geometry into the required single named massing object while
    # preserving its campus-coordinate vertices and expected collection.
    bpy.ops.object.select_all(action="DESELECT")
    parts = [o for o in staging.objects]
    # Move staging pieces into the asset collection before joining.
    for obj in parts:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        asset.objects.link(obj)
    bpy.data.collections.remove(staging)
    all_objs = list(asset.objects)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in all_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    body.name = "Cary Quadrangle South (CQS)"
    body.data.name = "CQS source-backed campus-coordinate massing"
    body["stable_building_id"] = ASSET_ID
    body["source_feature"] = "Purdue BuildingShapesZip4 FID 653 / BLDG_ABBR CQS"
    body["height_status"] = "Estimated from south elevation photograph; GIS Extrution=54 has undocumented units"
    body["floor_status"] = "GIS NUM_LEVELS=7; exact above-grade count is unverified"
    body["footprint_simplification_tolerance_m"] = 0.22
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.25, 0.25, 0.25)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    projected_bounds = [[min(p[0] for p in projected_raw), max(p[0] for p in projected_raw)],
                        [min(p[1] for p in projected_raw), max(p[1] for p in projected_raw)]]
    max_boundary_deviation = max(min(point_line_distance(p, ring[i - 1], ring[i])
                                     for i in range(len(ring))) for p in projected_raw)
    bldg_report = {
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)),
        "scene": SCENE_NAME,
        "export_collection": COLLECTION_NAME,
        "source_feature": {"provider": "Purdue University GIS", "service": "BuildingShapesZip4 FeatureServer/0",
                           "FID": 653, "BLDG_ABBR": "CQS", "BUILDING_N": feature["properties"]["BUILDING_N"],
                           "address": feature["properties"]["ADDRESS"], "retrieved_utc_date": "2026-10-26"},
        "source_vertex_count": len(raw_ring),
        "simplified_vertex_count": len(ring),
        "simplification_tolerance_m": 0.22,
        "max_source_vertex_to_simplified_segment_m": round(max_boundary_deviation, 4),
        "projected_source_bounds_m": projected_bounds,
        "model_footprint_bounds_m": [[xmin, xmax], [ymin, ymax]],
        "source_plan_area_m2": round(polygon_area(projected_raw), 2),
        "simplified_plan_area_m2": round(polygon_area(ring), 2),
        "height_m": [GROUND_Z, 22.125],
        "height_method": "Estimated from building-specific south elevation photograph; official GIS Extrution=54 units undocumented.",
        "level_evidence": {"NUM_LEVELS": feature["properties"]["NUM_LEVELS"],
                           "CountOfFLO": feature["properties"]["CountOfFLO"],
                           "interpretation": "GIS attributes both say 7; above-grade storey count is unverified."},
        "source_geometry_method": "WGS84 GIS polygon projected using documented project approximation; ring simplified to remove short survey traces while retaining footprint shape. Geometry stays in campus coordinates.",
        "model_scope": "Continuous GIS wall footprint, three roof bars that follow the observed U-shaped courtyard plan, central entry pavilion and paired towers; schematic window rhythm from identified south elevation photo.",
        "uncertainties": ["GIS Extrution units are undocumented; modeled height is an estimate.",
                          "Individual storey count is unverified despite GIS NUM_LEVELS=7.",
                          "Roof pitch and exact facade bay/window dimensions are not measured.",
                          "Facade position is inferred from the interior courtyard-facing north bar and documented photo point/heading."],
    }
    (EVIDENCE / "build_report.json").write_text(json.dumps(bldg_report, indent=2), encoding="utf-8")
    (EVIDENCE / "gis_projected_simplified_ring.json").write_text(
        json.dumps({"crs": "Purdue project local approximation from WGS84", "units": "m",
                    "ring_xy": ring}, indent=2), encoding="utf-8")
    print(json.dumps(bldg_report, indent=2))


build()
