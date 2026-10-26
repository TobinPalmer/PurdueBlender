"""Independent reopen evaluator for CHAS massing asset; run by Blender 4.5."""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_chaney_hale_hall_of_science_chas_6bb9ef7"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE = ROOT / "audit" / "chaney_hale_hall_of_science_chas" / "sources" / "purdue_gis_fid945_live.json"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)


def local_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def bbox(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)]


def polygon_area(points):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(points, points[1:] + points[:1])) / 2)


def evaluate():
    source_data = json.loads(SOURCE.read_text(encoding="utf-8"))
    matches = [f for f in source_data["features"] if f.get("attributes", {}).get("FID") == 945]
    assert len(matches) == 1, f"Expected one GIS FID 945 feature, got {len(matches)}"
    feature = matches[0]
    attrs = feature["attributes"]
    assert attrs.get("BLDG_ABBR") == "CHAS"
    assert attrs.get("BUILDING_N") == "Chaney-Hale Hall of Science"
    gis = [local_xy(lon, lat) for lon, lat in feature["geometry"]["rings"][0]]
    if gis[0] == gis[-1]:
        gis.pop()

    scene = bpy.context.scene
    collection_name = f"Asset_{ASSET_ID}"
    collection = bpy.data.collections.get(collection_name)
    objs = list(collection.objects) if collection else []
    obj = bpy.data.objects.get("Chaney-Hale Hall of Science (CHAS)")
    assert collection is not None and scene.name == f"Building_{ASSET_ID}"
    assert len(objs) == 1 and obj is objs[0] and obj.type == "MESH"

    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(dg)
    mesh = eval_obj.to_mesh()
    world = [eval_obj.matrix_world @ v.co for v in mesh.vertices]
    eval_obj.to_mesh_clear()
    ground = []
    for v in world:
        if abs(v.z) < 1e-4 and not any(math.hypot(v.x-x, v.y-y) < 1e-4 for x, y in ground):
            ground.append((v.x, v.y))
    errors = [min((math.dist(p, q) for q in ground), default=float("inf")) for p in gis]
    missing = [list(p) for p, e in zip(gis, errors) if e > 0.001]
    all_xyz = [(v.x, v.y, v.z) for v in world]
    source_box, shell_box = bbox(gis), bbox(ground)
    height = max(v[2] for v in all_xyz) - min(v[2] for v in all_xyz)
    ext_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath]
    collection_paths = sorted({getattr(lib, "filepath", "") for lib in bpy.data.libraries if lib.filepath})
    material_names = [m.name for m in obj.data.materials if m]

    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "points": 2.0,
         "earned": 2.0 if not missing and len(gis) == 52 else 1.5,
         "evidence": f"Purdue BuildingShapesZip4 FID 945 identifies CHAS. The {len(gis)}-point GIS ring is reproduced at ground level; maximum nearest-vertex deviation {max(errors):.8f} m. Source-derived approximate area {polygon_area(gis):.2f} m².",
         "findings": ["GIS feature is a map footprint, not surveyed structural-wall geometry."]},
        {"criterion": "Position, orientation, and scale/dimensions", "points": 2.0,
         "earned": 2.0 if not missing and max(errors) <= 0.001 and all(abs(x) < 1e-6 for x in obj.location) and all(abs(x-1) < 1e-6 for x in obj.scale) else 1.0,
         "evidence": f"Ground ring lies at GIS campus coordinates in the documented local approximation. Source bbox {source_box}; shell bbox {shell_box}; object transform location={list(obj.location)}, scale={list(obj.scale)}. No rotation is applied; source vertex sequence and shell vertices agree.",
         "findings": ["The GIS source provides no positional accuracy metadata; apparent numeric agreement validates reconstruction of the source data, not survey accuracy."]},
        {"criterion": "Evidence-backed height, floors, and roof form", "points": 2.0,
         "earned": 1.25,
         "evidence": f"Purdue's 2020 opening article states four stories; the supplied official photo and contractor photo show a broad, shallow flat roof edge. Reopened model height is {height:.2f} m and cap is modeled at z={max(v[2] for v in all_xyz):.2f} m.",
         "findings": ["16 m height and 0.72 m overhang are explicitly estimates; no elevation or survey datum supports them.", "Roof is represented as one flat cap; photographed roof soffit supports the general form only."]},
        {"criterion": "Facade, entrances, and distinctive architecture", "points": 2.0,
         "earned": 0.9,
         "evidence": f"Mesh has {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} polygons, and materials {material_names}. Photos support red brick, blue-gray glazing, dark base, pale horizontal bands, and deep soffit.",
         "findings": ["Reference photos show broad, nearly continuous curtainwall fields, narrow vertical mullions, solid brick end zones with tall slit windows, and visible doors; the model instead uses repeated isolated rectangular window panels and largely unarticulated brick end walls.", "No distinct entrance or canopy geometry is present, and the selected preview omits the principal photographed elevation.", "A single extruded GIS polygon cannot demonstrate the actual wing height/setback differences beyond the outline."]},
        {"criterion": "Modular export, portability, and complete evidence", "points": 2.0,
         "earned": 2.0 if len(objs) == 1 and not obj.modifiers and not ext_images else 1.0,
         "evidence": f"Reopened with Blender {bpy.app.version_string}; expected scene/collection and one mesh are present; {len(obj.modifiers)} modifiers, {len(ext_images)} external image paths. Material nodes are internal. Candidate evidence folder contains raw GIS, metadata, official Purdue article/photo, ECN webcam photo, architect page, contractor photo, and source/method/uncertainty record.",
         "findings": ["No project-relative linked-library dependency or external image path is required; the saved massing asset opens standalone."]},
    ]
    score = round(sum(c["earned"] for c in criteria), 2)
    result = {
        "building": "Chaney-Hale Hall of Science (CHAS)", "asset_id": ASSET_ID,
        "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "grader": "independent subagent", "grade_date": "2026-10-26",
        "blender_version": bpy.app.version_string, "score": score, "max_score": 10,
        "passing_threshold": 8, "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "source_feature": {"provider": "Purdue BuildingShapesZip4 ArcGIS FeatureServer", "FID": 945,
                               "building_name": attrs.get("BUILDING_N"), "abbreviation": attrs.get("BLDG_ABBR"),
                               "vertices": len(gis), "approx_area_m2": round(polygon_area(gis), 3),
                               "gis_bbox_m": source_box, "shell_bbox_m": shell_box,
                               "max_nearest_ground_ring_vertex_error_m": max(errors), "missing_vertices_over_1mm": missing},
            "asset": {"scene": scene.name, "collection": collection.name, "object": obj.name,
                      "object_count": len(objs), "vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons),
                      "bounds_xyz_m": [[min(v[i] for v in all_xyz), max(v[i] for v in all_xyz)] for i in range(3)],
                      "object_location": list(obj.location), "object_rotation_euler": list(obj.rotation_euler),
                      "object_scale": list(obj.scale), "modifiers": [m.name for m in obj.modifiers],
                      "materials": material_names, "external_images": ext_images,
                      "linked_libraries": collection_paths},
            "inspected_views": ["candidate preview.png", "candidate topdown.png", "official Purdue 2020 exterior photo", "FRP contractor exterior photo", "Purdue ECN rooftop webcam photo"]
        },
        "findings": [finding for c in criteria for finding in c["findings"]],
        "recommendation": "Do not mark complete at this score. Improve the principal facade with source-supported curtainwall extent, vertical mullions, brick end-zone slit windows and entry treatment; capture a principal-elevation comparison and obtain better height/roof evidence if available, then request a fresh independent grade.",
        "files": {"source_candidate_evidence": "audit/chaney_hale_hall_of_science_chas/", "script": "evaluate_chas.py", "probe": "blender_probe.json", "log": "blender.log"}
    }
    (OUT / "blender_probe.json").write_text(json.dumps({
        "blender": bpy.app.version_string,
        "opened_asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "scene": scene.name,
        "expected_scene": f"Building_{ASSET_ID}",
        "collection": collection.name,
        "object_names_in_collection": [o.name for o in objs],
        "object_types": [o.type for o in objs],
        "gis_fid": 945,
        "source_vertex_count": len(gis),
        "shell_ground_vertex_count": len(ground),
        "source_bbox_m": source_box,
        "ground_bbox_m": shell_box,
        "max_ring_vertex_error_m": max(errors),
        "missing_ring_vertices_over_1mm": missing,
        "evaluated_bounds_xyz_m": [[min(v[i] for v in all_xyz), max(v[i] for v in all_xyz)] for i in range(3)],
        "external_image_paths": ext_images,
        "linked_libraries": collection_paths
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("CHAS independent score:", score, "/ 10; pass:", score >= 8)
    print("Report:", OUT / "result.json")


evaluate()
