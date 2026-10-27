import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "audit" / "phi_kappa_sigma"
SOURCE = EVIDENCE / "sources" / "purdue_gis_fid829_2026-10-26.json"
OUTPUT = ROOT / "modular" / "buildings" / "massing_phi_kappa_sigma_fid829.blend"
COLLECTION_NAME = "Asset_massing_phi_kappa_sigma_fid829"
SCENE_NAME = "Building_massing_phi_kappa_sigma_fid829"
LAT0, LON0 = 40.4274, -86.9137


def campus_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def polygon_area(indices, points):
    return abs(sum(points[indices[i]][0] * points[indices[(i + 1) % len(indices)]][1] -
                   points[indices[(i + 1) % len(indices)]][0] * points[indices[i]][1]
                   for i in range(len(indices))) / 2.0)


def material(name, color, roughness=0.78):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    p = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = roughness
    return mat


def add_brick_noise(mat):
    nt = mat.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexBrick")
    tex.inputs["Color1"].default_value = (0.92, 0.90, 0.86, 1)
    tex.inputs["Color2"].default_value = (0.81, 0.80, 0.76, 1)
    tex.inputs["Mortar"].default_value = (0.64, 0.63, 0.60, 1)
    tex.inputs["Scale"].default_value = 1.0
    tex.inputs["Mortar Size"].default_value = 0.014
    tex.inputs["Brick Width"].default_value = 0.24
    tex.inputs["Row Height"].default_value = 0.07
    coords = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coords.outputs["UV"], tex.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.2
    bump.inputs["Distance"].default_value = 0.014
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])


