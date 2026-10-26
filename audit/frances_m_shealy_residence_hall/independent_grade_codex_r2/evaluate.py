"""Independent Shealy Hall source, asset, and evidence evaluator.

Run with Blender after opening the assigned asset. Architectural appearance
scores are manual rubric judgments based on the official archive photograph
and rendered views; the script independently verifies identity, footprint,
transforms, collection export, and stored evidence facts.
"""
import bpy
import json
import math
import os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(EVIDENCE_DIR, "..", ".."))
EVIDENCE = json.load(open(os.path.join(EVIDENCE_DIR, "evidence.json"), encoding="utf8"))
FEATURE = json.load(open(os.path.join(EVIDENCE_DIR, "source_feature_277_raw.json"), encoding="utf8"))
OBSERVATION = json.load(open(os.path.join(EVIDENCE_DIR, "source_exterior_reference_observation.json"), encoding="utf8"))
ID = "massing_shealy_frances_m_residence_hall_a210e50"
COLLECTION = "Asset_" + ID
OBJECT = "Shealy (Frances M.) Residence Hall"


def evaluate():
    obj = bpy.data.objects.get(OBJECT)
    collection = bpy.data.collections.get(COLLECTION)
    assert obj is not None and collection is not None
    ring = FEATURE["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    lat0, lon0 = 40.4274, -86.9137
    expected = sorted({(
        (lon - lon0) * 111412.84 * math.cos(math.radians(lat0)),
        (lat - lat0) * 111040.0,
    ) for lon, lat in ring})
    bottom = sorted({(round(v.co.x, 5), round(v.co.y, 5)) for v in obj.data.vertices if abs(v.co.z) < 1e-5})
    errors = [min(math.hypot(x - ax, y - ay) for ax, ay in bottom) for x, y in expected]
    max_error = max(errors)
    bounds = [min(v.co[i] for v in obj.data.vertices) for i in range(3)] + [max(v.co[i] for v in obj.data.vertices) for i in range(3)]
    assert len(collection.objects) == 1 and collection.objects[0] == obj
    assert obj.type == "MESH"
    assert os.path.normcase(bpy.data.filepath) == os.path.normcase(os.path.join(ROOT, "modular", "buildings", ID + ".blend"))

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "The source feature snapshot identifies FID 277 / SHLY / Frances M. Shealy Residence Hall.",
                f"Independently compared the {len(expected)} unique projected GIS ring vertices to the mesh base vertices; maximum nearest XY difference is {max_error:.6f} m.",
                "The official ring is a concave U-shaped plan; the rendered model preserves its open courtyard and long wings.",
            ],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": [
                "Asset mesh is in the repository's documented campus-local XY coordinate approximation and follows the source polygon orientation.",
                f"World-space mesh bounds measured from the reopened asset are {bounds} m.",
                "The source polygon comparison demonstrates direct implementation consistency, but the GIS service publishes no positional accuracy or survey uncertainty; no independent site control is present.",
            ],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.2,
            "max_score": 2.0,
            "evidence": [
                "The GIS attribute reports five levels, but it is not an elevation measurement; the modeled 15.2 m wall height is explicitly estimated.",
                "The archive photo directly shows a broad, continuous pitched slate roof with several prominent front-facing gables and chimneys.",
                "The updated oblique and roof-plan renders show sloped roof planes rising toward a smaller cap, replacing the earlier single flat cap. The resulting broad faceted inset roof is still unlike the photo's dark slate ridges and distinct gable composition; overall roof plan and elevation remain uncertain.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.4,
            "max_score": 2.0,
            "evidence": [
                "The archive photo shows red-brown brick, strong pale limestone surrounds and string courses, grouped and bay windows, an elaborate stone portal, and a large Tudor entrance gable.",
                "Current views show the projecting triangular entrance gable, a limestone-framed doorway, lion/shield relief, repeated limestone courses, and selected projecting bay windows.",
                "The portal and relief remain schematic and low contrast; bay projections and window grouping are much simpler than the photographed stone portal, grouped windows, and broad stacked bays.",
            ],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": [
                f"Reopened asset contains one mesh object in the expected collection with {len(obj.data.vertices)} vertices and {len(obj.data.polygons)} faces.",
                "A dedicated building builder module, relative source/evidence paths, raw GIS snapshot, archive image and metadata, structured evidence JSON, and rendered views are present.",
                "The model saves and reopens in the assigned library path with zero object transforms; the updated builder and three rendered evidence views are present. Shared master integration has not been independently checked.",
            ],
        },
    ]
    score = round(sum(item["score"] for item in criteria), 1)
    return {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "model": os.path.relpath(bpy.data.filepath, ROOT).replace("\\", "/"),
            "evidence_directory": os.path.relpath(EVIDENCE_DIR, ROOT).replace("\\", "/"),
            "reference_photo_date": OBSERVATION["source_date"],
            "source_feature_id": FEATURE["attributes"]["FID"],
            "gis_ring_point_count": len(expected),
            "base_vertex_max_nearest_error_m": round(max_error, 8),
            "mesh_vertex_count": len(obj.data.vertices),
            "mesh_face_count": len(obj.data.polygons),
            "mesh_bounds_min_xyz_m": bounds[:3],
            "mesh_bounds_max_xyz_m": bounds[3:],
            "collection_object_count": len(collection.objects),
        },
        "findings": [
            "The updated roof is pitched but remains a generic inset faceted cap instead of the photograph's dark slate ridges and multiple gables; a more source-specific roof plan is still needed.",
            "The entrance gable and selected projections are visible, but the portal, bay dimensions, grouped windows and lion relief remain much simpler than the archival facade.",
            "Height is not independently verified: keep it labeled as an estimate and do not treat the GIS five-level field as measured elevation.",
        ],
    }


result = evaluate()
out_path = os.path.join(HERE, "result.json")
json.dump(result, open(out_path, "w", encoding="utf8"), indent=2)
print("INDEPENDENT_GRADE=" + json.dumps(result))
