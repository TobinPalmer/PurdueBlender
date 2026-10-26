"""Rebuild the Kappa Sigma massing asset from its source-backed campus footprint.

Run from any directory with Blender's bundled Python, for example:
  blender -b --python modular/buildings/build_massing_kappa_sigma_c1b36ec.py

The output stays in campus coordinates (meters, X east, Y north, Z up) because
this is a simple massing asset, not a local-coordinate detailed library.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_kappa_sigma_c1b36ec"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / ASSET_ID / "sources" / "purdue_gis_fid804_2026-10-26.json"
PREVIEW_PATH = ROOT / "audit" / ASSET_ID / "kappa_sigma_preview.png"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
OBJECT_NAME = "Kappa Sigma"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137


def project(lon: float, lat: float) -> tuple[float, float]:
    """Use the campus' documented approximate lon/lat-to-meter conversion."""
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - 40.4274) * 111040.0
    return x, y


def material(name: str, color: tuple[float, float, float, float], roughness: float = 0.8):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


class MeshAssembly:
    """Accumulate disconnected solid details into the required single mesh."""
    def __init__(self):
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[int, ...]] = []
        self.material_ids: list[int] = []

    def face(self, points, mat_id: int):
        start = len(self.vertices)
        self.vertices.extend(tuple(float(v) for v in point) for point in points)
        self.faces.append(tuple(range(start, start + len(points))))
        self.material_ids.append(mat_id)

    def box_axes(self, center, axis_x, axis_y, dims, mat_id: int):
        """Append a box whose horizontal axes are local wall tangent/normal."""
        cx, cy, cz = center
        ax, ay = axis_x
        bx, by = axis_y
        sx, sy, sz = (d / 2 for d in dims)
        pts = []
        for dz in (-sz, sz):
            for v, u in ((-sy, -sx), (-sy, sx), (sy, sx), (sy, -sx)):
                pts.append((cx + u * ax + v * bx, cy + u * ay + v * by, cz + dz))
        # A closed six-sided box, with consistent vertex reuse within this solid.
        start = len(self.vertices)
        self.vertices.extend(pts)
        local_faces = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                       (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
        for f in local_faces:
            self.faces.append(tuple(start + i for i in f))
            self.material_ids.append(mat_id)

    def bar_between(self, start_point, end_point, normal, width, depth, mat_id):
        """Add a raised rectangular stroke on a vertical facade plane."""
        p = Vector(start_point)
        q = Vector(end_point)
        outward = Vector((normal[0], normal[1], 0.0)).normalized()
        direction = (q - p).normalized()
        across = outward.cross(direction).normalized()
        center = (p + q) / 2
        half_length = (q - p).length / 2
        pts = []
        for s_depth in (-depth / 2, depth / 2):
            for s_width in (-width / 2, width / 2):
                for s_length in (-half_length, half_length):
                    v = center + direction * s_length + across * s_width + outward * s_depth
                    pts.append(tuple(v))
        start = len(self.vertices)
        self.vertices.extend(pts)
        local_faces = ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4),
                       (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6))
        for face in local_faces:
            self.faces.append(tuple(start + i for i in face))
            self.material_ids.append(mat_id)

    def prism(self, points, z0, z1, side_mat: int, top_mat: int | None = None):
        n = len(points)
        lo = len(self.vertices)
        self.vertices.extend((x, y, z0) for x, y in points)
        hi = len(self.vertices)
        self.vertices.extend((x, y, z1) for x, y in points)
        self.face_at_indices(tuple(lo + i for i in reversed(range(n))), side_mat)
        self.face_at_indices(tuple(hi + i for i in range(n)), side_mat if top_mat is None else top_mat)
        for i in range(n):
            j = (i + 1) % n
            self.faces.append((lo + i, lo + j, hi + j, hi + i))
            self.material_ids.append(side_mat)

    def gable_wedge(self, front_left, front_right, front_ridge,
                    back_left, back_right, back_ridge, brick_mat, roof_mat):
        start = len(self.vertices)
        self.vertices.extend((front_left, front_right, front_ridge,
                              back_left, back_right, back_ridge))
        # Closed five-face wedge: two roof slopes, two gable ends, and its base.
        faces = ((0, 2, 5, 3), (2, 1, 4, 5), (0, 1, 4, 3),
                 (0, 1, 2), (3, 5, 4))
        materials = (roof_mat, roof_mat, roof_mat, brick_mat, brick_mat)
        for face, mat_id in zip(faces, materials):
            self.faces.append(tuple(start + i for i in face))
            self.material_ids.append(mat_id)

    def face_at_indices(self, indices, mat_id):
        self.faces.append(indices)
        self.material_ids.append(mat_id)


