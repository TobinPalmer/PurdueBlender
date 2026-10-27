"""Build the source-backed, local-coordinate Horticulture Building library.

Run with Blender 5.2.3 in background mode. The output collection name and asset
path are fixed by modular/manifest.json; preview-only objects live outside the
export collection.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "horticulture_building.blend"
EVIDENCE_DIR = ROOT / "audit" / "horticulture_building"
GIS = EVIDENCE_DIR / "sources" / "purdue_gis_fid232.json"
PREVIEW = EVIDENCE_DIR / "renders" / "horticulture_exterior.png"
TOP = EVIDENCE_DIR / "renders" / "horticulture_top.png"
ENTRY = EVIDENCE_DIR / "renders" / "horticulture_entry.png"
LAT0, LON0 = 40.4274, -86.9137
LON_M = 111412.84 * math.cos(math.radians(LAT0))
LAT_M = 111040.0


def material(name, color, roughness=0.75, metallic=0.0, noise_scale=22.0, variation=0.08):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    tex = nodes.new("ShaderNodeTexCoord")
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.025 if name.endswith("brick") else 0.055
    bump.inputs["Distance"].default_value = 0.004 if name.endswith("brick") else 0.018
    # A restrained object-space variation keeps the brick facade legible without
    # creating false vertical striping on the concave multi-face GIS shell.
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 5.0 if name.endswith("brick") else noise_scale
    noise.inputs["Detail"].default_value = 2.0 if name.endswith("brick") else 3.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = tuple(max(0.0, c * (1.0 - variation)) for c in color) + (1.0,)
    ramp.color_ramp.elements[1].color = tuple(min(1.0, c * (1.0 + variation)) for c in color) + (1.0,)
    mat.node_tree.links.new(tex.outputs["Object"], noise.inputs["Vector"])
    mat.node_tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    mat.node_tree.links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    mat.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    mat.node_tree.links.new(shader.outputs["BSDF"], out.inputs["Surface"])
    return mat


def mesh_object(name, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    if mat:
        mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def prism(name, ring, z0, z1, mat, collection):
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return mesh_object(name, verts, faces, mat, collection)


def box(name, center, size, mat, collection, bevel=0.0, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    obj.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Small stone arris", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def simplify_ring(ring, tolerance=0.25):
    ring = list(ring)
    while len(ring) > 8:
        candidate = (float("inf"), None)
        for i, p in enumerate(ring):
            a, b = ring[i - 1], ring[(i + 1) % len(ring)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            den = dx * dx + dy * dy
            if den < 1e-10:
                dist = math.dist(p, a)
            else:
                t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den))
                dist = math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
            if dist < candidate[0]:
                candidate = (dist, i)
        if candidate[0] > tolerance:
            break
        ring.pop(candidate[1])
    return ring


def segment_quad(a, b, z0, z1, offset):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    ox, oy = uy, -ux  # exterior for a counter-clockwise footprint
    p = (a[0] + ox * offset, a[1] + oy * offset)
    q = (b[0] + ox * offset, b[1] + oy * offset)
    return [(p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], z1), (p[0], p[1], z1)]


def add_windows(ring, floor_levels, stone, dark, glass, collection, main_edge):
    glass_v, glass_f, frame_v, frame_f, sash_v, sash_f, sill_v, sill_f = [], [], [], [], [], [], [], []
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 5.4:
            continue
        ux, uy = dx / length, dy / length
        ox, oy = uy, -ux
        if i == main_edge:
            # Source image: two paired central window groups with single
            # flanking openings. The group spacing is estimated; the actual
            # west-facing elevation is registered separately from the map.
            window_centers = []
            for fraction, paired in ((0.13, False), (0.31, True), (0.69, True), (0.87, False)):
                center = fraction * length
                if paired:
                    window_centers.extend((center - 0.73, center + 0.73))
                else:
                    window_centers.append(center)
        else:
            count = max(1, round(length / 7.2))
            window_centers = [(k + 0.5) * length / count for k in range(count)]
        width, height = (1.08, 2.55) if i == main_edge else (1.05, 2.35)
        for floor_index, floor_z in enumerate(floor_levels):
            z0 = floor_z + 0.50
            row_centers = list(window_centers)
            if i == main_edge and floor_index > 0:
                # The official photo shows a central single-pair-single group
                # above the portal on both upper rows. This fills the 14.17 m
                # blank strip left by the earlier six-window interpretation.
                mid = length * 0.5
                row_centers.extend((mid - 4.2, mid - 0.73, mid + 0.73, mid + 4.2))
            for center in row_centers:
                # Keep the doorway clear at grade; upper central openings are
                # deliberately placed above the shallow entry assembly.
                if i == main_edge and floor_index == 0 and abs(center - length * 0.5) < 2.8:
                    continue
                lo, hi = center - width / 2, center + width / 2
                off = 0.095
                window_base = z0
                window_height = height
                if i == main_edge and floor_index == 1 and abs(center - length * 0.5) < 5.0:
                    # Portal/balcony sits below the central second-row sash;
                    # raise the inner single-pair-single group to clear it.
                    window_base += 0.58
                    window_height -= 0.58
                x0, y0 = a[0] + ux * lo + ox * off, a[1] + uy * lo + oy * off
                x1, y1 = a[0] + ux * hi + ox * off, a[1] + uy * hi + oy * off
                idx = len(glass_v)
                glass_v.extend([(x0, y0, window_base), (x1, y1, window_base), (x1, y1, window_base + window_height), (x0, y0, window_base + window_height)])
                glass_f.append((idx, idx + 1, idx + 2, idx + 3))
                # Narrow dark steel frame and a source-visible limestone sill.
                frame = 0.055
                for d0, d1, bot, top in [
                    (lo - frame, lo + frame, window_base, window_base + window_height),
                    (hi - frame, hi + frame, window_base, window_base + window_height),
                    (lo, hi, window_base - frame, window_base + frame),
                    (lo, hi, window_base + window_height - frame, window_base + window_height + frame),
                ]:
                    idx = len(frame_v)
                    for d, z in ((d0, bot), (d1, bot), (d1, top), (d0, top)):
                        frame_v.append((a[0] + ux * d + ox * (off + 0.025), a[1] + uy * d + oy * (off + 0.025), z))
                    frame_f.append((idx, idx + 1, idx + 2, idx + 3))
                # Double-hung vertical meeting rail and horizontal sash bar.
                for d0, d1, zbot, ztop in [
                    (center - 0.035, center + 0.035, window_base, window_base + window_height),
                    (lo, hi, window_base + window_height * 0.52 - 0.035, window_base + window_height * 0.52 + 0.035),
                ]:
                    idx = len(sash_v)
                    for d, z in ((d0, zbot), (d1, zbot), (d1, ztop), (d0, ztop)):
                        sash_v.append((a[0] + ux * d + ox * (off + 0.04), a[1] + uy * d + oy * (off + 0.04), z))
                    sash_f.append((idx, idx + 1, idx + 2, idx + 3))
                idx = len(sill_v)
                for d, z in ((lo - 0.09, window_base - 0.18), (hi + 0.09, window_base - 0.18), (hi + 0.09, window_base - 0.04), (lo - 0.09, window_base - 0.04)):
                    sill_v.append((a[0] + ux * d + ox * (off + 0.055), a[1] + uy * d + oy * (off + 0.055), z))
                sill_f.append((idx, idx + 1, idx + 2, idx + 3))
    mesh_object("Historic sash windows | glazing", glass_v, glass_f, glass, collection)
    mesh_object("Historic sash windows | slender bronze frames", frame_v, frame_f, dark, collection)
    mesh_object("Historic sash windows | meeting rails", sash_v, sash_f, dark, collection)
    mesh_object("Historic sash windows | limestone sills", sill_v, sill_f, stone, collection)


def add_brick_pilasters(ring, index, z_top, brick, collection):
    """Raised brick piers on the source-photographed principal elevation."""
    a, b = ring[index], ring[(index + 1) % len(ring)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    ox, oy = uy, -ux
    angle = math.atan2(-uy, -ux)  # local box Y axis points outward
    # The photograph shows full-height vertical brick piers defining bays.
    for fraction in (0.035, 0.245, 0.755, 0.965):
        distance = length * fraction
        center = (a[0] + ux * distance + ox * 0.10, a[1] + uy * distance + oy * 0.10, z_top / 2)
        box("West elevation | brick pilaster", center, (0.48, 0.20, z_top), brick, collection, angle=angle)


def add_course(ring, z, thickness, mat, collection, offset=0.12):
    verts, faces = [], []
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        quad = segment_quad(a, b, z - thickness / 2, z + thickness / 2, offset)
        idx = len(verts)
        verts.extend(quad)
        faces.append((idx, idx + 1, idx + 2, idx + 3))
    mesh_object("Continuous limestone string course", verts, faces, mat, collection)


def add_brick_bed_joints(ring, index, z_top, mortar, collection):
    """Fine horizontal bed joints make the photographed brick read as masonry."""
    a, b = ring[index], ring[(index + 1) % len(ring)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    ox, oy = uy, -ux
    verts, faces = [], []
    for z in [0.26 + i * 0.28 for i in range(int((z_top - 0.3) / 0.28))]:
        idx = len(verts)
        for d, h in ((0.0, z - 0.008), (length, z - 0.008), (length, z + 0.008), (0.0, z + 0.008)):
            verts.append((a[0] + ux * d + ox * 0.035, a[1] + uy * d + oy * 0.035, h))
        faces.append((idx, idx + 1, idx + 2, idx + 3))
    mesh_object("West elevation | fine brick bed joints", verts, faces, mortar, collection)


def add_entry(ring, index, stone, dark, glass, collection):
    a, b = ring[index], ring[(index + 1) % len(ring)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    ox, oy = uy, -ux
    angle = math.atan2(-uy, -ux)  # box local Y axis is the outward facade normal
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    # Shallow flush classical portal follows the photo: broad carved stone
    # surround and inscription, paired door, upper cornice and narrow rail.
    cx, cy = mid[0] + ox * 0.11, mid[1] + oy * 0.11
    box("West entry | dark double door", (cx, cy, 1.53), (2.20, 0.12, 2.88), dark, collection, angle=angle)
    box("West entry | glazed transom", (cx, cy, 3.20), (2.24, 0.10, 0.48), glass, collection, angle=angle)
    # Door stile and rail articulate the glazed double leaf.
    box("West entry | center door stile", (cx, cy + oy * 0.085, 1.55), (0.055, 0.035, 2.70), stone, collection, angle=angle)
    box("West entry | transom bar", (cx, cy + oy * 0.09, 3.18), (2.15, 0.04, 0.055), stone, collection, angle=angle)
    portal_z = 2.28
    for side in (-1, 1):
        px, py = cx + ux * side * 1.53, cy + uy * side * 1.53
        box("West entry | flush carved portal jamb", (px, py, portal_z), (0.28, 0.12, 4.12), stone, collection, 0.015, angle)
    box("West entry | carved flush entablature", (cx, cy, 4.35), (4.05, 0.14, 0.48), stone, collection, 0.015, angle=angle)
    box("West entry | shallow portal cornice", (cx + ox * 0.015, cy + oy * 0.015, 4.68), (4.35, 0.17, 0.16), stone, collection, 0.015, angle=angle)
    # Inscription is shallow text on the facade panel, not a projecting sign.
    text_curve = bpy.data.curves.new("Horticulture carved portal inscription", "FONT")
    text_curve.body = "HORTICULTURE"
    text_curve.size = 0.24
    text_curve.align_x = "CENTER"
    text_curve.align_y = "CENTER"
    text_curve.extrude = 0.004
    text_obj = bpy.data.objects.new("West entry | carved HORTICULTURE inscription", text_curve)
    collection.objects.link(text_obj)
    text_obj.location = (cx + ox * 0.19, cy + oy * 0.19, 4.35)
    text_obj.rotation_euler = Vector((ox, oy, 0)).to_track_quat("Z", "Y").to_euler()
    text_curve.materials.append(dark)
    # Photo shows a short railing above the entry, beneath the second-story windows.
    rail_y = cy + oy * 0.12
    box("West entry | shallow balcony sill", (cx, rail_y, 4.90), (4.15, 0.18, 0.12), stone, collection, angle=angle)
    box("West entry | balcony top rail", (cx, rail_y + oy * 0.07, 5.55), (3.75, 0.045, 0.045), dark, collection, angle=angle)
    box("West entry | balcony lower rail", (cx, rail_y + oy * 0.07, 5.05), (3.75, 0.035, 0.035), dark, collection, angle=angle)
    for i in range(9):
        x = -1.72 + i * 0.43
        box("West entry | balcony baluster", (cx + ux * x + ox * 0.19, cy + uy * x + oy * 0.19, 5.30), (0.025, 0.025, 0.50), dark, collection, angle=angle)
    for step, (z, width, depth) in enumerate(((0.12, 3.2, 0.38), (0.28, 2.75, 0.32)), 1):
        step_center = (cx + ox * (0.20 + depth * 0.5), cy + oy * (0.20 + depth * 0.5), z)
        box(f"West entry | shallow step {step}", step_center, (width, depth, 0.24), stone, collection, 0.02, angle)


def build():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "renders").mkdir(parents=True, exist_ok=True)
    with GIS.open(encoding="utf-8") as f:
        source = json.load(f)
    attrs, geom = source["attributes"], source["geometry"]
    ring_geo = geom["rings"][0]
    if ring_geo[0] == ring_geo[-1]:
        ring_geo = ring_geo[:-1]
    world = [((p[0] - LON0) * LON_M, (p[1] - LAT0) * LAT_M) for p in ring_geo]
    origin = ((min(p[0] for p in world) + max(p[0] for p in world)) / 2,
              (min(p[1] for p in world) + max(p[1] for p in world)) / 2)
    ring = [(x - origin[0], y - origin[1]) for x, y in world]
    cleaned = []
    for p in ring:
        if not cleaned or math.dist(p, cleaned[-1]) > 0.04:
            cleaned.append(p)
    if len(cleaned) > 1 and math.dist(cleaned[0], cleaned[-1]) < 0.04:
        cleaned.pop()
    ring = simplify_ring(cleaned, 0.25)
    area2 = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring)))
    if area2 < 0:
        ring.reverse()
    edge_lengths = [math.dist(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring))]
    # GIS coordinates use X east/Y north. Purdue's campus map places HORT east
    # of the Agricultural Mall, and its official photo shows the planted mall
    # foreground. The west-facing long wall is therefore the registered photo
    # elevation. The source image does not establish an exact door offset.
    west_edges = []
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        length = edge_lengths[i]
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        outward = (uy, -ux)
        if outward[0] < -0.80 and length > 30.0:
            west_edges.append(i)
    if not west_edges:
        raise ValueError("Could not identify a west-facing Horticulture photo elevation from the GIS ring")
    principal = max(west_edges, key=lambda i: edge_lengths[i])

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    scene = bpy.context.scene
    for child in list(scene.collection.children):
        scene.collection.children.unlink(child)

    asset = bpy.data.collections.new("Asset_horticulture_building")
    scene.collection.children.link(asset)
    structure = bpy.data.collections.new("Structure")
    facade = bpy.data.collections.new("Facade_Details")
    interiors = bpy.data.collections.new("Schematic_Interior")
    asset.children.link(structure)
    asset.children.link(facade)
    asset.children.link(interiors)
    stage = bpy.data.collections.new("Preview_Stage")
    scene.collection.children.link(stage)

    brick = material("Horticulture | warm red brick", (0.34, 0.095, 0.055), noise_scale=34.0, variation=0.18)
    stone = material("Horticulture | light limestone", (0.72, 0.66, 0.53), noise_scale=12.0, variation=0.07)
    glass = material("Horticulture | blue-black sash glazing", (0.035, 0.085, 0.105), roughness=0.2, metallic=0.12, noise_scale=6.0)
    dark = material("Horticulture | dark bronze door", (0.045, 0.055, 0.05), roughness=0.45, metallic=0.38)
    roof = material("Horticulture | charcoal flat roof", (0.13, 0.145, 0.15), roughness=0.8)
    concrete = material("Horticulture | cast concrete base", (0.38, 0.37, 0.33), roughness=0.88)
    floor = material("Horticulture | schematic floor plates", (0.49, 0.46, 0.39), roughness=0.68)
    mortar = material("Horticulture | dark brick mortar", (0.28, 0.085, 0.060), roughness=0.92)

    # GIS vertical units are undocumented (verticalSpatialReference=null).
    # F02=11.7, F03=23.4, and R=35.1 form 11.7-unit floor intervals. If these
    # values are feet—as the Elevation=615.9 site value makes plausible—R is
    # 10.70m above grade and Extrution=48 is 14.63m. The model uses R as a
    # best-estimate roof level; its evidence records 10.70–14.63m as the range
    # implied by the competing fields. No field is claimed as surveyed height.
    height = 35.1 * 0.3048
    base = 0.0
    floor_levels = [0.0, 11.7 * 0.3048, 23.4 * 0.3048]
    prism("HORT structural shell | official GIS FID 232 outline", ring, base, height, brick, structure)
    prism("HORT raised foundation plinth", ring, base, 0.48, concrete, structure)
    # Flat roof follows the concave GIS polygon, preserving its open/reentrant plan.
    prism("HORT flat roof deck | GIS outline", ring, height - 0.18, height + 0.08, roof, structure)
    add_windows(ring, floor_levels, stone, dark, glass, facade, principal)
    add_brick_pilasters(ring, principal, height - 0.42, brick, facade)
    add_brick_bed_joints(ring, principal, height - 0.42, mortar, facade)
    add_course(ring, height - 0.20, 0.40, stone, facade, 0.17)
    add_entry(ring, principal, stone, dark, glass, facade)

    # Schematic floors are intentionally limited: no unsupported room plan is implied.
    for i, level in enumerate(floor_levels):
        verts = [(x, y, 0.15 + level) for x, y in ring]
        mesh_object(f"Schematic floor plate {i + 1} | no room layout implied", verts, [tuple(range(len(ring)))], floor, interiors)

    # Preview stage is isolated from the exported Asset collection.
    ground = material("Preview stage | campus lawn", (0.19, 0.25, 0.17), roughness=0.94, noise_scale=2.0)
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    dx, dy = max(xs) - min(xs), max(ys) - min(ys)
    span = max(dx, dy) * 1.5
    box("Preview ground plane", (0, 0, -0.30), (span, span, 0.18), ground, stage)

    # Put principal side toward camera; offset along the side to show one return.
    a, b = ring[principal], ring[(principal + 1) % len(ring)]
    ux, uy = (b[0] - a[0]) / edge_lengths[principal], (b[1] - a[1]) / edge_lengths[principal]
    ox, oy = uy, -ux
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    view_target = Vector((0, 0, height * 0.43))
    view_distance = max(dx, dy) * 1.55
    camera_data = bpy.data.cameras.new("Horticulture exterior camera")
    camera = bpy.data.objects.new("Horticulture exterior camera", camera_data)
    stage.objects.link(camera)
    camera.location = (mid[0] + ox * view_distance + ux * view_distance * 0.28,
                       mid[1] + oy * view_distance + uy * view_distance * 0.28,
                       height * 0.98 + view_distance * 0.30)
    camera.rotation_euler = (view_target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.lens = 48
    scene.camera = camera
    for name, loc, energy, size in (
        ("Large soft key", (20, -40, 65), 24000, 45),
        ("Cool fill", (-45, 30, 35), 12000, 38),
    ):
        light_data = bpy.data.lights.new(name, "AREA")
        light_obj = bpy.data.objects.new(name, light_data)
        stage.objects.link(light_obj)
        light_obj.location = loc
        light_data.energy = energy
        light_data.shape = "DISK"
        light_data.size = size
        light_obj.rotation_euler = (Vector((0, 0, 5)) - light_obj.location).to_track_quat("-Z", "Y").to_euler()
    world = bpy.data.worlds.new("Purdue overcast preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.24, 0.31, 0.40, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.48
    scene.world = world
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 1280, 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"

    asset["building_id"] = "horticulture_building"
    asset["source_feature_id"] = 232
    asset["placement_origin_xy_m"] = list(origin)
    asset["local_coordinates"] = True
    asset["height_m"] = height
    asset["height_range_m"] = [height, 48.0 * 0.3048]
    asset["height_status"] = "estimated; R=35.1 interpreted as feet gives 10.70m; Extrution=48 interpreted as feet gives 14.63m upper bound; GIS does not publish attribute units or vertical CRS"
    asset["photo_elevation"] = "west-facing edge; inferred from campus map position east of Agricultural Mall and planted foreground in official photo"
    asset["photo_elevation_edge_index"] = principal
    asset["footprint_source"] = "Purdue Campus GIS BuildingShapesZip4 layer 0, FID 232"
    asset["footprint_vertex_count"] = len(ring)
    asset["facade_source"] = "Purdue Events Horticulture Building exterior photo"

    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET), compress=True)
    scene.render.filepath = str(PREVIEW)
    bpy.ops.render.render(write_still=True)

    # Top-down evidence view: set temporary camera, render, restore front camera.
    top_data = bpy.data.cameras.new("Horticulture roof plan evidence camera")
    top_cam = bpy.data.objects.new("Horticulture roof plan evidence camera", top_data)
    stage.objects.link(top_cam)
    top_cam.location = (0, 0, max(dx, dy) * 2.0)
    top_cam.rotation_euler = (0, 0, 0)
    top_data.type = "ORTHO"
    top_data.ortho_scale = max(dx, dy) * 1.45
    scene.camera = top_cam
    scene.render.filepath = str(TOP)
    bpy.ops.render.render(write_still=True)
    scene.camera = camera
    bpy.data.objects.remove(top_cam, do_unlink=True)
    bpy.data.cameras.remove(top_data)
    # Entry close view using same world-space camera direction and a narrower lens.
    entry_data = bpy.data.cameras.new("Horticulture entry evidence camera")
    entry_cam = bpy.data.objects.new("Horticulture entry evidence camera", entry_data)
    stage.objects.link(entry_cam)
    entry_cam.location = (mid[0] + ox * 30 + ux * 5, mid[1] + oy * 30 + uy * 5, 8.4)
    entry_target = Vector((mid[0], mid[1], 4.9))
    entry_cam.rotation_euler = (entry_target - entry_cam.location).to_track_quat("-Z", "Y").to_euler()
    entry_data.lens = 58
    scene.camera = entry_cam
    scene.render.filepath = str(ENTRY)
    bpy.ops.render.render(write_still=True)
    scene.camera = camera
    bpy.data.objects.remove(entry_cam, do_unlink=True)
    bpy.data.cameras.remove(entry_data)
    # Re-save without temporary cameras; main preview camera remains outside Asset.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET), compress=True)

    footprint_bounds = [[min(xs), max(xs)], [min(ys), max(ys)], [0.0, height]]
    summary = {
        "building_id": "horticulture_building",
        "asset_file": "modular/buildings/horticulture_building.blend",
        "collection": "Asset_horticulture_building",
        "source_feature_id": 232,
        "placement_origin_xy_m": list(origin),
        "local_footprint_bounds_m": [[min(p[0] for p in ring), max(p[0] for p in ring)], [min(p[1] for p in ring), max(p[1] for p in ring)]],
        "ring_vertices_after_simplification": len(ring),
        "simplification_tolerance_m": 0.25,
        "approximate_model_height_m": height,
        "height_range_m": [height, 48.0 * 0.3048],
        "height_status": "estimate, not surveyed; GIS vertical units/semantics undocumented. Under a feet hypothesis, R=35.1 -> 10.70m roof-level best estimate and Extrution=48 -> 14.63m upper bound. Three photo-visible levels align with F01/F02/F03; B=-10 is below grade; NUM_LEVELS/CountOfFLO=5 may count basement/ground levels.",
        "registered_photo_elevation": "west-facing GIS edge; map places HORT east of Agriculture Mall. The Purdue photo shows planted greenspace in foreground. Direction is a sourced inference; exact entrance coordinate along the wall remains estimated.",
        "world_bounds_local_m": footprint_bounds,
        "object_count_asset": len(asset.all_objects),
        "texture_paths": "none; procedural materials only",
        "renders": [str(PREVIEW), str(TOP), str(ENTRY)],
        "sha256": "pending reopen check",
    }
    (EVIDENCE_DIR / "build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("BUILT HORTICULTURE", json.dumps(summary), flush=True)


if __name__ == "__main__":
    build()

