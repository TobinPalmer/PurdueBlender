"""Reopen and validate the standalone Brunner Farm Animal Hospital library."""
import bpy
import hashlib
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_ID = "david_and_bonnie_brunner_farm_animal_hospital"
ASSET_PATH = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
EVIDENCE_DIR = os.path.dirname(__file__)
GIS_PATH = os.path.join(EVIDENCE_DIR, "sources", "purdue_gis_feature_408.json")
MANIFEST_PATH = os.path.join(ROOT, "modular", "manifest.json")
OUT = os.path.join(EVIDENCE_DIR, "reopen_validation.json")
ORIGIN = (40.4274, -86.9137)


def area_centroid(points):
    area2 = cx = cy = 0.0
    for (x, y), (u, v) in zip(points, points[1:] + points[:1]):
        cross = x * v - u * y
        area2 += cross
        cx += (x + u) * cross
        cy += (y + v) * cross
    return cx / (3 * area2), cy / (3 * area2)


def main():
    bpy.ops.wm.open_mainfile(filepath=ASSET_PATH)
    scene = bpy.context.scene
    collection_name = "Asset_" + ASSET_ID
    collection = bpy.data.collections.get(collection_name)
    assert collection is not None, f"Missing export collection: {collection_name}"
    shell_name = ASSET_ID + "_GIS_outline_primary_shell"
    shell = bpy.data.objects.get(shell_name)
    assert shell is not None and shell.type == "MESH", f"Missing GIS shell: {shell_name}"

    with open(GIS_PATH, encoding="utf-8") as f:
        gis = json.load(f)
    feature = gis["feature"]
    attributes = feature["attributes"]
    assert attributes["FID"] == 408 and attributes["BLDG_ABBR"] == "BRFM"
    source_ring = feature["geometry"]["rings"][0][:-1]
    lat0, lon0 = ORIGIN
    sx = 111412.84 * math.cos(math.radians(lat0))
    sy = 111040.0
    projected = [((lon - lon0) * sx, (lat - lat0) * sy) for lon, lat in source_ring]
    ox, oy = area_centroid(projected)
    local = [(x - ox, y - oy) for x, y in projected]
    local_area_m2 = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(local, local[1:] + local[:1]))) / 2

    # The shell is generated from the exact source ring, repeated once at the
    # modeled top. Compare its lower ring in source order after reopening.
    half = len(shell.data.vertices) // 2
    shell_points = [(v.co.x, v.co.y) for v in shell.data.vertices[:half]]
    assert len(shell_points) == len(local) == 16, (len(shell_points), len(local))
    errors = [math.dist(a, b) for a, b in zip(shell_points, local)]
    max_error = max(errors)
    assert max_error < 0.002, f"GIS shell mismatch: max vertex error {max_error:.6f} m"

    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest_entry = next(a for a in manifest["assets"] if a["id"] == ASSET_ID)
    assert manifest_entry["file"] == "buildings/" + ASSET_ID + ".blend"
    assert manifest_entry["collection"] == collection_name
    expected_origin = manifest_entry["placement_origin_xy_m"]
    origin_error = math.dist((ox, oy), expected_origin)
    assert origin_error < 0.002, f"Manifest placement-origin delta {origin_error:.6f} m"

    # Confirm evaluated shell bounds, local-coordinate export, and portability.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = shell.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    world_vertices = [evaluated.matrix_world @ v.co for v in evaluated_mesh.vertices]
    bounds = [[min(v[i] for v in world_vertices), max(v[i] for v in world_vertices)] for i in range(3)]
    evaluated.to_mesh_clear()
    external_images = []
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath and not image.packed_file:
            external_images.append(image.filepath)
    assert not external_images, f"Unpacked external images: {external_images}"

    asset_sha = hashlib.sha256(open(ASSET_PATH, "rb").read()).hexdigest()
    object_names = [obj.name for obj in collection.all_objects]
    required_objects = [
        shell_name,
        "BRFM_public_entry_glass",
        "BRFM_entry_clay_tile_hip_roof_estimated",
        "BRFM_service_bay_overhead_door_1",
        "BRFM_service_personnel_door",
        "BRFM_raised_reception_brick_volume",
        "BRFM_reception_narrow_window_7",
        "BRFM_right_return_louver_recess",
    ]
    missing = [name for name in required_objects if name not in object_names]
    assert not missing, f"Missing source-specific geometry: {missing}"

    # Produce post-reopen evidence renders from this exact saved file.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    mesh_points = [obj.matrix_world @ Vector(v) for obj in collection.all_objects if obj.type == "MESH" for v in obj.bound_box]
    mins = [min(v[i] for v in mesh_points) for i in range(3)]
    maxs = [max(v[i] for v in mesh_points) for i in range(3)]
    camera = scene.camera
    assert camera is not None
    camera.location = (maxs[0] + 77, mins[1] - 84, 66)
    overview_target = Vector(((mins[0] + maxs[0]) / 2, (mins[1] + maxs[1]) / 2, 3.2))
    camera.rotation_euler = (overview_target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 42
    scene.render.filepath = os.path.join(EVIDENCE_DIR, "reopened_overview.png")
    bpy.ops.render.render(write_still=True)

    # Use the GIS south-facing long edge for an orthographic-like facade view.
    front = max((i for i in range(len(local)) if math.dist(local[i], local[(i + 1) % len(local)]) > 40),
                key=lambda i: math.dist(local[i], local[(i + 1) % len(local)]))
    a = local[front]
    b = local[(front + 1) % len(local)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    signed = sum(local[i][0] * local[(i + 1) % len(local)][1] - local[(i + 1) % len(local)][0] * local[i][1] for i in range(len(local)))
    nx, ny = math.sin(ang), -math.cos(ang)
    if signed < 0:
        nx, ny = -nx, -ny
    if ny > 0:
        nx, ny = -nx, -ny
    mid = Vector(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 3.6))
    camera.location = (mid.x + nx * 92, mid.y + ny * 92, 24)
    camera.rotation_euler = (mid - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(EVIDENCE_DIR, "reopened_facade.png")
    bpy.ops.render.render(write_still=True)

    report = {
        "date": "2026-10-27",
        "blender_version": bpy.app.version_string,
        "asset": os.path.relpath(ASSET_PATH, ROOT).replace("\\", "/"),
        "asset_sha256": asset_sha,
        "manifest_id": manifest_entry["id"],
        "exported_collection": collection_name,
        "collection_object_count": len(collection.all_objects),
        "gis_feature_id": attributes["FID"],
        "gis_building_code": attributes["BLDG_ABBR"],
        "shell_vertex_count": len(shell_points),
        "source_vertex_max_error_m": max_error,
        "manifest_placement_origin_xy_m": expected_origin,
        "source_computed_origin_xy_m": [ox, oy],
        "origin_error_m": origin_error,
        "local_ground_footprint_area_m2": local_area_m2,
        "published_floor_area_m2": 23900 * 0.09290304,
        "shell_evaluated_local_bounds_m": bounds,
        "unpacked_external_image_dependencies": external_images,
        "required_source_specific_objects_present": required_objects,
        "reopened_successfully": True,
        "renders_from_reopened_asset": [
            os.path.basename(scene.render.filepath).replace("reopened_facade.png", "reopened_overview.png"),
            "reopened_facade.png",
        ],
        "limits": [
            "Wall height 6.2 m and one principal level remain estimates from a building-specific image; GIS height/level fields are zero.",
            "Roof/door dimensions, window schedule and interior arrangement are not supported by measured drawings.",
            "GIS Shape__Area is a Web Mercator attribute; local ground footprint and published floor area measure different quantities and are not compared directly.",
        ],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    evidence_path = os.path.join(EVIDENCE_DIR, ASSET_ID + "_evidence.json")
    with open(evidence_path, encoding="utf-8") as f:
        evidence = json.load(f)
    evidence.setdefault("validation", {}).update({
        "reopen_validation": os.path.relpath(OUT, ROOT).replace("\\", "/"),
        "reopened_successfully": True,
        "asset_sha256": asset_sha,
        "reopened_object_count": len(collection.all_objects),
        "source_shell_max_vertex_error_m": max_error,
        "placement_origin_error_m": origin_error,
        "reopened_overview": os.path.relpath(os.path.join(EVIDENCE_DIR, "reopened_overview.png"), ROOT).replace("\\", "/"),
        "reopened_facade": os.path.relpath(os.path.join(EVIDENCE_DIR, "reopened_facade.png"), ROOT).replace("\\", "/"),
        "unpacked_external_image_dependencies": external_images,
    })
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
