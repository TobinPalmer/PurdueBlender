"""Normalize and rebuild the Benjamin Harrison Hall modular export.

The detailed geometry predates this canonical script and is preserved from
the existing asset. This repeatable builder reopens that seed library, verifies
its footprint against the official Purdue GIS snapshot, records source/height
limits, compares visible facade cues against Purdue's building-specific
exterior photograph, separates preview cameras and light from the exported
collection, then saves the asset and its three review renders. A single
perspective photo does not justify inferring facade dimensions.

Run from the PurdueBlender project root with Blender 4.5+:
  blender --background --python modular/buildings/build_benjamin_harrison_hall.py
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "benjamin_harrison_hall"
COLLECTION_NAME = "Asset_benjamin_harrison_hall"
SCENE_NAME = "Building_benjamin_harrison_hall"
ASSET_PATH = ROOT / "modular" / "buildings" / "benjamin_harrison_hall.blend"
EVIDENCE = ROOT / "audit" / BUILDING_ID
SOURCES = EVIDENCE / "sources"
GIS_PATH = SOURCES / "benjamin_harrison_hall_gis_feature_85_raw.json"
PREVIEW_COLLECTION = "PreviewOnly_benjamin_harrison_hall"
PLACEMENT_ORIGIN_XY_M = (-1110.0, -260.0)
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
METERS_PER_LON_DEG = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
METERS_PER_LAT_DEG = 111040.0
CAMERAS = ["Cam_Hero_Perspective", "Cam_TopDown_Footprint", "Cam_West_Entrance"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def open_seed_if_needed() -> None:
    loaded = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
    if loaded != ASSET_PATH.resolve():
        bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))


def source_contract():
    manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
    entry = next((x for x in manifest["assets"] if x.get("id") == BUILDING_ID), None)
    assert entry is not None, f"Manifest ID missing: {BUILDING_ID}"
    assert entry["file"].replace("\\", "/") == f"buildings/{BUILDING_ID}.blend"
    assert entry["collection"] == COLLECTION_NAME
    assert entry["scene"] == SCENE_NAME
    assert list(entry.get("placement_origin_xy_m", [])) == list(PLACEMENT_ORIGIN_XY_M)
    assert GIS_PATH.is_file(), f"Missing official GIS snapshot: {GIS_PATH}"
    payload = json.loads(GIS_PATH.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    feature = next((f for f in features if int(f.get("attributes", {}).get("FID", -1)) == 85), None)
    assert feature is not None, "Official GIS snapshot lacks feature 85"
    attrs = feature["attributes"]
    assert attrs.get("BLDG_ABBR") == "HARR"
    assert attrs.get("BUILDING_N") == "Benjamin Harrison Residence Hall"
    assert attrs.get("ADDRESS", "").lower() == "107 macarthur drive"
    rings = feature["geometry"].get("rings", [])
    assert len(rings) == 1 and len(rings[0]) >= 5
    for source in ("purdue_oep_harrison_emergency_plan_2026-10-25.html",
                   "purdue_residences_harrison_2026-10-25.html",
                   "purdue_residences_award_photos_2026-10-25.html",
                   "purdue_harrison_hall_exterior_hero.jpg"):
        assert (SOURCES / source).is_file(), f"Missing saved source snapshot: {source}"
    return entry, payload, feature


def local_gis_ring(feature):
    ring = feature["geometry"]["rings"][0]
    points = []
    for lon, lat, *_ in ring[:-1]:
        x = (lon - ORIGIN_LON) * METERS_PER_LON_DEG - PLACEMENT_ORIGIN_XY_M[0]
        y = (lat - ORIGIN_LAT) * METERS_PER_LAT_DEG - PLACEMENT_ORIGIN_XY_M[1]
        points.append((x, y))
    return points


def mesh_base_ring(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        min_z = min(p.z for p in points)
        base = [(round(p.x, 6), round(p.y, 6)) for p in points if abs(p.z - min_z) < 1e-4]
        unique = sorted(set(base))
        return min_z, unique
    finally:
        evaluated.to_mesh_clear()


def symmetric_nearest_error(a, b):
    def directed(p, q):
        return max(min(math.dist(x, y) for y in q) for x in p)
    return max(directed(a, b), directed(b, a))


def source_match(feature, collection):
    base = collection.objects.get("HARR_Ground_Plinth_Base")
    assert base is not None, "The structural perimeter object is missing"
    base_z, model_ring = mesh_base_ring(base)
    gis_ring = local_gis_ring(feature)
    error = symmetric_nearest_error(model_ring, gis_ring)
    assert len(model_ring) == 28, f"Expected 28 unique footprint vertices, got {len(model_ring)}"
    assert len(gis_ring) == 28, f"Expected 28 source vertices, got {len(gis_ring)}"
    assert error < 0.02, f"Footprint source/model error exceeds 2 cm: {error:.4f} m"
    return base_z, model_ring, gis_ring, error


def move_preview_gear(scene, collection):
    preview = bpy.data.collections.get(PREVIEW_COLLECTION)
    if preview is None:
        preview = bpy.data.collections.new(PREVIEW_COLLECTION)
        scene.collection.children.link(preview)
    elif preview.name not in {c.name for c in scene.collection.children}:
        scene.collection.children.link(preview)

    moved = []
    for obj in list(collection.objects):
        if obj.type not in {"CAMERA", "LIGHT"}:
            continue
        for owner_collection in list(obj.users_collection):
            if owner_collection == collection:
                owner_collection.objects.unlink(obj)
        if preview.objects.get(obj.name) is None:
            preview.objects.link(obj)
        moved.append(obj.name)
    return preview, sorted(moved)


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)
    open_seed_if_needed()
    entry, gis, feature = source_contract()
    scene = bpy.context.scene
    assert scene.name == SCENE_NAME, f"Unexpected scene: {scene.name}"
    collection = bpy.data.collections.get(COLLECTION_NAME)
    assert collection is not None, f"Missing exported collection: {COLLECTION_NAME}"
    # These object anchors let reviewers trace the visible cues in the Purdue
    # exterior photo to geometry in the exported asset.
    facade_object_anchors = [
        "HARR_North_Tower_Brick_Core", "HARR_South_Tower_Brick_Core",
        "HARR_NorthTower_North_Frames", "HARR_SouthTower_South_Frames",
        "HARR_Center_Pavilion_Main_Brick", "HARR_West_Solar_Screen_Grid",
        "HARR_Center_West_Entrance_Bay", "HARR_Entrance_Canopy_Slab",
        "HARR_Entrance_Canopy_Fascia"
    ]
    missing_facade_anchors = [name for name in facade_object_anchors if collection.objects.get(name) is None]
    assert not missing_facade_anchors, f"Photo comparison anchors missing: {missing_facade_anchors}"
    facade_photo = SOURCES / "purdue_harrison_hall_exterior_hero.jpg"

    feature_attrs = feature["attributes"]
    base_z, model_ring, gis_ring, footprint_error = source_match(feature, collection)
    all_before = list(collection.objects)
    preview, moved = move_preview_gear(scene, collection)
    remaining = list(collection.objects)
    preview_gear = sorted(o.name for o in preview.objects if o.type in {"CAMERA", "LIGHT"})
    assert all(obj.type not in {"CAMERA", "LIGHT"} for obj in remaining)
    assert set(preview_gear) == set(CAMERAS + ["Sun_Purdue_Daylight"])
    assert len(remaining) == len(all_before) - len(moved)

    scene["building_id"] = BUILDING_ID
    scene["source_feature_id"] = 85
    scene["source_provider"] = "Purdue University official campus map / BuildingShapes ArcGIS FeatureServer"
    scene["builder_script"] = "modular/buildings/build_benjamin_harrison_hall.py"
    scene["height_status"] = "UNVERIFIED: OEP documents 8 stories in each main wing and 2 in the central section; no total height/floor datum survey was found."
    scene["roof_status"] = "UNVERIFIED: roof form and elevation were not specified by the consulted Purdue sources."
    scene["export_collection"] = COLLECTION_NAME

    # Blender 5's legacy EEVEE identifier is unavailable in the available 4.5
    # runtime. Use its supported Eevee Next engine for portable preview renders.
    if scene.render.engine not in {"BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "BLENDER_CYCLES"}:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    for cam_name in CAMERAS:
        camera = bpy.data.objects.get(cam_name)
        assert camera is not None and camera.type == "CAMERA", f"Missing source preview camera: {cam_name}"
        assert preview.objects.get(cam_name) is not None, f"Camera was not moved out of export: {cam_name}"
    key_camera = bpy.data.objects.get("Cam_Hero_Perspective")
    scene.camera = key_camera

    # Repeated idempotent builds otherwise fail if Blender's temporary version
    # backup from a prior interrupted save remains beside the ignored asset.
    bpy.context.preferences.filepaths.save_version = 0
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    render_records = []
    for cam_name in CAMERAS:
        scene.camera = bpy.data.objects[cam_name]
        image_path = EVIDENCE / f"{cam_name.lower()}.png"
        scene.render.filepath = str(image_path)
        bpy.ops.render.render(write_still=True)
        render_records.append({"camera": cam_name, "path": str(image_path.relative_to(ROOT)), "sha256": sha256(image_path)})

    # Restore a useful view camera and save the final library once more.
    scene.camera = key_camera
    scene.render.filepath = "//"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH))

    object_types = {}
    for obj in collection.objects:
        object_types[obj.type] = object_types.get(obj.type, 0) + 1
    file_hash = sha256(ASSET_PATH)
    evidence = {
        "building_id": BUILDING_ID,
        "assigned_owner": "Rossen",
        "asset": "modular/buildings/benjamin_harrison_hall.blend",
        "scene": SCENE_NAME,
        "export_collection": COLLECTION_NAME,
        "builder_script": "modular/buildings/build_benjamin_harrison_hall.py",
        "retrieved": date.today().isoformat(),
        "method": "Preserved the existing detailed local-coordinate model; this dedicated builder verifies its GIS ring, records an official Purdue building-specific exterior photograph, maps visible photo cues to model object groups, and separates preview-only cameras/light from the exported collection. It does not infer dimensions from a perspective image.",
        "gis_source": {
            "provider": "Purdue University official campus map / BuildingShapes ArcGIS FeatureServer",
            "url": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D85&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
            "feature_id": int(feature_attrs["FID"]),
            "building_code": feature_attrs["BLDG_ABBR"],
            "name": feature_attrs["BUILDING_N"],
            "address": feature_attrs.get("ADDRESS"),
            "retrieved": date.today().isoformat(),
            "source_crs": "Purdue ArcGIS service native EPSG:3857; returned snapshot geometry EPSG:4326",
            "snapshot": "audit/benjamin_harrison_hall/sources/benjamin_harrison_hall_gis_feature_85_raw.json",
            "measurement": "28-point exterior ring; transformed using the project's local meters-per-degree approximation, then subtracting manifest placement origin [-1110,-260] m. Symmetric nearest-vertex error against the preserved HARR_Ground_Plinth_Base perimeter is recorded below.",
            "limits": "Official campus map footprint is not a certified survey and does not verify facade or vertical dimensions."
        },
        "architectural_sources": [
            {
                "provider": "Purdue University Office of Emergency Preparedness",
                "url": "https://www.purdue.edu/operations/emergency-preparedness/harr/",
                "page_revision": "2026-03-17",
                "retrieved": date.today().isoformat(),
                "snapshot": "audit/benjamin_harrison_hall/sources/purdue_oep_harrison_emergency_plan_2026-10-25.html",
                "supports": "Three major wings; north and south wings are 8 stories; center section is 2 stories.",
                "uncertainty": "No total height, roof elevation/form, or floor-to-floor measurements."
            },
            {
                "provider": "Purdue University Residences",
                "url": "https://www.housing.purdue.edu/my-housing/options/residence-halls/harrison.html",
                "page_revision": "Page last modified 2025-12-10; checked 2026-10-25",
                "retrieved": date.today().isoformat(),
                "snapshot": "audit/benjamin_harrison_hall/sources/purdue_residences_harrison_2026-10-25.html",
                "supports": "Opened in 1966; two wings connected by central common areas; address 107 MacArthur Drive.",
                "uncertainty": "Residence page is not an elevation or dimensional source."
            },
            {
                "provider": "Purdue University Residences",
                "url": "https://www.housing.purdue.edu/campus-living/get-involved/work-with-us/awards/pastwinners.html",
                "source_date": "February 2024 Harrison Hall award entry; page last modified 2026-04-20",
                "retrieved": date.today().isoformat(),
                "snapshot": "audit/benjamin_harrison_hall/sources/purdue_residences_award_photos_2026-10-25.html",
                "supports": "Official page identifies an image taken outside the Harrison Hall entrance.",
                "uncertainty": "The image is not a measured facade elevation."
            },
            {
                "provider": "Purdue University Residences",
                "url": "https://www.housing.purdue.edu/my-housing/options/residence-halls/harrison.html",
                "source_date": "No publication date for the page hero image; page checked 2026-10-25.",
                "retrieved": date.today().isoformat(),
                "source_image_url": "https://housing.purdue.edu/images/_hero/harrison-exterior.jpg",
                "source_image_caption": "Harrison Hall exterior (official page hero image); capture date and viewpoint orientation not stated.",
                "raw_page_snapshot": "audit/benjamin_harrison_hall/sources/purdue_residences_harrison_2026-10-25.html",
                "raw_image_snapshot": "audit/benjamin_harrison_hall/sources/purdue_harrison_hall_exterior_hero.jpg",
                "supports": "Building-specific exterior image visibly shows red-brown brick on tall wings and lower connector, repeated vertically stacked narrow windows, a light-colored perforated screen across the lower connector, and a glazed entrance adjoining a broad light canopy/overhang.",
                "uncertainty": "Perspective photograph supports visible material and composition cues only; it provides no facade dimensions, screen dimensions, compass orientation, or evidence for unpictured elevations."
            }
        ],
        "facade_photo_comparison": {
            "source_image": "audit/benjamin_harrison_hall/sources/purdue_harrison_hall_exterior_hero.jpg",
            "source_image_sha256": sha256(facade_photo),
            "source_page": "https://www.housing.purdue.edu/my-housing/options/residence-halls/harrison.html",
            "compared_model_view": "audit/benjamin_harrison_hall/cam_west_entrance.png",
            "status": "Photo-backed visual cues; no dimensions extracted from perspective image.",
            "viewpoint_registration": "The Purdue page does not state the photograph's compass direction. Compare motifs only; the mapping to the model's west view is visual, not georeferenced.",
            "observed_cues_and_model_objects": [
                {"photo_cue": "Red-brown brick on the tall wings and lower connector.", "model_objects": ["HARR_North_Tower_Brick_Core", "HARR_South_Tower_Brick_Core", "HARR_Center_Pavilion_Main_Brick"], "status": "Visible material cue supported."},
                {"photo_cue": "Repeated narrow windows stacked vertically on a tall wing.", "model_objects": ["HARR_NorthTower_North_Frames", "HARR_SouthTower_South_Frames"], "status": "Repeated window rhythm is visible; exact spacing remains schematic, and photo-to-wing orientation is not established."},
                {"photo_cue": "Light perforated screen across the lower connector.", "model_objects": ["HARR_West_Solar_Screen_Grid", "HARR_Screen_End_Pier_S", "HARR_Screen_End_Pier_N", "HARR_Screen_Top_Beam"], "status": "Screen presence and contrast supported; exact dimensions/pattern and solar-control function remain unverified."},
                {"photo_cue": "Glazed entrance adjoining a broad, light canopy/overhang.", "model_objects": ["HARR_Center_West_Entrance_Bay", "HARR_Entrance_Canopy_Slab", "HARR_Entrance_Canopy_Fascia"], "status": "Composition supported; exact proportions remain schematic."}
            ],
            "not_established_by_photo": [
                "Exact window width, spacing, and frame profile.",
                "Perforated screen dimensions, precise block pattern, and solar-control function.",
                "Canopy dimensions, roof construction, parapets, and rooftop equipment.",
                "The modeled HARRISON HALL lettering and its location.",
                "Facade treatments on elevations not visible in this photograph."
            ],
            "validated_model_object_anchors": facade_object_anchors,
            "geometry_changes_this_iteration": [],
            "reason_no_facade_geometry_change": "The rendered entrance elevation already expresses the visible photo-supported cues. A perspective photograph cannot establish dimensions or justify moving facade elements, so unmeasured details remain schematic instead of being guessed."
        },
        "placement": {
            "manifest_origin_xy_m": list(PLACEMENT_ORIGIN_XY_M),
            "local_frame": "meters; X east, Y north, Z up",
            "local_geometry_preserved": True
        },
        "geometry_validation": {
            "source_ring_distinct_vertices": len(gis_ring),
            "model_base_ring_distinct_vertices": len(model_ring),
            "source_model_symmetric_nearest_vertex_error_m": footprint_error,
            "model_base_z_local_m": base_z,
            "expected_collection": COLLECTION_NAME,
            "manifest_object_count_before_shared_refresh": entry.get("object_count", len(entry.get("objects", []))),
            "manifest_object_name_count_before_shared_refresh": len(entry.get("objects", [])),
            "manifest_names_still_listed_for_preview_gear": sorted(set(entry.get("objects", [])) & set(preview_gear)),
            "object_count_before_preview_split": len(all_before) + len([o for o in preview.objects if o.type in {"CAMERA", "LIGHT"} and o.name not in moved]),
            "preview_gear_moved": moved,
            "preview_gear_in_sibling_collection": preview_gear,
            "object_count_after_preview_split": len(remaining),
            "export_object_types": object_types,
            "export_contains_camera_or_light": any(o.type in {"CAMERA", "LIGHT"} for o in collection.objects),
            "source_asset_sha256_after_save": file_hash
        },
        "vertical_status": {
            "source_level_attribute": feature_attrs.get("NUM_LEVELS"),
            "height": "Unverified. The official OEP plan supports relative story arrangement only: 8 stories each in north/south wings; 2 stories in the central section.",
            "roof": "Unverified; no roof form or elevation found in the consulted Purdue sources.",
            "floor_to_floor": "Unverified; no authoritative vertical measurements found.",
            "existing_model_major_core_bounds_local_m": {"north": [3.8, 26.6], "south": [3.8, 26.6], "central": [3.8, 7.4]},
            "existing_model_total_bounds_local_m": [-0.06, 30.35],
            "interpretation": "Do not treat modeled z values or GIS NUM_LEVELS as surveyed total building height or precise floor datums."
        },
        "export_validation": {
            "preview_collection": PREVIEW_COLLECTION,
            "preview_collection_excluded_from_export": True,
            "rendered_views": render_records,
            "external_image_dependencies": [],
            "geometry_rebuilt": False,
            "blender_runtime_version": bpy.app.version_string,
            "geometry_note": "Retained existing detailed geometry because its GIS perimeter and three-wing massing agree with official Purdue sources and its entrance view expresses the photo-backed brick, stacked-window, lower-screen, and entrance/canopy cues. No photo-derived dimensions or unsupported facade edits were made."
        },
        "remaining_uncertainty": [
            "No authoritative total building height, roof geometry, or floor-to-floor dimensions were located.",
            "Exact window spacing, west screen dimensions/pattern/function, entrance proportions, and unpictured elevations remain unverified; the photo is perspective, not an elevation.",
            "The official GIS polygon supports identity and horizontal plan geometry but is not a survey."
        ]
    }
    (EVIDENCE / "build_evidence.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (EVIDENCE / "facade_photo_comparison.json").write_text(
        json.dumps(evidence["facade_photo_comparison"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"asset": str(ASSET_PATH), "collection": COLLECTION_NAME,
                      "objects_before": len(all_before), "objects_after": len(remaining),
                      "moved_preview_gear": moved, "source_model_footprint_error_m": footprint_error,
                      "export_types": object_types, "sha256": file_hash}, indent=2), flush=True)


if __name__ == "__main__":
    main()
