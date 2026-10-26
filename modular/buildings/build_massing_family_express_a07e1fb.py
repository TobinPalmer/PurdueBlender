"""Build the Family Express at 1812 Northwestern Ave as a portable Blender library.

Coordinates are campus meters and the building wall footprint is the OpenStreetMap
way 374563309 outline, transformed with the project's documented local approximation.
The gas canopy and store styling use the location-matched MapQuest photo as reference.
"""

import bpy
import json
import math
import os
import hashlib
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSET_ID = "massing_family_express_a07e1fb"
ASSET_COLLECTION = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
OUT_BLEND = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
EVIDENCE_DIR = os.path.join(ROOT, "audit", "family_express")
SOURCE_DIR = os.path.join(EVIDENCE_DIR, "sources")

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LON_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
LAT_M = 111040.0

# OpenStreetMap way 374563309 (ordered ring, without closure point), recorded in
# audit/family_express/sources/osm_way_374563309_2026-10-26.json.
RING_LATLON = [
    (40.4454801, -86.9205025),
    (40.4453665, -86.9204138),
    (40.4453749, -86.9203953),
    (40.4453458, -86.9203725),
    (40.4454175, -86.9202139),
    (40.4455910, -86.9203495),
    (40.4455588, -86.9204206),
    (40.4455159, -86.9205154),
    (40.4454851, -86.9204913),
]
RING = [((lon - ORIGIN_LON) * LON_M, (lat - ORIGIN_LAT) * LAT_M) for lat, lon in RING_LATLON]


def link(a, b):
    a.links.new(a, b)


