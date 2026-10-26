"""Build a localized, evidence-backed Wang Hall asset for the Purdue campus library.

Run with Blender 5.x in background mode from the repository root:
  blender -b --python modular/buildings/build_massing_wang_hall_wang_0dac5ab.py

Geometry stays local to the manifest placement marker. The OSM building ring supplies the
structural outline; Purdue GIS, official building imagery, architect material and floor count
are preserved in audit/wang_hall/.
"""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_wang_hall_wang_0dac5ab"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / "wang_hall"
OSM_PATH = AUDIT / "sources" / "wang_hall_osm_way_301932787_full_2026-10-26.json"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def local_xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def read_outline():
    data = json.loads(OSM_PATH.read_text(encoding="utf-8"))
    way = next(e for e in data["elements"] if e["type"] == "way")
    nodes = {e["id"]: e for e in data["elements"] if e["type"] == "node"}
    ring = [local_xy(nodes[i]["lon"], nodes[i]["lat"]) for i in way["nodes"]]
    if ring[0] == ring[-1]:
        ring.pop()
    xmin, xmax = min(x for x, y in ring), max(x for x, y in ring)
    ymin, ymax = min(y for x, y in ring), max(y for x, y in ring)
    anchor = ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0)
    return [(x - anchor[0], y - anchor[1]) for x, y in ring], anchor, way


