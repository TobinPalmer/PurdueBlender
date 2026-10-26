"""Rebuild the Bechtel Innovation Design Center library from Purdue GIS.

Run from any working directory with the project's Blender installation:
    blender --background --python build_bechtel_innovation_design_center_bidc.py

All building geometry uses a local frame centered at the source polygon
centroid. The campus instance remains controlled by Placement_<id> in the
shared master. Facade and rooftop detailing is identified as interpretive
where public sources do not provide elevations or dimensions.
"""
import bpy
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "bechtel_innovation_design_center_bidc"
ASSET_FILE = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
GIS_FILE = ROOT / "audit" / BUILDING_ID / "sources" / "gis_feature_912.json"
EVIDENCE_DIR = ROOT / "audit" / BUILDING_ID
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
GIS_FILE.parent.mkdir(parents=True, exist_ok=True)
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
LON_M = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
LAT_M = 111040.0

with GIS_FILE.open(encoding="utf-8") as source:
    gis = json.load(source)
feature = gis["feature"]
attributes = feature["attributes"]
assert attributes["FID"] == 912
assert attributes["BLDG_ABBR"] == "BIDC"
assert attributes["BUILDING_N"] == "Bechtel Innovation Design Center"
ring = feature["geometry"]["rings"][0]
xy = [((p[0] - ORIGIN_LON) * LON_M, (p[1] - ORIGIN_LAT) * LAT_M) for p in ring[:-1]]

twice_area = sum(xy[i][0] * xy[(i + 1) % len(xy)][1]
                 - xy[(i + 1) % len(xy)][0] * xy[i][1]
                 for i in range(len(xy)))
assert abs(twice_area) > 1.0
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

# Start from an empty scene so the saved library contains only this asset and a
# non-exported render rig. It does not read or save the campus master.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    bpy.data.collections.remove(collection)
scene = bpy.context.scene
asset = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset)
asset["building_id"] = BUILDING_ID
asset["source_feature_id"] = 912
asset["local_frame"] = "polygon centroid; metres; X east, Y north, Z up"
structure = bpy.data.collections.new("BIDC_Structure")
facade = bpy.data.collections.new("BIDC_Facade")
roof = bpy.data.collections.new("BIDC_Roof")
for collection in (structure, facade, roof):
    asset.children.link(collection)
rig = bpy.data.collections.new("Preview_Rig_not_for_export")
scene.collection.children.link(rig)


def material(name, color, roughness=0.72, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, alpha)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (*color, alpha)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        mat.blend_method = "BLEND"
        shader.inputs["Alpha"].default_value = alpha
    return mat


brick = material("BIDC | light gray insulated metal panel cladding", (0.57, 0.60, 0.61), 0.70, 0.22)
stone = material("BIDC | pale cast stone base and bands", (0.63, 0.59, 0.52), 0.75)
glass = material("BIDC | muted blue gray glazing", (0.25, 0.39, 0.43), 0.18, 0.18, 0.58)
metal = material("BIDC | charcoal curtain wall framing", (0.045, 0.065, 0.075), 0.35, 0.64)
roof_mat = material("BIDC | charcoal low slope roof", (0.15, 0.17, 0.18), 0.83)
equipment = material("BIDC | neutral gray roof equipment", (0.40, 0.43, 0.43), 0.72, 0.12)
interior = material("BIDC | warm workshop interior (schematic)", (0.56, 0.43, 0.29), 0.76)


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
    count = len(points)
    verts = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count)
                 for i in range(count))
    return mesh_object(name, verts, faces, collection, mat)


def box(name, center, size, collection, mat, angle=0.0):
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
    return obj


# The explicit footprint ring from Purdue feature 912 controls every envelope
# corner; its centroid agrees with the established manifest placement origin.
base_z = 0.0
roof_z = 10.8  # visual estimate only; GIS Elevation is 0 and Extrution is a legacy field.
ground_floor_top = 4.55
second_floor_top = 9.55
prism("BIDC_GIS_primary_shell", footprint, base_z, roof_z - 0.45, structure, brick)
prism("BIDC_stone_base", footprint, base_z, 0.42, facade, stone)
prism("BIDC_roof_slab", footprint, roof_z - 0.55, roof_z, roof, roof_mat)

# Traceable band heights encode two above-ground floors (plus the published
# basement plan); exact floor-to-floor dimensions were not found.
for z, width, depth in ((ground_floor_top, 0.17, 0.10), (second_floor_top, 0.17, 0.10)):
    for i, a in enumerate(footprint):
        b = footprint[(i + 1) % len(footprint)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 0.25:
            continue
        theta = math.atan2(dy, dx)
        box(f"BIDC_floor_band_{z:.2f}_{i:02d}",
            ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z),
            (length + 0.02, depth, width), facade, stone, theta)

