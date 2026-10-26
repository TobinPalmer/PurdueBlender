"""Build the Purdue Student Health Center (PUSH) massing from Purdue GIS.

The footprint and campus location follow Purdue BuildingShapes FID 274.
The red brick, pale trim, repeated windows, entry, and tiled hip roof are
modeled from Purdue's 2020 exterior photograph. Vertical dimensions remain an
estimate: GIS level records and the photograph do not fully agree on the
visible story count.
"""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_student_health_center_push_1200c3b"
ASSET_FILE = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS_FILE = ROOT / "audit" / ASSET_ID / "sources" / "purdue_gis_fid274_raw.json"
PREVIEW_FILE = ROOT / "audit" / ASSET_ID / "renders" / "push_exterior_preview.png"
TOP_FILE = ROOT / "audit" / ASSET_ID / "renders" / "push_footprint_preview.png"
RESULT_FILE = ROOT / "audit" / ASSET_ID / "build_result.json"
REGIONS_FILE = ROOT / "audit" / ASSET_ID / "mass_regions.json"
SCENE_NAME = "Building_" + ASSET_ID
COLLECTION_NAME = "Asset_" + ASSET_ID

ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
# The GIS says NUM_LEVELS=5, B=-11.3, F01-F04=11.3..45.2, Extrution=48 and
# R=69.8, with no explicit units/semantics. The 2020 oblique photo looks like
# three visible levels. Use a three-band photo reading and a 48-ft envelope
# only as a clearly labeled estimate; never present either as measured truth.
ESTIMATED_HEIGHT_M = 48.0 * 0.3048
MAIN_EAVE_M = 10.45
MAIN_RIDGE_M = ESTIMATED_HEIGHT_M
ENTRY_EAVE_M = 3.8
ENTRY_RIDGE_M = 5.6
REAR_EAVE_M = 5.8
REAR_CAP_M = 6.4
PHOTO_VISIBLE_LEVELS_ESTIMATE = 3


def local_xy(lon, lat):
    """Project WGS84 coordinates using the repository's documented transform."""
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return (x, y)


def material(name, color, roughness=0.78):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


