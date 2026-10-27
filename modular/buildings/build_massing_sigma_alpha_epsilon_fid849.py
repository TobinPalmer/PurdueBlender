"""Build a source-backed massing model for Purdue SAE (official GIS FID 849).

The GIS footprint is kept in the campus coordinate frame required for massing
assets. The facade/roof treatment follows the architect's renovation renderings;
undocumented elevations and unseen sides remain estimates.
"""

import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_sigma_alpha_epsilon_fid849.blend"
GIS = ROOT / "audit" / "sae_fid849" / "sources" / "purdue_fid849_raw_feature.json"
AUDIT = ROOT / "audit" / "sae_fid849"
RENDER = AUDIT / "renders" / "sigma_alpha_epsilon_fid849_three_quarter.png"
ID = "massing_sigma_alpha_epsilon_fid849"
COLLECTION_NAME = "Asset_" + ID
FID = 849
ORIGIN_LON, ORIGIN_LAT = -86.9137, 40.4274


def materials():
    def make(name, color, roughness=0.82, metallic=0.0):
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = (*color, 1.0)
        mat.use_nodes = True
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        return mat

    return {
        "brick": make("SAE_Soft_Rose_Brick", (0.68, 0.43, 0.41)),
        "upper": make("SAE_Warm_Off_White_Stucco", (0.86, 0.82, 0.72)),
        "stone": make("SAE_Limestone_Trim", (0.92, 0.85, 0.70)),
        "roof": make("SAE_Brown_Architectural_Roof", (0.48, 0.40, 0.29)),
        "glass": make("SAE_Window_Glass", (0.12, 0.20, 0.24), 0.27),
        "door": make("SAE_Entry_Door_Walnut", (0.20, 0.12, 0.075)),
        "dark": make("SAE_Entry_Recess", (0.055, 0.055, 0.052)),
        "metal": make("SAE_Lettering_Gold", (0.77, 0.52, 0.08), 0.42, 0.25),
    }


def footprint():
    feature = json.loads(GIS.read_text(encoding="utf-8"))["feature"]
    ring = feature["geometry"]["rings"][0]
    c = math.cos(math.radians(ORIGIN_LAT))
    points = [((lon - ORIGIN_LON) * 111412.84 * c,
               (lat - ORIGIN_LAT) * 111040.0) for lon, lat in ring]
    if points[0] == points[-1]:
        points.pop()
    return points


def new_mesh(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    if material:
        mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return obj


def add_prism(coll, name, center, width, depth, height, u, normal, material):
    """Add a rectangular prism oriented along facade tangent u and normal."""
    u = Vector((u[0], u[1], 0.0)).normalized()
    normal = Vector((normal[0], normal[1], 0.0)).normalized()
    center = Vector(center)
    verts = []
    for z in (-height / 2, height / 2):
        for d in (-depth / 2, depth / 2):
            for w in (-width / 2, width / 2):
                p = center + u * w + normal * d + Vector((0, 0, z))
                verts.append(tuple(p))
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (1, 5, 7, 3), (3, 7, 6, 2), (2, 6, 4, 0)]
    obj = new_mesh(name, verts, faces, material)
    coll.objects.link(obj)
    return obj


def add_facade_band(coll, name, p0, p1, z0, z1, material):
    verts = [(p0[0], p0[1], z0), (p1[0], p1[1], z0),
             (p1[0], p1[1], z1), (p0[0], p0[1], z1)]
    obj = new_mesh(name, verts, [(0, 1, 2, 3)], material)
    coll.objects.link(obj)
    return obj


def edge_geometry(points, i):
    p0, p1 = points[i], points[(i + 1) % len(points)]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    u = (dx / length, dy / length)
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    vx, vy = mid[0] - cx, mid[1] - cy
    norm = math.hypot(vx, vy)
    n = (vx / norm, vy / norm)
    # On concave corners, centroid direction can be poor; test both normals
    # against a point slightly beyond the edge and retain the outward one.
    left = (-u[1], u[0])
    right = (u[1], -u[0])
    test = 0.3
    if point_in_polygon((mid[0] + left[0] * test, mid[1] + left[1] * test), points):
        n = right
    else:
        n = left
    return p0, p1, length, u, mid, n


