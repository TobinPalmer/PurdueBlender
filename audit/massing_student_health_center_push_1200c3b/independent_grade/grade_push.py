"""Independent rubric evaluation of the PUSH Blender library.

Run with the project's Blender executable and --background --python grade_push.py.
The evaluator reads the saved .blend, raw GIS feature, published photo, source
register, and reopen evidence. It does not modify the builder or asset.
"""
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_student_health_center_push_1200c3b"
AUDIT = ROOT / "audit" / ASSET_ID
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = AUDIT / "independent_grade" / "independent_grade.json"


def evaluate():
    evidence = json.loads((AUDIT / "build_evidence.json").read_text(encoding="utf-8"))
    register = json.loads((AUDIT / "source_register.json").read_text(encoding="utf-8"))
    raw = json.loads((AUDIT / "sources" / "purdue_gis_fid274_raw.json").read_text(encoding="utf-8-sig"))
    feature = raw["features"][0]
    assert feature["attributes"]["FID"] == 274
    assert feature["attributes"]["BLDG_ABBR"] == "PUSH"
    assert feature["attributes"]["ADDRESS"] == "601 Stadium Mall Drive"
    assert any(s.get("feature_id") == 274 for s in register["sources"])

    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    coll = bpy.data.collections.get("Asset_" + ASSET_ID)
    mesh_objects = [o for o in coll.objects if o.type == "MESH"] if coll else []
    objects = [o for o in coll.objects] if coll else []
    bounds = []
    if mesh_objects:
        coords = [o.matrix_world @ v.co for o in mesh_objects for v in o.data.vertices]
        bounds = [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
    material_count = len({m.name for o in mesh_objects for m in o.data.materials if m})
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file]
    collection_ok = bool(coll and len(objects) == 1 and len(mesh_objects) == 1)
    reopen_record = json.loads((AUDIT / "reopen_verification.json").read_text(encoding="utf-8"))
    reopened_ok = reopen_record.get("result") == "pass" and reopen_record.get("blend_reopened") is True

    # Evidence-based scores: exact GIS identity/ring; source transform and bounds;
    # explicit height conflict; visible facade elements compared with photo; and
    # actual saved library structure plus the evidence/reopen artifacts.
    criteria = [
        {
            "name": "Identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": "Raw Purdue BuildingShapes feature FID 274 names Purdue University Student Health Center (PUSH), address 601 Stadium Mall Drive. The 13-vertex outline is transformed with the project campus formula; build record area is 1204.48 m2.",
            "finding": "Strong identity and plan source match. The exterior photo independently corroborates the building appearance, though it is not a dimensioned footprint survey.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2,
            "evidence": f"Reopened asset vertex bounds are {bounds}; recorded GIS boundary mismatch is 0.0291 m. The GIS ring establishes campus placement, orientation, and horizontal dimensions.",
            "finding": "Horizontal placement and footprint scale closely reproduce the authoritative feature. The project uses an approximate local geographic conversion rather than a surveyed campus CRS, so minor systematic position/scale error remains possible.",
        },
        {
            "name": "Height, floors, and roof form",
            "score": 0.8,
            "max_score": 2,
            "evidence": "GIS FID 274 reports NUM_LEVELS/CountOfFLO=5, floor elevations through F04, and Extrution=48 without documented units. Model height is an explicitly estimated 14.63 m based on 48 ft; the photo shows a red pitched roof and approximately three above-ground levels in the visible portion.",
            "finding": "Height and floor count are unresolved, not measured. The model uses a single fan-like hipped roof over the entire irregular footprint. The 2020 photo instead shows different roof heights and a low entrance wing adjoining the taller main block; that massing is absent.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.0,
            "max_score": 2,
            "evidence": "The Purdue 2020 photograph directly supports red brick, pale stone trim/bands, upper-story windows, a broad glazed entrance, medical emblem, and red tile roof. The model represents brick, repeated windows, bands, glazing, emblem, and red roof.",
            "finding": "The principal facade features are recognizable, but the model repeats small windows uniformly around the perimeter. The photo has larger, differently proportioned upper-story windows, a broad and detailed entrance, and a one-story entrance wing. The entrance wall was selected by longest edge rather than source orientation, and side/rear facades are unverified.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.8,
            "max_score": 2,
            "evidence": f"Saved library collection check: {collection_ok}, {len(objects)} object(s), {len(mesh_objects)} mesh; {material_count} assigned material(s); unpacked external images: {external_images}. Reopen record: {reopened_ok}. Evidence includes raw GIS and metadata, official map PDF, Purdue photo and page snapshots, source register, renders, build record, and reopen validation.",
            "finding": "Stable asset file, collection, and ID are preserved; the export is self-contained and the reopen check passes. The one-mesh export is portable, although the building's architectural parts are not separately editable. Source citations and stated uncertainty are unusually complete.",
        },
    ]
    result = {
        "asset_id": ASSET_ID,
        "asset_file": "modular/buildings/" + ASSET_ID + ".blend",
        "grader": "independent subagent",
        "score": round(sum(c["score"] for c in criteria), 1),
        "max_score": 10,
        "pass_threshold": 8,
        "status": "pass" if sum(c["score"] for c in criteria) >= 8 else "needs_iteration",
        "criteria": criteria,
        "evidence": {
            "direct_asset_inspection": {"collection_present": coll is not None, "object_count": len(objects), "mesh_object_count": len(mesh_objects), "evaluated_vertex_bounds_xyz_m": bounds, "material_count": material_count, "unpacked_external_images": external_images},
            "source_inspection": {"gis_feature_id": feature["attributes"]["FID"], "gis_name": feature["attributes"]["BUILDING_N"], "gis_address": feature["attributes"]["ADDRESS"], "gis_vertex_count": len(feature["geometry"]["rings"][0]) - 1, "source_types": [s["provider"] for s in register["sources"]]},
            "visual_inspection": ["renders/push_exterior_preview.png", "renders/push_footprint_preview.png", "sources/purdue_push_exterior_2020.jpg"],
            "reopen_validation": reopen_record,
        },
        "findings": [
            "The footprint/placement model is well evidenced, but the architectural massing in the source photo has a tall main block and a lower entrance wing; the exported model has one continuous wall height and one simplified roof system.",
            "The GIS floor/extrusion fields and visible story count do not establish a reliable measured height. Keep the height explicitly estimated until a dimensioned elevation or other authoritative vertical source is found.",
            "The facade reference is one oblique image. Entrance orientation and facade rhythms on other sides remain unverified.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PUSH_INDEPENDENT_GRADE=" + json.dumps(result))
    return result


if __name__ == "__main__":
    evaluate()