# Window bays and dark metal mullions follow each source-ring wall. Modules are
# schematic facade rhythm; horizontal widths/heights are not surveyed.
for edge_index, a in enumerate(footprint):
    b = footprint[(edge_index + 1) % len(footprint)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 4.2:
        continue
    theta = math.atan2(dy, dx)
    outward_side = -area_sign
    nx = outward_side * (-math.sin(theta))
    ny = outward_side * math.cos(theta)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    bays = max(1, int(length / 2.4))
    base_bay_width = (length / bays) * 0.84
    is_south = (dy > -0.1 and dy < 0.1 and (a[1] + b[1]) / 2 < -12)
    for floor, (bottom, top) in enumerate(((0.72, 4.30), (4.85, 9.70)), start=1):
        for bay in range(bays):
            bay_width = base_bay_width
            along = -length / 2 + length * (bay + 0.5) / bays
            cx, cy = mx + along * math.cos(theta), my + along * math.sin(theta)
            if is_south and abs(along) < min(7.0, length * 0.24):
                # The glazed makerspace entrance is a larger, two storey cue
                # documented by the architect and Purdue project photography.
                if floor == 2:
                    continue
                bottom, top = 0.55, 8.70
                bay_width = min(13.2 / bays, length / bays * 0.90)
                glazing = glass
            else:
                glazing = glass if floor == 1 else glass
            surface = 0.065
            box(f"BIDC_glazing_{edge_index:02d}_{floor}_{bay:02d}",
                (cx + nx * surface, cy + ny * surface, (bottom + top) / 2),
                (bay_width, 0.055, top - bottom), facade, glazing, theta)
            # Vertical framing is spaced at the same evidence-limited bay rhythm.
            box(f"BIDC_mullion_{edge_index:02d}_{floor}_{bay:02d}",
                (cx + nx * (surface + 0.05), cy + ny * (surface + 0.05), (bottom + top) / 2),
                (0.075, 0.11, top - bottom + 0.10), facade, metal, theta)

# A clearly labeled interpretive makerspace tableau sits behind the transparent
# entrance. It represents use, not an as-built room schedule or equipment plan.
box("BIDC_schematic_workshop_bench", (0.0, -7.2, 1.72), (5.4, 1.05, 0.16), facade, interior)
for i, x in enumerate((-1.8, 0.0, 1.8)):
    box(f"BIDC_schematic_tool_silhouette_{i+1}", (x, -7.2, 2.35), (0.62, 0.58, 1.08), facade, equipment)

# Low-slope parapet and a restrained roof mechanical zone; equipment dimensions
# and arrangement are interpretive pending an as-built roof plan.
for i, a in enumerate(footprint):
    b = footprint[(i + 1) % len(footprint)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length > 0.25:
        box(f"BIDC_roof_parapet_{i:02d}", ((a[0]+b[0])/2, (a[1]+b[1])/2, roof_z + 0.22),
            (length + 0.10, 0.34, 0.44), roof, roof_mat, math.atan2(dy, dx))
box("BIDC_rooftop_plant_schematic", (2.0, 2.0, roof_z + 0.82), (8.5, 4.8, 1.2), roof, equipment)
for i in range(4):
    box(f"BIDC_rooftop_vent_{i+1}", (-8.0 + i * 4.4, 7.5, roof_z + 0.6),
        (0.55, 0.55, 0.8), roof, metal)

# Render rig is outside the exported asset collection.
world = bpy.data.worlds.new("BIDC review world")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.72, 0.76, 0.79, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.75
scene.world = world
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"


def look_at(obj, point):
    obj.rotation_euler = (mathutils.Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


import mathutils

def camera(name, location, target, ortho, filename):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    rig.objects.link(obj)
    obj.location = location
    data.type = "ORTHO"
    data.ortho_scale = ortho
    look_at(obj, target)
    scene.camera = obj
    scene.render.filepath = str(EVIDENCE_DIR / filename)


def area_light(name, location, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new(name, data)
    rig.objects.link(obj)
    obj.location = location
    look_at(obj, (0, 0, 4.5))


area_light("BIDC_key_light", (16, -32, 31), 4500, 23)
area_light("BIDC_fill_light", (-26, -2, 18), 2800, 19)
camera("BIDC_overview_camera", (47, -54, 38), (0, 0, 5), 63,
       "overview.png")
bpy.ops.render.render(write_still=True)
camera("BIDC_plan_camera", (0, 0, 85), (0, 0, 4), 52,
       "plan.png")
bpy.ops.render.render(write_still=True)

# Save the library with the expected collection and no external image links.
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
ASSET_FILE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
print(json.dumps({
    "asset_file": ASSET_FILE.relative_to(ROOT).as_posix(),
    "collection": COLLECTION_NAME,
    "gis_feature": attributes["FID"],
    "vertices": len(footprint),
    "gis_area_m2": round(abs(twice_area) / 2, 2),
    "polygon_centroid_local_m": [0, 0],
    "placement_origin_xy_m": [round(centroid_x, 6), round(centroid_y, 6)],
    "building_object_count": sum(1 for obj in asset.all_objects if obj.type == "MESH"),
    "estimated_roof_height_m": roof_z,
    "render_overview": "audit/" + BUILDING_ID + "/overview.png",
    "render_plan": "audit/" + BUILDING_ID + "/plan.png",
}, indent=2))