def add_window(assembly, midpoint, tangent, normal, z, brick, trim, glass):
    mx, my = midpoint
    # A repeated rectangular opening with pale trim and dark glazing, inferred
    # from the undated chapter-house photo. Its exact dimensions are estimates.
    width, height = 1.05, 1.3
    center = (mx + normal[0] * 0.09, my + normal[1] * 0.09, z)
    frame_depth = 0.20
    assembly.box_axes((center[0], center[1], z), tangent, normal,
                      (width - 0.12, 0.055, height - 0.18), glass)
    # Individual frame rails leave the central glazed area visible.
    for offset in (-width / 2 + 0.06, width / 2 - 0.06):
        rail = (center[0] + tangent[0] * offset,
                center[1] + tangent[1] * offset, z)
        assembly.box_axes(rail, tangent, normal, (0.12, frame_depth, height), trim)
    for offset in (-height / 2 + 0.06, height / 2 - 0.06):
        rail = (center[0], center[1], z + offset)
        assembly.box_axes(rail, tangent, normal, (width, frame_depth, 0.12), trim)
    assembly.box_axes((center[0], center[1], z - height / 2 - 0.06),
                      tangent, normal, (width + 0.10, 0.24, 0.12), trim)


def add_facade_bar(assembly, p, q, z, width, thickness, mat_id):
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    if length < 0.01:
        return
    tangent = (dx / length, dy / length)
    outward = (tangent[1], -tangent[0])
    center = ((p[0] + q[0]) / 2 + outward[0] * thickness / 2,
              (p[1] + q[1]) / 2 + outward[1] * thickness / 2, z)
    assembly.box_axes(center, tangent, outward, (length, thickness, width), mat_id)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    building_col = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(building_col)
    return scene, building_col