class MeshBuilder:
    """One mesh containing disconnected, material-assigned building details."""
    def __init__(self):
        self.verts = []
        self.faces = []
        self.material_ids = []

    def face(self, points, material_id):
        start = len(self.verts)
        self.verts.extend(tuple(p) for p in points)
        self.faces.append(tuple(range(start, start + len(points))))
        self.material_ids.append(material_id)

    def box(self, center, axes, size, material_id):
        c = Vector(center)
        ax, ay, az = (Vector(a) for a in axes)
        sx, sy, sz = (v / 2.0 for v in size)
        corners = [
            c + ax * (sx * x) + ay * (sy * y) + az * (sz * z)
            for x, y, z in (
                (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
            )
        ]
        for indices in (
            (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
            (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        ):
            self.face([corners[i] for i in indices], material_id)


def signed_area(poly):
    return 0.5 * sum(
        poly[i][0] * poly[(i + 1) % len(poly)][1]
        - poly[(i + 1) % len(poly)][0] * poly[i][1]
        for i in range(len(poly))
    )


def dist2(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def is_same_segment(a, b, c, d, tol=0.04):
    return (dist2(a, c) < tol and dist2(b, d) < tol) or (dist2(a, d) < tol and dist2(b, c) < tol)


def roof_z(point, axis, center, eave, peak, max_offset):
    # A ridge runs along axis; height falls linearly across the gable.
    across = (-axis[1], axis[0])
    offset = abs((point[0] - center[0]) * across[0] + (point[1] - center[1]) * across[1])
    return eave + (peak - eave) * max(0.0, 1.0 - offset / max(max_offset, 0.01))


def main():
    feature = json.loads(GIS_FILE.read_text(encoding="utf-8-sig"))["features"][0]
    attrs = feature["attributes"]
    assert attrs["FID"] == 274
    assert attrs["BLDG_ABBR"] == "PUSH"
    assert attrs["ADDRESS"] == "601 Stadium Mall Drive"
    footprint = [local_xy(lon, lat) for lon, lat in feature["geometry"]["rings"][0][:-1]]
    area = signed_area(footprint)
    is_ccw = area > 0

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for scene in list(bpy.data.scenes):
        if scene != bpy.context.scene:
            bpy.data.scenes.remove(scene)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)

    mats = [
        material("PUSH warm red brick", (0.48, 0.12, 0.07)),
        material("PUSH pale limestone trim", (0.70, 0.65, 0.53)),
        material("PUSH blue gray glazing", (0.105, 0.20, 0.25), 0.32),
        material("PUSH terracotta tile roof", (0.40, 0.11, 0.045)),
        material("PUSH dark entrance glazing", (0.055, 0.12, 0.15), 0.25),
        material("PUSH metal hardware", (0.30, 0.32, 0.31), 0.36),
    ]
    mesh = MeshBuilder()

    region_data = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    regions = {r["name"]: r for r in region_data["regions"]}
    heights = {
        "main": (MAIN_EAVE_M, MAIN_RIDGE_M, 3),
        "entry_wing": (ENTRY_EAVE_M, ENTRY_RIDGE_M, 3),
        "southeast_wing": (REAR_EAVE_M, REAR_CAP_M, 3),
    }
    center_xy = Vector((sum(p[0] for p in footprint) / len(footprint),
                        sum(p[1] for p in footprint) / len(footprint)))
    seam_edges = []
    for region in regions.values():
        for seam in region["internal_seams"]:
            a, b = seam["coordinates_xy_m"]
            seam_edges.append((a, b, region["name"], seam["neighbor"]))

    # Build walls by region, using the seam graph to join low wings into the
    # taller main block without drawing duplicate internal walls.
    for name, region in regions.items():
        eave, peak, wall_mat = heights[name]
        loops = [region["exterior_xy_m"], *region.get("holes_xy_m", [])]
        for loop in loops:
            for i, a in enumerate(loop):
                b = loop[(i + 1) % len(loop)]
                seam = next((s for s in seam_edges if s[2] == name and is_same_segment(a, b, s[0], s[1])), None)
                if seam:
                    if name == "main":
                        lower_eave = heights[seam[3]][0]
                        mesh.face([(a[0], a[1], lower_eave), (b[0], b[1], lower_eave),
                                   (b[0], b[1], eave), (a[0], a[1], eave)], 0)
                    continue
                mesh.face([(a[0], a[1], 0), (b[0], b[1], 0),
                           (b[0], b[1], eave), (a[0], a[1], eave)], wall_mat)

    # Region-specific roof triangulation follows the 2023 IGIO orthophoto:
    # red tiled pitched main block, low tiled entrance wing, and low flat rear
    # extension. All region partitions remain inside the official FID 274 ring.
    for name, region in regions.items():
        eave, peak, roof_mat = heights[name]
        axis = region["roof_axis_xy"]
        norm = math.hypot(*axis)
        axis = (axis[0] / norm, axis[1] / norm)
        center = region["roof_center_xy_m"]
        across = (-axis[1], axis[0])
        offsets = [abs((p[0] - center[0]) * across[0] + (p[1] - center[1]) * across[1])
                   for tri in region["roof_triangles_xy_m"] for p in tri]
        max_offset = max(offsets)
        for tri in region["roof_triangles_xy_m"]:
            if name == "southeast_wing":
                pts = [(p[0], p[1], peak) for p in tri]
            else:
                pts = [(p[0], p[1], roof_z(p, axis, center, eave, peak, max_offset)) for p in tri]
            mesh.face(pts, roof_mat)

    # Facades: long public-facing entry frontage gets a large glazed vestibule;
    # the upper brick block receives broader, more regularly spaced windows.
    def add_window(a, b, along, width, zc, height):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        tx, ty = dx / length, dy / length
        lx, ly = -ty, tx
        sign = 1.0 if is_ccw else -1.0
        nx, ny = sign * ty, sign * -tx
        axes = ((tx, ty, 0), (lx, ly, 0), (0, 0, 1))
        center = (a[0] + tx * along + nx * 0.13, a[1] + ty * along + ny * 0.13, zc)
        mesh.box((center[0] + nx * 0.10, center[1] + ny * 0.10, zc), axes, (width, 0.07, height), 2)
        trim = (center[0] + nx * 0.16, center[1] + ny * 0.16)
        for side in (-1, 1):
            mesh.box((trim[0] + tx * side * (width + 0.10) / 2,
                      trim[1] + ty * side * (width + 0.10) / 2, zc), axes, (0.11, 0.06, height + 0.22), 1)
            mesh.box((trim[0], trim[1], zc + side * (height + 0.06) / 2), axes, (width + 0.12, 0.06, 0.11), 1)

    # The photo shows wide paired/window groups at regular upper-story rhythm;
    # we use larger 1.7 x 1.9 m openings, and leave other walls conservative.
    for i, a in enumerate(footprint):
        b = footprint[(i + 1) % len(footprint)]
        length = dist2(a, b)
        if length < 18:
            continue
        count = max(2, round(length / 6.3))
        margin = min(2.8, length * 0.12)
        for story in range(3):
            zc = 2.05 + story * 3.34
            for j in range(count):
                along = margin + (j + 0.5) * (length - 2 * margin) / count
                add_window(a, b, along, 1.72, zc, 1.82)
        # Subtle continuous stone courses establish three photo-read facade bands.
        dx, dy = b[0] - a[0], b[1] - a[1]
        tx, ty = dx / length, dy / length
        lx, ly = -ty, tx
        mesh.box(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 3.28),
                 ((tx, ty, 0), (lx, ly, 0), (0, 0, 1)), (length, 0.07, 0.09), 1)
        mesh.box(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 6.62),
                 ((tx, ty, 0), (lx, ly, 0), (0, 0, 1)), (length, 0.07, 0.09), 1)

    # Entrance is placed on the lower wing's exterior long wall, the frontage
    # visible in Purdue's oblique photo (not an inferred longest main-wall edge).
    entry_region = regions["entry_wing"]
    wing = entry_region["exterior_xy_m"]
    a, b = wing[2], wing[3]
    length = dist2(a, b)
    tx, ty = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    lx, ly = -ty, tx
    sign = 1.0 if is_ccw else -1.0
    nx, ny = sign * ty, sign * -tx
    entry_axes = ((tx, ty, 0), (lx, ly, 0), (0, 0, 1))
    along = length * 0.53
    door_center = (a[0] + tx * along + nx * 0.18, a[1] + ty * along + ny * 0.18, 1.55)
    mesh.box((door_center[0] + nx * 0.11, door_center[1] + ny * 0.11, 1.58), entry_axes, (3.5, 0.08, 2.85), 4)
    mesh.box((door_center[0] + nx * 0.20, door_center[1] + ny * 0.20, 3.08), entry_axes, (4.3, 0.08, 0.16), 1)
    mesh.box((door_center[0] + nx * 0.20, door_center[1] + ny * 0.20, 0.16), entry_axes, (4.3, 0.08, 0.18), 1)
    for side in (-1, 1):
        mesh.box((door_center[0] + tx * side * 2.08 + nx * 0.20,
                  door_center[1] + ty * side * 2.08 + ny * 0.20, 1.58), entry_axes, (0.15, 0.08, 3.05), 1)
    # Side-light glazing and three broad steps strengthen the recognizable entrance.
    for side in (-1, 1):
        mesh.box((door_center[0] + tx * side * 2.70 + nx * 0.18,
                  door_center[1] + ty * side * 2.70 + ny * 0.18, 1.42), entry_axes, (0.82, 0.08, 2.45), 2)
    for n in range(3):
        mesh.box((door_center[0] - nx * (0.55 + n * 0.43), door_center[1] - ny * (0.55 + n * 0.43), 0.08 + n * 0.02),
                 entry_axes, (5.6 + n * 0.42, 0.62, 0.10), 1)
    emblem_center = (door_center[0] - tx * 4.4 + nx * 0.13, door_center[1] - ty * 4.4 + ny * 0.13, 2.15)
    mesh.box(emblem_center, entry_axes, (0.20, 0.12, 1.75), 1)
    mesh.box((emblem_center[0], emblem_center[1], 2.65), entry_axes, (1.1, 0.12, 0.12), 1)

    data = bpy.data.meshes.new(ASSET_ID + "_mesh")
    data.from_pydata(mesh.verts, [], mesh.faces)
    data.materials.clear()
    for mat in mats:
        data.materials.append(mat)
    data.update()
    obj = bpy.data.objects.new("Student Health Center (PUSH)", data)
    asset.objects.link(obj)
    for poly, material_id in zip(data.polygons, mesh.material_ids):
        poly.material_index = material_id
    obj["source_fid"] = 274
    obj["vertical_height_status"] = "estimated only; GIS Extrution=48 units and R=69.8 semantics/units are undocumented; 48 ft is one possible interpretation"
    obj["facade_reference"] = "Purdue University/John Underwood, 2020 exterior photograph; Indiana 2023 orthophoto for roof plan"

    # Preview render camera, lighting, and floor remain outside the export collection.
    render_coll = bpy.data.collections.new("Preview_Rig")
    scene.collection.children.link(render_coll)
    ground_mat = material("Preview neutral ground", (0.47, 0.50, 0.48))
    ground_mesh = bpy.data.meshes.new("Preview_Ground_Mesh")
    ground_mesh.from_pydata([
        (-500, -500, -0.15), (500, -500, -0.15),
        (500, 500, -0.15), (-500, 500, -0.15),
    ], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(ground_mat)
    ground = bpy.data.objects.new("Preview Ground", ground_mesh)
    render_coll.objects.link(ground)

    def point_camera(camera, target):
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()

    target = (center_xy.x, center_xy.y, 6.5)
    cam_data = bpy.data.cameras.new("PUSH Preview Camera")
    cam = bpy.data.objects.new("PUSH Preview Camera", cam_data)
    render_coll.objects.link(cam)
    # The principal 51 m public elevation runs about 51 degrees clockwise
    # from east; photograph it from its outward (northeast) side rather than
    # looking along the facade.
    edge_mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    cam.location = (edge_mid[0] + nx * 82, edge_mid[1] + ny * 82, 31)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 112
    point_camera(cam, target)
    scene.camera = cam

    def add_area(name, location, energy, size):
        light_data = bpy.data.lights.new(name, "AREA")
        light_data.energy = energy
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(name, light_data)
        render_coll.objects.link(light)
        light.location = location
        point_camera(light, target)

    add_area("PUSH soft key", (center_xy.x + 25, center_xy.y + 35, 70), 32000, 60)
    add_area("PUSH fill", (center_xy.x - 50, center_xy.y - 10, 42), 12000, 50)
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW_FILE)
    scene.render.film_transparent = False
    scene.world.color = (0.35, 0.35, 0.35)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.50, 0.50, 0.50, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_FILE))
    bpy.ops.render.render(write_still=True)

    # Top-down footprint evidence render.
    cam.location = (center_xy.x, center_xy.y, 150)
    cam.data.ortho_scale = 82
    point_camera(cam, (center_xy.x, center_xy.y, 0))
    scene.render.resolution_x = 1300
    scene.render.resolution_y = 1300
    scene.render.filepath = str(TOP_FILE)
    bpy.ops.render.render(write_still=True)

    xs = [p[0] for p in footprint]
    ys = [p[1] for p in footprint]
    report = {
        "asset_id": ASSET_ID,
        "asset_file": str(ASSET_FILE.relative_to(ROOT)),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "source_fid": 274,
        "gis_feature_name": attrs["BUILDING_N"],
        "gis_abbreviation": attrs["BLDG_ABBR"],
        "address": attrs["ADDRESS"],
        "footprint_vertex_count": len(footprint),
        "footprint_area_m2_projected": abs(area),
        "footprint_bounds_m": [[min(xs), min(ys)], [max(xs), max(ys)]],
        "modeled_facade_levels_photo_read_estimate": PHOTO_VISIBLE_LEVELS_ESTIMATE,
        "estimated_region_eaves_m": {"main": MAIN_EAVE_M, "entry_wing": ENTRY_EAVE_M, "southeast_wing": REAR_EAVE_M},
        "estimated_region_roof_peaks_m": {"main": MAIN_RIDGE_M, "entry_wing": ENTRY_RIDGE_M, "southeast_wing": REAR_CAP_M},
        "estimated_height_m": ESTIMATED_HEIGHT_M,
        "vertical_source_conflict": "GIS records NUM_LEVELS=5, CountOfFLO=5, B=-11.3, F01-F04=11.3/22.6/33.9/45.2, Extrution=48, R=69.8; units and field semantics are undocumented. The 2020 photo appears to show three above-grade facade bands. The model uses that visual interpretation and a 48-ft-equivalent envelope only as estimates.",
        "mass_zones": {name: {"area_m2": region["area_m2"], "roof_form": region["roof_form"]} for name, region in regions.items()},
        "entry_orientation_status": "photo-informed interpretation; frontage placed on the exterior edge of the low entry wing, exact wall orientation is not surveyed",
        "render_preview": str(PREVIEW_FILE.relative_to(ROOT)),
        "render_top": str(TOP_FILE.relative_to(ROOT)),
        "mesh_vertex_count": len(data.vertices),
        "mesh_polygon_count": len(data.polygons),
        "material_count": len(data.materials),
    }
    RESULT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PUSH_BUILD_RESULT=" + json.dumps(report))


if __name__ == "__main__":
    main()
