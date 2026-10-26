"""Build a detailed, source-backed library for Purdue's Kozuch Football Performance Complex.

Run from the repository root with Blender 5.2:
  blender --background --python modular/buildings/build_massing_purdue_football_performance_complex_f106c29.py

The asset stays in a local coordinate frame. Its placement origin is recorded in the
building evidence; the coordinator updates the shared manifest and master marker.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "massing_purdue_football_performance_complex_f106c29"
ASSET_FILE = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
EVIDENCE_DIR = ROOT / "audit" / "purdue_football_performance_complex"
SOURCE_FILE = EVIDENCE_DIR / "sources" / "purdue_gis_fpc_fid1202_2026-10-26.geojson"
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
SCENE_NAME = f"Building_{BUILDING_ID}"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def campus_xy(lon: float, lat: float) -> tuple[float, float]:
    """Use the project's documented local longitude/latitude approximation."""
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return x, y


def polygon_area(points: list[tuple[float, float]]) -> float:
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1]
                   - points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) * 0.5)


def new_material(name: str, color: tuple[float, float, float, float],
                 *, metallic: float = 0.0, roughness: float = 0.5,
                 noise_scale: float | None = None, bump_strength: float = 0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    if noise_scale is not None:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = noise_scale
        noise.inputs["Detail"].default_value = 2.0
        noise.inputs["Roughness"].default_value = 0.68
        noise.location = (-500, -100)
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.035
        bump.location = (-220, -80)
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def link_mesh(name: str, vertices, faces, material, collection, *, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.validate(verbose=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    return obj


def box_mesh(name, low, high, material, collection):
    x0, y0, z0 = low
    x1, y1, z1 = high
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return link_mesh(name, verts, faces, material, collection)


def slab(name, points, z, thickness, material, collection):
    n = len(points)
    verts = [(x, y, z) for x, y in points] + [(x, y, z - thickness) for x, y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return link_mesh(name, verts, faces, material, collection)


def sloped_slab(name, points, z_func, thickness, material, collection):
    """Extrude a planar, gently sloping roof polygon without changing its footprint."""
    n = len(points)
    top = [(x, y, z_func(x, y)) for x, y in points]
    bottom = [(x, y, z_func(x, y) - thickness) for x, y in points]
    verts = top + bottom
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return link_mesh(name, verts, faces, material, collection)


def clip_polygon_x(points, split_x, keep_left):
    """Clip a simple GIS polygon at one vertical line (one output ring per side)."""
    if not points:
        return []
    def inside(p):
        return p[0] <= split_x + 1e-8 if keep_left else p[0] >= split_x - 1e-8
    output = []
    previous = points[-1]
    previous_inside = inside(previous)
    for current in points:
        current_inside = inside(current)
        if current_inside != previous_inside:
            dx = current[0] - previous[0]
            if abs(dx) > 1e-9:
                t = (split_x - previous[0]) / dx
                output.append((split_x, previous[1] + t * (current[1] - previous[1])))
        if current_inside:
            output.append(current)
        previous, previous_inside = current, current_inside
    cleaned = []
    for p in output:
        if not cleaned or math.dist(cleaned[-1], p) > 1e-6:
            cleaned.append(p)
    if len(cleaned) > 2 and math.dist(cleaned[0], cleaned[-1]) < 1e-6:
        cleaned.pop()
    return cleaned if len(cleaned) >= 3 else []


def panel(name, p0, p1, z0, z1, material, collection, offset=0.0):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if length < 0.15 or z1 <= z0:
        return None
    nx, ny = -dy / length, dx / length
    verts = [(p0[0] + nx * offset, p0[1] + ny * offset, z0),
             (p1[0] + nx * offset, p1[1] + ny * offset, z0),
             (p1[0] + nx * offset, p1[1] + ny * offset, z1),
             (p0[0] + nx * offset, p0[1] + ny * offset, z1)]
    return link_mesh(name, verts, [(0, 1, 2, 3)], material, collection)


def edge_beam(name, p0, p1, z0, z1, width, depth, material, collection):
    """A narrow rectangular mullion following a facade edge vertically."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if length < 0.001:
        return None
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    # p0 is the beam centre along the edge; depth projects through the wall.
    verts = []
    for z in (z0, z1):
        for a, b in ((-width / 2, -depth / 2), (width / 2, -depth / 2),
                     (width / 2, depth / 2), (-width / 2, depth / 2)):
            verts.append((p0[0] + ux * a + nx * b, p0[1] + uy * a + ny * b, z))
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return link_mesh(name, verts, faces, material, collection)


def tube_between(name, start, end, radius, material, collection, segments=20):
    """Make a solid slanted stainless entrance column as a local cylinder mesh."""
    a, b = Vector(start), Vector(end)
    axis = (b - a).normalized()
    rotation = axis.to_track_quat("Z", "Y")
    ring_a, ring_b = [], []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        offset = rotation @ Vector((math.cos(angle) * radius, math.sin(angle) * radius, 0))
        ring_a.append(a + offset)
        ring_b.append(b + offset)
    verts = [tuple(v) for v in ring_a + ring_b]
    faces = [tuple(reversed(range(segments))), tuple(range(segments, 2 * segments))]
    faces += [(i, (i + 1) % segments, (i + 1) % segments + segments, i + segments)
              for i in range(segments)]
    return link_mesh(name, verts, faces, material, collection, smooth=True)


def add_text(name, text, location, size, rotation, material, collection, *, extrude=0.02, align="CENTER"):
    curve = bpy.data.curves.new(name + "Curve", "FONT")
    curve.body = text
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = 0.005
    curve.align_x = align
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    return obj


def make_camera(collection, location, target, ortho_scale, name="KFPC_Preview_Camera"):
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    collection.objects.link(camera)
    camera.location = location
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = ortho_scale
    camera_data.lens = 50
    return camera


def main():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    geo = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    feature = next(f for f in geo["features"] if f.get("id", f["properties"].get("OBJECTID")) == 1202)
    raw_ring = feature["geometry"]["coordinates"][0]
    campus_ring = [campus_xy(float(lon), float(lat)) for lon, lat, *_ in raw_ring]
    if campus_ring[0] == campus_ring[-1]:
        campus_ring.pop()
    min_x, max_x = min(p[0] for p in campus_ring), max(p[0] for p in campus_ring)
    min_y, max_y = min(p[1] for p in campus_ring), max(p[1] for p in campus_ring)
    origin_x, origin_y = (min_x + max_x) / 2, (min_y + max_y) / 2
    local = [(x - origin_x, y - origin_y) for x, y in campus_ring]
    footprint_area = polygon_area(local)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    preview_collection = bpy.data.collections.new("Preview_Only_Not_Exported")
    scene.collection.children.link(preview_collection)

    cream = new_material("KFPC | champagne anodized aluminum", (0.68, 0.61, 0.45, 1),
                         metallic=0.62, roughness=0.28, noise_scale=160, bump_strength=0.045)
    charcoal = new_material("KFPC | charcoal metal panels", (0.035, 0.045, 0.058, 1),
                            metallic=0.72, roughness=0.31, noise_scale=95, bump_strength=0.025)
    glass = new_material("KFPC | blue black curtainwall glass", (0.055, 0.105, 0.14, 1),
                         metallic=0.38, roughness=0.16)
    mullion = new_material("KFPC | black aluminum mullions", (0.018, 0.025, 0.03, 1),
                           metallic=0.82, roughness=0.28)
    concrete = new_material("KFPC | warm architectural concrete", (0.34, 0.33, 0.30, 1),
                            metallic=0.0, roughness=0.72, noise_scale=90, bump_strength=0.06)
    steel = new_material("KFPC | brushed stainless steel", (0.57, 0.61, 0.63, 1),
                         metallic=0.88, roughness=0.23)
    interior_floor = new_material("KFPC | interior dark rubber and wood", (0.10, 0.075, 0.055, 1),
                                  metallic=0.05, roughness=0.68, noise_scale=32, bump_strength=0.035)
    sign_black = new_material("KFPC | sign black", (0.008, 0.012, 0.02, 1), metallic=0.55, roughness=0.22)
    turf_green = new_material("KFPC | training floor green", (0.075, 0.17, 0.10, 1), metallic=0.0, roughness=0.84,
                              noise_scale=120, bump_strength=0.08)

    # Ground-level foundation and readable three-storey interior decks.
    slab("KFPC | structural ground plinth", local, 0.45, 0.45, concrete, asset)
    slab("KFPC | level 02 floor plate", local, 4.15, 0.24, interior_floor, asset)
    slab("KFPC | level 03 floor plate", local, 8.05, 0.24, interior_floor, asset)
    top_local = list(local)

    # Main envelope: three levels, with a clearly legible glazed entry side and
    # insulated metal-clad service sides. The floor-to-floor datums are estimates.
    count = len(local)
    mid_y = (min_y + max_y) / 2 - origin_y
    front_edges = []
    for i, p0 in enumerate(local):
        p1 = local[(i + 1) % count]
        length = math.dist(p0, p1)
        midpoint_y = (p0[1] + p1[1]) / 2
        midpoint_x = (p0[0] + p1[0]) / 2
        # The public entrance faces the south/John R Wooden Drive side. The GIS
        # polygon has several short collinear segments there, so keep each edge.
        is_front = midpoint_y < (min(p[1] for p in local) + 8.5) and length > 3.0
        is_west = midpoint_x < min(p[0] for p in local) + 9 and length > 4.5
        if is_front or is_west:
            front_edges.append((i, p0, p1, length, is_front))

        # Continuous masonry/metal base, then three glazing and spandrel bands.
        panel(f"KFPC | opaque base wall {i:02d}", p0, p1, 0.45, 1.25, concrete, asset, offset=0.045)
        if is_front or is_west:
            glazing_bands = [(1.25, 3.85), (4.38, 7.76), (8.28, 11.45)]
            spandrel_mat = charcoal
            glass_mat = glass
        else:
            glazing_bands = [(1.55, 3.45), (4.65, 6.9), (8.85, 10.7)]
            spandrel_mat = cream
            glass_mat = glass
        for level, (z0, z1) in enumerate(glazing_bands):
            panel(f"KFPC | glass curtainwall edge {i:02d} level {level+1}",
                  p0, p1, z0, z1, glass_mat, asset, offset=0.055)
            # Continuous perimeter spandrels articulate the three floors.
            if level < 2:
                upper = glazing_bands[level + 1][0]
                panel(f"KFPC | floor spandrel edge {i:02d} level {level+1}",
                      p0, p1, z1, upper, spandrel_mat, asset, offset=0.075)
        panel(f"KFPC | parapet fascia edge {i:02d}", p0, p1, 11.45, 12.75,
              cream if (is_front or is_west) else charcoal, asset, offset=0.055)

        # Vertical aluminum mullions at a 4.5 m rhythm; dark horizontal transoms
        # make the three floors readable in the photo and retain correct scale.
        bays = max(1, math.ceil(length / 4.5))
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        for b in range(bays + 1):
            t = b / bays
            q = (p0[0] + dx * t, p0[1] + dy * t)
            box_mesh(f"KFPC | mullion {i:02d}-{b:02d}",
                     (q[0]-0.055, q[1]-0.055, 1.20),
                     (q[0]+0.055, q[1]+0.055, 11.50), mullion, asset)
        for z in (3.92, 7.83):
            panel(f"KFPC | transom {i:02d}-{z:.2f}", p0, p1, z, z + 0.10,
                  mullion, asset, offset=0.13)

    # An inset upper administrative level creates the layered roof silhouette.
    # Continuous ribbon windows are retained, but the glazing steps back from the
    # exterior steel/panel line at this level.
    for i, p0 in enumerate(top_local):
        p1 = top_local[(i + 1) % count]
        panel(f"KFPC | upper level glazing {i:02d}", p0, p1, 8.35, 11.8, glass, asset, offset=0.06)
        panel(f"KFPC | upper level roof fascia {i:02d}", p0, p1, 11.8, 12.7, cream, asset, offset=0.08)

    slab("KFPC | folded roof deck", top_local, 13.1, 0.38, cream, asset)

    # Training/support spaces read through the curtain wall; these are schematic
    # fit-out masses, not measured room partitions. A high central hall remains open.
    cx, cy = 0.0, 0.0
    span_x = max(p[0] for p in local) - min(p[0] for p in local)
    span_y = max(p[1] for p in local) - min(p[1] for p in local)
    box_mesh("KFPC | team hall internal screen", (-span_x * 0.23, -span_y * 0.03, 0.6),
             (span_x * 0.23, span_y * 0.02, 11.6), charcoal, asset)
    box_mesh("KFPC | sports medicine interior core", (-span_x * 0.40, span_y * 0.12, 0.55),
             (-span_x * 0.22, span_y * 0.43, 3.8), cream, asset)
    box_mesh("KFPC | meeting rooms interior core", (span_x * 0.20, span_y * 0.10, 4.35),
             (span_x * 0.42, span_y * 0.42, 7.7), cream, asset)
    box_mesh("KFPC | strength zone turf floor", (-span_x * 0.19, span_y * 0.05, 0.5),
             (span_x * 0.19, span_y * 0.43, 0.61), turf_green, asset)
    # A simple stair flight is visible in the glass lobby; individual treads are
    # grouped as one mesh so the library remains small and portable.
    stairs_v, stairs_f = [], []
    steps = 18
    stair_x0, stair_x1 = -span_x * 0.15, span_x * 0.14
    stair_y0, stair_y1 = -span_y * 0.34, -span_y * 0.08
    tread = (stair_y1 - stair_y0) / steps
    for j in range(steps):
        x0, x1 = stair_x0 + j * 0.10, stair_x1
        y0, y1 = stair_y0 + j * tread, stair_y0 + (j + 1) * tread
        z0, z1 = 0.8 + j * 0.17, 0.8 + (j + 1) * 0.17
        base = len(stairs_v)
        stairs_v.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
        stairs_f.extend([(base+0,base+3,base+2,base+1),(base+4,base+5,base+6,base+7),
                         (base+0,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),
                         (base+2,base+3,base+7,base+6),(base+3,base+0,base+4,base+7)])
    link_mesh("KFPC | lobby stair - schematic", stairs_v, stairs_f, steel, asset)

    # Entrance canopy: two angular metal planes extend west from the public entry.
    # The aerial footprint and entry photo place this at the west/parking-lot end.
    xmin, xmax = min(p[0] for p in local), max(p[0] for p in local)
    ymin = min(p[1] for p in local)
    canopy_half = 12.0
    canopy_depth = 8.5
    canopy_center_y = 4.3
    canopy_outer_x = xmin - canopy_depth
    canopy_inner_x = xmin + 1.7
    canopy_y0, canopy_y1 = canopy_center_y - canopy_half, canopy_center_y + canopy_half
    canopy_verts = [(canopy_outer_x, canopy_y0, 13.3),
                    (canopy_outer_x, canopy_y1, 13.3),
                    (canopy_inner_x, canopy_y1, 14.55),
                    (canopy_inner_x, canopy_y0, 14.55),
                    (canopy_outer_x, canopy_y0, 13.0),
                    (canopy_outer_x, canopy_y1, 13.0),
                    (canopy_inner_x, canopy_y1, 14.25),
                    (canopy_inner_x, canopy_y0, 14.25)]
    canopy_faces = [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    link_mesh("KFPC | floating angular entrance canopy", canopy_verts, canopy_faces, cream, asset)
    # Five slender angled stainless columns support the cantilevered canopy.
    for index, t in enumerate((-0.82, -0.42, 0.0, 0.42, 0.82)):
        y = canopy_center_y + canopy_half * t
        lean = 1.05 * (1 if index % 2 == 0 else -1)
        tube_between(f"KFPC | splayed stainless canopy column {index+1}",
                     (canopy_outer_x + 0.55, y - lean, 0.25),
                     (canopy_outer_x + 0.55, y, 13.5), 0.34, steel, asset)

    # Landmark west entrance fascia: charcoal backing, oversized P and address.
    west_wall_x = xmin - 0.08
    logo_center_y = canopy_center_y + 3.0
    box_mesh("KFPC | champagne P sign backing",
             (west_wall_x - 0.12, logo_center_y - 6.1, 8.2),
             (west_wall_x + 0.12, logo_center_y + 6.1, 12.25), cream, asset)
    p_logo = add_text("KFPC | Purdue P sign", "P", (west_wall_x - 0.16, logo_center_y, 8.55),
                      5.15, (0, 0, 0), sign_black, asset, extrude=0.08)
    p_logo.rotation_mode = "QUATERNION"
    p_logo.rotation_quaternion = Vector((-1, 0, 0)).to_track_quat("Z", "Y")
    address = add_text("KFPC | address number 1228", "1228",
                       (west_wall_x - 0.17, logo_center_y - 5.4, 3.95),
                       1.25, (0, 0, 0), charcoal, asset, extrude=0.045)
    address.rotation_mode = "QUATERNION"
    address.rotation_quaternion = Vector((-1, 0, 0)).to_track_quat("Z", "Y")
    building_name = add_text("KFPC | building name at entry", "KOZUCH FOOTBALL PERFORMANCE COMPLEX",
                             (west_wall_x - 0.18, logo_center_y - 7.7, 1.65), 0.43,
                             (0, 0, 0), sign_black, asset, extrude=0.018)
    building_name.rotation_mode = "QUATERNION"
    building_name.rotation_quaternion = Vector((-1, 0, 0)).to_track_quat("Z", "Y")

    # Split the footprint itself into two roof wings with opposite gentle slopes.
    # This evokes Populous's two-plane roof line while staying strictly inside the
    # verified GIS building outline (the previous single-block massing overreached).
    west_roof = clip_polygon_x(top_local, 0.0, True)
    east_roof = clip_polygon_x(top_local, 0.0, False)
    if west_roof:
        sloped_slab("KFPC | west flight-inspired roof plane", west_roof,
                    lambda x, y: 13.80 + 0.006 * y, 0.28, cream, asset)
    if east_roof:
        sloped_slab("KFPC | east flight-inspired roof plane", east_roof,
                    lambda x, y: 14.08 - 0.006 * y, 0.28, cream, asset)

    # Black-and-gold tapered site steps at the entry make the front base legible.
    for tier in range(3):
        z0 = 0.1 + tier * 0.14
        box_mesh(f"KFPC | entry step {tier+1}",
                 (canopy_outer_x - 1.6 - tier*0.55,
                  canopy_center_y - canopy_half*0.52 - tier*0.45, z0),
                 (canopy_outer_x - tier*0.55,
                  canopy_center_y + canopy_half*0.52 + tier*0.45, z0 + 0.14),
                 concrete, asset)

    # Preview-only lighting/camera are deliberately outside the exported collection.
    world = bpy.data.worlds.new("KFPC Preview World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.43, 0.54, 0.68, 1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.38
    sun_data = bpy.data.lights.new("KFPC Preview Sun", "SUN")
    sun = bpy.data.objects.new("KFPC Preview Sun", sun_data)
    preview_collection.objects.link(sun)
    sun.rotation_euler = (math.radians(28), math.radians(-24), math.radians(-32))
    sun_data.energy = 2.0
    area_data = bpy.data.lights.new("KFPC Preview Fill", "AREA")
    area = bpy.data.objects.new("KFPC Preview Fill", area_data)
    preview_collection.objects.link(area)
    area.location = (0, -70, 55)
    area_data.energy = 7000
    area_data.shape = "DISK"
    area_data.size = 55
    area.rotation_euler = (Vector((0,0,6)) - area.location).to_track_quat("-Z", "Y").to_euler()
    overview_camera = make_camera(preview_collection,
                                  (span_x * 0.58, ymin - span_y * 1.05, 34),
                                  (0, 0, 6.7), max(span_x, span_y) * 1.38,
                                  "KFPC_Overview_Camera")
    entrance_camera = make_camera(preview_collection,
                                  (xmin - 67, canopy_center_y - 39, 25),
                                  (xmin + 10, canopy_center_y, 7.0), 102,
                                  "KFPC_Entrance_Camera")
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x = 1700
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.camera = entrance_camera
    scene.render.filepath = str(EVIDENCE_DIR / "preview_entrance.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = overview_camera
    scene.render.filepath = str(EVIDENCE_DIR / "preview_three_quarter.png")
    bpy.ops.render.render(write_still=True)

    # Save only after the preview is rendered; paths are portable and no external
    # textures are linked. The export contract is exactly one named asset collection.
    ASSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
    assets = [o for o in asset.all_objects if o.type in {"MESH", "CURVE", "FONT"}]
    bounds = [[min((o.matrix_world @ Vector(c))[axis] for o in assets for c in o.bound_box),
               max((o.matrix_world @ Vector(c))[axis] for o in assets for c in o.bound_box)]
              for axis in range(3)]
    report = {
        "building_id": BUILDING_ID,
        "name": "Kozuch Football Performance Complex",
        "asset_path": ASSET_FILE.relative_to(ROOT).as_posix(),
        "asset_collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "placement_origin_xy_m": [origin_x, origin_y],
        "campus_local_conversion": {
            "origin_latitude": ORIGIN_LAT,
            "origin_longitude": ORIGIN_LON,
            "x_m": "(longitude - origin_longitude) * 111412.84 * cos(radians(origin_latitude))",
            "y_m": "(latitude - origin_latitude) * 111040.0",
            "projection_note": "Project's local approximate degree-to-meter conversion; not surveyed CRS. GIS source geometry returned EPSG:4326 from Purdue MapServer."
        },
        "source_feature": {
            "provider": "Purdue Libraries campus GIS ArcGIS MapServer layer 0",
            "feature_id": 1202,
            "abbreviation": "FPC",
            "source_name": "Kozuch Football Performance Complex",
            "address": "1228 John R Wooden Drive (Purdue Athletics)",
            "mapserver_reported_area_m2": feature["properties"].get("Shape.STArea()"),
            "local_approx_polygon_area_m2": footprint_area,
            "vertex_count": len(local),
            "source_url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0/query?where=OBJECTID%3D1202&outFields=*&returnGeometry=true&outSR=4326&f=geojson"
        },
        "sources": [
            {
                "provider": "Purdue Libraries Campus GIS / ArcGIS MapServer",
                "url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0/query?where=OBJECTID%3D1202&outFields=*&returnGeometry=true&outSR=4326&f=geojson",
                "feature_id": 1202,
                "retrieval_date": "2026-10-26",
                "source_crs": "EPSG:4326 response; service source is EPSG:3857",
                "method": "Use source polygon FID 1202, transform WGS84 coordinates with the project’s documented local approximation, and compare structural plan outline in campus XY.",
                "uncertainty": "Source polygon represents the campus feature labelled FPC; its edge may combine the joined footprint and additions. The source map's Shape.STArea() is Web Mercator area and differs from the local approximate area."
            },
            {
                "provider": "Purdue University Athletics official facilities page",
                "url": "https://purduesports.com/facilities/kozuch-football-performance-complex",
                "retrieval_date": "2026-10-26",
                "source_date": "Page describes the facility opened August 2017; current page accessed 2026-10-26",
                "source_crs": "Not applicable",
                "method": "Verify identity, address, three-level program, 112,000 square feet, use, and visible entrance against page text and official exterior photograph in sources/.",
                "uncertainty": "Published gross floor area does not provide surveyed exterior dimensions or elevations."
            },
            {
                "provider": "Populous, project architect",
                "url": "https://populous.com/showcases/purdue-university-football-performance-complex",
                "retrieval_date": "2026-10-26",
                "source_date": "Project opened 2017",
                "source_crs": "Not applicable",
                "method": "Use project description and exterior image for the glass curtainwall, old gold/black palette, two-plane flight-inspired roof concept, and location between practice fields.",
                "uncertainty": "No dimensioned elevations or construction drawings are published on the page."
            },
            {
                "provider": "Esri World Imagery basemap export",
                "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=-86.9181%2C40.4338%2C-86.9154%2C40.4372&bboxSR=4326&imageSR=4326&size=1600%2C1200&format=jpg&f=image",
                "retrieval_date": "2026-10-26",
                "source_date": "Imagery vintage is not exposed in the export response",
                "source_crs": "EPSG:4326 request/response, 1600x1200 pixels; export response extent [-86.9190166667, 40.4338, -86.9144833333, 40.4372]",
                "method": "Overlay Purdue GIS FID 1202 on the aerial image using the export response extent; the resulting outline aligns with the white-roofed football performance building at the north end of Mollenkopf.",
                "uncertainty": "The image export does not expose a dated imagery acquisition record."
            },
            {
                "provider": "FRP Inc. construction/project photography",
                "url": "https://frpinc.com/projects/purdue-university-football-performance-complex/",
                "retrieval_date": "2026-10-26",
                "source_date": "Project photo; page publication date not shown",
                "source_crs": "Not applicable",
                "method": "Use entrance photo to interpret glass corner, tilted stainless columns, canopy, metal panel cladding, and 1228 sign.",
                "uncertainty": "Single perspective photograph; component dimensions and hidden elevations remain estimated."
            },
            {
                "provider": "Purdue Archives and Special Collections / Historic Facilities Database",
                "url": "https://collections.lib.purdue.edu/campus/buildings/318",
                "retrieval_date": "2026-10-26",
                "source_date": "Database access date 2026-10-26",
                "source_crs": "Not applicable",
                "method": "Cross-check identity as a three-level building adjoining the north end of Mollenkopf Athletic Center, with football locker, weight, coaching, meeting, equipment, and sports medicine areas.",
                "uncertainty": "Historical narrative does not supply exact building dimensions or elevations."
            }
        ],
        "geometry": {
            "local_bounds_m": bounds,
            "structural_footprint_from_GIS": True,
            "floor_count": 3,
            "story_to_story_heights_m": [3.7, 3.9, 3.75],
            "total_envelope_height_m": 14.55,
            "height_status": "estimated from three-level description and image proportions; not measured",
            "roof": "two angular overlapping flight-inspired planes, interpreted from Populous description and photos; not surveyed"
        },
        "model_scope": {
            "mesh_and_curve_object_count": len(assets),
            "material_count": len([m for m in bpy.data.materials if m.name.startswith("KFPC |")]),
            "interior": "Schematic visible lobby/team-hall, support-room masses, floor plates and stair; not an as-built interior. No source plans were available in this build pass.",
            "edits": ["Replaced inaccurate single-block massing with a footprint derived from Purdue GIS FID 1202.", "Added three levels, facade glazing/mullions, metal cladding and entrance canopy.", "Added splayed stainless steel columns, Purdue P/address signage, floors and schematic lobby/support interior."]
        },
        "preview": "audit/purdue_football_performance_complex/preview_three_quarter.png",
        "preview_entrance": "audit/purdue_football_performance_complex/preview_entrance.png",
        "retrieval_date": "2026-10-26",
        "uncertainty": ["No measured elevation or construction drawings were found; floor heights and roof geometry are visual estimates.", "A campus GIS polygon identifies the FPC building feature; existing massing footprint differs substantially, and its source could not be validated. The detailed model follows authoritative FID 1202.", "Interior layout is schematic except for published program and visible lobby features."]
    }
    (EVIDENCE_DIR / "build_evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