def material(name, color, roughness=0.55, metallic=0.0, brick=False, noise=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "transparent atrium glazing" in name.lower():
        bsdf.inputs["Alpha"].default_value = 0.24
        bsdf.inputs["Transmission Weight"].default_value = 0.22
        try:
            mat.surface_render_method = "BLENDED"
        except (AttributeError, TypeError, ValueError):
            pass
    if brick or noise:
        tex = nt.nodes.new("ShaderNodeTexCoord")
        if brick:
            texbrick = nt.nodes.new("ShaderNodeTexBrick")
            texbrick.inputs["Color1"].default_value = (0.40, 0.115, 0.065, 1)
            texbrick.inputs["Color2"].default_value = (0.30, 0.075, 0.045, 1)
            texbrick.inputs["Mortar"].default_value = (0.48, 0.43, 0.37, 1)
            texbrick.inputs["Scale"].default_value = 1.0
            texbrick.inputs["Mortar Size"].default_value = 0.02
            texbrick.inputs["Mortar Smooth"].default_value = 0.01
            texbrick.inputs["Brick Width"].default_value = 0.48
            texbrick.inputs["Row Height"].default_value = 0.20
            nt.links.new(tex.outputs["UV"], texbrick.inputs["Vector"])
            color_out = texbrick.outputs["Color"]
            height_out = texbrick.outputs["Fac"]
        else:
            texnoise = nt.nodes.new("ShaderNodeTexNoise")
            texnoise.inputs["Scale"].default_value = 3.0
            texnoise.inputs["Detail"].default_value = 3.0
            nt.links.new(tex.outputs["Object"], texnoise.inputs["Vector"])
            color_ramp = nt.nodes.new("ShaderNodeValToRGB")
            c1 = tuple(max(0, min(1, v * 0.82)) for v in color) + (1,)
            c2 = tuple(max(0, min(1, v * 1.13)) for v in color) + (1,)
            color_ramp.color_ramp.elements[0].color = c1
            color_ramp.color_ramp.elements[1].color = c2
            nt.links.new(texnoise.outputs["Fac"], color_ramp.inputs["Fac"])
            color_out = color_ramp.outputs["Color"]
            height_out = texnoise.outputs["Fac"]
        nt.links.new(color_out, bsdf.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.18 if brick else 0.07
        bump.inputs["Distance"].default_value = 0.035 if brick else 0.018
        nt.links.new(height_out, bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


class BoxBatch:
    """Append many oriented cuboids to one mesh to keep the library compact."""
    def __init__(self, name, collection, materials):
        self.name = name
        self.collection = collection
        self.materials = materials
        self.verts, self.faces, self.indices = [], [], []
        self.mat_index = {m.name: i for i, m in enumerate(materials)}

    def box(self, center, dims, mat, angle=0.0):
        cx, cy, cz = center
        dx, dy, dz = dims
        co, si = math.cos(angle), math.sin(angle)
        base = len(self.verts)
        for z in (-dz / 2, dz / 2):
            for y in (-dy / 2, dy / 2):
                for x in (-dx / 2, dx / 2):
                    self.verts.append((cx + co * x - si * y,
                                       cy + si * x + co * y,
                                       cz + z))
        local_faces = ((0, 1, 3, 2), (4, 6, 7, 5),
                       (0, 4, 5, 1), (2, 3, 7, 6),
                       (0, 2, 6, 4), (1, 5, 7, 3))
        mi = self.mat_index[mat.name]
        for face in local_faces:
            self.faces.append(tuple(base + i for i in face))
            self.indices.append(mi)

    def finish(self):
        if not self.faces:
            return None
        mesh = bpy.data.meshes.new(self.name + "Mesh")
        mesh.from_pydata(self.verts, [], self.faces)
        mesh.materials.clear()
        for mat in self.materials:
            mesh.materials.append(mat)
        mesh.update()
        # World-plan/elevation UVs keep brick courses at real dimensions on pavilion
        # wall batches as well as on the main mapped shell.
        uv = mesh.uv_layers.new(name="Facade course UV")
        for loop in mesh.loops:
            x, y, z = mesh.vertices[loop.vertex_index].co
            uv.data[loop.index].uv = (x, z)
        obj = bpy.data.objects.new(self.name, mesh)
        self.collection.objects.link(obj)
        for poly, idx in zip(mesh.polygons, self.indices):
            poly.material_index = idx
        return obj


def solid_polygon(name, ring, z0, z1, mat, collection):
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    area2 = sum(ring[i][0] * ring[(i + 1) % n][1] -
                ring[(i + 1) % n][0] * ring[i][1] for i in range(n))
    is_ccw = area2 > 0
    ix = list(range(n))
    bottom = list(reversed(ix)) if is_ccw else ix
    top = [i + n for i in (ix if is_ccw else list(reversed(ix)))]
    faces = [bottom, top]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n) if is_ccw else (j, i, i + n, j + n))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    uv = mesh.uv_layers.new(name="Masonry course UV")
    for poly_index, poly in enumerate(mesh.polygons):
        if poly_index >= 2:
            edge_index = poly_index - 2
            p = ring[edge_index]
            q = ring[(edge_index + 1) % n]
            dx, dy = q[0] - p[0], q[1] - p[1]
            length = math.hypot(dx, dy)
            tx, ty = dx / length, dy / length
        for loop_index in poly.loop_indices:
            vi = mesh.loops[loop_index].vertex_index
            x, y, z = verts[vi]
            if poly_index >= 2:
                u = (x - p[0]) * tx + (y - p[1]) * ty
                v = z
            else:
                u, v = x, y
            uv.data[loop_index].uv = (u, v)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def add_text(name, text, location, tangent, outward, size, mat, collection):
    curve = bpy.data.curves.new(name + "Text", "FONT")
    curve.body = text
    curve.size = size
    curve.extrude = 0.008
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    # Build orientation from the facade tangent and outward horizontal normal.
    # The text baseline follows the facade; local +Y is vertical.
    x_axis = Vector((tangent[0], tangent[1], 0)).normalized()
    z_axis = Vector((outward[0], outward[1], 0)).normalized()
    y_axis = Vector((0, 0, 1))
    from mathutils import Matrix
    matrix = Matrix(((x_axis.x, y_axis.x, z_axis.x),
                     (x_axis.y, y_axis.y, z_axis.y),
                     (x_axis.z, y_axis.z, z_axis.z)))
    obj.rotation_euler = matrix.to_euler()
    curve.materials.append(mat)
    return obj


def add_arched_crown(name, center, tangent, outward, half_width, depth,
                     base_z, rise, mat, collection):
    """Build a shallow elliptical parapet/crown extrusion over the atrium pavilion."""
    steps = 24
    section = [(-half_width, base_z - 0.24)]
    for i in range(steps + 1):
        u = -half_width + (2 * half_width * i / steps)
        top = base_z + rise * math.sqrt(max(0.0, 1.0 - (u / half_width) ** 2))
        section.append((u, top))
    section.append((half_width, base_z - 0.24))
    verts = []
    for side in (-1, 1):
        for u, z in section:
            verts.append((center[0] + tangent[0] * u + outward[0] * side * depth / 2,
                          center[1] + tangent[1] * u + outward[1] * side * depth / 2,
                          z))
    n = len(section)
    faces = [tuple(range(n)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def set_view(camera, location, target):
    camera.location = location
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def main():
    ring, anchor, way = read_outline()
    # Confirm the geometry origin is the massing marker's center before replacing it.
    assert abs(anchor[0] - 98.2954902278031) < 0.001, anchor
    assert abs(anchor[1] - 339.9100960000692) < 0.001, anchor

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        if col.users == 0:
            bpy.data.collections.remove(col)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)

    brick = material("Wang Hall | warm red-orange modular brick", (0.43, 0.15, 0.09), brick=True)
    stone = material("Wang Hall | pale limestone and precast", (0.72, 0.69, 0.62), noise=True)
    concrete = material("Wang Hall | light exposed concrete", (0.55, 0.55, 0.52), noise=True)
    glass = material("Wang Hall | blue-grey reflective glass", (0.035, 0.12, 0.19), roughness=0.16, metallic=0.32)
    atrium_glass = material("Wang Hall | transparent atrium glazing", (0.045, 0.16, 0.22), roughness=0.12, metallic=0.18)
    darkmetal = material("Wang Hall | charcoal anodized aluminum", (0.075, 0.09, 0.095), roughness=0.28, metallic=0.72)
    roofmat = material("Wang Hall | membrane roof", (0.39, 0.42, 0.42), roughness=0.78, noise=True)
    amber = material("Wang Hall | warm lobby light", (0.95, 0.52, 0.16), roughness=0.5)
    floor = material("Wang Hall | pale lobby stone floor", (0.66, 0.63, 0.56), noise=True)
    wood = material("Wang Hall | maple interior panels", (0.52, 0.29, 0.12), roughness=0.4, noise=True)
    carpet = material("Wang Hall | charcoal commercial carpet", (0.17, 0.18, 0.18), roughness=0.96, noise=True)
    green = material("Wang Hall | green lab accent", (0.26, 0.38, 0.22), roughness=0.8)
    white = material("Wang Hall | white aluminum trim", (0.78, 0.80, 0.78), roughness=0.25, metallic=0.35)

    # Verified 4-storey height from the OSM feature (14.8 m), corroborated by the
    # architect and Purdue dedication record. Roof and floor elevations are rounded.
    body_top = 14.22
    story = 3.48
    body = solid_polygon("Wang Hall | source-backed structural footprint", ring, 0.34, body_top,
                         brick, asset)
    solid_polygon("Wang Hall | stone base and storefront plinth", ring, 0.0, 0.72,
                  concrete, asset)
    roof_deck = solid_polygon("Wang Hall | flat roof deck", ring, body_top, 14.42, roofmat, asset)

    # Determine exterior normals for the ordered OSM polygon and compute the primary
    # street facade (southwest-facing side along Northwestern Avenue).
    area2 = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] -
                ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring)))
    ccw = area2 > 0
    edges = []
    for i, p in enumerate(ring):
        q = ring[(i + 1) % len(ring)]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        if length < 0.8:
            continue
        tx, ty = dx / length, dy / length
        # Right-hand normal for a counter-clockwise outer ring, left for clockwise.
        nx, ny = (ty, -tx) if ccw else (-ty, tx)
        edges.append({"p": p, "q": q, "len": length, "t": (tx, ty), "n": (nx, ny),
                      "angle": math.atan2(ty, tx), "i": i})
    front_candidates = [e for e in edges if e["len"] >= 8 and e["n"][1] < -0.25]
    if not front_candidates:
        front_candidates = sorted(edges, key=lambda e: e["n"][1])[:2]
    # Select the continuous street-facing wall plane by normal direction. A y-only
    # filter also catches the two angled end returns and puts an entry bay in the core.
    main_edge = max(front_candidates, key=lambda e: e["len"])
    front_edges = [e for e in front_candidates
                   if e["n"][0] * main_edge["n"][0] + e["n"][1] * main_edge["n"][1] > 0.96]
    front_len = sum(e["len"] for e in front_edges)
    front_center = (sum(((e["p"][0] + e["q"][0]) / 2) * e["len"] for e in front_edges) / front_len,
                    sum(((e["p"][1] + e["q"][1]) / 2) * e["len"] for e in front_edges) / front_len)
    # The mapped facade has shallow chamfered offsets, so project the weighted center
    # onto the nearest straight front segment before placing glazing and the entrance.
    main_edge = min(front_edges,
                    key=lambda e: math.hypot((e["p"][0] + e["q"][0]) / 2 - front_center[0],
                                             (e["p"][1] + e["q"][1]) / 2 - front_center[1]))
    along = max(0.0, min(main_edge["len"],
                          (front_center[0] - main_edge["p"][0]) * main_edge["t"][0] +
                          (front_center[1] - main_edge["p"][1]) * main_edge["t"][1]))
    front_center = (main_edge["p"][0] + main_edge["t"][0] * along,
                    main_edge["p"][1] + main_edge["t"][1] * along)
    # Carve the documented central atrium approach through the street wall. This lets
    # the modeled balcony, stair and gathering-space structure read behind the glazing.
    cavity_depth = 34.0
    cut_mesh = bpy.data.meshes.new("Wang Hall atrium opening cutter mesh")
    cut_mesh.from_pydata([(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5),
                          (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5),
                          (0.5, -0.5, -0.5), (0.5, -0.5, 0.5),
                          (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)], [],
                         [(0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1),
                          (2, 3, 7, 6), (0, 1, 3, 2), (4, 6, 7, 5)])
    cutter = bpy.data.objects.new("Wang Hall atrium temporary cutter", cut_mesh)
    asset.objects.link(cutter)
    cutter.location = (front_center[0] - main_edge["n"][0] * (cavity_depth / 2 - 0.25),
                       front_center[1] - main_edge["n"][1] * (cavity_depth / 2 - 0.25), 8.38)
    cutter.rotation_euler.z = main_edge["angle"]
    cutter.scale = (14.2, cavity_depth, 11.10)
    bpy.context.view_layer.objects.active = cutter
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    boolean = body.modifiers.new("Source-supported four-storey atrium opening", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = cutter
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    cutter.select_set(False)
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    # Interrupt the roof slab above the projecting atrium pavilion. Without this
    # small source-visible roof notch the curved crown is hidden by the flat deck.
    roof_cut = bpy.data.objects.new("Wang Hall atrium roof notch cutter", cut_mesh)
    asset.objects.link(roof_cut)
    roof_cut.location = (front_center[0] - main_edge["n"][0] * 2.2,
                         front_center[1] - main_edge["n"][1] * 2.2, 14.25)
    roof_cut.rotation_euler.z = main_edge["angle"]
    roof_cut.scale = (16.0, 4.6, 1.4)
    bpy.context.view_layer.objects.active = roof_cut
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    roof_bool = roof_deck.modifiers.new("Atrium pavilion roof reveal", "BOOLEAN")
    roof_bool.operation = "DIFFERENCE"
    roof_bool.solver = "EXACT"
    roof_bool.object = roof_cut
    bpy.context.view_layer.objects.active = roof_deck
    bpy.ops.object.modifier_apply(modifier=roof_bool.name)
    bpy.data.objects.remove(roof_cut, do_unlink=True)

    trim_batch = BoxBatch("Wang Hall | facade bands, frames and pilasters", asset,
                          [stone, concrete, darkmetal, white, glass, amber])
    glass_batch = BoxBatch("Wang Hall | facade glazing and storefront", asset,
                           [glass, darkmetal, white, atrium_glass])
    tower_batch = BoxBatch("Wang Hall | projecting atrium pavilion masonry", asset,
                           [brick, stone, darkmetal])
    # Story bands, brick piers, and windows follow the mapped perimeter edge by edge.
    for e in edges:
        if e["len"] < 3.2:
            continue
        p, q = e["p"], e["q"]
        tx, ty = e["t"]
        nx, ny = e["n"]
        angle = e["angle"]
        cx, cy = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        # Slight inset from the source wall line keeps projected pieces inside the outline.
        wall_x, wall_y = cx - nx * 0.12, cy - ny * 0.12
        for z in (3.42, 6.90, 10.38, 13.86):
            trim_batch.box((wall_x, wall_y, z), (e["len"], 0.18, 0.20), stone, angle)
        trim_batch.box((wall_x, wall_y, 0.78), (e["len"], 0.18, 0.12), stone, angle)
        if e["len"] < 7.0:
            continue
        bay = 5.35
        count = max(1, int(e["len"] / bay))
        pitch = e["len"] / count
        win_w = min(4.05, pitch * 0.76)
        for j in range(count):
            s = (j + 0.5) * pitch
            wx = p[0] + tx * s - nx * 0.02
            wy = p[1] + ty * s - ny * 0.02
            # The central glass hall is a direct architect-source feature on the street face.
            is_front = e in front_edges
            if is_front and math.hypot(wx - front_center[0], wy - front_center[1]) < 8.6:
                continue
            # Ground-level public/retail glazing, then three rows of divided upper windows.
            glass_batch.box((wx + nx * 0.04, wy + ny * 0.04, 1.88),
                            (win_w, 0.11, 2.12), glass, angle)
            for xoff in (-win_w / 2, win_w / 2):
                trim_batch.box((wx + tx * xoff + nx * 0.12,
                                wy + ty * xoff + ny * 0.12, 1.88),
                               (0.11, 0.16, 2.32), white, angle)
            trim_batch.box((wx + nx * 0.12, wy + ny * 0.12, 0.76),
                           (win_w + 0.14, 0.16, 0.12), white, angle)
            # upper storeys, with two-lite vertical glazing and a transom in each bay
            for level in range(1, 4):
                z = level * story + 1.77
                wh = 2.70 if level < 3 else 2.55
                glass_batch.box((wx + nx * 0.04, wy + ny * 0.04, z),
                                (win_w, 0.11, wh), glass, angle)
                for xoff in (-win_w / 2, 0, win_w / 2):
                    trim_batch.box((wx + tx * xoff + nx * 0.12,
                                    wy + ty * xoff + ny * 0.12, z),
                                   (0.075, 0.15, wh + 0.12), white, angle)
                trim_batch.box((wx + nx * 0.12, wy + ny * 0.12, z - wh * 0.20),
                               (win_w, 0.14, 0.075), white, angle)
                # Pale stone head and sill; inset brick panel sits between window rows.
                trim_batch.box((wx + nx * 0.12, wy + ny * 0.12, z + wh / 2 + 0.16),
                               (win_w + 0.32, 0.18, 0.14), stone, angle)
                trim_batch.box((wx + nx * 0.12, wy + ny * 0.12, z - wh / 2 - 0.14),
                               (win_w + 0.32, 0.18, 0.12), stone, angle)

    # Distinctive, projecting central atrium pavilion and raised curved crown, modeled
    # from the architect's northwest elevation and completed-building photographs.
    t = main_edge["t"]
    n = main_edge["n"]
    angle = main_edge["angle"]
    ax, ay = front_center
    tower_front = 0.88
    # Tall brick cheeks flank the narrow glass screen and visibly project from the wings.
    for xoff in (-5.75, 5.75):
        tower_batch.box((ax + t[0] * xoff + n[0] * tower_front,
                         ay + t[1] * xoff + n[1] * tower_front, 7.25),
                        (3.25, 1.70, 13.15), brick, angle)
    # Brick spandrel above the glazed atrium, beneath a light elliptical cap.
    tower_batch.box((ax + n[0] * tower_front, ay + n[1] * tower_front, 13.40),
                    (14.7, 1.70, 1.75), brick, angle)
    # Tall glass atrium between the tower piers and the public ground-floor doors.
    pane_z, pane_h, pane_w = 8.45, 8.05, 8.25
    glass_batch.box((ax + n[0] * 1.78, ay + n[1] * 1.78, pane_z),
                    (pane_w, 0.10, pane_h), atrium_glass, angle)
    glass_batch.box((ax + n[0] * 1.78, ay + n[1] * 1.78, 2.00),
                    (9.25, 0.10, 3.25), glass, angle)
    # A softly lit rear atrium wall gives depth through the transparent front screen.
    inside_atrium_wall = BoxBatch("Wang Hall | atrium inner luminous wall", asset,
                                  [floor, white, amber])
    atrium_back = (ax - n[0] * 25.0, ay - n[1] * 25.0)
    inside_atrium_wall.box((atrium_back[0], atrium_back[1], 8.0),
                          (10.2, 0.22, 12.0), white, angle)
    inside_atrium_wall.box((atrium_back[0], atrium_back[1] - n[1] * 0.13, 2.0),
                          (8.0, 0.04, 0.18), amber, angle)
    inside_atrium_wall.finish()
    for xoff in [-4.10, -2.05, 0, 2.05, 4.10]:
        trim_batch.box((ax + t[0] * xoff + n[0] * 1.86,
                        ay + t[1] * xoff + n[1] * 1.86, pane_z),
                       (0.075, 0.16, pane_h), darkmetal, angle)
    for z in (4.55, 6.75, 8.95, 11.15, 12.48):
        trim_batch.box((ax + n[0] * 1.86, ay + n[1] * 1.86, z),
                       (pane_w, 0.16, 0.10), darkmetal, angle)
    add_arched_crown("Wang Hall | curved limestone atrium crown",
                     (ax + n[0] * tower_front, ay + n[1] * tower_front),
                     t, n, 7.35, 1.72, 13.75, 1.05, stone, asset)
    tower_batch.finish()
    # Entry canopy, columns and fascia align to the street-facing glazed lobby.
    canopy_z = 4.15
    trim_batch.box((ax + n[0] * 1.25, ay + n[1] * 1.25, canopy_z),
                   (13.2, 2.35, 0.34), concrete, angle)
    for xoff in (-5.8, -4.0, -2.0, 2.0, 4.0, 5.8):
        trim_batch.box((ax + t[0] * xoff + n[0] * 2.20,
                        ay + t[1] * xoff + n[1] * 2.20, 2.05),
                       (0.22, 0.22, 3.85), white, angle)
    add_text("Wang Hall | entrance lettering", "SENG-LIANG WANG HALL",
             (ax + n[0] * 2.30, ay + n[1] * 2.30, canopy_z + 0.28),
             t, n, 0.42, darkmetal, asset)

    trim_batch.finish()
    glass_batch.finish()

    # Low continuous parapet and roof edge; rooftop skylight and mechanical groups.
    parapet = BoxBatch("Wang Hall | roof parapet, skylight and equipment", asset,
                       [stone, roofmat, glass, darkmetal, concrete])
    roof_z = 14.42
    for e in edges:
        if e["len"] > 1.5:
            c = ((e["p"][0] + e["q"][0]) / 2,
                 (e["p"][1] + e["q"][1]) / 2)
            parapet.box((c[0], c[1], 14.62), (e["len"], 0.34, 0.38), stone, e["angle"])
    roof_angle = math.atan2(-0.79, 0.61)
    parapet.box((0, 0, 14.47), (33.0, 7.6, 0.14), glass, roof_angle)
    for xoff in (-16.5, 16.5):
        parapet.box((xoff * math.cos(roof_angle), xoff * math.sin(roof_angle), 14.57),
                    (0.16, 8.0, 0.18), darkmetal, roof_angle)
    for yoff in (-3.8, 3.8):
        parapet.box((-yoff * math.sin(roof_angle), yoff * math.cos(roof_angle), 14.57),
                    (33.0, 0.16, 0.18), darkmetal, roof_angle)
    for x, y, sx, sy, h in [(-14, 4, 3.8, 2.2, 0.26), (-7, 3, 4.3, 2.6, 0.34),
                            (10, 0, 4.0, 2.7, 0.30), (16, -6, 3.4, 2.2, 0.25),
                            (-10, -7, 2.8, 2.0, 0.22)]:
        parapet.box((x, y, 14.42 + h / 2), (sx, sy, h), concrete, roof_angle)
    parapet.finish()

    # Interior: a schematic four-storey atrium, balcony edges and lobby seating. The
    # architect describes an open, light-filled atrium; exact room layout was unavailable.
    inside = BoxBatch("Wang Hall | atrium interior and gathering spaces", asset,
                      [floor, white, glass, wood, carpet, green, amber, darkmetal])
    core_center = (front_center[0] - main_edge["n"][0] * 18.0,
                   front_center[1] - main_edge["n"][1] * 18.0)

    def interior_xy(u, v):
        return (core_center[0] + u * main_edge["t"][0] - v * main_edge["n"][0],
                core_center[1] + u * main_edge["t"][1] - v * main_edge["n"][1])

    for level in range(4):
        z = 0.95 + level * story
        # Balcony bands around a central opening; restrained to the documented common area.
        for u, v, sx, sy in [(-6.8, 0, 6.0, 0.22), (6.8, 0, 6.0, 0.22),
                             (0, -8.0, 11.4, 0.22), (0, 8.0, 11.4, 0.22)]:
            x, y = interior_xy(u, v)
            inside.box((x, y, z), (sx, sy, 0.22), floor, angle)
            inside.box((x, y, z + 0.55), (sx, 0.08, 0.12), white, angle)
            inside.box((x, y, z + 0.28), (sx, 0.06, 0.55), glass, angle)
        for u in (-6.8, 6.8):
            x, y = interior_xy(u, 0)
            inside.box((x, y, z + 0.25), (0.12, 16.0, 0.60), glass, angle)
    # Ground lobby tile, reception, feature wall and stairs (visible through atrium glass).
    x, y = interior_xy(0, 0)
    inside.box((x, y, 0.88), (14.0, 16.0, 0.16), floor, angle)
    x, y = interior_xy(0, 6.0)
    inside.box((x, y, 2.2), (8.0, 0.32, 2.5), wood, angle)
    inside.box((x, y - 0.22, 3.35), (7.5, 0.14, 0.22), amber, angle)
    x, y = interior_xy(0, -6.6)
    inside.box((x, y, 1.55), (5.6, 1.15, 0.82), wood, angle)
    # Simplified stair flights switch back on each level inside the atrium volume.
    for level in range(3):
        z = 1.2 + level * story
        for i in range(14):
            u = -5.0 + i * 0.72
            zz = z + i * 0.17
            x, y = interior_xy(u, -3.8 + (level % 2) * 7.6)
            inside.box((x, y, zz), (0.78, 1.12, 0.18), white, angle)
        for u in (-5.0, 5.0):
            x, y = interior_xy(u, -3.8 + (level % 2) * 7.6)
            inside.box((x, y, z + 1.0), (0.06, 1.05, 1.8), darkmetal, angle)
    # A light public-space feel without claiming a verified floor plan.
    for u in (-4.8, 4.8):
        x, y = interior_xy(u, -0.8)
        inside.box((x, y, 1.35), (2.2, 0.72, 0.55), carpet, angle)
        inside.box((x, y, 1.67), (1.95, 0.58, 0.14), green, angle)
    inside.finish()

    # Discrete entry furniture, planters, benches and bollards support the public frontage.
    site = BoxBatch("Wang Hall | entrance furnishings", asset,
                    [concrete, darkmetal, stone, green, wood])
    for xoff in (-8.6, 8.6):
        site.box((ax + t[0] * xoff + n[0] * 3.3,
                  ay + t[1] * xoff + n[1] * 3.3, 0.32), (2.5, 1.0, 0.64), concrete, angle)
        site.box((ax + t[0] * xoff + n[0] * 3.3,
                  ay + t[1] * xoff + n[1] * 3.3, 0.75), (2.1, 0.65, 0.28), stone, angle)
        site.box((ax + t[0] * xoff + n[0] * 3.3,
                  ay + t[1] * xoff + n[1] * 3.3, 1.6), (1.7, 0.4, 1.4), green, angle)
    for i in range(7):
        s = -10.2 + i * 3.4
        site.box((ax + t[0] * s + n[0] * 4.6, ay + t[1] * s + n[1] * 4.6, 0.46),
                 (0.22, 0.22, 0.92), darkmetal, angle)
    for s in (-14, -10, 10, 14):
        site.box((ax + t[0] * s + n[0] * 5.1,
                  ay + t[1] * s + n[1] * 5.1, 0.55), (2.3, 0.58, 0.82), wood, angle)
        site.box((ax + t[0] * s + n[0] * 5.1,
                  ay + t[1] * s + n[1] * 5.1, 0.98), (2.2, 0.54, 0.10), darkmetal, angle)
    site.finish()

    # Separate, clearly named preview rig. It is kept outside the exported asset collection.
    rig = bpy.data.collections.new("__PreviewRig_WangHall")
    scene.collection.children.link(rig)
    camera_data = bpy.data.cameras.new("Wang Hall preview camera")
    camera = bpy.data.objects.new("Wang Hall preview camera", camera_data)
    rig.objects.link(camera)
    camera_data.lens = 58
    scene.camera = camera
    light_data = bpy.data.lights.new("Wang Hall key", "AREA")
    light = bpy.data.objects.new("Wang Hall key", light_data)
    rig.objects.link(light)
    light.location = (-55, -70, 78)
    light_data.energy = 16000
    light_data.shape = "DISK"
    light_data.size = 42
    light2_data = bpy.data.lights.new("Wang Hall fill", "AREA")
    light2 = bpy.data.objects.new("Wang Hall fill", light2_data)
    rig.objects.link(light2)
    light2.location = (65, 25, 40)
    light2_data.energy = 11000
    light2_data.size = 36
    for obj in (light, light2):
        obj.rotation_euler = (math.radians(20), 0, 0)
    world = bpy.data.worlds.new("Wang Hall preview sky")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.40, 0.48, 0.58, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.68

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(AUDIT / "preview_three_quarter.png")
    camera_data.dof.use_dof = False
    camera_data.clip_end = 400
    set_view(camera, (-112, -122, 56), (0, 0, 6.8))
    bpy.ops.render.render(write_still=True)

    # Close facade review view directly checks the projecting atrium pavilion,
    # arched crown, glazing, window proportions and entry against CSO photos.
    scene.render.filepath = str(AUDIT / "preview_atrium_detail.png")
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    camera_data.type = "PERSP"
    camera_data.lens = 74
    close_camera = (ax + n[0] * 62 - t[0] * 13,
                    ay + n[1] * 62 - t[1] * 13, 20.5)
    set_view(camera, close_camera, (ax, ay, 7.3))
    bpy.ops.render.render(write_still=True)

    # Top-down roof review preview.
    scene.render.filepath = str(AUDIT / "preview_roof_plan.png")
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    camera.location = (0, 0, 190)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 125
    bpy.ops.render.render(write_still=True)

    scene.camera = camera
    scene.render.filepath = "//wang_hall_preview.png"
    scene.unit_settings.system = "METRIC"
    scene.render.resolution_percentage = 55
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH), compress=True)
    print("WANG_BUILD_OK", json.dumps({
        "asset": str(ASSET_PATH), "asset_id": ASSET_ID, "collection": COLLECTION_NAME,
        "scene": SCENE_NAME, "anchor_xy_m": anchor, "osm_vertices": len(ring),
        "story_count": 4, "height_m": 14.8, "asset_objects": len(asset.objects),
        "sha256": hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
