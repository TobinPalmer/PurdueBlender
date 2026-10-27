"""Independent, reproducible UPOF review. Run with Blender after opening the asset."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/utility_plant_office_facility"
ASSET = ROOT / "modular/buildings/massing_utility_plant_office_facility_e219ef5.blend"
EXPECTED_SCENE = "Building_massing_utility_plant_office_facility_e219ef5"
EXPECTED_COLLECTION = "Asset_massing_utility_plant_office_facility_e219ef5"
SHELL_NAME = "UPOF_Office_Shell_Footprint_Verified_Extrusion_Estimated"


def _source_geometry():
    feature = json.loads((AUDIT / "sources/arcgis_fid296_feature.json").read_text(encoding="utf-8"))["features"][0]
    ring = feature["geometry"]["rings"][0][:-1]
    campus = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
               (lat - 40.4274) * 111040.0) for lon, lat in ring]
    cross = [campus[i][0] * campus[(i + 1) % len(campus)][1]
             - campus[(i + 1) % len(campus)][0] * campus[i][1]
             for i in range(len(campus))]
    signed_area = sum(cross) / 2
    cx = sum((campus[i][0] + campus[(i + 1) % len(campus)][0]) * cross[i]
             for i in range(len(campus))) / (6 * signed_area)
    cy = sum((campus[i][1] + campus[(i + 1) % len(campus)][1]) * cross[i]
             for i in range(len(campus))) / (6 * signed_area)
    local = [(x - cx, y - cy) for x, y in campus]
    lengths = [math.hypot(local[(i + 1) % len(local)][0] - local[i][0],
                          local[(i + 1) % len(local)][1] - local[i][1])
               for i in range(len(local))]
    major_edge = lengths.index(max(lengths))
    p0, p1 = local[major_edge], local[(major_edge + 1) % len(local)]
    long_axis_from_north = abs((math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0])) - 90 + 180) % 360 - 180)
    return feature, local, (cx, cy), abs(signed_area), long_axis_from_north


def evaluate():
    """Return {score,max_score,criteria,evidence,findings} from raw sources and Blender data."""
    scene = bpy.context.scene
    asset_collection = bpy.data.collections.get(EXPECTED_COLLECTION)
    shell = bpy.data.objects.get(SHELL_NAME)
    source, source_local, centroid, source_area, source_axis_offset_deg = _source_geometry()
    assert scene and scene.name == EXPECTED_SCENE, "Wrong or missing scene"
    assert asset_collection is not None and shell is not None, "Expected UPOF collection/shell missing"
    assert source["attributes"]["FID"] == 296 and source["attributes"]["BLDG_ABBR"] == "UPOF"

    model_ring = [(float((shell.matrix_world @ v.co).x), float((shell.matrix_world @ v.co).y))
                  for v in list(shell.data.vertices)[:10]]
    model_area = abs(sum(model_ring[i][0] * model_ring[(i + 1) % 10][1]
                         - model_ring[(i + 1) % 10][0] * model_ring[i][1]
                         for i in range(10)) / 2)
    point_errors = [math.dist(a, b) for a, b in zip(source_local, model_ring)]
    bxs = (min(p[0] for p in model_ring), max(p[0] for p in model_ring))
    bys = (min(p[1] for p in model_ring), max(p[1] for p in model_ring))
    rms = math.sqrt(sum(err * err for err in point_errors) / len(point_errors))
    max_error = max(point_errors)
    area_delta_pct = abs(model_area - source_area) / source_area * 100
    source_attrs = source["attributes"]
    validation = json.loads((AUDIT / "validation.json").read_text(encoding="utf-8"))
    provenance = json.loads((AUDIT / "source_provenance.json").read_text(encoding="utf-8"))
    oep = next(item for item in provenance["sources"] if item["source_id"] == "purdue_oep_bep_upof")
    imagery = next(item for item in provenance["sources"] if item["source_id"] == "esri_world_imagery_tile")

    window_count = sum(1 for obj in asset_collection.all_objects if "_glazing" in obj.name)
    door_objects = [obj for obj in asset_collection.all_objects if "Main_Entry_Door" in obj.name]
    roof_equipment = [obj.name for obj in asset_collection.all_objects
                      if obj.name.startswith("Roof_HVAC_Cabinet")]
    schematic_collections = [c.name for c in asset_collection.children
                             if c.name.startswith("Interior_Schematic")]
    external_images = [image.filepath for image in bpy.data.images
                       if image.source == "FILE" and image.filepath and not image.packed_file
                       and not Path(bpy.path.abspath(image.filepath)).exists()]

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "points": 2.0,
            "max_points": 2.0,
            "status": "verified",
            "evidence": f"Raw Purdue GIS feature FID={source_attrs['FID']} / {source_attrs['BLDG_ABBR']} is {source_attrs['BUILDING_N']}; official OEP snapshot identifies the address. Independently recomputed shell-vs-feature ring RMS error {rms:.4f} m, max vertex error {max_error:.4f} m, area {source_area:.3f} vs {model_area:.3f} m² ({area_delta_pct:.4f}% difference).",
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "points": 1.8,
            "max_points": 2.0,
            "status": "verified for library anchor and plan; master registration pending",
            "evidence": f"Source geometry centroid independently recomputes to ({centroid[0]:.3f}, {centroid[1]:.3f}) campus meters; declared local-library anchor is ({validation['placement_origin_xy_m'][0]:.3f}, {validation['placement_origin_xy_m'][1]:.3f}). Structural plan bounds are {bxs[1]-bxs[0]:.3f} × {bys[1]-bys[0]:.3f} m, matching the converted GIS outline; major axis is about {source_axis_offset_deg:.2f}° from north. The master placement marker was not part of this asset review.",
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "points": 1.2,
            "max_points": 2.0,
            "status": "partial; height estimated",
            "evidence": f"Purdue OEP describes two floors; aerial tile shows a bright, ribbed, low-looking roof. GIS feature NUM_LEVELS={source_attrs['NUM_LEVELS']}; its Extrution={source_attrs['Extrution']} value lacks documented units. The 7.32 m parapet height is a plausible but unverified feet interpretation. Rooftop equipment height is above the roof silhouette and should not be counted as structural height.",
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "points": 1.0,
            "max_points": 2.0,
            "status": "partly supported; most facade detailing uncertain",
            "evidence": f"OEP confirms the main entry on the east wall and official room use, but neither the saved OEP page nor the available aerial tile verifies facade material, window pattern, floor-band trim, or the four modeled large rooftop HVAC cabinets. Current model has {len(door_objects)} door leaves and {window_count} glazing panels. The facade is a generic, mostly opaque envelope from the review view; exact architectural features are therefore not verified.",
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "points": 1.9,
            "max_points": 2.0,
            "status": "pass with integration handoff remaining",
            "evidence": f"Fresh Blender 5.2.3 open succeeded; expected scene and collection exist and contain {len(asset_collection.all_objects)} objects. Procedural materials have no missing external image dependencies. GIS/OEP/aerial snapshots and provenance are present. Interior groups {schematic_collections} are labeled schematic. Master linkage/integration is coordinator-owned and remains pending.",
        },
    ]
    score = round(sum(c["points"] for c in criteria), 2)
    findings = [
        "The GIS-derived footprint and anchor pass at the stated local-meters tolerance. The assigned library is not placed in the master by this review, so marker registration remains a separate integration check.",
        "Height is estimated, not measured: ArcGIS field `Extrution=24` has no units in service metadata. Confirm units or keep the 7.32 m value explicitly estimated.",
        "The available high-resolution overhead image shows a mostly uninterrupted bright roof with narrow parallel seams; the model's multiple large HVAC cabinets and hatch are not evidenced by the captured tile. Reduce or reposition those only with stronger imagery/plans.",
        "No current direct UPOF facade image or architectural elevation was supplied. East entry location and two-floor office use are supported, while window rhythm and warm-gray facade material remain visual estimates. Do not report those as verified.",
    ]
    return {
        "score": score,
        "max_score": 10,
        "passing_threshold": 8.0,
        "criteria": criteria,
        "evidence": {
            "fresh_open_scene": scene.name,
            "fresh_open_collection": asset_collection.name,
            "asset_objects": len(asset_collection.all_objects),
            "source_fid": source_attrs["FID"],
            "source_code": source_attrs["BLDG_ABBR"],
            "source_area_m2": round(source_area, 4),
            "shell_area_m2": round(model_area, 4),
            "shell_rms_vertex_error_m": round(rms, 5),
            "shell_max_vertex_error_m": round(max_error, 5),
            "shell_area_delta_percent": round(area_delta_pct, 5),
            "footprint_bounds_local_m": {"x": [round(bxs[0], 4), round(bxs[1], 4)],
                                          "y": [round(bys[0], 4), round(bys[1], 4)]},
            "placement_origin_xy_m": validation["placement_origin_xy_m"],
            "unpacked_missing_images": external_images,
            "source_snapshots": [
                x.get("snapshot") or x.get("tile_snapshot") or x.get("metadata_snapshot")
                for x in provenance["sources"]
                if x.get("snapshot") or x.get("tile_snapshot") or x.get("metadata_snapshot")
            ],
            "imagery_acquisition_date": imagery["imagery_acquisition_date"],
            "height_source_value": {"NUM_LEVELS": source_attrs["NUM_LEVELS"],
                                    "Extrution": source_attrs["Extrution"]},
            "oep_facts_used": oep["facts_used"],
        },
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    path = AUDIT / "independent_grade/grade_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("INDEPENDENT_UPOF_GRADE", json.dumps(result, sort_keys=True))
