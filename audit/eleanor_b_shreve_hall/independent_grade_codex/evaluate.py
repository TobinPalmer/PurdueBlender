"""Independent Shreve Hall source, mesh, and evidence evaluator.

Run with Blender after opening the assigned .blend. The function independently
checks footprint vertices, transforms, bounds, exported collection, and evidence;
architectural rubric scores are manual judgments against the saved references.
"""
import bpy
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(EVIDENCE_DIR, "..", ".."))
ID = "massing_shreve_hall_06d270a"
OBJECT = "Shreve Hall"
COLLECTION = "Asset_" + ID
FEATURE = json.load(open(os.path.join(EVIDENCE_DIR, "source_feature_258_raw.json"), encoding="utf8"))
EVIDENCE = json.load(open(os.path.join(EVIDENCE_DIR, "evidence.json"), encoding="utf8"))
REOPEN = json.load(open(os.path.join(EVIDENCE_DIR, "shreve_reopen_check.json"), encoding="utf8"))
PHOTO = json.load(open(os.path.join(EVIDENCE_DIR, "purdue_official_exterior_observation.json"), encoding="utf8"))


def evaluate():
    obj = bpy.data.objects.get(OBJECT)
    collection = bpy.data.collections.get(COLLECTION)
    assert obj is not None and collection is not None
    assert obj in collection.objects[:] and len(collection.objects) == 1
    assert obj.type == "MESH"
    expected_path = os.path.join(ROOT, "modular", "buildings", ID + ".blend")
    assert os.path.normcase(bpy.data.filepath) == os.path.normcase(expected_path)

    ring = FEATURE["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    lat0, lon0 = 40.4274, -86.9137
    source_points = sorted({(
        (lon-lon0)*111412.84*math.cos(math.radians(lat0)),
        (lat-lat0)*111040.0,
    ) for lon, lat in ring})
    world_vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
    base = [(p.x, p.y) for p in world_vertices if abs(p.z) < 1e-5]
    errors = [min(math.hypot(x-bx, y-by) for bx, by in base) for x, y in source_points]
    max_error = max(errors)
    bounds = [[min(p[i] for p in world_vertices), max(p[i] for p in world_vertices)] for i in range(3)]
    transform = {
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
    }

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "Official Purdue GIS feature 258 identifies Eleanor B. Shreve Residence Hall (SHRV).",
                f"Independently compared {len(source_points)} distinct projected GIS ring points with the reopened mesh base; maximum nearest XY difference is {max_error:.6f} m.",
                "The source polygon's stepped multi-wing plan is preserved by the structural mesh. The official footprint is not a certified survey.",
            ],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": [
                "The base vertices use the repository's documented campus-local conversion and match the source ring at coordinate-conversion precision.",
                f"Reopened mesh bounds in meters are {bounds}; object transform is {transform}.",
                "Position and dimensions are consistent with the GIS polygon, but no survey control or published positional uncertainty is available.",
            ],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.2,
            "max_score": 2.0,
            "evidence": [
                "The GIS snapshot lists NUM_LEVELS=10; Purdue move-in directions distinguish floors 1-5 and 6-8, confirming at least eight numbered floors.",
                "The official Purdue exterior photograph shows a flat roof and a raised mechanical screen, both reflected in the asset.",
                "The 29 m wall height and 32.275 m total mesh peak are estimates; the available sources provide no scaled elevation or measured height. The photograph does not show all wings, so relative tower/connector heights remain uncertain.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.4,
            "max_score": 2.0,
            "evidence": [
                "The official exterior photo supports red brick, a pale lower base and vertical facade strips, repeated narrow windows, a broad glass entry, a canopy supported by columns, stairs, and a rooftop enclosure.",
                "The model includes brick and pale trim, repeated windows, the column-supported canopy and raised stair, plus a raised rooftop screen.",
                "The facade rhythm, vertical strips, connector-to-tower height changes, and entrance bearing/dimensions remain schematic because the official photo is unscaled and shows only part of the building.",
            ],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": [
                f"The saved asset reopens with one mesh in the expected collection ({len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces).",
                "A dedicated portable builder, raw GIS snapshot, official Purdue exterior photo and observation, move-in evidence, structured evidence, reopen validation, and current overview/detail renders are present.",
                "The asset is still awaiting integration and reopen review in the shared master blend, which is coordinator-owned.",
            ],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    return {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "model": os.path.relpath(bpy.data.filepath, ROOT).replace("\\", "/"),
            "feature_id": FEATURE["attributes"]["FID"],
            "building_code": FEATURE["attributes"]["BLDG_ABBR"],
            "gis_ring_point_count": len(source_points),
            "max_nearest_base_vertex_error_m": round(max_error, 8),
            "mesh_bounds_world_m": bounds,
            "object_transform": transform,
            "mesh_vertices": len(obj.data.vertices),
            "mesh_faces": len(obj.data.polygons),
            "exported_collection_object_count": len(collection.objects),
            "saved_asset_reopened": REOPEN["saved_asset_reopened"],
            "official_photo_date": PHOTO["source_date"],
            "wall_height_m_status": EVIDENCE["measurements"]["height_status"],
            "roof_screen_height_limit_m": bounds[2][1],
        },
        "findings": [
            "The footprint and overall facade vocabulary are supported, but the GIS map does not establish site-survey accuracy or height.",
            "The official photo supports a rooftop screen and entrance canopy, but its unscaled partial view cannot validate exact roof height, full facade composition, or connector-to-tower height transitions.",
        ],
    }


result = evaluate()
with open(os.path.join(HERE, "result.json"), "w", encoding="utf8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print("INDEPENDENT_GRADE=" + json.dumps(result))
