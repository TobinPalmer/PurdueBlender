"""Build the Delta Tau Delta Gamma Lambda chapter-house library from cited sources.

The footprint is derived from the Indiana 2018 LiDAR building-footprint service.
Vertical dimensions and architectural subdivision are explicitly estimated; the
public record found for this task does not contain plans or measured elevations.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


BUILDING_ID = "massing_delta_tau_delta_e06b0b5"
COLLECTION_NAME = f"Asset_{BUILDING_ID}"
SCENE_NAME = f"Building_{BUILDING_ID}"
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "audit" / "delta_tau_delta_e06b0b5"
GIS_SNAPSHOT = EVIDENCE_DIR / "sources" / "indiana_lidar_building_footprint_oid409940_2026-10-26.json"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"

# Project convention: local approximation with origin 40.4274, -86.9137.
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
WALL_TOP = 10.4  # estimate, not a measured elevation
RIDGE_TOP = 15.2  # estimate, not a measured elevation


def xy_from_lonlat(lon: float, lat: float) -> tuple[float, float]:
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return x, y


def material(name: str, color: tuple[float, float, float, float], roughness: float = 0.82):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.roughness = roughness
    return mat


def make_mesh_object(collection, name, vertices, faces, mat):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def make_box(collection, name, center, dims, mat, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Keep the box in the assigned library collection only.
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def create_body(collection, footprint, brick):
    n = len(footprint)
    verts = [(x, y, z) for z in (0.0, WALL_TOP) for x, y in footprint]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return make_mesh_object(collection, "DTD_Main_Brick_Envelope", verts, faces, brick)


def add_gable_roof(collection, footprint, slate, brick):
    # The public footprint is elongated north-south. This simple, steep Tudor
    # gable is a silhouette estimate, informed by available chapter-house views.
    xs = [p[0] for p in footprint]
    ys = [p[1] for p in footprint]
    xmin, xmax = min(xs) - 0.35, max(xs) + 0.35
    ymin, ymax = min(ys) - 0.35, max(ys) + 0.35
    xmid = (xmin + xmax) / 2
    eave = WALL_TOP
    ridge = RIDGE_TOP
    # Two pitched roof planes with an overhang. The flat surfaces deliberately
    # avoid pretending that unmeasured dormer and roof details are known.
    left = [(xmin, ymin, eave), (xmid, ymin, ridge), (xmid, ymax, ridge), (xmin, ymax, eave)]
    right = [(xmid, ymin, ridge), (xmax, ymin, eave), (xmax, ymax, eave), (xmid, ymax, ridge)]
    make_mesh_object(collection, "DTD_Steep_Tudor_Gable_Roof_West_Slope", left, [(0, 1, 2, 3)], slate)
    make_mesh_object(collection, "DTD_Steep_Tudor_Gable_Roof_East_Slope", right, [(0, 1, 2, 3)], slate)
    # End gable infill: visible under the north and south roof ends.
    for label, y in (("South", ymin + 0.35), ("North", ymax - 0.35)):
        verts = [(xmin, y, eave), (xmax, y, eave), (xmid, y, ridge)]
        make_mesh_object(collection, f"DTD_{label}_Gable_Infill", verts, [(0, 1, 2)], brick)
    # Ridge cap and three brick chimney stacks, all interpreted rather than measured.
    make_box(collection, "DTD_Ridge_Cap", (xmid, (ymin + ymax) / 2, ridge + 0.06), (0.22, ymax - ymin, 0.18), slate)
    for i, y in enumerate((ymin + 8.0, (ymin + ymax) / 2, ymax - 7.0), start=1):
        make_box(collection, f"DTD_Stack_Chimney_{i}", (xmid, y, ridge + 1.1), (0.8, 0.9, 2.2), brick)


def wall_panel(collection, name, a, b, fraction, z, width, height, depth, mat, outward):
    tangent = Vector((b[0] - a[0], b[1] - a[1]))
    length = tangent.length
    tangent.normalize()
    normal = Vector(outward).normalized()
    point = Vector((a[0], a[1])) + tangent * (length * fraction) + normal * (depth * 0.52)
    angle = math.atan2(tangent.y, tangent.x)
    return make_box(collection, name, (point.x, point.y, z), (width, depth, height), mat, angle)


def add_facade(collection, footprint, brick, glass, trim, stone, wood, slate):
    # Polygon ordering is clockwise in the local project plane. The longest west
    # exterior edge is used as the principal public frontage; exact entry side
    # remains uncertain because no plan or measured survey was located.
    edges = []
    for i, a in enumerate(footprint):
        b = footprint[(i + 1) % len(footprint)]
        length = math.dist(a, b)
        edges.append((length, a, b))
    _, west_a, west_b = max(edges, key=lambda item: item[0])
    tangent = Vector((west_b[0] - west_a[0], west_b[1] - west_a[1])).normalized()
    # For the clockwise ring, the left normal points outside along the long west wall.
    normal = Vector((-tangent.y, tangent.x)).normalized()
    for floor_index, z in enumerate((2.0, 5.1, 8.2), start=1):
        for i in range(7):
            fraction = 0.10 + i * 0.13
            wall_panel(collection, f"DTD_West_Window_F{floor_index}_{i+1}", west_a, west_b,
                       fraction, z, 1.18, 1.55, 0.16, glass, normal)
            wall_panel(collection, f"DTD_West_Stone_Lintel_F{floor_index}_{i+1}", west_a, west_b,
                       fraction, z + 0.86, 1.28, 0.12, 0.12, trim, normal)
    # Entry is centered on the same frontage; Tudor doorway treatment is
    # schematic, with a stone surround and dark timber door.
    wall_panel(collection, "DTD_Entrance_Door", west_a, west_b, 0.52, 1.28, 1.5, 2.55, 0.24, wood, normal)
    wall_panel(collection, "DTD_Entrance_Stone_Surround_Left", west_a, west_b, 0.52, 1.42, 0.14, 2.84, 0.34, stone, normal)
    # Windows along the east side balance the long residential elevations.
    east_edges = sorted(edges, key=lambda item: item[0], reverse=True)
    east_a, east_b = east_edges[1][1], east_edges[1][2]
    east_tangent = Vector((east_b[0] - east_a[0], east_b[1] - east_a[1])).normalized()
    east_normal = Vector((east_tangent.y, -east_tangent.x)).normalized()
    for floor_index, z in enumerate((2.0, 5.1, 8.2), start=1):
        for i in range(5):
            wall_panel(collection, f"DTD_East_Window_F{floor_index}_{i+1}", east_a, east_b,
                       0.12 + i * 0.18, z, 1.12, 1.48, 0.16, glass, east_normal)
    # A restrained projecting entry gable supports the Tudor silhouette.
    mid = Vector((west_a[0], west_a[1])) + tangent * (math.dist(west_a, west_b) * 0.52) + normal * 0.22
    half_width = 2.7
    base_z, apex_z = 3.3, 6.6
    x0, y0 = mid.x, mid.y
    x1, y1 = tangent.x * half_width, tangent.y * half_width
    make_mesh_object(collection, "DTD_Entry_Gable_Front", [(x0-x1,y0-y1,base_z),(x0+x1,y0+y1,base_z),(x0,y0,apex_z)], [(0,1,2)], brick)
    # A pair of shallow trim beams under the entry gable, not half-timbering.
    for i, sign in enumerate((-1, 1), start=1):
        p = mid + tangent * (sign * half_width * 0.68) + normal * 0.16
        make_box(collection, f"DTD_Entry_Gable_Beam_{i}", (p.x,p.y,4.8), (2.25,0.14,0.14), trim, math.atan2(tangent.y,tangent.x))
    # Small slate canopy makes the documented Tudor Revival entry legible in profile.
    # Its depth and exact form are illustrative because no elevations were found.
    front = mid + normal * 1.55
    back = mid - normal * 1.2
    for i, sign in enumerate((-1, 1), start=1):
        front_eave = front + tangent * (sign * half_width)
        back_eave = back + tangent * (sign * half_width)
        verts = [(front_eave.x, front_eave.y, base_z),
                 (back_eave.x, back_eave.y, base_z),
                 (back.x, back.y, apex_z),
                 (front.x, front.y, apex_z)]
        make_mesh_object(collection, f"DTD_Entry_Canopy_Roof_{i}", verts, [(0,1,2,3)], slate)
    # East-side stone lintels emphasize the repeated sash-window rhythm.
    # No facade detail is presented as measured.


def add_front_gables(collection, footprint, brick, slate, glass):
    """Add the visible multi-gable frontage documented by the chapter photo."""
    edges = []
    for i, a in enumerate(footprint):
        b = footprint[(i + 1) % len(footprint)]
        edges.append((math.dist(a, b), a, b))
    _, a, b = max(edges, key=lambda item: item[0])
    tangent = Vector((b[0] - a[0], b[1] - a[1])).normalized()
    normal = Vector((-tangent.y, tangent.x)).normalized()
    length = math.dist(a, b)
    eave = WALL_TOP
    peak = RIDGE_TOP
    half_width = 3.35
    depth = 4.1
    for index, fraction in enumerate((0.19, 0.50, 0.81), start=1):
        center = Vector((a[0], a[1])) + tangent * (length * fraction)
        # The photo shows these gabled bays projecting visibly forward of the
        # long wall, so carry the gable face past the main eave overhang.
        front = center + normal * 1.7
        back = center - normal * 3.0
        left_f = front - tangent * half_width
        right_f = front + tangent * half_width
        left_b = back - tangent * half_width
        right_b = back + tangent * half_width
        ridge_f = Vector((front.x, front.y, peak))
        ridge_b = Vector((back.x, back.y, peak))
        make_mesh_object(collection, f"DTD_Front_Gable_{index}_Brick_Infill",
                         [(left_f.x,left_f.y,eave),(right_f.x,right_f.y,eave),
                          (front.x,front.y,peak)], [(0,1,2)], brick)
        make_mesh_object(collection, f"DTD_Front_Gable_{index}_West_Slope",
                         [(left_f.x,left_f.y,eave),(ridge_f.x,ridge_f.y,ridge_f.z),
                          (ridge_b.x,ridge_b.y,ridge_b.z),(left_b.x,left_b.y,eave)],
                         [(0,1,2,3)], slate)
        make_mesh_object(collection, f"DTD_Front_Gable_{index}_East_Slope",
                         [(ridge_f.x,ridge_f.y,ridge_f.z),(right_f.x,right_f.y,eave),
                          (right_b.x,right_b.y,eave),(ridge_b.x,ridge_b.y,ridge_b.z)],
                         [(0,1,2,3)], slate)
        # One small upper sash per gable is visible in the chapter's snow photo.
        window = center + normal * 1.8
        make_box(collection, f"DTD_Front_Gable_{index}_Upper_Window",
                 (window.x, window.y, 12.35), (0.82, 0.14, 0.92), glass,
                 math.atan2(tangent.y, tangent.x))


def main():
    if not GIS_SNAPSHOT.exists():
        raise FileNotFoundError(GIS_SNAPSHOT)
    payload = json.loads(GIS_SNAPSHOT.read_text(encoding="utf-8-sig"))
    feature = payload["features"][0]
    assert feature["attributes"]["objectid"] == 409940
    source_ring = feature["geometry"]["rings"][0]
    footprint = [xy_from_lonlat(lon, lat) for lon, lat in source_ring[:-1]]

    scene = bpy.context.scene
    scene.name = SCENE_NAME
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(collection)
    else:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

    brick = material("DTD_Deep_Red_Brick", (0.34, 0.075, 0.047, 1.0))
    slate = material("DTD_Dark_Slate_Roof", (0.105, 0.125, 0.15, 1.0))
    glass = material("DTD_Deep_Recessed_Window_Glass", (0.055, 0.105, 0.16, 1.0), 0.24)
    trim = material("DTD_Light_Stone_Trim", (0.73, 0.67, 0.53, 1.0))
    stone = material("DTD_Entry_Stone", (0.55, 0.48, 0.37, 1.0))
    wood = material("DTD_Entrance_Wood", (0.16, 0.055, 0.028, 1.0))

    create_body(collection, footprint, brick)
    add_gable_roof(collection, footprint, slate, brick)
    add_facade(collection, footprint, brick, glass, trim, stone, wood, slate)
    add_front_gables(collection, footprint, brick, slate, glass)

    # Expose required asset identifiers and source trace on the primary shell.
    body = bpy.data.objects["DTD_Main_Brick_Envelope"]
    body["building_id"] = BUILDING_ID
    body["footprint_source"] = "Indiana Building Footprints, 2018 LiDAR, objectid 409940"
    body["vertical_geometry"] = "estimated only; no measured elevation or floor plan located"

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    render_world = bpy.data.worlds.get("DTD_Render_World") or bpy.data.worlds.new("DTD_Render_World")
    scene.world = render_world
    render_world.use_nodes = True
    render_world.node_tree.nodes.clear()
    world_output = render_world.node_tree.nodes.new("ShaderNodeOutputWorld")
    background = render_world.node_tree.nodes.new("ShaderNodeBackground")
    background.inputs["Color"].default_value = (0.42, 0.46, 0.52, 1.0)
    background.inputs["Strength"].default_value = 0.8
    render_world.node_tree.links.new(background.outputs["Background"], world_output.inputs["Surface"])
    scene.view_settings.view_transform = "AgX"
    # Render-only camera and lights remain outside the exported building collection.
    for obj in list(scene.objects):
        if obj.name.startswith("DTD_Render_"):
            bpy.data.objects.remove(obj, do_unlink=True)
    cx = sum(x for x, _ in footprint) / len(footprint)
    cy = sum(y for _, y in footprint) / len(footprint)
    bpy.ops.object.camera_add(location=(cx - 55, cy - 54, 30))
    camera = bpy.context.object
    camera.name = "DTD_Render_Camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 67
    direction = Vector((cx, cy, 7.0)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    for c in list(camera.users_collection):
        c.objects.unlink(camera)
    scene.collection.objects.link(camera)
    bpy.ops.object.light_add(type="AREA", location=(cx - 20, cy - 20, 42))
    light = bpy.context.object
    light.name = "DTD_Render_Key"
    light.data.energy = 4500
    light.data.shape = "DISK"
    light.data.size = 35
    light.rotation_euler = (math.radians(25), 0, math.radians(-35))
    for c in list(light.users_collection):
        c.objects.unlink(light)
    scene.collection.objects.link(light)
    scene.render.filepath = str(EVIDENCE_DIR / "previews" / "delta_tau_delta_three_quarter.png")
    bpy.ops.render.render(write_still=True)

    # Store an orthographic plan preview by moving only the render camera.
    plan_cx = (min(x for x, _ in footprint) + max(x for x, _ in footprint)) / 2
    plan_cy = (min(y for _, y in footprint) + max(y for _, y in footprint)) / 2
    camera.location = (plan_cx, plan_cy, 100)
    camera.data.ortho_scale = 90
    # Default Blender camera looks down -Z, with local Y aligned to north.
    camera.rotation_euler = (0.0, 0.0, 0.0)
    scene.render.filepath = str(EVIDENCE_DIR / "previews" / "delta_tau_delta_plan.png")
    bpy.ops.render.render(write_still=True)

    # Remove render rig from the library after previews so it remains building-only.
    for obj in (camera, light):
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.camera = None
    # Ensure the expected collection is visible and exports only assigned geometry.
    scene.render.filepath = "//"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    print("DTD_ASSET", ASSET_PATH)
    print("DTD_COLLECTION_OBJECTS", len(collection.objects))
    print("DTD_FOOTPRINT_XY", footprint)


if __name__ == "__main__":
    main()
