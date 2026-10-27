"""Build the Delta Upsilon (FID 751) library from its verified GIS outline.

Run from the project root with Blender 5.2:
  blender -b modular/buildings/massing_house_301841256_1cc7641.blend \
    --python audit/delta_upsilon/build_delta_upsilon.py

The output library is local-coordinate geometry centered on the official
feature polygon centroid. Its campus placement is deliberately left to the
master coordinator.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular/buildings/massing_house_301841256_1cc7641.blend"
GIS_PATH = ROOT / "audit/delta_upsilon/official_fid_751.geojson"
AUDIT = ROOT / "audit/delta_upsilon"
ASSET_ID = "massing_house_301841256_1cc7641"
COLLECTION_NAME = "Asset_massing_house_301841256_1cc7641"
SCENE_NAME = "Building_massing_house_301841256_1cc7641"
BASE_OBJECT_NAME = "House_301841256"
MODEL_HEIGHT_M = 11.58  # Estimated from the GIS `Extrution=38` field, presumed feet.
WALL_EAVE_M = 9.35


class MeshAccumulator:
    def __init__(self, name, material):
        self.name = name
        self.material = material
        self.vertices = []
        self.faces = []
        self.uv_faces = []

    def face(self, points, uvs=None):
        start = len(self.vertices)
        self.vertices.extend(tuple(float(c) for c in p) for p in points)
        self.faces.append(tuple(range(start, start + len(points))))
        if uvs is None:
            uvs = [(0.0, 0.0)] * len(points)
        self.uv_faces.append(uvs)

    def box(self, center, axis_t, axis_n, width, depth, height, zbase=None):
        """Box aligned to edge tangent/outward normal and vertical Z."""
        c = Vector(center)
        t = Vector((axis_t[0], axis_t[1], 0.0)).normalized()
        n = Vector((axis_n[0], axis_n[1], 0.0)).normalized()
        if zbase is not None:
            c.z = zbase + height * 0.5
        hw, hd, hh = width * 0.5, depth * 0.5, height * 0.5
        corners = [
            c - t * hw - n * hd - Vector((0, 0, hh)),
            c + t * hw - n * hd - Vector((0, 0, hh)),
            c + t * hw + n * hd - Vector((0, 0, hh)),
            c - t * hw + n * hd - Vector((0, 0, hh)),
            c - t * hw - n * hd + Vector((0, 0, hh)),
            c + t * hw - n * hd + Vector((0, 0, hh)),
            c + t * hw + n * hd + Vector((0, 0, hh)),
            c - t * hw + n * hd + Vector((0, 0, hh)),
        ]
        k = len(self.vertices)
        self.vertices.extend(tuple(v) for v in corners)
        for side in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                     (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.faces.append(tuple(k + i for i in side))
            self.uv_faces.append([(0, 0), (1, 0), (1, 1), (0, 1)])

    def mesh_object(self, collection):
        mesh = bpy.data.meshes.new(self.name + "_Mesh")
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.materials.append(self.material)
        if self.faces:
            uv = mesh.uv_layers.new(name="UVMap")
            for poly, face_uvs in zip(mesh.polygons, self.uv_faces):
                for li, co in zip(poly.loop_indices, face_uvs):
                    uv.data[li].uv = co
        obj = bpy.data.objects.new(self.name, mesh)
        collection.objects.link(obj)
        return obj


def set_input(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def make_material(name, color, roughness=0.7, brick=False, stone=False,
                  roof=False, glass=False, wood=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (700, 40)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (460, 40)
    set_input(bsdf, "Roughness", roughness)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if glass:
        set_input(bsdf, "Metallic", 0.32)
        set_input(bsdf, "Roughness", 0.18)
        set_input(bsdf, "IOR", 1.48)
        set_input(bsdf, "Coat Weight", 0.25)
    if wood:
        set_input(bsdf, "Roughness", 0.55)
    if brick or stone or roof or wood:
        texcoord = nt.nodes.new("ShaderNodeTexCoord")
        texcoord.location = (-850, 40)
        vec = texcoord.outputs["UV"]
        if brick:
            tex = nt.nodes.new("ShaderNodeTexBrick")
            tex.location = (-570, 110)
            set_input(tex, "Color1", (0.18, 0.030, 0.018, 1))
            set_input(tex, "Color2", (0.30, 0.065, 0.036, 1))
            set_input(tex, "Mortar", (0.37, 0.30, 0.23, 1))
            set_input(tex, "Scale", 1.0)
            set_input(tex, "Mortar Size", 0.015)
            set_input(tex, "Mortar Smooth", 0.02)
            set_input(tex, "Brick Width", 0.52)
            set_input(tex, "Row Height", 0.24)
            set_input(tex, "Offset", 0.5)
            set_input(tex, "Offset Frequency", 2)
            nt.links.new(vec, tex.inputs["Vector"])
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            bump = nt.nodes.new("ShaderNodeBump")
            bump.location = (190, -160)
            set_input(bump, "Strength", 0.15)
            set_input(bump, "Distance", 0.035)
            nt.links.new(tex.outputs["Color"], bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        elif roof:
            tex = nt.nodes.new("ShaderNodeTexBrick")
            tex.location = (-570, 110)
            set_input(tex, "Color1", (0.035, 0.045, 0.06, 1))
            set_input(tex, "Color2", (0.075, 0.09, 0.12, 1))
            set_input(tex, "Mortar", (0.025, 0.03, 0.04, 1))
            set_input(tex, "Scale", 1.0)
            set_input(tex, "Brick Width", 0.36)
            set_input(tex, "Row Height", 0.19)
            set_input(tex, "Mortar Size", 0.006)
            set_input(tex, "Mortar Smooth", 0.01)
            set_input(tex, "Offset", 0.5)
            nt.links.new(vec, tex.inputs["Vector"])
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        elif wood:
            noise = nt.nodes.new("ShaderNodeTexNoise")
            noise.location = (-500, 80)
            set_input(noise, "Scale", 7.0)
            set_input(noise, "Detail", 3.0)
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.location = (-220, 90)
            ramp.color_ramp.elements[0].position = 0.22
            ramp.color_ramp.elements[0].color = (0.11, 0.035, 0.014, 1)
            ramp.color_ramp.elements[1].position = 0.78
            ramp.color_ramp.elements[1].color = (0.30, 0.10, 0.035, 1)
            nt.links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
            nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            noise = nt.nodes.new("ShaderNodeTexNoise")
            noise.location = (-530, 100)
            set_input(noise, "Scale", 4.5 if stone else 2.0)
            set_input(noise, "Detail", 2.0)
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.location = (-230, 100)
            if stone:
                ramp.color_ramp.elements[0].color = (0.38, 0.35, 0.30, 1)
                ramp.color_ramp.elements[1].color = (0.75, 0.70, 0.61, 1)
            else:
                ramp.color_ramp.elements[0].color = (0.2, 0.17, 0.14, 1)
                ramp.color_ramp.elements[1].color = (0.38, 0.33, 0.28, 1)
            nt.links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
            nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        set_input(bsdf, "Base Color", (*color, 1.0))
    return mat


def polygon_area(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
               poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) * 0.5


def polygon_centroid(poly):
    area6 = 0.0
    cx = cy = 0.0
    for i, (x, y) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        cross = x * y2 - x2 * y
        area6 += cross
        cx += (x + x2) * cross
        cy += (y + y2) * cross
    return (cx / (3.0 * area6), cy / (3.0 * area6))


def point_in_polygon(point, poly):
    x, y = point
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def line_intersection(a, v, b, w):
    det = v[0] * w[1] - v[1] * w[0]
    if abs(det) < 1e-8:
        return None
    delta = (b[0] - a[0], b[1] - a[1])
    t = (delta[0] * w[1] - delta[1] * w[0]) / det
    return (a[0] + t * v[0], a[1] + t * v[1])


def inward_offset(poly, distance):
    area = polygon_area(poly)
    sign = 1 if area > 0 else -1
    lines = []
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        # Interior is left for CCW polygons and right for CW polygons.
        inward = (-sign * dy / length, sign * dx / length)
        lines.append((a, (dx / length, dy / length), inward))
    result = []
    for i in range(len(poly)):
        prev = lines[(i - 1) % len(poly)]
        nxt = lines[i]
        a = (poly[i][0] + distance * prev[2][0], poly[i][1] + distance * prev[2][1])
        b = (poly[i][0] + distance * nxt[2][0], poly[i][1] + distance * nxt[2][1])
        p = line_intersection(a, prev[1], b, nxt[1])
        if p is None or math.dist(p, poly[i]) > distance * 8 + 1:
            p = ((poly[i][0] + distance * prev[2][0] + distance * nxt[2][0]) * 0.5,
                 (poly[i][1] + distance * prev[2][1] + distance * nxt[2][1]) * 0.5)
        result.append(p)
    return result


def add_quad(acc, A, B, z0, z1, uv_u0=0.0):
    acc.face([Vector((A[0], A[1], z0)), Vector((A[0], A[1], z1)),
              Vector((B[0], B[1], z1)), Vector((B[0], B[1], z0))],
             [(uv_u0, z0), (uv_u0, z1), (uv_u0 + math.dist(A, B), z1),
              (uv_u0 + math.dist(A, B), z0)])


def add_wall_panel(acc, A, B, z0, z1, openings):
    length = math.dist(A, B)
    u_breaks = [0.0, length]
    z_breaks = [z0, z1]
    for u0, u1, h0, h1 in openings:
        u_breaks.extend((max(0, u0), min(length, u1)))
        z_breaks.extend((max(z0, h0), min(z1, h1)))
    u_breaks = sorted(set(round(x, 5) for x in u_breaks if 0 <= x <= length))
    z_breaks = sorted(set(round(z, 5) for z in z_breaks if z0 <= z <= z1))
    dx, dy = (B[0] - A[0]) / length, (B[1] - A[1]) / length
    for i in range(len(u_breaks) - 1):
        ua, ub = u_breaks[i], u_breaks[i + 1]
        um = (ua + ub) * 0.5
        for j in range(len(z_breaks) - 1):
            za, zb = z_breaks[j], z_breaks[j + 1]
            zm = (za + zb) * 0.5
            if any(u0 < um < u1 and h0 < zm < h1 for u0, u1, h0, h1 in openings):
                continue
            pa = (A[0] + dx * ua, A[1] + dy * ua)
            pb = (A[0] + dx * ub, A[1] + dy * ub)
            # UV coordinates are in approximate physical meters for the brick shader.
            add_quad(acc, pa, pb, za, zb, uv_u0=ua)


def main():
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
    scene = bpy.data.scenes.get(SCENE_NAME)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if scene is None or collection is None:
        raise RuntimeError("Expected stable building scene/collection missing")

    # Verify the source feature identity before replacing its massing.
    feature = json.loads(GIS_PATH.read_text(encoding="utf-8"))["features"][0]
    props = feature["properties"]
    if props.get("FID") != 751 or props.get("BUILDING_N") != "Delta Upsilon":
        raise RuntimeError("FID 751 is not labeled Delta Upsilon in the source snapshot")
    lonlat = feature["geometry"]["coordinates"][0][:-1]
    world_poly = [((lon + 86.9137) * 84810.60416539927,
                   (lat - 40.4274) * 111040.0) for lon, lat in lonlat]
    origin = polygon_centroid(world_poly)
    poly = [(x - origin[0], y - origin[1]) for x, y in world_poly]
    if not point_in_polygon((0, 0), poly):
        raise RuntimeError("GIS centroid unexpectedly lies outside the building polygon")

    # Preserve the scene, collection, and original base object name, clearing only
    # the assigned collection's previous single massing object.
    existing = bpy.data.objects.get(BASE_OBJECT_NAME)
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    # Make reruns deterministic: discard unreferenced datablocks from earlier
    # versions of this same assigned asset before recreating stable names.
    # Remove orphan meshes/curves first so their material slots stop keeping
    # the prior materials alive during cleanup.
    for block_list in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for block in list(block_list):
            if block.users == 0 and (block.name.startswith("DU_") or
                                     block.name.startswith("House_301841256")):
                block_list.remove(block)

    brick = make_material("DU_Deep_Red_Brick", (0.42, 0.12, 0.08), brick=True)
    stone = make_material("DU_Light_Limestone_Trim", (0.68, 0.63, 0.55), stone=True)
    foundation = make_material("DU_Concrete_Foundation", (0.45, 0.43, 0.39), stone=True)
    slate = make_material("DU_Charcoal_Slate_Roof", (0.17, 0.19, 0.22), roof=True)
    glass = make_material("DU_Dark_Blue_Window_Glass", (0.018, 0.048, 0.085), roughness=0.2, glass=True)
    frame = make_material("DU_Painted_Window_Sash", (0.10, 0.13, 0.16), roughness=0.42)
    door_mat = make_material("DU_Dark_Stained_Wood_Entry", (0.18, 0.065, 0.025), wood=True)
    metal = make_material("DU_Door_Hardware", (0.38, 0.29, 0.17), roughness=0.32)
    sign_blue = make_material("DU_Sapphire_Name_Sign", (0.03, 0.13, 0.28), roughness=0.55)

    walls = MeshAccumulator("House_301841256", brick)
    foundation_mesh = MeshAccumulator("DU_Foundation_Courses", foundation)
    trim = MeshAccumulator("DU_Limestone_Bands_and_Sills", stone)
    glass_mesh = MeshAccumulator("DU_Blue_Sash_Glazing", glass)
    frames = MeshAccumulator("DU_Window_Sash_Frames", frame)
    door = MeshAccumulator("DU_Main_Entry_Door", door_mat)
    hardware = MeshAccumulator("DU_Entry_Hardware", metal)
    roof = MeshAccumulator("DU_Hipped_Slate_Roof", slate)
    signage = MeshAccumulator("DU_Freestanding_Chapter_Sign", brick)
    signpanel = MeshAccumulator("DU_Sign_Light_Stone_Panel", stone)
    steps = MeshAccumulator("DU_Entry_Stone_Steps", stone)

    # Height/story bands are estimates. The official image shows a brick facade
    # with three upper window rows and a low base; GIS `Extrution=38` is treated
    # as feet only as a plausible nominal height clue.
    upper_rows = [(1.65, 3.08), (4.35, 5.78), (7.05, 8.48)]
    basement_rows = (0.38, 0.92)
    upper_wall = WALL_EAVE_M
    n = len(poly)
    signed_area = polygon_area(poly)
    outward_sign = -1 if signed_area < 0 else 1
    all_window_positions = []
    door_info = None

    for i, A in enumerate(poly):
        B = poly[(i + 1) % n]
        dx, dy = B[0] - A[0], B[1] - A[1]
        length = math.hypot(dx, dy)
        if length < 0.5:
            continue
        t = (dx / length, dy / length)
        # Correct outward normal for the ring orientation.
        outn = (outward_sign * dy / length, outward_sign * -dx / length)
        opening_specs = []
        # The small south-facing footprint projection is the likely entrance bay.
        is_entry_front = (i == 4)
        door_u = length * 0.52 if is_entry_front else None
        door_width, door_height, door_base = 1.34, 2.35, 0.52
        if is_entry_front:
            opening_specs.append((door_u - door_width / 2, door_u + door_width / 2,
                                  door_base, door_base + door_height))
            door_info = (A, t, outn, door_u, i)

        # Regular tall sash windows, based on visible reference spacing. Counts
        # are reduced at corners and kept on every wall band as a schematic.
        margin = 0.95
        spacing = 3.6
        centers = []
        if length >= 2.8:
            count = max(1, int((length - 2 * margin) // spacing) + 1)
            if count == 1:
                centers = [length * 0.5]
            else:
                available = length - 2 * margin
                centers = [margin + k * available / (count - 1) for k in range(count)]
        for row_index, (z0, z1) in enumerate(upper_rows):
            for center in centers:
                w = min(1.28 if row_index == 0 else 1.15, max(0.72, length / (len(centers) + 1) * 0.54))
                if is_entry_front and abs(center - door_u) < 1.0:
                    continue
                opening_specs.append((center - w / 2, center + w / 2, z0, z1))
                all_window_positions.append((A, t, outn, center, w, z0, z1, False))
        # Small basement sash/windows at widely spaced bays.
        for center in centers[::2]:
            bw = min(0.82, max(0.55, length / (len(centers) + 1) * 0.38))
            opening_specs.append((center - bw / 2, center + bw / 2, *basement_rows))
            all_window_positions.append((A, t, outn, center, bw, *basement_rows, True))

        add_wall_panel(walls, A, B, 0.0, upper_wall, opening_specs)

        # Foundation and lightly expressed belt courses follow surveyed wall runs.
        for z0, z1 in ((0.0, 0.30),):
            add_quad(foundation_mesh, A, B, z0, z1, 0.0)
        for z in (0.94, 3.72, 6.50, 9.20):
            trim.box(((A[0] + B[0]) * 0.5 + outn[0] * 0.045,
                      (A[1] + B[1]) * 0.5 + outn[1] * 0.045,
                      z + 0.055), t, outn, length, 0.11, 0.11)

    # Deep blue sash windows, dark muntins, and projecting pale stone sills.
    for A, t, outn, center, width, z0, z1, basement in all_window_positions:
        e = Vector((A[0] + t[0] * center, A[1] + t[1] * center, (z0 + z1) / 2))
        nvec = Vector((outn[0], outn[1], 0))
        height = z1 - z0
        glass_mesh.face([e + Vector((-t[0]*width/2, -t[1]*width/2, -height/2)) + nvec*0.035,
                         e + Vector((t[0]*width/2, t[1]*width/2, -height/2)) + nvec*0.035,
                         e + Vector((t[0]*width/2, t[1]*width/2, height/2)) + nvec*0.035,
                         e + Vector((-t[0]*width/2, -t[1]*width/2, height/2)) + nvec*0.035],
                        [(0, 0), (1, 0), (1, 1), (0, 1)])
        bar = 0.055 if not basement else 0.045
        depth = 0.12
        # outer frame + central vertical sash and cross rail
        for sign in (-1, 1):
            frames.box(e + nvec*0.075 + Vector((t[0]*(width/2-bar/2*1.3*sign),
                                                t[1]*(width/2-bar/2*1.3*sign), 0)),
                       t, outn, bar, depth, height + bar*2)
            frames.box(e + nvec*0.075 + Vector((-t[0]*width/2, -t[1]*width/2,
                                                sign*(height/2-bar/2*1.3))),
                       t, outn, width + bar*2, depth, bar)
        frames.box(e + nvec*0.083, t, outn, bar*0.75, depth, height)
        frames.box(e + nvec*0.083, t, outn, width, depth, bar*0.72)
        if not basement:
            trim.box(e + nvec*0.10 + Vector((0, 0, -height/2 - 0.06)), t, outn,
                     width + 0.34, 0.24, 0.12)
            # Light, modest stone head/surround accents reflect the chapter photo.
            trim.box(e + nvec*0.085 + Vector((0, 0, height/2 + 0.055)), t, outn,
                     width + 0.18, 0.16, 0.09)

    # A simple solid wood panel-and-transom door inside the GIS footprint's
    # projecting entry bay. The exact door position is inferred from plan shape.
    if door_info:
        A, t, outn, door_u, _ = door_info
        center = Vector((A[0] + t[0]*door_u, A[1] + t[1]*door_u,
                         door_base + door_height/2))
        nvec = Vector((outn[0], outn[1], 0))
        door.box(center + nvec*0.045, t, outn, door_width*0.80, 0.09, door_height*0.95)
        # Raised transom glazing and three understated recessed panel bands.
        glass_mesh.face([center + nvec*0.10 + Vector((-t[0]*0.34,-t[1]*0.34,0.30)),
                         center + nvec*0.10 + Vector((t[0]*0.34,t[1]*0.34,0.30)),
                         center + nvec*0.10 + Vector((t[0]*0.34,t[1]*0.34,0.82)),
                         center + nvec*0.10 + Vector((-t[0]*0.34,-t[1]*0.34,0.82)),
                        ], [(0,0),(1,0),(1,1),(0,1)])
        trim.box(center + nvec*0.085 + Vector((-t[0]*(door_width/2+0.12),-t[1]*(door_width/2+0.12),0)),
                 t, outn, 0.18, 0.28, door_height+0.18)
        trim.box(center + nvec*0.085 + Vector((t[0]*(door_width/2+0.12),t[1]*(door_width/2+0.12),0)),
                 t, outn, 0.18, 0.28, door_height+0.18)
        trim.box(center + nvec*0.085 + Vector((0,0,door_height/2+0.11)), t, outn,
                 door_width+0.42, 0.28, 0.20)
        hardware.box(center + nvec*0.11 + Vector((t[0]*door_width*0.27,t[1]*door_width*0.27,0)),
                      t, outn, 0.05, 0.12, 0.1)
        # Stone approach stairs, projecting outward from the door.
        for k in range(4):
            width = 2.65
            depth = 0.38
            rise = door_base / 4.0
            out_distance = 0.20 + k * 0.38
            zbase = door_base - (k + 1) * rise
            wallbase = Vector((A[0] + t[0]*door_u, A[1] + t[1]*door_u, 0))
            c = wallbase + nvec*out_distance + Vector((0,0,zbase+rise/2))
            steps.box(c, t, outn, width, depth, rise)

    # Continuous light limestone cap reflects the window surrounds and facade bands.
    for i, A in enumerate(poly):
        B = poly[(i + 1) % n]
        dx, dy = B[0] - A[0], B[1] - A[1]
        length = math.hypot(dx, dy)
        if length < 0.5: continue
        t = (dx / length, dy / length)
        outn = (outward_sign * dy / length, outward_sign * -dx / length)
        trim.box(((A[0]+B[0])*0.5+outn[0]*0.07,
                  (A[1]+B[1])*0.5+outn[1]*0.07,
                  upper_wall + 0.01), t, outn, length + 0.10, 0.23, 0.18)

    # A clipped inset roof ring gives the U-shaped plan a low, complex hip roof.
    # The ring direction, hip rise, and pitches are estimated; the aerial shows
    # intersecting gray roof planes but no reliable dimensional roof survey.
    offset_distance = 2.0
    inset = inward_offset(poly, offset_distance)
    def ring_sane(candidate):
        if abs(polygon_area(candidate)) < 3.0: return False
        return all(point_in_polygon(p, poly) for p in candidate)
    if not ring_sane(inset):
        for d in (1.5, 1.0, 0.5, 0.25):
            inset = inward_offset(poly, d)
            if ring_sane(inset):
                offset_distance = d
                break
        else:
            raise RuntimeError("Could not create a safe inset hip-roof ring")
    roof_eave = WALL_EAVE_M + 0.16
    roof_ridge = MODEL_HEIGHT_M
    # Outer eaves to inner hip ridge. Separate per-edge facets retain crisp roof hips.
    for i, a in enumerate(poly):
        b = poly[(i + 1) % n]
        c = inset[(i + 1) % n]
        d = inset[i]
        points = [(a[0], a[1], roof_eave), (b[0], b[1], roof_eave),
                  (c[0], c[1], roof_ridge), (d[0], d[1], roof_ridge)]
        uvs = [(0,0),(math.dist(a,b),0),(math.dist(a,b),2.5),(0,2.5)]
        if signed_area < 0:
            points.reverse()
            uvs.reverse()
        roof.face(points, uvs)
    # Inner polygon top cap. Mesh n-gon triangulation is handled by Blender.
    cap = [(x, y, roof_ridge) for x, y in inset]
    cap_uvs = [(x, y) for x, y in inset]
    if signed_area < 0:
        cap.reverse()
        cap_uvs.reverse()
    roof.face(cap, cap_uvs)

    # Build all accumulated geometry into the stable asset collection.
    created = []
    for acc in (walls, foundation_mesh, trim, glass_mesh, frames, door,
                hardware, roof, signage, signpanel, steps):
        if acc.faces:
            created.append(acc.mesh_object(collection))

    # Freestanding low monument sign: its brick piers and light face are visible
    # in the official 2023 chapter photograph. Exact offset within the lawn is
    # inferred from the photo and aerial, not measured from GIS.
    if door_info:
        A, t, outn, door_u, _ = door_info
        tvec = Vector((t[0], t[1], 0))
        nvec = Vector((outn[0], outn[1], 0))
        door_mid = Vector((A[0] + t[0]*door_u, A[1] + t[1]*door_u, 0))
        sign_center = door_mid + tvec*5.0 + nvec*4.2 + Vector((0,0,0.73))
        # Low brick piers, header, and an inset light stone name field.
        signage.box(sign_center + tvec*(-0.92), t, outn, 0.34, 0.40, 1.18)
        signage.box(sign_center + tvec*(0.92), t, outn, 0.34, 0.40, 1.18)
        signage.box(sign_center + Vector((0,0,0.52)), t, outn, 2.12, 0.38, 0.18)
        signpanel.box(sign_center, t, outn, 1.66, 0.16, 0.82)
        # Text is a face-on, shallow 3D extrusion. Local X follows the sign's
        # left-to-right axis, local Y is vertical, and local Z points outward.
        from mathutils import Matrix
        xaxis = -tvec
        yaxis = Vector((0,0,1))
        zaxis = nvec
        orient = Matrix(((xaxis.x, yaxis.x, zaxis.x),
                         (xaxis.y, yaxis.y, zaxis.y),
                         (xaxis.z, yaxis.z, zaxis.z))).to_4x4()
        for body, size, zoff, lettermat, name in (
            ("ΔΥ", 0.25, 0.23, sign_blue, "DU_Sign_Greek_Letters"),
            ("Delta Upsilon", 0.19, -0.02, sign_blue, "DU_Sign_Chapter_Name"),
            ("Established 1914", 0.12, -0.25, sign_blue, "DU_Sign_Founding_Date"),
        ):
            curve = bpy.data.curves.new(name + "_Curve", type="FONT")
            curve.body = body
            curve.size = size
            curve.extrude = 0.002
            curve.align_x = "CENTER"
            curve.align_y = "CENTER"
            text_obj = bpy.data.objects.new(name, curve)
            collection.objects.link(text_obj)
            text_obj.location = sign_center + nvec*0.095 + Vector((0,0,zoff))
            text_obj.rotation_euler = orient.to_euler()
            text_obj.data.materials.append(lettermat)
        # The sign boxes were accumulated after the main geometry pass above.
        signage.mesh_object(collection)
        signpanel.mesh_object(collection)
    # Preserve the stable original object and collection name.
    wall_obj = bpy.data.objects.get(BASE_OBJECT_NAME)
    if wall_obj is None:
        raise RuntimeError("Stable primary building object was not created")
    wall_obj.name = BASE_OBJECT_NAME
    wall_obj["asset_id"] = ASSET_ID
    wall_obj["verified_footprint"] = "Purdue GIS BuildingShapesZip4 FID 751"
    wall_obj["height_status"] = "estimated; source GIS extrusion field 38 presumed feet"

    # Asset collection remains identity transform and is now local to GIS centroid.
    collection.instance_offset = (0, 0, 0)
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = 100
    scene.camera = None

    # Temporary camera, lighting, and neutral ground are outside the library
    # collection and are deleted before save; preview is saved in the audit folder.
    temp = bpy.data.collections.new("_DU_Render_Temporary")
    scene.collection.children.link(temp)
    cam_data = bpy.data.cameras.new("_DU_Preview_Camera")
    cam = bpy.data.objects.new("_DU_Preview_Camera", cam_data)
    temp.objects.link(cam)
    scene.camera = cam
    target = Vector((0, -0.4, 5.0))
    cam.location = (0, -53, 22)
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 32
    cam.data.dof.use_dof = False
    sun_data = bpy.data.lights.new("_DU_Preview_Sun", type="SUN")
    sun = bpy.data.objects.new("_DU_Preview_Sun", sun_data)
    temp.objects.link(sun)
    sun.rotation_euler = (math.radians(24), math.radians(-20), math.radians(-30))
    sun.data.energy = 0.60
    sun_data.angle = math.radians(18)
    area_data = bpy.data.lights.new("_DU_Preview_Fill", type="AREA")
    area = bpy.data.objects.new("_DU_Preview_Fill", area_data)
    temp.objects.link(area)
    area.location = (15, -22, 16)
    area.data.energy = 260
    area.data.shape = "DISK"
    area.data.size = 14
    area.rotation_euler = (target - area.location).to_track_quat("-Z", "Y").to_euler()
    ground_mat = make_material("_DU_Preview_Ground", (0.12, 0.16, 0.08), roughness=0.95)
    ground_mesh = bpy.data.meshes.new("_DU_Preview_GroundMesh")
    s = 60
    ground_mesh.from_pydata([(-s,-s,-0.08),(s,-s,-0.08),(s,s,-0.08),(-s,s,-0.08)], [], [(0,1,2,3)])
    ground_mesh.materials.append(ground_mat)
    ground_obj = bpy.data.objects.new("_DU_Preview_Ground", ground_mesh)
    temp.objects.link(ground_obj)
    scene.world.color = (0.52, 0.58, 0.68)
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.65
    scene.render.filepath = str(AUDIT / "delta_upsilon_preview.png")
    bpy.ops.render.render(write_still=True)

    if door_info:
        # Detail frame makes the documented chapter sign and entry legible.
        entry_target = sign_center + Vector((0, 0, 2.2))
        cam.location = sign_center + nvec*22 + Vector((0, 0, 8.0))
        cam.rotation_euler = (entry_target - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = 55
        scene.render.filepath = str(AUDIT / "delta_upsilon_entry_preview.png")
        bpy.ops.render.render(write_still=True)

    # Remove all temporary preview-only objects/materials, restore asset-only scene.
    scene.camera = None
    for obj in list(temp.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(temp)
    if ground_mat.users == 0:
        bpy.data.materials.remove(ground_mat)
    scene.render.filepath = "//"
    # ensure no loose unrelated objects are left in the expected asset scene.
    for obj in list(scene.objects):
        if obj.name not in [o.name for o in collection.objects]:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.camera = None
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    bounds = [
        [min(v[0] for v in poly), max(v[0] for v in poly)],
        [min(v[1] for v in poly), max(v[1] for v in poly)],
        [0.0, MODEL_HEIGHT_M],
    ]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    asset_points = []
    for obj in collection.objects:
        if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            asset_points.extend(tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    collection_bounds = [
        [min(p[axis] for p in asset_points), max(p[axis] for p in asset_points)]
        for axis in range(3)
    ] if asset_points else None
    footprint_area = abs(polygon_area(poly))
    footprint_perimeter = sum(math.dist(poly[i], poly[(i+1) % len(poly)])
                              for i in range(len(poly)))
    report = {
        "asset_id": ASSET_ID,
        "feature": "Purdue BuildingShapesZip4 FID 751 / Delta Upsilon / 1300 Stadium",
        "asset_file": str(ASSET_PATH.relative_to(ROOT)),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "coordinate_status": "local project meters; subtract official polygon centroid; parent master Placement marker is required",
        "local_origin_project_xy_m": [round(origin[0], 6), round(origin[1], 6)],
        "footprint_bounds_local_m": [[round(v, 4) for v in axis] for axis in bounds],
        "all_asset_geometry_bounds_local_m": [[round(v, 4) for v in axis] for axis in collection_bounds],
        "footprint_area_local_project_m2": round(footprint_area, 4),
        "footprint_perimeter_local_project_m": round(footprint_perimeter, 4),
        "official_gis_feature_area_field": props.get("Shape__Area"),
        "official_gis_feature_perimeter_field": props.get("Shape__Length"),
        "height": "11.58 m estimated from GIS Extrution=38 assumed feet; facade rows/roof pitch estimated",
        "interior": "not modeled; no reliable floor-plan evidence located",
        "façade_evidence": "official 2023 chapter photo: red brick, repeated blue sash windows, light stone surrounds/bands, freestanding chapter sign; geometry inferred where obscured",
        "roof_evidence": "Google Maps aerial imagery inspected 2026-10-26; low, complex gray roof; exact roof form and image acquisition date unavailable",
        "window_count": len(all_window_positions),
        "object_count": len(collection.objects),
        "material_count": len({m.name for o in collection.objects
                                for m in getattr(o.data, "materials", []) if m}),
        "roof_inset_offset_m": offset_distance,
    }
    (AUDIT / "build_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("DU_BUILD_REPORT", json.dumps(report, sort_keys=True))


main()
