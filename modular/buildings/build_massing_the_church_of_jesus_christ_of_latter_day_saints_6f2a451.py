from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS = ROOT / "audit" / "official_purdue_buildings_wgs84.json"
AUDIT = ROOT / "audit" / ASSET_ID
RENDERS = AUDIT / "renders"
COLLECTION = "Asset_" + ASSET_ID
SCENE = "Building_" + ASSET_ID
OBJECT_NAME = "The Church of Jesus Christ of Latter-day Saints"
GIS_FID = 779


def xy(lon: float, lat: float) -> tuple[float, float]:
    """Purdue campus's documented approximate WGS84-to-local-metre conversion."""
    return (
        (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
        (lat - 40.4274) * 111040.0,
    )


def unit(v: Vector) -> Vector:
    out = Vector((v.x, v.y, 0.0))
    if out.length < 1e-9:
        raise ValueError("Cannot normalize a zero-length horizontal vector")
    return out.normalized()


def unit2(v: Vector) -> Vector:
    out = Vector((v.x, v.y))
    if out.length < 1e-9:
        raise ValueError("Cannot normalize a zero-length plan vector")
    return out.normalized()


class MeshBuilder:
    """Append separate architectural solids into one manifest-listed mesh object."""

    def __init__(self, materials: list[bpy.types.Material]):
        self.materials = materials
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[int, ...]] = []
        self.material_ids: list[int] = []

    def component(self, vertices, faces, material_id: int):
        offset = len(self.vertices)
        self.vertices.extend(tuple(float(c) for c in v) for v in vertices)
        for face in faces:
            self.faces.append(tuple(offset + int(i) for i in face))
            self.material_ids.append(material_id)

    def box(self, center, size, material_id: int, angle: float = 0.0):
        x, y, z = center
        sx, sy, sz = size
        c, s = math.cos(angle), math.sin(angle)
        coords = [
            (-sx / 2, -sy / 2, -sz / 2),
            (sx / 2, -sy / 2, -sz / 2),
            (sx / 2, sy / 2, -sz / 2),
            (-sx / 2, sy / 2, -sz / 2),
            (-sx / 2, -sy / 2, sz / 2),
            (sx / 2, -sy / 2, sz / 2),
            (sx / 2, sy / 2, sz / 2),
            (-sx / 2, sy / 2, sz / 2),
        ]
        verts = [(x + a * c - b * s, y + a * s + b * c, z + h) for a, b, h in coords]
        faces = [
            (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
            (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        ]
        self.component(verts, faces, material_id)

    def face_box(self, center, tangent: Vector, outward: Vector, width, depth, height, material_id):
        """A box oriented to a facade plane: width follows tangent, depth is outward."""
        t, n = unit(tangent), unit(outward)
        center = Vector(center)
        verts = []
        for zoff in (-height / 2, height / 2):
            for toff, noff in (
                (-width / 2, -depth / 2),
                (width / 2, -depth / 2),
                (width / 2, depth / 2),
                (-width / 2, depth / 2),
            ):
                p = center + t * toff + n * noff + Vector((0, 0, zoff))
                verts.append(tuple(p))
        self.component(
            verts,
            [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
            material_id,
        )

    def triangle_prism(self, vertices, material_id):
        self.component(vertices, [(0, 1, 2)], material_id)


def make_material(name: str, rgb, roughness=0.82, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def get_source_polygon():
    data = json.loads(GIS.read_text(encoding="utf-8"))
    feature = next(f for f in data["features"] if f["attributes"].get("FID") == GIS_FID)
    ring = feature["geometry"]["rings"][0]
    points = []
    for lon, lat in ring:
        p = xy(lon, lat)
        if not points or (Vector(p) - Vector(points[-1])).length > 0.001:
            points.append(p)
    if len(points) > 2 and (Vector(points[0]) - Vector(points[-1])).length < 0.001:
        points.pop()
    if len(points) != 4:
        raise ValueError(f"Expected the FID {GIS_FID} four-corner footprint, got {len(points)} points")
    return feature, points


def prism(builder: MeshBuilder, points, z0, z1, mat_id):
    n = len(points)
    verts = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    faces.append(tuple(reversed(range(n, 2 * n))))
    faces.append(tuple(range(n)))
    builder.component(verts, faces, mat_id)


def add_window(builder, center, tangent, outward, width, height, z, ids):
    t, n = unit(tangent), unit(outward)
    center = Vector((center.x, center.y, 0.0)) + n * 0.06 + Vector((0, 0, z))
    # The panorama shows dark, modest openings set in brick rather than bright stone trim.
    # Opening sizes and mullion counts remain approximate due perspective and vegetation.
    builder.face_box(center, t, n, width + 0.10, 0.10, height + 0.10, ids[2])
    builder.face_box(center + n * 0.075, t, n, width, 0.045, height, ids[1])
    builder.face_box(center + n * 0.135, t, n, 0.045, 0.05, height * 0.93, ids[2])


def add_gable(builder, corners, eave_z, ridge_z, roof_material, gable_material):
    """A low ridge spanning the short axis; the roof form is explicitly estimated."""
    # GIS ring order is NE, SE, SW, NW. The long ridge runs along its long axis.
    north_mid = (Vector(corners[0]) + Vector(corners[3])) * 0.5
    south_mid = (Vector(corners[1]) + Vector(corners[2])) * 0.5
    ridge_n = (north_mid.x, north_mid.y, ridge_z)
    ridge_s = (south_mid.x, south_mid.y, ridge_z)
    eave = [(x, y, eave_z) for x, y in corners]
    builder.component(
        [eave[0], ridge_n, ridge_s, eave[1]],
        [(0, 1, 2, 3)], roof_material,
    )
    builder.component(
        [ridge_n, eave[3], eave[2], ridge_s],
        [(0, 1, 2, 3)], roof_material,
    )
    # Brick triangles close the north/south ends below the roof planes.
    builder.triangle_prism([eave[0], (ridge_n[0], ridge_n[1], eave_z), eave[3]], gable_material)
    builder.triangle_prism([eave[1], eave[2], (ridge_s[0], ridge_s[1], eave_z)], gable_material)
    return north_mid, south_mid


def exterior_openings(builder, points, ids, eave_z):
    # Select the long west wall, the visible face from the 23 Waldron Street view.
    edges = []
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        length = (Vector(b) - Vector(a)).length
        midpoint = (Vector(a) + Vector(b)) * 0.5
        if length > 25:
            edges.append((midpoint.x, i, a, b, length))
    if not edges:
        raise ValueError("Could not identify the long facade edge from GIS footprint")
    _, edge_i, a, b, length = min(edges, key=lambda e: e[0])
    tangent = unit(Vector(b) - Vector(a))
    mid = (Vector(a) + Vector(b)) * 0.5
    centroid = sum((Vector(p) for p in points), Vector((0, 0))) / len(points)
    outward = unit(mid - centroid)

    # The Street View composition puts the entrance well left of facade center and
    # shows a broad, recessed glazed zone divided by brick piers. Fractions and sizes
    # are visual estimates from one oblique, partly occluded photo.
    # The west-front camera reads this GIS edge in reverse screen order, so the
    # higher GIS edge fractions put the entry left-of-center in the saved render.
    zone_t, door_t = 0.65, 0.71
    zone_center_xy = Vector(a) + (Vector(b) - Vector(a)) * zone_t
    entry_center_xy = Vector(a) + (Vector(b) - Vector(a)) * door_t
    zone_center = Vector((zone_center_xy.x, zone_center_xy.y, 1.70)) + outward * 0.12
    zone_width, zone_height = 7.2, 2.95
    # Dark backing reads as the recessed glazing behind the brick columns.
    builder.face_box(zone_center, tangent, outward, zone_width, 0.08, zone_height, ids[1])
    # Four modest brick piers define three visible glazed bays.
    for offset in (-zone_width / 2, -1.15, 1.15, zone_width / 2):
        pier_center = zone_center + tangent * offset + outward * 0.28
        builder.face_box(pier_center, tangent, outward, 0.32, 0.55, 3.18, 0)
    # Brick fascia/lintel closes the broad entry zone below the low roof eave.
    lintel_center = Vector((zone_center_xy.x, zone_center_xy.y, 3.42)) + outward * 0.25
    builder.face_box(lintel_center, tangent, outward, zone_width + 0.42, 0.50, 0.34, 0)

    # Narrower double entry doors sit toward the left side of the glazed zone.
    entry_center = Vector((entry_center_xy.x, entry_center_xy.y, 1.43)) + outward * 0.34
    door_width, door_height = 1.65, 2.48
    builder.face_box(entry_center, tangent, outward, door_width + 0.12, 0.10,
                     door_height + 0.08, ids[2])
    builder.face_box(entry_center + outward * 0.07, tangent, outward,
                     door_width, 0.045, door_height, ids[1])
    builder.face_box(entry_center + outward * 0.13, tangent, outward,
                     0.045, 0.05, door_height * 0.94, ids[2])
    # Low sill/transom divisions are simplified; exact pane layout is not resolved.
    builder.face_box(entry_center + Vector((0, 0, -0.34)) + outward * 0.13,
                     tangent, outward, door_width * 0.92, 0.045, 0.055, ids[2])
    builder.face_box(entry_center + Vector((0, 0, 0.88)) + outward * 0.13,
                     tangent, outward, door_width * 0.92, 0.045, 0.055, ids[2])

    # Two isolated small windows are visible at the ends of the photographed wall;
    # their deliberately irregular placement avoids inventing a regular rhythm.
    window_specs = ((0.92, 1.05, 1.08, 2.18), (0.15, 0.92, 1.02, 2.12))
    for fraction, width, height, sill_z in window_specs:
        center = Vector(a) + (Vector(b) - Vector(a)) * fraction
        add_window(builder, center, tangent, outward, width, height, sill_z, (ids[0], ids[1], ids[2]))

    # Access ramp and three steps are non-structural foreground geometry, excluded from
    # the GIS wall-footprint comparison. They are indicated by the July 2023 street view.
    ramp_center = Vector((entry_center_xy.x, entry_center_xy.y, 0.0)) + outward * 2.05
    ramp = [
        ramp_center - tangent * 1.05 - outward * 1.80 + Vector((0, 0, 0.07)),
        ramp_center + tangent * 1.05 - outward * 1.80 + Vector((0, 0, 0.07)),
        ramp_center + tangent * 1.05 + outward * 1.80 + Vector((0, 0, -0.20)),
        ramp_center - tangent * 1.05 + outward * 1.80 + Vector((0, 0, -0.20)),
    ]
    builder.component([tuple(p) for p in ramp], [(0, 1, 2, 3)], ids[4])
    for rail_sign in (-1, 1):
        rail_center = ramp_center + tangent * (rail_sign * 0.99) + outward * 0.15 + Vector((0, 0, 0.78))
        builder.box(tuple(rail_center), (3.1, 0.045, 0.07), ids[5],
                    math.atan2(outward.y, outward.x))
        for post_t in (0.0, 0.48, 0.96):
            p = ramp_center + tangent * (rail_sign * 0.99) + outward * (0.15 + post_t * 2.75) + Vector((0, 0, 0.35 - post_t * 0.22))
            builder.box(tuple(p), (0.045, 0.045, 0.78), ids[5])

    # A short three-step stair run beside the ramp, kept below wall-height and out of the shell outline.
    step_side = -0.95
    for i in range(3):
        step_depth = 0.32 + i * 0.42
        center = (ramp_center + tangent * step_side - outward * (1.68 - step_depth / 2)
                  + Vector((0, 0, 0.06 + i * 0.12)))
        builder.face_box(center, tangent, outward, 1.25, step_depth, 0.12, ids[4])


def write_render(scene, builder_object, view_name, camera_location, target, ortho_scale=None):
    camera_data = bpy.data.cameras.new(f"PreviewCamera_{view_name}")
    camera = bpy.data.objects.new(f"PreviewCamera_{view_name}", camera_data)
    scene.collection.objects.link(camera)
    camera.location = camera_location
    camera.rotation_euler = (Vector(target) - Vector(camera_location)).to_track_quat("-Z", "Y").to_euler()
    if ortho_scale:
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = ortho_scale
    scene.camera = camera
    area_data = bpy.data.lights.new(f"PreviewArea_{view_name}", "AREA")
    area = bpy.data.objects.new(f"PreviewArea_{view_name}", area_data)
    scene.collection.objects.link(area)
    area.location = (target[0] - 15, target[1] + 20, target[2] + 27)
    area_data.energy = 4200
    area_data.shape = "DISK"
    area_data.size = 22
    area.rotation_euler = (Vector(target) - Vector(area.location)).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(RENDERS / f"{view_name}.png")
    bpy.ops.render.render(write_still=True)
    scene.collection.objects.unlink(camera)
    scene.collection.objects.unlink(area)
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.objects.remove(area, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    bpy.data.lights.remove(area_data)
    scene.camera = None


def build():
    AUDIT.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    feature, points = get_source_polygon()
    attrs = feature["attributes"]

    # Start clean so the future-version 5.2 source file is never saved by Blender 4.5.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new("LDS_Institute_Preview_World")
    scene.world.color = (0.55, 0.55, 0.55)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.55, 0.55, 0.55, 1.0)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
    scene.render.image_settings.color_mode = "RGBA"

    coll = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(coll)
    mats = [
        make_material("LDS_Institute_Brick", (0.31, 0.105, 0.070)),
        make_material("LDS_Institute_Brick_Accent", (0.39, 0.145, 0.095)),
        make_material("LDS_Institute_Glass", (0.045, 0.10, 0.12), roughness=0.24, metallic=0.12),
        make_material("LDS_Institute_Dark_Frame", (0.075, 0.070, 0.060), roughness=0.48, metallic=0.25),
        make_material("LDS_Institute_Low_Dark_Roof", (0.13, 0.12, 0.11), roughness=0.76),
        make_material("LDS_Institute_Red_Metal_Roof", (0.35, 0.12, 0.065), roughness=0.66, metallic=0.12),
        make_material("LDS_Institute_Stone", (0.67, 0.61, 0.51)),
        make_material("LDS_Institute_Concrete", (0.48, 0.46, 0.42)),
        make_material("LDS_Institute_Rail", (0.10, 0.10, 0.09), roughness=0.45, metallic=0.5),
    ]
    # Material slots: brick, accent brick, glass, dark frame, dark roof, red roof,
    # stone reveals, concrete access, metal rail.
    g = MeshBuilder(mats)
    body_height = 4.15  # estimated from the single-story July 2023 view; not a survey
    main_eave = 4.30
    main_ridge = 5.45
    secondary_ridge = 5.90
    prism(g, points, 0.0, body_height, 0)
    add_gable(g, points, main_eave, main_ridge, 4, 1)

    # Street View shows a small higher reddish roof behind the dark front roof. Its
    # footprint and rise are estimated, and it may represent a rear roof section.
    # Construct it as a compact raised cross-gable over the eastern/rear half.
    p = [Vector(q) for q in points]
    north_mid = (p[0] + p[3]) * 0.5
    south_mid = (p[1] + p[2]) * 0.5
    east_center = (p[0] + p[1]) * 0.5
    west_center = (p[2] + p[3]) * 0.5
    eastward = unit2(east_center - west_center)
    longward = unit2(south_mid - north_mid)
    center = sum(p, Vector((0, 0))) / 4
    secondary_center = center + eastward * 3.8 + longward * 1.0
    width, length = 7.2, 13.5
    n0 = secondary_center - longward * (length / 2) - eastward * (width / 2)
    n1 = secondary_center - longward * (length / 2) + eastward * (width / 2)
    s1 = secondary_center + longward * (length / 2) + eastward * (width / 2)
    s0 = secondary_center + longward * (length / 2) - eastward * (width / 2)
    sub_corners = [tuple(n1), tuple(s1), tuple(s0), tuple(n0)]
    add_gable(g, sub_corners, 4.52, secondary_ridge, 5, 1)

    exterior_openings(g, points, (6, 2, 3, 4, 7, 8), main_eave)
    me = bpy.data.meshes.new(f"{ASSET_ID}_Mesh")
    me.from_pydata(g.vertices, [], g.faces)
    me.materials.clear()
    for mat in mats:
        me.materials.append(mat)
    me.update()
    obj = bpy.data.objects.new(OBJECT_NAME, me)
    coll.objects.link(obj)
    for poly, mat_id in zip(me.polygons, g.material_ids):
        poly.material_index = mat_id
    obj["stable_building_id"] = ASSET_ID
    obj["source_feature_id"] = GIS_FID
    obj["source_feature_name"] = attrs.get("BUILDING_N", "")
    obj["reconciled_identity"] = "Institute of Religion at 14 Waldron Street; GIS FID 779. Separate from 3224 Jasper meetinghouse."
    obj["plan_source"] = "Purdue campus GIS FID 779 WGS84 polygon, transformed using project local campus conversion."
    obj["story_evidence"] = "GIS NUM_LEVELS=1. One-story massing is supported; roof/eave heights are estimated from July 2023 Street View."
    obj["height_evidence"] = "No scaled elevation or documented height. Modeled body top 4.15 m, main ridge 5.45 m, rear roof ridge 5.90 m, all explicitly estimated. Legacy GIS Extrution=12 has unknown units."
    obj["roof_evidence"] = "July 2023 Google Street View from 23 Waldron shows a low dark roof and a small higher reddish roof behind the main roofline. Roof pitch/plan and secondary roof limits are estimated from the oblique, partly occluded view."
    obj["facade_evidence"] = "The July 2023 view shows red-brown brick, an off-center broad recessed glazed front zone with brick piers, access ramp/steps, and isolated small openings. The two modeled small windows, bay/pier layout, entry-door position, heights, materials beyond brick, and all hidden faces remain estimated or unverified."
    obj["structural_footprint_note"] = "Structural shell uses the FID 779 GIS footprint. The access ramp, steps, and rails are non-structural additions outside that footprint."
    obj["source_image"] = "audit/massing_the_church_of_jesus_christ_of_latter_day_saints_6f2a451/sources/google_street_view_23_waldron_2023.jpg"
    coll["stable_building_id"] = ASSET_ID
    coll["export_collection"] = COLLECTION
    coll["source_feature_id"] = GIS_FID
    coll["coordinate_contract"] = "Massing asset remains in campus-world coordinates; do not localize or alter master placement."

    xy_pts = [(x, y) for x, y in points]
    cx = sum(x for x, _ in xy_pts) / len(xy_pts)
    cy = sum(y for _, y in xy_pts) / len(xy_pts)
    target = (cx, cy, 2.65)
    scene["asset_id"] = ASSET_ID
    scene["source_fid"] = GIS_FID
    scene["source_name"] = attrs.get("BUILDING_N")
    scene["official_address"] = "14 Waldron St, West Lafayette, IN"
    scene["estimated_height_m"] = secondary_ridge
    scene["height_status"] = "estimated from unscaled, oblique July 2023 Street View; no measured elevation available"
    scene["legacy_gis_extrution"] = attrs.get("Extrution")
    scene["legacy_gis_extrution_units"] = "undocumented"
    scene["story_count_from_gis"] = attrs.get("NUM_LEVELS")

    # Preview cameras and lights exist only during rendering; the saved library keeps
    # exactly the single manifest-listed building object in its exported collection.
    write_render(scene, obj, "01_west_northwest_hero", (cx - 43, cy + 22, 18), target, 43)
    write_render(scene, obj, "02_west_facade", (cx - 42, cy + 2, 7.5), (cx, cy, 2.7), 39)
    write_render(scene, obj, "03_top", (cx, cy, 54), (cx, cy, 0), 42)
    scene.render.filepath = "//"
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

    result = {
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET.relative_to(ROOT)),
        "collection": COLLECTION,
        "scene": SCENE,
        "object_count_in_export_collection": len(coll.objects),
        "source_fid": GIS_FID,
        "source_name": attrs.get("BUILDING_N"),
        "source_address": attrs.get("ADDRESS"),
        "source_polygon_xy_m": [[round(x, 4), round(y, 4)] for x, y in points],
        "shell_height_estimated_m": body_height,
        "main_roof_ridge_estimated_m": main_ridge,
        "secondary_roof_ridge_estimated_m": secondary_ridge,
        "preview_renders": [str(p.relative_to(ROOT)) for p in sorted(RENDERS.glob("*.png"))],
        "uncertainties": [
            "No scaled elevation or measured height available; all z dimensions are estimates.",
            "The July 2023 photograph is oblique and partly tree-occluded; exact window count and spacing remain uncertain.",
            "The small raised reddish roof may be a rear roof section; its footprint and pitch are estimated.",
            "Purdue Archives catalogs older exterior Institute photos, but the finding-aid PDF is blocked by a 403 challenge and images were not retrieved.",
        ],
    }
    (AUDIT / "build_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    build()