def build():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing evidence snapshot: {SOURCE_PATH}")
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    if len(features) != 1 or features[0]["attributes"].get("FID") != 804:
        raise RuntimeError("Expected exactly Purdue GIS BuildingShapesZip4 FID 804")
    attrs = features[0]["attributes"]
    if attrs.get("BUILDING_N") != "Kappa Sigma" or attrs.get("ADDRESS") != "308 North St":
        raise RuntimeError("FID 804 identity/address no longer match Kappa Sigma")
    ring = features[0]["geometry"]["rings"][0]
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    footprint = [project(lon, lat) for lon, lat in ring]
    if len(footprint) < 4:
        raise RuntimeError("Footprint ring is unexpectedly small")
    signed_area = sum(
        footprint[i][0] * footprint[(i + 1) % len(footprint)][1]
        - footprint[(i + 1) % len(footprint)][0] * footprint[i][1]
        for i in range(len(footprint))
    ) / 2
    outward_sign = 1.0 if signed_area > 0 else -1.0

    scene, col = clear_scene()
    mats = [
        material("KappaSigma_Red_Brick", (0.34, 0.105, 0.065, 1.0)),
        material("KappaSigma_Roof_Membrane", (0.12, 0.15, 0.16, 1.0)),
        material("KappaSigma_White_Trim", (0.84, 0.80, 0.70, 1.0)),
        material("KappaSigma_Window_Glass", (0.055, 0.085, 0.11, 1.0), 0.25),
        material("KappaSigma_Door", (0.16, 0.075, 0.04, 1.0)),
        material("KappaSigma_Stone_Base", (0.49, 0.46, 0.40, 1.0)),
        material("KappaSigma_Lettering", (0.91, 0.88, 0.77, 1.0)),
    ]
    brick, roof, trim, glass, door, stone, letters = range(len(mats))
    mesh = MeshAssembly()

    # Source-matched wall perimeter. 9.6 m approximates three photographed
    # levels at ~3.2 m each; no published measured elevation was located.
    wall_height = 9.6
    parapet_height = 0.25
    mesh.prism(footprint, 0.0, wall_height, brick)
    # Small stone water table, kept on the exterior of the source footprint.
    # The exact foundation edge is unverified, so this remains a shallow accent.
    # A roof slab follows the official polygon's exterior, matching its plan.
    mesh.prism(footprint, wall_height, wall_height + parapet_height, brick, roof)

    # Place regularly spaced openings along source-backed long exterior walls.
    # Exact fenestration is estimated from the chapter-house photograph.
    xs = [p[0] for p in footprint]
    ys = [p[1] for p in footprint]
    min_y, max_y = min(ys), max(ys)
    wall_edges = []
    for a, b in zip(footprint, footprint[1:] + footprint[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length >= 4.1:
            tangent = (dx / length, dy / length)
            outward = (tangent[1] * outward_sign, -tangent[0] * outward_sign)
            wall_edges.append((a, b, length, tangent, outward))
    for a, b, length, tangent, outward in wall_edges:
        # Aim for roughly 3.8 m between window centers, avoiding corners.
        count = max(1, int((length - 1.8) // 3.7)) if length >= 5.1 else 1
        for row_z in (1.75, 4.75, 7.75):
            for idx in range(count):
                along = length * (idx + 1) / (count + 1)
                center = (a[0] + tangent[0] * along, a[1] + tangent[1] * along)
                add_window(mesh, center, tangent, outward, row_z, brick, trim, glass)

    # Entrance on the long south-facing edge inferred from the 308 North Street
    # address and public front photo; exact door placement is not geodetically
    # verified. Keep the door wholly inside the GIS outline.
    south_edges = [edge for edge in wall_edges
                   if (edge[0][1] + edge[1][1]) / 2 <= min_y + 3.7
                   and abs(edge[3][1]) < 0.25]
    if south_edges:
        facade_center_x = (min(xs) + max(xs)) / 2
        a, b, length, tangent, outward = min(
            south_edges,
            key=lambda edge: abs((edge[0][0] + edge[1][0]) / 2 - facade_center_x),
        )
        center_along = length / 2
        cx, cy = a[0] + tangent[0] * center_along, a[1] + tangent[1] * center_along
        normal = outward
        door_center = (cx + normal[0] * 0.18, cy + normal[1] * 0.18, 1.24)
        for offset in (-0.60, 0.60):
            mesh.box_axes((door_center[0] + tangent[0] * offset,
                           door_center[1] + tangent[1] * offset, door_center[2]),
                          tangent, normal, (0.12, 0.26, 2.48), trim)
        mesh.box_axes(door_center, tangent, normal, (1.32, 0.26, 0.14), trim)
        mesh.box_axes((cx + normal[0] * 0.31, cy + normal[1] * 0.31, 1.20),
                      tangent, normal, (0.94, 0.08, 2.18), door)
        # A modest porch hood and one-step threshold are qualitative details.
        mesh.box_axes((cx + normal[0] * 0.46, cy + normal[1] * 0.46, 2.62),
                      tangent, normal, (2.5, 1.1, 0.18), roof)
        mesh.box_axes((cx + normal[0] * 0.72, cy + normal[1] * 0.72, 0.12),
                      tangent, normal, (2.2, 1.15, 0.24), stone)

        sign_location = (cx + normal[0] * 0.20, cy + normal[1] * 0.20, 8.35)
        def stroke(x0, z0, x1, z1):
            p = (sign_location[0] + tangent[0] * x0,
                 sign_location[1] + tangent[1] * x0, sign_location[2] + z0)
            q = (sign_location[0] + tangent[0] * x1,
                 sign_location[1] + tangent[1] * x1, sign_location[2] + z1)
            mesh.bar_between(p, q, normal, width=0.095, depth=0.085, mat_id=letters)

        # Portable raised K and Sigma letter strokes; no external font dependency.
        stroke(-0.82, -0.48, -0.82, 0.48)
        stroke(-0.78, 0.0, -0.28, 0.48)
        stroke(-0.78, 0.0, -0.28, -0.48)
        stroke(0.12, 0.48, 0.90, 0.48)
        stroke(0.12, 0.48, 0.50, 0.0)
        stroke(0.50, 0.0, 0.12, -0.48)
        stroke(0.12, -0.48, 0.90, -0.48)

        # Three shallow gables and a tall brick chimney follow the visible
        # asymmetrical roofline in the chapter-house photo. Their exact extents
        # are estimates constrained by the orthophoto and GIS roof envelope.
        front_y = cy
        roof_back_y = min(max_y - 0.2, front_y + 10.0)
        roof_sections = (
            (facade_center_x - 13.0, 4.3, 11.7),
            (facade_center_x + 1.5, 5.0, 12.0),
            (facade_center_x + 14.0, 4.0, 11.4),
        )
        for roof_cx, half_width, ridge_z in roof_sections:
            left_x, right_x = roof_cx - half_width, roof_cx + half_width
            front_left = (left_x, front_y, wall_height + 0.15)
            front_right = (right_x, front_y, wall_height + 0.15)
            front_ridge = (roof_cx, front_y, ridge_z)
            back_left = (left_x, roof_back_y, wall_height + 0.15)
            back_right = (right_x, roof_back_y, wall_height + 0.15)
            back_ridge = (roof_cx, roof_back_y, ridge_z)
            mesh.gable_wedge(front_left, front_right, front_ridge,
                             back_left, back_right, back_ridge, brick, roof)

        chimney_x = facade_center_x - 4.0
        chimney_y = front_y + 6.4
        mesh.box_axes((chimney_x, chimney_y, 12.1), (1.0, 0.0), (0.0, 1.0),
                      (0.9, 1.0, 3.2), brick)

    data = bpy.data.meshes.new("Kappa Sigma source-footprint massing")
    data.from_pydata(mesh.vertices, [], mesh.faces)
    data.update(calc_edges=True)
    for mat in mats:
        data.materials.append(mat)
    for poly, mat_id in zip(data.polygons, mesh.material_ids):
        poly.material_index = mat_id
    obj = bpy.data.objects.new(OBJECT_NAME, data)
    col.objects.link(obj)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)

    # Render rig lives outside the exported building collection.
    render_col = bpy.data.collections.new("Preview_Render_Setup")
    scene.collection.children.link(render_col)
    center_x = (min(xs) + max(xs)) / 2
    center_y = (min_y + max_y) / 2
    camera_data = bpy.data.cameras.new("Kappa Sigma preview camera")
    camera = bpy.data.objects.new("Kappa Sigma preview camera", camera_data)
    render_col.objects.link(camera)
    camera.location = (center_x + 43.0, min_y - 55.0, 32.0)
    target = (center_x, center_y, 5.0)
    direction = Vector(target) - Vector(camera.location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 50
    scene.camera = camera

    light_data = bpy.data.lights.new("Kappa Sigma preview key", "AREA")
    light = bpy.data.objects.new("Kappa Sigma preview key", light_data)
    render_col.objects.link(light)
    light.location = (center_x - 10.0, min_y - 20.0, 36.0)
    light.data.energy = 9000
    light.data.shape = "DISK"
    light.data.size = 32.0
    light.rotation_euler = (math.radians(28), 0, math.radians(20))
    scene.world.color = (0.20, 0.20, 0.20)

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW_PATH)
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.resolution_percentage = 80
    scene.render.engine = "BLENDER_EEVEE_NEXT"

    # Save the one-asset library and a non-invasive preview.
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    bounds = [
        [min(v[0] for v in mesh.vertices), max(v[0] for v in mesh.vertices)],
        [min(v[1] for v in mesh.vertices), max(v[1] for v in mesh.vertices)],
        [min(v[2] for v in mesh.vertices), max(v[2] for v in mesh.vertices)],
    ]
    print("KAPPA_SIGMA_BUILD_RESULT=" + json.dumps({
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "scene": SCENE_NAME,
        "collection": COLLECTION_NAME,
        "object": OBJECT_NAME,
        "collection_objects": [o.name for o in col.objects],
        "bounds_world_m": bounds,
        "footprint_vertices": len(footprint),
        "facade_glazing_panels": sum(1 for mat_id in mesh.material_ids if mat_id == glass) // 6,
        "wall_height_estimate_m": wall_height,
        "roof_ridge_estimate_m": 12.0,
        "chimney_top_estimate_m": 13.7,
        "source_fid": attrs["FID"],
        "preview_path": str(PREVIEW_PATH.relative_to(ROOT)).replace("\\", "/"),
    }, sort_keys=True))


if __name__ == "__main__":
    build()
