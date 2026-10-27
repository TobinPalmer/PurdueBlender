"""Build a source-backed detailed library for Purdue Sigma Phi Epsilon.

The asset remains in campus-world coordinates because it is a massing library
linked directly by the project master. Geometry follows OSM way 301841250;
architectural details are limited to the official chapter descriptions and
the chapter's 2025 exterior photograph.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ASSET_ID = "massing_house_301841250_d63b09a"
WAY_ID = 301841250
ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
AUDIT = ROOT / "audit" / "sigma_phi_epsilon"
SOURCES = AUDIT / "sources"
RENDER = AUDIT / "preview.png"
COLLECTION_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"


def load_osm_ring():
    """Read the preserved Purdue-area OSM snapshot and create local-metre ring."""
    raw = json.loads((ROOT / "purdue_campus_buildings.json").read_text(encoding="utf-8"))
    way = next(e for e in raw["elements"] if e.get("type") == "way" and e.get("id") == WAY_ID)
    nodes = {e["id"]: e for e in raw["elements"] if e.get("type") == "node"}
    coords_geo = [[nodes[n]["lon"], nodes[n]["lat"]] for n in way["nodes"]]
    coords = []
    for lon, lat in coords_geo:
        x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
        y = (lat - 40.4274) * 111040.0
        coords.append([x, y])
    source = {
        "asset_id": ASSET_ID,
        "source": "OpenStreetMap",
        "source_url": f"https://www.openstreetmap.org/way/{WAY_ID}",
        "source_api_url": f"https://api.openstreetmap.org/api/0.6/way/{WAY_ID}/full.json",
        "provider": "OpenStreetMap contributors",
        "way_id": WAY_ID,
        "retrieval_date": "2026-10-26",
        "source_snapshot_timestamp": raw.get("osm3s", {}).get("timestamp_osm_base"),
        "tags": way.get("tags", {}),
        "source_crs": "WGS84 longitude/latitude (EPSG:4326)",
        "project_local_transform": "x=(lon+86.9137)*111412.84*cos(radians(40.4274)); y=(lat-40.4274)*111040.0; z metres; approximate local tangent conversion, not survey-grade",
        "geometry_method": "Original closed OSM way node sequence, preserving all bends and orthogonal recesses; transformed node-by-node without warping",
        "geometry_geojson": {"type": "Polygon", "coordinates": [coords_geo]},
        "geometry_local_m": {"type": "Polygon", "coordinates": [coords]},
        "uncertainty": "OSM outline is a mapped building footprint; wall-vs-roof edge convention and survey accuracy are undocumented. Tag `building=school` is generic and not identity evidence by itself; address 690 plus official SigEp facility page establishes the crosswalk.",
    }
    SOURCES.mkdir(parents=True, exist_ok=True)
    (SOURCES / "osm_way_301841250.json").write_text(json.dumps(source, indent=2), encoding="utf-8")
    area2 = sum(coords[i][0] * coords[i + 1][1] - coords[i + 1][0] * coords[i][1] for i in range(len(coords) - 1))
    area = abs(area2) / 2.0
    bounds = [[min(p[k] for p in coords) for k in (0, 1)], [max(p[k] for p in coords) for k in (0, 1)]]
    return coords, area, bounds, source


def new_material(name, color, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def link_object(obj):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    bpy.data.collections[COLLECTION_NAME].objects.link(obj)
    return obj


def cube(name, loc, dims, material, rotation=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    obj.rotation_euler[2] = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_object(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def mesh_object(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(clean_customdata=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections[COLLECTION_NAME].objects.link(obj)
    if material:
        mesh.materials.append(material)
    return obj


def extruded_footprint(ring, height, material):
    base = [(p[0], p[1], 0.0) for p in ring[:-1]]
    top = [(p[0], p[1], height) for p in ring[:-1]]
    n = len(base)
    verts = base + top
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return mesh_object("House_301841250", verts, faces, material)


def gable_roof(name, xmin, xmax, ymin, ymax, eave, peak, tile_mat):
    """Simple gable volume, ridge oriented along the wing's long north-south axis."""
    inset = 0.18
    xmin += inset
    xmax -= inset
    ymin += inset
    ymax -= inset
    xm = (xmin + xmax) / 2.0
    verts = [
        (xmin, ymin, eave), (xmax, ymin, eave), (xm, ymin, peak),
        (xmin, ymax, eave), (xmax, ymax, eave), (xm, ymax, peak),
    ]
    faces = [(0, 2, 5, 3), (2, 1, 4, 5), (0, 1, 2), (3, 5, 4),
             (0, 3, 4, 1)]
    return mesh_object(name, verts, faces, tile_mat)


