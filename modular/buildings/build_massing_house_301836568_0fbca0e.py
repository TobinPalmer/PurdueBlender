"""Rebuild Sigma Pi (Purdue FID 776) from its official footprint and cited records.

Coordinates follow the project local geographic approximation and remain in campus
space because this asset is a simple massing library. Unobserved facade/roof details
are deliberately kept restrained and called out in the accompanying evidence.
"""

import bpy
import bmesh
import json
import math
import os
from pathlib import Path
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_house_301836568_0fbca0e.blend"
GIS = ROOT / "audit" / "sigma_pi" / "sources" / "purdue_gis_fid776_sigma_pi_2026-10-26.json"
ROOF = ROOT / "audit" / "sigma_pi" / "sources" / "sigma_pi_lidar_roof_mesh.json"
AUDIT = ROOT / "audit" / "sigma_pi"
RENDER = AUDIT / "renders" / "sigma_pi_preview.png"

FID = 776
ID = "massing_house_301836568_0fbca0e"
COLLECTION_NAME = "Asset_" + ID


def load_footprint():
    feature = json.loads(GIS.read_text(encoding="utf-8"))
    ring = feature["geometry"]["rings"][0]
    # Source EPSG:4326 -> Purdue project local meter approximation.
    origin_lon, origin_lat = -86.9137, 40.4274
    c = math.cos(math.radians(origin_lat))
    points = [((lon - origin_lon) * 111412.84 * c,
               (lat - origin_lat) * 111040.0) for lon, lat in ring]
    if points[0] == points[-1]:
        points.pop()
    return points


def mat(name, color, roughness=0.8):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def new_mesh(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return obj


def add_box(coll, name, center, size, material, angle=0.0):
    cx, cy, cz = center
    sx, sy, sz = size
    ca, sa = math.cos(angle), math.sin(angle)
    verts = []
    for z in (-sz / 2, sz / 2):
        for y in (-sy / 2, sy / 2):
            for x in (-sx / 2, sx / 2):
                verts.append((cx + x * ca - y * sa,
                              cy + x * sa + y * ca,
                              cz + z))
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (1, 5, 7, 3), (3, 7, 6, 2), (2, 6, 4, 0)]
    obj = new_mesh(name, verts, faces, material)
    coll.objects.link(obj)
    return obj


def add_wall_beam(coll, name, start, end, outward, width, depth, material):
    """Create a rectangular timber prism along a 3D line on a facade plane."""
    a, b = Vector(start), Vector(end)
    along = (b - a).normalized()
    normal = Vector((outward[0], outward[1], 0.0)).normalized()
    across = normal.cross(along).normalized()
    half_w, half_d = width / 2.0, depth / 2.0
    verts = []
    for point in (a, b):
        for s_n, s_w in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
            q = point + normal * (s_n * half_d) + across * (s_w * half_w)
            verts.append(tuple(q))
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    obj = new_mesh(name, verts, faces, material)
    coll.objects.link(obj)
    return obj


