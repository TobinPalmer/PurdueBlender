"""Repair and export Purdue Armory from its GIS footprint and archival photo.

Run with Blender from the PurdueBlender root:
    blender --background --python modular/buildings/build_armory.py

The source .blend is reopened and retained as the base because it contains
portable materials and established facade/context detail. This module fits its
structural perimeter to Purdue GIS, removes unsupported roof towers/monitor,
and adds the archival central stepped gable. Height and total story count are
not published by the sources and remain explicitly estimated/unverified.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular/buildings/armory.blend"
GIS_PATH = ROOT / "audit/armory/purdue_gis_feature_207.json"
EVIDENCE = ROOT / "audit/armory"
PREVIEW = EVIDENCE / "armory_repaired_preview.png"
DETAIL = EVIDENCE / "armory_central_gable_detail.png"
COLLECTION_NAME = "Asset_armory"
ASSET_ID = "armory"
PLACEMENT_XY = (-208.7750015258789, 68.34999656677246)


def gis_local_geometry():
    record = json.loads(GIS_PATH.read_text(encoding="utf-8"))
    feature = record["query_response"]["features"][0]
    a = feature["attributes"]
    assert a["OBJECTID"] == 207 and a["ABBR"] == "AR" and a["Name"] == "Armory"
    ring = feature["geometry"]["rings"][0][:-1]
    points = []
    for x3857, y3857 in ring:
        lon = math.degrees(x3857 / 6378137.0)
        lat = math.degrees(2 * math.atan(math.exp(y3857 / 6378137.0)) - math.pi / 2)
        x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
        y = (lat - 40.4274) * 111040.0
        points.append((x - PLACEMENT_XY[0], y - PLACEMENT_XY[1]))
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in (0, 1)]
    return record, feature, points, bounds


def geometry_bounds(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    coords = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        coords.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        evaluated.to_mesh_clear()
    if not coords:
        return None
    return [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]


def fit_all_library_geometry(asset, target_bounds):
    """Apply small GIS-derived XY affine fit without changing object parenting."""
    structural = [asset.objects.get(n) for n in (
        "Armory_Wall_East", "Armory_Wall_West", "Armory_Wall_North_Low", "Armory_Wall_South_Low")]
    structural = [o for o in structural if o]
    before = geometry_bounds(structural)
    assert before, "Structural perimeter meshes are missing"
    current_xy = before[:2]
    current_center = [(b[0] + b[1]) / 2 for b in current_xy]
    target_center = [(b[0] + b[1]) / 2 for b in target_bounds]
    scale = [(target_bounds[i][1] - target_bounds[i][0]) /
             (current_xy[i][1] - current_xy[i][0]) for i in (0, 1)]
    assert all(0.97 < s < 1.03 for s in scale), f"Unexpected GIS fit: {scale}"
    if all(abs(current_xy[i][0] - target_bounds[i][0]) < 0.01 and
           abs(current_xy[i][1] - target_bounds[i][1]) < 0.01 for i in (0, 1)):
        return before, before, scale, current_center, target_center

    # Work in evaluated world coordinates, then map vertices back through the
    # unchanged matrix. Do not move non-mesh parent empties: mesh vertices are
    # fitted through their existing parent matrices, avoiding double transforms.
    for obj in list(asset.all_objects):
        if obj.type == "MESH" and obj.data.library is None:
            if obj.data.users > 1:
                obj.data = obj.data.copy()
            inv = obj.matrix_world.inverted_safe()
            for vertex in obj.data.vertices:
                w = obj.matrix_world @ vertex.co
                fitted = Vector((target_center[0] + (w.x - current_center[0]) * scale[0],
                                 target_center[1] + (w.y - current_center[1]) * scale[1], w.z))
                vertex.co = inv @ fitted
            obj.data.update()
    bpy.context.view_layer.update()
    after = geometry_bounds(structural)
    asset["gis_affine_fit_applied"] = True
    asset["gis_affine_scale_xy"] = json.dumps(scale)
    asset["gis_affine_center_before_xy_m"] = json.dumps(current_center)
    asset["gis_affine_center_target_xy_m"] = json.dumps(target_center)
    return before, after, scale, current_center, target_center


def material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def mesh_object(name, verts, faces, target_collection, mat):
    data = bpy.data.meshes.new(name + "Mesh")
    data.from_pydata(verts, [], faces)
    data.materials.append(mat)
    data.update()
    obj = bpy.data.objects.new(name, data)
    target_collection.objects.link(obj)
    return obj


def extruded_yz_polygon(name, outline, x0, x1, target_collection, mat):
    n = len(outline)
    verts = [(x, y, z) for x in (x0, x1) for y, z in outline]
    faces = [tuple(range(n)), tuple(range(n, 2 * n))[::-1]]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return mesh_object(name, verts, faces, target_collection, mat)


def add_beam_yz(name, a, b, x, width, depth, target_collection, mat):
    """A shallow rectangular molding beam following a Y/Z outline segment."""
    dy, dz = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dy, dz)
    ny, nz = -dz / length * width / 2, dy / length * width / 2
    p = [(a[0] + ny, a[1] + nz), (b[0] + ny, b[1] + nz),
         (b[0] - ny, b[1] - nz), (a[0] - ny, a[1] - nz)]
    return extruded_yz_polygon(name, p, x - depth / 2, x + depth / 2, target_collection, mat)


def add_gable(asset, brick, stone, roof, glass):
    # Source-supported central stepped gable above the east-side main entry.
    # Its registration, width and elevation are interpretive estimates.
    x_back, x_front = 15.75, 19.65
    outline = [(-15.5, 12.45), (-15.5, 13.05), (-11.5, 13.05),
               (-11.5, 14.05), (-7.0, 14.05), (0.0, 19.35),
               (7.0, 14.05), (11.5, 14.05), (11.5, 13.05),
               (15.5, 13.05), (15.5, 12.45)]
    gable = extruded_yz_polygon("Armory_Rosen_Central_Stepped_Gable", outline,
                                x_back, x_front, asset, brick)
    gable["evidence_status"] = "Stepped central gable and attic fanlight follow the Purdue Archives Armory exterior photograph (archival date not established from the image record); exact dimensions/registration are estimates."
    # Light limestone coping tracks the characteristic stepped roof outline.
    for i, (a, b) in enumerate(zip(outline, outline[1:] + outline[:1])):
        if i in (0, len(outline) - 1):
            continue
        add_beam_yz(f"Armory_Rosen_Gable_Coping_{i:02d}", a, b,
                    x_front + 0.12, 0.34, 0.20, asset, stone)
    # Projecting gable roof leaves, a shallow cross-gabled canopy volume.
    roof_verts = [
        (x_back, -15.7, 13.05), (x_back, 0, 19.45), (x_back, 15.7, 13.05),
        (x_front + 0.32, -15.7, 13.05), (x_front + 0.32, 0, 19.45),
        (x_front + 0.32, 15.7, 13.05)]
    mesh_object("Armory_Rosen_Gable_Roof_Wings", roof_verts,
                [(0, 1, 4, 3), (1, 2, 5, 4)], asset, roof)
    gable["roof_material_status"] = "Historic source describes roof tiles during the 1928 fire; present roof surface/finish is unverified. Render material is a restrained illustrative tile tone."

    # Central semicircular fanlight visible in the archival front elevation.
    cx = x_front + 0.16
    radius = 4.15
    spring_z = 16.15
    segments = 24
    arch = [(-radius, 15.3), (radius, 15.3), (radius, spring_z)]
    arch.extend((radius * math.cos(i * math.pi / segments),
                 spring_z + radius * math.sin(i * math.pi / segments))
                for i in range(1, segments + 1))
    extruded_yz_polygon("Armory_Rosen_Gable_Arched_Fanlight_Glass", arch,
                        cx, cx + 0.08, asset, glass)
    # Limestone semicircular archivolt and jambs.
    for side in (-1, 1):
        add_beam_yz(f"Armory_Rosen_Fanlight_Jamb_{side}", (side * radius, 15.25),
                    (side * radius, spring_z), cx + 0.22, 0.28, 0.18, asset, stone)
    for i in range(segments):
        a = (radius * math.cos(i * math.pi / segments),
             spring_z + radius * math.sin(i * math.pi / segments))
        b = (radius * math.cos((i + 1) * math.pi / segments),
             spring_z + radius * math.sin((i + 1) * math.pi / segments))
        add_beam_yz(f"Armory_Rosen_Fanlight_Arch_{i:02d}", a, b,
                    cx + 0.22, 0.26, 0.18, asset, stone)
    add_beam_yz("Armory_Rosen_Fanlight_Sill", (-radius, 15.25), (radius, 15.25),
                cx + 0.22, 0.30, 0.18, asset, stone)
    # Center and radial muntins read as an arched multi-light sash.
    add_beam_yz("Armory_Rosen_Fanlight_Center_Muntin", (0, 15.3), (0, spring_z + radius),
                cx + 0.34, 0.10, 0.07, asset, stone)
    for y in (-2.1, 2.1):
        ztop = spring_z + math.sqrt(max(0.0, radius * radius - y * y))
        add_beam_yz(f"Armory_Rosen_Fanlight_Vertical_Muntin_{y:+.1f}",
                    (y, 15.3), (y, ztop), cx + 0.34, 0.085, 0.07, asset, stone)
    add_beam_yz("Armory_Rosen_Fanlight_Cross_Muntin", (-radius * 0.88, 16.75),
                (radius * 0.88, 16.75), cx + 0.34, 0.085, 0.07, asset, stone)


def main():
    record, feature, points, target_bounds = gis_local_geometry()
    assert len(points) == 4
    bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
    asset = bpy.data.collections.get(COLLECTION_NAME)
    assert asset is not None
    assert bpy.context.scene.name == "Building_armory"

    shell_before, shell_after, scale, center_before, center_target = fit_all_library_geometry(asset, target_bounds)

    # Remove unsupported four tall corner bastions and the unreferenced ridge
    # monitor/hip roof patch; the 1918 archive view shows a central gable.
    # The interior roof trusses were visible outside the reconstructed roof and
    # have no structural drawing source, so remove those too.
    removed_towers = 0
    removed_trusses = 0
    for obj in list(asset.all_objects):
        name = obj.name
        if (name.startswith("Armory_Tower_") or name.startswith("Armory_Battlement_") or
                name.startswith("Armory_Merlon_") or name.startswith("Armory_Roof_Seg_") or
                name.startswith("Armory_Ridge_") or name.startswith("Armory_Truss_") or
                name == "Armory_Continuous_Roof_Repair" or name == "Armory_Drill_Floor_Slab"):
            if name.startswith(("Armory_Tower_", "Armory_Battlement_", "Armory_Merlon_")):
                removed_towers += 1
            if name.startswith("Armory_Truss_"):
                removed_trusses += 1
            bpy.data.objects.remove(obj, do_unlink=True)
    asset["removed_unsupported_tower_detail_count"] = max(
        removed_towers, int(asset.get("removed_unsupported_tower_detail_count", 0)))
    asset["removed_unverified_truss_detail_count"] = max(
        removed_trusses, int(asset.get("removed_unverified_truss_detail_count", 0)))

    # A previous repair pass left its 216 window-frame/muntin objects detached
    # about 10 m from the masonry. Align them to the GIS-matched long walls.
    east_wall_x, west_wall_x = target_bounds[0][1], target_bounds[0][0]
    for obj in list(asset.all_objects):
        if not obj.name.startswith("Armory_Window_Frame_Repair") or obj.get("armory_gis_wall_aligned"):
            continue
        if obj.type != "MESH" or obj.data.library is not None:
            continue
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        world = [obj.matrix_world @ v.co for v in obj.data.vertices]
        if not world:
            continue
        mean_x = sum(v.x for v in world) / len(world)
        target_x = east_wall_x + 0.11 if mean_x > 0 else west_wall_x - 0.11
        dx = target_x - mean_x
        inv = obj.matrix_world.inverted_safe()
        for vertex, w in zip(obj.data.vertices, world):
            vertex.co = inv @ Vector((w.x + dx, w.y, w.z))
        obj.data.update()
        obj["armory_gis_wall_aligned"] = True

    # Keep lights available for preview renders but outside the manifest export.
    scene = bpy.context.scene
    preview_collection = bpy.data.collections.get("Armory_Preview_Setup")
    if preview_collection is None:
        preview_collection = bpy.data.collections.new("Armory_Preview_Setup")
        scene.collection.children.link(preview_collection)
    for obj in list(asset.all_objects):
        if obj.type in {"LIGHT", "CAMERA"}:
            for owner in list(obj.users_collection):
                owner.objects.unlink(obj)
            preview_collection.objects.link(obj)

    # Build on every run deterministically by removing prior generated geometry.
    generated_prefixes = ("Armory_Rosen_",)
    for obj in list(asset.all_objects):
        if obj.name.startswith(generated_prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)

    brick = bpy.data.materials.get("Purdue_Red_Brick") or material(
        "Armory_Rosen_Brick", (0.31, 0.075, 0.045), 0.9)
    stone = bpy.data.materials.get("Bedford_Indiana_Limestone") or material(
        "Armory_Rosen_Limestone", (0.66, 0.61, 0.52), 0.8)
    roof = material("Armory_Rosen_Historic_Tile_Roof_Estimate", (0.19, 0.12, 0.095), 0.82)
    glass = material("Armory_Rosen_Arched_Fanlight_Glass", (0.045, 0.095, 0.13), 0.34, 0.08)

    # A low longitudinal gable roof is an inferred structural roof form; its
    # eave/ridge heights are estimates, while the archival central gable is the
    # distinctive source-supported silhouette.
    xw, xe = target_bounds[0][0] - 0.6, target_bounds[0][1] + 0.6
    yc, yn, ys = center_target[1], target_bounds[1][0] - 0.55, target_bounds[1][1] + 0.55
    xr = (target_bounds[0][0] + target_bounds[0][1]) / 2
    eave_z, ridge_z = 12.8, 18.0
    roof_v = [(xw, yn, eave_z), (xr, yn, ridge_z), (xe, yn, eave_z),
              (xw, ys, eave_z), (xr, ys, ridge_z), (xe, ys, eave_z)]
    mesh_object("Armory_Rosen_Main_Gabled_Roof_Estimate", roof_v,
                [(0, 1, 4, 3), (1, 2, 5, 4)], asset, roof)
    for end_y, label in ((yn, "South"), (ys, "North")):
        outline = [(xw, 12.3), (xe, 12.3), (xr, ridge_z - 0.12)]
        n = len(outline)
        verts = [(x, end_y, z) for x, z in outline]
        mesh_object(f"Armory_Rosen_Main_Gable_End_{label}", verts, [(0, 1, 2)], asset, brick)
    add_gable(asset, brick, stone, roof, glass)

    asset["building_id"] = ASSET_ID
    asset["building_name"] = "Armory"
    asset["owner"] = "Rosen"
    asset["source_feature_id"] = 207
    asset["gis_source"] = "Purdue University PuGeoDB.DBO.CampusBuilding MapServer layer 0, OBJECTID 207, EPSG:3857"
    asset["local_frame"] = "Meters, X east, Y north, Z up; manifest placement origin unchanged. Footprint fit follows modular/AGENTS.md local geographic conversion."
    asset["footprint_status"] = "Structural perimeter fitted to all four corners of official GIS polygon; exact source coordinates and pre/post envelope are in audit/armory/source_record.json."
    asset["height_status"] = "No authoritative total height/story count found. Wall and roof heights are visual/typology estimates calibrated to the archive photo; do not treat as survey values."
    asset["story_count_status"] = "Archival facade shows two principal windowed levels and a gable/attic light; current Purdue AFROTC directions mention stairs to a second floor. Total number of stories and basement status remain unverified."
    asset["roof_status"] = "Archival photograph supports the central stepped gable and arched upper light. Main gable roof form and dimensions are inferred; tile material is documented historically but current finish is unverified."

    # Preview helpers remain outside the exported collection.
    cam = scene.camera
    if cam is None:
        camdata = bpy.data.cameras.new("Armory_Repaired_Preview_Camera")
        cam = bpy.data.objects.new("Armory_Repaired_Preview_Camera", camdata)
        preview_collection.objects.link(cam)
        scene.camera = cam
    target = Vector((center_target[0], center_target[1], 9.0))
    cam.location = (center_target[0] + 125, center_target[1] - 115, 38)
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    # Retune the external lights to a clear exterior-view setup.
    area_lights = [o for o in preview_collection.objects if o.type == "LIGHT"]
    for light in area_lights:
        light.data.energy = min(light.data.energy, 1200)
    if not area_lights:
        ld = bpy.data.lights.new("Armory_Repaired_Key_Area", "AREA")
        ld.energy, ld.size = 8500, 65
        light = bpy.data.objects.new("Armory_Repaired_Key_Area", ld)
        preview_collection.objects.link(light)
        light.location = (center_target[0] + 25, center_target[1] - 55, 50)
        light.rotation_euler = (Vector((center_target[0], center_target[1], 8)) - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 12
    scene.render.resolution_x, scene.render.resolution_y = 1400, 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    scene.render.film_transparent = False
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(PREVIEW)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    # Secondary elevation view isolates the archive-supported gable/entry.
    cam.location = (center_target[0] + 78, center_target[1] - 14, 30)
    cam.rotation_euler = (Vector((center_target[0] + 17, center_target[1], 15.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 55
    scene.render.resolution_x, scene.render.resolution_y = 1100, 850
    scene.render.filepath = str(DETAIL)
    bpy.ops.render.render(write_still=True)

    print(json.dumps({"asset": str(ASSET_PATH), "collection": COLLECTION_NAME,
                      "gis_target_bounds_local_m": target_bounds,
                      "shell_before_bounds_local_m": shell_before,
                      "shell_after_bounds_local_m": shell_after,
                      "fit_scale_xy": scale,
                      "objects_in_export": len(asset.all_objects),
                      "preview": str(PREVIEW), "detail": str(DETAIL)}, indent=2))


if __name__ == "__main__":
    main()