def window(name, x, y, z, angle, width, brick, trim, glass):
    # A four-piece frame keeps the dark glazing visible from outside.
    tx, ty = math.cos(angle), math.sin(angle)
    bar = 0.105
    clear_w = max(0.55, width - 2 * bar)
    clear_h = 1.42 - 2 * bar
    for side, sign in (("L", -1), ("R", 1)):
        cube(name + f"_Frame_{side}", (x + tx * sign * (width - bar) / 2, y + ty * sign * (width - bar) / 2, z),
             (bar, 0.16, 1.42), trim, angle)
    for side, sign in (("T", 1), ("B", -1)):
        cube(name + f"_Frame_{side}", (x, y, z + sign * (1.42 - bar) / 2),
             (clear_w + 2 * bar, 0.16, bar), trim, angle)
    cube(name + "_Glass", (x, y, z), (clear_w, 0.045, clear_h), glass, angle)
    cube(name + "_MullionV", (x, y, z), (0.045, 0.055, clear_h), trim, angle)
    cube(name + "_MullionH", (x, y, z), (clear_w, 0.055, 0.045), trim, angle)
    # Brick sill, kept shallow so it reads as trim without altering the source shell.
    cube(name + "_Sill", (x, y, z - 0.78), (width + 0.08, 0.22, 0.13), brick, angle)