def main():
    # Keep other scenes/data in the source library intact, but replace only this
    # exported building collection and its object(s).
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(coll)
    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    stucco = mat("SigmaPi_Stucco_LightWarm", (0.68, 0.60, 0.49))
    trim = mat("SigmaPi_WoodTrim_Painted", (0.28, 0.23, 0.18))
    brick = mat("SigmaPi_StreetLevel_Brick", (0.30, 0.20, 0.15))
    glass = mat("SigmaPi_Window_Glass", (0.12, 0.22, 0.29), 0.3)
    roof = mat("SigmaPi_Roof_Graphite", (0.055, 0.065, 0.08))
    door_mat = mat("SigmaPi_Entry_Door", (0.18, 0.13, 0.10))
    sill = mat("SigmaPi_Foundation_Stone", (0.37, 0.34, 0.29))

    pts = load_footprint()
    n = len(pts)
    # Wall height remains an estimated visualization choice. 2018 LiDAR samples
    # the roof surface, but does not identify the wall line or floor count.
    wall_bottom = 0.25
    # Chosen just below the low end of the robust LiDAR surface mesh so the
    # estimated wall volume meets the roof skin; it remains an estimated wall line.
    wall_top = 9.35
    verts = [(x, y, wall_bottom) for x, y in pts]
    verts += [(x, y, wall_top) for x, y in pts]
    faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    faces.append(tuple(reversed(range(n))))
    # The base polygon is concave but has no interior ring. Blender's ngon
    # tessellator handles the exact source ring for a restrained low roof.
    faces.append(tuple(range(n, 2 * n)))
    shell = new_mesh("SigmaPi_Stucco_Shell_FID776", verts, faces, stucco)
    # Preserve source interpretation with the shipped geometry. The 1932
    # Purdue Debris illustration is on the Sigma Pi chapter page (p.323), but
    # predates the 1989 addition recorded in the 2004 Eta Data; it is a historic
    # visual cue, not a current elevation or a measured roof profile.
    shell["source_identity"] = "Purdue GIS FID 776 / Sigma Pi / 130 Russell St"
    shell["plan_source"] = "Purdue GIS BuildingShapesZip4 layer 0, FID 776"
    shell["plan_metric_interpretation"] = "Stored Shape__Area/Length match the service's EPSG:3857 planar values; WGS84 geodesic ring metrics are 473.159 m2 / 117.120 m."
    shell["vertical_status"] = "Wall line and occupied-level arrangement estimated; 2018 QL2 surface returns support roof elevations, not story count or wall height."
    shell["current_facade_reference"] = "Eta Chapter of Sigma Pi, The Eta Data, November 2004, pp. 1 and 6; dated Homecoming and house-improvement photographs identify the 130 Russell chapter house."
    shell["facade_reference_limit"] = "The dated 2004 photographs support qualitative Tudor half-timber upper facade, multi-gabled roof, window bays, masonry base, and entries after the 1989 addition. They do not provide measured elevations, exact openings, or verified side/rear arrangement."
    shell["roof_surface_source"] = "Indiana Statewide Elevation Data 2018 QL2 COPC tile in2018_29951885_12.copc.laz; unclassified returns over GIS FID 776."
    shell["roof_surface_limit"] = "0.9 m constrained mesh, with IDW from nearby class-1 returns >=650 ft NAVD88 and 5th-95th percentile clipping, relative to nearby class-2 ground median; vegetation cannot be entirely excluded. Supports roof articulation and elevation, not a surveyed roof."
    shell["historic_visual_source"] = "Purdue Debris 1932, p.323, Sigma Pi chapter page; archive item debris:18615"
    shell["historic_visual_limit"] = "Historical house illustration only; likely associated with the chapter's pre-1989 house, exact current building continuity and dimensions unverified."
    shell["dated_facade_photo_source"] = "The Eta Data, November 2004, pp. 1 and 6; local crops: audit/sigma_pi/sources/eta_data_2004_page1_house_photo.png and eta_data_2004_page6_house_photo.png."
    shell["dated_facade_photo_limit"] = "As-of-November-2004 qualitative facade evidence; page 6 appears in the house-improvement section. Individual capture day is not stated; no dimensions or 2026 condition inferred."
    bm = bmesh.new()
    bm.from_mesh(shell.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(shell.data)
    bm.free()
    coll.objects.link(shell)

    # Foundation follows the mapped ring, which is treated as a roof outline,
    # not a verified wall line.
    base_verts = [(x, y, wall_bottom) for x, y in pts]
    base_verts += [(x, y, wall_bottom + 0.42) for x, y in pts]
    base_faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    plinth = new_mesh("SigmaPi_Stone_BaseCourse", base_verts, base_faces, sill)
    coll.objects.link(plinth)

    # The listing image shows masonry at street level. This is a broad material
    # cue only; its exact height and continuation around unseen sides are unknown.
    for i, (p0, p1) in enumerate(zip(pts, pts[1:] + pts[:1])):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        length = math.hypot(dx, dy)
        if length < 2.5:
            continue
        angle = math.atan2(dy, dx)
        # The source ring is clockwise, so the left-hand edge normal is outward.
        nx, ny = -math.sin(angle), math.cos(angle)
        cx, cy = (p0[0] + p1[0]) / 2 + nx * 0.06, (p0[1] + p1[1]) / 2 + ny * 0.06
        add_box(coll, f"SigmaPi_Brick_Lower_Facade_{i:02d}", (cx, cy, 1.72),
                (length, 0.12, 2.95), brick, angle)

    # Narrow wood courses reflect the chapter newsletter's explicit references
    # to exterior wood trim. Use separate narrow pieces on long mapped walls.
    for level_z in (3.15, 6.15, wall_top - 0.18):
        for i, (p0, p1) in enumerate(zip(pts, pts[1:] + pts[:1])):
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            length = math.hypot(dx, dy)
            if length < 2.5:
                continue
            angle = math.atan2(dy, dx)
            cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            add_box(coll, f"SigmaPi_Wood_Course_{level_z:.1f}_{i:02d}",
                    (cx, cy, level_z), (length, 0.13, 0.10), trim, angle)

    # Repeated windows render the multiple tiers visible in the listing photo.
    # Their count, size, and precise positions remain unmeasured estimates.
    for i, (p0, p1) in enumerate(zip(pts, pts[1:] + pts[:1])):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        length = math.hypot(dx, dy)
        if length < 5.0:
            continue
        angle = math.atan2(dy, dx)
        nx, ny = -math.sin(angle), math.cos(angle)
        count = max(1, int(length // 4.4))
        spacing = length / (count + 1)
        for floor, z in enumerate((1.85, 4.55, 7.8), 1):
            for j in range(count):
                t = (j + 1) * spacing
                x, y = p0[0] + (t * dx / length), p0[1] + (t * dy / length)
                # Slight outward offset, dimensions intentionally restrained.
                x += nx * 0.05
                y += ny * 0.05
                face_angle = angle  # local Y points to the exterior normal for this clockwise ring
                add_box(coll, f"SigmaPi_Window_F{floor}_{i:02d}_{j:02d}",
                        (x, y, z), (1.35, 0.12, 1.55), glass, face_angle)
                # Wood frame around each glazing panel.
                add_box(coll, f"SigmaPi_WindowHead_F{floor}_{i:02d}_{j:02d}",
                        (x, y, z + 0.82), (1.55, 0.17, 0.10), trim, face_angle)
                add_box(coll, f"SigmaPi_WindowSill_F{floor}_{i:02d}_{j:02d}",
                        (x, y, z - 0.82), (1.55, 0.17, 0.10), trim, face_angle)

    # The eastmost long frontage faces Russell Street based on the source
    # coordinates; a modest entry is included as an estimate, not a surveyed fact.
    east_edge = max(range(n), key=lambda i: max(pts[i][0], pts[(i + 1) % n][0]))
    p0, p1 = pts[east_edge], pts[(east_edge + 1) % n]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if length > 4:
        angle = math.atan2(dy, dx)
        nx, ny = -math.sin(angle), math.cos(angle)
        x, y = (p0[0] + p1[0]) / 2 + nx * 0.08, (p0[1] + p1[1]) / 2 + ny * 0.08
        face_angle = angle
        add_box(coll, "SigmaPi_Estimated_Main_Entry", (x, y, 1.35), (1.15, 0.18, 2.55), door_mat, face_angle)
        add_box(coll, "SigmaPi_Entry_Head_Trim", (x, y, 2.68), (1.5, 0.18, 0.14), trim, face_angle)
        add_box(coll, "SigmaPi_Entry_Canopy", (x + nx * 0.8, y + ny * 0.8, 2.9), (2.0, 1.6, 0.18), roof, face_angle)

    # Use the recorded 2018 LiDAR surface interpolation. It supports roof
    # articulation and elevation, while retaining uncertainty about vegetation,
    # exact roof materials, wall line, and structural roof profile.
    roof_data = json.loads(ROOF.read_text(encoding="utf-8"))
    roof_mesh = bpy.data.meshes.new("SigmaPi_Roof_Plane_Mesh")
    roof_mesh.from_pydata(roof_data["vertices"], [], roof_data["faces"])
    roof_mesh.materials.append(roof)
    roof_mesh.update()
    roof_bm = bmesh.new()
    roof_bm.from_mesh(roof_mesh)
    bmesh.ops.recalc_face_normals(roof_bm, faces=roof_bm.faces)
    roof_bm.to_mesh(roof_mesh)
    roof_bm.free()
    for poly in roof_mesh.polygons:
        poly.use_smooth = True
    roof_obj = bpy.data.objects.new("SigmaPi_Roof_Surface_LiDAR_2018_Interpolated", roof_mesh)
    roof_obj["profile_status"] = "Interpolated 2018 unclassified LiDAR surface; roof articulation cue with vegetation and point-class uncertainty"
    roof_obj["source_return_count"] = roof_data["source_return_count"]
    roof_obj["interpolation"] = roof_data["method"]
    roof_obj["visual_smoothing"] = "Blender Smooth modifier factor 0.18 x 2 to reduce interpolation noise; LiDAR-derived source mesh remains unchanged."
    soften = roof_obj.modifiers.new("LiDAR_Surface_Soften_For_Massing", "SMOOTH")
    soften.factor = 0.18
    soften.iterations = 2
    solidify = roof_obj.modifiers.new("Estimated_Roof_Skin_Thickness", "SOLIDIFY")
    solidify.thickness = 0.22
    solidify.offset = -1.0
    coll.objects.link(roof_obj)

    # Dated 2004 house-improvement photographs show half-timber framing on the
    # upper street facade. The GIS roof ring has three near-east-facing wall
    # runs separated by small notches; keep the photo-backed treatment there
    # and describe the layout as schematic, not a surveyed elevation.
    east_x = max(x for x, _ in pts)
    front_window_centers = []
    for window in coll.objects:
        if not window.name.startswith("SigmaPi_Window_F"):
            continue
        coords = [v.co for v in window.data.vertices]
        center = Vector(tuple(sum(v[i] for v in coords) / len(coords) for i in range(3)))
        if center.x >= east_x - 1.5:
            front_window_centers.append(center)
    street_edges = []
    for i, (p0, p1) in enumerate(zip(pts, pts[1:] + pts[:1])):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        length = math.hypot(dx, dy)
        if max(p0[0], p1[0]) >= east_x - 1.5 and abs(dx) < 1.2 and length >= 2.5:
            street_edges.append((i, p0, p1, dx, dy, length))

    timber_bottom, timber_top = 3.12, 9.12
    for edge_i, p0, p1, dx, dy, length in street_edges:
        angle = math.atan2(dy, dx)
        nx, ny = -math.sin(angle), math.cos(angle)
        divisions = max(2, round(length / 2.15))

        def facade_point(t, z):
            return (p0[0] + dx*t + nx*0.17, p0[1] + dy*t + ny*0.17, z)

        for j in range(divisions + 1):
            t = j / divisions
            add_wall_beam(coll, f"SigmaPi_Tudor_Stile_E{edge_i}_{j:02d}",
                          facade_point(t, timber_bottom), facade_point(t, timber_top),
                          (nx, ny), 0.17, 0.16, trim)
        for z in (timber_bottom, 6.15, timber_top):
            add_wall_beam(coll, f"SigmaPi_Tudor_Rail_E{edge_i}_{z:.2f}",
                          facade_point(0.0, z), facade_point(1.0, z),
                          (nx, ny), 0.17, 0.16, trim)

        for j in range(divisions):
            t0, t1 = j / divisions, (j + 1) / divisions
            bay = length / divisions
            if bay < 1.75:
                continue
            window_t = []
            for wc in front_window_centers:
                t = ((wc.x - p0[0]) * dx + (wc.y - p0[1]) * dy) / (length * length)
                projected_x, projected_y = p0[0] + t*dx, p0[1] + t*dy
                if 0.0 <= t <= 1.0 and math.hypot(wc.x-projected_x, wc.y-projected_y) < 0.8:
                    window_t.append((t, wc.z))
            for lo, hi in ((timber_bottom + 0.16, 6.15 - 0.12),
                           (6.15 + 0.12, timber_top - 0.16)):
                panel_has_window = any(t0 <= wt <= t1 and lo - 0.85 <= wz <= hi + 0.85
                                       for wt, wz in window_t)
                if panel_has_window:
                    continue
                add_wall_beam(coll, f"SigmaPi_Tudor_Diagonal_E{edge_i}_{j}_{lo:.1f}A",
                              facade_point(t0 + 0.04, lo), facade_point(t1 - 0.04, hi),
                              (nx, ny), 0.13, 0.17, trim)
                add_wall_beam(coll, f"SigmaPi_Tudor_Diagonal_E{edge_i}_{j}_{lo:.1f}B",
                              facade_point(t0 + 0.04, hi), facade_point(t1 - 0.04, lo),
                              (nx, ny), 0.13, 0.17, trim)

    # Add a legible casement-like grid to the street-facing glazing. These bars
    # follow the photographed timber contrast; opening sizes/count stay estimates.
    for obj in list(coll.objects):
        if not obj.name.startswith("SigmaPi_Window_F"):
            continue
        coords = [v.co for v in obj.data.vertices]
        center = Vector(tuple(sum(v[i] for v in coords) / len(coords) for i in range(3)))
        if center.x < east_x - 1.5:
            continue
        nx, ny = 1.0, 0.0
        for side in (-0.72, 0.72):
            add_wall_beam(coll, f"SigmaPi_Window_Jamb_{obj.name}_{side:+.2f}",
                          (center.x + 0.12, center.y + side, center.z - 0.77),
                          (center.x + 0.12, center.y + side, center.z + 0.77),
                          (nx, ny), 0.10, 0.13, trim)
        add_wall_beam(coll, f"SigmaPi_Window_Mullion_{obj.name}",
                      (center.x + 0.13, center.y, center.z - 0.74),
                      (center.x + 0.13, center.y, center.z + 0.74),
                      (nx, ny), 0.07, 0.14, trim)
        add_wall_beam(coll, f"SigmaPi_Window_Crossrail_{obj.name}",
                      (center.x + 0.14, center.y - 0.67, center.z),
                      (center.x + 0.14, center.y + 0.67, center.z),
                      (nx, ny), 0.07, 0.15, trim)

    # Set useful render/camera and pack dependencies; no external textures used.
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    center_x = sum(x for x, _ in pts) / n
    center_y = sum(y for _, y in pts) / n
    center = Vector((center_x, center_y, 5.5))
    camera_data = bpy.data.cameras.new("SigmaPi_Preview_Camera")
    camera = bpy.data.objects.new("SigmaPi_Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((48, -36, 12))
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 60
    scene.camera = camera
    light_data = bpy.data.lights.new("SigmaPi_Preview_Area", "AREA")
    light = bpy.data.objects.new("SigmaPi_Preview_Area", light_data)
    scene.collection.objects.link(light)
    light.location = center + Vector((8, -20, 34))
    light_data.energy = 52000
    light_data.shape = "DISK"
    light_data.size = 34
    light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.world.color = (0.22, 0.22, 0.22)
    scene.render.filepath = str(RENDER)

    # Keep the original scene name and create a scene whose name remains stable.
    scene.name = "Building_" + ID
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
