"""Build a locally-framed detailed asset for Purdue Lutheran Ministry (PLM).

Identity and footprint are sourced from OSM way 860901812 and official Purdue
PLM directory references. The south facade is modeled from an archived official
PLM-site image; roof profile, hidden elevations and room layout remain informed
inferences. All building geometry is local to the documented polygon centroid;
the parent/master supplies campus placement through its marker.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_purdue_lutheran_ministry_5425b3c"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / "purdue_lutheran_ministry"
PREVIEW = EVIDENCE / "review_preview.png"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

# OSM way 860901812, WGS84 vertices ordered NW, NE, SE, SW. The official PLM
# address is 330 W Fowler; the south edge is consequently the road-facing side.
RING_LONLAT = [
    (-86.9096724, 40.4278681),
    (-86.9095744, 40.4278685),
    (-86.9095737, 40.4277594),
    (-86.9096717, 40.4277590),
]
GEO_ORIGIN_LON = -86.9137
GEO_ORIGIN_LAT = 40.4274
LON_M = 111412.84 * math.cos(math.radians(GEO_ORIGIN_LAT))
LAT_M = 111040.0
RING_CAMPUS = [
    ((lon - GEO_ORIGIN_LON) * LON_M, (lat - GEO_ORIGIN_LAT) * LAT_M)
    for lon, lat in RING_LONLAT
]
# Polygon centroid in the project's documented local approximate meter frame.
def polygon_centroid(points):
    cross = [points[i][0] * points[(i + 1) % len(points)][1] -
             points[(i + 1) % len(points)][0] * points[i][1]
             for i in range(len(points))]
    area6 = 3.0 * sum(cross)
    return (sum((points[i][0] + points[(i + 1) % len(points)][0]) * cross[i]
                for i in range(len(points))) / area6,
            sum((points[i][1] + points[(i + 1) % len(points)][1]) * cross[i]
                for i in range(len(points))) / area6)

ANCHOR_XY = polygon_centroid(RING_CAMPUS)
RING = [(x - ANCHOR_XY[0], y - ANCHOR_XY[1]) for x, y in RING_CAMPUS]

WALL_EAVE = 5.70           # approximate two-storey height checked against archived facade photo
GABLE_RISE = 1.55          # roof pitch still inferred; not visible in facade crop
ROOF_OVERHANG = 0.28       # illustrative
WALL_DEPTH = 0.24


def material(name, color, roughness=0.78, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m, bsdf


def procedural_siding():
    m, bsdf = material("PLM | golden yellow horizontal lap siding, archived facade reference", (0.79, 0.36, 0.075), 0.76)
    n, l = m.node_tree.nodes, m.node_tree.links
    tc = n.new("ShaderNodeTexCoord")
    wave = n.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 27.0
    wave.inputs["Distortion"].default_value = 0.0
    l.new(tc.outputs["Object"], wave.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.34
    ramp.color_ramp.elements[0].color = (0.63, 0.27, 0.045, 1)
    ramp.color_ramp.elements[1].position = 0.66
    ramp.color_ramp.elements[1].color = (0.88, 0.44, 0.09, 1)
    l.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.014
    l.new(wave.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def roof_material():
    m, bsdf = material("PLM | weathered charcoal-gray shingles, inferred", (0.20, 0.23, 0.25), 0.91)
    n, l = m.node_tree.nodes, m.node_tree.links
    tc = n.new("ShaderNodeTexCoord")
    mapping = n.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (2.7, 2.7, 2.7)
    l.new(tc.outputs["Object"], mapping.inputs["Vector"])
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 4.0
    noise.inputs["Detail"].default_value = 2.0
    l.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.19
    ramp.color_ramp.elements[0].color = (0.11, 0.13, 0.15, 1)
    ramp.color_ramp.elements[1].position = 0.81
    ramp.color_ramp.elements[1].color = (0.32, 0.35, 0.37, 1)
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.24
    bump.inputs["Distance"].default_value = 0.035
    l.new(noise.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def floor_material():
    m, bsdf = material("PLM | warm terrazzo floor, illustrative", (0.50, 0.45, 0.37), 0.82)
    nodes, links = m.node_tree.nodes, m.node_tree.links
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (0.55, 0.55, 0.55)
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 32
    noise.inputs["Detail"].default_value = 2
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.30, 0.27, 0.23, 1)
    ramp.color_ramp.elements[1].color = (0.63, 0.58, 0.50, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.10
    bump.inputs["Distance"].default_value = 0.007
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def cube(name, loc, dims, mat, col, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for old in list(o.users_collection):
        old.objects.unlink(o)
    col.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    if bevel > 0:
        mod = o.modifiers.new("Fine edge softening", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new("Corner normals", "WEIGHTED_NORMAL")
    return o


def mesh_object(name, verts, faces, mat, col):
    me = bpy.data.meshes.new(name + " | mesh")
    me.from_pydata(verts, [], faces)
    me.materials.append(mat)
    me.update()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def wall_prism(name, a, b, z0, z1, thickness, mat, col):
    # Local XY segment extruded vertically and inward/outward along its normal.
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    p = [(ax + nx * thickness / 2, ay + ny * thickness / 2),
         (bx + nx * thickness / 2, by + ny * thickness / 2),
         (bx - nx * thickness / 2, by - ny * thickness / 2),
         (ax - nx * thickness / 2, ay - ny * thickness / 2)]
    verts = [(x, y, z) for z in (z0, z1) for x, y in p]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_object(name, verts, faces, mat, col)


def roof_panel(name, verts, mat, col):
    ob = mesh_object(name, verts, [(0, 1, 2, 3)], mat, col)
    solid = ob.modifiers.new("Roof board thickness", "SOLIDIFY")
    solid.thickness = 0.16
    ob.modifiers.new("Roof edge normals", "WEIGHTED_NORMAL")
    return ob


def cut_wall_opening(wall, center, tangent, width, height, name):
    """Apply a rectangular-through-wall Boolean; cutter geometry is discarded."""
    cx, cy, cz = center
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    cutter = bpy.context.object
    cutter.name = "TEMP aperture cutter " + name
    cutter.dimensions = (width, 0.90, height)
    cutter.rotation_euler[2] = math.atan2(tangent[1], tangent[0])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    boolean = wall.modifiers.new("True aperture | " + name, "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = cutter
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    wall.select_set(True)
    bpy.context.view_layer.objects.active = wall
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def window(name, center, width, height, horizontal_axis, col, wall_mat, frame_mat, glass_mat,
           shutter_mat=None, shutters=False, vertical_divisions=1, shell_wall=None):
    # Applied to one of the cardinal walls. Horizontal axis is a local tangent.
    cx, cy, cz = center
    tangent = Vector(horizontal_axis).normalized()
    normal = Vector((-tangent.y, tangent.x, 0.0))
    if shell_wall is not None:
        cut_wall_opening(shell_wall, (cx, cy, cz), horizontal_axis, width - 0.10, height - 0.10, name)
    def oriented_cube(nm, offset, dims, mat, bevel=0):
        c = Vector((cx, cy, cz)) + tangent * offset[0] + normal * offset[1] + Vector((0, 0, offset[2]))
        ob = cube(nm, tuple(c), dims, mat, col, bevel)
        ob.rotation_euler[2] = math.atan2(tangent.y, tangent.x)
        if "glazing" not in nm:
            ob.visible_shadow = False
        return ob
    # Window well inside wall plane. Surrounding casing, sash, mullions and sill.
    oriented_cube(name + " | glazing", (0, -WALL_DEPTH * 0.54, 0), (width, 0.035, height), glass_mat, 0.0)
    for s in (-1, 1):
        oriented_cube(name + " | side casing", (s * (width / 2 + 0.055), -WALL_DEPTH * 0.6, 0), (0.11, 0.12, height + 0.22), frame_mat, 0.0)
    for z in (-height / 2 - 0.055, height / 2 + 0.055):
        oriented_cube(name + " | head/sill casing", (0, -WALL_DEPTH * 0.6, z), (width + 0.22, 0.12, 0.11), frame_mat, 0.0)
    for index in range(1, vertical_divisions + 1):
        offset = -width / 2 + width * index / (vertical_divisions + 1)
        oriented_cube(name + f" | mullion {index}", (offset, -WALL_DEPTH * 0.66, 0), (0.045, 0.055, height), frame_mat, 0.0)
    # One horizontal sash rail matches the two-over-two divisions visible in the facade reference.
    for z in (0.0,):
        oriented_cube(name + " | sash", (0, -WALL_DEPTH * 0.66, z), (width, 0.055, 0.035), frame_mat, 0.0)
    if shutters and shutter_mat:
        for side in (-1, 1):
            shx = side * (width / 2 + 0.19)
            oriented_cube(name + " | navy shutter", (shx, -WALL_DEPTH * 0.64, 0), (0.26, 0.10, height + 0.10), shutter_mat, 0.018)
            for z in (-height * 0.27, 0.0, height * 0.27):
                oriented_cube(name + " | shutter louver", (shx, -WALL_DEPTH * 0.71, z), (0.24, 0.045, 0.035), frame_mat, 0.005)


def make_materials():
    siding = procedural_siding()
    roof = roof_material()
    limestone, _ = material("PLM | light concrete foundation", (0.53, 0.52, 0.48), 0.85)
    wood, _ = material("PLM | white entry and window trim", (0.83, 0.80, 0.71), 0.48)
    glass, bsdf = material("PLM | slightly reflective blue-gray glazing", (0.075, 0.16, 0.20), 0.22, 0.15)
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.45
    floor = floor_material()
    oak, _ = material("PLM | warm oak furniture, illustrative", (0.34, 0.17, 0.075), 0.49)
    gutter, _ = material("PLM | aged charcoal gutter metal, inferred", (0.12, 0.14, 0.15), 0.51, 0.24)
    shutter, _ = material("PLM | deep navy upper shutters, archived facade reference", (0.025, 0.055, 0.12), 0.64)
    upholstery, _ = material("PLM | muted blue-green lounge upholstery, illustrative", (0.14, 0.28, 0.29), 0.89)
    return locals()


def build():
    # Dedicated asset scene, no shared/master file is loaded or modified.
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for col in list(bpy.data.collections):
        for child in list(col.children):
            col.children.unlink(child)
    for child in list(scene.collection.children):
        scene.collection.children.unlink(child)
    for col in list(bpy.data.collections):
        if col.users == 0:
            bpy.data.collections.remove(col)
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    detail = bpy.data.collections.new("PLM | exterior, interior and roof details")
    asset.children.link(detail)
    structure = bpy.data.collections.new("PLM | structural shell")
    asset.children.link(structure)
    interior = bpy.data.collections.new("PLM | illustrative interior")
    asset.children.link(interior)
    roof_collection = bpy.data.collections.new("PLM | removable roof panels, hide to inspect interior")
    asset.children.link(roof_collection)
    preview_setup = bpy.data.collections.new("PLM | review-only camera and lights")
    scene.collection.children.link(preview_setup)
    root = bpy.data.objects.new("AssetRoot_" + ASSET_ID, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.55
    root.location = (0, 0, 0)
    asset.objects.link(root)
    root["asset_id"] = ASSET_ID
    root["geometry_coordinate_frame"] = "Local meters centered on OSM footprint polygon centroid"
    root["campus_anchor_xy_m"] = [round(ANCHOR_XY[0], 6), round(ANCHOR_XY[1], 6)]
    root["identity"] = "Purdue Lutheran Ministry, 330 W Fowler Ave; not University Lutheran Church"
    root["facade_roof_uncertainty"] = "Facade material/openings based on archived official PLM photo; other elevations and overall roof form inferred"
    mats = make_materials()

    # Derive oriented wall edges from the actual OSM ring; south edge is Fowler.
    shell_walls = []
    for i in range(4):
        a, b = RING[i], RING[(i + 1) % 4]
        shell_walls.append(wall_prism(f"PLM shell wall {i+1}", a, b, 0.20, WALL_EAVE, WALL_DEPTH, mats["siding"], structure))
    # Slightly raised interior floor and perimeter stone base course.
    floorverts = [(x * 0.965, y * 0.965, 0.22) for x, y in RING]
    mesh_object("PLM | continuous interior floor", floorverts, [(0, 1, 2, 3)], mats["floor"], interior)
    for i in range(4):
        if i == 2:  # keep the Fowler entry threshold clear
            continue
        a, b = RING[i], RING[(i + 1) % 4]
        wall_prism(f"PLM limestone water table {i+1}", a, b, 0.20, 0.48, WALL_DEPTH + 0.045, mats["limestone"], detail)

    # Gabled roof with north-south ridge, inferred from the house footprint and
    # low-resolution overhead imagery; the archived facade crop does not show it.
    xs = [p[0] for p in RING]
    ys = [p[1] for p in RING]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    xmid = (xmin + xmax) / 2
    eave_y0, eave_y1 = ymin - ROOF_OVERHANG, ymax + ROOF_OVERHANG
    ridge_z = WALL_EAVE + GABLE_RISE
    roof_panel("PLM | west roof slope", [
        (xmin - ROOF_OVERHANG, eave_y0, WALL_EAVE),
        (xmid, eave_y0, ridge_z),
        (xmid, eave_y1, ridge_z),
        (xmin - ROOF_OVERHANG, eave_y1, WALL_EAVE)], mats["roof"], roof_collection)
    roof_panel("PLM | east roof slope", [
        (xmid, eave_y0, ridge_z),
        (xmax + ROOF_OVERHANG, eave_y0, WALL_EAVE),
        (xmax + ROOF_OVERHANG, eave_y1, WALL_EAVE),
        (xmid, eave_y1, ridge_z)], mats["roof"], roof_collection)
    # Simple rainwater detailing makes the roof edge legible at street scale.
    for side, xedge in (("west", xmin - ROOF_OVERHANG), ("east", xmax + ROOF_OVERHANG)):
        cube(f"PLM | {side} eavestrough", (xedge, (ymin + ymax) / 2, WALL_EAVE - 0.05),
             (0.15, ymax - ymin + 0.60, 0.12), mats["gutter"], roof_collection, 0.035)
        for yedge, suffix in ((ymin, "south"), (ymax, "north")):
            downspout_height = WALL_EAVE - 0.35
            cube(f"PLM | {side}-{suffix} downspout", (xedge, yedge, 0.35 + downspout_height / 2),
                 (0.085, 0.085, downspout_height), mats["gutter"], roof_collection, 0.025)

    # Gable infill at north and south ends. End façade geometry follows the exact footprint frontage.
    for side, a, b, orient in (("south", RING[3], RING[2], -1),
                               ("north", RING[0], RING[1], 1)):
        yedge = (a[1] + b[1]) / 2
        left, right = sorted((a, b), key=lambda p: p[0])
        verts = [(left[0], yedge, WALL_EAVE), (right[0], yedge, WALL_EAVE), (xmid, yedge, ridge_z),
                 (left[0], yedge + orient * WALL_DEPTH, WALL_EAVE), (right[0], yedge + orient * WALL_DEPTH, WALL_EAVE), (xmid, yedge + orient * WALL_DEPTH, ridge_z)]
        faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
        mesh_object(f"PLM | {side} gable infill", verts, faces, mats["siding"], structure)

    # The south/Fowler facade is directly informed by a PLM-owned archived image:
    # yellow lap siding, second-storey navy shutters, white-trimmed glazing, a glass
    # entry, broad front window and ministry sign. Small positioning remains estimated.
    door_x = xmid - 2.55
    door_y = ymin
    cut_wall_opening(shell_walls[2], (door_x + 0.38, door_y, 1.48), (1.0, 0.0, 0.0), 1.92, 2.52, "south glazed entrance")
    cube("PLM | entry surround", (door_x + 0.38, door_y - 0.06, 1.48), (2.02, 0.18, 2.56), mats["wood"], detail, 0.035)
    cube("PLM | glazed entry door", (door_x + 0.03, door_y - 0.165, 1.48), (1.22, 0.045, 2.28), mats["glass"], detail, 0.018)
    cube("PLM | door lower kick plate", (door_x + 0.03, door_y - 0.20, 0.45), (1.00, 0.035, 0.20), mats["wood"], detail, 0.012)
    cube("PLM | narrow information sidelight", (door_x + 0.88, door_y - 0.17, 1.50), (0.42, 0.05, 2.22), mats["shutter"], detail, 0.015)
    # Narrow white framing breaks the glazed door and sidelight into real panels.
    for dx in (-0.60, 0.65, 1.12):
        cube("PLM | entry vertical trim", (door_x + dx, door_y - 0.205, 1.48), (0.075, 0.06, 2.45), mats["wood"], detail, 0.01)
    for z in (0.28, 2.62):
        cube("PLM | entry horizontal trim", (door_x + 0.38, door_y - 0.205, z), (2.02, 0.06, 0.08), mats["wood"], detail, 0.01)
    cube("PLM | entry pull handle", (door_x + 0.41, door_y - 0.24, 1.28), (0.035, 0.045, 0.32), mats["gutter"], detail, 0.012)

    # Broad, shallow porch canopy (asphalt shingle cover visible in the official image).
    porch_front_y = ymin - 1.80
    porch_rear_y = ymin + 0.12
    porch_front_z = 3.12
    porch_rear_z = 3.42
    roof_panel("PLM | front porch shingle canopy", [
        (xmin - 0.28, porch_front_y, porch_front_z),
        (xmax + 0.28, porch_front_y, porch_front_z),
        (xmax + 0.28, porch_rear_y, porch_rear_z),
        (xmin - 0.28, porch_rear_y, porch_rear_z)], mats["roof"], roof_collection)
    cube("PLM | porch canopy fascia", (xmid, porch_front_y, porch_front_z - 0.04),
         (xmax - xmin + 0.62, 0.14, 0.24), mats["wood"], detail, 0.025)
    for side, x in (("west", xmin + 0.16), ("east", xmax - 0.16)):
        cube(f"PLM | {side} porch support post", (x, porch_front_y + 0.12, 1.70),
             (0.15, 0.15, 2.76), mats["siding"], detail, 0.02)
    cube("PLM | front porch deck", (xmid, (porch_front_y + ymin) / 2, 0.18),
         (xmax - xmin + 0.26, ymin - porch_front_y + 0.22, 0.20), mats["limestone"], detail, 0.035)
    cube("PLM | front porch step", (door_x + 0.38, porch_front_y - 0.30, 0.10), (2.5, 0.48, 0.16), mats["limestone"], detail, 0.025)
    # A small west-side handrail echoes the visible yellow porch rail in the photo.
    cube("PLM | west porch handrail", (xmin + 0.23, porch_front_y + 0.90, 0.83), (0.09, 1.65, 0.10), mats["siding"], detail, 0.02)
    for y in (porch_front_y + 0.15, porch_front_y + 1.60):
        cube("PLM | west porch rail post", (xmin + 0.23, y, 0.51), (0.09, 0.09, 0.69), mats["siding"], detail, 0.015)

    south_tangent = (1.0, 0.0, 0.0)
    window("PLM | south front triple window", (xmid + 2.48, ymin, 1.93), 2.25, 1.48, south_tangent,
           detail, mats["siding"], mats["wood"], mats["glass"], vertical_divisions=2, shell_wall=shell_walls[2])
    window("PLM | south second-storey west window", (xmid - 2.05, ymin, 4.48), 1.12, 1.34, south_tangent,
           detail, mats["siding"], mats["wood"], mats["glass"], mats["shutter"], shutters=True, shell_wall=shell_walls[2])
    window("PLM | south second-storey east window", (xmid + 2.00, ymin, 4.48), 1.12, 1.34, south_tangent,
           detail, mats["siding"], mats["wood"], mats["glass"], mats["shutter"], shutters=True, shell_wall=shell_walls[2])

    # Explicit nameplate copied from the readable wording on the archived PLM image.
    sign_x = xmid - 0.05
    sign_z = 2.22
    sign_y = ymin - 0.12
    plaque = cube("PLM | exterior ministry sign", (sign_x, sign_y, sign_z), (2.62, 0.12, 0.83), mats["wood"], detail, 0.025)
    plaque["text_reference"] = "PLM / Purdue Lutheran Ministry / 330 West Fowler Avenue (archived official PLM photo)"
    for label, body, z, size in (("brand", "LuMin", 2.36, 0.33),
                                 ("name", "PURDUE LUTHERAN MINISTRY", 2.02, 0.12)):
        bpy.ops.object.text_add(location=(sign_x, sign_y - 0.075, z))
        lettering = bpy.context.object
        lettering.name = f"PLM | exterior sign {label} lettering"
        lettering.data.body = body
        lettering.data.align_x = "CENTER"
        lettering.data.align_y = "CENTER"
        lettering.data.size = size
        lettering.data.extrude = 0.001
        lettering.rotation_euler[0] = math.radians(90)
        lettering.data.materials.append(mats["shutter"])
        for old in list(lettering.users_collection):
            old.objects.unlink(lettering)
        detail.objects.link(lettering)

    # Side elevations and upper stories are not shown clearly in the available
    # facade image; these regular house windows are conservative, inferred placement.
    for side, x, side_tangent in (("east", xmax, (0.0, 1.0, 0.0)),
                                  ("west", xmin, (0.0, -1.0, 0.0))):
        for floor_level, z in (("ground", 1.95), ("upper", 4.35)):
            for k, y in enumerate((ymin + 3.0, ymin + 8.7)):
                window(f"PLM | {side} {floor_level} side window {k+1}", (x, y, z), 1.08, 1.28, side_tangent,
                       detail, mats["siding"], mats["wood"], mats["glass"], shell_wall=shell_walls[1 if side == "east" else 3])

    # Interior-ready, schematic converted-ministry common room. The archived
    # photograph proves the former house-style facade but supplies no floor plan;
    # furnishings are deliberately illustrative and modest.
    interior_x0, interior_x1 = xmin + 0.32, xmax - 0.32
    interior_y0, interior_y1 = ymin + 0.32, ymax - 0.32
    lounge_x = xmid - 1.35
    lounge_y = ymin + 4.15
    # Sofa with separate seat/back cushions and short block feet.
    cube("PLM | illustrative lounge sofa base", (lounge_x, lounge_y, 0.47), (2.55, 0.88, 0.44), mats["upholstery"], interior, 0.14)
    cube("PLM | illustrative lounge sofa back", (lounge_x, lounge_y + 0.35, 1.05), (2.55, 0.20, 0.78), mats["upholstery"], interior, 0.13)
    for xoff in (-0.78, 0.0, 0.78):
        cube("PLM | illustrative sofa seat cushion", (lounge_x + xoff, lounge_y - 0.055, 0.72), (0.72, 0.68, 0.16), mats["upholstery"], interior, 0.07)
    for xoff in (-1.05, 1.05):
        cube("PLM | illustrative sofa arm", (lounge_x + xoff, lounge_y - 0.02, 0.77), (0.34, 0.88, 0.48), mats["upholstery"], interior, 0.10)
    for xoff in (-1.0, 1.0):
        for yoff in (-0.30, 0.30):
            cube("PLM | illustrative sofa foot", (lounge_x + xoff, lounge_y + yoff, 0.25), (0.11, 0.11, 0.32), mats["oak"], interior, 0.015)
    # Low coffee table and two informal lounge chairs face the sofa.
    coffee_y = lounge_y - 1.05
    cube("PLM | illustrative coffee table top", (lounge_x, coffee_y, 0.63), (1.18, 0.65, 0.12), mats["oak"], interior, 0.035)
    for xoff in (-0.48, 0.48):
        for yoff in (-0.23, 0.23):
            cube("PLM | illustrative coffee table leg", (lounge_x + xoff, coffee_y + yoff, 0.39), (0.07, 0.07, 0.48), mats["oak"], interior, 0.01)
    for xoff in (-2.75, 2.20):
        cube("PLM | illustrative lounge chair seat", (xmid + xoff, coffee_y - 0.08, 0.63), (0.82, 0.78, 0.20), mats["upholstery"], interior, 0.08)
        cube("PLM | illustrative lounge chair back", (xmid + xoff, coffee_y + 0.24, 1.05), (0.82, 0.18, 0.90), mats["upholstery"], interior, 0.08)
    # A small community table and four chairs form a second flexible gathering area.
    dining_x = xmid + 1.55
    dining_y = interior_y1 - 2.0
    cube("PLM | illustrative community table top", (dining_x, dining_y, 0.91), (1.72, 0.82, 0.12), mats["oak"], interior, 0.035)
    for dx in (-0.68, 0.68):
        for dy in (-0.27, 0.27):
            cube("PLM | illustrative community table leg", (dining_x + dx, dining_y + dy, 0.51), (0.08, 0.08, 0.80), mats["oak"], interior, 0.012)
    for dx in (-0.72, 0.72):
        for dy in (-0.74, 0.74):
            cube("PLM | illustrative community chair seat", (dining_x + dx, dining_y + dy, 0.53), (0.48, 0.48, 0.12), mats["oak"], interior, 0.025)
            cube("PLM | illustrative community chair back", (dining_x + dx, dining_y + dy + (0.24 if dy < 0 else -0.24), 0.95), (0.48, 0.09, 0.78), mats["oak"], interior, 0.025)

    # Parent all geometry to explicit placement origin. Root origin == GIS polygon centroid.
    for obj in list(detail.objects) + list(structure.objects) + list(interior.objects) + list(roof_collection.objects):
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
    # Review rig remains outside the exported model collection to avoid duplicated
    # cameras/lights when the building asset is instanced in the campus master.
    world = bpy.data.worlds.new("PLM studio world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.24, 0.30, 0.39, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.40
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.camera = None
    bpy.ops.object.light_add(type="AREA", location=(6, -10, 14))
    key = bpy.context.object
    key.name = "PLM | key softbox"
    key.data.energy = 1900
    key.data.shape = "DISK"
    key.data.size = 8
    key.rotation_euler = (math.radians(22), 0, math.radians(28))
    for old in list(key.users_collection): old.objects.unlink(key)
    preview_setup.objects.link(key)
    bpy.ops.object.light_add(type="AREA", location=(-9, 1, 9))
    fill = bpy.context.object
    fill.name = "PLM | cool fill"
    fill.data.energy = 1000
    fill.data.size = 7
    fill.rotation_euler = (math.radians(25), 0, math.radians(-35))
    for old in list(fill.users_collection): old.objects.unlink(fill)
    preview_setup.objects.link(fill)

    bpy.ops.object.camera_add(location=(12, -19, 4.5))
    camera = bpy.context.object
    camera.name = "PLM | review camera"
    target = Vector((0, 0, 2.8))
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 48
    for old in list(camera.users_collection): old.objects.unlink(camera)
    preview_setup.objects.link(camera)
    scene.camera = camera
    scene.render.filepath = str(PREVIEW)

    # Documentation custom properties make the origin and uncertainty discoverable in Blender.
    scene["asset_id"] = ASSET_ID
    scene["asset_frame"] = "All model geometry local to polygon centroid. Set Placement_<asset id> XY to campus_anchor_xy_m."
    scene["campus_anchor_xy_m"] = [round(ANCHOR_XY[0], 6), round(ANCHOR_XY[1], 6)]
    scene["footprint_source"] = "OSM way 860901812, downloaded 2026-10-26; EPSG:4326"
    scene["facade_height_roof_and_interior_status"] = "South facade based on archived PLM-hosted photo; height/roof profile/side elevations/interior layout remain estimated or inferred"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH), compress=True)
    bpy.ops.render.render(write_still=True)
    # A second, higher angle shows the inferred main-roof profile separately
    # from the street-level facade reference view.
    roof_preview = EVIDENCE / "review_preview_roof.png"
    camera.location = (12.0, -19.0, 8.2)
    camera.rotation_euler = (Vector((0.0, 0.0, 3.6)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(roof_preview)
    bpy.ops.render.render(write_still=True)
    interior_preview = EVIDENCE / "review_preview_interior.png"
    roof_collection.hide_render = True
    structure.hide_render = False
    for ob in structure.objects:
        ob.hide_render = True
    for name in ("PLM shell wall 1", "PLM | north gable infill"):
        if name in bpy.data.objects:
            bpy.data.objects[name].hide_render = False
    for ob in detail.objects:
        if ob.type not in {"LIGHT", "CAMERA"}:
            ob.hide_render = True
    camera.location = (10.5, -15.5, 13.0)
    camera.rotation_euler = (Vector((0.0, 0.0, 1.0)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 42
    scene.render.filepath = str(interior_preview)
    bpy.ops.render.render(write_still=True)
    # Restore the asset's normal visible/renderable state and the street view camera.
    roof_collection.hide_render = False
    structure.hide_render = False
    for ob in structure.objects:
        ob.hide_render = False
    for ob in detail.objects:
        ob.hide_render = False
    camera.location = (12.0, -19.0, 4.5)
    camera.rotation_euler = (Vector((0.0, 0.0, 2.8)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 48
    scene.render.filepath = str(PREVIEW)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH), compress=True)

    # Evidence JSON is dedicated to this assigned asset.
    bounds_local = {
        "x": [min(p[0] for p in RING), max(p[0] for p in RING)],
        "y": [min(p[1] for p in RING), max(p[1] for p in RING)],
        "wall_eave_z_m_estimated": WALL_EAVE,
        "ridge_z_m_estimated": ridge_z,
    }
    record = {
        "asset_id": ASSET_ID,
        "identity": "Purdue Lutheran Ministry (PLM), 330 W Fowler Ave; this is not University Lutheran Church at 460 Northwestern.",
        "artifact": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "model_coordinate_frame": {
            "axes": "X east, Y north, Z up; meters",
            "campus_geographic_origin": {"latitude": GEO_ORIGIN_LAT, "longitude": GEO_ORIGIN_LON},
            "placement_anchor_xy_m": [round(ANCHOR_XY[0], 6), round(ANCHOR_XY[1], 6)],
            "anchor_method": "centroid of four-vertex OSM way 860901812 after applying the project's approximate equirectangular transform",
            "local_geometry": "Subtract placement_anchor_xy_m from project campus-meter footprint; root empty at local (0,0,0). Integrator should set Placement_<asset_id> location XY to the recorded anchor, leaving root and children untransformed. Review-only camera/lights are outside the exported asset collection.",
            "local_footprint_bounds_m": bounds_local,
        },
        "verification": {
            "identity": "verified by official Our Saviour/PLM page and Purdue resource guide",
            "footprint": "OSM footprint used; it matches the target massing's original XY bounds to rounding. A correctly centered official Purdue BuildingShapes GIS envelope query returned no intersecting features, so no authoritative Purdue building polygon is available for this independent ministry parcel.",
            "position": "within approximate project transform; placement anchor is OSM polygon centroid",
            "orientation": "OSM ring orientation verified; Fowler street/address side is south",
            "height": "no verified height source; two storeys are visible in an archived official PLM facade photo. Modeled eaves at 5.70m and ridge at 7.25m as an approximate residential scale; not measured.",
            "roof_form": "main roof pitch/profile is unverified; simple north-south gable is inferred from rectangular house footprint and low-resolution overhead imagery. Shallow shingle porch canopy is visible in PLM facade source.",
            "facade_openings_and_material": "south facade visually supported by archived official PLM photo: golden-yellow lap siding, white trim, two upper double-hung windows with navy shutters, glazed entry, wide lower window, sign, and shallow shingle porch roof. Approximate feature sizes/positions; north and side facades remain inferred.",
            "interior": "schematic converted-house ministry lounge/common room, not a sourced floor plan",
            "texture_assets": "procedural, packed in Blender material nodes; no external texture file dependencies",
            "quality_limitations": ["The available PLM image is an archival close crop, not a current complete elevation; it supports visible south facade materials and features but not exact dimensions, full roof silhouette, side/rear elevations, or current condition."],
        },
        "sources": [
            {
                "provider": "Purdue University BuildingShapes FeatureServer layer",
                "feature_id": "spatial envelope query at the verified PLM location returned zero features (not a positive feature match)",
                "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&geometry=-86.9100,40.4275,-86.9093,40.4281&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&f=geojson",
                "retrieval_date": "2026-10-26",
                "source_date": "live feature service layer; no feature returned",
                "source_crs": "EPSG:4326 query envelope; no output feature geometry",
                "method": "Queried a 0.0007 by 0.0006 degree envelope around the official location pin and exact named OSM footprint. The envelope intersects no Purdue BuildingShapes features; consequently this layer supplies no authoritative PLM footprint.",
                "uncertainty": "A zero match can reflect layer coverage (PLM is an independent ministry property) rather than prove no building exists.",
                "snapshot": "sources/purdue_gis_plm_area_2026-10-26.geojson",
            },
            {
                "provider": "OpenStreetMap contributors",
                "feature_id": "way/860901812",
                "url": "https://api.openstreetmap.org/api/0.6/way/860901812/full.json",
                "retrieval_date": "2026-10-26",
                "source_date": "2020-10-20T13:47:46Z (OSM way timestamp)",
                "source_crs": "EPSG:4326 WGS 84",
                "method": "Downloaded raw full way JSON; used closed building polygon vertices only. Transform used project local equirectangular approximation stated above.",
                "uncertainty": "OpenStreetMap footprint is not a surveyed as-built record; no authoritative Purdue BuildingShapes feature returned for the target building.",
                "snapshot": "sources/osm_way_860901812_full_2026-10-26.json",
            },
            {
                "provider": "Purdue University College of Science",
                "feature_id": "Lafayette Area Resource Guide for Students, Fall 2022, Religious Centers entry",
                "url": "https://web.ics.purdue.edu/~thomazj/Lafayette%20Area%20Resource%20Guide%20-%20Fall%202022.pdf",
                "retrieval_date": "2026-10-26",
                "source_date": "Fall 2022; last updated 2022-05-03",
                "source_crs": "address text only; no geometry",
                "method": "Identity/address check: PLM at 330 W Fowler at Fowler/Northwestern intersection. Distinguishes it from University Lutheran Church at 460 Northwestern.",
                "uncertainty": "Address confirms identity only; no footprint or architectural details.",
                "snapshot": "sources/purdue_resource_guide_fall_2022.pdf",
            },
            {
                "provider": "Our Saviour Lutheran Church / Purdue Lutheran Ministry official page",
                "feature_id": "location listing Purdue Lutheran Ministry – PLM",
                "url": "https://osluth.org/locations/purdue-lutheran-ministry-plm/",
                "retrieval_date": "2026-10-26",
                "source_date": "page crawled during retrieval; no posted feature date",
                "source_crs": "WGS84 latitude/longitude as listed on page",
                "method": "Confirms official address and page coordinates (40.4277913, -86.9096160). Coordinates fall within/at the target named OSM building footprint.",
                "uncertainty": "Official location pin, not a measured building wall corner/centroid.",
                "snapshot": "sources/official_plm_location_page_2026-10-26.html; official page's image field referenced plm.jpg but its image URL was 404",
            },
            {
                "provider": "Purdue Lutheran Ministry website (PLM-hosted image preserved by Internet Archive Wayback Machine)",
                "feature_id": "cropped-PLM-House-resized-1536x922.jpg; Wayback image capture 2024-02-12 09:59:23 UTC",
                "url": "https://web.archive.org/web/20240212095923im_/https://plm.org/wp-content/uploads/2017/06/cropped-PLM-House-resized-1536x922.jpg",
                "original_url": "https://plm.org/wp-content/uploads/2017/06/cropped-PLM-House-resized-1536x922.jpg",
                "retrieval_date": "2026-10-26",
                "source_date": "image path identifies June 2017; archived image capture 2024-02-12",
                "source_crs": "unreferenced facade photograph; visible sign reads Purdue Lutheran Ministry, 330 West Fowler Avenue",
                "method": "Used as direct south/front facade evidence for the yellow/orange lap siding, upper pair of windows and navy shutters, white trim, glazed entry/sidelight, broad lower window, PLM/LuMin identity sign, and shallow shingle canopy. Scaled features approximately against the OSM footprint; no unseen side or roof details inferred from the crop.",
                "uncertainty": "Close-cropped archival facade view; does not show ground line, full building height, roof silhouette, or current alterations.",
                "snapshot": "sources/plm_house_archived_2024.jpg",
            },
            {
                "provider": "Esri World Imagery basemap",
                "feature_id": "World_Imagery/MapServer tile z20/y395337/x271145",
                "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/20/395337/271145",
                "retrieval_date": "2026-10-26",
                "source_date": "mosaic date unspecified by tile service",
                "source_crs": "Web Mercator tile matrix, EPSG:3857",
                "method": "Retrieved unmodified tile for context; compared pixel tile coordinates with OSM polygon projected to Web Mercator. The 256px tile resolves footprint/roof tone only; not facade or height.",
                "uncertainty": "Image mosaic vintage and resolution support only broad roof shape/land cover; roof pitch and material remain unverified.",
                "snapshot": "sources/world_imagery_tile.jpg; sources/world_imagery_plm_crop_enlarged.jpg is nearest-neighbor enlargement for human review",
            },
        ],
        "asset_edits": [
            "Replaced single unsupported 16m extruded massing prism with one local-coordinate detailed converted-house ministry asset.",
            "Retained the four-vertex OSM footprint and explicit centroid placement origin.",
            "Modeled the visible south facade from PLM's archived official image; added a procedural lap-siding texture, white trim, navy shutters, glazed entry, ministry sign, shallow porch canopy, inferred two-storey shell/roof and illustrative lounge interior.",
            "Kept all geometry within this dedicated asset collection and made no master, README, manifest, or other shared-file changes.",
        ],
        "review_previews": ["review_preview.png", "review_preview_roof.png", "review_preview_interior.png"],
    }
    (EVIDENCE / "evidence_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("PLM_ANCHOR_XY_M", [round(ANCHOR_XY[0], 6), round(ANCHOR_XY[1], 6)])
    print("PLM_LOCAL_FOOTPRINT_BOUNDS", json.dumps(bounds_local))
    print("PLM_ASSET", ASSET_PATH)


if __name__ == "__main__":
    build()