def new_material(name, color, roughness=0.72, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def brick_material():
    mat = new_material("FEXP warm red-brown brick", (0.36, 0.115, 0.075), 0.82)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    tc = nodes.new("ShaderNodeTexCoord")
    brick = nodes.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value = (0.46, 0.19, 0.12, 1)
    brick.inputs["Color2"].default_value = (0.27, 0.075, 0.048, 1)
    brick.inputs["Mortar"].default_value = (0.56, 0.47, 0.40, 1)
    # The shell has real-meter UVs (U along each wall, V vertical), so the
    # default brick width and row height land near realistic masonry dimensions.
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.018
    brick.inputs["Mortar Smooth"].default_value = 0.012
    brick.inputs["Brick Width"].default_value = 0.5
    brick.inputs["Row Height"].default_value = 0.25
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 2.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.035
    links.new(tc.outputs["UV"], brick.inputs["Vector"])
    links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tc.outputs["UV"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def roof_material():
    mat = new_material("FEXP charcoal gray roof shingles", (0.12, 0.15, 0.17), 0.9)
    n, l = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(x for x in n if x.type == "BSDF_PRINCIPLED")
    tc = n.new("ShaderNodeTexCoord")
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 65.0
    noise.inputs["Detail"].default_value = 2.0
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (0.045, 0.06, 0.07, 1)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (0.24, 0.28, 0.30, 1)
    l.new(tc.outputs["Object"], noise.inputs["Vector"])
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def set_mat(obj, mat):
    obj.data.materials.append(mat)


def mesh_obj(name, verts, faces, mat, collection, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def box(name, center, size, mat, collection, tangent=None, normal=None, bevel=0.025):
    """Box in world XY, optionally oriented with x=tangent and y=normal."""
    cx, cy, cz = center
    sx, sy, sz = size
    if tangent is None:
        tangent = Vector((1.0, 0.0))
    else:
        tangent = Vector(tangent).normalized()
    if normal is None:
        normal = Vector((-tangent.y, tangent.x))
    else:
        normal = Vector(normal).normalized()
    verts = []
    for zsign in (-1, 1):
        for ysign in (-1, 1):
            for xsign in (-1, 1):
                p = Vector((cx, cy)) + tangent * (xsign * sx / 2) + normal * (ysign * sy / 2)
                verts.append((p.x, p.y, cz + zsign * sz / 2))
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    obj = mesh_obj(name, verts, faces, mat, collection)
    if bevel:
        mod = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod2 = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def cylinder(name, loc, radius, depth, mat, collection, vertices=16, axis=(0, 0, 1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    # Move Blender's newly-created object into the assigned library collection.
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if axis != (0, 0, 1):
        obj.rotation_euler = Vector(axis).to_track_quat("Z", "Y").to_euler()
    set_mat(obj, mat)
    return obj


def oriented_text(name, body, center, tangent, normal, size, mat, collection, extrude=0.012):
    curve = bpy.data.curves.new(name + "Curve", "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = extrude
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = (center[0] + normal[0] * 0.14, center[1] + normal[1] * 0.14, center[2])
    quat = Vector((normal[0], normal[1], 0.0)).to_track_quat("Z", "Y")
    obj.rotation_euler = quat.to_euler()
    set_mat(obj, mat)
    return obj


def add_window(name, a, b, z_center, width_fraction, height, wall_offset, collection, glass, trim, mullion):
    edge = Vector((b[0] - a[0], b[1] - a[1]))
    length = edge.length
    tangent = edge.normalized()
    # Ring is counter-clockwise, so outward is the right-hand normal.
    outward = Vector((tangent.y, -tangent.x))
    width = length * width_fraction
    midpoint = (Vector(a) + Vector(b)) * 0.5 + outward * wall_offset
    box(name + " glazing", (midpoint.x, midpoint.y, z_center), (width, 0.09, height), glass, collection, tangent, outward, 0.0)
    for x in (-width / 2, width / 2):
        p = midpoint + tangent * x
        box(name + " side frame", (p.x, p.y, z_center), (0.12, 0.16, height + 0.12), trim, collection, tangent, outward, 0.012)
    for z in (-height / 2, height / 2):
        box(name + " sill or lintel", (midpoint.x, midpoint.y, z_center + z), (width + 0.16, 0.16, 0.12), trim, collection, tangent, outward, 0.015)
    box(name + " center mullion", (midpoint.x, midpoint.y, z_center), (0.065, 0.16, height), mullion, collection, tangent, outward, 0.006)


def build_asset():
    # Reset the file so repeated script runs produce identical output.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 820
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("FEXP neutral daylight preview")
    scene.world.color = (0.2, 0.2, 0.2)
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = os.path.join(EVIDENCE_DIR, "exterior_preview.png")

    root = bpy.data.collections.new(ASSET_COLLECTION)
    scene.collection.children.link(root)
    preview = bpy.data.collections.new("Preview_only_context_exclude_from_master")
    scene.collection.children.link(preview)
    # Materials: the red-brown brick, graphite shingles, pale mortar and white trim
    # are grounded in the location-specific retail photograph.
    brick = brick_material()
    roof = roof_material()
    cream = new_material("FEXP warm white trim", (0.78, 0.75, 0.67), 0.7)
    white = new_material("FEXP canopy white coated metal", (0.87, 0.91, 0.91), 0.35, 0.12)
    blue = new_material("Family Express cyan blue", (0.035, 0.55, 0.78), 0.38, 0.1)
    blue_light = new_material("Family Express light blue stripes", (0.24, 0.72, 0.86), 0.4)
    red = new_material("Family Express logo red", (0.78, 0.06, 0.11), 0.42)
    dark = new_material("FEXP black structural steel", (0.035, 0.045, 0.05), 0.36, 0.45)
    glass = new_material("FEXP reflective storefront glass", (0.075, 0.22, 0.28), 0.18, 0.25)
    glass_bsdf = next(n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    glass_bsdf.inputs["Transmission Weight"].default_value = 0.22
    glass_bsdf.inputs["Alpha"].default_value = 0.34
    try:
        glass.surface_render_method = "DITHERED"
    except (AttributeError, TypeError):
        pass
    wood = new_material("FEXP warm interior finish", (0.42, 0.25, 0.13), 0.68)
    tile = new_material("FEXP interior tile", (0.50, 0.46, 0.38), 0.65)
    yellow = new_material("FEXP safety bollard yellow", (0.95, 0.55, 0.03), 0.4)
    display = new_material("FEXP illuminated digital display", (0.04, 0.17, 0.15), 0.3)
    pump_white = new_material("FEXP pump porcelain white", (0.86, 0.86, 0.82), 0.35, 0.08)
    asphalt = new_material("FEXP forecourt concrete", (0.34, 0.35, 0.35), 0.9)
    shelving = new_material("FEXP shelving gray", (0.30, 0.32, 0.32), 0.6, 0.15)
    package_mats = [
        new_material("Retail package cream", (0.83, 0.65, 0.18), 0.5),
        new_material("Retail package red", (0.67, 0.08, 0.05), 0.5),
        new_material("Retail package blue", (0.08, 0.34, 0.62), 0.5),
        new_material("Retail package green", (0.13, 0.48, 0.21), 0.5),
    ]

    # Primary footprint and wall shell from the tagged retail polygon.
    minz, eavez, ridgez = 0.0, 4.95, 8.40
    verts = [(x, y, z) for z in (minz, eavez) for x, y in RING]
    n = len(RING)
    # The street-side face stays open behind modeled glazing so interior fixtures
    # are visible through the storefront windows.
    faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n) if i != 0]
    walls = mesh_obj("FEXP source footprint brick exterior walls", verts, faces, brick, root)
    walls["source_feature"] = "OpenStreetMap way 374563309"
    walls["wall_height_m"] = eavez
    uv_layer = walls.data.uv_layers.new(name="FacadeUV_meters")
    cumulative = 0.0
    face_index = 0
    for i in range(n):
        if i == 0:
            continue
        poly = walls.data.polygons[face_index]
        a = Vector(RING[i])
        b = Vector(RING[(i + 1) % n])
        length = (b - a).length
        face_uvs = ((cumulative, 0.0), (cumulative + length, 0.0),
                    (cumulative + length, eavez), (cumulative, eavez))
        for loop_index, uv in zip(poly.loop_indices, face_uvs):
            uv_layer.data[loop_index].uv = uv
        cumulative += length
        face_index += 1
    slab = mesh_obj("FEXP interior floor slab", [(x, y, 0.12) for x, y in RING], [tuple(range(n))], tile, root)

    # Main storefront follows the southwest edge facing Northwestern Avenue and
    # the pump apron. That side is represented by the broad first south-west wall
    # segment in the tagged outline; the tiny adjacent segments are the entry jog.
    front_i, front_a, front_b = 0, RING[0], RING[1]
    ft = Vector((front_b[0] - front_a[0], front_b[1] - front_a[1])).normalized()
    fn = Vector((ft.y, -ft.x))
    front_center = (Vector(front_a) + Vector(front_b)) / 2 + fn * 0.13
    front_len = math.dist(front_a, front_b)

    # Continuous pale plinth, corner quoins and top belt emphasize the colonial
    # red-brick shop architecture visible in the address-matched photo.
    for i, p in enumerate(RING):
        q = RING[(i + 1) % n]
        v = Vector((q[0] - p[0], q[1] - p[1]))
        if v.length < 1:
            continue
        t = v.normalized()
        out = Vector((t.y, -t.x))
        mid = (Vector(p) + Vector(q)) / 2
        length = v.length
        box("FEXP pale masonry water table", (mid.x + out.x * 0.05, mid.y + out.y * 0.05, 0.30), (length + 0.08, 0.18, 0.46), cream, root, t, out, 0.025)
        box("FEXP pale roof cornice band", (mid.x + out.x * 0.05, mid.y + out.y * 0.05, 4.98), (length + 0.08, 0.25, 0.34), cream, root, t, out, 0.035)
        # Ground-floor street windows on each long side; tiny service notches stay plain.
        if i != front_i and length > 10:
            count = max(2, int(length // 5))
            for k in range(count):
                frac = (k + 0.5) / count
                a = (p[0] + (q[0] - p[0]) * (frac - 0.22 / count), p[1] + (q[1] - p[1]) * (frac - 0.22 / count))
                b = (p[0] + (q[0] - p[0]) * (frac + 0.22 / count), p[1] + (q[1] - p[1]) * (frac + 0.22 / count))
                add_window("FEXP side retail window %d_%d" % (i, k), a, b, 2.75, 0.98, 1.82, 0.09, root, glass, cream, dark)
        elif i != front_i:
            # Decorative upper clerestory pairs on shorter elevations.
            for frac in (0.32, 0.68):
                a = (p[0] + (q[0] - p[0]) * (frac - 0.10), p[1] + (q[1] - p[1]) * (frac - 0.10))
                b = (p[0] + (q[0] - p[0]) * (frac + 0.10), p[1] + (q[1] - p[1]) * (frac + 0.10))
                add_window("FEXP side window %d_%.1f" % (i, frac), a, b, 2.75, 0.98, 1.55, 0.09, root, glass, cream, dark)

    # Window door arrangement with red-brown brick piers and lit merchandise interior.
    door_center = front_center
    box("FEXP double entry doors", (door_center.x, door_center.y, 1.68), (2.15, 0.14, 2.82), glass, root, ft, fn, 0.015)
    for dx in (-1.08, 0, 1.08):
        p = door_center + ft * dx
        box("FEXP entry door metal stile", (p.x, p.y + fn.y * 0.10, 1.68), (0.085, 0.18, 2.82), cream, root, ft, fn, 0.01)
    box("FEXP entry door transom", (door_center.x, door_center.y + fn.y * 0.1, 3.04), (2.3, 0.18, 0.20), cream, root, ft, fn, 0.012)
    # Two wide storefront windows on each side of the doors, with mullions.
    for side in (-1, 1):
        for j in range(2):
            offset = side * (2.65 + j * 2.9)
            wc = front_center + ft * offset
            box("FEXP storefront window %s_%s" % (side, j), (wc.x, wc.y, 2.60), (2.1, 0.13, 2.20), glass, root, ft, fn, 0.0)
            for dx in (-1.05, 0, 1.05):
                p = wc + ft * dx
                box("FEXP storefront mullion %s_%s" % (side, j), (p.x, p.y + fn.y * 0.1, 2.60), (0.07, 0.18, 2.24), cream, root, ft, fn, 0.006)
            for z in (1.47, 3.73):
                box("FEXP storefront sill %s_%s" % (side, j), (wc.x, wc.y + fn.y * 0.1, z), (2.24, 0.18, 0.13), cream, root, ft, fn, 0.015)

    # Shingled hipped roof. The peak follows the long building axis; a smaller
    # ridge span and four roof planes create the low colonial hip visible in photos.
    pts = [Vector(p) for p in RING]
    major = max((Vector(RING[(i+1)%n])-Vector(RING[i]) for i in range(n)), key=lambda v: v.length)
    u = major.normalized()
    v = Vector((-u.y, u.x))
    proj_u, proj_v = [p.dot(u) for p in pts], [p.dot(v) for p in pts]
    u0, u1 = min(proj_u)-0.75, max(proj_u)+0.75
    v0, v1 = min(proj_v)-0.75, max(proj_v)+0.75
    midv = (v0 + v1) / 2
    halfw = (v1 - v0) / 2
    ridgestart, ridgeend = u0 + halfw * 0.78, u1 - halfw * 0.78
    def world(uu, vv, zz):
        p = u * uu + v * vv
        return (p.x, p.y, zz)
    roof_verts = [world(u0,v0,eavez), world(u1,v0,eavez), world(u1,v1,eavez), world(u0,v1,eavez),
                  world(ridgestart,midv,ridgez), world(ridgeend,midv,ridgez)]
    roof_obj = mesh_obj("FEXP charcoal shingle hip roof", roof_verts,
                        [(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)], roof, root)
    roof_obj["roof_form"] = "low hipped roof, height estimated from exterior photograph"
    # White fascia eave and thin cyan horizontal roof accents.
    for i in range(4):
        a = Vector(roof_verts[i][:2]); b = Vector(roof_verts[(i+1)%4][:2])
        t = (b-a).normalized(); out = Vector((t.y,-t.x)); mid=(a+b)/2
        box("FEXP white roof fascia", (mid.x,mid.y,eavez-0.04), ((b-a).length,0.24,0.30), white, root, t, out, 0.025)
    # Front canopy awning above the storefront and signature brand board.
    box("FEXP white entry awning", (door_center.x + fn.x*0.95, door_center.y + fn.y*0.95, 4.12), (4.1,1.8,0.26), white, root, ft, fn, 0.04)
    for xoff in (-1.7, 1.7):
        p = door_center + ft*xoff + fn*1.62
        cylinder("FEXP awning support", (p.x,p.y,3.12), 0.055, 1.8, dark, root, 12)
    signcenter = front_center + fn*0.25
    box("FEXP storefront brand panel", (signcenter.x,signcenter.y,4.56), (4.9,0.20,0.62), blue, root, ft, fn, 0.06)
    # Red oval-like capsule and white lettering call out the location branding.
    oriented_text("FEXP front sign lettering", "FAMILY EXPRESS", (signcenter.x,signcenter.y,4.56), ft, fn, 0.37, white, root, 0.009)
    # A second branded sign on the main roof fascia, visible over the pump canopy.
    roof_sign_pos = Vector(front_a) + (Vector(front_b)-Vector(front_a))*0.50 + fn*0.4
    box("FEXP roof edge logo backing", (roof_sign_pos.x,roof_sign_pos.y,5.30), (3.3,0.24,0.70), blue, root, ft, fn, 0.08)
    oriented_text("FEXP roof FAMILY EXPRESS logo", "FAMILY EXPRESS", (roof_sign_pos.x,roof_sign_pos.y,5.30), ft, fn, 0.27, white, root, 0.008)
    # Retail floor area and visible aisle fixtures: tile, freezer wall, aisles,
    # checkout counter, colorful product blocks and a small takeout counter.
    center_xy = sum(pts, Vector((0,0))) / len(pts)
    box("FEXP tiled retail floor", (center_xy.x,center_xy.y,0.20), (13.0,10.0,0.10), tile, root, u, v, 0.02)
    for row in range(3):
        aisle_center = center_xy + u*0.8 + v*((row-1)*3.35)
        for shelf_z in (0.72,1.36,2.00):
            box("FEXP aisle shelf %d %.2f"%(row,shelf_z),(aisle_center.x,aisle_center.y,shelf_z),(10.3,0.90,0.08),cream,root,u,v,0.015)
        for support_x in (-5.0,0.0,5.0):
            support=aisle_center+u*support_x
            box("FEXP aisle upright %d %.1f"%(row,support_x),(support.x,support.y,1.37),(0.10,0.78,2.62),shelving,root,u,v,0.015)
        for k in range(12):
            along = -4.55+k*0.82
            for level,z in enumerate((0.96,1.60,2.24)):
                for depth_side in (-1,1):
                    pack_center=aisle_center + u*along + v*(depth_side*0.22)
                    box("FEXP shelf stock %d_%d_%d_%d"%(row,k,level,depth_side),(pack_center.x,pack_center.y,z),(0.48,0.30,0.38),package_mats[(k+level+row)%len(package_mats)],root,u,v,0.025)
    for k in range(10):
        pos=center_xy + u*(-6.2+k*1.28) + v*5.6
        box("FEXP refrigerator cooler %d"%k,(pos.x,pos.y,1.70),(1.10,0.42,2.7),pump_white,root,u,v,0.025)
        box("FEXP refrigerator glass %d"%k,(pos.x,pos.y-v.y*0.24,1.70),(0.97,0.10,2.4),glass,root,u,v,0.012)
    counter=center_xy + u*6.1 + v*(-4.1)
    box("FEXP checkout counter",(counter.x,counter.y,1.12),(5.4,1.0,1.3),wood,root,u,v,0.05)
    for k in range(3):
        p=counter+u*(-1.6+k*1.6)+v*(-0.10)
        box("FEXP register screen %d"%k,(p.x,p.y,1.85),(0.48,0.16,0.48),display,root,u,v,0.02)
    # One small high window band gives the interior a complete story under roof.
    # (All partitions and fixtures remain inside the exact wall polygon envelope.)

    # Fuel canopy faces the long storefront frontage, at a modest offset toward
    # the access apron. This placement is visible in the location-specific photo;
    # exact pump coordinates are not represented in the OSM building footprint.
    canopy_center = front_center + fn * 13.2
    canopy_width, canopy_depth, canopy_z = min(24.0, front_len+2.0), 9.0, 5.0
    box("FEXP pump canopy soffit", (canopy_center.x,canopy_center.y,canopy_z), (canopy_width,canopy_depth,0.44), white, root, ft, fn, 0.08)
    box("FEXP canopy blue fascia main frontage", (canopy_center.x,canopy_center.y+fn.y*canopy_depth/2,canopy_z-0.16), (canopy_width,0.28,0.28), blue, root, ft, fn, 0.035)
    box("FEXP canopy blue stripe secondary", (canopy_center.x,canopy_center.y+fn.y*(canopy_depth/2-0.32),canopy_z-0.18), (canopy_width,0.10,0.10), blue_light, root, ft, fn, 0.02)
    # Six black columns, in three pairs, carry the broad white canopy.
    for i, along in enumerate((-canopy_width*0.43, 0, canopy_width*0.43)):
        for side in (-1, 1):
            p=canopy_center + ft*along + fn*(side*(canopy_depth/2-0.45))
            box("FEXP canopy black steel column %d_%d"%(i,side),(p.x,p.y,2.55),(0.34,0.34,4.95),dark,root,ft,fn,0.035)
            box("FEXP column white base %d_%d"%(i,side),(p.x,p.y,0.30),(0.60,0.60,0.50),cream,root,ft,fn,0.035)
    # Two three-pump rows. Each dispenser includes a white body, blue panels,
    # dark display, nozzles and hanging hose loops.
    for row, npos in enumerate((-2.1,2.1)):
        for i, upos in enumerate((-canopy_width*0.29,0,canopy_width*0.29)):
            p=canopy_center + ft*upos + fn*npos
            box("FEXP pump island %d_%d"%(row,i),(p.x,p.y,0.13),(2.8,0.82,0.25),asphalt,root,ft,fn,0.10)
            box("FEXP dispenser cabinet %d_%d"%(row,i),(p.x,p.y,1.48),(0.95,0.72,2.5),pump_white,root,ft,fn,0.09)
            box("FEXP blue pump header %d_%d"%(row,i),(p.x,p.y,2.53),(0.97,0.76,0.38),blue,root,ft,fn,0.04)
            box("FEXP digital pump screen %d_%d"%(row,i),(p.x,p.y+fn.y*0.38,1.88),(0.54,0.075,0.42),display,root,ft,fn,0.015)
            for side in (-1,1):
                hpos=p+ft*(side*0.44)+fn*0.42
                cylinder("FEXP pump hose loop %d_%d_%d"%(row,i,side),(hpos.x,hpos.y,1.25),0.045,0.88,dark,root,12)
                box("FEXP pump nozzle handle %d_%d_%d"%(row,i,side),(hpos.x,hpos.y,1.63),(0.16,0.15,0.42),dark,root,ft,fn,0.035)
    # Small protective yellow bollards near the store corners and fuel islands.
    for i, along in enumerate((-canopy_width*0.49, canopy_width*0.49)):
        p=canopy_center+ft*along
        for side in (-1,1):
            q=p+fn*(side*0.85)
            cylinder("FEXP yellow site safety bollard %d_%d"%(i,side),(q.x,q.y,0.56),0.11,1.12,yellow,root,14)
    # Store and canopy text signs; use exact chain wording, not a logo image.
    canopy_sign_pos=canopy_center+fn*(canopy_depth/2+0.15)
    box("FEXP canopy front sign backing",(canopy_sign_pos.x,canopy_sign_pos.y,canopy_z+0.03),(5.1,0.22,0.76),blue,root,ft,fn,0.06)
    oriented_text("FEXP canopy illuminated sign","FAMILY EXPRESS",(canopy_sign_pos.x,canopy_sign_pos.y,canopy_z+0.03),ft,fn,0.36,white,root,0.012)

    # Separate preview context, excluded from the linked asset collection.
    def point_target(obj, target):
        obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    target = (center_xy.x + fn.x*4.5, center_xy.y + fn.y*4.5, 3.3)
    cam_data=bpy.data.cameras.new("FEXP exterior preview camera")
    camera=bpy.data.objects.new("FEXP exterior preview camera",cam_data)
    preview.objects.link(camera)
    camera.location=(center_xy.x + fn.x*55.0 - ft.x*42.0, center_xy.y + fn.y*55.0 - ft.y*42.0, 19.0)
    camera.data.lens=46
    point_target(camera,target)
    scene.camera=camera
    for name,loc,power,size in (("FEXP large softbox key",(center_xy.x+fn.x*35-ft.x*20,center_xy.y+fn.y*35-ft.y*20,32),4200,24),
                                ("FEXP canopy fill",(center_xy.x+fn.x*22+ft.x*22,center_xy.y+fn.y*22+ft.y*22,24),2600,18)):
        data=bpy.data.lights.new(name,"AREA")
        obj=bpy.data.objects.new(name,data)
        preview.objects.link(obj)
        obj.location=loc
        obj.data.energy=power
        obj.data.shape="DISK"
        obj.data.size=size
        point_target(obj,target)
    scene.world.use_nodes = True
    world_bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
    world_bg.inputs["Color"].default_value = (0.35,0.47,0.60,1.0)
    world_bg.inputs["Strength"].default_value = 0.65
    scene.render.image_settings.file_format="PNG"
    scene.render.filepath=os.path.join(EVIDENCE_DIR,"exterior_preview.png")
    scene.render.resolution_percentage=75
    scene.camera.data.dof.use_dof=False

    # Ensure asset collection is the only collection linked into the campus master.
    scene.collection.children.unlink(preview)
    # Keep preview objects and camera in their own unlinked collection datablock so
    # they remain available in this source file but do not enter the master library.
    scene.collection.children.link(preview)
    for obj in preview.objects:
        obj.hide_set(True)
    # Save, render review views, and save again with portable procedural materials.
    os.makedirs(EVIDENCE_DIR,exist_ok=True)
    os.makedirs(SOURCE_DIR,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    bpy.ops.render.render(write_still=True)

    # Cutaway evidence image: temporarily remove the roof, pump canopy and
    # storefront glazing, then look down into the retail fixture layout.
    hidden_for_cutaway=[]
    cutaway_tokens=("charcoal shingle hip roof","white roof fascia","pump canopy",
                    "canopy blue fascia","canopy blue stripe","canopy black steel",
                    "canopy front sign","canopy illuminated sign","pump",
                    "yellow site safety bollard","storefront window",
                    "double entry doors","entry door metal stile","entry door transom",
                    "entry awning","awning support","roof edge logo",
                    "storefront brand panel","front sign lettering")
    for obj in root.objects:
        if any(token in obj.name for token in cutaway_tokens):
            hidden_for_cutaway.append((obj,obj.hide_render))
            obj.hide_render=True
    interior_data=bpy.data.cameras.new("FEXP interior cutaway camera")
    interior_cam=bpy.data.objects.new("FEXP interior cutaway camera",interior_data)
    preview.objects.link(interior_cam)
    interior_target=(center_xy.x + fn.x*0.2,center_xy.y + fn.y*0.2,1.9)
    interior_cam.location=(center_xy.x + fn.x*32.0 - ft.x*13.0,
                           center_xy.y + fn.y*32.0 - ft.y*13.0,13.0)
    point_target(interior_cam,interior_target)
    interior_cam.data.type="ORTHO"
    interior_cam.data.ortho_scale=30.0
    scene.camera=interior_cam
    interior_light_data=bpy.data.lights.new("FEXP interior cutaway softbox","AREA")
    interior_light=bpy.data.objects.new("FEXP interior cutaway softbox",interior_light_data)
    preview.objects.link(interior_light)
    interior_light.location=(center_xy.x,center_xy.y,8)
    interior_light.data.energy=1200
    interior_light.data.shape="DISK"
    interior_light.data.size=14
    scene.render.filepath=os.path.join(EVIDENCE_DIR,"interior_cutaway_preview.png")
    bpy.ops.render.render(write_still=True)
    for obj,old_hide in hidden_for_cutaway:
        obj.hide_render=old_hide
    interior_cam.hide_render=True
    interior_light.hide_render=True
    scene.camera=camera

    # A top view is useful to review the modeled footprint and site canopy relation.
    top_data=bpy.data.cameras.new("FEXP top review camera")
    top=bpy.data.objects.new("FEXP top review camera",top_data)
    preview.objects.link(top)
    plan_center = center_xy + fn*7.0
    top.location=(plan_center.x,plan_center.y,82)
    top.rotation_euler=(0,0,0)
    # camera looks toward -Z when rotation is zero
    top.data.type="ORTHO"
    top.data.ortho_scale=90.0
    scene.camera=top
    scene.render.filepath=os.path.join(EVIDENCE_DIR,"top_preview.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

    # Probe summary from in-memory saved result.
    asset_objects=list(root.objects)
    bounds=[]
    for obj in asset_objects:
        if obj.type != "MESH":
            continue
        for c in obj.bound_box:
            v=obj.matrix_world @ Vector(c)
            bounds.append(tuple(v))
    probe={
        "building_id":ASSET_ID,
        "scene":SCENE_NAME,
        "asset_collection":ASSET_COLLECTION,
        "object_count":len(asset_objects),
        "object_names":[o.name for o in asset_objects],
        "mesh_object_count":sum(o.type=="MESH" for o in asset_objects),
        "font_object_count":sum(o.type=="FONT" for o in asset_objects),
        "material_names":sorted({m.name for o in asset_objects if o.type=="MESH" for m in o.data.materials if m}),
        "world_bounds_m":[[min(v[i] for v in bounds) for i in range(3)],[max(v[i] for v in bounds) for i in range(3)]],
        "footprint_ring_world_xy":RING,
        "source_feature":"OpenStreetMap way 374563309",
        "source_footprint_bounds_m":[[min(p[0] for p in RING),max(p[0] for p in RING)],[min(p[1] for p in RING),max(p[1] for p in RING)],[0.0,eavez]],
        "image_datablocks":[{"name":i.name,"source":i.source,"filepath":i.filepath} for i in bpy.data.images],
        "external_image_dependencies":sum(bool(i.filepath) and i.source not in {"GENERATED","VIEWER"} for i in bpy.data.images),
        "linked_libraries":len(bpy.data.libraries),
        "preview_only_objects":len(preview.objects),
        "asset_sha256":hashlib.sha256(open(OUT_BLEND,"rb").read()).hexdigest(),
    }
    with open(os.path.join(EVIDENCE_DIR,"candidate_probe.json"),"w",encoding="utf-8") as f:
        json.dump(probe,f,indent=2)
    print("FAMILY_EXPRESS_BUILD_PASS",json.dumps({k:probe[k] for k in ("object_count","mesh_object_count","font_object_count","world_bounds_m","asset_sha256")}))


if __name__ == "__main__":
    build_asset()
