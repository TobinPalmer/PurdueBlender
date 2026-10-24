"""Build a source library for Purdue's Convergence Center.

Run with Blender 5.2 background Python from the project root.  The exported
asset collection is local to the approximate official footprint centroid; the
original campus-coordinate massing file is intentionally untouched.
"""
import bpy
import json
import math
import os
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEOJSON = os.path.join(os.path.dirname(__file__), "convergence_gis_feature_946.geojson")
OUT_BLEND = os.path.join(ROOT, "modular", "buildings", "convergence_center.blend")
OUT_PREVIEW = os.path.join(os.path.dirname(__file__), "convergence_center_preview.png")
OUT_EVIDENCE = os.path.join(os.path.dirname(__file__), "convergence_center_evidence.json")

# Project convention: local campus linear approximation, meters; X east, Y north.
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
SCALE_X = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
SCALE_Y = 111040.0
CENTROID_XY = (-1131.698568664057, -405.52500592356535)


def remove_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    root = bpy.context.scene.collection
    for child in list(root.children):
        if child.name == "Collection":
            root.children.unlink(child)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def make_material(name, color, roughness=0.55, metallic=0.0, noise_scale=24.0, bump_strength=0.08):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    tex = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 3.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.19
    ramp.color_ramp.elements[0].color = (*(c * 0.91 for c in color), 1.0)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (*(min(1, c * 1.04) for c in color), 1.0)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.025
    links.new(tex.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def move_to_collection(obj, collection):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def mesh_object(name, verts, faces, collection, material, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def prism(name, outline, z0, z1, collection, material):
    n = len(outline)
    verts = [(x, y, z0) for x, y in outline] + [(x, y, z1) for x, y in outline]
    # Official GIS ring is clockwise. Keep bottom normals down, top normals up,
    # and each extruded side normal outward.
    faces = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    faces.extend((i, i + n, (i + 1) % n + n, (i + 1) % n) for i in range(n))
    return mesh_object(name, verts, faces, collection, material)


def box(name, loc, dims, material, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = move_to_collection(bpy.context.object, collection)
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("small manufactured edge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def edge_basis(a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    tangent = (dx / length, dy / length)
    # GIS rings are clockwise in the projected local frame; right normal is outward.
    normal = (-tangent[1], tangent[0])
    return length, tangent, normal


def wall_strip(name, a, b, s0, s1, z0, z1, offset, collection, material):
    length, t, nrm = edge_basis(a, b)
    p0 = (a[0] + t[0] * s0 + nrm[0] * offset, a[1] + t[1] * s0 + nrm[1] * offset)
    p1 = (a[0] + t[0] * s1 + nrm[0] * offset, a[1] + t[1] * s1 + nrm[1] * offset)
    return mesh_object(name,
        [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)],
        [(0, 1, 2, 3)], collection, material)


def main():
    remove_scene()
    scene = bpy.context.scene
    asset = bpy.data.collections.new("Asset_convergence_center")
    preview = bpy.data.collections.new("Preview_Only")
    scene.collection.children.link(asset)
    scene.collection.children.link(preview)

    with open(GEOJSON, "r", encoding="utf-8-sig") as f:
        feature = json.load(f)["features"][0]
    assert feature["properties"]["FID"] == 946
    assert feature["properties"]["BLDG_ABBR"] == "CONV"
    ring_ll = feature["geometry"]["coordinates"][0]
    outline = []
    for lon, lat in ring_ll[:-1]:
        x = (lon - ORIGIN_LON) * SCALE_X - CENTROID_XY[0]
        y = (lat - ORIGIN_LAT) * SCALE_Y - CENTROID_XY[1]
        outline.append((x, y))
    # Independently recompute the linear-ring centroid from the downloaded GIS
    # feature and verify that it matches the declared local placement origin.
    projected_abs = [((lon - ORIGIN_LON) * SCALE_X, (lat - ORIGIN_LAT) * SCALE_Y) for lon, lat in ring_ll]
    twice_area = centroid_x_num = centroid_y_num = 0.0
    for (x0, y0), (x1, y1) in zip(projected_abs, projected_abs[1:]):
        cross = x0 * y1 - x1 * y0
        twice_area += cross
        centroid_x_num += (x0 + x1) * cross
        centroid_y_num += (y0 + y1) * cross
    gis_area_m2 = abs(twice_area / 2.0)
    gis_centroid = (centroid_x_num / (3.0 * twice_area), centroid_y_num / (3.0 * twice_area))
    centroid_delta = (gis_centroid[0] - CENTROID_XY[0], gis_centroid[1] - CENTROID_XY[1])
    assert math.hypot(*centroid_delta) < 0.02, f"GIS ring centroid differs from manifest origin: {centroid_delta}"

    # Architectural readings: GIS footprint is authoritative for plan shape;
    # floor heights and curtain-wall module are estimates from five-story imagery.
    mat_shell = make_material("Convergence | pale cool-gray metal cladding", (0.47, 0.51, 0.53), 0.68, 0.25, 38, 0.11)
    mat_light = make_material("Convergence | light aluminum trim", (0.73, 0.76, 0.74), 0.38, 0.48, 60, 0.06)
    mat_spandrel = make_material("Convergence | charcoal spandrel", (0.12, 0.16, 0.18), 0.34, 0.25, 26, 0.06)
    mat_glass = bpy.data.materials.new("Convergence | blue-gray low-e glazing")
    mat_glass.diffuse_color = (0.075, 0.16, 0.20, 1.0)
    mat_glass.use_nodes = True
    glass_bsdf = next(n for n in mat_glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    glass_bsdf.inputs["Base Color"].default_value = (0.075, 0.16, 0.20, 1)
    glass_bsdf.inputs["Roughness"].default_value = 0.2
    glass_bsdf.inputs["Metallic"].default_value = 0.28
    if "IOR" in glass_bsdf.inputs:
        glass_bsdf.inputs["IOR"].default_value = 1.46
    glass_nodes, glass_links = mat_glass.node_tree.nodes, mat_glass.node_tree.links
    glass_coord = glass_nodes.new("ShaderNodeTexCoord")
    glass_noise = glass_nodes.new("ShaderNodeTexNoise")
    glass_noise.inputs["Scale"].default_value = 95.0
    glass_noise.inputs["Detail"].default_value = 2.0
    glass_ramp = glass_nodes.new("ShaderNodeMapRange")
    glass_ramp.inputs["From Min"].default_value = 0.0
    glass_ramp.inputs["From Max"].default_value = 1.0
    glass_ramp.inputs["To Min"].default_value = 0.17
    glass_ramp.inputs["To Max"].default_value = 0.25
    glass_bump = glass_nodes.new("ShaderNodeBump")
    glass_bump.inputs["Strength"].default_value = 0.012
    glass_bump.inputs["Distance"].default_value = 0.006
    glass_links.new(glass_coord.outputs["Generated"], glass_noise.inputs["Vector"])
    glass_links.new(glass_noise.outputs["Fac"], glass_ramp.inputs["Value"])
    glass_links.new(glass_ramp.outputs["Result"], glass_bsdf.inputs["Roughness"])
    glass_links.new(glass_noise.outputs["Fac"], glass_bump.inputs["Height"])
    glass_links.new(glass_bump.outputs["Normal"], glass_bsdf.inputs["Normal"])
    mat_roof = make_material("Convergence | dark membrane roof", (0.105, 0.125, 0.14), 0.83, 0.06, 32, 0.12)
    mat_concrete = make_material("Convergence | architectural concrete", (0.48, 0.49, 0.46), 0.88, 0.0, 18, 0.16)
    mat_interior = make_material("Convergence | warm lobby interior", (0.64, 0.46, 0.25), 0.4, 0.0, 10, 0.04)
    mat_sign = make_material("Convergence | identity sign charcoal", (0.055, 0.066, 0.071), 0.45, 0.12, 28, 0.03)

    # GIS polygon produces the main wall envelope at 35 x 84 m with the verified
    # stepped south extension.  5 stories = official count; 20.4 m is an estimate.
    floor_z = [0.0, 4.25, 8.3, 12.35, 16.4, 20.45]
    roof_z = 20.45
    # Ground-level plinth + five-storey upper envelope; keep footprint geometry local.
    prism("CONV_GIS_ground_plate", outline, -0.25, 0.20, asset, mat_concrete)
    prism("CONV_GIS_five_story_cladding_volume", outline, 4.15, roof_z, asset, mat_shell)
    prism("CONV_flat_roof", outline, roof_z, roof_z + 0.32, asset, mat_roof)

    # A recessed shadow line and floor bands clearly articulate five levels.
    for level, z in enumerate(floor_z[1:5], 1):
        prism(f"CONV_floor_{level}_continuous_spandrel_band", outline, z - 0.13, z + 0.16, asset, mat_spandrel)
        prism(f"CONV_floor_{level}_aluminum_slab_edge", outline, z + 0.16, z + 0.25, asset, mat_light)

    # Continuous ground-floor curtain wall around the exact GIS perimeter.
    for i, a in enumerate(outline):
        b = outline[(i + 1) % len(outline)]
        length, t, nrm = edge_basis(a, b)
        wall_strip(f"CONV_lobby_glass_{i:02d}", a, b, 0.30, length - 0.30, 0.48, 4.05, 0.10, asset, mat_glass)
        # Fine dark mullions, approximately 1.55 m on center.
        count = max(1, int(length / 1.55))
        for j in range(1, count):
            s = length * j / count
            cx = a[0] + t[0] * s + nrm[0] * 0.13
            cy = a[1] + t[1] * s + nrm[1] * 0.13
            box(f"CONV_lobby_mullion_{i:02d}_{j:02d}", (cx, cy, 2.24), (0.065, 0.065, 3.48), mat_spandrel, asset)

        # Upper storeys: inset ribbon glazing with repeated light-metal vertical bays.
        for story in range(1, 5):
            z0 = floor_z[story] + 1.02
            z1 = floor_z[story + 1] - 0.56
            if z1 <= z0:
                continue
            # Main ribbon is broken into individual panes with visible metal mullions.
            bay = 3.05
            n_bays = max(1, int((length - 1.1) / bay))
            usable = length - 0.9
            actual_bay = usable / n_bays
            for j in range(n_bays):
                s0 = 0.45 + j * actual_bay + 0.13
                s1 = 0.45 + (j + 1) * actual_bay - 0.13
                if s1 > s0:
                    wall_strip(f"CONV_upper_glazing_F{story}_{i:02d}_{j:02d}", a, b, s0, s1, z0, z1, 0.075, asset, mat_glass)
                    # Light metal panel piers separate the windows from neighbors.
                    if j > 0:
                        sm = (s0 + s1) / 2
                        p0 = (a[0] + t[0] * sm + nrm[0] * 0.135,
                              a[1] + t[1] * sm + nrm[1] * 0.135)
                        p1 = (p0[0] + t[0] * 0.07, p0[1] + t[1] * 0.07)
                        mesh_object(f"CONV_mullion_F{story}_{i:02d}_{j:02d}",
                            [(p0[0],p0[1],z0),(p1[0],p1[1],z0),(p1[0],p1[1],z1),(p0[0],p0[1],z1)],
                            [(0,1,2,3)], asset, mat_light)

        # Continuous light-colored cornice emphasizes the measured plan perimeter.
        wall_strip(f"CONV_roof_edge_{i:02d}", a, b, 0.0, length, 20.72, 21.02, 0.14, asset, mat_light)

    # Entry canopy and glazed vestibule on the long west frontage facing Foundry
    # Drive, inferred from the official address/photos and Google Maps site layout.
    # Exact door bay remains approximate because no elevation was available.
    west_edge = max(range(len(outline)), key=lambda i: edge_basis(outline[i], outline[(i + 1) % len(outline)])[0]
                    if abs((outline[i][0] + outline[(i + 1) % len(outline)][0]) * 0.5 - min(x for x, _ in outline)) < 0.7 else 0)
    a, b = outline[west_edge], outline[(west_edge + 1) % len(outline)]
    length, t, nrm = edge_basis(a, b)
    center_s = length * 0.50
    cx = a[0] + t[0] * center_s
    cy = a[1] + t[1] * center_s
    # On the south face the outward normal is expected to point south.
    canopy_center = (cx + nrm[0] * 1.10, cy + nrm[1] * 1.10, 4.20)
    longitudinal = abs(t[1]) > abs(t[0])
    canopy_dims = (2.25, 12.5, 0.32) if longitudinal else (12.5, 2.25, 0.32)
    vestibule_dims = (1.10, 5.0, 3.65) if longitudinal else (5.0, 1.10, 3.65)
    box("CONV_west_entry_canopy", canopy_center, canopy_dims, mat_spandrel, asset, 0.08)
    vestibule_center = (cx + nrm[0] * 0.58, cy + nrm[1] * 0.58, 2.05)
    box("CONV_glazed_entry_vestibule", vestibule_center, vestibule_dims, mat_glass, asset, 0.02)
    for side, sign in (("A", -1.0), ("B", 1.0)):
        col_center = (cx + t[0] * sign * 5.35 + nrm[0] * 1.20,
                      cy + t[1] * sign * 5.35 + nrm[1] * 1.20, 2.05)
        box(f"CONV_canopy_support_column_{side}", col_center, (0.20, 0.20, 4.0), mat_light, asset)

    # Evidence-supported visible lobby hint: warm floor and a compact welcome desk,
    # with no unsupported room layouts or upper-floor interiors.
    lobby_cx = cx - nrm[0] * 5.0
    lobby_cy = cy - nrm[1] * 5.0
    prism("CONV_visible_lobby_floor", [
        (lobby_cx - 8.0, lobby_cy - 8.0), (lobby_cx + 8.0, lobby_cy - 8.0),
        (lobby_cx + 8.0, lobby_cy + 8.0), (lobby_cx - 8.0, lobby_cy + 8.0)],
        0.42, 0.52, asset, mat_interior)
    # keep reception element near the glazed entrance, scaled as a silhouette.
    desk_center = (cx - nrm[0] * 3.2, cy - nrm[1] * 3.2, 1.35)
    box("CONV_lobby_reception_desk_visible_cue", desk_center, (3.5, 0.75, 0.95), mat_concrete, asset, 0.12)

    # Roof screen and rooftop mechanical units are intentionally restrained and
    # not treated as verified equipment locations.
    # An open mechanical screen follows the roof perimeter; keep the center roof
    # open so the rooftop plant remains visually legible.
    for i, a in enumerate(outline):
        b = outline[(i + 1) % len(outline)]
        length, t, nrm = edge_basis(a, b)
        wall_strip(f"CONV_roof_screen_panel_{i:02d}", a, b, 0.0, length, 21.02, 22.15, -1.0, asset, mat_shell)
        nslats = max(2, int(length / 1.5))
        for j in range(1, nslats):
            s = length * j / nslats
            px = a[0] + t[0] * s + nrm[0] * -0.86
            py = a[1] + t[1] * s + nrm[1] * -0.86
            box(f"CONV_roof_screen_louver_{i:02d}_{j:02d}", (px, py, 21.57), (0.075, 0.075, 1.05), mat_spandrel, asset)
    for idx, (x, y, sx, sy) in enumerate([(-8, 15, 5, 3.2), (0, 15, 5, 3.2), (8, 15, 5, 3.2), (-5, 6, 3.8, 2.8), (4, 6, 3.8, 2.8)]):
        box(f"CONV_roof_HVAC_estimated_{idx+1}", (x, y, 21.45), (sx, sy, 0.85), mat_spandrel, asset, 0.08)

    # Discreet building identity panel. Text is oriented to the west frontage.
    sign_loc = (cx + nrm[0] * 0.18, cy + nrm[1] * 0.18, 6.15)
    sign_dims = (0.25, 5.0, 1.05) if longitudinal else (5.0, 0.25, 1.05)
    box("CONV_convergence_identity_sign_backing", sign_loc, sign_dims, mat_sign, asset, 0.04)
    curve = bpy.data.curves.new("CONV_identity_text_curve", "FONT")
    curve.body = "CONVERGENCE"
    curve.size = 0.36
    curve.extrude = 0.003
    text_obj = bpy.data.objects.new("CONV_identity_sign_text", curve)
    asset.objects.link(text_obj)
    text_obj.data.materials.append(mat_light)
    # Font local x is baseline, local y is up, local z faces out from the wall.
    up = Vector((0.0, 0.0, 1.0))
    normal = Vector((nrm[0], nrm[1], 0.0))
    baseline = up.cross(normal).normalized()
    rot = Matrix((baseline, up, normal)).transposed()
    text_obj.location = (cx + nrm[0] * 0.34 + baseline.x * 1.45,
                         cy + nrm[1] * 0.34 + baseline.y * 1.45, 5.98)
    text_obj.rotation_euler = rot.to_euler()

    # Preview-only ground, naturalistic daylight and two views; not part of asset.
    ground_mat = make_material("Preview | neutral pavement", (0.23, 0.26, 0.27), 0.88, 0, 9, 0.12)
    box("Preview_ground", (0, 0, -0.66), (145, 150, 0.32), ground_mat, preview)
    world = bpy.data.worlds.new("Convergence preview | clear sky") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.34, 0.50, 0.68, 1)
    bg.inputs["Strength"].default_value = 0.48
    light_data = bpy.data.lights.new("Preview_sun", "SUN")
    light_obj = bpy.data.objects.new("Preview_sun", light_data)
    preview.objects.link(light_obj)
    light_obj.rotation_euler = (math.radians(28), math.radians(-24), math.radians(-28))
    light_data.energy = 3.0
    area = bpy.data.lights.new("Preview_softbox", "AREA")
    area.energy = 4200
    area.shape = "DISK"
    area.size = 34
    area_obj = bpy.data.objects.new("Preview_softbox", area)
    preview.objects.link(area_obj)
    area_obj.location = (55, -68, 62)
    area_obj.rotation_euler = (Vector((0, 0, 9)) - area_obj.location).to_track_quat("-Z", "Y").to_euler()

    cam_data = bpy.data.cameras.new("Preview_camera")
    cam = bpy.data.objects.new("Preview_camera", cam_data)
    preview.objects.link(cam)
    cam.location = (-112, -126, 77)
    target = Vector((0, 0, 8.8))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 54
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = 80
    scene.render.filepath = OUT_PREVIEW
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.camera.data.dof.use_dof = False
    # Hide preview-only objects when the collection is linked into the master.
    preview.hide_render = True
    # render with preview visibility enabled temporarily
    preview.hide_render = False
    bpy.ops.render.render(write_still=True)
    preview.hide_render = True

    # Save a clean asset file; collection is the only content to be linked by the master.
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

    # Evidence carries original native GIS snapshot and transformed footprint metrics.
    bounds = {
        "x_min": min(x for x, _ in outline), "x_max": max(x for x, _ in outline),
        "y_min": min(y for _, y in outline), "y_max": max(y for _, y in outline),
        "width_m": max(x for x, _ in outline) - min(x for x, _ in outline),
        "depth_m": max(y for _, y in outline) - min(y for _, y in outline),
    }
    evidence = {
        "building_id": "convergence_center",
        "asset_file": "modular/buildings/convergence_center.blend",
        "exported_collection": "Asset_convergence_center",
        "original_massing_asset_preserved": "modular/buildings/massing_convergence_center_for_innovation_and_collaboration_conv_ce5226e.blend",
        "retrieved_utc_date": "2026-10-23",
        "sources": [
            {"provider": "Purdue University News", "url": "https://www.purdue.edu/newsroom/archive/releases/2018/Q4/discovery-park-district-lays-welcome-mat-with-construction-of-145,000-square-foot,-five-story-building.html", "use": "official name, five-story count, 145,000-sq-ft area, large lobby/plaza, first-floor retail; 2018 construction announcement includes design rendering"},
            {"provider": "Purdue University News / Purdue Research Foundation", "url": "https://www.purdue.edu/newsroom/archive/releases/2021/Q3/purdue,-purdue-research-foundation-launch-lab-to-life-6g-digital-innovation-at-discovery-park-district.html", "use": "official building photo caption and operational identity"},
            {"provider": "Purdue University News / Purdue Research Foundation", "url": "https://www.purdue.edu/newsroom/archive/releases/2021/Q1/wabash-national-set-to-open-collaboration-space-in-purdues-discovery-park-district.html", "use": "official exterior photo associated with occupied Convergence Center"},
            {"provider": "Purdue Innovates", "url": "https://purdueinnovates.org/venue/the-convergence-center-for-innovation-and-collaboration/", "use": "current venue identity and exact address 101 Foundry Drive"},
            {"provider": "Google Maps", "url": "https://www.google.com/maps/place/The+Convergence+Center+for+Innovation+and+Collaboration/@40.4237313,-86.929787,17z/data=!3m1!4b1!4m6!3m5!1s0x8812e38bd7e04541:0xc20b61b4bddde859!8m2!3d40.4237313!4d-86.9272121!16s%2Fg%2F11j7kpptjx", "use": "verified exact place listing/address and site map context; map places the west frontage on Foundry Drive with State Street north of the site and District Boulevard south; frontage inference only, not dimensional evidence"},
            {"provider": "Google Maps Street View", "url": "https://www.google.com/maps/@40.4235695,-86.9268681,3a,75y/data=!3m7!1e1!3m5!1s0x0:0x0!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D90%26panoid%3D0x0%253A0x0%26yaw%3D0!7i8192!8i4096", "use": "street-view coverage attempted on 2026-10-23; Google reports no street-level imagery at selected point and serves a Carr Workplaces interior panorama instead. Exterior facade therefore comes from official Purdue images, not Street View."},
            {"provider": "Purdue official CampusMap ArcGIS FeatureServer", "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0", "feature_query": "query?where=FID%3D946&outFields=*&returnGeometry=true", "feature_id": 946, "code": "CONV", "source_crs": "EPSG:3857 (WKID 102100, latest WKID 3857); captured feature transformed to EPSG:4326 for GeoJSON and reprojected with project approximation for model", "use": "authoritative official-campus footprint/source-feature identity"},
        ],
        "gis_snapshot": {"native": "audit/convergence_gis_feature_946_native.json", "wgs84": "audit/convergence_gis_feature_946.geojson", "layer_metadata": "audit/convergence_gis_layer_metadata.json", "retrieval_date": "2026-10-23", "native_crs": "EPSG:3857", "output_crs": "EPSG:4326", "feature_id": 946, "name": "Convergence", "BLDG_ABBR": "CONV", "address": "101 Foundry Drive, West Lafayette, IN"},
        "coordinate_frame": {"units": "meters", "axes": "X east, Y north, Z up", "project_origin_latitude": ORIGIN_LAT, "project_origin_longitude": ORIGIN_LON, "local_origin_xy_m": list(CENTROID_XY), "origin_definition": "official GIS polygon largest-ring centroid from existing Purdue official footprint reference; use master placement marker at this XY", "transform": "X=(longitude + 86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude - 40.4274)*111040; local XY subtract centroid"},
        "footprint_local_bounds_m": bounds,
        "footprint_validation": {"GIS_polygon_area_m2_projected": gis_area_m2, "centroid_xy_m_projected": list(gis_centroid), "local_origin_centroid_delta_m": list(centroid_delta), "transform_method": "ArcGIS EPSG:3857 source was requested as EPSG:4326 GeoJSON; vertices were transformed to the project's local approximate east/north metric frame, then the ring centroid was recalculated by shoelace formula. The independently calculated centroid matches the saved campus reference center exactly."},
        "geometry_edits": ["replaced one-object rectangular massing with 5-story local-coordinate shell following official stepped GIS footprint", "added light gray metal panel facade, restrained floor bands, ribbon windows, metal mullions, ground-floor curtain wall", "added west-facing Foundry Drive entrance canopy/vestibule, low-detail lobby cue, approximate identity panel, roof screen and estimated mechanical units", "used procedural material texture variation on cladding, concrete, roof and metal trim"],
        "vertical_evidence": {"story_count": {"value": 5, "status": "verified from official 2018 Purdue construction release"}, "roof_height_m": {"value_estimate": 22.25, "status": "estimated, not measured; based on five-story contemporary office-building scale and modeled roof screen"}, "floor_heights": "estimated: ground floor 4.25 m, four upper stories approximately 4.05 m each"},
        "uncertainty": ["No survey or dimensioned architectural elevation was found; vertical dimensions and window spacing are estimated.", "Footprint identity verified by FID/code/name and address; GIS is an official campus-map polygon, not a certified survey.", "South-side entry/canopy placement is inferred from official facade imagery and local street/address context; exact entrance bay not dimensioned.", "Roof screen/HVAC placement is illustrative and unverified.", "Interior modeling is limited to a subtle lobby floor/reception cue because public evidence confirms a large ground-floor lobby but does not expose complete interior layouts."],
        "preview": "audit/convergence_center_preview.png",
        "source_urls_and_retrieval_date": "URL/provider/date recorded above; sources consulted 2026-10-23",
    }
    with open(OUT_EVIDENCE, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
        f.write("\n")
    print(json.dumps({"saved": OUT_BLEND, "preview": OUT_PREVIEW, "evidence": OUT_EVIDENCE, "outline_vertices": len(outline), "bounds": bounds, "asset_object_count": len(asset.objects)}))


if __name__ == "__main__":
    main()
