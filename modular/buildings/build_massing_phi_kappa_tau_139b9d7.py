"""Rebuild the Rossen-assigned Phi Kappa Tau campus-world massing asset.

The GIS source is the current 416 N Chauncey footprint (Purdue BuildingShapes
FID 820; historically labeled Theta Tau). The older FID 856 crosswalk is
conflicted and is documented separately under audit/phi_kappa_tau/.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "phi_kappa_tau"
SOURCE = AUDIT / "fid820_arcgis_snapshot.json"
OUT = ROOT / "modular" / "buildings" / "massing_phi_kappa_tau_139b9d7.blend"
PREVIEW = AUDIT / "preview_phi_kappa_tau.png"
PREVIEW_FRONT = AUDIT / "preview_phi_kappa_tau_front.png"
PREVIEW_TOP = AUDIT / "preview_phi_kappa_tau_top.png"
REPORT = AUDIT / "build_validation.json"

ASSET_ID = "massing_phi_kappa_tau_139b9d7"
COLLECTION_NAME = "Asset_massing_phi_kappa_tau_139b9d7"
SCENE_NAME = "Building_massing_phi_kappa_tau_139b9d7"
OBJECT_NAME = "Phi Kappa Tau"

LAT0 = 40.4274
LON0 = -86.9137
LAT_M = 111040.0
LON_M = 111412.84 * math.cos(math.radians(LAT0))
WEB_MERCATOR_R = 6378137.0


def local_xy_from_3857(x: float, y: float) -> tuple[float, float]:
    lon = math.degrees(x / WEB_MERCATOR_R)
    lat = math.degrees(2.0 * math.atan(math.exp(y / WEB_MERCATOR_R)) - math.pi / 2.0)
    return (lon - LON0) * LON_M, (lat - LAT0) * LAT_M


def polygon_points() -> list[tuple[float, float]]:
    data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    feature = next(f for f in data["features"] if f["attributes"].get("FID") == 820)
    ring = feature["geometry"]["rings"][0]
    points = [local_xy_from_3857(float(x), float(y)) for x, y in ring]
    if len(points) > 1 and math.dist(points[0], points[-1]) < 1e-5:
        points.pop()
    return points


def make_material(name: str, color: tuple[float, float, float, float], roughness=0.82):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def make_mesh(name: str, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    ASSET.objects.link(obj)
    return obj


def box(name, center, size, material):
    cx, cy, cz = center
    sx, sy, sz = (v / 2.0 for v in size)
    verts = [(cx + x * sx, cy + y * sy, cz + z * sz)
             for x, y, z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                             (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),
             (2,3,7,6),(3,0,4,7)]
    return make_mesh(name, verts, faces, material)


def cylinder(name, center, radius, depth, material, segments=16):
    cx, cy, cz = center
    verts = []
    for z in (cz - depth / 2.0, cz + depth / 2.0):
        verts.extend((cx + radius * math.cos(2 * math.pi * i / segments),
                      cy + radius * math.sin(2 * math.pi * i / segments), z)
                     for i in range(segments))
    faces = [tuple(reversed(range(segments))), tuple(range(segments, 2 * segments))]
    faces.extend((i, (i + 1) % segments, (i + 1) % segments + segments, i + segments)
                 for i in range(segments))
    return make_mesh(name, verts, faces, material)


def extruded_polygon(name, points, z0, z1, material):
    n = len(points)
    verts = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    return make_mesh(name, verts, faces, material)


def gable_roof(name, x0, x1, y0, y1, eave_z, peak_z, material):
    """A simple pitched roof with its ridge along Y, matching the long facade."""
    xm = (x0 + x1) / 2.0
    # Lower eave corners plus two ridge points; closed wedge.
    verts = [(x0,y0,eave_z),(x1,y0,eave_z),(x1,y1,eave_z),(x0,y1,eave_z),
             (xm,y0,peak_z),(xm,y1,peak_z)]
    faces = [(0,3,2,1), (0,4,5,3), (4,1,2,5),
             (0,1,4), (3,5,2)]
    return make_mesh(name, verts, faces, material)


def yz_gable_prism(name, x0, x1, y0, y1, base_z, peak_z, material):
    """Pediment with triangular ends in YZ and a shallow projection along X."""
    ym = (y0 + y1) / 2.0
    verts = [(x0,y0,base_z),(x0,y1,base_z),(x0,ym,peak_z),
             (x1,y0,base_z),(x1,y1,base_z),(x1,ym,peak_z)]
    faces = [(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)]
    return make_mesh(name, verts, faces, material)


def west_window(prefix, xwall, y, z, width, height, glass, trim):
    # Window and trim are thin exterior overlays on the west-facing wall.
    x = xwall - 0.065
    box(prefix + "_glass", (x, y, z), (0.09, width, height), glass)
    t = 0.11
    for dy in (-width / 2.0 - t / 2.0, width / 2.0 + t / 2.0):
        box(prefix + "_jamb", (x - 0.025, y + dy, z), (0.14, t, height + 0.18), trim)
    box(prefix + "_lintel", (x - 0.025, y, z + height / 2.0 + 0.09),
        (0.14, width + 0.32, t), trim)
    box(prefix + "_sill", (x - 0.055, y, z - height / 2.0 - 0.12),
        (0.24, width + 0.42, 0.17), trim)


def side_window(prefix, x, ywall, z, width, height, glass, trim, north=True):
    sign = 1.0 if north else -1.0
    y = ywall + sign * 0.065
    box(prefix + "_glass", (x, y, z), (width, 0.09, height), glass)
    t = 0.11
    for dx in (-width / 2.0 - t / 2.0, width / 2.0 + t / 2.0):
        box(prefix + "_jamb", (x + dx, y + sign * 0.025, z), (t, 0.14, height + 0.18), trim)
    box(prefix + "_lintel", (x, y + sign * 0.025, z + height / 2.0 + 0.09),
        (width + 0.32, 0.14, t), trim)
    box(prefix + "_sill", (x, y + sign * 0.055, z - height / 2.0 - 0.12),
        (width + 0.42, 0.24, 0.17), trim)


def dormer(prefix, xwall, y, zbase, width=2.15):
    # Compact white dormer sitting on the west roof slope; third-floor room is
    # visible in chapter images, but its exact construction dimensions are not published.
    depth = 1.55
    xfront = xwall + 2.1
    xback = xfront + depth
    box(prefix + "_body", ((xfront + xback) / 2.0, y, zbase + 0.78),
        (depth, width, 1.56), SIDING)
    yz_gable_prism(prefix + "_gable", xfront - 0.12, xback + 0.12,
                   y - width / 2.0 - 0.12, y + width / 2.0 + 0.12,
                   zbase + 1.48, zbase + 2.25, TRIM)
    # front glass; local west-side plane
    box(prefix + "_glass", (xfront - 0.055, y, zbase + 0.88),
        (0.10, width * 0.58, 1.02), GLASS)
    box(prefix + "_sill", (xfront - 0.12, y, zbase + 0.27),
        (0.22, width * 0.72, 0.13), TRIM)


def world_bounds(objects):
    coords = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            coords.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    return [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]


def render_preview(points):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(PREVIEW)
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("PhiTauPreviewWorld")
    scene.world.color = (0.20, 0.20, 0.20)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    cam_data = bpy.data.cameras.new("PreviewCamera")
    cam = bpy.data.objects.new("PreviewCamera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (min(xs) - 43.0, cy - 22.0, 19.0)
    target = Vector((cx, cy, 4.8))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 48
    scene.camera = cam
    light_data = bpy.data.lights.new("PreviewArea", "AREA")
    light = bpy.data.objects.new("PreviewArea", light_data)
    scene.collection.objects.link(light)
    light.location = (cx - 20.0, cy - 15.0, 27.0)
    light.data.energy = 4500
    light.data.shape = "DISK"
    light.data.size = 18
    light.rotation_euler = (Vector((cx, cy, 4.0)) - light.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.render.render(write_still=True)
    # Straight-on west facade to inspect bay rhythm and entrance.
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 38.0
    cam.location = (min(xs) - 40.0, cy, 6.0)
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(PREVIEW_FRONT)
    bpy.ops.render.render(write_still=True)
    # Top view makes the FID 820 concave/L-shaped wall plan and roof split legible.
    cam.location = (cx, cy, 46.0)
    cam.rotation_euler = (Vector((cx, cy, 0.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = 36.0
    scene.render.filepath = str(PREVIEW_TOP)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.objects.remove(light, do_unlink=True)


def main():
    global ASSET, BRICK, STONE, FOUNDATION, ROOF, GLASS, TRIM, SIDING
    AUDIT.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    # Rebuild as a clean standalone library with the original stable identifiers.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    ASSET = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(ASSET)

    BRICK = make_material("PhiTau_Brown_Red_Brick", (0.37,0.105,0.065,1))
    STONE = make_material("PhiTau_Limestone_Trim", (0.82,0.79,0.70,1))
    FOUNDATION = make_material("PhiTau_Stone_Base", (0.38,0.39,0.37,1))
    ROOF = make_material("PhiTau_Dark_Slate_Roof", (0.10,0.12,0.14,1))
    GLASS = make_material("PhiTau_Glazing", (0.105,0.18,0.22,1), 0.28)
    TRIM = STONE
    SIDING = make_material("PhiTau_Dormer_Light_Siding", (0.86,0.83,0.75,1))
    DOOR = make_material("PhiTau_Entry_Door", (0.14,0.075,0.045,1))

    points = polygon_points()
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    xmid, ymid = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0
    # GIS ring exactly determines the structural wall footprint. Heights below
    # are estimates from chapter exterior imagery and 2002 county assessment.
    extruded_polygon("Foundation", points, 0.0, 0.78, FOUNDATION)
    extruded_polygon("BrickWallShell", points, 0.78, 7.45, BRICK)
    # Three limestone/string courses and corner quoins, based on the current
    # official exterior photograph. Their dimensions are illustrative.
    for z in (0.88, 3.18, 5.58, 7.28):
        box("LimestoneCourseWest", (xmin - 0.055, ymid, z), (0.16, ymax-ymin, 0.16), STONE)
        box("LimestoneCourseEast", (xmax + 0.055, ymid, z), (0.16, ymax-ymin, 0.16), STONE)
    for z in (1.35, 2.18, 3.75, 4.58, 6.05, 6.82):
        for x in (xmin + 0.10, xmax - 0.10):
            for y in (ymin + 0.10, ymax - 0.10):
                box("CornerQuoin", (x, y, z), (0.38, 0.42, 0.36), STONE)

    # Main north-south gable and shorter south-west wing roof; exact roof outline
    # is unverified and these compact roof blocks are deliberately marked estimated.
    wing_y0 = ymin
    wing_y1 = min(ymin + 6.05, ymax)
    wing_x1 = min(xmin + 8.4, xmax)
    gable_roof("MainSlateGable", xmin - 0.30, xmax + 0.30,
               wing_y1 - 0.15, ymax + 0.25, 7.45, 9.15, ROOF)
    gable_roof("SouthWingSlateGable", xmin - 0.30, wing_x1,
               wing_y0 - 0.22, wing_y1 + 0.20, 7.45, 8.45, ROOF)

    # West-facing entrance/portico. Orientation is inferred from 416 N Chauncey
    # street frontage and current facade photos; exact siting is not surveyed.
    entry_y = ymid + 1.0
    porch_front = xmin - 2.45
    porch_back = xmin + 0.22
    porch_halfwidth = 3.55
    yz_gable_prism("LimestonePorticoPediment", porch_front, porch_back,
                   entry_y - porch_halfwidth, entry_y + porch_halfwidth,
                   6.75, 8.65, STONE)
    box("PorticoEntablature", ((porch_front + porch_back)/2, entry_y, 6.78),
        (porch_back - porch_front + 0.25, porch_halfwidth*2 + 0.35, 0.30), STONE)
    for dy in (-2.8, -0.95, 0.95, 2.8):
        cylinder("PorticoColumn", (xmin - 1.45, entry_y + dy, 3.88), 0.20, 5.55, STONE)
        box("ColumnBase", (xmin - 1.45, entry_y + dy, 1.18), (0.62,0.62,0.28), STONE)
        box("ColumnCapital", (xmin - 1.45, entry_y + dy, 6.62), (0.60,0.60,0.25), STONE)
    box("FrontDoor", (xmin - 0.075, entry_y, 2.15), (0.14,1.65,2.75), DOOR)
    box("DoorHeader", (xmin - 0.16, entry_y, 3.57), (0.30,2.0,0.22), STONE)
    for dy in (-0.93, 0.93):
        box("DoorJamb", (xmin - 0.15, entry_y + dy, 2.15), (0.30,0.18,2.95), STONE)
    # Three shallow entry steps project toward Chauncey; their footprints do not
    # alter the GIS structural wall ring.
    for i in range(3):
        box("EntryStep", (xmin - 3.25 + i*0.42, entry_y, 0.18 + i*0.24),
            (0.90, 4.6, 0.36 + i*0.12), FOUNDATION)

    # Repeated window bays from current chapter exterior photos. These are visual
    # cues, not measured opening schedules.
    bay_y = [ymin + 3.2, ymin + 8.1, ymin + 13.0, ymin + 18.2, ymin + 23.3, ymax - 2.3]
    for level, z in enumerate((2.15, 4.65)):
        for index, y in enumerate(bay_y):
            if abs(y - entry_y) < 1.65:
                continue
            west_window(f"WestWindow_L{level+1}_{index+1}", xmin, y, z,
                        1.62, 1.34, GLASS, STONE)
    # North/south return windows, 2 each per full floor.
    for i, x in enumerate((xmin + 2.1, xmin + 5.2, xmin + 8.5, xmax - 2.0)):
        side_window(f"NorthWindow_{i}", x, ymax, 4.6, 1.55, 1.35, GLASS, STONE, True)
        side_window(f"SouthWindow_{i}", x, ymin, 4.6, 1.55, 1.35, GLASS, STONE, False)
        side_window(f"NorthWindowLow_{i}", x, ymax, 2.15, 1.55, 1.35, GLASS, STONE, True)
        side_window(f"SouthWindowLow_{i}", x, ymin, 2.15, 1.55, 1.35, GLASS, STONE, False)

    # Four dormer cues on the west roof plane; the official imagery supports their
    # presence, but exact spacing and size have no plan/elevation source.
    for i, y in enumerate((ymin + 8.7, ymin + 13.3, ymin + 18.0, ymin + 22.5), 1):
        dormer(f"WestDormer_{i}", xmin, y, 8.10, 2.05)

    # Join all architectural pieces into one portable mesh while retaining the
    # expected stable object name and exported collection.
    objs = list(ASSET.objects)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    building = bpy.context.view_layer.objects.active
    building.name = OBJECT_NAME
    building.data.name = "PhiKappaTau_MassingMesh"
    building["asset_id"] = ASSET_ID
    building["source_feature"] = "Purdue BuildingShapes FID 820; historic name Theta Tau; current official chapter address 416 N Chauncey"
    building["footprint_source_crs"] = "EPSG:3857 transformed with project local geographic approximation"
    building["gis_wall_ring_xy_m_json"] = json.dumps([[round(x, 6), round(y, 6)] for x, y in points])
    building["height_status"] = "estimated from current exterior photos; no verified elevations"
    building["placement_status"] = "corrected from prior unsubstantiated placement to FID 820 / 416 N Chauncey"

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    bounds = world_bounds([building])
    render_preview(points)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    record = {
        "asset_id": ASSET_ID,
        "asset_path": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "sha256": digest,
        "scene": SCENE_NAME,
        "collection": COLLECTION_NAME,
        "object": OBJECT_NAME,
        "object_count": len(ASSET.objects),
        "evaluated_bounds_world_m_before_save": bounds,
        "gis_wall_ring_bounds_world_m": [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)],
        "before_bounds_world_m": [[437.351318359375,458.1553649902344],[-101.17964935302734,-87.56614685058594],[0.0,16.0]],
        "after_geometry_edits": ["Replaced unsupported 28-vertex block with wall shell from FID 820 footprint", "Moved campus-world asset from prior bounds to 416 N Chauncey GIS-derived bounds", "Added estimated brick/stone facade cues, portico, repeated windows, pitched roof and dormers"],
        "height_note": "Wall/eave and roof heights are estimates. Current official chapter imagery supports 3-story appearance, stone accents, portico, dormers and pitched slate-like roof; no elevations found.",
        "preview": str(PREVIEW.relative_to(ROOT)).replace("\\", "/"),
        "preview_front": str(PREVIEW_FRONT.relative_to(ROOT)).replace("\\", "/"),
        "preview_top": str(PREVIEW_TOP.relative_to(ROOT)).replace("\\", "/"),
    }
    REPORT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
