"""Build the source-backed Phi Delta Theta massing asset.

The plan comes from Purdue BuildingShapes FID 796 (SOFDH, 503 State St).
Facade and roof silhouette are conservative interpretations of the chapter's
2017 street photograph; all heights are explicitly estimates.
Run with Blender 5.2+: blender --background --python this_file.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ID = "massing_phi_delta_theta_258cddd"
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
GIS = ROOT / "audit" / ID / "sources" / "purdue_gis_fid_796_current.json"
EVIDENCE = ROOT / "audit" / ID / "build_result.json"
RENDERS = ROOT / "audit" / ID / "renders"
SCENE_NAME = "Building_massing_phi_delta_theta_258cddd"
COLLECTION_NAME = "Asset_massing_phi_delta_theta_258cddd"
OBJECT_NAME = "Phi Delta Theta"


def xy_from_wgs84(lon: float, lat: float) -> tuple[float, float]:
    # Repository local campus approximation; explicitly not a surveyed CRS.
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def mat(name: str, color: tuple[float, float, float, float], roughness=0.78):
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def move_to_asset(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    asset.objects.link(obj)
    return obj


def cube(name, loc, dims, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft masonry arris", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return move_to_asset(o)


def cylinder(name, loc, radius, depth, material, vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    return move_to_asset(o)


def polygon_extrusion(points, levels, name, materials):
    """Create a watertight footprint extrusion with one ring per height band."""
    n = len(points)
    verts = [(x, y, z) for z in levels for x, y in points]
    faces, face_mats = [], []
    for band in range(len(levels) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((band * n + i, band * n + j,
                          (band + 1) * n + j, (band + 1) * n + i))
            face_mats.append(0 if band < 2 else 1)
    faces.append(tuple((len(levels) - 1) * n + i for i in range(n)))
    face_mats.append(2)
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for m in materials:
        mesh.materials.append(m)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name, mesh)
    asset.objects.link(ob)
    # Material assignments survive face-normal recalculation by polygon order.
    for idx, poly in enumerate(mesh.polygons):
        if idx < (len(levels) - 1) * n:
            poly.material_index = face_mats[idx]
        else:
            poly.material_index = 2
    return ob


def triangle_mesh(name, coords, material):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(coords, [], [(0, 1, 2)])
    mesh.materials.append(material)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    asset.objects.link(ob)
    return ob


def gable_roof(name, x0, x1, y0, y1, eave, ridge, axis, roof_mat, siding_mat):
    """Two roof planes and end gables. Ridge axis is x or y."""
    thick = 0.28
    if axis == "y":  # roof ridge extends into the site; south end has a gable
        cx = (x0 + x1) / 2
        top = [(x0, y0, eave), (cx, y0, ridge), (x1, y0, eave),
               (x0, y1, eave), (cx, y1, ridge), (x1, y1, eave)]
        faces = [(0, 1, 4, 3), (1, 2, 5, 4)]
        # End-gable triangles are surface fills on both short ends.
        triangle_mesh(name + "_South_Gable", [top[0], top[2], (cx, y0, ridge)], siding_mat)
        triangle_mesh(name + "_North_Gable", [top[3], (cx, y1, ridge), top[5]], siding_mat)
        cube(name + "_South_Fascia", (cx, y0 - 0.12, eave), (x1 - x0, 0.22, 0.32), trim)
        cube(name + "_North_Fascia", (cx, y1 + 0.12, eave), (x1 - x0, 0.22, 0.32), trim)
    else:
        cy = (y0 + y1) / 2
        top = [(x0, y0, eave), (x0, cy, ridge), (x0, y1, eave),
               (x1, y0, eave), (x1, cy, ridge), (x1, y1, eave)]
        faces = [(0, 1, 4, 3), (1, 2, 5, 4)]
        triangle_mesh(name + "_West_Gable", [top[0], top[2], (x0, cy, ridge)], siding_mat)
        triangle_mesh(name + "_East_Gable", [top[3], (x1, cy, ridge), top[5]], siding_mat)
        cube(name + "_West_Fascia", (x0 - 0.12, cy, eave), (0.22, y1 - y0, 0.32), trim)
        cube(name + "_East_Fascia", (x1 + 0.12, cy, eave), (0.22, y1 - y0, 0.32), trim)
    mesh = bpy.data.meshes.new(name + "_planes_mesh")
    mesh.from_pydata(top, [], faces)
    mesh.materials.append(roof_mat)
    mesh.update()
    ob = bpy.data.objects.new(name + "_Roof_Planes", mesh)
    asset.objects.link(ob)
    return ob


def window_south(prefix, x, y, z, width=1.62, height=1.68, shutters=False):
    # South-facing elevations lie at negative Y.
    pane = cube(prefix + "_glass", (x, y - 0.07, z), (width - 0.23, 0.08, height - 0.23), glass)
    pane["role"] = "photo-backed window opening; trim and pane are surface detail"
    cube(prefix + "_frame_L", (x - width / 2 + 0.06, y - 0.14, z), (0.12, 0.18, height), trim)
    cube(prefix + "_frame_R", (x + width / 2 - 0.06, y - 0.14, z), (0.12, 0.18, height), trim)
    cube(prefix + "_sill", (x, y - 0.16, z - height / 2 + 0.04), (width + 0.16, 0.28, 0.13), trim)
    cube(prefix + "_lintel", (x, y - 0.14, z + height / 2 - 0.04), (width, 0.18, 0.12), trim)
    cube(prefix + "_mullion_v", (x, y - 0.18, z), (0.07, 0.10, height - 0.16), trim)
    cube(prefix + "_mullion_h", (x, y - 0.18, z), (width - 0.15, 0.10, 0.07), trim)
    if shutters:
        for side in (-1, 1):
            cube(prefix + f"_shutter_{side}", (x + side * (width / 2 + 0.17), y - 0.12, z),
                 (0.22, 0.12, height * 0.9), shutter)


def window_north(prefix, x, y, z, width=1.62, height=1.68, shutters=False):
    # The State Street frontage is on the north side of this parcel.
    cube(prefix + "_glass", (x, y + 0.07, z), (width - 0.23, 0.08, height - 0.23), glass)
    cube(prefix + "_frame_L", (x - width / 2 + 0.06, y + 0.14, z), (0.12, 0.18, height), trim)
    cube(prefix + "_frame_R", (x + width / 2 - 0.06, y + 0.14, z), (0.12, 0.18, height), trim)
    cube(prefix + "_sill", (x, y + 0.16, z - height / 2 + 0.04), (width + 0.16, 0.28, 0.13), trim)
    cube(prefix + "_lintel", (x, y + 0.14, z + height / 2 - 0.04), (width, 0.18, 0.12), trim)
    cube(prefix + "_mullion_v", (x, y + 0.18, z), (0.07, 0.10, height - 0.16), trim)
    cube(prefix + "_mullion_h", (x, y + 0.18, z), (width - 0.15, 0.10, 0.07), trim)
    if shutters:
        for side in (-1, 1):
            cube(prefix + f"_shutter_{side}", (x + side * (width / 2 + 0.17), y + 0.12, z),
                 (0.22, 0.12, height * 0.9), shutter)


def window_east(prefix, x, y, z, width=1.55, height=1.68):
    # East-end feature wall faces +X; width runs north-south.
    cube(prefix + "_glass", (x + 0.07, y, z), (0.08, width - 0.22, height - 0.22), glass)
    for side in (-1, 1):
        cube(prefix + f"_frame_{side}", (x + 0.14, y + side * (width / 2 - 0.06), z), (0.18, 0.12, height), trim)
    cube(prefix + "_sill", (x + 0.17, y, z - height / 2 + 0.04), (0.28, width + 0.16, 0.13), trim)
    cube(prefix + "_lintel", (x + 0.14, y, z + height / 2 - 0.04), (0.18, width, 0.12), trim)
    cube(prefix + "_mullion_v", (x + 0.18, y, z), (0.10, 0.07, height - 0.16), trim)


def text_on_south(name, body, x, y, z, size, material):
    cu = bpy.data.curves.new(name + "_curve", "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"
    cu.extrude = 0.014
    ob = bpy.data.objects.new(name, cu)
    ob.location = (x, y, z)
    ob.rotation_euler = (math.pi / 2, 0.0, 0.0)
    ob.data.materials.append(material)
    asset.objects.link(ob)
    return ob


def text_on_north(name, body, x, y, z, size, material):
    cu = bpy.data.curves.new(name + "_curve", "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"
    cu.extrude = 0.014
    ob = bpy.data.objects.new(name, cu)
    ob.location = (x, y, z)
    # Local +Z becomes world +Y and local +Y stays vertical.
    ob.rotation_euler = (math.pi / 2, 0.0, math.pi)
    ob.data.materials.append(material)
    asset.objects.link(ob)
    return ob


def text_on_east(name, body, x, y, z, size, material):
    cu = bpy.data.curves.new(name + "_curve", "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"
    cu.extrude = 0.014
    ob = bpy.data.objects.new(name, cu)
    ob.location = (x, y, z)
    ob.rotation_euler = (math.pi / 2, 0.0, math.pi / 2)
    ob.data.materials.append(material)
    asset.objects.link(ob)
    return ob


def add_column(x, y, base_z=0.32, top_z=7.35):
    h = top_z - base_z
    cylinder(f"Portico_Column_{x:.2f}_Shaft", (x, y, base_z + h / 2), 0.31, h, trim, 24)
    cube(f"Portico_Column_{x:.2f}_Base", (x, y, base_z + 0.20), (0.86, 0.86, 0.40), trim, 0.04)
    cylinder(f"Portico_Column_{x:.2f}_Neck", (x, y, top_z - 0.08), 0.48, 0.16, trim, 24)
    cube(f"Portico_Column_{x:.2f}_Capital", (x, y, top_z - 0.27), (1.06, 1.06, 0.30), trim, 0.04)


def setup_render(center, camera_offset, path, ortho=62):
    scene = bpy.context.scene
    setup = bpy.data.collections.new("Temporary_Render_Setup")
    scene.collection.children.link(setup)
    cdata = bpy.data.cameras.new("PreviewCamera")
    camera = bpy.data.objects.new("PreviewCamera", cdata)
    setup.objects.link(camera)
    target = Vector(center)
    camera.location = target + Vector(camera_offset)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    cdata.type = "ORTHO"
    cdata.ortho_scale = ortho
    scene.camera = camera
    light_data = bpy.data.lights.new("Key", "AREA")
    light = bpy.data.objects.new("Key", light_data)
    setup.objects.link(light)
    light.location = (83, -455, 52)
    light_data.energy = 4200
    light_data.size = 36
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("PhiDeltaThetaWorld")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.58, 0.64, 0.72, 1.0)
    background.inputs["Strength"].default_value = 0.75
    return setup


# Build from scratch so this asset contains only the named building collection.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(COLLECTION_NAME)
scene.collection.children.link(asset)

brick = mat("PhiDelt_RedBrick", (0.30, 0.085, 0.055, 1))
upper = mat("Painted_White_Siding", (0.82, 0.80, 0.73, 1))
trim = mat("Classical_White_Trim", (0.94, 0.91, 0.82, 1))
roof = mat("Slate_Charcoal_Roof", (0.105, 0.12, 0.15, 1))
glass = mat("Window_Glass", (0.12, 0.18, 0.23, 1), 0.24)
shutter = mat("Deep_Maroon_Shutters", (0.13, 0.045, 0.05, 1))
dark = mat("Door_Deep_Blue", (0.04, 0.09, 0.16, 1))

doc = json.loads(GIS.read_text(encoding="utf-8-sig"))
feature = doc["features"][0]
attrs = feature["attributes"]
assert attrs["FID"] == 796 and attrs["BUILDING_N"] == "Phi Delta Theta" and attrs["ADDRESS"] == "503 State St"
ring = feature["geometry"]["rings"][0]
points = [xy_from_wgs84(lon, lat) for lon, lat in ring[:-1]]
footprint_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in (0, 1)]

# Height levels are photo-based estimates; the GIS does not measure height.
wall_levels = [0.0, 3.55, 7.05, 10.15]
shell = polygon_extrusion(points, wall_levels, OBJECT_NAME, [brick, upper, roof])
shell["source_feature"] = "Purdue BuildingShapes FID 796, SOFDH, 503 State St"
shell["footprint_method"] = "Exact source ring transformed with repository local campus approximation"
shell["height_status"] = "Estimated from chapter street photograph; no elevation drawing or survey found"
shell["floor_count_estimate"] = 3

# Masses interpreted from the oblique chapter photograph and the official plan.
# These roof rectangles sit inside the source shell, except small photographic overhangs.
gable_roof("West_Wing", 67.75, 91.10, -412.55, -400.55, 10.15, 13.20, "x", roof, upper)
gable_roof("Central_Pavilion", 91.0, 105.45, -414.0, -392.98, 10.15, 13.15, "x", roof, brick)
gable_roof("East_Wing", 105.45, 110.40, -408.0, -393.05, 10.15, 12.55, "x", roof, upper)

# West wing north/street elevation: residential windows follow the photographed rhythm.
front_y = -400.42
for floor, z in enumerate((1.75, 5.15, 8.65), 1):
    for i, x in enumerate((77.1, 81.0, 85.0, 88.5), 1):
        window_north(f"West_Facade_F{floor}_W{i}", x, front_y, z,
                     width=1.65 if floor < 3 else 1.50,
                     height=1.78 if floor < 3 else 1.55,
                     shutters=floor == 3)

# East-side wing windows plus visible vertical fraternity mark.
east_x = 110.50
for floor, z in enumerate((1.75, 5.15, 8.65), 1):
    for i, y in enumerate((-397.0, -402.0, -406.0), 1):
        window_east(f"East_End_F{floor}_W{i}", east_x, y, z)
text_on_east("Phi_Delta_Theta_Wall_Mark_1", "PHI", east_x + 0.22, -402.5, 7.9, 1.05, trim)
text_on_east("Phi_Delta_Theta_Wall_Mark_2", "DELTA", east_x + 0.22, -402.5, 6.7, 0.78, trim)
text_on_east("Phi_Delta_Theta_Wall_Mark_3", "THETA", east_x + 0.22, -402.5, 5.55, 0.74, trim)

# Main portico and pediment are supported by the source photograph, but exact sizes remain estimated.
portico_center = 100.80
portico_width = 12.5
portico_y = -391.78
for i, x in enumerate((94.8, 97.8, 100.8, 103.8, 106.8), 1):
    add_column(x, portico_y)
cube("Portico_Entablature", (portico_center, portico_y + 0.02, 7.43), (portico_width + 1.2, 1.25, 0.78), trim, 0.06)
cube("Portico_Balcony_Deck", (portico_center, -392.55, 7.95), (portico_width + 1.5, 2.0, 0.28), trim)
cube("Portico_Balustrade_Top", (portico_center, -391.58, 8.75), (portico_width, 0.22, 0.18), trim)
cube("Portico_Balustrade_Base", (portico_center, -391.58, 8.1), (portico_width, 0.24, 0.16), trim)
for i in range(17):
    x = portico_center - portico_width / 2 + 0.30 + i * (portico_width - 0.60) / 16
    cube(f"Portico_Baluster_{i+1:02d}", (x, -391.58, 8.42), (0.10, 0.12, 0.56), trim, 0.025)

# Front facing pediment triangle and white cornice/gable outline.
ped_y = -390.25
ped_x0, ped_x1, ped_base, ped_peak = portico_center - portico_width / 2, portico_center + portico_width / 2, 9.82, 13.15
triangle_mesh("Portico_Pediment_Infill", [(ped_x0, ped_y, ped_base), (ped_x1, ped_y, ped_base), (portico_center, ped_y, ped_peak)], brick)
cube("Pediment_Base_Cornice", (portico_center, ped_y - 0.10, ped_base), (portico_width + 0.50, 0.36, 0.35), trim)
for side in (-1, 1):
    # sloped cornice beam along each pediment rake
    dx = portico_width / 2
    dz = ped_peak - ped_base
    length = math.hypot(dx, dz)
    beam = cube(f"Pediment_Rake_{side}", (portico_center + side * dx / 2, ped_y - 0.14, ped_base + dz / 2), (length, 0.32, 0.25), trim)
    # Local +X points up the left rake and down the right rake.
    beam.rotation_euler[1] = side * math.atan2(dz, dx)
vent = cylinder("Pediment_Round_Vent", (portico_center, ped_y - 0.20, 11.20), 0.55, 0.10, trim, 32)
vent.rotation_euler[0] = math.pi / 2

# Door and sidelights recessed into the State Street projection.
door_y = -392.98
cube("Main_Entry_Door", (portico_center, door_y + 0.10, 1.58), (1.75, 0.18, 3.16), dark, 0.04)
for side in (-1, 1):
    cube(f"Main_Entry_Sidelight_{side}", (portico_center + side * 1.13, door_y + 0.15, 1.72), (0.40, 0.12, 2.35), glass)
    cube(f"Main_Entry_Pilaster_{side}", (portico_center + side * 1.48, door_y + 0.20, 1.8), (0.19, 0.24, 3.4), trim)
cube("Main_Entry_Transom", (portico_center, door_y + 0.16, 3.05), (2.45, 0.14, 0.20), trim)
text_on_north("PHI_DELTA_THETA_ENTABLATURE", "PHI DELTA THETA", portico_center, -390.98, 8.20, 0.57, brick)

# North-front window group around the portico on the central section.
for floor, z in enumerate((1.75, 5.10, 8.78), 1):
    for i, x in enumerate((93.3, 96.0, 105.6, 108.2), 1):
        window_north(f"Central_Facade_F{floor}_W{i}", x, -392.98, z,
                     width=1.55, height=1.70, shutters=floor == 3)

# White horizontal cornices and roofline trim on the main visible street elevations.
cube("West_Front_First_Floor_Belt", (79.4, -400.20, 3.63), (23.0, 0.28, 0.22), trim)
cube("West_Front_Second_Floor_Belt", (79.4, -400.20, 7.14), (23.0, 0.28, 0.24), trim)
cube("West_Front_Eave_Cornice", (79.4, -400.15, 10.00), (23.4, 0.50, 0.34), trim)

# Settings for a clean default save and compact preview renders.
for o in bpy.context.selected_objects:
    o.select_set(False)
center = (89.0, -402.5, 6.7)
setup = setup_render(center, (8, 75, 22), RENDERS / "01_street_facade.png", 62)
bpy.ops.render.render(write_still=True)
scene.render.filepath = str(RENDERS / "02_north_elevation.png")
setup.objects["PreviewCamera"].location = Vector((90, -322, 15.5))
setup.objects["PreviewCamera"].rotation_euler = (Vector((89, -405, 7.5)) - setup.objects["PreviewCamera"].location).to_track_quat("-Z", "Y").to_euler()
setup.objects["PreviewCamera"].data.type = "ORTHO"
setup.objects["PreviewCamera"].data.ortho_scale = 63
bpy.ops.render.render(write_still=True)
scene.render.filepath = str(RENDERS / "03_plan.png")
setup.objects["PreviewCamera"].location = Vector((89, -405, 105))
setup.objects["PreviewCamera"].rotation_euler = (Vector((89, -405, 0)) - setup.objects["PreviewCamera"].location).to_track_quat("-Z", "Y").to_euler()
setup.objects["PreviewCamera"].data.type = "ORTHO"
setup.objects["PreviewCamera"].data.ortho_scale = 56
bpy.ops.render.render(write_still=True)

# Remove temporary cameras/lights from the deliverable and save the portable library.
for o in list(setup.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(setup)
scene.camera = None
scene.render.filepath = "//"
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

# Capture post-build geometric evidence for an independent grader.
xy_bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in (0, 1)]
evidence = {
    "building_id": ID,
    "asset_path": "modular/buildings/" + ASSET.name,
    "collection": COLLECTION_NAME,
    "scene": SCENE_NAME,
    "source_feature": {
        "provider": "Purdue BuildingShapes ArcGIS FeatureServer, layer 0",
        "fid": attrs["FID"], "name": attrs["BUILDING_N"], "abbreviation": attrs["BLDG_ABBR"],
        "address": attrs["ADDRESS"], "owner": attrs["OWNER"], "source_crs": "EPSG:4326",
        "geometry_vertices_including_close": len(ring), "source_area_field": attrs["Shape__Area"],
        "source_perimeter_field": attrs["Shape__Length"],
        "local_conversion": "X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040",
        "local_xy_bounds_m": xy_bounds,
    },
    "model": {
        "export_objects": len(asset.objects), "wall_levels_m": wall_levels,
        "estimated_stories": 3, "estimated_eave_m": 10.15, "estimated_roof_peaks_m": [12.55, 13.15, 13.20],
        "xy_footprint_source_derived": True, "object_names": sorted(o.name for o in asset.objects),
    },
    "evidence_sources": [
        {"provider": "Purdue BuildingShapes ArcGIS FeatureServer", "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D796&outFields=*&returnGeometry=true&outSR=4326&f=pjson", "snapshot": "audit/"+ID+"/sources/purdue_gis_fid_796_current.json", "retrieved": "2026-10-26", "notes": "Named feature, SOFDH, address 503 State St, OWNER=GREEK; exact ring used for plan."},
        {"provider": "Phi Delta Theta Purdue chapter website", "url": "https://purdue-phi.net/state-street-makeover/", "snapshot": "audit/"+ID+"/sources/purdue_phi_delta_state_street_makeover_2017.html", "retrieved": "2026-10-26", "source_date": "2017-06-13", "notes": "Article identifies the house at 503 W State Street and the image as taken outside the house; photo used for street facade."},
        {"provider": "Esri World Imagery tile service", "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/20/{y}/{x}", "snapshot": "audit/"+ID+"/sources/esri_world_imagery_mosaic_z20.jpg", "retrieved": "2026-10-26", "source_date": None, "notes": "Eight zoom-20 tiles (X 271135–271138, Y 395351–395352) form the saved 4×2 mosaic. Acquisition date is not exposed by the tile endpoint. GIS boundary overlay is in audit/"+ID+"/renders/gis_footprint_imagery_overlay.png."},
        {"provider": "Phi Delta Theta historical chapter publication (The Scroll, 1910 issue)", "url": "https://phideltathetaarchive.com/wp-content/uploads/2012/03/1909-10_vol34_no1-5.pdf", "snapshot": "audit/"+ID+"/sources/phi_delta_theta_scroll_1910_issue.pdf", "retrieved": "2026-10-26", "source_date": "1910-03", "notes": "Search-indexed article 'Indiana Theta’s New House' documents a 1909 house project, a corner site opposite the university, and architect Elmer E. Dunlap; historical context only, not used to assert current geometry."},
    ],
    "measurements": {
        "plan": "GIS plan ring transformed via documented approximate local campus conversion; no surveyed projection asserted.",
        "height": "Unverified; 3-storey interpretation and roof heights are estimates from the chapter's oblique 2017 facade image.",
        "facade_uncertainty": "Window spacing, floor heights, roof pitch, portico width, and hidden elevations are approximate; image does not provide a scale reference.",
        "boundary_uncertainty": "Source polygon is official feature FID 796. The upper roof and decorative portico are allowed to overhang its structural base slightly.",
    },
    "evidence_document": "audit/"+ID+"/evidence.md",
    "reopen_validation": "audit/"+ID+"/reopen_validation.json",
    "renders": ["audit/"+ID+"/renders/01_street_facade.png", "audit/"+ID+"/renders/02_north_elevation.png", "audit/"+ID+"/renders/03_plan.png", "audit/"+ID+"/renders/gis_footprint_imagery_overlay.png"],
}
EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"asset": str(ASSET), "export_objects": len(asset.objects), "xy_bounds": xy_bounds, "evidence": str(EVIDENCE)}, indent=2))
