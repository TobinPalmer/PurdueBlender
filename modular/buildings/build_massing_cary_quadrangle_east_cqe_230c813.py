"""Build a detailed, source-backed campus-coordinate Cary East library.

The official Purdue FID 639 outline supplies the plan. Historic records support
the brick/stone Tudor-Gothic character, three stories plus basement, and a
42 x 269 ft historical envelope. Roof details and facade rhythm are interpreted
from archival Cary imagery and current orthophotography, with uncertainty
recorded in the dedicated evidence folder.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_east_cqe_230c813"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EVIDENCE = ROOT / "audit" / ASSET_ID
SOURCE = EVIDENCE / "sources" / "purdue_building_shapes_fid639_cqe_2026-10-25.geojson"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"

SIMPLIFY_TOLERANCE_M = 0.12
FOUNDATION_HEIGHT_M = 0.9
WALL_TOP_M = 10.65
ROOF_EAVES_M = 10.75
ROOF_RIDGE_M = 14.63  # GIS Extrution=48, interpreted as approximate feet.
FLOOR_BASES_M = (0.45, 3.65, 6.85)
FLOOR_TO_FLOOR_M = 3.2
FEET_TO_METERS = 1200.0 / 3937.0


def project_lon_lat(lon, lat):
    """Documented project conversion from WGS84 to campus coordinates."""
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    return x, y


def point_segment_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    denom = dx*dx + dy*dy
    if denom <= 1e-12:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/denom))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))


def simplify_ring(points, tolerance):
    pts = list(points)
    if len(pts) > 1 and math.dist(pts[0], pts[-1]) < 1e-8:
        pts.pop()
    changed = True
    while changed and len(pts) > 8:
        changed = False
        for i, p in enumerate(pts):
            if point_segment_distance(p, pts[(i-1) % len(pts)], pts[(i+1) % len(pts)]) <= tolerance:
                pts.pop(i)
                changed = True
                break
    return pts


def signed_area(points):
    return 0.5 * sum(points[i][0]*points[(i+1) % len(points)][1] -
                     points[(i+1) % len(points)][0]*points[i][1]
                     for i in range(len(points)))


def make_material(name, color, roughness=0.78, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


def create_prism(name, points, z0, z1, side_material, cap_material, collection):
    n = len(points)
    verts = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = [(i, (i+1) % n, n+(i+1) % n, n+i) for i in range(n)]
    faces.extend([tuple(range(n, 2*n)), tuple(reversed(range(n)))])
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(side_material)
    mesh.materials.append(cap_material)
    for poly in mesh.polygons:
        if len(poly.vertices) == n and min(poly.vertices) >= n:
            poly.material_index = 1
    return obj


def oriented_box_vertices(center, width, depth, height, angle):
    cx, cy, cz = center
    c, s = math.cos(angle), math.sin(angle)
    result = []
    for z in (-height/2, height/2):
        for y in (-depth/2, depth/2):
            for x in (-width/2, width/2):
                result.append((cx+x*c-y*s, cy+x*s+y*c, cz+z))
    return result


BOX_FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


def add_box(buffer, center, width, depth, height, angle):
    verts = oriented_box_vertices(center, width, depth, height, angle)
    offset = len(buffer["verts"])
    buffer["verts"].extend(verts)
    buffer["faces"].extend(tuple(offset+i for i in f) for f in BOX_FACES)


def create_box_batch(name, buffer, material, collection):
    if not buffer["verts"]:
        return None
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(buffer["verts"], [], buffer["faces"])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    return obj


def create_gable_roof(name, axis_origin, longitudinal, crosswise, u_bounds, v_bounds,
                      eaves_z, ridge_z, material, collection, overhang=0.45):
    u0, u1 = u_bounds[0]-overhang, u_bounds[1]+overhang
    v0, v1 = v_bounds[0]-overhang, v_bounds[1]+overhang
    vm = (v0+v1)/2

    def xyz(u, v, z):
        return (axis_origin[0] + longitudinal[0]*u + crosswise[0]*v,
                axis_origin[1] + longitudinal[1]*u + crosswise[1]*v, z)

    verts = [xyz(u0, v0, eaves_z), xyz(u0, vm, ridge_z), xyz(u0, v1, eaves_z),
             xyz(u1, v0, eaves_z), xyz(u1, vm, ridge_z), xyz(u1, v1, eaves_z)]
    faces = [(0, 3, 4, 1), (1, 4, 5, 2), (0, 1, 2), (3, 5, 4)]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    return obj


def create_cross_gable_bay(name, center_u, outside_v, outward_sign, longitudinal, crosswise,
                           base_z, ridge_z, width, depth, brick_material,
                           roof_material, collection):
    """Create a conservative projecting cross-gable bay on a long elevation.

    The 1928 Cary exterior photograph indexed by Purdue Archives shows repeated
    projecting gables. The image is Cary-complex context and not explicitly
    tagged East, so these are simplified architectural interpretations.
    """
    half = width / 2
    inside_v = outside_v - outward_sign*depth

    def xyz(u, v, z):
        return (longitudinal[0]*u + crosswise[0]*v,
                longitudinal[1]*u + crosswise[1]*v, z)

    # Triangular gable end, duplicated at its inner plane for a closed mesh.
    front = [xyz(center_u-half, outside_v, base_z),
             xyz(center_u+half, outside_v, base_z),
             xyz(center_u, outside_v, ridge_z)]
    back = [xyz(center_u-half, inside_v, base_z),
            xyz(center_u+half, inside_v, base_z),
            xyz(center_u, inside_v, ridge_z)]
    verts = front + back
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1),
             (1, 4, 5, 2), (2, 5, 3, 0)]
    mesh = bpy.data.meshes.new(name + "EndMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    end = bpy.data.objects.new(name + "_Brick_Gable_End", mesh)
    collection.objects.link(end)
    mesh.materials.append(brick_material)

    # Two simple pitched roof planes extend from the projecting gable to the
    # main roof ridge. This conveys the roof silhouette without fake dormers.
    roof_verts = [xyz(center_u-half, outside_v, base_z),
                  xyz(center_u, outside_v, ridge_z),
                  xyz(center_u+half, outside_v, base_z),
                  xyz(center_u-half, inside_v, base_z),
                  xyz(center_u, inside_v, ridge_z),
                  xyz(center_u+half, inside_v, base_z)]
    roof_faces = [(0, 3, 4, 1), (1, 4, 5, 2)]
    roof_mesh = bpy.data.meshes.new(name + "RoofMesh")
    roof_mesh.from_pydata(roof_verts, [], roof_faces)
    roof_mesh.update()
    roof = bpy.data.objects.new(name + "_Slate_Roof", roof_mesh)
    collection.objects.link(roof)
    roof_mesh.materials.append(roof_material)


def create_pointed_entry(name, center_xy, tangent, normal, angle, materials, collection):
    """A shallow stone pointed-arch surround over a dark recessed door panel."""
    stone, door, glass = materials
    cx, cy = center_xy

    def build_poly(name, outline, material, depth):
        # outline coordinates are (along-wall offset, z); extrude along wall normal.
        verts = []
        for d in (-depth/2, depth/2):
            for u, z in outline:
                verts.append((cx + tangent[0]*u + normal[0]*d,
                              cy + tangent[1]*u + normal[1]*d, z))
        n = len(outline)
        faces = [tuple(range(n, 2*n)), tuple(reversed(range(n)))]
        faces.extend((i, (i+1) % n, n+(i+1) % n, n+i) for i in range(n))
        mesh = bpy.data.meshes.new(name + "Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        mesh.materials.append(material)
        return obj

    outer = [(-1.65, 0.1), (1.65, 0.1), (1.65, 2.45), (0.0, 4.1), (-1.65, 2.45)]
    inner = [(-1.25, 0.12), (1.25, 0.12), (1.25, 2.30), (0.0, 3.55), (-1.25, 2.30)]
    build_poly(name + "_Stone_Arch", outer, stone, 0.24)
    build_poly(name + "_Dark_Pointed_Door", inner, door, 0.12)
    # Door muntins and a small transom are intentionally schematic.
    add_box(GLASS_DETAIL_BUFFER, (cx+normal[0]*0.20, cy+normal[1]*0.20, 2.55),
            1.55, 0.06, 0.12, angle)


def read_source():
    data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    feature = data["features"][0]
    ring = feature["geometry"]["coordinates"][0]
    projected = [project_lon_lat(lon, lat) for lon, lat in ring]
    return simplify_ring(projected, SIMPLIFY_TOLERANCE_M), feature, len(ring)-1


GLASS_DETAIL_BUFFER = {"verts": [], "faces": []}


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    asset_collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset_collection)
    preview_collection = bpy.data.collections.new("CQE_Preview_Setup")
    scene.collection.children.link(preview_collection)
    return scene, asset_collection, preview_collection


def build_geometry(points, feature, raw_vertex_count, collection):
    global GLASS_DETAIL_BUFFER
    GLASS_DETAIL_BUFFER = {"verts": [], "faces": []}
    brick = make_material("CQE_Purdue_Red_Brick", (0.42, 0.12, 0.085))
    brick_dark = make_material("CQE_Shadowed_Brick", (0.29, 0.075, 0.05))
    limestone = make_material("CQE_Bedford_Limestone_Interpretation", (0.68, 0.64, 0.54))
    foundation = make_material("CQE_Stone_Foundation", (0.43, 0.43, 0.39))
    roof_mat = make_material("CQE_Dark_Slate_Roof", (0.16, 0.19, 0.22), roughness=0.9)
    glass = make_material("CQE_Dark_Window_Glass", (0.09, 0.16, 0.20), roughness=0.28)
    door_mat = make_material("CQE_Deep_Wood_Door", (0.12, 0.075, 0.04), roughness=0.7)
    metal = make_material("CQE_Window_Sash", (0.76, 0.72, 0.61), roughness=0.55)

    create_prism("CQE_Stone_Foundation_Shell", points, 0.0, FOUNDATION_HEIGHT_M,
                 foundation, foundation, collection)
    create_prism("CQE_Brick_Wall_Shell", points, FOUNDATION_HEIGHT_M, WALL_TOP_M,
                 brick, brick, collection)

    area = signed_area(points)
    sign = 1.0 if area < 0 else -1.0
    min_x, max_x = min(p[0] for p in points), max(p[0] for p in points)
    min_y, max_y = min(p[1] for p in points), max(p[1] for p in points)
    center = (sum(p[0] for p in points)/len(points), sum(p[1] for p in points)/len(points))

    # Main building axis: the long axis is nearly north-south. Derive it from the
    # oriented bounding rectangle of the actual GIS outline.
    dominant = max(((b[0]-a[0], b[1]-a[1]) for a, b in zip(points, points[1:]+points[:1])),
                   key=lambda v: math.hypot(*v))
    long_axis = Vector(dominant).normalized()
    if long_axis.y < 0:
        long_axis = -long_axis
    cross_axis = Vector((long_axis.y, -long_axis.x))
    us = [p[0]*long_axis.x + p[1]*long_axis.y for p in points]
    vs = [p[0]*cross_axis.x + p[1]*cross_axis.y for p in points]
    u_bounds = (min(us), max(us))
    v_bounds = (min(vs), max(vs))
    # u and v are dot products of absolute world coordinates, so reconstruct
    # from (0,0); adding the footprint center again would translate the roof.
    axis_origin = (0.0, 0.0)

    # Longitudinal slate gable roof: roof height is supported only approximately
    # by the GIS extrusion field interpreted as 48 ft; it is not a survey datum.
    create_gable_roof("CQE_Main_Slate_Gable_Roof", axis_origin,
                      (long_axis.x, long_axis.y), (cross_axis.x, cross_axis.y),
                      u_bounds, v_bounds, ROOF_EAVES_M, ROOF_RIDGE_M,
                      roof_mat, collection)

    window_buffer = {"verts": [], "faces": []}
    frame_buffer = {"verts": [], "faces": []}
    belt_buffer = {"verts": [], "faces": []}
    entry_hood_buffer = {"verts": [], "faces": []}
    pilaster_buffer = {"verts": [], "faces": []}
    detail_count = 0
    west_candidates = []
    window_width = 1.48
    window_height = 1.72
    step = 3.20

    for i, start in enumerate(points):
        end = points[(i+1) % len(points)]
        dx, dy = end[0]-start[0], end[1]-start[1]
        length = math.hypot(dx, dy)
        if length < 2.6:
            continue
        tangent = (dx/length, dy/length)
        normal = (-tangent[1]*sign, tangent[0]*sign)
        angle = math.atan2(tangent[1], tangent[0])
        along_u = ((start[0]+end[0])/2)*long_axis.x + ((start[1]+end[1])/2)*long_axis.y
        if normal[0] < -0.82 and u_bounds[0]+0.26*(u_bounds[1]-u_bounds[0]) < along_u < u_bounds[1]-0.26*(u_bounds[1]-u_bounds[0]):
            west_candidates.append((length, start, end, tangent, normal, angle))

        # Repeated vertical window bays, three visible stories based on the
        # building-specific historical record. Bay counts follow wall lengths.
        bays = max(1, int(round((length-0.8)/step)))
        for floor_index, floor_base in enumerate(FLOOR_BASES_M):
            zc = floor_base + 1.86
            for bay in range(bays):
                t = (bay+0.5)/bays
                cx = start[0] + dx*t + normal[0]*0.10
                cy = start[1] + dy*t + normal[1]*0.10
                add_box(window_buffer, (cx, cy, zc), window_width, 0.15, window_height, angle)
                # Stone sills/lintels and narrow sash members.
                add_box(frame_buffer, (cx, cy, zc-window_height/2-0.055), window_width+0.16, 0.25, 0.11, angle)
                add_box(frame_buffer, (cx, cy, zc+window_height/2+0.055), window_width+0.16, 0.25, 0.11, angle)
                for side in (-1, 1):
                    off = side*(window_width/2+0.035)
                    add_box(frame_buffer, (cx+tangent[0]*off, cy+tangent[1]*off, zc),
                            0.09, 0.24, window_height+0.12, angle)
                add_box(GLASS_DETAIL_BUFFER, (cx, cy, zc), 0.07, 0.22, window_height-0.12, angle)
                detail_count += 1

        # Horizontal stone belt courses support the three-story reading.
        mid = ((start[0]+end[0])/2+normal[0]*0.06,
               (start[1]+end[1])/2+normal[1]*0.06)
        for z in (3.55, 6.75, 9.95):
            add_box(belt_buffer, (mid[0], mid[1], z), length, 0.16, 0.13, angle)

        # A modest pilaster at major wall segments echoes the stone/brick palette.
        for t in (0.03, 0.97):
            px = start[0]+dx*t+normal[0]*0.07
            py = start[1]+dy*t+normal[1]*0.07
            add_box(pilaster_buffer, (px, py, 5.25), 0.32, 0.24, 9.1, angle)

    # The 2023 orthophoto supports an interrupted roof silhouette. A Purdue
    # Archives exterior photo dated 1928 shows repeated cross-gable bays in a
    # Cary building, but is not individually labeled CQE; keep these forms
    # simplified and explicitly interpreted rather than asserting exact count.
    v_mid = (v_bounds[1]+v_bounds[0])/2
    vhalf = (v_bounds[1]-v_bounds[0])/2
    u_span = u_bounds[1]-u_bounds[0]
    cross_gable_count = 0
    for side in (-1, 1):
        outside_v = v_mid + side*(vhalf+0.18)
        for frac in (0.10, 0.50, 0.90):
            u = u_bounds[0] + u_span*frac
            create_cross_gable_bay(
                f"CQE_Cross_Gable_{side}_{frac:.2f}", u, outside_v, side,
                (long_axis.x, long_axis.y), (cross_axis.x, cross_axis.y),
                ROOF_EAVES_M, min(ROOF_RIDGE_M+0.45, 15.1), 7.6, 3.7,
                brick, roof_mat, collection)
            # Small attic windows are visible in the archival Cary gable
            # photographs and also make the GIS five-level count compatible
            # with three documented stories plus basement only as a possibility.
            window_u = u
            window_v = outside_v + side*0.06
            window_z = ROOF_EAVES_M + 2.35
            facade_angle = math.atan2(long_axis.y, long_axis.x)
            add_box(frame_buffer,
                    (long_axis.x*window_u + cross_axis.x*window_v,
                     long_axis.y*window_u + cross_axis.y*window_v, window_z),
                    1.42, 0.24, 1.62, facade_angle)
            add_box(GLASS_DETAIL_BUFFER,
                    (long_axis.x*window_u + cross_axis.x*(window_v+side*0.13),
                     long_axis.y*window_u + cross_axis.y*(window_v+side*0.13), window_z),
                    1.12, 0.13, 1.32, facade_angle)
            cross_gable_count += 1

    create_box_batch("CQE_Window_Glass_Bays", window_buffer, glass, collection)
    create_box_batch("CQE_Limestone_Window_Trim", frame_buffer, limestone, collection)
    create_box_batch("CQE_Story_Belt_Courses", belt_buffer, limestone, collection)
    create_box_batch("CQE_Brick_and_Stone_Pilasters", pilaster_buffer, brick_dark, collection)
    # Entrance is placed on the west-facing long elevation, toward Cary's central
    # quadrangle. Its exact bay/location is an architectural interpretation.
    entry = max(west_candidates, key=lambda item: item[0], default=None)
    if entry:
        length, start, end, tangent, normal, angle = entry
        t = 0.5
        cx = start[0]+(end[0]-start[0])*t+normal[0]*0.14
        cy = start[1]+(end[1]-start[1])*t+normal[1]*0.14
        create_pointed_entry("CQE_Courtyard_Entrance", (cx, cy), tangent, normal,
                             angle, (limestone, door_mat, glass), collection)
        # A stone projecting hood and small upper bay mark the same entry.
        add_box(entry_hood_buffer, (cx+normal[0]*0.65, cy+normal[1]*0.65, 4.35),
                4.6, 1.15, 0.27, angle)
        create_box_batch("CQE_Entry_Stone_Hood", entry_hood_buffer, limestone, collection)

    create_box_batch("CQE_Door_Transom_Details", GLASS_DETAIL_BUFFER, metal, collection)

    collection["asset_id"] = ASSET_ID
    collection["building_name"] = "Franklin Levering Cary Quadrangle (East)"
    collection["source_feature"] = "Purdue BuildingShapesZip4 FID 639, BLDG_ABBR CQE"
    collection["coordinate_contract"] = "Simple massing asset in campus world coordinates; X east, Y north, Z up, meters."
    collection["height_status"] = "estimated, not surveyed; 2018 3DEP NDHM inside source footprint has median surface height 14.08 m (p10-p90 11.94-15.89 m), which corroborates the modeled maximum 15.08 m. GIS Extrution=48 has undocumented units; its tentative feet interpretation is not the sole height basis. Historic source says three stories plus basement; GIS level count conflict remains unresolved."
    collection["source_uncertainty"] = "Facade bays, entrance position, cross-gable count, and Tudor-Gothic trim are approximate interpretations. Purdue Archives exterior images are Cary-wide context and do not identify CQE. Historic three-stories-plus-basement and GIS five-level fields may have different counting conventions; this is unresolved."

    return {
        "source_fid": feature["properties"].get("FID"),
        "source_name": feature["properties"].get("BUILDING_N"),
        "raw_footprint_vertices": raw_vertex_count,
        "built_footprint_vertices": len(points),
        "window_bay_count": detail_count,
        "cross_gable_bay_count": cross_gable_count,
        "footprint_bounds_world_m": [
            [min(p[0] for p in points), max(p[0] for p in points)],
            [min(p[1] for p in points), max(p[1] for p in points)],
        ],
        "wall_eaves_height_estimate_m": WALL_TOP_M,
        "roof_ridge_height_estimate_m": ROOF_RIDGE_M,
        "cross_gable_ridge_height_estimate_m": min(ROOF_RIDGE_M+0.45, 15.1),
        "overall_height_estimate_m": min(ROOF_RIDGE_M+0.45, 15.1),
        "visible_storeys_estimated": 3,
        "basement": "historically documented; only the upper foundation band is modeled above grade",
        "facade_orientation": "west elevation treated as the quadrangle-facing entrance side; estimated from the site arrangement",
    }


def render_previews(scene, preview_collection, points):
    center_x = sum(p[0] for p in points)/len(points)
    center_y = sum(p[1] for p in points)/len(points)
    ground = make_material("CQE_Preview_Ground", (0.40, 0.42, 0.40), roughness=0.95)
    ground_mesh = bpy.data.meshes.new("CQE_PreviewGroundMesh")
    ground_mesh.from_pydata([(center_x-140, center_y-140, -0.25),
                             (center_x+140, center_y-140, -0.25),
                             (center_x+140, center_y+140, -0.25),
                             (center_x-140, center_y+140, -0.25)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(ground)
    plane = bpy.data.objects.new("CQE_Preview_Ground", ground_mesh)
    preview_collection.objects.link(plane)

    world = bpy.data.worlds.new("CQE_Preview_World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.67, 0.72, 0.78, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    scene.world = world
    key_data = bpy.data.lights.new("CQE_Preview_Key", "AREA")
    key_data.energy = 16000
    key_data.shape = "DISK"
    key_data.size = 65
    key = bpy.data.objects.new("CQE_Preview_Key", key_data)
    preview_collection.objects.link(key)
    key.location = (center_x-45, center_y-55, 90)

    camera_data = bpy.data.cameras.new("CQE_Preview_Camera")
    camera = bpy.data.objects.new("CQE_Preview_Camera", camera_data)
    preview_collection.objects.link(camera)
    target = Vector((center_x, center_y, 6.5))
    camera.location = (center_x-112, center_y-72, 47)
    camera.rotation_euler = (target-Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera_data.lens = 46
    scene.camera = camera

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = 1420
    scene.render.resolution_y = 920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = str(EVIDENCE / "cqe_detailed_preview.png")
    bpy.ops.render.render(write_still=True)

    top_data = bpy.data.cameras.new("CQE_Footprint_Camera")
    top = bpy.data.objects.new("CQE_Footprint_Camera", top_data)
    preview_collection.objects.link(top)
    top_data.type = "ORTHO"
    top_data.ortho_scale = max(max(p[0] for p in points)-min(p[0] for p in points),
                               max(p[1] for p in points)-min(p[1] for p in points))*1.28
    top.location = (center_x, center_y, 130)
    top.rotation_euler = (0.0, 0.0, 0.0)
    scene.camera = top
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.filepath = str(EVIDENCE / "cqe_top_preview.png")
    bpy.ops.render.render(write_still=True)
    scene.camera = camera


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    scene, asset_collection, preview_collection = setup_scene()
    points, feature, raw_count = read_source()
    summary = build_geometry(points, feature, raw_count, asset_collection)
    render_previews(scene, preview_collection, points)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    report = {
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "scene": SCENE_NAME,
        "collection": COLLECTION_NAME,
        "coordinate_contract": "campus world coordinates; meters; identity object transform",
        "source": "Purdue BuildingShapesZip4 FeatureServer FID 639",
        "build": summary,
        "asset_objects": len(asset_collection.objects),
        "asset_mesh_objects": sum(o.type == "MESH" for o in asset_collection.objects),
        "preview_setup_objects_outside_asset": len(preview_collection.objects),
        "preview": "audit/massing_cary_quadrangle_east_cqe_230c813/cqe_detailed_preview.png",
        "top_preview": "audit/massing_cary_quadrangle_east_cqe_230c813/cqe_top_preview.png",
    }
    (EVIDENCE / "build_report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
