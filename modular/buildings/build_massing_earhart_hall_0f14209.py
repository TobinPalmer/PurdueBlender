"""Build a source-backed, campus-coordinate Earhart Hall library.

Run with Blender 5.2 background mode. The stable manifest ID, path, scene, and
collection remain unchanged. Geometry uses the project-local campus XY metres.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


BUILDING_ID = "massing_earhart_hall_0f14209"
COLLECTION_NAME = "Asset_massing_earhart_hall_0f14209"
SCENE_NAME = "Building_massing_earhart_hall_0f14209"
ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "earhart_hall" / "sources" / "purdue_building_shapes_erht_2026-10-26.geojson"
AUDIT_DIR = ROOT / "audit" / "earhart_hall"

# Purdue's 2017 BuildingShapes layer reports eight levels in its F01–F08 fields,
# and the bathroom-renovation source covers floors 1–8. We model eight levels.
# The R=81.1 GIS attribute has no unit description; feet are a plausible reading,
# yielding 24.72 m. That roof height is an estimate, never treated as surveyed.
LEVELS = [0.0, 4.10, 7.05, 10.00, 12.95, 15.90, 18.85, 21.80, 24.75]
FLOOR_COUNT = len(LEVELS) - 1
WALL_THICKNESS = 0.27
SIMPLIFY_TOLERANCE_M = 0.75


def xy_from_lonlat(lon, lat):
    """Project WGS84 vertices using the project conversion in modular/AGENTS.md."""
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    return (x, y)


def point_line_distance(point, start, end):
    ax, ay = start
    bx, by = end
    px, py = point
    dx, dy = bx - ax, by - ay
    if abs(dx) + abs(dy) < 1e-12:
        return math.hypot(px - ax, py - ay)
    return abs(dy * px - dx * py + bx * ay - by * ax) / math.hypot(dx, dy)


def rdp(points, tolerance):
    if len(points) <= 2:
        return list(points)
    a, b = points[0], points[-1]
    best_i, best_d = -1, -1.0
    for i in range(1, len(points) - 1):
        d = point_line_distance(points[i], a, b)
        if d > best_d:
            best_i, best_d = i, d
    if best_d > tolerance:
        left = rdp(points[: best_i + 1], tolerance)
        right = rdp(points[best_i:], tolerance)
        return left[:-1] + right
    return [a, b]


def simplify_ring(points, tolerance):
    """Simplify a closed ring by splitting at its farthest vertex pair."""
    points = list(points)
    if points[0] == points[-1]:
        points.pop()
    i0 = 0
    i1 = max(range(1, len(points)), key=lambda i: (points[i][0] - points[i0][0]) ** 2 + (points[i][1] - points[i0][1]) ** 2)
    if i1 < i0:
        i0, i1 = i1, i0
    first = rdp(points[i0 : i1 + 1], tolerance)
    second = rdp(points[i1:] + points[: i0 + 1], tolerance)
    result = first[:-1] + second[:-1]
    if signed_area(result) * signed_area(points) < 0:
        result.reverse()
    return result


def signed_area(points):
    return 0.5 * sum(
        points[i][0] * points[(i + 1) % len(points)][1]
        - points[(i + 1) % len(points)][0] * points[i][1]
        for i in range(len(points))
    )


def load_footprint():
    raw = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    features = raw.get("features", [])
    matching = [f for f in features if f.get("properties", {}).get("BLDG_ABBR") == "ERHT"]
    if len(matching) != 1:
        raise RuntimeError(f"Expected one ERHT Purdue GIS feature, found {len(matching)}")
    feature = matching[0]
    if feature.get("properties", {}).get("FID") != 61:
        raise RuntimeError("Purdue GIS feature identity changed; refusing to build")
    coordinates = feature["geometry"]["coordinates"][0]
    local = [xy_from_lonlat(lon, lat) for lon, lat, *_ in coordinates]
    if local[0] == local[-1]:
        local.pop()
    return feature["properties"], local, simplify_ring(local, SIMPLIFY_TOLERANCE_M)


def make_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    if name == "ERHT_Red_Brick_Procedural":
        geo = nodes.new("ShaderNodeNewGeometry")
        brick = nodes.new("ShaderNodeTexBrick")
        brick.inputs["Color1"].default_value = (0.34, 0.075, 0.045, 1)
        brick.inputs["Color2"].default_value = (0.49, 0.14, 0.085, 1)
        brick.inputs["Mortar"] .default_value = (0.22, 0.17, 0.14, 1)
        brick.inputs["Scale"].default_value = 2.7
        brick.inputs["Mortar Size"].default_value = 0.025
        brick.inputs["Mortar Smooth"].default_value = 0.015
        links.new(geo.outputs["Position"], brick.inputs["Vector"])
        links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 5.0
        noise.inputs["Detail"].default_value = 2.0
        links.new(geo.outputs["Position"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.14
        bump.inputs["Distance"].default_value = 0.035
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    elif name == "ERHT_Stone_Procedural":
        geo = nodes.new("ShaderNodeNewGeometry")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 3.5
        noise.inputs["Detail"].default_value = 3.0
        noise.inputs["Roughness"].default_value = 0.7
        links.new(geo.outputs["Position"], noise.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.2
        ramp.color_ramp.elements[0].color = (0.56, 0.48, 0.36, 1)
        ramp.color_ramp.elements[1].position = 0.8
        ramp.color_ramp.elements[1].color = (0.82, 0.74, 0.61, 1)
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    elif name == "ERHT_Glass":
        bsdf.inputs["Base Color"].default_value = (0.10, 0.21, 0.29, 1)
        bsdf.inputs["Metallic"].default_value = 0.24
        bsdf.inputs["Roughness"].default_value = 0.19
    return mat


class GeometryBucket:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def quad(self, points):
        base = len(self.vertices)
        self.vertices.extend(tuple(float(v) for v in p) for p in points)
        self.faces.append(tuple(range(base, base + len(points))))

    def box(self, center, axis_t, axis_n, width, depth, height):
        t = Vector((axis_t[0], axis_t[1], 0.0)).normalized()
        n = Vector((axis_n[0], axis_n[1], 0.0)).normalized()
        c = Vector((center[0], center[1], center[2]))
        hw, hd, hh = width / 2.0, depth / 2.0, height / 2.0
        corners = []
        for z_sign in (-1, 1):
            for t_sign, n_sign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                p = c + t * (t_sign * hw) + n * (n_sign * hd) + Vector((0, 0, z_sign * hh))
                corners.append(tuple(p))
        base = len(self.vertices)
        self.vertices.extend(corners)
        self.faces.extend(
            (
                (base + 0, base + 3, base + 2, base + 1),
                (base + 4, base + 5, base + 6, base + 7),
                (base + 0, base + 1, base + 5, base + 4),
                (base + 1, base + 2, base + 6, base + 5),
                (base + 2, base + 3, base + 7, base + 6),
                (base + 3, base + 0, base + 4, base + 7),
            )
        )


def p_at(p0, tangent, s, normal, offset, z):
    return (p0[0] + tangent[0] * s + normal[0] * offset, p0[1] + tangent[1] * s + normal[1] * offset, z)


def add_wall_panel(bucket, p0, tangent, normal, s0, s1, z0, z1, offset=0.0):
    if s1 - s0 < 1e-4 or z1 - z0 < 1e-4:
        return
    # For the clockwise Purdue exterior ring, this order faces outward.
    bucket.quad(
        (
            p_at(p0, tangent, s0, normal, offset, z0),
            p_at(p0, tangent, s0, normal, offset, z1),
            p_at(p0, tangent, s1, normal, offset, z1),
            p_at(p0, tangent, s1, normal, offset, z0),
        )
    )


def add_mesh_object(name, bucket, material, collection):
    if not bucket.vertices or not bucket.faces:
        return None
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(bucket.vertices, [], bucket.faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_text(name, body, location, size, material, collection, facing="south"):
    curve = bpy.data.curves.new(name + "_Curve", "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.006
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    if facing == "south":
        obj.rotation_euler = (math.radians(90), 0, 0)
    elif facing == "east":
        obj.rotation_euler = (math.radians(90), 0, math.radians(-90))
    obj.data.materials.append(material)
    return obj


def link_scene_object(name, mesh_name, vertices, faces, material, collection):
    bucket = GeometryBucket()
    bucket.vertices.extend(vertices)
    bucket.faces.extend(faces)
    return add_mesh_object(name, bucket, material, collection)


def add_flat_polygon(name, ring, z, material, collection):
    bucket = GeometryBucket()
    verts = [(x, y, z) for x, y in ring]
    bucket.vertices.extend(verts)
    face = tuple(range(len(verts)))
    if signed_area(ring) < 0:
        face = tuple(reversed(face))
    bucket.faces.append(face)
    return add_mesh_object(name, bucket, material, collection)


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_scene(scene_name):
    scene = bpy.context.scene
    scene.name = scene_name
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def make_asset():
    props, source_ring, footprint = load_footprint()
    if len(footprint) < 8:
        raise RuntimeError("Simplified ERHT footprint unexpectedly collapsed")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = create_scene(SCENE_NAME)
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    preview = bpy.data.collections.new("Preview_only_context_exclude_from_master")
    scene.collection.children.link(preview)

    brick = make_material("ERHT_Red_Brick_Procedural", (0.43, 0.11, 0.07), 0.78)
    stone = make_material("ERHT_Stone_Procedural", (0.72, 0.65, 0.53), 0.76)
    glass = make_material("ERHT_Glass", (0.10, 0.21, 0.29), 0.18, 0.24)
    concrete = make_material("ERHT_Concrete", (0.39, 0.39, 0.36), 0.88)
    roof_mat = make_material("ERHT_Roof_Membrane", (0.12, 0.14, 0.15), 0.88)
    frame_mat = make_material("ERHT_Window_Frame", (0.66, 0.59, 0.48), 0.6)
    metal = make_material("ERHT_Dark_Metal", (0.10, 0.11, 0.12), 0.42, 0.35)
    sign_mat = make_material("ERHT_Sign_Lettering", (0.78, 0.73, 0.61), 0.35, 0.2)
    interior_floor = make_material("ERHT_Interior_Oak", (0.38, 0.20, 0.10), 0.7)
    wall_paint = make_material("ERHT_Interior_Paint", (0.72, 0.70, 0.64), 0.85)
    furniture = make_material("ERHT_Interior_Wood", (0.47, 0.29, 0.15), 0.74)
    purdue_red = make_material("ERHT_Interior_Purdue_Red", (0.42, 0.018, 0.045), 0.84)

    buckets = {name: GeometryBucket() for name in ("brick", "stone", "glass", "concrete", "roof", "frame", "metal", "interior_floor", "wall_paint", "furniture", "purdue_red")}
    winding = signed_area(footprint)
    bounds = [min(p[0] for p in footprint), min(p[1] for p in footprint), max(p[0] for p in footprint), max(p[1] for p in footprint)]

    # Floor slabs are explicit so the linked library has a readable interior volume.
    for level in LEVELS[:-1]:
        add_flat_polygon(f"ERHT_Floor_{level:05.2f}", footprint, level + 0.06, interior_floor, asset)

    edges = []
    for i, p0 in enumerate(footprint):
        p1 = footprint[(i + 1) % len(footprint)]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        length = math.hypot(dx, dy)
        if length < 0.05:
            continue
        tangent = (dx / length, dy / length)
        if winding < 0:
            normal = (-tangent[1], tangent[0])
        else:
            normal = (tangent[1], -tangent[0])
        edges.append((i, p0, p1, length, tangent, normal))

    # The mapped southern recess is the photographed dining-court entry.
    entrance_target = (-951.5, -198.3)
    entrance_edge = min(edges, key=lambda e: math.hypot((e[1][0] + e[2][0]) / 2 - entrance_target[0], (e[1][1] + e[2][1]) / 2 - entrance_target[1]))
    entry_idx, entry_p0, entry_p1, entry_len, entry_t, entry_n = entrance_edge
    entry_s = max(0.0, min(entry_len, (entrance_target[0] - entry_p0[0]) * entry_t[0] + (entrance_target[1] - entry_p0[1]) * entry_t[1]))
    entry_center_xy = (entry_p0[0] + entry_t[0] * entry_s, entry_p0[1] + entry_t[1] * entry_s)

    def is_entry(edge):
        return edge[0] == entry_idx

    window_records = []

    # Eight brick storeys, with openings constructed into the facade rather than
    # pasted onto a solid block. Street views can read the actual glazing and depth.
    for edge in edges:
        _, p0, p1, length, tangent, normal = edge
        long_enough = length >= 4.5
        if long_enough:
            count = max(1, int((length - 1.4) / 3.15))
            span = length - 1.4
            centers = [0.7 + span * (i + 0.5) / count for i in range(count)]
        else:
            centers = []
        for floor in range(FLOOR_COUNT):
            z0, z1 = LEVELS[floor], LEVELS[floor + 1]
            ground = floor == 0
            if is_entry(edge) and ground:
                # Wide dining-court curtain wall and paired doors across the recessed entry.
                opening_w = min(18.0, max(0.0, length - 2.4))
                left = max(0.9, entry_s - opening_w / 2)
                right = min(length - 0.9, entry_s + opening_w / 2)
                sill, head = 0.45, 3.25
                add_wall_panel(buckets["brick"], p0, tangent, normal, 0.0, left, z0, z1, 0.0)
                add_wall_panel(buckets["brick"], p0, tangent, normal, right, length, z0, z1, 0.0)
                add_wall_panel(buckets["brick"], p0, tangent, normal, left, right, z0, sill, 0.0)
                add_wall_panel(buckets["brick"], p0, tangent, normal, left, right, head, z1, 0.0)
                # Recessed dark glazing and warm bronze mullions.
                add_wall_panel(buckets["glass"], p0, tangent, normal, left + 0.07, right - 0.07, sill + 0.05, head - 0.06, -0.035)
                divisions = max(4, int((right - left) / 2.2))
                for j in range(divisions + 1):
                    s = left + (right - left) * j / divisions
                    buckets["frame"].box((p0[0] + tangent[0] * s + normal[0] * 0.06, p0[1] + tangent[1] * s + normal[1] * 0.06, (sill + head) / 2), tangent, normal, 0.11, 0.10, head - sill)
                buckets["frame"].box((entry_center_xy[0] + normal[0] * 0.06, entry_center_xy[1] + normal[1] * 0.06, (sill + head) / 2), tangent, normal, 0.15, 0.12, head - sill)
                buckets["frame"].box((entry_center_xy[0] + normal[0] * 0.06, entry_center_xy[1] + normal[1] * 0.06, sill + 0.05), tangent, normal, 1.42, 0.15, head - sill - 0.12)
                # Raised stone header over the storefront.
                buckets["stone"].box((entry_center_xy[0] + normal[0] * 0.08, entry_center_xy[1] + normal[1] * 0.08, 3.43), tangent, normal, right - left + 0.45, 0.34, 0.24)
                window_records.append({"edge": edge[0], "floor": floor + 1, "center_s": entry_s, "width": right - left, "type": "dining_court_curtainwall"})
                continue

            # Residential openings: narrow paired vertical panes in each repeated bay.
            win_w = 1.42 if not ground else 1.85
            win_h = 1.72 if not ground else 2.28
            zbot = z0 + (0.79 if not ground else 0.68)
            ztop = min(zbot + win_h, z1 - 0.28)
            valid_centers = [c for c in centers if c - win_w / 2 > 0.38 and c + win_w / 2 < length - 0.38]
            if not valid_centers:
                add_wall_panel(buckets["brick"], p0, tangent, normal, 0.0, length, z0, z1, 0.0)
                continue
            spans = [(max(0.0, c - win_w / 2), min(length, c + win_w / 2), c) for c in valid_centers]
            cursor = 0.0
            for a, b, center_s in spans:
                add_wall_panel(buckets["brick"], p0, tangent, normal, cursor, a, z0, z1, 0.0)
                add_wall_panel(buckets["brick"], p0, tangent, normal, a, b, z0, zbot, 0.0)
                add_wall_panel(buckets["brick"], p0, tangent, normal, a, b, ztop, z1, 0.0)
                # Two panes, stone reveal, sill, head and a central mullion.
                center = (p0[0] + tangent[0] * center_s, p0[1] + tangent[1] * center_s)
                add_wall_panel(buckets["glass"], p0, tangent, normal, a + 0.12, b - 0.12, zbot + 0.10, ztop - 0.10, -0.035)
                frame_d = 0.15
                for s, ww in ((a + 0.04, 0.13), (b - 0.04, 0.13), (center_s, 0.10)):
                    buckets["frame"].box((p0[0] + tangent[0] * s + normal[0] * 0.07, p0[1] + tangent[1] * s + normal[1] * 0.07, (zbot + ztop) / 2), tangent, normal, ww, frame_d, ztop - zbot + 0.10)
                for z in (zbot + 0.04, ztop - 0.04, (zbot + ztop) / 2):
                    buckets["frame"].box((center[0] + normal[0] * 0.07, center[1] + normal[1] * 0.07, z), tangent, normal, win_w, frame_d, 0.10 if z not in (zbot + 0.04, ztop - 0.04) else 0.14)
                # Pale limestone sills and lintels repeat across each elevation.
                buckets["stone"].box((center[0] + normal[0] * 0.075, center[1] + normal[1] * 0.075, zbot - 0.055), tangent, normal, win_w + 0.20, 0.19, 0.12)
                buckets["stone"].box((center[0] + normal[0] * 0.065, center[1] + normal[1] * 0.065, ztop + 0.045), tangent, normal, win_w + 0.18, 0.16, 0.10)
                window_records.append({"edge": edge[0], "floor": floor + 1, "center_s": center_s, "width": win_w, "type": "residential_pair"})
                cursor = b
            add_wall_panel(buckets["brick"], p0, tangent, normal, cursor, length, z0, z1, 0.0)

        # A restrained limestone belt at every storey matches the light trim seen in the references.
        for level in LEVELS[1:-1]:
            buckets["stone"].box(((p0[0] + p1[0]) / 2 + normal[0] * 0.035, (p0[1] + p1[1]) / 2 + normal[1] * 0.035, level), tangent, normal, length + 0.04, 0.11, 0.095)
        # Ground-level limestone base course.
        buckets["stone"].box(((p0[0] + p1[0]) / 2 + normal[0] * 0.07, (p0[1] + p1[1]) / 2 + normal[1] * 0.07, 0.31), tangent, normal, length + 0.06, 0.20, 0.46)

    # Masonry corner piers and the flat roof/parapet silhouette.
    for x, y in footprint:
        buckets["stone"].box((x + 0.025, y + 0.025, LEVELS[-1] / 2), (1, 0), (0, 1), 0.20, 0.20, LEVELS[-1])
    add_flat_polygon("ERHT_Flat_Roof_Deck", footprint, LEVELS[-1] - 0.08, roof_mat, asset)
    roof_bucket = GeometryBucket()
    for _, p0, p1, length, tangent, normal in edges:
        roof_bucket.box(((p0[0] + p1[0]) / 2 + normal[0] * 0.02, (p0[1] + p1[1]) / 2 + normal[1] * 0.02, LEVELS[-1] + 0.37), tangent, normal, length + 0.06, 0.22, 0.74)
    add_mesh_object("ERHT_Low_Flat_Roof_Parapet", roof_bucket, stone, asset)

    # Dining-court entrance canopy: the GIS recess opens toward First Street.
    entry_n = Vector(entry_n)
    entry_t = Vector(entry_t)
    entry_xy = Vector(entry_center_xy)
    def entry_world(outward, z):
        p = entry_xy + entry_n * outward
        return (p.x, p.y, z)

    canopy_depth = 4.8
    canopy_width = min(19.5, max(12.0, entry_len - 4.0))
    canopy_center = entry_world(canopy_depth * 0.58, 3.68)
    buckets["metal"].box(canopy_center, entry_t, entry_n, canopy_width, canopy_depth, 0.24)
    for s in (-canopy_width * 0.42, -canopy_width * 0.14, canopy_width * 0.14, canopy_width * 0.42):
        center_xy = entry_xy + entry_t * s + entry_n * canopy_depth * 0.86
        buckets["frame"].box((center_xy.x, center_xy.y, 1.83), entry_t, entry_n, 0.22, 0.22, 3.58)
    # The glazed wall and entry steps sit within the mapped recess.
    platform = GeometryBucket()
    platform.box(entry_world(canopy_depth * 0.53, 0.15), entry_t, entry_n, canopy_width + 4.0, canopy_depth + 4.8, 0.30)
    add_mesh_object("ERHT_Dining_Court_Concrete_Podium", platform, concrete, asset)
    stair_bucket = GeometryBucket()
    for step in range(6):
        depth = 0.38
        outward = canopy_depth * 0.53 + canopy_depth / 2 + 0.19 + step * depth
        h = 0.16
        center = entry_world(outward, (step + 0.5) * h)
        stair_bucket.box(center, entry_t, entry_n, canopy_width * 0.66, depth, h)
    add_mesh_object("ERHT_Dining_Court_Six_Entry_Steps", stair_bucket, concrete, asset)

    # Header sign and the west-corner name plaque are supported by current and 2015 views.
    sign_center = entry_world(-0.14, 3.45)
    sign_back = GeometryBucket()
    sign_back.box(sign_center, entry_t, entry_n, min(14.0, entry_len - 2), 0.12, 0.48)
    add_mesh_object("ERHT_Dining_Court_Sign_Backplate", sign_back, metal, asset)
    text_loc = entry_world(-0.23, 3.45)
    add_text("ERHT_Dining_Court_Lettering", "EARHART DINING COURT", text_loc, 0.39, sign_mat, asset, "south")

    # Interior dining floor, basic columns, tables and counter are visible through the entrance glass.
    dining = GeometryBucket()
    dining_center = (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2
    # A clear sample hall centered on the GIS centroid, leaving paths to the entry.
    floor_z = 0.16
    for row in range(3):
        for col in range(4):
            cx = dining_center[0] - 8.0 + col * 5.3
            cy = dining_center[1] - 6.8 + row * 4.4
            dining.box((cx, cy, 1.05), (1, 0), (0, 1), 2.1, 1.05, 0.12)
            for dx in (-0.95, 0.95):
                for dy in (-0.78, 0.78):
                    dining.box((cx + dx, cy + dy, 0.56), (1, 0), (0, 1), 0.42, 0.42, 0.84)
    # Dining service counter, menu board and structural columns.
    dining.box((dining_center[0] + 7.0, dining_center[1] + 11.0, 1.35), (1, 0), (0, 1), 12.0, 1.0, 0.95)
    for xoff in (-10.0, -4.0, 4.0, 10.0):
        dining.box((dining_center[0] + xoff, dining_center[1], 1.9), (1, 0), (0, 1), 0.28, 0.28, 3.6)
    add_mesh_object("ERHT_Dining_Court_Tables_Chairs_Counter", dining, furniture, asset)

    # One measured-size typical double room is repeated on the residential floors.
    # Purdue's official standard-layout illustration lists 11 ft 6.5 in × 16 ft 4 in,
    # an 8 ft 1 in ceiling, two beds/desks and built-in dressers.
    west_edge = max((e for e in edges if abs(e[2][0] - e[1][0]) < 1.0 and e[3] > 45.0 and e[1][0] < bounds[0] + 2.0), key=lambda e: e[3])
    _, room_p0, _, room_length, room_t, room_out = west_edge
    room_t = Vector(room_t)
    room_out = Vector(room_out)
    room_width = 3.518
    room_depth = 4.979
    room_window_sill = 1.0
    candidate_centers = [0.7 + (room_length - 1.4) * (i + 0.5) / max(1, int((room_length - 1.4) / 3.15)) for i in range(max(1, int((room_length - 1.4) / 3.15)))]
    room_s = min(candidate_centers, key=lambda s: abs(s - room_length / 2))
    room_outer_xy = Vector(room_p0) + room_t * room_s
    room_buckets = {name: GeometryBucket() for name in ("floor", "wall", "furniture", "red")}

    def add_room_box(bucket, center_xy, z, axis_t, axis_n, w, d, h):
        bucket.box((center_xy.x, center_xy.y, z), (axis_t.x, axis_t.y), (axis_n.x, axis_n.y), w, d, h)

    for floor in range(1, FLOOR_COUNT):
        z0, z1 = LEVELS[floor], LEVELS[floor + 1]
        clear_h = min(2.55, z1 - z0 - 0.20)
        center_d = room_depth / 2 + 0.08
        center = room_outer_xy - room_out * center_d
        add_room_box(room_buckets["floor"], center, z0 + 0.15, room_t, room_out, room_width, room_depth, 0.12)
        # Side partitions and back wall create a real representative interior cell.
        inward = -room_out
        side_axis_n = Vector((-room_t.y, room_t.x))
        for side in (-1, 1):
            side_center = room_outer_xy - room_out * center_d + room_t * (side * room_width / 2)
            add_room_box(room_buckets["wall"], side_center, z0 + clear_h / 2 + 0.16, inward, room_t, room_depth, 0.11, clear_h)
        back_center = room_outer_xy - room_out * (room_depth + 0.10)
        add_room_box(room_buckets["wall"], back_center - room_t * (room_width * 0.26), z0 + clear_h / 2 + 0.16, room_t, room_out, room_width * 0.48, 0.11, clear_h)
        add_room_box(room_buckets["wall"], back_center + room_t * (room_width * 0.37), z0 + clear_h / 2 + 0.16, room_t, room_out, room_width * 0.26, 0.11, clear_h)
        # Door leaf and dark frame toward the corridor.
        door_center = back_center + room_t * (room_width * 0.04)
        add_room_box(room_buckets["furniture"], door_center, z0 + 1.12, room_t, room_out, 0.83, 0.045, 2.18)
        # Twin beds, mattresses, headboards, desks, chairs and built-in dresser.
        for side in (-1, 1):
            bed_center = room_outer_xy - room_out * 2.70 + room_t * (side * 0.82)
            add_room_box(room_buckets["furniture"], bed_center, z0 + 0.45, room_t, room_out, 0.88, 2.00, 0.38)
            add_room_box(room_buckets["red"], bed_center - room_out * 0.03, z0 + 0.68, room_t, room_out, 0.84, 1.92, 0.12)
            headboard = room_outer_xy - room_out * 3.75 + room_t * (side * 0.82)
            add_room_box(room_buckets["furniture"], headboard, z0 + 0.84, room_t, room_out, 0.90, 0.11, 1.45)
            desk_center = room_outer_xy - room_out * 0.65 + room_t * (side * 0.82)
            add_room_box(room_buckets["furniture"], desk_center, z0 + 0.79, room_t, room_out, 1.18, 0.62, 0.10)
            chair_center = desk_center - room_t * (side * 0.15) - room_out * 0.52
            add_room_box(room_buckets["furniture"], chair_center, z0 + 0.48, room_t, room_out, 0.48, 0.48, 0.82)
        dresser_center = room_outer_xy - room_out * 4.68 + room_t * 0.8
        add_room_box(room_buckets["furniture"], dresser_center, z0 + 0.62, room_t, room_out, 1.10, 0.38, 1.12)

    # Convert the material-appropriate geometry buckets into compact mesh objects.
    for name, material in (("brick", brick), ("stone", stone), ("glass", glass), ("concrete", concrete), ("roof", roof_mat), ("frame", frame_mat), ("metal", metal)):
        add_mesh_object("ERHT_" + {"brick": "Brick_Facade", "stone": "Limestone_Trim_and_Base", "glass": "Glazing", "concrete": "Concrete", "roof": "Roof", "frame": "Stone_Window_Frames", "metal": "Dark_Metal_Entry"}[name], buckets[name], material, asset)
    add_mesh_object("ERHT_Interior_Standard_Room_Floors", room_buckets["floor"], interior_floor, asset)
    add_mesh_object("ERHT_Interior_Standard_Room_Partitions", room_buckets["wall"], wall_paint, asset)
    add_mesh_object("ERHT_Interior_Standard_Room_Furniture", room_buckets["furniture"], furniture, asset)
    add_mesh_object("ERHT_Interior_Standard_Room_Bedding", room_buckets["red"], purdue_red, asset)

    # Entry walk/curb sits outside the source wall footprint but stays contained in the recess.
    walk = GeometryBucket()
    walk_center = entry_world(canopy_depth + 4.2, -0.06)
    walk.box(walk_center, entry_t, entry_n, canopy_width + 15.0, 2.8, 0.12)
    add_mesh_object("ERHT_Dining_Court_Entry_Walk", walk, concrete, asset)

    # Scene render setup; camera/lights remain outside the exported asset collection.
    scene.world = bpy.data.worlds.new("ERHT_Preview_World")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.07, 0.09, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    camera_data = bpy.data.cameras.new("ERHT_Exterior_Camera")
    camera = bpy.data.objects.new("ERHT_Exterior_Camera", camera_data)
    preview.objects.link(camera)
    camera.location = (dining_center[0] + 55.0, bounds[1] - 88.0, 44.0)
    look_at(camera, (dining_center[0], dining_center[1], 12.0))
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 118.0
    scene.camera = camera

    def area_light(name, location, energy, size, color):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        preview.objects.link(obj)
        obj.location = location
        look_at(obj, (dining_center[0], dining_center[1], 10.0))
        return obj

    area_light("ERHT_Key_Light", (-890, -280, 110), 42000, 85, (1.0, 0.86, 0.69))
    area_light("ERHT_Fill_Light", (-1030, -100, 75), 30000, 70, (0.72, 0.82, 1.0))
    sun_data = bpy.data.lights.new("ERHT_Soft_Daylight", "SUN")
    sun_data.energy = 2.0
    sun_data.angle = math.radians(18)
    sun = bpy.data.objects.new("ERHT_Soft_Daylight", sun_data)
    preview.objects.link(sun)
    sun.location = (-940, -270, 100)
    look_at(sun, (dining_center[0], dining_center[1], 8.0))
    # Blender 5.2 exposes the Eevee renderer under BLENDER_EEVEE.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = str(AUDIT_DIR / "exterior_preview.png")
    scene.render.film_transparent = False
    scene.camera.data.lens = 50
    scene.render.fps = 24
    scene.world.color = (0.08, 0.09, 0.12)

    # Save before rendering so the library itself remains a clean asset file.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    # Build evidence from the actual geometry and exported collection.
    world_verts = []
    for obj in asset.all_objects:
        if obj.type == "MESH":
            world_verts.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
    final_bounds = [[min(v[i] for v in world_verts), max(v[i] for v in world_verts)] for i in range(3)]
    material_assignments = {}
    for obj in asset.all_objects:
        for mat in obj.data.materials if obj.type == "MESH" else []:
            if mat:
                material_assignments.setdefault(mat.name, 0)
                material_assignments[mat.name] += 1
    report = {
        "building_id": BUILDING_ID,
        "asset_path": str(ASSET_PATH),
        "source_feature": {k: props.get(k) for k in ("FID", "BLDG_ABBR", "BUILDING_N", "ADDRESS", "NUM_LEVELS", "CountOfFLO", "R", "Extrution", "Shape__Area", "Shape__Length")},
        "source_ring_vertex_count": len(source_ring),
        "simplified_ring_vertex_count": len(footprint),
        "simplify_tolerance_m": SIMPLIFY_TOLERANCE_M,
        "geometry_bounds_world_m": final_bounds,
        "structural_footprint_bounds_m": [[bounds[0], bounds[2]], [bounds[1], bounds[3]]],
        "building_level_count": FLOOR_COUNT,
        "roof_height_estimate_m": LEVELS[-1],
        "roof_height_method": "Estimated as 81.1 ft converted to 24.72 m from Purdue GIS R field; the service does not document field units. Floors/eaves are not measured.",
        "floor_elevations_m": LEVELS,
        "residential_window_count": sum(1 for w in window_records if w["type"] == "residential_pair"),
        "special_glazing": [w for w in window_records if w["type"] == "dining_court_curtainwall"],
        "objects": [{"name": o.name, "type": o.type, "mesh_vertices": len(o.data.vertices) if o.type == "MESH" else None, "materials": [m.name for m in o.data.materials if m]} for o in asset.all_objects],
        "object_count": len(asset.all_objects),
        "material_object_assignments": material_assignments,
        "external_image_dependencies": [],
        "preview_file": "audit/earhart_hall/exterior_preview.png",
    }
    (AUDIT_DIR / "build_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    footprint_record = {
        "building_id": BUILDING_ID,
        "local_xy_conversion": "X=(longitude+86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude-40.4274)*111040.0",
        "source_ring_xy_m": source_ring,
        "simplified_ring_xy_m": footprint,
        "simplify_tolerance_m": SIMPLIFY_TOLERANCE_M,
    }
    (AUDIT_DIR / "footprint_geometry.json").write_text(json.dumps(footprint_record, indent=2) + "\n", encoding="utf-8")
    print("ERHT_BUILD_REPORT", json.dumps({k: report[k] for k in ("object_count", "geometry_bounds_world_m", "building_level_count", "roof_height_estimate_m", "residential_window_count", "external_image_dependencies")}))


make_asset()
