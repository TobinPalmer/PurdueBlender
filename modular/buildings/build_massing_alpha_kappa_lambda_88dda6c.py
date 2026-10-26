from pathlib import Path
import json
import math
import os
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_alpha_kappa_lambda_88dda6c"
ASSET_PATH = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE_PATH = ROOT / "audit" / "alpha_kappa_lambda" / "sources" / "purdue_gis_fid784_2026-10-25.json"
PREVIEW_PATH = ROOT / "audit" / "alpha_kappa_lambda" / "alpha_kappa_lambda_preview.png"
RESULT_PATH = ROOT / "audit" / "alpha_kappa_lambda" / "build_result.json"
SCENE_NAME = "Building_massing_alpha_kappa_lambda_88dda6c"
COLLECTION_NAME = "Asset_massing_alpha_kappa_lambda_88dda6c"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
# Purdue GIS Extrution=12 is a source attribute with undocumented units; it
# is used only as an explicit provisional height value, not a measured height.
HEIGHT_M = 12.0


def xy(lon, lat):
    return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
            (lat - ORIGIN_LAT) * 111040.0)


def polygon_area(points):
    return sum(points[i][0] * points[(i + 1) % len(points)][1]
               - points[(i + 1) % len(points)][0] * points[i][1]
               for i in range(len(points))) / 2.0


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (*color, 1.0)
    return mat


def clear_scene(scene):
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for other in list(bpy.data.scenes):
        if other != scene:
            bpy.data.scenes.remove(other)


def main():
    feature = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))["features"][0]
    attr = feature["attributes"]
    assert attr["FID"] == 784 and attr["BUILDING_N"] == "Alpha Kappa Lambda"
    assert attr["BLDG_ABBR"] == "SOAKL" and attr["ADDRESS"] == "417 Waldron St"
    # One unholed official perimeter ring, in EPSG:4326. The documented campus
    # approximation is applied directly so the simple massing remains world-space.
    raw = feature["geometry"]["rings"][0]
    footprint = [xy(lon, lat) for lon, lat in raw[:-1]]
    if polygon_area(footprint) < 0:
        footprint.reverse()
    n = len(footprint)
    scene = bpy.context.scene
    clear_scene(scene)
    scene.name = SCENE_NAME
    asset = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(asset)
    rig = bpy.data.collections.new("Render_Setup")
    scene.collection.children.link(rig)

    # Neutral, deliberately undecorated shell: no source located supports an
    # exact roof silhouette, facade pattern, or entrance. A simple cap makes
    # the asset usable as massing while leaving those details unasserted.
    verts = [(x, y, z) for z in (0.0, HEIGHT_M) for x, y in footprint]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    faces.extend((i, (i+1) % n, (i+1) % n + n, i+n) for i in range(n))
    mesh = bpy.data.meshes.new("Alpha Kappa Lambda official GIS footprint massing")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Alpha Kappa Lambda", mesh)
    asset.objects.link(obj)
    shell = material("Neutral gray massing; architectural finish unverified", (0.34, 0.39, 0.43))
    mesh.materials.append(shell)
    for poly in mesh.polygons:
        poly.material_index = 0
        poly.use_smooth = False

    cx = sum(x for x, y in footprint) / n
    cy = sum(y for x, y in footprint) / n
    # Render from SW, elevated, showing the footprint outline and overall mass.
    cam_data = bpy.data.cameras.new("AKL massing preview camera")
    cam = bpy.data.objects.new("AKL massing preview camera", cam_data)
    rig.objects.link(cam)
    cam.location = (cx - 44, cy - 46, 33)
    cam.rotation_euler = (Vector((cx, cy, HEIGHT_M * 0.40)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 50
    scene.camera = cam
    light_data = bpy.data.lights.new("AKL soft key", "AREA")
    light_data.energy = 10000
    light_data.shape = "DISK"
    light_data.size = 32
    light = bpy.data.objects.new("AKL soft key", light_data)
    rig.objects.link(light)
    light.location = (cx - 25, cy - 30, 38)
    light.rotation_euler = (Vector((cx, cy, 4)) - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.77, 0.80, 0.83)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.52, 0.55, 0.60, 1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = str(PREVIEW_PATH)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))
    bpy.ops.render.render(write_still=True)

    bounds = [[min(v[i] for v in obj.bound_box), max(v[i] for v in obj.bound_box)] for i in range(3)]
    result = {
        "asset_id": ASSET_ID,
        "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
        "collection": COLLECTION_NAME,
        "scene": SCENE_NAME,
        "object_name": obj.name,
        "object_count_in_asset_collection": len(asset.objects),
        "mesh_vertices": len(mesh.vertices),
        "mesh_faces": len(mesh.polygons),
        "source_feature_id": attr["FID"],
        "source_name": attr["BUILDING_N"],
        "campus_coordinates": "X east / Y north / Z up; simple massing remains in campus coordinates",
        "source_crs": "EPSG:4326 WGS84; transformed by README's local geographic approximation",
        "gis_unique_ring_vertices": n,
        "gis_ring_area_m2_approx_local_projection": abs(polygon_area(footprint)),
        "bounds_world_m": bounds,
        "provisional_height_m": HEIGHT_M,
        "height_status": "uncertain estimate/provisional GIS Extrution=12 interpreted as meters for massing; source field units undocumented; NUM_LEVELS=1 conflicts with prior 11.4m model and does not independently establish vertical form",
        "roof_status": "flat cap is a massing convention; roof form unverified",
        "facade_status": "unverified; no facade openings, material claims, or entrance are modeled",
        "preview": str(PREVIEW_PATH.relative_to(ROOT)).replace("\\", "/"),
        "external_dependencies": [],
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

