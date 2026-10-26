"""Rebuild the ABE building library from its matched Purdue GIS shell.

Coordinates are local meters (X east, Y north, Z up). The master owns
campus placement; this script never edits the manifest or campus master.
Run with Blender's bundled Python: blender --background --python <this file>.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVIDENCE = ROOT / "audit" / "abe" / "evidence"
GIS = EVIDENCE / "purdue_abe_gis_feature_406.json"
OUT = HERE / "agricultural_and_biological_engineering_abe.blend"
PREVIEW = EVIDENCE / "abe_exterior_overview.png"
DETAIL_PREVIEW = EVIDENCE / "abe_entry_detail.png"
ASSET_ID = "agricultural_and_biological_engineering_abe"
COLLECTION_NAME = f"Asset_{ASSET_ID}"

ORIGIN_LON = -86.9137
ORIGIN_LAT = 40.4274
SCALE_X = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
SCALE_Y = 111040.0
PLACEMENT_ORIGIN_XY_M = (-246.71846085020562, -632.8773862787382)


def material(name, color, roughness=0.72):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def box(collection, name, center, size, mat, bevel=0.0, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler.z = angle
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    collection.objects.link(ob)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Soft arris", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return ob


def polygon_prism(collection, name, points, z0, z1, mat):
    n = len(points)
    verts = [(x, y, z) for z in (z0, z1) for x, y in points]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, n * 2))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    ob["source_geometry"] = "Purdue GIS feature 406 outer ring"
    return ob


def simplify(points, threshold=0.75, collinear_tolerance=0.22):
    pts = points[:]
    changed = True
    while changed and len(pts) > 4:
        changed = False
        new = []
        for i, p in enumerate(pts):
            a = pts[i - 1]
            b = pts[(i + 1) % len(pts)]
            va, vb = Vector(a) - Vector(p), Vector(b) - Vector(p)
            span = (Vector(b) - Vector(a)).length
            distance = abs(va.x * vb.y - va.y * vb.x) / max(span, 1e-9)
            if (Vector(p) - Vector(a)).length < threshold or (Vector(p) - Vector(b)).length < threshold or distance < collinear_tolerance:
                changed = True
            else:
                new.append(p)
        if len(new) >= 4:
            pts = new
        else:
            break
    return pts


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with GIS.open(encoding="utf-8") as f:
        record = json.load(f)
    feature = record["feature"]
    attrs = feature["attributes"]
    rings = feature["geometry"]["rings"]
    ring = max(rings, key=len)
    # Convert to the project's campus approximation, then remove the manifest
    # placement translation. The modular asset itself must remain centered in
    # building-local coordinates; the master applies PLACEMENT_ORIGIN_XY_M.
    points = [
        ((lon - ORIGIN_LON) * SCALE_X - PLACEMENT_ORIGIN_XY_M[0],
         (lat - ORIGIN_LAT) * SCALE_Y - PLACEMENT_ORIGIN_XY_M[1])
        for lon, lat in ring[:-1]
    ]
    points = simplify(points)
    if len(points) < 4:
        raise RuntimeError("GIS footprint failed validity screening")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections,):
        for item in list(datablocks):
            if item.name != "Collection":
                datablocks.remove(item)
    scene = bpy.context.scene
    root = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(root)
    structural = bpy.data.collections.new("ABE_Structure_GIS_Footprint")
    facade = bpy.data.collections.new("ABE_Exterior_Brick_and_Glazing")
    roof = bpy.data.collections.new("ABE_Roof_and_Lab_Services")
    for c in (structural, facade, roof):
        root.children.link(c)

    brick = material("ABE warm red-brown brick (visual estimate)", (0.36, 0.115, 0.075))
    nodes = brick.node_tree.nodes
    links = brick.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.location = (350, 0)
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-650, 0)
    texture = nodes.new("ShaderNodeTexBrick")
    texture.location = (-400, 0)
    texture.inputs["Color1"].default_value = (0.42, 0.14, 0.09, 1)
    texture.inputs["Color2"].default_value = (0.29, 0.075, 0.05, 1)
    texture.inputs["Mortar"] .default_value = (0.22, 0.19, 0.17, 1)
    texture.inputs["Scale"].default_value = 2.5
    texture.inputs["Mortar Size"].default_value = 0.025
    texture.inputs["Mortar Smooth"].default_value = 0.006
    texture.inputs["Brick Width"].default_value = 0.56
    texture.inputs["Row Height"].default_value = 0.26
    links.new(texcoord.outputs["Object"], texture.inputs["Vector"])
    links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    limestone = material("ABE pale limestone (photographic cue)", (0.66, 0.61, 0.52))
    glass = material("ABE blue-grey glazing (photographic cue)", (0.075, 0.22, 0.28), 0.22)
    metal = material("ABE grey roof metal (estimate)", (0.32, 0.34, 0.35), 0.62)
    concrete = material("ABE concrete plinth (estimate)", (0.47, 0.46, 0.42))
    white = material("ABE trim (estimate)", (0.77, 0.74, 0.65))

    # Height/floors preserve the source's redevelopment history: three levels
    # of renovated offices plus a five-storey research addition. The exact
    # boundary between these areas is not established by the public sources.
    floor_h = 3.60
    z_grade, z_top = 0.0, 18.0
    polygon_prism(structural, "agricultural_and_biological_engineering_abe_GIS_outline_primary_shell", points, z_grade, z_top, brick)
    polygon_prism(structural, "ABE_GIS_foundation_plinth", points, -0.05, 0.55, concrete)

    centroid = (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))
    edges = []
    for i, p in enumerate(points):
        q = points[(i + 1) % len(points)]
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        if length < 2.5:
            continue
        tx, ty = dx / length, dy / length
        # Exterior normal from signed polygon winding.
        area = sum(points[j][0] * points[(j + 1) % len(points)][1] - points[(j + 1) % len(points)][0] * points[j][1] for j in range(len(points)))
        nx, ny = ((ty, -tx) if area > 0 else (-ty, tx))
        edges.append((p, q, length, tx, ty, nx, ny))

    # Repeated vertical window bays follow the 5-storey building sections.
    # Long expanses use glazed bays; brick sections retain punched windows.
    for edge_i, (p, q, length, tx, ty, nx, ny) in enumerate(edges):
        inset = 0.06
        usable = max(1.0, length - 0.9)
        bay_w = min(2.7, max(1.1, usable / max(1, round(usable / 3.3)) - 0.34))
        pitch = bay_w + 0.85
        count = max(1, int((usable + 0.15) / pitch))
        occupied = count * bay_w + (count - 1) * (pitch - bay_w)
        start = (length - occupied) / 2 + bay_w / 2
        tall_glazed = length > 16.0 and (edge_i % 4 in (1, 2))
        for floor in range(5):
            sill = 0.82 + floor * floor_h
            height = 2.12 if tall_glazed else 1.52
            if sill + height > z_top - 0.45:
                continue
            for j in range(count):
                u = start + j * pitch
                cx = p[0] + tx * u + nx * inset
                cy = p[1] + ty * u + ny * inset
                center = (cx, cy, sill + height / 2)
                if tall_glazed:
                    box(facade, f"ABE_curtainwall_{edge_i}_{floor}_{j}", center, (bay_w, 0.11, height), glass, 0.015, math.atan2(ty, tx))
                    # Slim pale piers and floor bands articulate the glass wing.
                    for side in (-1, 1):
                        box(facade, f"ABE_glazing_mullion_{edge_i}_{floor}_{j}_{side}", (cx + tx * bay_w * 0.47 * side, cy + ty * bay_w * 0.47 * side, center[2]), (0.09, 0.13, height + 0.08), metal, angle=math.atan2(ty, tx))
                else:
                    box(facade, f"ABE_punched_window_{edge_i}_{floor}_{j}", center, (bay_w, 0.10, height), glass, 0.025, math.atan2(ty, tx))
                box(facade, f"ABE_limestone_sill_{edge_i}_{floor}_{j}", (cx, cy, sill - 0.035), (bay_w + 0.18, 0.19, 0.08), white, angle=math.atan2(ty, tx))
        # Continuous light horizontal datums are visible in project photos.
        for level in (3, 5):
            z = 0.46 + level * floor_h
            box(facade, f"ABE_horizontal_limestone_belt_{edge_i}_{level}", ((p[0] + q[0]) / 2 + nx * 0.08, (p[1] + q[1]) / 2 + ny * 0.08, z), (length, 0.18, 0.10), white, angle=math.atan2(ty, tx))

    # Low roof parapet with a compact, explicitly estimated lab-services screen.
    polygon_prism(roof, "ABE_flat_roof_parapet_datum", points, z_top - 0.18, z_top + 0.12, metal)
    # The GIS centroid is not a surveyed plant location; the services are
    # positioned inboard so they do not alter the structural footprint.
    roof_x, roof_y = centroid
    box(roof, "ABE_roof_mechanical_screen_estimated", (roof_x, roof_y, 19.15), (17.0, 8.0, 2.2), metal, 0.10)
    for i in range(6):
        box(roof, f"ABE_roof_service_louver_{i}", (roof_x - 6 + i * 2.4, roof_y - 4.08, 19.15), (1.25, 0.06, 1.05), white)

    # Photographed signature entry; orientation to a particular GIS edge remains
    # provisional. This is a 1928 historic marker, not a surveyed door schedule.
    p, q, length, tx, ty, nx, ny = max(edges, key=lambda e: e[2])
    center_u = length * 0.51
    ex, ey = p[0] + tx * center_u + nx * 0.17, p[1] + ty * center_u + ny * 0.17
    heading = math.atan2(ty, tx)
    entry = box(facade, "ABE_photographed_limestone_entry_portal_approximate", (ex, ey, 2.15), (5.8, 0.42, 4.3), limestone, 0.08, heading)
    door = box(facade, "ABE_glazed_entry_pair_approximate", (ex + nx * 0.235, ey + ny * 0.235, 1.3), (2.2, 0.12, 2.6), glass, 0.02, heading)
    lintel = box(facade, "ABE_historic_1928_lintel_approximate", (ex + nx * 0.24, ey + ny * 0.24, 4.35), (3.9, 0.18, 0.54), white, 0.03, heading)
    bpy.ops.object.text_add(location=(ex + nx * 0.36, ey + ny * 0.36, 4.24), rotation=(math.pi / 2, 0, heading + math.pi))
    text = bpy.context.object
    text.name = "ABE_1928_entry_marker_photographic_cue"
    text.data.body = "1928"
    text.data.size = 0.34
    text.data.extrude = 0.004
    for c in list(text.users_collection):
        c.objects.unlink(text)
    facade.objects.link(text)
    text.data.materials.append(metal)

    # Only metadata inside this per-building asset; no shared file changes.
    root["building_id"] = ASSET_ID
    root["source_feature_id"] = 406
    root["footprint_crs"] = "Building-local meters (X east, Y north) derived from Purdue FeatureServer WGS84 snapshot; campus placement offset removed"
    root["footprint_status"] = "Purdue GIS exterior boundary; identity matched by building code, name and street address"
    root["vertical_status"] = "Estimated 18 m roof datum for five floors above grade; GIS 58 ft extrusion is a separate conflicting mapping attribute; basement not represented"
    root["facade_status"] = "Qualitative brick, limestone and glazing cues from project photographs; exact bay positions, retained/addition split and entrance side are approximate"
    root["interior_status"] = "Not modeled; no public as-built floor plans found"
    root["placement_origin_xy_m"] = list(PLACEMENT_ORIGIN_XY_M)
    root["coordinate_frame"] = "Building-local XY centered by subtracting placement_origin_xy_m; campus master adds placement_origin_xy_m exactly once"
    root["model_units"] = "meters"

    # Render-only setup lives outside the exported asset collection.
    world = bpy.data.worlds.new("ABE preview world")
    scene.world = world
    world.color = (0.35, 0.38, 0.41)
    cam_data = bpy.data.cameras.new("ABE_preview_camera")
    cam = bpy.data.objects.new("ABE_preview_camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (centroid[0] - 115, centroid[1] - 92, 65)
    direction = Vector((centroid[0], centroid[1], 8.5)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 112
    scene.camera = cam
    light_data = bpy.data.lights.new("ABE_preview_key", "AREA")
    light = bpy.data.objects.new("ABE_preview_key", light_data)
    scene.collection.objects.link(light)
    light.location = (centroid[0] - 30, centroid[1] - 50, 70)
    light_data.energy = 5400
    light_data.shape = "DISK"
    light_data.size = 42
    light.rotation_euler = (Vector((centroid[0], centroid[1], 8)) - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW)
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_percentage = 70

    # Hide render helpers from the library export.
    scene.camera.hide_set(True)
    light.hide_set(True)
    # Keep the asset and metadata in the named collection, as manifest expects.
    # Render helpers are direct scene objects and not linked into the asset.
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    bpy.ops.render.render(write_still=True)
    # A closer independent view documents the entry placement limitation and
    # the photographed 1928 stone lintel cue without changing the asset.
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 75
    cam.location = (ex + nx * 30, ey + ny * 30, 9)
    direction = Vector((ex + nx * 0.5, ey + ny * 0.5, 3.5)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 16
    scene.render.filepath = str(DETAIL_PREVIEW)
    bpy.ops.render.render(write_still=True)
    print(json.dumps({"asset": str(OUT), "collection": COLLECTION_NAME, "shell_vertices": len(points), "object_count": len(root.all_objects), "local_bounds_xy": [[min(p[0] for p in points), min(p[1] for p in points)], [max(p[0] for p in points), max(p[1] for p in points)]], "placement_origin_xy_m": PLACEMENT_ORIGIN_XY_M, "height_m": z_top, "preview": str(PREVIEW)}))


if __name__ == "__main__":
    main()
