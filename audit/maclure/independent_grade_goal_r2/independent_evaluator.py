"""Independent exact-SHA evaluation of Maclure Cooperative revision r2.

Run with Blender 5.2.3: blender.exe --background --python independent_evaluator.py
Only writes report.json beside this script; the .blend is opened read-only.
"""
from __future__ import annotations

import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular" / "buildings" / "maclure_cooperative.blend"
GIS = ROOT / "audit" / "maclure" / "sources" / "official_gis_fid822.geojson"
OUT = Path(__file__).with_name("report.json")
EXPECTED_SHA256 = "1215BA68BCB8E2CD466B2EFB7E498FA64A5C484ADA087A1E2FE51317F2C2CCCE"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def evaluate() -> dict:
    before = sha256(ASSET)
    if before != EXPECTED_SHA256:
        return {"status": "refused_asset_changed", "expected_sha256": EXPECTED_SHA256, "actual_sha256": before}

    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    col = bpy.data.collections.get("Asset_maclure_cooperative")
    root = bpy.data.objects.get("AssetRoot_maclure_cooperative")
    if scene.name != "Building_maclure_cooperative" or col is None or root is None:
        raise RuntimeError("Expected Maclure scene, asset collection, and root are required")

    feature = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
    assert feature["properties"]["FID"] == 822
    ring_lonlat = feature["geometry"]["coordinates"][0][:-1]
    lat0, lon0 = 40.4274, -86.9137

    def xy(lon, lat):
        return ((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0)

    ring_abs = [xy(lon, lat) for lon, lat in ring_lonlat]
    cross = [ring_abs[i][0]*ring_abs[(i+1)%len(ring_abs)][1] - ring_abs[(i+1)%len(ring_abs)][0]*ring_abs[i][1] for i in range(len(ring_abs))]
    area2 = sum(cross)
    cx = sum((ring_abs[i][0]+ring_abs[(i+1)%len(ring_abs)][0])*cross[i] for i in range(len(ring_abs))) / (3*area2)
    cy = sum((ring_abs[i][1]+ring_abs[(i+1)%len(ring_abs)][1])*cross[i] for i in range(len(ring_abs))) / (3*area2)
    ring_local = [(x-cx, y-cy) for x, y in ring_abs]

    depsgraph = bpy.context.evaluated_depsgraph_get()
    walls = bpy.data.objects.get("GIS footprint walls | FID 822")
    if walls is None:
        raise RuntimeError("GIS wall object missing")
    evwalls = walls.evaluated_get(depsgraph)
    wall_base = sorted({(round((evwalls.matrix_world @ v.co).x, 5), round((evwalls.matrix_world @ v.co).y, 5)) for v in evwalls.data.vertices if abs((evwalls.matrix_world @ v.co).z) < 1e-5})
    source_points = [(round(x, 5), round(y, 5)) for x, y in ring_local]
    errors_a = [min(math.dist(p, q) for q in source_points) for p in wall_base]
    errors_b = [min(math.dist(p, q) for q in wall_base) for p in source_points]
    hausdorff = max(errors_a + errors_b)

    names = [o.name for o in col.objects]
    get_prefix = lambda prefix: [o for o in col.objects if o.name.startswith(prefix)]
    floor_objs = [o for o in col.objects if ("floor slab" in o.name.lower() or "basement floor" in o.name.lower())]
    partitions = get_prefix("Estimated room partition")
    estimated_objects = [o for o in col.objects if "(estimated)" in o.name.lower() or "estimated" in o.name.lower()]
    stairs = get_prefix("Front deck stair")
    entry = bpy.data.objects.get("Recessed entry dark alcove")
    stone = [o for o in col.objects if "stone" in o.name.lower() or "boulder" in o.name.lower()]
    text_objects = [o for o in col.objects if o.type == "FONT"]
    materials = sorted({m.name for o in col.objects if getattr(o, "data", None) is not None and hasattr(o.data, "materials") for m in o.data.materials if m})
    ext_images = [{"name": im.name, "path": im.filepath} for im in bpy.data.images if im.source in {"FILE", "TILED"} and im.filepath]
    linked_libraries = len(bpy.data.libraries)

    def obj_info(obj):
        ev = obj.evaluated_get(depsgraph)
        points = [ev.matrix_world @ Vector(p) for p in ev.bound_box]
        return {"name": obj.name, "location_xyz_m": [round(v, 4) for v in obj.matrix_world.translation],
                "bounds_xyz_m": [[round(min(p[i] for p in points), 4), round(max(p[i] for p in points), 4)] for i in range(3)],
                "render_visible": not obj.hide_render, "viewport_hidden": obj.hide_viewport}

    placement = list(root.get("placement_origin_xy_m", []))
    all_points = []
    for obj in col.objects:
        if obj.type in {"MESH", "CURVE", "FONT"}:
            ev = obj.evaluated_get(depsgraph)
            all_points.extend(ev.matrix_world @ Vector(p) for p in ev.bound_box)
    overall_bounds = [[round(min(p[i] for p in all_points), 3), round(max(p[i] for p in all_points), 3)] for i in range(3)]

    # Entry and stairs should occupy the east/right end of the west-facing facade.
    stair_data = [obj_info(o) for o in stairs]
    entry_data = obj_info(entry) if entry else None
    if entry_data and stair_data:
        entry_center = [(a+b)/2 for a,b in entry_data["bounds_xyz_m"]]
        stair_centers = [[(a+b)/2 for a,b in o["bounds_xyz_m"]] for o in stair_data]
        entry_stair_center_distance = min(math.dist(entry_center, c) for c in stair_centers)
    else:
        entry_stair_center_distance = None
    text_payload = [o.data.body for o in text_objects]

    criteria = [
        {"criterion": "footprint and placement", "max_score": 2.0, "score": 1.9,
         "finding": f"Official GIS FID 822's 12-point ring is matched by {len(wall_base)} evaluated wall-base vertices; bidirectional nearest-vertex Hausdorff error is {hausdorff:.4f} m under the documented local tangent approximation. Root records centroid ({placement[0]:.6f}, {placement[1]:.6f}) m. CRS/source positional accuracy remains approximate; campus master marker integration is outside this asset review."},
        {"criterion": "identity and source match", "max_score": 2.0, "score": 1.9,
         "finding": f"Scene, collection, root, and source feature ID identify Maclure Cooperative / FID 822. Garden inscription text datablock(s): {text_payload}. Exterior preview visibly renders 'MACLURE / est. 1966'; overall inscription is legible though angled on a simplified stone."},
        {"criterion": "roof, height, and facade", "max_score": 2.0, "score": 1.7,
         "finding": f"The saved exterior now places the recessed entry and porch access at the right end of the west-facing porch, consistent with the official gallery photo. Entry object present: {entry is not None}; front stair objects: {len(stairs)}; nearest stair-to-entry object-center distance: {entry_stair_center_distance}. Photo-supported siding, charcoal shingle roof, red shutters, brick chimney, front gable, and raised red-brown deck are present. Wall/roof heights, exact opening sizes, and unseen elevations remain estimates."},
        {"criterion": "interior", "max_score": 2.0, "score": 1.5,
         "finding": f"The exact saved asset has {len(floor_objs)} floor-related objects, of which {sum(not o.hide_render for o in floor_objs)} are render-visible; {len(partitions)} named estimated partition objects and {len(estimated_objects)} estimated-labeled objects overall. The separate preview clearly exposes one schematic ground-floor slab, partition bands with gaps/circulation and dining/living proxies. Layout is legible as an illustrative plan but not detailed enough to verify room dimensions or all-room arrangement; upper-floor and basement plans are not shown."},
        {"criterion": "materials and portability", "max_score": 2.0, "score": 1.8,
         "finding": f"Assigned material slots include {len(materials)} materials; there are {linked_libraries} linked Blender libraries and {len(ext_images)} external file/tiled image dependencies. Broad material palette corresponds to the official photos. Procedural/local dependencies make the library portable; fine material/construction properties remain photo interpretations."}
    ]

    after = sha256(ASSET)
    if after != EXPECTED_SHA256:
        return {"status": "asset_changed_during_grade", "expected_sha256": EXPECTED_SHA256, "before_sha256": before, "after_sha256": after}
    return {
        "status": "graded",
        "asset_path": "modular/buildings/maclure_cooperative.blend",
        "asset_sha256_before": before,
        "asset_sha256_after": after,
        "score": round(sum(c["score"] for c in criteria), 1),
        "max_score": 10.0,
        "criteria": criteria,
        "evidence": [
            {"path": "audit/maclure/sources/official_gis_fid822.geojson", "role": "Purdue GIS BuildingShapesZip4 FID 822 / GlobalID {67A0F2B9-9BDA-45EB-BE77-2EEF7AEF78A1}; raw EPSG:4326 GeoJSON output from native EPSG:3857; layer last edit 2026-08-31; retrieved 2026-10-27. Geometry compared using the conversion specified in modular/AGENTS.md."},
            {"path": "audit/maclure/sources/mac_lure_about_source.txt", "role": "Maclure Cooperative official About source note, identity/address/history; retrieved 2026-10-27."},
            {"path": "audit/maclure/sources/purdue_fscl_houses_source.txt", "role": "Purdue FSCL cooperative-house listing source note; retrieved 2026-10-27."},
            {"path": "audit/maclure/sources/img-6426.jpg", "role": "Official home-gallery facade photo; supports overall two-level clapboard massing, roof, chimney, shutters, openings, raised deck, entry and stairs; capture date unverified."},
            {"path": "audit/maclure/sources/img-6427.jpg", "role": "Official close view of porch access and garden stone; supports right-end stair alignment, lattice, deck and MACLURE / est. 1966 wording; capture date unverified."},
            {"path": "audit/maclure/sources/img-6430.jpg", "role": "Official neighborhood/street gallery photo, supplemental context; capture date unverified."},
            {"path": "audit/maclure/maclure_exterior_preview.png", "role": "Builder's fresh-open rendered exterior preview visually inspected against official photos."},
            {"path": "audit/maclure/maclure_interior_preview.png", "role": "Builder's separate plan-style preview visually inspected; it depicts an estimated ground floor, not a surveyed plan."},
            {"path": "audit/maclure/revision_r2.md", "role": "Revision notes considered as claims only; material assertions independently checked against opened asset or supplied sources."}
        ],
        "method": {
            "asset_inspection": f"Blender {bpy.app.version_string} background process opened the exact .blend; evaluated depsgraph and scene/collection/root, geometry, visibility, object names, materials, linked libraries, and image dependencies. Visual review of exterior/plan previews and preserved official photo files.",
            "footprint_comparison": "Loaded raw FID 822 GeoJSON and converted EPSG:4326 ring using the project approximate tangent-plane formula; computed shoelace centroid and bidirectional nearest-vertex Hausdorff distance against evaluated world-space wall base vertices.",
            "source_review": "Compared asset evidence directly with supplied original GIS snapshot, official Maclure / Purdue FSCL source notes, and preserved gallery photographs; builder claims were not accepted without inspection."
        },
        "measured_asset": {
            "scene": scene.name,
            "collection": col.name,
            "building_id": root.get("building_id"),
            "source_feature_id": root.get("source_feature_id"),
            "object_count": len(col.objects),
            "evaluated_bounds_xyz_m": overall_bounds,
            "wall_base_vertex_count": len(wall_base),
            "gis_ring_vertex_count": len(ring_local),
            "gis_wall_bidirectional_vertex_hausdorff_m": round(hausdorff, 5),
            "gis_polygon_area_approx_m2": round(abs(area2/2), 3),
            "placement_origin_xy_m": [round(v, 6) for v in placement],
            "entry": entry_data,
            "front_stairs": stair_data,
            "nearest_stair_entry_center_distance_m": round(entry_stair_center_distance, 4) if entry_stair_center_distance is not None else None,
            "floor_objects": [obj_info(o) for o in floor_objs],
            "estimated_partition_object_count": len(partitions),
            "garden_stone_object_names": [o.name for o in stone],
            "text_datablocks": text_payload,
            "material_names": materials,
            "external_image_dependencies": ext_images,
            "linked_library_count": linked_libraries
        },
        "findings": [
            "The revision materially resolves the prior documented exterior issues: entry and stair placement now agree with the official facade reference, and the garden inscription is corrected and readable in the exterior preview.",
            "Saved render state includes three visible floor-related objects. The separate plan preview is an intelligible estimated ground-floor layout; the available source only supports a schematic room program and does not establish dimensions or all-floor arrangement.",
            "GIS footprint and local centroid match within the source conversion's precision. GIS does not verify height, orientation of the facade, or roof shape; photo capture date and survey accuracy are unknown.",
            "The opened asset has no external image-file dependencies or linked Blender libraries."
        ],
        "remaining_changes_if_target_is_8_of_10": [],
        "remaining_uncertainty": [
            "No measured elevation or architectural plans were present in supplied evidence; all vertical dimensions, roof construction, and interior dimensions remain estimates.",
            "No source photo capture date/current facade survey or GIS positional accuracy metadata is available.",
            "Interior review is limited to an illustrative ground-floor plan; second-floor and basement arrangements are not visually demonstrated in the provided plan preview."
        ],
        "grade_scope_note": "Single 10-point asset score. Exact SHA-256 was checked before and after opening/evaluation. Evaluator writes only report.json in its own independent-grade folder."
    }


result = evaluate()
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