def point_in_polygon(point, poly):
    x, y = point
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi:
            inside = not inside
        j = i
    return inside


def build_shell(coll, pts, mats):
    # The architect's three-level elevation informs the broad facade banding.
    # Floor elevations are estimates; the GIS extrusion is retained as a 12 m cap.
    z_levels = [0.0, 3.65, 7.25, 10.65]
    band_mats = [mats["brick"], mats["upper"], mats["upper"]]
    for i in range(len(pts)):
        p0, p1 = pts[i], pts[(i + 1) % len(pts)]
        for floor in range(3):
            add_facade_band(coll, f"SAE_FID849_Facade_{i:02d}_Level_{floor + 1}",
                            p0, p1, z_levels[floor], z_levels[floor + 1], band_mats[floor])

    # The architect's rendering shows broad low-pitch roofs over lower wings and
    # a raised central section. A simple roof plate keeps the mapped eave intact.
    # The central cap carries the 12 m GIS extrusion height as a bounded estimate.
    cx = sum(x for x, _ in pts) / len(pts)
    cy = sum(y for _, y in pts) / len(pts)
    roof_verts = [(x, y, 10.72) for x, y in pts]
    roof = new_mesh("SAE_FID849_Low_Pitched_Roof_Plate_Estimated", roof_verts,
                    [tuple(range(len(pts)))], mats["roof"])
    coll.objects.link(roof)

    # Raised central upper volume is visible in the architect's front elevation.
    # Its compact placement is schematic and remains inside the source footprint.
    u = Vector(edge_geometry(pts, front_edge_index(pts))[3]).to_3d().normalized()
    n = Vector(edge_geometry(pts, front_edge_index(pts))[5]).to_3d().normalized()
    center = Vector((cx, cy, 9.2))
    along = u * 4.4
    inward = -n * 6.2
    corners = [center - along + inward, center + along + inward,
               center + along - inward, center - along - inward]
    verts = [(p.x, p.y, 8.0) for p in corners] + [(p.x, p.y, 11.30) for p in corners]
    faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
             (4, 5, 6, 7)]
    raised = new_mesh("SAE_FID849_Central_Upper_Volume_Estimated", verts, faces, mats["upper"])
    coll.objects.link(raised)
    # Low hip roof over the raised central volume, with a short central ridge.
    ridge0 = center - u * 2.7
    ridge1 = center + u * 2.7
    capverts = [(p.x, p.y, 11.35) for p in corners]
    capverts += [(ridge0.x, ridge0.y, 11.95), (ridge1.x, ridge1.y, 11.95)]
    capfaces = [(0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)]
    cap = new_mesh("SAE_FID849_Central_Hipped_Roof_Estimated", capverts, capfaces, mats["roof"])
    coll.objects.link(cap)
    return (cx, cy)


def front_edge_index(pts):
    candidates = []
    for i in range(len(pts)):
        p0, p1, length, u, mid, n = edge_geometry(pts, i)
        if length >= 15.0:
            candidates.append((mid[0], i, length))
    return min(candidates)[1]


