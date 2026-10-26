"""Build the Bindley Bioscience Center asset from the matched Purdue footprint.

Run with the project's Blender executable:
    blender --background --python build_bindley_bioscience_center.py

Geometry is in local metres centered on the GIS footprint centroid. The campus
Placement_bindley_bioscience_center marker remains controlled by the manifest.
Photographic facade cues are identified in the evidence record; unmeasured
dimensions and the interior tableau are explicitly interpretive.
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "bindley_bioscience_center"
ASSET_FILE = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
EVIDENCE_DIR = ROOT / "audit" / BUILDING_ID
GIS_FILE = EVIDENCE_DIR / "sources" / "gis_feature_605.json"
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LON_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
LAT_M = 111040.0

with GIS_FILE.open(encoding="utf-8") as source:
    gis = json.load(source)
feature = gis["feature"]
attributes = feature["attributes"]
assert attributes["FID"] == 605
assert attributes["BLDG_ABBR"] == "BIND"
assert attributes["BUILDING_N"] == "Bindley Bioscience Center"
ring = feature["geometry"]["rings"][0]
xy = [((p[0] - ORIGIN_LON) * LON_M, (p[1] - ORIGIN_LAT) * LAT_M) for p in ring[:-1]]

twice_area = sum(xy[i][0] * xy[(i + 1) % len(xy)][1]
                 - xy[(i + 1) % len(xy)][0] * xy[i][1]
                 for i in range(len(xy)))
assert abs(twice_area) > 10.0
area_sign = 1.0 if twice_area > 0 else -1.0
centroid_x = sum((xy[i][0] + xy[(i + 1) % len(xy)][0]) *
                 (xy[i][0] * xy[(i + 1) % len(xy)][1]
                  - xy[(i + 1) % len(xy)][0] * xy[i][1])
                 for i in range(len(xy))) / (3.0 * twice_area)
centroid_y = sum((xy[i][1] + xy[(i + 1) % len(xy)][1]) *
                 (xy[i][0] * xy[(i + 1) % len(xy)][1]
                  - xy[(i + 1) % len(xy)][0] * xy[i][1])
                 for i in range(len(xy))) / (3.0 * twice_area)
footprint = [(x - centroid_x, y - centroid_y) for x, y in xy]

# Create a simplified facade guide for opening rhythms, while retaining the
# full unsimplified GIS ring for the primary shell and plan outline.
def distance_to_line(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    if denom <= 1e-12:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denom))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def rdp(points, tolerance):
    if len(points) <= 2:
        return points
    distances = [(i, distance_to_line(points[i], points[0], points[-1]))
                 for i in range(1, len(points) - 1)]
    index, max_distance = max(distances, key=lambda item: item[1])
    if max_distance <= tolerance:
        return [points[0], points[-1]]
    left = rdp(points[:index + 1], tolerance)
    right = rdp(points[index:], tolerance)
    return left[:-1] + right


closed = footprint + [footprint[0]]
facade_points = rdp(closed, 0.35)[:-1]
facade_edges = []
for i, a in enumerate(facade_points):
    b = facade_points[(i + 1) % len(facade_points)]
    length = math.dist(a, b)
    if length >= 5.5:
        facade_edges.append((i, a, b, length))
assert facade_edges, "GIS outline did not yield facade runs"
front_index, front_a, front_b, front_length = max(facade_edges, key=lambda item: item[3])

# Empty scene and a dedicated export collection. Render cameras/lights remain in
# their own non-exported collection and are never linked into the campus master.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    bpy.data.collections.remove(collection)
scene = bpy.context.scene
asset = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset)
asset["building_id"] = BUILDING_ID
asset["source_feature_id"] = 605
asset["local_frame"] = "GIS polygon centroid; metres; X east, Y north, Z up"
shells = bpy.data.collections.new("BIND_Shell_and_roof")
facade = bpy.data.collections.new("BIND_Facade_and_entry")
interior = bpy.data.collections.new("BIND_Schematic_interior_not_as_built")
for collection in (shells, facade, interior):
    asset.children.link(collection)
rig = bpy.data.collections.new("Preview_Rig_not_for_export")
scene.collection.children.link(rig)


def material(name, color, roughness=0.55, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, alpha)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (*color, alpha)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        shader.inputs["Alpha"].default_value = alpha
        mat.blend_method = "BLEND"
    return mat


panel = material("BIND | pale silver aluminum composite panels", (0.62, 0.66, 0.68), 0.43, 0.52)
concrete = material("BIND | warm light cast concrete", (0.70, 0.67, 0.60), 0.78)
glass = material("BIND | blue gray laboratory curtain wall glass", (0.19, 0.34, 0.40), 0.19, 0.20, 0.62)
frame = material("BIND | dark blue gray anodized aluminum framing", (0.055, 0.085, 0.10), 0.34, 0.68)
sign_mat = material("BIND | charcoal entry sign wall", (0.018, 0.024, 0.028), 0.73)
roof_mat = material("BIND | low slope charcoal roof membrane", (0.20, 0.23, 0.24), 0.78)
plant = material("BIND | screened rooftop mechanical plant", (0.43, 0.47, 0.47), 0.63, 0.18)
warm = material("BIND | schematic laboratory furnishings", (0.57, 0.50, 0.39), 0.67)
white = material("BIND | warm white signage", (0.89, 0.88, 0.80), 0.48)


def mesh_object(name, verts, faces, collection, mat):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.validate(clean_customdata=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def prism(name, points, z0, z1, collection, mat):
    n = len(points)
    verts = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return mesh_object(name, verts, faces, collection, mat)


def box(name, center, size, collection, mat, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    obj.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def text_object(name, body, location, size, angle, collection, mat):
    data = bpy.data.curves.new(name + "Curve", "FONT")
    data.body = body
    data.size = size
    data.extrude = 0.006
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi / 2, 0.0, angle + math.pi)
    obj.data.materials.append(mat)
    return obj


# GIS outline controls the full horizontal envelope. The source record's 3 level
# count is retained, but no GIS elevation/extrusion field is interpreted as a
# surveyed vertical dimension.
eave_z = 13.3  # estimated for visualization; no verified section/elevation found
roof_z = 13.9
parapet_top = 14.55
prism("BIND_GIS_primary_shell", footprint, 0.0, eave_z, shells, panel)
prism("BIND_low_slope_roof", footprint, eave_z, roof_z, shells, roof_mat)
prism("BIND_ground_level_plinth", footprint, 0.0, 0.42, facade, concrete)

# Floor bands and exterior openings. The glazing, light metal palette and
# sign-wall/entrance composition follow building-specific architect/Purdue
# photos; bay sizes and all unpictured sides remain estimated.
floors = ((0.80, 3.55), (4.75, 7.50), (8.70, 11.45))
for z in (4.15, 8.10, 12.0):
    for edge_no, a, b, length in facade_edges:
        theta = math.atan2(b[1] - a[1], b[0] - a[0])
        count = max(1, int(length / 4.0))
        for bay in range(count):
            along = length * (bay + 0.5) / count
            x = a[0] + along * math.cos(theta)
            y = a[1] + along * math.sin(theta)
            box(f"BIND_panel_band_{z:.1f}_{edge_no}_{bay}", (x, y, z),
                (length / count + 0.02, 0.22, 0.20), facade, panel, theta)

for edge_no, a, b, length in facade_edges:
    dx, dy = b[0] - a[0], b[1] - a[1]
    theta = math.atan2(dy, dx)
    outward = -area_sign
    nx, ny = outward * -math.sin(theta), outward * math.cos(theta)
    count = max(1, int(length / 4.0))
    spacing = length / count
    for floor_no, (bottom, top) in enumerate(floors):
        for bay in range(count):
            # Leave realistic opaque panel piers between broad research windows.
            if (bay + edge_no) % 5 == 2 and length > 14:
                continue
            along = -length / 2 + spacing * (bay + 0.5)
            mx = (a[0] + b[0]) / 2 + along * math.cos(theta)
            my = (a[1] + b[1]) / 2 + along * math.sin(theta)
            width = spacing * 0.77
            # Main photographed lobby is expressed as a wider, two-storey glazed bay.
            at_front = edge_no == front_index and abs(along) < length * 0.34
            if at_front:
                if floor_no > 0:
                    continue
                bottom, top = (0.48, 11.65)
                width = spacing * 0.90
            # Facade guides simplify the dense GIS ring by at most 0.35m; this
            # stand-off keeps glazing outside the exact shell surface.
            surface = 0.65
            box(f"BIND_glazing_{edge_no}_{floor_no}_{bay}",
                (mx + nx * surface, my + ny * surface, (bottom + top) / 2),
                (width, 0.08, top - bottom), facade, glass, theta)
            for sign in (-1, 1):
                offset = sign * width * 0.48
                box(f"BIND_mullion_{edge_no}_{floor_no}_{bay}_{sign}",
                    (mx + math.cos(theta) * offset + nx * (surface + 0.055),
                     my + math.sin(theta) * offset + ny * (surface + 0.055), (bottom + top) / 2),
                    (0.075, 0.12, top - bottom + 0.10), facade, frame, theta)
            box(f"BIND_window_sill_{edge_no}_{floor_no}_{bay}",
                (mx + nx * (surface + 0.04), my + ny * (surface + 0.04), bottom - 0.06),
                (width + 0.12, 0.16, 0.11), facade, panel, theta)

# The distinctive dark name wall and canopy flank the main glazed entrance.
front_theta = math.atan2(front_b[1] - front_a[1], front_b[0] - front_a[0])
front_nx = -area_sign * -math.sin(front_theta)
front_ny = -area_sign * math.cos(front_theta)
front_mid_x = (front_a[0] + front_b[0]) / 2
front_mid_y = (front_a[1] + front_b[1]) / 2
sign_center = -front_length * 0.22
# Purdue and Flad exterior photographs show a broad, opaque, charcoal name
# wall beside/in front of the lobby glazing. Put it clearly in the foreground
# so the label reads against the wall rather than getting lost on glass.
sign_x = front_mid_x + sign_center * math.cos(front_theta) + front_nx * 0.98
sign_y = front_mid_y + sign_center * math.sin(front_theta) + front_ny * 0.98
box("BIND_entry_name_wall", (sign_x, sign_y, 1.75), (18.0, 0.72, 3.5), facade, sign_mat, front_theta)
text_object("BIND_entry_sign_text", "BINDLEY BIOSCIENCE CENTER",
            (sign_x + 5.0 * math.cos(front_theta) + 1.37 * front_nx,
             sign_y + 5.0 * math.sin(front_theta) + 1.37 * front_ny, 2.30),
            0.82, front_theta, facade, white)
canopy_center = front_length * 0.13
canopy_x = front_mid_x + canopy_center * math.cos(front_theta)
canopy_y = front_mid_y + canopy_center * math.sin(front_theta)
box("BIND_entry_canopy", (canopy_x + front_nx * 1.0, canopy_y + front_ny * 1.0, 4.0),
    (9.0, 2.6, 0.36), facade, frame, front_theta)
for i in (-1, 1):
    box(f"BIND_entry_canopy_support_{i}",
        (canopy_x + front_nx * 2.0 + i * 3.8 * math.cos(front_theta),
         canopy_y + front_ny * 2.0 + i * 3.8 * math.sin(front_theta), 2.0),
        (0.18, 0.18, 4.0), facade, frame, front_theta)

# A wider three-storey curtain-wall bay captures the architect-documented
# transparent research frontage; the measured bay width is unavailable.
atrium_center = front_length * 0.20
atrium_x = front_mid_x + atrium_center * math.cos(front_theta) + front_nx * 0.72
atrium_y = front_mid_y + atrium_center * math.sin(front_theta) + front_ny * 0.72
atrium_width = min(25.0, front_length * 0.70)
box("BIND_primary_three_storey_curtain_wall", (atrium_x, atrium_y, 6.0),
    (atrium_width, 0.08, 11.8), facade, glass, front_theta)
for i in range(6):
    offset = -atrium_width / 2 + atrium_width * i / 5
    box(f"BIND_primary_curtainwall_mullion_v{i+1}",
        (atrium_x + math.cos(front_theta) * offset + front_nx * 0.06,
         atrium_y + math.sin(front_theta) * offset + front_ny * 0.06, 6.0),
        (0.12, 0.14, 12.0), facade, frame, front_theta)
for i, z in enumerate((0.8, 4.55, 8.5, 11.8)):
    box(f"BIND_primary_curtainwall_transom_{i+1}",
        (atrium_x + front_nx * 0.08, atrium_y + front_ny * 0.08, z),
        (atrium_width, 0.14, 0.12), facade, frame, front_theta)

# Interpretive louver panels and restrained screen enclosures suggest the
# research-building services visible in architect photographs, without claiming
# an as-built roof plan.
for edge_no, a, b, length in facade_edges:
    if length < 12:
        continue
    theta = math.atan2(b[1] - a[1], b[0] - a[0])
    for floor_z in (2.0, 6.0, 10.0):
        if floor_z == 2.0:
            continue
        center = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        box(f"BIND_mechanical_louver_{edge_no}_{floor_z}",
            (center[0], center[1], floor_z), (min(length * 0.22, 8.0), 0.10, 0.8),
            facade, frame, theta)
for i, (xoff, yoff, w, d, h) in enumerate(((4, 2, 13, 7, 0.60), (-9, 12, 7, 5, 0.55), (13, -12, 8, 4.5, 0.55))):
    box(f"BIND_roof_plant_screen_{i+1}", (xoff, yoff, roof_z + h/2), (w, d, h), shells, plant)
for i, (xoff, yoff) in enumerate(((-13, -8), (0, -7), (13, -5), (-5, 13), (9, 14))):
    box(f"BIND_roof_vent_{i+1}", (xoff, yoff, roof_z + 0.30), (1.0, 0.9, 0.60), shells, frame)

# A small visible laboratory tableau represents research use, not an as-built room.
for floor_no, z in enumerate((1.05, 5.05, 9.05)):
    box(f"BIND_schematic_research_bench_{floor_no}", (0.0, 0.0, z), (5.4, 1.0, 0.14), interior, warm)
    for j, x in enumerate((-1.7, 0.0, 1.7)):
        box(f"BIND_schematic_lab_instrument_{floor_no}_{j}", (x, 0.0, z + 0.85),
            (0.52, 0.50, 1.35), interior, plant)

# Build a render rig with a front-oblique view perpendicular to the longest GIS
# facade guide and a top view for footprint inspection.
world = bpy.data.worlds.new("BIND review world")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.72, 0.76, 0.80, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.78
scene.world = world
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1440
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"

import mathutils


def look_at(obj, point):
    obj.rotation_euler = (mathutils.Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, location, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new(name, data)
    rig.objects.link(obj)
    obj.location = location
    look_at(obj, (0, 0, 6.0))


def camera(name, location, target, ortho):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    rig.objects.link(obj)
    obj.location = location
    data.type = "ORTHO"
    data.ortho_scale = ortho
    look_at(obj, target)
    return obj


area_light("BIND_key_light", (45, -110, 75), 6500, 65)
area_light("BIND_fill_light", (-70, 40, 45), 3400, 55)
front_n = (front_nx, front_ny)
camera("BIND_overview_camera",
       (front_mid_x + front_n[0] * 175 + front_length * 0.20 * math.cos(front_theta),
        front_mid_y + front_n[1] * 175 + front_length * 0.20 * math.sin(front_theta), 36),
       (0, 0, 6.5), 132)
camera("BIND_plan_camera", (0, 0, 220), (0, 0, 6), 170)
camera("BIND_entry_camera",
       (sign_x + front_n[0] * 67 + 14 * math.cos(front_theta),
        sign_y + front_n[1] * 67 + 14 * math.sin(front_theta), 16),
       (sign_x, sign_y, 4.2), 64)

ASSET_FILE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
print(json.dumps({
    "asset_file": ASSET_FILE.relative_to(ROOT).as_posix(),
    "collection": COLLECTION_NAME,
    "gis_feature": attributes["FID"],
    "footprint_vertices": len(footprint),
    "facade_guide_vertices": len(facade_points),
    "gis_local_ring_area_m2": round(abs(twice_area) / 2, 2),
    "polygon_centroid_local_m": [0, 0],
    "placement_origin_xy_m": [round(centroid_x, 6), round(centroid_y, 6)],
    "primary_facade_run_m": round(front_length, 2),
    "mesh_object_count": sum(1 for obj in asset.all_objects if obj.type == "MESH"),
    "estimated_eave_height_m": eave_z,
}, indent=2))