def facade_windows(ring, brick, trim, glass):
    # OSM ring is clockwise. For each edge, clockwise exterior normal is its right side.
    levels = [(1, 1.72), (2, 4.78), (3, 7.72)]
    serial = 0
    for i in range(len(ring) - 1):
        ax, ay = ring[i]
        bx, by = ring[i + 1]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        if length < 5.0:
            continue
        angle = math.atan2(dy, dx)
        # Screen out one window near the main west entry; do not pretend to cut openings.
        count = max(1, int(length // 3.05))
        for k in range(count):
            t = (k + 0.5) / count
            px, py = ax + t * dx, ay + t * dy
            nx, ny = dy / length, -dx / length
            for floor, z in levels:
                if abs(px + 330.57) < 0.8 and 394.8 < py < 397.4 and floor == 1:
                    continue
                serial += 1
                window(f"FacadeWindow_{serial:03d}_F{floor}", px + nx * 0.10, py + ny * 0.10,
                       z, angle, min(1.28, length / (count + 1) * 0.48), brick, trim, glass)


def gable_roofs(ring, tile):
    # Roof zones follow the major orthogonal footprint wings; exact framing is unmeasured.
    xs = [p[0] for p in ring[:-1]]
    ys = [p[1] for p in ring[:-1]]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    # Main north block, southwest long wing, and east wing inferred from the mapped outline.
    gable_roof("TileGable_NorthWing", xmin, -315.30, 400.2, ymax + 0.05, 8.75, 12.70, tile)
    gable_roof("TileGable_SouthwestWing", xmin, -322.30, 380.7, 400.2, 8.75, 12.20, tile)
    gable_roof("TileGable_EastWing", -316.35, xmax, 391.4, ymax + 0.05, 8.75, 11.20, tile)
    # Low tiled veranda roofs are specifically reported by the 2023 facility-renovation page.
    cube("TileCanopy_MainVeranda", (-331.25, 396.1, 4.05), (1.15, 5.4, 0.18), tile)
    cube("TileCanopy_NorthVeranda", (-331.25, 405.0, 4.05), (1.15, 5.5, 0.18), tile)


def build():
    ring, area, bounds, osm_record = load_osm_ring()
    # Fresh standalone library scene; no other building assets are loaded or edited.
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        if col.name != "Collection":
            bpy.data.collections.remove(col)
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        scene.collection.children.link(col)
    default = bpy.data.collections.get("Collection")
    if default is not None and default != col:
        if default.name in scene.collection.children:
            scene.collection.children.unlink(default)
        bpy.data.collections.remove(default)

    brick = new_material("SigEp_Red_Brick", (0.39, 0.12, 0.08))
    brick_light = new_material("SigEp_Warm_Brick_Trim", (0.47, 0.22, 0.13))
    stone = new_material("SigEp_Limestone", (0.73, 0.67, 0.56))
    trim = new_material("SigEp_OffWhite_Window_Trim", (0.88, 0.84, 0.72))
    glass = new_material("SigEp_Dark_Glass", (0.085, 0.16, 0.20), 0.24, 0.12)
    roof = new_material("SigEp_Red_Tile_Roof", (0.39, 0.105, 0.075), 0.68)
    door_mat = new_material("SigEp_Dark_Entry", (0.10, 0.075, 0.055))
    metal = new_material("SigEp_Lantern_Metal", (0.16, 0.14, 0.11), 0.35, 0.45)
    ground = new_material("SigEp_Stone_Paving", (0.48, 0.45, 0.39))
    extruded_footprint(ring, 8.75, brick)
    # Light stone belt courses and cornice make the masonry trim explicit but restrained.
    for z in (0.42, 3.25, 6.35, 8.58):
        # Build narrow segments on all source edges to keep the full perimeter exact.
        for i in range(len(ring) - 1):
            ax, ay = ring[i]
            bx, by = ring[i + 1]
            length = math.hypot(bx - ax, by - ay)
            if length < 1.0:
                continue
            angle = math.atan2(by - ay, bx - ax)
            cx, cy = (ax + bx) / 2.0, (ay + by) / 2.0
            cube(f"StoneCourse_{z:.2f}_{i:02d}", (cx, cy, z), (length, 0.08, 0.16), stone, angle)
    facade_windows(ring, brick, trim, glass)
    gable_roofs(ring, roof)

    # The official nighttime 2025 chapter image shows a row of upper-level
    # windows set into the steep west-facing roof slope. Model restrained
    # dormer projections on the long north wing; dimensions are visual estimates.
    west = min(p[0] for p in ring[:-1])
    for idx, yy in enumerate((402.4, 405.4, 408.4, 411.4, 414.4), 1):
        cube(f"RoofDormer_{idx}_Face", (west - 0.36, yy, 9.78), (0.20, 1.55, 1.50), brick)
        cube(f"RoofDormer_{idx}_Glass", (west - 0.49, yy, 9.85), (0.06, 1.02, 0.93), glass)
        cube(f"RoofDormer_{idx}_Sill", (west - 0.53, yy, 9.31), (0.18, 1.17, 0.12), stone)
        # Small triangular gable cap above each dormer front.
        y0, y1 = yy - 0.78, yy + 0.78
        verts = [(west - 0.48, y0, 10.53), (west - 0.48, y1, 10.53),
                 (west - 0.48, yy, 11.18), (west + 0.10, y0, 10.53),
                 (west + 0.10, y1, 10.53), (west + 0.10, yy, 11.18)]
        mesh_object(f"RoofDormer_{idx}_TileGable", verts,
                    [(0, 2, 5, 3), (2, 1, 4, 5), (0, 1, 2), (3, 5, 4)], roof)

    # West-facing principal entry and veranda, with dimensions treated as visual estimates.
    cube("MainEntry_DoubleDoor", (-330.68, 396.1, 1.70), (2.05, 0.16, 2.65), door_mat, math.pi / 2)
    for yy in (394.95, 397.25):
        cube(f"Entry_Sidelight_{yy:.2f}", (-330.72, yy, 1.80), (0.45, 0.10, 1.75), glass, math.pi / 2)
    # Four square masonry piers frame the porch; stone caps and a shallow veranda deck.
    for idx, yy in enumerate((393.6, 395.0, 397.2, 398.6), 1):
        cube(f"Veranda_Pier_{idx}", (-331.63, yy, 2.2), (0.42, 0.42, 3.7), brick_light)
        cube(f"Veranda_Pier_Cap_{idx}", (-331.63, yy, 4.08), (0.65, 0.58, 0.16), stone)
    cube("MainVeranda_Deck", (-331.0, 396.1, 0.42), (1.55, 5.8, 0.24), stone)
    # Front steps and an east-west accessible path, not counted as building footprint.
    for i in range(4):
        cube(f"EntryStep_{i+1}", (-331.85 - 0.36 * i, 396.1, 0.15 + i * 0.12),
             (0.72, 2.9, 0.18), stone)
    cube("WindingWalk_StraightApproach", (-333.10, 396.1, 0.025), (2.5, 1.4, 0.05), ground)

    # Two front-yard pillars with lanterns, called out in the chapter history.
    for idx, yy in enumerate((390.8, 401.4), 1):
        cube(f"EntryGate_Pillar_{idx}", (-334.0, yy, 0.85), (0.60, 0.60, 1.70), brick_light)
        cube(f"EntryGate_Cap_{idx}", (-334.0, yy, 1.75), (0.78, 0.78, 0.16), stone)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.20,
                                             location=(-334.0, yy, 2.15))
        lamp = link_object(bpy.context.object)
        lamp.name = f"EntryGate_Lantern_{idx}"
        lamp.scale = (0.72, 0.72, 1.15)
        lamp.data.materials.append(metal)

    # Discrete wall plaque/lettering: avoid inventing unsupported logo relief.
    cube("ChapterPlaque_Stone", (-330.74, 396.1, 6.65), (0.10, 1.4, 0.62), stone, math.pi / 2)
    txt_curve = bpy.data.curves.new("ChapterLettersCurve", "FONT")
    txt_curve.body = "SPE"
    txt_curve.size = 0.28
    txt_curve.extrude = 0.006
    txt_obj = bpy.data.objects.new("ChapterLetters_SPE", txt_curve)
    bpy.data.collections[COLLECTION_NAME].objects.link(txt_obj)
    txt_obj.location = (-330.83, 395.77, 6.58)
    txt_obj.rotation_euler = (math.pi / 2, 0.0, -math.pi / 2)
    txt_obj.data.materials.append(brick_light)

    # Render setup: west/south view that exposes the long facade and gable profile.
    world = bpy.data.worlds.new("SigmaPhiEpsilonWorld") if bpy.data.worlds.get("SigmaPhiEpsilonWorld") is None else bpy.data.worlds["SigmaPhiEpsilonWorld"]
    scene.world = world
    world.color = (0.46, 0.52, 0.62)
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.46, 0.52, 0.62, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    light_data = bpy.data.lights.new("Key", "AREA")
    light_data.energy = 6500
    light_data.size = 26
    light_obj = bpy.data.objects.new("Preview_Key_Light", light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = (-346, 369, 34)
    light_obj.rotation_euler = (math.radians(28), math.radians(-12), math.radians(-30))
    sun_data = bpy.data.lights.new("Soft_Sun", "SUN")
    sun_data.energy = 1.5
    sun_data.angle = math.radians(22)
    sun_obj = bpy.data.objects.new("Preview_Sun", sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(28), math.radians(-18), math.radians(-34))
    cam_data = bpy.data.cameras.new("PreviewCamera")
    cam = bpy.data.objects.new("PreviewCamera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (-366, 367, 24)
    target = Vector((-321.5, 396.5, 5.4))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 55
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(RENDER)
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    AUDIT.mkdir(parents=True, exist_ok=True)
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    bpy.ops.render.render(write_still=True)

    record = {
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "retrieved_date": "2026-10-26",
        "osm_source": "https://www.openstreetmap.org/way/301841250",
        "chapter_sources": [
            {"url": "https://purdue.sigep.org/meet-our-chapter/about-our-chapter/", "provider": "Sigma Phi Epsilon Indiana Alpha", "source_date": "accessed 2026-10-26", "evidence": "Identifies 690 Waldron as century-old English Colonial; brick trimmed in stone; pillars and approach landscape."},
            {"url": "https://purdue.sigep.org/meet-our-chapter/chapter-facility/", "provider": "Sigma Phi Epsilon Indiana Alpha", "source_date": "accessed 2026-10-26", "evidence": "Confirms 690 Waldron, three occupied levels, red tile roof and two veranda roof areas; recent renovation installed doors/windows."},
            {"url": "https://purdue.sigep.org/wp-content/uploads/sites/207/2025/05/SPE-Web-Headers.png", "provider": "Sigma Phi Epsilon Indiana Alpha", "source_date": "May 2025 (URL path; photo caption calls it 690 Waldron)", "evidence": "Exterior photo shows long red-brick multi-wing facade, tall roof/dormer forms, light-trimmed windows, veranda and central entry."},
            {"url": "https://www.westlafayette.in.gov/DocumentCenter/View/13226/Sidewalk-Closure---Stadium-Avenue---Engineering", "provider": "City of West Lafayette Engineering Department", "source_date": "2024-07-02", "evidence": "City memo places Sigma Phi Epsilon building at 690 Waldron and references its north elevation / Stadium Avenue context."}
        ],
        "geometry": {"source_feature": f"OSM way {WAY_ID}", "source_crs": "EPSG:4326", "method": "node-by-node project local conversion; no fit or warp", "projected_bounds_xy_m": bounds, "polygon_area_m2_planar": round(area, 3), "wall_footprint_uncertainty": "OSM edge may describe roof projection or wall; not surveyed"},
        "model_changes": ["Rebuilt the massing shell from the complete 21-vertex OSM outline, retaining local-project XY campus position.", "Replaced fallback 16 m block with three-level 8.75 m masonry eaves and evidence-informed multi-wing red tile gables (estimated height).", "Added regular window rhythm, stone belt courses, west-facing entrance and two low tile veranda canopies; all facade dimensions are visual estimates from the 2025 official image.", "Added entry piers, lamps, steps and winding approach as isolated details; these are not included in the source footprint."],
        "validation_status": "Builder save and preview render complete; independent fresh-process reopen measurements pending.",
        "uncertainty": ["No surveyed elevation or measured floor-to-floor heights found; 8.75 m eaves and 11.45 m peak are estimates.", "OSM wall/roof outline convention and survey tolerance are unknown.", "The exterior reference is a nighttime wide-angle photo; hidden elevations and exact window/roof dimensions are unverified.", "Overlapping wing roof zones approximate the multi-gable silhouette, not construction framing."]
    }
    (AUDIT / "build_evidence.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({"asset": str(ASSET), "objects": len(col.objects), "bounds": bounds, "area_m2": round(area, 3), "render": str(RENDER)}, indent=2))


build()
