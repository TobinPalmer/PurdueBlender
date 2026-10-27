"""Build the detailed, portable UPOF building library from its dedicated evidence.

The exported mesh is in local meters.  Campus placement stays with the master
Placement_<id> marker.  The ArcGIS polygon in this file is the service's UPOF
FID 296 geometry converted to the project's approximate local tangent frame.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector


BUILDING_ID = "massing_utility_plant_office_facility_e219ef5"
ASSET_COLLECTION = f"Asset_{BUILDING_ID}"
SCENE_NAME = f"Building_{BUILDING_ID}"
ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
AUDIT_DIR = ROOT / "audit" / "utility_plant_office_facility"
PREVIEW_DIR = AUDIT_DIR / "previews"

# Purdue BuildingShapes service feature 296 (UPOF), requested with outSR=4326.
# Points were converted using the repository's specified local approximation.
PLACEMENT_ORIGIN_XY_M = (105.20840981346892, -1052.103607498187)
WGS84_ORIGIN = (40.4274, -86.9137)
GIS_FEATURE_ID = 296
GIS_POLYGON_LOCAL_XY_M = [
    (113.535, -1063.907), (95.869, -1064.019),
    (95.686, -1040.262), (113.368, -1040.074),
    (113.458, -1048.673), (116.507, -1048.633),
    (116.548, -1054.235), (116.405, -1054.253),
    (116.394, -1056.939), (113.533, -1056.967),
]
POLY = [(x - PLACEMENT_ORIGIN_XY_M[0], y - PLACEMENT_ORIGIN_XY_M[1])
        for x, y in GIS_POLYGON_LOCAL_XY_M]

WALL_TOP = 6.88
ROOF_TOP = 7.17
PARAPET_TOP = 7.32  # about 24 ft total, inferred from GIS Extrution=24
FLOOR_LEVELS = (0.0, 3.40, 6.88)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections, bpy.data.materials, bpy.data.cameras,
                       bpy.data.lights, bpy.data.meshes, bpy.data.curves):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    for child in list(scene.collection.children):
        scene.collection.children.unlink(child)
    root = bpy.data.collections.new("UPOF_Utility_Office_Facility")
    scene.collection.children.link(root)
    return scene, root


def make_material(name, color, roughness=0.72, metallic=0.0, noise_scale=150.0,
                  bump_strength=0.1, bump_distance=0.025):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    texcoord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 2.0
    links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (*[c * 0.90 for c in color], 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (*[min(1.0, c * 1.07) for c in color], 1.0)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def link_object(obj, collection):
    collection.objects.link(obj)
    return obj


def cube(name, loc, dims, mat, collection, yaw=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler.z = yaw
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    link_object(obj, collection)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft edge highlights", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
    return obj


def make_ribbed_wall_material(name, base_color, axis):
    """Subtle painted-metal striations, aligned to one cardinal wall plane."""
    mat = make_material(name, base_color, 0.78, 0.16, 46, 0.09, 0.024)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    texcoord = next(n for n in nodes if n.type == "TEX_COORD")
    prior_bump = next(n for n in nodes if n.type == "BUMP")
    wave = nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = axis
    wave.inputs["Scale"].default_value = 80.0
    wave.inputs["Distortion"].default_value = 0.0
    wave.inputs["Detail"].default_value = 0.0
    links.new(texcoord.outputs["Generated"], wave.inputs["Vector"])
    ribs = nodes.new("ShaderNodeBump")
    ribs.inputs["Strength"].default_value = 0.28
    ribs.inputs["Distance"].default_value = 0.018
    links.new(wave.outputs["Color"], ribs.inputs["Height"])
    links.new(prior_bump.outputs["Normal"], ribs.inputs["Normal"])
    links.new(ribs.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def extruded_polygon(name, points, z0, z1, mat, collection, side_materials=None):
    n = len(points)
    verts = [(x, y, z) for z in (z0, z1) for x, y in points]
    faces = []
    faces.append(tuple(range(n - 1, -1, -1)))
    faces.append(tuple(range(n, 2 * n)))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    if side_materials:
        mesh.materials.append(side_materials[0])
        mesh.materials.append(side_materials[1])
        for i, a in enumerate(points):
            b = points[(i + 1) % len(points)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            mesh.polygons[2 + i].material_index = 1 if abs(dx) >= abs(dy) else 2
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    bevel = obj.modifiers.new("Crisp edge highlights", "BEVEL")
    bevel.width = 0.015
    bevel.segments = 1
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def facade_box(name, a, b, z, dims, mat, collection, outward=0.12, bevel=0.0):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    tx, ty = dx / length, dy / length
    # GIS ring is clockwise: its outward normal is the left-hand normal.
    nx, ny = -ty, tx
    midx, midy = (ax + bx) / 2 + nx * outward, (ay + by) / 2 + ny * outward
    yaw = math.atan2(ty, tx)
    return cube(name, (midx, midy, z), dims, mat, collection, yaw, bevel)


def make_window(edge_index, bay_index, floor_index, a, b, mats, collection):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length < 4.7:
        return
    tx, ty = dx / length, dy / length
    nx, ny = -ty, tx
    yaw = math.atan2(ty, tx)
    count = max(1, int(length // 2.9))
    segment = length / count
    floor_z = 0.0 if floor_index == 0 else 3.4
    sill = floor_z + (1.03 if floor_index == 0 else 0.93)
    height = 1.34
    width = min(1.72, segment * 0.64)
    for bay in range(count):
        t = (bay + 0.5) / count
        cx, cy = ax + dx * t + nx * 0.15, ay + dy * t + ny * 0.15
        zc = sill + height / 2
        # Deep, dark glass, pale metal perimeter frame and a strong transom.
        cube(f"Facade_W{edge_index:02d}_B{bay_index + bay:02d}_F{floor_index + 1}_frame",
             (cx, cy, zc), (width + 0.15, 0.10, height + 0.15), mats["frame"],
             collection, yaw, 0.025)
        cube(f"Facade_W{edge_index:02d}_B{bay_index + bay:02d}_F{floor_index + 1}_glazing",
             (cx, cy - ny * 0.058, zc), (width, 0.035, height), mats["glass"],
             collection, yaw, 0.012)
        cube(f"Facade_W{edge_index:02d}_B{bay_index + bay:02d}_F{floor_index + 1}_transom",
             (cx, cy - ny * 0.087, zc), (width, 0.025, 0.055), mats["frame"],
             collection, yaw, 0.004)
        if width > 1.3:
            cube(f"Facade_W{edge_index:02d}_B{bay_index + bay:02d}_F{floor_index + 1}_mullion",
                 (cx, cy - ny * 0.09, zc), (0.045, 0.028, height), mats["frame"],
                 collection, yaw, 0.004)


def add_text(name, body, loc, size, mat, collection, yaw=0.0):
    curve = bpy.data.curves.new(name + "Curve", "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.006
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (math.pi / 2, 0.0, yaw)
    if mat:
        obj.data.materials.append(mat)
    return obj


def create_building(scene, root):
    asset = bpy.data.collections.new(ASSET_COLLECTION)
    root.children.link(asset)
    interiors_1 = bpy.data.collections.new("Interior_Schematic_Floor_1_Unverified")
    interiors_2 = bpy.data.collections.new("Interior_Schematic_Floor_2_Unverified")
    asset.children.link(interiors_1)
    asset.children.link(interiors_2)

    mats = {
        "wall": make_material("Light gray industrial cladding estimate — facade unverified", (0.56, 0.58, 0.58), 0.82, 0.10, 42, 0.09, 0.025),
        "wall_x": make_ribbed_wall_material("Facade vertical ribs along east-west walls — estimated", (0.56, 0.58, 0.58), "X"),
        "wall_y": make_ribbed_wall_material("Facade vertical ribs along north-south walls — estimated", (0.56, 0.58, 0.58), "Y"),
        "base": make_material("Concrete plinth with subtle grain", (0.32, 0.34, 0.34), 0.92, 0.0, 80, 0.18, 0.045),
        "roof": make_material("Light galvanized standing-seam roof", (0.74, 0.78, 0.79), 0.38, 0.48, 90, 0.1, 0.018),
        "roof_edge": make_material("Roof trim aluminum", (0.56, 0.60, 0.62), 0.32, 0.65, 70, 0.08, 0.012),
        "frame": make_material("Warm gray aluminum window frames", (0.29, 0.31, 0.31), 0.38, 0.6, 120, 0.03, 0.008),
        "glass": make_material("Smoky blue-gray office glazing", (0.23, 0.36, 0.41), 0.14, 0.36, 100, 0.015, 0.004),
        "door": make_material("Dark bronze entrance doors", (0.19, 0.22, 0.23), 0.32, 0.48, 80, 0.02, 0.006),
        "concrete": make_material("Entry concrete", (0.58, 0.57, 0.52), 0.9, 0.0, 60, 0.1, 0.03),
        "partition": make_material("Schematic office partitions", (0.72, 0.73, 0.70), 0.9, 0.0, 30, 0.04, 0.01),
        "floor": make_material("Interior gray resilient flooring", (0.47, 0.48, 0.47), 0.9, 0.0, 100, 0.04, 0.008),
        "furniture": make_material("Office workstations", (0.36, 0.37, 0.36), 0.65, 0.0, 60, 0.04, 0.01),
        "label": make_material("Pale metal wayfinding lettering", (0.85, 0.84, 0.79), 0.36, 0.25, 80, 0.02, 0.004),
    }

    # Exterior wall shell carries the complete official GIS polygon. It is only
    # an extruded envelope; no wall heights are claimed as surveyed.
    extruded_polygon("UPOF_Office_Shell_Footprint_Verified_Extrusion_Estimated",
                     POLY, 0.0, WALL_TOP, mats["wall"], asset,
                     side_materials=(mats["wall_x"], mats["wall_y"]))
    extruded_polygon("UPOF_Roof_Deck_Light_Metal", POLY, WALL_TOP, ROOF_TOP,
                     mats["roof"], asset)
    extruded_polygon("UPOF_Flat_Roof_Surface", POLY, ROOF_TOP, ROOF_TOP + 0.035,
                     mats["roof"], asset)

    # Slightly raised perimeter coping supports the crisp, low roof silhouette.
    points = POLY
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        facade_box(f"Roof_Coping_{i + 1:02d}", a, b, (ROOF_TOP + PARAPET_TOP) / 2,
                   (math.dist(a, b) + 0.05, 0.17, PARAPET_TOP - ROOF_TOP),
                   mats["roof_edge"], asset, outward=0.02, bevel=0.025)

    # Fine east-west roof seams follow the high-resolution aerial orthomosaic.
    west = min(x for x, y in POLY)
    east = max(x for x, y in POLY)
    south = min(y for x, y in POLY)
    north = max(y for x, y in POLY)
    main_west = west + 0.22
    main_east = 113.39 - PLACEMENT_ORIGIN_XY_M[0] - 0.22
    seam_south = south + 0.24
    seam_north = north - 0.24
    for idx, y in enumerate([seam_south + 0.52 * i for i in range(int((seam_north - seam_south) / 0.52) + 1)]):
        cube(f"Roof_Standing_Seam_Main_EW_{idx + 1:02d}", ((main_west + main_east) / 2, y, ROOF_TOP + 0.055),
             (main_east - main_west, 0.025, 0.025), mats["roof_edge"], asset, bevel=0.006)
    annex_x0 = main_east + 0.3
    annex_x1 = east - 0.2
    annex_south = -1056.9 - PLACEMENT_ORIGIN_XY_M[1] + 0.18
    annex_north = -1048.7 - PLACEMENT_ORIGIN_XY_M[1] - 0.18
    if annex_x1 > annex_x0:
        for idx, y in enumerate([annex_south + 0.52 * i for i in range(int((annex_north - annex_south) / 0.52) + 1)]):
            cube(f"Roof_Standing_Seam_East_Projection_EW_{idx + 1:02d}",
                 ((annex_x0 + annex_x1) / 2, y, ROOF_TOP + 0.055),
                 (annex_x1 - annex_x0, 0.025, 0.025), mats["roof_edge"], asset, bevel=0.005)
    # The close aerial shows a nearly continuous ribbed roof. No distinct HVAC
    # cabinets or hatch are modeled because their identity is not verifiable.

    # Base-course and floor-level bands emphasize the two documented stories.
    for edge_index, a in enumerate(POLY):
        b = POLY[(edge_index + 1) % len(POLY)]
        length = math.dist(a, b)
        if length < 0.7:
            continue
        facade_box(f"Facade_Concrete_Base_{edge_index + 1:02d}", a, b, 0.32,
                   (length, 0.25, 0.64), mats["base"], asset, outward=0.18)
        facade_box(f"Facade_Floor_Belt_{edge_index + 1:02d}", a, b, 3.42,
                   (length, 0.12, 0.15), mats["roof_edge"], asset, outward=0.14)

    # OEP says the AED and main entry are on the east wall. F/G is the clear
    # east-facing plane of the east projection in the GIS outline.
    east_a, east_b = POLY[5], POLY[6]
    dx, dy = east_b[0] - east_a[0], east_b[1] - east_a[1]
    el = math.hypot(dx, dy)
    tangent = (dx / el, dy / el)
    outward = (-tangent[1], tangent[0])
    ex = (east_a[0] + east_b[0]) / 2 + outward[0] * 0.20
    ey = (east_a[1] + east_b[1]) / 2 + outward[1] * 0.20
    yaw = math.atan2(tangent[1], tangent[0])
    cube("Main_Entry_Concrete_Threshold", (ex, ey, 0.08), (3.7, 1.1, 0.16), mats["concrete"], asset, yaw, 0.045)
    cube("Main_Entry_Canopy", (ex - outward[0] * 0.35, ey - outward[1] * 0.35, 2.83),
         (3.2, 1.2, 0.16), mats["roof_edge"], asset, yaw, 0.03)
    for side, dxoff in (("L", -0.49), ("R", 0.49)):
        # side offsets are along the wall tangent
        cx, cy = ex + tangent[0] * dxoff, ey + tangent[1] * dxoff
        cube(f"Main_Entry_Door_{side}", (cx, cy, 1.12), (0.86, 0.11, 2.20), mats["door"], asset, yaw, 0.025)
        cube(f"Main_Entry_Glass_Lite_{side}", (cx, cy - outward[1] * 0.065, 1.47),
             (0.48, 0.035, 1.35), mats["glass"], asset, yaw, 0.012)
    for dxoff in (-1.22, 1.22):
        cube("Main_Entry_Sidelight", (ex + tangent[0] * dxoff, ey + tangent[1] * dxoff, 1.32),
             (0.33, 0.095, 1.78), mats["glass"], asset, yaw, 0.015)

    # Window bays, two floors, regular rhythm on the broad faces. Facade
    # materials and exact bay spacing are estimated because no elevations or
    # current close-range imagery were available.
    for edge_index, a in enumerate(POLY):
        b = POLY[(edge_index + 1) % len(POLY)]
        if math.dist(a, b) < 4.7:
            continue
        for floor_index in range(2):
            make_window(edge_index, 0, floor_index, a, b, mats, asset)

    # Small facade sign, placed on the long south-facing elevation. The name
    # plate is interpretive and kept unobtrusive rather than claiming a photo.
    south_edge = next((i for i, a in enumerate(POLY)
                       if POLY[(i + 1) % len(POLY)][1] < a[1] - 20.0), None)
    if south_edge is not None:
        a, b = POLY[south_edge], POLY[(south_edge + 1) % len(POLY)]
        midx, midy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        add_text("UPOF_Identification_Lettering", "UTILITY PLANT OFFICE FACILITY",
                 (midx - 3.6, midy - 0.25, 2.75), 0.25, mats["label"], asset,
                 yaw=math.atan2(b[1] - a[1], b[0] - a[0]))

    # Schematic interior: the published emergency plan confirms office use,
    # ground-floor restrooms at the southwest, second-floor Utility Engineering
    # and BAS staff, and no elevator. It does not provide full floor plans.
    floor_polygon = POLY
    for level, col in enumerate((interiors_1, interiors_2)):
        z = 0.0 if level == 0 else 3.4
        extruded_polygon(f"Schematic_Office_Floor_{level + 1}_Plan_Not_To_Scale",
                         floor_polygon, z + 0.04, z + 0.13, mats["floor"], col)
        cube(f"Schematic_Corridor_F{level + 1}", (0.0, 0.0, z + 0.18),
             (2.0, 17.0, 0.08), mats["floor"], col)
        # Generic private-office partitions and low cubicle banks, visibly
        # schematic so they cannot be mistaken for documented dimensions.
        for ix, x in enumerate((-6.0, -1.7, 2.6, 6.3)):
            cube(f"Schematic_Office_Partition_F{level + 1}_{ix + 1}",
                 (x, 2.9, z + 1.55), (0.11, 7.3, 2.9), mats["partition"], col)
        for iy, y in enumerate((-7.3, -4.3, -1.3, 2.0, 5.0, 8.0)):
            cube(f"Schematic_Cubicle_Bank_F{level + 1}_{iy + 1}",
                 (-4.0, y, z + 0.75), (3.2, 0.10, 1.15), mats["partition"], col)
            cube(f"Schematic_Cubicle_Bank_F{level + 1}_{iy + 1}_East",
                 (4.3, y, z + 0.75), (3.0, 0.10, 1.15), mats["partition"], col)
        for iy, y in enumerate((-6.0, -2.3, 1.4, 5.1, 8.8)):
            cube(f"Schematic_Workstation_F{level + 1}_{iy + 1}",
                 (-4.0, y, z + 0.90), (1.4, 0.68, 0.10), mats["furniture"], col, bevel=0.03)
            cube(f"Schematic_Workstation_F{level + 1}_{iy + 1}_R",
                 (4.4, y, z + 0.90), (1.4, 0.68, 0.10), mats["furniture"], col, bevel=0.03)
        if level == 0:
            # The two southwest restrooms are source-backed in location only.
            for ri, rx in enumerate((-7.3, -4.6)):
                ry = -9.0
                cube(f"Schematic_SW_Restroom_F1_{ri + 1}", (rx, ry, z + 1.25),
                     (2.3, 3.0, 2.5), mats["partition"], col)
        else:
            # Rooms are labels for use, not architectural room shapes.
            add_text("Schematic_Utility_Engineering_Label", "UTILITY ENGINEERING",
                     (-6.7, 7.5, z + 2.6), 0.22, mats["furniture"], col)
            add_text("Schematic_BAS_Console_Label", "BAS CONSOLE", (3.3, 7.5, z + 2.6),
                     0.22, mats["furniture"], col)

    # Keep all exported objects assigned only to the expected asset hierarchy.
    for obj in list(scene.objects):
        if not any(col == asset or col.name.startswith("Interior_Schematic") for col in obj.users_collection):
            for col in list(obj.users_collection):
                col.objects.unlink(obj)
            asset.objects.link(obj)
    return asset


def add_render_setup(scene):
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    world = bpy.data.worlds.new("UPOF neutral studio world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.20, 0.24, 0.28, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    scene.world = world

    sun_data = bpy.data.lights.new("Soft afternoon sun", "SUN")
    sun_data.energy = 2.1
    sun_data.angle = math.radians(12.0)
    sun = bpy.data.objects.new("Soft afternoon sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(28), math.radians(-20), math.radians(-32))

    area_data = bpy.data.lights.new("Facade fill", "AREA")
    area_data.energy = 2100
    area_data.shape = "DISK"
    area_data.size = 22
    area = bpy.data.objects.new("Facade fill", area_data)
    scene.collection.objects.link(area)
    area.location = (16, -23, 25)
    area.rotation_euler = (math.radians(25), 0.0, math.radians(30))

    camera_data = bpy.data.cameras.new("UPOF oblique review camera")
    camera = bpy.data.objects.new("UPOF oblique review camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (31, -39, 27)
    target = Vector((0.0, 0.0, 3.2))
    direction = target - Vector(camera.location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 45
    scene.camera = camera
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.camera.data.lens = 50
    return camera


def render_preview(scene, camera, target_path):
    scene.render.filepath = str(target_path)
    bpy.ops.render.render(write_still=True)


def main():
    scene, root = clear_scene()
    asset = create_building(scene, root)
    camera = add_render_setup(scene)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    # The saved scene is a portable library; render setup is retained in scene.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    render_preview(scene, camera, PREVIEW_DIR / "utility_plant_office_facility_oblique.png")
    # Top view preview, framed independently for checking the GIS plan silhouette.
    camera.location = (0.0, -0.5, 52.0)
    camera.rotation_euler = (0.0, 0.0, 0.0)
    camera.data.ortho_scale = 34.0
    camera.data.lens = 50
    scene.render.filepath = str(PREVIEW_DIR / "utility_plant_office_facility_plan.png")
    bpy.ops.render.render(write_still=True)
    # Reset saved review camera to the oblique position, then save its exact state.
    camera.location = (31, -39, 27)
    direction = Vector((0.0, 0.0, 3.2)) - Vector(camera.location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    records = {
        "building_id": BUILDING_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "export_collection": ASSET_COLLECTION,
        "scene": SCENE_NAME,
        "coordinate_frame": "local meters; X east, Y north, Z up; geometry points are relative to placement_origin_xy_m",
        "placement_origin_xy_m": list(PLACEMENT_ORIGIN_XY_M),
        "placement_origin_wgs84": [40.417925003534776, -86.91245948991464],
        "official_feature_id": GIS_FEATURE_ID,
        "official_identity": {
            "source_code": "UPOF",
            "source_name": "Utility Plant Office Facility",
            "source_address": "419 S Grant Street, West Lafayette, IN 47907",
            "source_global_id": "{951C189B-81B2-4E4F-B022-69690FFF495A}",
            "match_confidence": "exact official code, name, address and feature ID",
        },
        "footprint_measurements": {
            "source": "Purdue BuildingShapes ArcGIS FID 296, requested in EPSG:4326 and converted by the project tangent approximation",
            "retrieved": "2026-10-26",
            "width_east_west_m": 20.862,
            "depth_north_south_m": 23.945,
            "area_from_converted_outline_m2": 446.006,
            "perimeter_from_converted_outline_m": 88.989,
            "orientation_from_north_deg": 0.441,
            "validation": "shell base ring follows the GIS polygon vertices; fresh-open checker compares points against raw source geometry",
            "uncertainty": "Project tangent approximation is not survey-grade geodetic control.",
        },
        "wall_height_m": WALL_TOP,
        "roof_top_m": PARAPET_TOP,
        "height_status": "estimated; GIS Extrution=24 interpreted as feet, consistent with two office floors; no published elevation found",
        "height_uncertainty": {
            "GIS_Extrution_attribute": 24,
            "attribute_units_documented": False,
            "interpretation": "24 feet used only as an approximate two-floor total; model wall top 6.88 m, parapet top 7.32 m",
            "status": "estimated, not measured",
        },
        "floor_count": 2,
        "interior_status": "schematic only; emergency plan confirms office functions and southwest restrooms but no complete architectural plans were found",
        "entrance_and_program_evidence": "Purdue OEP BEP revised 2026-03-23: east-wall main entry, two floors, mostly cubicle office use, southwest first-floor restrooms, second-floor Utility Engineering/BAS functions, no elevator.",
        "footprint_status": "GIS polygon converted to local meters; the facade/structural-wall outline is interpreted from the primary building polygon",
        "material_status": "light-gray vertically ribbed industrial cladding is a restrained site-context estimate; roof is based on orthophoto",
        "roof_evidence": "Esri zoom-20 orthomosaic shows a bright, nearly continuous roof with east-west ribs; unsupported cabinets and hatch omitted.",
        "facade_evidence": "Purdue ECN image captioned 'from UPOF' shows nearby pale-gray ribbed utility cladding and a lower masonry/window section, but camera bearing and foreground-wall identity are undocumented. Facade/window layout remains estimated.",
        "portable_dependencies": "Procedural Blender materials only; no external texture files or absolute asset paths.",
        "integration_note": "Coordinator must place the master marker at placement_origin_xy_m; the previous massing AABB center is about 0.95 m east of this GIS centroid.",
        "objects_in_asset_collection": len(asset.all_objects),
    }
    (AUDIT_DIR / "build_evidence.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("UPOF_BUILD_COMPLETE", json.dumps(records, sort_keys=True))


if __name__ == "__main__":
    main()