def box(name, center, dimensions, mat, coll, rotation=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dimensions
    ob.rotation_euler[2] = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def cylinder(name, center, radius, depth, mat, coll, rotation=0, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                         location=center, rotation=(0, 0, rotation))
    ob = bpy.context.object
    ob.name = name
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def make_stepped_shell(points, modules, wall_mat, roof_mat, coll):
    """Build one watertight-ish shell from adjoining GIS partitions and stepped heights.

    Exterior walls are emitted once, module roofs are face caps (not extruded solids), and
    an internal step wall is added only where adjoining roof heights differ.
    """
    n = len(points)
    module_edges = []
    for module in modules:
        ids = module["ids"]
        module_edges.append({frozenset((ids[i], ids[(i + 1) % len(ids)]))
                             for i in range(len(ids))})
    verts = []
    vert_map = {}
    faces = []
    face_uvs = []

    def vi(index, z):
        key = (index, round(z, 5))
        if key not in vert_map:
            vert_map[key] = len(verts)
            verts.append((points[index][0], points[index][1], z))
        return vert_map[key]

    def face(indices, material_index=0, uvs=None):
        faces.append(tuple(indices))
        face_uvs.append(uvs)

    # One exterior wall per GIS boundary segment at the height of its owning wing.
    edge_owner = {}
    for i in range(n):
        j = (i + 1) % n
        key = frozenset((i, j))
        owners = [m for m, edges in enumerate(module_edges) if key in edges]
        assert len(owners) == 1, f"GIS boundary edge {i}-{j} has {len(owners)} owners"
        edge_owner[key] = owners[0]
        h = modules[owners[0]]["height"]
        edge_length = math.dist(points[i], points[j])
        face((vi(i, 0), vi(j, 0), vi(j, h), vi(i, h)),
             uvs=((0, 0), (edge_length, 0), (edge_length, h), (0, h)))

    # A single underside cap prevents visible gaps from below.
    base_poly = [Vector((p[0], p[1], 0)) for p in points]
    for tri in tessellate_polygon([base_poly]):
        face(tuple(vi(i, 0) for i in reversed(tri)))

    # Cap the shared seams only where the taller wing rises above its neighbor.
    shared = {}
    for mi, edges in enumerate(module_edges):
        for edge in edges:
            shared.setdefault(edge, []).append(mi)
    for edge, owners in shared.items():
        if len(owners) != 2:
            continue
        ia, ib = sorted(edge)
        h0, h1 = (modules[owners[0]]["height"], modules[owners[1]]["height"])
        low, high = min(h0, h1), max(h0, h1)
        if high - low > 0.02:
            edge_length = math.dist(points[ia], points[ib])
            face((vi(ia, low), vi(ib, low), vi(ib, high), vi(ia, high)),
                 uvs=((0, 0), (edge_length, 0), (edge_length, high - low), (0, high - low)))

    wall_mesh = bpy.data.meshes.new("Phi_Kappa_Sigma_SteppedShell_Mesh")
    wall_mesh.from_pydata(verts, [], faces)
    wall_mesh.materials.append(wall_mat)
    uv_layer = wall_mesh.uv_layers.new(name="FacadeUV_PhysicalMeters")
    for poly, face_uv in zip(wall_mesh.polygons, face_uvs):
        poly.material_index = 0
        if face_uv is not None:
            for loop_index, uv in zip(poly.loop_indices, face_uv):
                uv_layer.data[loop_index].uv = uv
    bm = bmesh.new()
    bm.from_mesh(wall_mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(wall_mesh)
    bm.free()
    wall_mesh.update()
    shell = bpy.data.objects.new("Phi Kappa Sigma | stepped GIS shell", wall_mesh)
    coll.objects.link(shell)
    bevel = shell.modifiers.new("Fine masonry edge easing", "BEVEL")
    bevel.width = 0.025
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    shell.modifiers.new("Weighted exterior normals", "WEIGHTED_NORMAL")

    # Independent single-surface roof caps prevent coincident full-height roof extrusions.
    for module in modules:
        ids = module["ids"]
        poly2d = [Vector((points[i][0], points[i][1], 0)) for i in ids]
        roof_verts = [(points[i][0], points[i][1], module["height"] + 0.015) for i in ids]
        roof_faces = [tuple(reversed(tri)) for tri in tessellate_polygon([poly2d])]
        roof_mesh = bpy.data.meshes.new(module["name"] + "_roof_mesh")
        roof_mesh.from_pydata(roof_verts, [], roof_faces)
        roof_mesh.materials.append(roof_mat)
        roof_mesh.update()
        roof = bpy.data.objects.new(module["name"] + " | flat roof cap", roof_mesh)
        coll.objects.link(roof)

    return shell, edge_owner, module_edges, shared


def add_roof_parapet(edge, height, points, outward, trim_mat, coll, label):
    ia, ib = edge
    a, b = points[ia], points[ib]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    tangent = (dx / length, dy / length)
    yaw = math.atan2(tangent[1], tangent[0])
    center = ((a[0] + b[0]) / 2 - outward[0] * 0.17,
              (a[1] + b[1]) / 2 - outward[1] * 0.17,
              height + 0.31)
    box(label, center, (length, 0.34, 0.62), trim_mat, coll, yaw)


def add_terrace_rail(edge, points, outward, height, trim_mat, coll, label):
    ia, ib = edge
    a, b = points[ia], points[ib]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    tangent = (dx / length, dy / length)
    yaw = math.atan2(tangent[1], tangent[0])
    rail_h = 1.02
    base_z = height
    # Set the rail just inside the terrace edge and raise its top over the flat deck.
    x = (a[0] + b[0]) / 2 - outward[0] * 0.12
    y = (a[1] + b[1]) / 2 - outward[1] * 0.12
    for k, zoff in enumerate((0.16, rail_h)):
        box(f"{label}_Horizontal_{k}", (x, y, base_z + zoff),
            (length, 0.09, 0.09), trim_mat, coll, yaw)
    posts = max(2, math.ceil(length / 1.35))
    for j in range(posts + 1):
        s = length * j / posts - length / 2
        cx, cy = x + tangent[0] * s, y + tangent[1] * s
        box(f"{label}_Post_{j}", (cx, cy, base_z + rail_h / 2),
            (0.10, 0.12, rail_h), trim_mat, coll, yaw)
    pickets = max(2, math.ceil(length / 0.28))
    for j in range(1, pickets):
        s = length * j / pickets - length / 2
        cx, cy = x + tangent[0] * s, y + tangent[1] * s
        box(f"{label}_Baluster_{j}", (cx, cy, base_z + rail_h / 2),
            (0.045, 0.07, rail_h - 0.1), trim_mat, coll, yaw)


def facade_point(origin, tangent, outward, s, z, offset=0):
    return (origin[0] + tangent[0] * s + outward[0] * offset,
            origin[1] + tangent[1] * s + outward[1] * offset, z)


def add_window(prefix, center, tangent, outward, z, width, height, mats, coll):
    # Dark sash, pale casing, sill, and black shutters echo current exterior photos.
    yaw = math.atan2(tangent[1], tangent[0])
    p = facade_point(center, tangent, outward, 0, z, 0.075)
    box(prefix + "_recess", p, (width, 0.10, height), mats["glass"], coll, yaw)
    for side in (-1, 1):
        q = facade_point(center, tangent, outward, side * (width * 0.59), z, 0.17)
        box(prefix + ("_shutter_L" if side < 0 else "_shutter_R"), q,
            (width * 0.22, 0.12, height * 1.04), mats["shutter"], coll, yaw)
        q = facade_point(center, tangent, outward, side * (width * 0.51), z, 0.16)
        box(prefix + ("_jamb_L" if side < 0 else "_jamb_R"), q,
            (0.12, 0.13, height + 0.24), mats["trim"], coll, yaw)
    q = facade_point(center, tangent, outward, 0, z + height / 2 + 0.06, 0.17)
    box(prefix + "_lintel", q, (width + 0.22, 0.15, 0.13), mats["trim"], coll, yaw)
    q = facade_point(center, tangent, outward, 0, z - height / 2 - 0.06, 0.2)
    box(prefix + "_sill", q, (width + 0.36, 0.28, 0.16), mats["trim"], coll, yaw)
    # A narrow white center mullion and a mid-rail are visible at close range.
    q = facade_point(center, tangent, outward, 0, z, 0.145)
    box(prefix + "_mullion", q, (0.055, 0.06, height), mats["trim"], coll, yaw)
    q = facade_point(center, tangent, outward, 0, z, 0.145)
    box(prefix + "_meeting_rail", q, (width, 0.06, 0.055), mats["trim"], coll, yaw)


def main():
    with SOURCE.open(encoding="utf-8") as f:
        feature = json.load(f)["features"][0]
    assert feature["attributes"]["FID"] == 829
    assert feature["attributes"]["BUILDING_N"] == "Phi Kappa Sigma"
    ring = feature["geometry"]["rings"][0]
    points = [campus_xy(float(p[0]), float(p[1])) for p in ring[:-1]]
    # The GIS ring is clockwise in the adopted campus frame. Remove any duplicate closure.
    if math.dist(points[0], points[-1]) < 0.001:
        points.pop()

    # A clean one-building file with a stable collection and scene for linked-library import.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene["source_feature_id"] = 829
    scene["wing_height_estimates_m"] = json.dumps({
        "rear_core": 9.5, "front_house": 10.1, "terrace_wing": 6.7
    }, sort_keys=True)
    coll = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(coll)

    mats = {
        "brick": material("White painted brick | procedural", (0.86, 0.84, 0.80)),
        "trim": material("Painted white trim", (0.94, 0.92, 0.87)),
        "roof": material("Pale gray low-slope roof membrane", (0.57, 0.56, 0.53)),
        "glass": material("Dark reflective sash glazing", (0.055, 0.09, 0.12), 0.24),
        "shutter": material("Near-black painted shutters", (0.035, 0.045, 0.055)),
        "door": material("Dark wood entry doors", (0.11, 0.075, 0.05)),
        "metal": material("Dark bronze door hardware", (0.24, 0.17, 0.08), 0.36),
    }
    add_brick_noise(mats["brick"])

    # Exact GIS footprint decomposed into the photographed main house, the slightly lower rear
    # block, and the low rooftop-terrace wing visible at the left end of current exterior photos.
    # The low wing's terrace railing is visible in chapter photo 4; actual elevations are estimates.
    modules = [
        {"name": "Phi Kappa Sigma | rear core", "ids": [0, 1, 2, 3, 4, 5, 12], "height": 9.5},
        {"name": "Phi Kappa Sigma | front house", "ids": [5, 6, 7, 12], "height": 10.1},
        {"name": "Phi Kappa Sigma | terrace wing", "ids": [7, 8, 9, 10, 11, 12], "height": 6.7},
    ]
    part_areas = {m["name"].split("|")[-1].strip(): polygon_area(m["ids"], points) for m in modules}
    full_area = polygon_area(list(range(len(points))), points)
    assert abs(sum(part_areas.values()) - full_area) < 0.01
    scene["footprint_partition_areas_m2_local"] = json.dumps(part_areas, sort_keys=True)
    scene["footprint_area_m2_local"] = full_area
    shell, edge_owner, module_edges, shared = make_stepped_shell(points, modules, mats["brick"], mats["roof"], coll)

    # The long southwest-facing edge is the front shown by the chapter's recent exterior images.
    # Determine it from the GIS ring; select the longest edge whose outward normal points south.
    signed = sum(points[i][0] * points[(i + 1) % len(points)][1] -
                 points[(i + 1) % len(points)][0] * points[i][1]
                 for i in range(len(points))) / 2
    front = None
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        # For a clockwise polygon the outward normal is the left-hand edge normal.
        outward = (-dy / length, dx / length) if signed < 0 else (dy / length, -dx / length)
        if outward[1] < -0.55 and (front is None or length > front[0]):
            front = (length, a, b, (dx / length, dy / length), outward)
    assert front and front[0] > 18
    length, a, b, tangent, outward = front
    center = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    yaw = math.atan2(tangent[1], tangent[0])

    # Current front photos show seven regular openings per long floor band, with the main door
    # interrupting the central ground-floor bay and a shallow centered upper pediment.
    window_width, window_height = 1.12, 1.72
    usable = length - 1.3
    for floor, z in enumerate((1.82, 5.05, 8.16), start=1):
        for j in range(7):
            s = -usable / 2 + usable * (j + 0.5) / 7
            if floor == 1 and abs(s) < 1.35:
                continue
            c = (center[0] + tangent[0] * s, center[1] + tangent[1] * s)
            add_window(f"Front_F{floor}_Window{j+1}", c, tangent, outward, z,
                       window_width, window_height, mats, coll)

    # Two shallow belt courses and a top cornice establish the three photographed stories.
    for z, depth, thick, label in ((3.35, 0.14, 0.12, "Lower_Belt"),
                                   (6.62, 0.18, 0.14, "Upper_Belt"),
                                   (9.97, 0.28, 0.18, "Front_Cornice")):
        c = facade_point(center, tangent, outward, 0, z, 0.20)
        box(f"Facade_{label}", c, (length + 0.35, depth, thick), mats["trim"], coll, yaw)

    # Repeated sash windows on the side walls; omit short jogs and any hidden inside corner.
    for i, p0 in enumerate(points):
        p1 = points[(i + 1) % len(points)]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        edge = math.hypot(dx, dy)
        if edge < 9.5 or (p0 == a and p1 == b):
            continue
        owner = edge_owner[frozenset((i, (i + 1) % len(points)))]
        wall_height = modules[owner]["height"]
        t = (dx / edge, dy / edge)
        n = (-t[1], t[0]) if signed < 0 else (t[1], -t[0])
        # Avoid decorative detail on edges aimed into the re-entrant footprint notch.
        for floor, z in enumerate((1.82, 5.05, 8.16), start=1):
            if z + 0.83 > wall_height - 0.35:
                continue
            count = max(2, int(edge // 4.5))
            for j in range(count):
                s = -edge / 2 + edge * (j + 0.5) / count
                c = ( (p0[0] + p1[0]) / 2 + t[0] * s,
                      (p0[1] + p1[1]) / 2 + t[1] * s )
                add_window(f"Side{i+1}_F{floor}_W{j+1}", c, t, n, z,
                           1.12, 1.66, mats, coll)

    # Main roof edges receive the shallow parapet in the official exterior photos; the low
    # terrace wing uses a fine white balustrade around its exposed roof perimeter instead.
    for i, p0 in enumerate(points):
        j = (i + 1) % len(points)
        p1 = points[j]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        edge_len = math.hypot(dx, dy)
        if edge_len < 1.8:
            continue
        t = (dx / edge_len, dy / edge_len)
        n = (-t[1], t[0]) if signed < 0 else (t[1], -t[0])
        owner = edge_owner[frozenset((i, j))]
        if owner == 2:
            add_terrace_rail((i, j), points, n, modules[owner]["height"], mats["trim"], coll,
                             f"Terrace_Railing_Edge_{i}")
        else:
            add_roof_parapet((i, j), modules[owner]["height"], points, n, mats["trim"], coll,
                             f"Roof_Parapet_Edge_{i}")

    # Centered classically proportioned entrance on the main, southwest-facing facade.
    door_c = center
    yaw = math.atan2(tangent[1], tangent[0])
    for side in (-1, 1):
        c = facade_point(door_c, tangent, outward, side * 1.48, 1.55, 0.28)
        box(f"Entry_Pilaster_{side}", c, (0.32, 0.38, 2.9), mats["trim"], coll, yaw)
        c = facade_point(door_c, tangent, outward, side * 1.48, 0.28, 0.31)
        box(f"Entry_Pilaster_Base_{side}", c, (0.56, 0.55, 0.36), mats["trim"], coll, yaw)
        c = facade_point(door_c, tangent, outward, side * 1.48, 3.02, 0.31)
        box(f"Entry_Pilaster_Capital_{side}", c, (0.56, 0.55, 0.24), mats["trim"], coll, yaw)
        c = facade_point(door_c, tangent, outward, side * 0.91, 1.42, 0.20)
        box(f"Entry_Sidelight_{side}", c, (0.34, 0.10, 1.95), mats["glass"], coll, yaw)
        for jamb_side in (-1, 1):
            c = facade_point(door_c, tangent, outward, side * 0.91 + jamb_side * 0.23, 1.42, 0.27)
            box(f"Entry_Sidelight_Jamb_{side}_{jamb_side}", c, (0.08, 0.14, 2.12), mats["trim"], coll, yaw)
        for rail_z in (0.35, 2.49):
            c = facade_point(door_c, tangent, outward, side * 0.91, rail_z, 0.27)
            box(f"Entry_Sidelight_Rail_{side}_{rail_z}", c, (0.46, 0.14, 0.08), mats["trim"], coll, yaw)
    c = facade_point(door_c, tangent, outward, 0, 1.35, 0.31)
    box("Entry_Double_Door", c, (1.25, 0.12, 2.48), mats["door"], coll, yaw)
    for side in (-1, 1):
        c = facade_point(door_c, tangent, outward, side * 0.43, 1.35, 0.39)
        box(f"Entry_Door_Leaf_{side}", c, (0.025, 0.04, 2.37), mats["metal"], coll, yaw)
    c = facade_point(door_c, tangent, outward, 0, 2.68, 0.38)
    box("Entry_Transom", c, (1.27, 0.1, 0.28), mats["glass"], coll, yaw)
    c = facade_point(door_c, tangent, outward, 0, 3.0, 0.31)
    box("Entry_Entablature", c, (2.25, 0.55, 0.32), mats["trim"], coll, yaw)
    c = facade_point(door_c, tangent, outward, 0, 3.24, 0.31)
    box("Entry_Cornice", c, (2.65, 0.72, 0.15), mats["trim"], coll, yaw)
    c = facade_point(door_c, tangent, outward, 0, 3.43, 0.62)
    box("Entry_Portico_Canopy", c, (3.35, 1.25, 0.2), mats["trim"], coll, yaw)
    for step in range(3):
        c = facade_point(door_c, tangent, outward, 0, 0.105 + step * 0.16, 0.62 + step * 0.34)
        box(f"Entry_Stone_Step_{step+1}", c, (3.15 + step * 0.35, 0.34, 0.16), mats["trim"], coll, yaw)

    # A restrained upper pediment recalls the current chapter-house photos without inventing signage.
    base_center = facade_point(door_c, tangent, outward, 0, 6.85, 0.3)
    half = 3.15
    tri = [
        facade_point(base_center[:2], tangent, outward, -half, base_center[2], 0),
        facade_point(base_center[:2], tangent, outward, half, base_center[2], 0),
        (base_center[0], base_center[1], base_center[2] + 1.35),
    ]
    # Open white gable frame; use 3D bar axes so both rakes meet cleanly at the apex.
    segments = [("Base", tri[0], tri[1]), ("Left_Rake", tri[2], tri[0]),
                ("Right_Rake", tri[1], tri[2])]
    for label, p0, p1 in segments:
        mid = tuple((p0[i] + p1[i]) / 2 for i in range(3))
        direction = Vector(p1) - Vector(p0)
        ob = box(f"Pediment_{label}", mid, (direction.length, 0.22, 0.18), mats["trim"], coll)
        ob.rotation_euler = direction.to_track_quat("X", "Z").to_euler()
    box("Pediment_Return", base_center, (6.3, 0.52, 0.16), mats["trim"], coll, yaw)

    # Keep a legible named root and stable campus-coordinates in this massing library.
    root = bpy.data.objects.new("AssetRoot_phi_kappa_sigma_fid829", None)
    coll.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.hide_render = True

    # Move every modeled part into the requested collection and set a clear, useful viewport.
    for ob in list(scene.objects):
        if coll not in ob.users_collection:
            for c in list(ob.users_collection):
                c.objects.unlink(ob)
            coll.objects.link(ob)
    # Pack any images (none are required: surface detail is procedural and self-contained).
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    print("SAVED", OUTPUT)
    print("FOOTPRINT_VERTICES", len(points), "AREA_M2_LOCAL_APPROX", abs(signed))
    print("FRONT_EDGE_LENGTH_M", length, "FRONT_NORMAL", outward)
    print("FOOTPRINT_PARTITION_AREAS_M2", part_areas)
    print("OBJECT_COUNT", len(coll.objects))


if __name__ == "__main__":
    main()