def add_windows_and_trim(coll, pts, mats):
    floors = [(1, 1.85, 1.55), (2, 5.25, 1.70), (3, 8.62, 1.70)]
    front_i = front_edge_index(pts)
    for i in range(len(pts)):
        p0, p1, length, u, mid, n = edge_geometry(pts, i)
        if length < 5.8:
            continue
        count = max(1, int(length // (4.2 if length > 15 else 3.5)))
        span = length / (count + 1)
        for floor, z, h in floors:
            for j in range(count):
                t = (j + 1) * span
                # Leave the central entry bay clear on the principal west side.
                if i == front_i and abs(t - length / 2) < 3.4:
                    continue
                pos = (p0[0] + u[0] * t + n[0] * 0.08,
                       p0[1] + u[1] * t + n[1] * 0.08, z)
                w = 1.55 if length > 15 else 1.35
                add_prism(coll, f"SAE_FID849_Window_{i:02d}_{floor}_{j:02d}", pos,
                          w, 0.13, h, u, n, mats["glass"])
                for side in (-1, 1):
                    frame_pos = (pos[0] + u[0] * side * (w / 2 + 0.075),
                                 pos[1] + u[1] * side * (w / 2 + 0.075), z)
                    add_prism(coll, f"SAE_FID849_Window_Jamb_{i:02d}_{floor}_{j:02d}_{side}",
                              frame_pos, 0.14, 0.18, h + 0.16, u, n, mats["stone"])
                for dz, suffix in ((h / 2 + 0.06, "Head"), (-h / 2 - 0.06, "Sill")):
                    frame_pos = (pos[0], pos[1], z + dz)
                    add_prism(coll, f"SAE_FID849_Window_{suffix}_{i:02d}_{floor}_{j:02d}",
                              frame_pos, w + 0.28, 0.18, 0.13, u, n, mats["stone"])
                # One restrained vertical mullion, directly supported by the repeated window rhythm.
                mullion_pos = (pos[0], pos[1], z)
                add_prism(coll, f"SAE_FID849_Window_Mullion_{i:02d}_{floor}_{j:02d}",
                          mullion_pos, 0.055, 0.20, h - 0.12, u, n, mats["stone"])

    # Broad cornice bands follow the horizontal changes visible in the elevation.
    for z in (3.67, 7.27, 10.58):
        for i in range(len(pts)):
            p0, p1, length, u, mid, n = edge_geometry(pts, i)
            if length < 2.0:
                continue
            pos = (mid[0] + n[0] * 0.10, mid[1] + n[1] * 0.10, z)
            add_prism(coll, f"SAE_FID849_Cornice_{int(z*100)}_{i:02d}",
                      pos, length, 0.22, 0.18, u, n, mats["stone"])


def add_entry(coll, pts, mats):
    i = front_edge_index(pts)
    p0, p1, length, u, mid, n = edge_geometry(pts, i)
    tangent = Vector((u[0], u[1], 0)).normalized()
    outward = Vector((n[0], n[1], 0)).normalized()
    cx, cy = mid
    width = 6.4
    # Dark inset, paired walnut doors, and a limestone surround.
    door_center = (cx + n[0] * 0.16, cy + n[1] * 0.16, 1.63)
    add_prism(coll, "SAE_FID849_Entry_Recess", door_center, 3.15, 0.22, 3.25,
              u, n, mats["dark"])
    add_prism(coll, "SAE_FID849_Double_Door", (door_center[0] + n[0] * 0.14,
              door_center[1] + n[1] * 0.14, 1.47), 2.62, 0.10, 2.70,
              u, n, mats["door"])
    for side in (-1, 1):
        col_center = (cx + n[0] * 1.45 + tangent.x * side * (width / 2 - 0.30),
                      cy + n[1] * 1.45 + tangent.y * side * (width / 2 - 0.30), 2.25)
        add_prism(coll, f"SAE_FID849_Entry_Limestone_Pier_{side}", col_center,
                  0.60, 1.28, 4.50, u, n, mats["stone"])
    # Recessed round arch motif over the door, based on the architect's entry render.
    arch_center = (cx + n[0] * 0.34, cy + n[1] * 0.34)
    # A visible semicircle is assembled from a slim segmented trim strip.
    arc_verts = []
    arc_faces = []
    radius_outer, radius_inner = 1.50, 1.25
    for k in range(25):
        a = math.pi * k / 24
        for radius in (radius_outer, radius_inner):
            x = arch_center[0] + tangent.x * radius * math.cos(a) + n[0] * 0.36
            y = arch_center[1] + tangent.y * radius * math.cos(a) + n[1] * 0.36
            z = 2.68 + radius * math.sin(a)
            arc_verts.append((x, y, z))
    for k in range(24):
        a = 2 * k
        arc_faces.append((a, a + 2, a + 3, a + 1))
    arch = new_mesh("SAE_FID849_Entry_Segmented_Arch", arc_verts, arc_faces, mats["stone"])
    coll.objects.link(arch)

    # Gabled entry hood projects beyond the GIS eave; this is a supported
    # decorative entrance form from the architect rendering, not a wall-footprint edit.
    back = Vector((cx, cy, 0)) + outward * 0.60
    front = Vector((cx, cy, 0)) + outward * 2.15
    half = width / 2
    eave_z, ridge_z = 4.35, 5.90
    left_back = back - tangent * half
    right_back = back + tangent * half
    left_front = front - tangent * half
    right_front = front + tangent * half
    verts = [tuple(left_back + Vector((0, 0, eave_z))),
             tuple(right_back + Vector((0, 0, eave_z))),
             tuple(Vector((cx, cy, ridge_z)) + outward * 0.60),
             tuple(left_front + Vector((0, 0, eave_z))),
             tuple(right_front + Vector((0, 0, eave_z))),
             tuple(Vector((cx, cy, ridge_z)) + outward * 2.15)]
    hood = new_mesh("SAE_FID849_Gabled_Entry_Hood", verts,
                    [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1),
                     (0, 2, 5, 3), (1, 4, 5, 2)], mats["roof"])
    hood.data.materials.append(mats["stone"])
    coll.objects.link(hood)
    # Gold chapter letters on the front gable; converted to mesh for portability.
    curve = bpy.data.curves.new("SAE_FID849_Pediment_Lettering_Curve", "FONT")
    curve.body = "SAE"
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 0.90
    curve.extrude = 0.012
    letters = bpy.data.objects.new("SAE_FID849_Pediment_Lettering", curve)
    coll.objects.link(letters)
    # Make local X follow the facade and local Z point out of the building.
    if tangent.cross(Vector((0, 0, 1))).dot(outward) < 0:
        tangent = -tangent
    basis = Matrix(((tangent.x, 0, outward.x),
                    (tangent.y, 0, outward.y),
                    (0, 1, 0))).to_4x4()
    letters.matrix_world = basis
    letters.location = (cx + n[0] * 1.12, cy + n[1] * 1.12, 4.88)
    letters.data.materials.append(mats["metal"])
    bpy.context.view_layer.objects.active = letters
    letters.select_set(True)
    bpy.ops.object.convert(target="MESH")
    letters.select_set(False)


def configure_scene(center):
    scene = bpy.context.scene
    # The portable repository Blender bundle exposes Workbench only; a
    # material-colored studio render remains deterministic across machines.
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 85
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(RENDER)
    scene.world.color = (0.28, 0.31, 0.34)
    target = Vector((center[0], center[1], 6.0))
    camera_data = bpy.data.cameras.new("SAE_FID849_Preview_Camera")
    camera = bpy.data.objects.new("SAE_FID849_Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = target + Vector((-62, -26, 39))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 68
    scene.camera = camera
    light_data = bpy.data.lights.new("SAE_FID849_Preview_Area", "AREA")
    light = bpy.data.objects.new("SAE_FID849_Preview_Area", light_data)
    scene.collection.objects.link(light)
    light.location = target + Vector((-25, -20, 45))
    light_data.energy = 70000
    light_data.shape = "DISK"
    light_data.size = 48
    light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.view_settings.view_transform = "AgX"
    scene.name = "Building_" + ID


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.collections):
        if block.name != "Collection":
            bpy.data.collections.remove(block)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(coll)
    pts = footprint()
    mats = materials()
    center = build_shell(coll, pts, mats)
    add_windows_and_trim(coll, pts, mats)
    add_entry(coll, pts, mats)
    # Recalculate normals where shell faces meet; decorative panels remain separate.
    for obj in [o for o in coll.objects if o.type == "MESH"]:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(obj.data)
        bm.free()
    configure_scene(center)
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    RENDER.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    bpy.ops.render.render(write_still=True)
    print(json.dumps({"asset": str(ASSET), "scene": bpy.context.scene.name,
                      "collection": COLLECTION_NAME, "object_count": len(coll.objects),
                      "points": len(pts), "preview": str(RENDER)}))


if __name__ == "__main__":
    main()
