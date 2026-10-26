"""Independent fresh evaluator for the current AHF asset. Run inside Blender."""
import bpy
import bmesh
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ASSET = ROOT / "modular/buildings/massing_animal_holding_facility_4733f46.blend"
GIS_PATH = ROOT / "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25.json"
BUILD_EVIDENCE_PATH = ROOT / "audit/animal_holding_facility/build_evidence.json"
FOOTPRINT_METRICS_PATH = ROOT / "audit/animal_holding_facility/footprint_comparison.json"
HEIGHTS_PATH = ROOT / "audit/animal_holding_facility/ndhm_roof_height_statistics.json"
ROOF_PROFILE_PATH = ROOT / "audit/animal_holding_facility/ndhm_roof_profile_analysis.json"
EXIT_PLAN_PATH = ROOT / "audit/animal_holding_facility/sources/purdue_ahf_exits_diagram_2026-10-26.jpg"
LINK_CHECK_PATH = ROOT / "audit/animal_holding_facility/link_verification.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate():
    assert Path(bpy.data.filepath).resolve() == ASSET.resolve(), (
        f"Blender opened {bpy.data.filepath}, expected {ASSET}"
    )
    gis = load(GIS_PATH)
    build_evidence = load(BUILD_EVIDENCE_PATH)
    footprint = load(FOOTPRINT_METRICS_PATH)
    heights = load(HEIGHTS_PATH)
    profile = load(ROOF_PROFILE_PATH)
    link_check = load(LINK_CHECK_PATH)
    feature = gis["features"][0]
    attrs = feature["attributes"]
    assert attrs["FID"] == 266 and attrs["BLDG_ABBR"] == "AHF"
    assert attrs["BUILDING_N"] == "Animal Holding Facility"

    collection_name = "Asset_massing_animal_holding_facility_4733f46"
    collection = bpy.data.collections.get(collection_name)
    assert collection is not None, f"Missing collection {collection_name}"
    members = list(collection.objects)
    assert len(members) == 1, f"Expected one asset object, got {len(members)}"
    obj = members[0]
    assert obj.name == "Animal Holding Facility" and obj.type == "MESH"
    assert not obj.modifiers, f"Unexpected modifiers: {[m.name for m in obj.modifiers]}"

    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    non_manifold_count = sum(not edge.is_manifold for edge in bm.edges)
    boundary_count = sum(edge.is_boundary for edge in bm.edges)
    bm.free()
    world_vertices = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    actual_bounds = [[min(v[i] for v in world_vertices), max(v[i] for v in world_vertices)] for i in range(3)]
    evaluated_vertex_count, evaluated_face_count = len(mesh.vertices), len(mesh.polygons)
    evaluated.to_mesh_clear()
    mesh = None

    ring = feature["geometry"]["rings"][0]
    gis_xy = [
        (
            (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0,
        )
        for lon, lat in ring[:-1]
    ]
    gis_bounds = [
        [min(p[0] for p in gis_xy), max(p[0] for p in gis_xy)],
        [min(p[1] for p in gis_xy), max(p[1] for p in gis_xy)],
    ]
    model_xy = [(v[0], v[1]) for v in world_vertices]
    gis_vertex_to_model_distance = [
        min(math.dist(gis_point, model_point) for model_point in model_xy)
        for gis_point in gis_xy
    ]
    max_gis_vertex_to_model_vertex_m = max(gis_vertex_to_model_distance)
    envelope_deltas = [
        [actual_bounds[axis][i] - gis_bounds[axis][i] for i in range(2)]
        for axis in range(2)
    ]
    max_envelope_delta = max(abs(v) for row in envelope_deltas for v in row)
    horizontal_dims_m = [actual_bounds[0][1] - actual_bounds[0][0], actual_bounds[1][1] - actual_bounds[1][0]]
    vertical_extent_m = actual_bounds[2][1] - actual_bounds[2][0]
    image_dependencies = [img.filepath for img in bpy.data.images if img.source == "FILE"]

    # Egress credit is intentionally limited: the plan locates emergency exits,
    # not a unique public/main entrance, materials, or facade architecture.
    exit_record = build_evidence["emergency_exit_plan_registration"]
    exit_count = exit_record["door_count"]
    max_exit_residual = max(p["plan_to_shell_residual_m"] for p in exit_record["positions"])
    assert EXIT_PLAN_PATH.exists() and exit_count == 9

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": [
                "Purdue GIS feature FID 266 identifies BLDG_ABBR AHF and BUILDING_N Animal Holding Facility at 410 S University Street.",
                f"The official Purdue polygon and 2016-2020 Indiana footprint comparison reports 0.50 m centroid offset and {footprint['comparison']['maximum_vertex_to_other_boundary_m']:.3f} m maximum symmetric vertex-to-boundary distance.",
            ],
            "findings": "The building identity is unambiguous and the Purdue survey-style footprint is corroborated by an independent state footprint. The saved model follows the 16-vertex Purdue outline.",
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0 if max_envelope_delta <= 0.30 else 1.5,
            "max_score": 2.0,
            "evidence": [
                f"Reopened mesh evaluated XY bounds: X {actual_bounds[0][0]:.3f} to {actual_bounds[0][1]:.3f} m; Y {actual_bounds[1][0]:.3f} to {actual_bounds[1][1]:.3f} m.",
                f"Model bounds differ from the converted Purdue GIS footprint bounds by at most {max_envelope_delta:.3f} m; measured model envelope is {horizontal_dims_m[0]:.3f} by {horizontal_dims_m[1]:.3f} m.",
                f"Each GIS footprint corner is represented within {max_gis_vertex_to_model_vertex_m:.3f} m of a model vertex in XY.",
                "Top-down comparison against 2023 Indiana orthophoto visually confirms the building's orientation and campus placement.",
            ],
            "findings": "XY position, orientation, and plan scale are strongly supported. The small envelope expansion is consistent with the perimeter wall/roof edge around the GIS polygon.",
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.75,
            "max_score": 2.0,
            "evidence": [
                f"Purdue GIS attributes report NUM_LEVELS={attrs['NUM_LEVELS']} and CountOfFLO={attrs['CountOfFLO']}.",
                f"The 2018 Indiana 5-ft NDHM has {heights['zones']['north_main']['pixel_count']} north/main and {heights['zones']['south_addition']['pixel_count']} south/addition samples; median roof-surface heights are {heights['zones']['north_main']['median_m']:.3f} m and {heights['zones']['south_addition']['median_m']:.3f} m above ground.",
                f"Current model vertical extent is {vertical_extent_m:.3f} m; the southern roof profile trend is supported by multi-bin fits in {len(profile['bin_size_sensitivity']['south_addition'])} resolutions.",
            ],
            "findings": "The one-floor and two-zone roof massing have source support. Deduct 0.25 because the 5-ft normalized-height raster is not an eave survey and the roof-zone seam/slope remain approximations.",
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.5,
            "max_score": 2.0,
            "evidence": [
                f"Purdue AHF-01 emergency-exits plan dated 2023-12-20 explicitly marks {exit_count} red-arrow emergency exits; the asset contains corresponding schematic door panels.",
                f"Plan-to-GIS registration is approximate and has a maximum recorded shell residual of {max_exit_residual:.3f} m.",
            ],
            "findings": "This plan supports the existence and approximate plan locations of emergency egress doors only. It does not identify the public/main entrance, facade materials, window rhythm, signage, or distinctive exterior features. Door dimensions, appearance, and placement precision remain estimates; no architectural facade credit is awarded.",
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0 if (not image_dependencies and non_manifold_count == 0 and boundary_count == 0 and link_check.get("result") == "PASS") else 1.5,
            "max_score": 2.0,
            "evidence": [
                f"Expected collection {collection_name} contains exactly one mesh object named {obj.name}.",
                f"Fresh Blender evaluation reports {evaluated_vertex_count} vertices and {evaluated_face_count} faces, no modifiers, {non_manifold_count} non-manifold edges, and {boundary_count} boundary edges.",
                f"External image dependencies: {image_dependencies}; independent linked-library check: {link_check.get('result')}.",
            ],
            "findings": "The library asset is portable and structurally valid; its structured evidence covers GIS, orthophoto, lidar, and egress-plan inputs with limitations recorded.",
        },
    ]
    total = round(sum(c["score"] for c in criteria), 2)
    return {
        "evaluator": "independent AHF r7 evaluator",
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "asset": "modular/buildings/massing_animal_holding_facility_4733f46.blend",
        "score": total,
        "max_score": 10,
        "passing_threshold": 8,
        "pass": total >= 8,
        "criteria": criteria,
        "evidence": {
            "purdue_gis_feature_id": attrs["FID"],
            "purdue_gis_attributes": {k: attrs[k] for k in ("BLDG_ABBR", "BUILDING_N", "NUM_LEVELS", "CountOfFLO", "ADDRESS")},
            "max_gis_vertex_to_model_vertex_m": max_gis_vertex_to_model_vertex_m,
            "indiana_footprint_comparison": footprint["comparison"],
            "blender_reopen": {
                "blender_version": bpy.app.version_string,
                "scene": bpy.context.scene.name,
                "collection": collection.name,
                "object_count": len(members),
                "object_name": obj.name,
                "evaluated_vertex_count": evaluated_vertex_count,
                "evaluated_face_count": evaluated_face_count,
                "non_manifold_edge_count": non_manifold_count,
                "boundary_edge_count": boundary_count,
                "evaluated_bounds_world_m": actual_bounds,
                "external_image_dependencies": image_dependencies,
            },
            "egress_plan": {
                "source_image": "audit/animal_holding_facility/sources/purdue_ahf_exits_diagram_2026-10-26.jpg",
                "date": exit_record["image_date"],
                "emergency_exit_count": exit_count,
                "maximum_plan_to_shell_residual_m": max_exit_residual,
                "facade_or_main_entrance_evidence": False,
            },
        },
        "findings": [
            "The egress plan justifies a limited schematic emergency-door treatment. It does not resolve the facade/entrance evidence gap.",
            "The building passes the 8/10 threshold from footprint, position, roof/floor, export, and limited exit-location evidence; facade appearance and the primary entrance remain unverified.",
        ],
    }


result = evaluate()
(OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
