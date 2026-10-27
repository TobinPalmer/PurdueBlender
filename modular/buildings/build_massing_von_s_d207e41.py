"""Build the Von's Shops library from the verified OSM footprint and public photos.

Run from the project root with Blender 5.x, opening the existing assigned asset:
    blender -b modular/buildings/massing_von_s_d207e41.blend --python this_file.py

Only facade details supported by the source evidence are modeled. The flat roof,
upper apartment windows, floor heights, and exact openings are schematic estimates;
no interior is modeled because no public floor plan was found.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_von_s_d207e41"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / "von_s"
FOOTPRINT_PATH = EVIDENCE / "sources" / "osm_way_116427236_footprint.json"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
OBJECT_NAME = "Von's"

Z_GROUND = 0.0
Z_STORE_TOP = 4.05
Z_APARTMENT_TOP = 7.65
Z_PARAPET_TOP = 8.45


def material(name, base, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*base, 1.0)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def brick_material():
    mat = material("VonS_Warm_Red_Brick", (0.42, 0.16, 0.095), 0.88)
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    uv_map = nt.nodes.new("ShaderNodeUVMap")
    uv_map.uv_map = "Facade_Meters"
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value = (0.36, 0.105, 0.065, 1)
    brick.inputs["Color2"].default_value = (0.57, 0.25, 0.15, 1)
    brick.inputs["Mortar"].default_value = (0.24, 0.22, 0.19, 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = 0.48
    brick.inputs["Row Height"].default_value = 0.22
    brick.inputs["Mortar Size"].default_value = 0.018
    brick.inputs["Mortar Smooth"].default_value = 0.02
    nt.links.new(uv_map.outputs["UV"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.2
    bump.inputs["Distance"].default_value = 0.025
    nt.links.new(brick.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


MATS = {
    "brick": brick_material(),
    "brick_dark": material("VonS_Dark_Brick", (0.27, 0.085, 0.055), 0.9),
    "stone": material("VonS_Limestone_Trim", (0.63, 0.59, 0.51), 0.8),
    "roof": material("VonS_Flat_Roof_Membrane", (0.19, 0.20, 0.19), 0.94),
    "glass": material("VonS_Storefront_Glass", (0.025, 0.075, 0.095), 0.2, 0.15),
    "upper_glass": material("VonS_Apartment_Glass", (0.045, 0.12, 0.16), 0.25, 0.05),
    "frame": material("VonS_Painted_Window_Frame", (0.73, 0.70, 0.62), 0.5, 0.15),
    "metal": material("VonS_Dark_Metal", (0.12, 0.13, 0.13), 0.38, 0.65),
    "sign_pale": material("VonS_Sign_Cream", (0.87, 0.79, 0.62), 0.82),
    "sign_green": material("VonS_Sign_Green", (0.47, 0.64, 0.40), 0.85),
    "sign_pink": material("VonS_Sign_Dusty_Pink", (0.76, 0.45, 0.49), 0.85),
    "sign_lavender": material("VonS_Sign_Lavender", (0.56, 0.48, 0.68), 0.85),
    "sign_ink": material("VonS_Sign_Dark_Ink", (0.16, 0.13, 0.13), 0.82),
}


def get_ring():
    data = json.loads(FOOTPRINT_PATH.read_text(encoding="utf-8"))
    return [tuple(p) for p in data["projected_ring_m"][:-1]], data


def mesh_object(name, verts, faces, mat, collection):
    me = bpy.data.meshes.new(name + "_Mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    me.materials.append(mat)
    return ob


def prism(name, ring, z0, z1, mat, collection):
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    faces.extend([tuple(range(n, 2 * n)), tuple(reversed(range(n)))])
    ob = mesh_object(name, verts, faces, mat, collection)
    if "Brick" in mat.name:
        uv = ob.data.uv_layers.new(name="Facade_Meters")
        lengths = [math.dist(ring[i], ring[(i + 1) % n]) for i in range(n)]
        cumulative = [0.0]
        for length in lengths[:-1]:
            cumulative.append(cumulative[-1] + length)
        for poly in ob.data.polygons[:n]:
            i = poly.index
            for li in poly.loop_indices:
                vi = ob.data.loops[li].vertex_index
                right = (i + 1) % n
                u = cumulative[i] + (lengths[i] if vi in (right, n + right) else 0.0)
                v = z1 if vi >= n else z0
                uv.data[li].uv = (u, v)
        for poly in ob.data.polygons[n:]:
            for li in poly.loop_indices:
                vi = ob.data.loops[li].vertex_index
                uv.data[li].uv = (verts[vi][0], verts[vi][1])
    return ob


BOX_FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


def oriented_box(name, center, tangent, normal, width, height, depth, mat, collection):
    t = Vector((tangent[0], tangent[1], 0)).normalized()
    n = Vector((normal[0], normal[1], 0)).normalized()
    z = Vector((0, 0, 1))
    c = Vector(center)
    verts = []
    for zz in (-height / 2, height / 2):
        for dd in (-depth / 2, depth / 2):
            for uu in (-width / 2, width / 2):
                p = c + t * uu + n * dd + z * zz
                verts.append(tuple(p))
    return mesh_object(name, verts, BOX_FACES, mat, collection)


def wall_edge(a, b):
    d = Vector((b[0] - a[0], b[1] - a[1]))
    length = d.length
    t = d.normalized()
    # The source rings are counterclockwise in the project coordinate frame.
    n = Vector((t.y, -t.x))
    return length, (t.x, t.y), (n.x, n.y)


def edge_point(a, tangent, distance):
    return (a[0] + tangent[0] * distance, a[1] + tangent[1] * distance)


def add_window(edge, center_distance, bottom, width, height, collection, material_name, frame=True):
    a, b = edge
    length, tangent, normal = wall_edge(a, b)
    if center_distance - width / 2 < 0.7 or center_distance + width / 2 > length - 0.7:
        return
    x, y = edge_point(a, tangent, center_distance)
    # glass is just inside the wall plane; trim projects a little outside
    center = (x + normal[0] * 0.13, y + normal[1] * 0.13, bottom + height / 2)
    oriented_box("VonS_Window_Glass", center, tangent, normal, width - 0.12, height - 0.12, 0.06,
                 MATS[material_name], collection)
    if frame:
        trim = 0.105
        for offset in (-width / 2, width / 2):
            px, py = edge_point((x, y), tangent, offset)
            oriented_box("VonS_Window_Jamb", (px, py, bottom + height / 2), tangent, normal,
                         trim, height + 0.05, 0.16, MATS["frame"], collection)
        for z in (bottom, bottom + height):
            oriented_box("VonS_Window_HeadSill", (x, y, z), tangent, normal,
                         width + 0.12, trim, 0.16, MATS["frame"], collection)
        oriented_box("VonS_Window_Mullion", (x, y, bottom + height / 2), tangent, normal,
                     0.065, height, 0.17, MATS["frame"], collection)


def add_door(edge, center_distance, bottom, width, height, collection):
    add_window(edge, center_distance, bottom, width, height, collection, "glass", False)
    a, b = edge
    _, tangent, normal = wall_edge(a, b)
    x, y = edge_point(a, tangent, center_distance)
    oriented_box("VonS_Entry_Door_Frame", (x, y, bottom + height / 2), tangent, normal,
                 width + 0.16, height + 0.14, 0.18, MATS["frame"], collection)
    oriented_box("VonS_Entry_Door_Glass", (x + normal[0] * 0.15, y + normal[1] * 0.15, bottom + height / 2),
                 tangent, normal, width - 0.18, height - 0.2, 0.06, MATS["glass"], collection)
    # horizontal transom and metal pull
    oriented_box("VonS_Door_Transom", (x, y, bottom + height - 0.45), tangent, normal,
                 width - 0.15, 0.09, 0.14, MATS["metal"], collection)


def add_text(name, body, location, tangent, normal, size, mat, collection, align="CENTER"):
    curve = bpy.data.curves.new(name + "_Curve", type="FONT")
    curve.body = body
    curve.size = size
    curve.align_x = align
    curve.extrude = 0.008
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    # Local text X runs along the wall; local Y is vertical; local Z faces out.
    t = Vector((tangent[0], tangent[1], 0)).normalized()
    n = Vector((normal[0], normal[1], 0)).normalized()
    up = Vector((0, 0, 1))
    rot = Matrix(((t.x, up.x, n.x), (t.y, up.y, n.y), (t.z, up.z, n.z))).to_quaternion()
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = rot
    obj.data.materials.append(mat)
    # convert text to mesh so the delivered file contains no font dependency
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.select_set(False)
    return obj


def cleanup_old_geometry(collection, root):
    for ob in list(collection.objects):
        if ob != root:
            bpy.data.objects.remove(ob, do_unlink=True)
    if root.data:
        old = root.data
        root.data = bpy.data.meshes.new("VonS_Combined_Mesh")
        if old.users == 0:
            bpy.data.meshes.remove(old)
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    root.scale = (1, 1, 1)


def add_sign(edge, start_distance, width, collection):
    a, b = edge
    _, tangent, normal = wall_edge(a, b)
    cx, cy = edge_point(a, tangent, start_distance + width / 2)
    # painted category bars with dark lettering replicate the photographed mural;
    # this is a set of simple wall-mounted paint bands, not a projecting sign.
    zbase = 4.25
    bar_h = 0.31
    bar_w = width
    for i, (word, key) in enumerate([
        ("T-SHIRTS  •  COMICS", "sign_green"), ("BEADS  •  JEWELRY", "sign_lavender"),
        ("GIFTS  •  CARDS", "sign_pink"), ("RECORDS", "sign_pale"),
        ("BOOKS", "sign_green")]):
        z = zbase + i * (bar_h + 0.035)
        x, y = edge_point((cx, cy), normal, 0.075)
        oriented_box("VonS_Painted_Mural_Band", (x, y, z + bar_h / 2), tangent, normal,
                     bar_w, bar_h, 0.03, MATS[key], collection)
        text_x, text_y = edge_point((cx, cy), normal, 0.125)
        add_text("VonS_Mural_Category", word, (text_x, text_y, z + 0.055), tangent, normal,
                 0.2, MATS["sign_ink"], collection)
    x, y = edge_point((cx, cy), normal, 0.125)
    add_text("VonS_Mural_Name", "VON'S SHOPS", (x, y, zbase + 5 * (bar_h + 0.035)),
             tangent, normal, 0.54, MATS["sign_pale"], collection)


def configure_render(scene, root, evidence):
    engines = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else engines[0]
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.resolution_percentage = 100
    world = scene.world or bpy.data.worlds.new("VonS_Preview_World")
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.34, 0.43, 0.54, 1)
    bg.inputs["Strength"].default_value = 0.35

    temp = bpy.data.collections.new("_VonS_Preview_Temporary")
    scene.collection.children.link(temp)
    def area_light(name, loc, energy, size):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        ob = bpy.data.objects.new(name, data)
        temp.objects.link(ob)
        ob.location = loc
        direction = Vector((411.5, -402.0, 3.7)) - ob.location
        ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    area_light("VonS_Key_Light", (445, -365, 44), 2300, 34)
    area_light("VonS_Fill_Light", (378, -390, 28), 900, 28)

    def camera(name, location, target, ortho_scale, path):
        data = bpy.data.cameras.new(name)
        data.type = "ORTHO"
        data.ortho_scale = ortho_scale
        cam = bpy.data.objects.new(name, data)
        temp.objects.link(cam)
        cam.location = location
        direction = Vector(target) - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.camera = cam
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        return cam

    previews = evidence / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    camera("VonS_ThreeQuarter_Preview_Camera", (372, -362, 21), (411.7, -402.8, 4.0), 59,
           previews / "von_s_three_quarter.png")
    camera("VonS_StateStreet_Facade_Preview_Camera", (412.0, -363.5, 9.2), (412.0, -400.0, 4.8), 46,
           previews / "von_s_state_street_facade.png")
    camera("VonS_Mural_Detail_Preview_Camera", (373.0, -399.5, 5.8), (390.0, -399.5, 5.8), 19,
           previews / "von_s_mural_detail.png")
    camera("VonS_Roof_Footprint_Preview_Camera", (411.8, -403.2, 52), (411.8, -403.2, 4), 52,
           previews / "von_s_roof_footprint.png")
    scene.camera = None
    for ob in list(temp.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(temp)


def main():
    scene = bpy.data.scenes.get(SCENE_NAME)
    collection = bpy.data.collections.get(COLLECTION_NAME)
    root = bpy.data.objects.get(OBJECT_NAME)
    if scene is None or collection is None or root is None:
        raise RuntimeError("Assigned scene, collection, or stable root object is missing")
    ring, footprint = get_ring()
    cleanup_old_geometry(collection, root)

    # Rebuild the exact GIS plan outline as a simple mixed-use commercial shell.
    # The slab and parapet follow the whole source polygon, while upper openings,
    # signs, and roof details remain clearly documented schematic interpretations.
    shell = prism("VonS_Main_Brick_Shell", ring, Z_GROUND, Z_APARTMENT_TOP, MATS["brick"], collection)
    roof = prism("VonS_Roof_Cap", ring, Z_APARTMENT_TOP, Z_APARTMENT_TOP + 0.18, MATS["roof"], collection)
    # Thin perimeter parapet leaves the flat roof membrane visible from above.
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        length, tangent, normal = wall_edge(a, b)
        center_xy = edge_point(a, tangent, length / 2)
        oriented_box("VonS_Parapet_Wall",
                     (center_xy[0], center_xy[1], (Z_APARTMENT_TOP + 0.18 + Z_PARAPET_TOP) / 2),
                     tangent, normal, length + 0.08, Z_PARAPET_TOP - Z_APARTMENT_TOP - 0.18,
                     0.28, MATS["brick_dark"], collection)
    # Street-level masonry plinth band; window and door bays are layered onto it.
    plinth = prism("VonS_Stone_Base", ring, Z_GROUND, 0.38, MATS["stone"], collection)

    # Inspect the real ring for the long north-facing State Street wall and the
    # adjoining east-facing corner facade. Edge IDs are found by direction rather
    # than hard-coded, so the source ring remains the authority.
    edges = []
    for i, a in enumerate(ring):
        b = ring[(i + 1) % len(ring)]
        length, tangent, normal = wall_edge(a, b)
        edges.append((i, (a, b), length, tangent, normal))
    front = max((e for e in edges if e[4][1] > 0.86), key=lambda e: e[2])
    side = max((e for e in edges if e[4][0] > 0.86), key=lambda e: e[2])
    west = max((e for e in edges if e[4][0] < -0.86), key=lambda e: e[2])

    # Main State Street display windows and entry door. Ground floor shop uses are
    # separated by masonry piers; interior remains unmodeled without plan evidence.
    front_len = front[2]
    front_edge = front[1]
    store_centers = [front_len * t for t in (0.15, 0.33, 0.52, 0.70, 0.87)]
    for idx, c in enumerate(store_centers):
        if idx == 2:
            add_door(front_edge, c, 0.48, 1.45, 3.0, collection)
        else:
            add_window(front_edge, c, 0.68, 3.6, 2.6, collection, "glass")
        # a thin sill stone below every shop bay
        ln, tang, norm = wall_edge(*front_edge)
        px, py = edge_point(front_edge[0], tang, c)
        oriented_box("VonS_Storefront_Sill", (px, py, 0.57), tang, norm, 3.82, 0.12, 0.22,
                     MATS["stone"], collection)

    # Long front wall has a distinctive hand-painted category mural above the shop.
    # Keep it to a compact panel so it does not claim a full-wall graphic unsupported
    # by the official photograph.
    # The official photo shows a painted stacked-category mural on brick. Use the
    # west end wall to keep the State Street apartment-window rhythm unobscured.
    add_sign(west[1], west[2] * 0.20, min(10.5, west[2] * 0.54), collection)

    # Apartment-level window rhythm on State Street and the long corner elevation.
    for frac in (0.18, 0.31, 0.44, 0.58, 0.72, 0.86):
        add_window(front_edge, front_len * frac, 4.72, 1.55, 1.62, collection, "upper_glass")
    for frac in (0.20, 0.38, 0.56, 0.74, 0.90):
        add_window(side[1], side[2] * frac, 4.72, 1.4, 1.55, collection, "upper_glass")

    # A small wall A/C unit is visible in the storefront reference photograph.
    ln, tang, norm = wall_edge(*front_edge)
    px, py = edge_point(front_edge[0], tang, front_len * 0.94)
    oriented_box("VonS_Window_AC_Cabinet", (px, py, 6.05), tang, norm,
                 0.72, 0.48, 0.38, MATS["metal"], collection)
    for dx in (-0.18, -0.09, 0.0, 0.09, 0.18):
        xx, yy = edge_point((px, py), tang, dx)
        oriented_box("VonS_AC_Grille", (xx + norm[0] * 0.20, yy + norm[1] * 0.20, 6.05),
                     tang, norm, 0.025, 0.37, 0.015, MATS["frame"], collection)

    # Build one joined mesh to retain the stable manifest object name and simple
    # massing asset's expected object count while giving all components materials.
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    for ob in list(collection.objects):
        if ob != root and ob.type == "MESH":
            ob.select_set(True)
        elif ob != root and ob.type != "MESH":
            bpy.data.objects.remove(ob, do_unlink=True)
    bpy.ops.object.join()
    root.name = OBJECT_NAME
    root.data.name = "VonS_Detailed_Combined_Mesh"
    if root.data.uv_layers.get("Facade_Meters"):
        root.data.uv_layers.active = root.data.uv_layers.get("Facade_Meters")
    for idx in range(len(root.data.materials) - 1, -1, -1):
        if root.data.materials[idx] is None:
            root.data.materials.pop(index=idx)
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    root.scale = (1, 1, 1)
    root["asset_id"] = ASSET_ID
    root["footprint_source"] = "OpenStreetMap way 116427236; exact transformed polygon in audit/von_s/sources"
    root["height_status"] = "estimated 8.45 m; no surveyed elevation source found"
    root["interior_status"] = "not modeled; no public floor plan found"
    root["facade_status"] = "red brick and painted Von's Shops category mural verified by official photo; openings schematic"

    # Temporary render rig is removed before saving the reusable asset.
    configure_render(scene, root, EVIDENCE)
    scene.render.filepath = "//"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    print(json.dumps({
        "asset": str(ASSET_PATH), "asset_id": ASSET_ID,
        "scene": scene.name, "collection": collection.name, "object": root.name,
        "objects_in_scene": len(scene.objects), "vertices": len(root.data.vertices),
        "faces": len(root.data.polygons), "materials": [m.name for m in root.data.materials],
        "world_bounds_m": [[min(v.co.x for v in root.data.vertices), max(v.co.x for v in root.data.vertices)],
                            [min(v.co.y for v in root.data.vertices), max(v.co.y for v in root.data.vertices)],
                            [min(v.co.z for v in root.data.vertices), max(v.co.z for v in root.data.vertices)]],
        "height_m": Z_PARAPET_TOP
    }, indent=2))


if __name__ == "__main__":
    main()
