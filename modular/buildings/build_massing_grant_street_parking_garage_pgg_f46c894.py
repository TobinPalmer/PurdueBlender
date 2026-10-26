"""Build a detailed, source-backed Grant Street Parking Garage (PGG) library.

The asset remains a direct campus-coordinate library because its manifest entry
is still classified as massing. Source geometry is transformed from Purdue's
Web Mercator campus GIS layer into the project's documented local-meter frame.
Run with Blender 5.0.2+ in background mode, opening the target .blend first.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ASSET_ID = "massing_grant_street_parking_garage_pgg_f46c894"
ASSET_COLLECTION = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"
GIS_OBJECT_ID = 216
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
RETRIEVED = "2026-10-26"

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / ASSET_ID
SOURCES = AUDIT / "sources"
RENDERS = AUDIT / "renders"
GIS_PATH = SOURCES / "purdue_gis_oid216_2026-10-26.json"
OUTPUT = Path(bpy.data.filepath).resolve()
BOX_BATCHES = {}


def campus_xy_from_web_mercator(mx: float, my: float) -> tuple[float, float]:
    """Purdue EPSG:3857 to project approximation, fully recorded in audit."""
    lon = math.degrees(mx / 6378137.0)
    lat = math.degrees(2.0 * math.atan(math.exp(my / 6378137.0)) - math.pi / 2.0)
    x = (lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT))
    y = (lat - ORIGIN_LAT) * 111040.0
    return x, y


def material(name, color, roughness=0.78, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def make_mesh(name, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def box(name, loc, size, mat, collection, angle=0.0):
    """Append transformed box geometry to a material batch for compact exports."""
    batch = BOX_BATCHES.setdefault(mat.name, {"material": mat, "verts": [], "faces": []})
    base = len(batch["verts"])
    c, s = math.cos(angle), math.sin(angle)
    sx, sy, sz = size
    lx, ly, lz = loc
    for x, y, z in ((-sx/2, -sy/2, -sz/2), (sx/2, -sy/2, -sz/2),
                    (sx/2, sy/2, -sz/2), (-sx/2, sy/2, -sz/2),
                    (-sx/2, -sy/2, sz/2), (sx/2, -sy/2, sz/2),
                    (sx/2, sy/2, sz/2), (-sx/2, sy/2, sz/2)):
        batch["verts"].append((lx + c*x - s*y, ly + s*x + c*y, lz + z))
    batch["faces"].extend(tuple(base + i for i in face) for face in (
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)))
    return None


def flush_box_batches(collection):
    for mat_name, batch in BOX_BATCHES.items():
        make_mesh(f"PGG_DetailBatch_{mat_name}", batch["verts"], batch["faces"],
                  batch["material"], collection)
    BOX_BATCHES.clear()


def prism_polygon(name, polygon, z0, z1, mat, collection):
    """Solid, watertight extruded polygon following the official GIS ring."""
    n = len(polygon)
    verts = [(x, y, z0) for x, y in polygon] + [(x, y, z1) for x, y in polygon]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces.extend((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    return make_mesh(name, verts, faces, mat, collection)


def face_normal(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return 0.0, 0.0, 0.0
    # GIS ring is normalized CCW. Its left normal points inside; box geometry
    # uses local Y for bay length, so yaw is tangent minus 90 degrees.
    return -dy / length, dx / length, math.atan2(dy, dx) - math.pi / 2.0


def make_sign_text(name, text, loc, angle, mat, collection, size=0.8):
    curve = bpy.data.curves.new(name + "Text", "FONT")
    curve.body = text
    curve.size = size
    curve.extrude = 0.006
    obj = bpy.data.objects.new(name, curve)
    obj.location = loc
    obj.rotation_euler = (math.pi / 2.0, 0.0, angle)
    collection.objects.link(obj)
    curve.materials.append(mat)
    return obj


def setup_render(scene, bounds, collection):
    for object_name in ("PGG_EvidenceCamera", "PGG_Key", "PGG_Fill"):
        existing = bpy.data.objects.get(object_name)
        if existing is not None:
            bpy.data.objects.remove(existing, do_unlink=True)
    center_x = (bounds[0] + bounds[1]) / 2.0
    center_y = (bounds[2] + bounds[3]) / 2.0
    width = bounds[1] - bounds[0]
    depth = bounds[3] - bounds[2]
    camera_data = bpy.data.cameras.new("PGG_EvidenceCamera")
    camera = bpy.data.objects.new("PGG_EvidenceCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (center_x - width * 1.35, center_y - depth * 1.25, 88.0)
    target = Vector((center_x, center_y, 6.5))
    direction = target - Vector(camera.location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(width * 1.95, depth * 1.85)
    scene.camera = camera

    for name, loc, power, size in [
        ("PGG_Key", (center_x - 45, center_y - 25, 75), 36000, 48),
        ("PGG_Fill", (center_x + 45, center_y + 15, 50), 18000, 42),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        direction = Vector((center_x, center_y, 7)) - Vector(loc)
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(obj)

    world = bpy.data.worlds.new("PGG_EvidenceWorld") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.color = (0.24, 0.27, 0.31)
    engine_items = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
    engine_ids = {item.identifier for item in engine_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engine_ids else "BLENDER_EEVEE"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = -1.15
    if "AgX - Medium High Contrast" in {item.name for item in scene.view_settings.bl_rna.properties["look"].enum_items}:
        scene.view_settings.look = "AgX - Medium High Contrast"


def main():
    if not OUTPUT.exists():
        raise FileNotFoundError(f"Open the assigned asset before running: {OUTPUT}")
    if not GIS_PATH.exists():
        raise FileNotFoundError(GIS_PATH)
    feature_set = json.loads(GIS_PATH.read_text(encoding="utf-8-sig"))
    features = feature_set.get("features", [])
    feature = next((f for f in features if f["attributes"].get("OBJECTID") == GIS_OBJECT_ID), None)
    if feature is None:
        raise ValueError(f"Could not find Purdue GIS CampusBuilding OBJECTID {GIS_OBJECT_ID}")

    ring = feature["geometry"]["rings"][0]
    polygon = [campus_xy_from_web_mercator(float(x), float(y)) for x, y in ring[:-1]]
    area2 = sum(polygon[i][0] * polygon[(i + 1) % len(polygon)][1] -
                polygon[(i + 1) % len(polygon)][0] * polygon[i][1]
                for i in range(len(polygon)))
    if area2 < 0:
        polygon.reverse()
    bounds = (min(x for x, _ in polygon), max(x for x, _ in polygon),
              min(y for _, y in polygon), max(y for _, y in polygon))
    xmin, xmax, ymin, ymax = bounds
    width, depth = xmax - xmin, ymax - ymin
    cx, cy = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0

    scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
    scene.name = SCENE_NAME
    asset = bpy.data.collections.get(ASSET_COLLECTION)
    if asset is None:
        asset = bpy.data.collections.new(ASSET_COLLECTION)
        scene.collection.children.link(asset)
    elif asset.name not in {c.name for c in scene.collection.children}:
        scene.collection.children.link(asset)
    # Remove only objects in the assigned asset collection; evidence cameras,
    # lights, and every other scene/library object are left untouched.
    for obj in list(asset.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    brick = material("PGG | warm red-brown brick", (0.34, 0.105, 0.068), 0.88)
    brick_shadow = material("PGG | recessed brick joints", (0.20, 0.066, 0.046), 0.92)
    concrete = material("PGG | warm precast concrete", (0.71, 0.69, 0.63), 0.84)
    cap = material("PGG | pale limestone caps", (0.83, 0.80, 0.72), 0.78)
    asphalt = material("PGG | charcoal parking deck", (0.16, 0.175, 0.18), 0.95)
    glass = material("PGG | smoked stair glazing", (0.055, 0.105, 0.125), 0.28, 0.16)
    metal = material("PGG | dark steel railings", (0.095, 0.11, 0.12), 0.42, 0.62)
    paint = material("PGG | white parking markings", (0.91, 0.89, 0.80), 0.6)
    text_mat = material("PGG | entrance lettering", (0.10, 0.075, 0.055), 0.58)

    # Source footprint slab. Each level follows the slightly irregular Purdue
    # building outline rather than rescaling the older massing box.
    deck_z = [0.0, 3.18, 6.36, 9.54, 12.72, 15.90]
    prism_polygon("PGG_Footprint_Foundation", polygon, -0.16, 0.0, concrete, asset)
    for idx, z in enumerate(deck_z):
        if idx == 0:
            continue
        prism_polygon(f"PGG_Deck_{idx+1:02d}", polygon, z - 0.20, z,
                      asphalt if idx == len(deck_z) - 1 else concrete, asset)

    # Repetitive brick piers, concrete spandrels and open rail bays are based
    # on the multi-level open facade visible in the engineering firm's photo.
    segments = []
    for i, p0 in enumerate(polygon):
        p1 = polygon[(i + 1) % len(polygon)]
        length = math.dist(p0, p1)
        if length < 5.0:
            continue
        ux, uy, angle = face_normal(p0, p1)
        n_bays = max(1, round(length / 7.3))
        pts = [(p0[0] + (p1[0] - p0[0]) * j / n_bays,
                p0[1] + (p1[1] - p0[1]) * j / n_bays) for j in range(n_bays + 1)]
        for j, (px, py) in enumerate(pts[:-1]):
            qx, qy = pts[j + 1]
            midx, midy = (px + qx) / 2, (py + qy) / 2
            bay_length = math.dist((px, py), (qx, qy))
            box(f"PGG_Brick_Pier_{i:02d}_{j:02d}",
                (px + ux * 0.32, py + uy * 0.32, 8.0),
                (0.65, 0.72, 16.0), brick, asset, angle)
            segments.append((i, j, midx + ux * 0.34, midy + uy * 0.34,
                             bay_length, angle, ux, uy))

    for idx, z in enumerate(deck_z[:-1]):
        level_height = deck_z[idx + 1] - z
        for edge_id, bay_id, mx, my, bay_length, angle, ux, uy in segments:
            span = max(0.8, bay_length - 0.82)
            # Pale solid perimeter curb/spandrel at the lower edge of every
            # open parking bay, with two narrow dark guard rails above it.
            box(f"PGG_Concrete_Spandrel_{idx:02d}_{edge_id:02d}_{bay_id:02d}",
                (mx, my, z + 0.48), (0.28, span, 0.56), concrete, asset, angle)
            for rail_n, rail_z in enumerate((z + 1.15, z + 1.43)):
                box(f"PGG_Guardrail_{idx:02d}_{edge_id:02d}_{bay_id:02d}_{rail_n}",
                    (mx - ux * 0.19, my - uy * 0.19, rail_z),
                    (0.10, span, 0.075), metal, asset, angle)
            # A light cap line above the dark openings gives the characteristic
            # pale horizontal band seen on the real garage elevations.
            box(f"PGG_Fascia_Cap_{idx:02d}_{edge_id:02d}_{bay_id:02d}",
                (mx, my, z + level_height - 0.12),
                (0.42, span, 0.19), cap, asset, angle)

    # Full-height brick stair/elevator cores at two opposite corners. The
    # central glazed strips and pale floor belt courses are visible on the photo.
    core_w, core_d = 8.4, 11.8
    core_specs = [
        (xmin + core_w / 2 + 1.4, ymin + core_d / 2 + 1.5, "Southwest"),
        (xmax - core_w / 2 - 1.4, ymax - core_d / 2 - 1.5, "Northeast"),
    ]
    for ox, oy, suffix in core_specs:
        box(f"PGG_{suffix}_Core_BrickMass", (ox, oy, 8.0),
            (core_w, core_d, 16.0), brick, asset)
        for j, z in enumerate(deck_z[:-1]):
            box(f"PGG_{suffix}_Core_Belt_{j:02d}", (ox, oy, z + 0.10),
                (core_w + 0.20, core_d + 0.20, 0.22), cap, asset)
        # Tall dark glazing on the outward-facing pair of core walls. Mullions
        # retain a sturdy masonry frame and let the glass register at campus scale.
        glazing_width = 4.0
        for side, yy in (("south", oy - core_d / 2 - 0.04), ("north", oy + core_d / 2 + 0.04)):
            box(f"PGG_{suffix}_{side}_Glazing", (ox, yy, 8.1),
                (glazing_width, 0.12, 14.6), glass, asset)
            for n in range(5):
                xx = ox - glazing_width / 2 + n * glazing_width / 4
                box(f"PGG_{suffix}_{side}_Mullion_{n}", (xx, yy - 0.08, 8.1),
                    (0.10, 0.14, 14.7), metal, asset)

    # Ground-level parking-entry office/vestibule and vehicle clearance bar.
    entry_x, entry_y = cx, ymin + 0.9
    box("PGG_EntryVestibule_Brick", (entry_x, entry_y, 1.35),
        (12.0, 2.0, 2.7), brick, asset)
    box("PGG_EntryVestibule_Glazing", (entry_x, entry_y - 1.04, 1.30),
        (6.7, 0.10, 2.2), glass, asset)
    # Entrance lettering is an inferred orientation from the supplied exterior
    # photo; the sign exists in that photo but image orientation is not GIS-backed.
    make_sign_text("PGG_Entrance_ENTER", "ENTER", (entry_x - 1.5, entry_y - 1.17, 2.0),
                   0.0, text_mat, asset, 0.72)

    # White parking-space lines on the source-supported flat top deck. These
    # represent painted circulation marks, not surveyed stall coordinates.
    rooftop = deck_z[-1]
    for row, yy in enumerate([ymin + 22.0 + i * 5.2 for i in range(12)]):
        if yy > ymax - 14:
            continue
        for stall in range(14):
            xx = xmin + 4.5 + stall * 4.8
            if xx > xmax - 4.5:
                continue
            box(f"PGG_RoofStripe_{row:02d}_{stall:02d}",
                (xx, yy, rooftop + 0.012), (0.055, 4.25, 0.018), paint, asset)
    # Roof parapet rails are represented at a low architectural curb height.
    for i, p0 in enumerate(polygon):
        p1 = polygon[(i + 1) % len(polygon)]
        length = math.dist(p0, p1)
        if length < 5.0:
            continue
        ux, uy, angle = face_normal(p0, p1)
        box(f"PGG_RoofParapet_{i:02d}",
            ((p0[0] + p1[0]) / 2 + ux * 0.25,
             (p0[1] + p1[1]) / 2 + uy * 0.25, rooftop + 0.50),
            (0.38, length, 0.85), concrete, asset, angle)

    flush_box_batches(asset)
    # The source massing file carried four unused brick image datablocks. The
    # replacement has node materials with no image inputs, so discard those
    # orphan external references to keep this library self-contained.
    for image in list(bpy.data.images):
        if image.source == "FILE" and image.users == 0:
            bpy.data.images.remove(image)
    for old_material in list(bpy.data.materials):
        if old_material.users == 0:
            bpy.data.materials.remove(old_material)
    scene.render.filepath = str(RENDERS / "pgg_three_quarter.png")
    setup_render(scene, bounds, asset)
    camera = scene.camera
    # Keep the model's geometry only in its stable exported collection.
    bpy.context.view_layer.objects.active = None
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    bpy.ops.render.render(write_still=True)
    # Independent evaluator views: source-footprint roof plan and entry-side elevation.
    camera.location = (cx, cy, 110.0)
    camera.rotation_euler = (0.0, 0.0, 0.0)
    camera.data.ortho_scale = max(width, depth) * 1.22
    scene.render.filepath = str(RENDERS / "pgg_topdown.png")
    bpy.ops.render.render(write_still=True)
    camera.location = (cx, ymin - 96.0, 8.2)
    direction = Vector((cx, ymin + 3.0, 8.0)) - Vector(camera.location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.ortho_scale = max(width * 1.52, 118.0)
    scene.render.filepath = str(RENDERS / "pgg_south_facade.png")
    bpy.ops.render.render(write_still=True)
    # Restore the saved camera/render state that opens to the isometric evidence view.
    camera.location = (cx - width * 1.35, cy - depth * 1.25, 88.0)
    target = Vector((cx, cy, 6.5))
    camera.rotation_euler = (target - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.ortho_scale = max(width * 1.95, depth * 1.85)
    scene.render.filepath = str(RENDERS / "pgg_three_quarter.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))

    # Structured, machine-readable dimensions and provenance for the audit.
    attrs = feature["attributes"]
    record = {
        "building_id": ASSET_ID,
        "asset_path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "collection": ASSET_COLLECTION,
        "scene": SCENE_NAME,
        "retrieval_date": RETRIEVED,
        "sources": [
            {
                "source": "Purdue CampusBuilding FeatureServer, layer 0, OBJECTID 216",
                "provider": "Purdue University Library GIS / Purdue Maps",
                "url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/FeatureServer/0/query?where=OBJECTID%3D216&outFields=*&returnGeometry=true&f=json",
                "feature_id": "OBJECTID=216; ABBR=PGG; buildingidlong=95",
                "retrieval_date": RETRIEVED,
                "source_date": "Campus GIS service queried 2026-10-26; feature metadata reports current garage constructed 1994-1995",
                "source_crs": "EPSG:3857 (Esri WKID 102100), meters",
                "measurement_method": "Footprint polygon vertices inverse-Mercator projected to longitude/latitude and transformed using the project-documented local approximation (origin 40.4274,-86.9137).",
                "uncertainty": "Purdue project approximation is not a surveyed CRS; polygon is GIS building footprint, not a wall survey."
            },
            {
                "source": "Purdue Road School 2026 Parking Tips and Options PDF",
                "provider": "Purdue University Road School",
                "url": "https://roadschool.purdue.edu/Attendees/2026_Road_School_Parking_Tips_Options.pdf",
                "feature_id": "Grant Street Garage at 120 N. Grant St.",
                "retrieval_date": RETRIEVED,
                "source_date": "2026 event guidance",
                "source_crs": "Not applicable",
                "measurement_method": "Published address and vehicle entry clearance (7 ft 6 in); does not establish building height.",
                "uncertainty": "Visitor guidance can be transient; clearance is not a full-floor height measurement."
            },
            {
                "source": "Purdue Grant Street Parking Garage project photograph",
                "provider": "ARSEE Engineers",
                "url": "https://www.arsee-engineers.com/images/Parking/Purdue%20Grant%20Street%20Parking%20Garage.jpg",
                "feature_id": "Caption/page labels image Purdue Grant Street Parking Garage",
                "retrieval_date": RETRIEVED,
                "source_date": "Image date not stated",
                "source_crs": "Not georeferenced; oblique aerial photograph",
                "measurement_method": "Visual comparison of brick stair/elevator cores, pale concrete floor bands, open-air deck bays, flat roof parking and entrance canopy/sign.",
                "uncertainty": "Photo orientation and capture date are unstated; it supports architectural pattern but not precise facade dimensions or present condition."
            },
            {
                "source": "Purdue University West Lafayette Campus Map 2025",
                "provider": "Purdue University",
                "url": "https://www.purdue.edu/campus-map/graphics/campusmap.pdf",
                "feature_id": "PGG, campus-map grid H7",
                "retrieval_date": RETRIEVED,
                "source_date": "2025 map",
                "source_crs": "Schematic campus map, not a measurement CRS",
                "measurement_method": "Identity and relative campus placement cross-check against Grant Street / Purdue Memorial Union context.",
                "uncertainty": "Map is schematic and not suitable for plan dimensions."
            }
        ],
        "source_attributes": {
            "official_name": attrs.get("Name"),
            "address": attrs.get("ADDRESS"),
            "constructed": "1994-1995",
            "parking_spaces": "1,450 per Purdue GIS historical description; current capacity not independently reverified",
            "recorded_area_sqft": attrs.get("squarefootage"),
            "shape_area_m2_epsg3857": attrs.get("Shape__Area")
        },
        "dimensions_m": {"x": width, "y": depth, "z": 16.985},
        "campus_bounds_m": {"xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax},
        "geometry_changes": [
            "Replaced one fallback massing mesh with a GIS-footprint-based multi-deck garage.",
            "Added six deck planes (ground plus five upper planes at 3.18 m increments) with open guard bays, brick structural piers, two brick/glazed circulation cores, an inferred entry vestibule, roof parapet and parking stripes."
        ],
        "vertical_status": "Unverified. The saved mesh bounds span z=-0.16 m to z=16.825 m (16.985 m total); five 3.18 m story intervals and six deck planes are visual/architectural estimates, not surveyed elevations.",
        "orientation_status": "Plan orientation derives from GIS polygon; architectural entrance direction is inferred from an undated oblique photo.",
        "renders": ["renders/pgg_three_quarter.png", "renders/pgg_topdown.png", "renders/pgg_south_facade.png"]
    }
    (AUDIT / "evidence_record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({"asset": str(OUTPUT), "bounds": record["campus_bounds_m"],
                      "dimensions_m": record["dimensions_m"], "object_count": len(asset.objects),
                      "renders": record["renders"]}, indent=2))


if __name__ == "__main__":
    main()
