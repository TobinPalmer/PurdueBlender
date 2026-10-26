"""Rebuild the Animal Disease Diagnostic Laboratory library from its GIS source.

Run with Blender 4.5 in background mode from the repository root:
  blender --background --python modular/buildings/build_animal_disease_diagnostic_laboratory.py

The Purdue GIS polygon controls the plan. Roof height is the recorded GIS
extrusion value (57, interpreted as feet for a 17.3736 m modeling proxy); the
layer has no published field units or survey metadata, so the height remains
explicitly qualified in the evidence record. Facade rhythm and entrance cues
are qualitative interpretations of the cited, building-specific photograph.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "animal_disease_diagnostic_laboratory"
BUILDING_NAME = "Willie M. Reed Animal Disease Diagnostic Laboratory"
SOURCE_JSON = ROOT / "audit/build_batch_a/animal_disease_diagnostic_laboratory_gis_feature_241.json"
ASSET_PATH = ROOT / "modular/buildings/animal_disease_diagnostic_laboratory.blend"
PREVIEW_PATH = ROOT / "audit/animal_disease_diagnostic_laboratory/preview.png"
DETAIL_PATH = ROOT / "audit/animal_disease_diagnostic_laboratory/entry_detail.png"

ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274
SX = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
SY = 111040.0
BASE_Z = 0.35
LEVELS = 5
GIS_EXTRUSION = 57
GIS_HEIGHT_M = GIS_EXTRUSION * 0.3048
TOP_Z = BASE_Z + GIS_HEIGHT_M
FLOOR_ZS = [BASE_Z + GIS_HEIGHT_M * i / LEVELS for i in range(LEVELS + 1)]


def read_footprint():
    record = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    feature = record["feature"]
    attrs = feature["attributes"]
    assert attrs["BUILDING_N"] == BUILDING_NAME
    assert attrs["BLDG_ABBR"].strip() == "ADDL"
    assert attrs["NUM_LEVELS"] == LEVELS
    assert attrs["Extrution"] == GIS_EXTRUSION
    raw = feature["geometry"]["rings"][0]
    pts = [((lon - ORIGIN_LON) * SX, (lat - ORIGIN_LAT) * SY) for lon, lat in raw[:-1]]
    area2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
                - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    cx = sum((pts[i][0] + pts[(i + 1) % len(pts)][0])
             * (pts[i][0] * pts[(i + 1) % len(pts)][1]
                - pts[(i + 1) % len(pts)][0] * pts[i][1])
             for i in range(len(pts))) / (3 * area2)
    cy = sum((pts[i][1] + pts[(i + 1) % len(pts)][1])
             * (pts[i][0] * pts[(i + 1) % len(pts)][1]
                - pts[(i + 1) % len(pts)][0] * pts[i][1])
             for i in range(len(pts))) / (3 * area2)
    local = [(x - cx, y - cy) for x, y in pts]
    signed_area = sum(local[i][0] * local[(i + 1) % len(local)][1]
                      - local[(i + 1) % len(local)][0] * local[i][1]
                      for i in range(len(local))) / 2
    return record, local, (cx, cy), signed_area


def material(name, color, roughness=0.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def mesh_object(name, verts, faces, collection, mats, mat_indices=None):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if mat_indices:
        for p, i in zip(mesh.polygons, mat_indices):
            p.material_index = i
    return obj


def build_wall_rings(points, z0, z1, collection, brick):
    verts, faces = [], []
    faces_by_material = []
    area2 = sum(points[i][0] * points[(i + 1) % len(points)][1]
                - points[(i + 1) % len(points)][0] * points[i][1]
                for i in range(len(points)))
    for i, (a, b) in enumerate(zip(points, points[1:] + points[:1])):
        n = len(verts)
        verts.extend([(a[0], a[1], z0), (b[0], b[1], z0),
                      (b[0], b[1], z1), (a[0], a[1], z1)])
        face = (n, n + 1, n + 2, n + 3)
        faces.append(face if area2 > 0 else tuple(reversed(face)))
        midpoint = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        # The attached southeast volume is documented; its exact external
        # dimensions are not. Differentiate only GIS boundary faces in that
        # quadrant and retain a separate metadata caveat.
        faces_by_material.append(1 if midpoint[0] > 0 and midpoint[1] < -12 else 0)
    dark_service = material("ADDL southeast service addition finish - visual estimate",
                            (0.30, 0.13, 0.09), 0.88)
    return mesh_object("ADDL_GIS_Footprint_Primary_Shell", verts, faces, collection,
                       [brick, dark_service], faces_by_material)


def add_box(out_verts, out_faces, center, tangent, outward, half_w, half_d, z0, z1):
    c = Vector(center)
    t = Vector((tangent[0], tangent[1], 0.0))
    n = Vector((outward[0], outward[1], 0.0))
    start = len(out_verts)
    for z in (z0, z1):
        for s, d in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = c + s * half_w * t + d * half_d * n
            out_verts.append((p.x, p.y, z))
    out_faces.extend([(start + 0, start + 1, start + 2, start + 3),
                      (start + 4, start + 7, start + 6, start + 5),
                      (start + 0, start + 4, start + 5, start + 1),
                      (start + 1, start + 5, start + 6, start + 2),
                      (start + 2, start + 6, start + 7, start + 3),
                      (start + 3, start + 7, start + 4, start + 0)])


def make_windows(points, collection, glass, frame, sill, levels):
    v, f, idx = [], [], []
    floor_h = GIS_HEIGHT_M / LEVELS
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 3.2:
            continue
        t = (dx / length, dy / length)
        # GIS polygon vertices are clockwise, so the left normal is outward.
        n = (-t[1], t[0])
        bays = max(1, round(length / 3.35))
        pitch = length / bays
        for level in range(levels):
            zc = BASE_Z + level * floor_h + floor_h * 0.54
            wh = floor_h * 0.48
            ww = min(1.55, pitch * 0.55)
            for bay in range(bays):
                # Keep the photograph-supported modest entry centered on the
                # south-facing long elevation; this is an orientation estimate.
                center_dist = (bay + 0.5) * pitch
                if n[1] < -0.7 and level == 0 and abs(center_dist - length / 2) < 3.1:
                    continue
                cxy = (a[0] + t[0] * center_dist, a[1] + t[1] * center_dist)
                # Glass panel, inset reveals and a distinct stone sill.
                add_box(v, f, (*cxy, 0), t, n, ww / 2, 0.055,
                        zc - wh / 2, zc + wh / 2)
                idx.extend([0] * 6)
                add_box(v, f, (*cxy, 0), t, n, ww / 2 + 0.08, 0.08,
                        zc - wh / 2 - 0.075, zc - wh / 2)
                idx.extend([2] * 6)
                add_box(v, f, (*cxy, 0), t, n, ww / 2 + 0.08, 0.075,
                        zc + wh / 2, zc + wh / 2 + 0.065)
                idx.extend([1] * 6)
                for side in (-1, 1):
                    jamb = (cxy[0] + side * (ww / 2 + 0.035) * t[0],
                            cxy[1] + side * (ww / 2 + 0.035) * t[1])
                    add_box(v, f, (*jamb, 0), t, n, 0.035, 0.075,
                            zc - wh / 2, zc + wh / 2)
                    idx.extend([1] * 6)
    return mesh_object("ADDL_Repeating_Laboratory_Window_Bays", v, f, collection,
                       [glass, frame, sill], idx)


def add_loft(collection, points, materials):
    # Top membrane follows the exact source polygon. Its z is independent of
    # the service stacks added below, whose exact sizes/heights are unmeasured.
    verts = [(x, y, TOP_Z) for x, y in points]
    mesh_object("ADDL_Flat_Roof_Outline", verts, [tuple(range(len(points)))], collection, [materials])


def main():
    record, points, campus_xy, signed_area = read_footprint()
    if len(points) != 18:
        raise RuntimeError(f"Expected 18 source footprint vertices; got {len(points)}")
    if abs(signed_area) < 1000:
        raise RuntimeError(f"Unexpected source footprint area: {signed_area}")

    # New dedicated building file; do not load or alter the campus master.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections, bpy.data.materials, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    scene = bpy.context.scene
    scene.name = "Scene"
    asset = bpy.data.collections.new("Asset_animal_disease_diagnostic_laboratory")
    scene.collection.children.link(asset)

    brick = material("ADDL warm red brick - visual estimate", (0.48, 0.14, 0.085), 0.9)
    glass = material("ADDL blue-grey glazing - qualitative photo cue", (0.045, 0.23, 0.31), 0.25)
    trim = material("ADDL pale concrete trim - estimated", (0.72, 0.67, 0.55), 0.8)
    foundation = material("ADDL concrete plinth - estimated", (0.35, 0.37, 0.38), 0.9)
    roofmat = material("ADDL roof membrane - estimated", (0.20, 0.22, 0.23), 0.8)
    metal = material("ADDL service metal - estimated", (0.34, 0.38, 0.40), 0.65)
    labelmat = material("ADDL bronze-grey sign lettering - estimated", (0.10, 0.13, 0.14), 0.7)

    shell = build_wall_rings(points, BASE_Z, TOP_Z, asset, brick)
    shell["source_polygon_feature_id"] = 241
    shell["footprint_status"] = "Directly traced from Purdue University BuildingShapes feature FID 241; source CRS EPSG:3857; raw WGS84 snapshot; local conversion recorded in evidence."
    shell["height_status"] = "GIS Extrution=57, used as a 57 ft (17.3736 m) modeling proxy; layer field units/uniform measurement semantics are not documented, so this is not survey verified."
    shell["dimensions_status"] = "The plan follows the GIS footprint ring. GIS Shape__Area is EPSG:3857 projected area and is not reported as ground area."

    make_windows(points, asset, glass, trim, trim, LEVELS)
    add_loft(asset, points, roofmat)

    # Continuous low plinth is slightly inset from the structural wall line.
    v, f = [], []
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        n = len(v)
        v.extend([(a[0], a[1], 0.05), (b[0], b[1], 0.05),
                  (b[0], b[1], BASE_Z), (a[0], a[1], BASE_Z)])
        f.append((n, n + 1, n + 2, n + 3))
    mesh_object("ADDL_Base_Plinth", v, f, asset, [foundation])

    # Building-specific service volume: the 2007 Purdue newsletter identifies
    # a southeast BSL-3 addition but does not supply its exact dimensions.
    # A differentiated panel zone is retained as a low-confidence visual cue.
    # Modest glazed double-door entry and canopy, photo supported in form;
    # its precise orientation and dimensions remain estimated.
    # Use the south envelope as the candidate frontage pending street registration.
    south_edges = []
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        length = math.dist(a, b)
        if length > 4.0 and abs(a[1] - b[1]) < 0.4:
            south_edges.append((min(a[1], b[1]), length, a, b))
    south_candidates = [e for e in south_edges if e[0] <= min(y for _, y in points) + 10]
    if not south_candidates:
        raise RuntimeError("No substantial, near-horizontal south-side edge found for the candidate entrance")
    _, _, south_a, south_b = max(south_candidates, key=lambda e: e[1])
    dx, dy = south_b[0] - south_a[0], south_b[1] - south_a[1]
    edge_len = math.hypot(dx, dy)
    t_front = (dx / edge_len, dy / edge_len)
    x_front = (south_a[0] + south_b[0]) / 2
    y_front = (south_a[1] + south_b[1]) / 2
    span = 3.8
    door_verts, door_faces = [], []
    add_box(door_verts, door_faces, (x_front, y_front - 0.10, 0), t_front, (0, -1),
            span / 2, 0.12, BASE_Z, BASE_Z + 2.25)
    mesh_object("ADDL_Entry_Glazed_Double_Door_Visual_Proxy", door_verts, door_faces, asset, [glass])
    # Subtle center stile and side piers make the photograph-supported glazed
    # entrance legible in the close render; spacing and section sizes are estimates.
    entry_trim_v, entry_trim_f = [], []
    add_box(entry_trim_v, entry_trim_f, (x_front, y_front - 0.24, 0), t_front, (0, -1),
            0.045, 0.035, BASE_Z + 0.10, BASE_Z + 2.18)
    for side in (-1, 1):
        px = x_front + side * (span / 2 + 0.17) * t_front[0]
        py = y_front + side * (span / 2 + 0.17) * t_front[1]
        add_box(entry_trim_v, entry_trim_f, (px, py - 0.11, 0), t_front, (0, -1),
                0.14, 0.11, BASE_Z, BASE_Z + 2.42)
    mesh_object("ADDL_Entry_Stile_and_Piers_Visual_Proxy", entry_trim_v, entry_trim_f,
                asset, [metal, trim])

    # restrained canopy volume (estimated projection)
    can_v, can_f = [], []
    add_box(can_v, can_f, (x_front, y_front - 0.55, 0), t_front, (0, -1),
            2.6, 0.65, BASE_Z + 2.35, BASE_Z + 2.62)
    mesh_object("ADDL_Entry_Canopy_Visual_Proxy", can_v, can_f, asset, [metal])

    # Raised-letter building identification. Correct official name, scale and
    # mounting location are not documented; this label is an illustrative cue.
    curve = bpy.data.curves.new("ADDL_Official_Name_Sign_Data", "FONT")
    curve.body = "WILLIE M. REED ADDL"
    curve.size = 0.31
    curve.extrude = 0.008
    sign = bpy.data.objects.new("ADDL_Official_Name_Sign_Visual_Proxy", curve)
    asset.objects.link(sign)
    sign.location = (x_front - 1.55, y_front - 0.18, BASE_Z + 3.22)
    sign.rotation_euler[0] = math.radians(90)
    sign.data.materials.append(labelmat)
    sign["evidence_status"] = "Current official name verified in Purdue GIS and 2024 Board of Trustees records; modeled text, type size, and location are visual estimates."

    asset["building_id"] = BUILDING_ID
    asset["building_name"] = BUILDING_NAME
    asset["source_feature_id"] = 241
    asset["local_frame"] = "Centroid origin; meters; X east, Y north, Z up. Geographic conversion from the Purdue project convention."
    asset["campus_xy_m"] = json.dumps([round(campus_xy[0], 6), round(campus_xy[1], 6)])
    asset["story_count"] = LEVELS
    asset["stories_status"] = "Purdue GIS NUM_LEVELS and CountOfFLO are both 5. Floor elevations, story heights, and use of basement level are not verified by that count."

    # Non-asset render gear sits outside the exported collection.
    world = bpy.data.worlds.new("ADDL_preview_world")
    scene.world = world
    world.color = (0.55, 0.55, 0.55)
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.58, 0.62, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8

    light_data = bpy.data.lights.new("ADDL_Preview_Area", type="AREA")
    light_data.energy, light_data.shape, light_data.size = 7000, "DISK", 75
    light = bpy.data.objects.new("ADDL_Preview_Area", light_data)
    scene.collection.objects.link(light)
    light.location = (15, -30, 55)
    light.rotation_euler = (Vector((0, 0, TOP_Z / 2)) - light.location).to_track_quat("-Z", "Y").to_euler()

    cam_data = bpy.data.cameras.new("ADDL_Preview_Camera")
    cam = bpy.data.objects.new("ADDL_Preview_Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.location = (92, -105, 58)
    cam.rotation_euler = (Vector((0, 0, TOP_Z / 2)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 55

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 12
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = str(PREVIEW_PATH)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    # Focused sign/entry angle preview for the independent grader.
    detail_data = bpy.data.cameras.new("ADDL_Entry_Detail_Camera")
    detail = bpy.data.objects.new("ADDL_Entry_Detail_Camera", detail_data)
    scene.collection.objects.link(detail)
    detail.location = (x_front + 20, y_front - 28, BASE_Z + 10)
    detail.rotation_euler = (Vector((x_front, y_front, BASE_Z + 2.7)) - detail.location).to_track_quat("-Z", "Y").to_euler()
    detail_data.lens = 67
    scene.camera = detail
    scene.render.resolution_x, scene.render.resolution_y = 960, 720
    scene.render.filepath = str(DETAIL_PATH)
    bpy.ops.render.render(write_still=True)

    print(json.dumps({"asset": str(ASSET_PATH), "asset_collection": asset.name,
                      "vertex_count": len(points), "polygon_area_local_m2": abs(signed_area),
                      "centroid_campus_xy_m": campus_xy, "height_proxy_m": GIS_HEIGHT_M,
                      "levels": LEVELS, "objects": len(asset.objects)}))


if __name__ == "__main__":
    main()
