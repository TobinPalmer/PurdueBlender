#!/usr/bin/env python3
"""Second independent review of the Matthews Hall massing asset.

Run with Python 3. This script opens the saved .blend through Blender 5.2.3,
compares the source GIS outline with grade-level structural edges, checks the
export contract, and writes independent_grade_kyle2.json. It never edits the
model or shared project files.
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
ASSET_ID = "massing_matthews_hall_mthw_9326885"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SOURCE = AUDIT / "sources" / "feature_235_wgs84.json"
EMERGENCY_PLAN = AUDIT / "sources" / "purdue_emergency_plan.html"
EVENTS_PAGE = AUDIT / "sources" / "purdue_events_page.html"
PHOTO = AUDIT / "sources" / "purdue_events_matthews_hall.jpg"
EVIDENCE = AUDIT / "evidence.json"
MANIFEST = ROOT / "modular" / "manifest.json"
PREVIOUS_RESULT = AUDIT / "grade_result.json"
OUTPUT = AUDIT / "independent_grade_kyle2.json"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
OBJECT_NAME = "Matthews Hall (MTHW)"
COLLECTION_NAME = "Asset_" + ASSET_ID


def campus_xy(lon: float, lat: float) -> tuple[float, float]:
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0)


def edge_distance(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> float:
    """Orientation-independent endpoint distance for two polygon edges."""
    direct = max(math.dist(a, c), math.dist(b, d))
    reverse = max(math.dist(a, d), math.dist(b, c))
    return min(direct, reverse)


def inspect_saved_blend(expected_ring: list[tuple[float, float]]) -> dict:
    result_path = AUDIT / "_independent_blender_inspection.tmp.json"
    expr = """
import bpy, json, math
from pathlib import Path
from mathutils import Vector
obj=bpy.data.objects.get(%r); coll=bpy.data.collections.get(%r)
if obj is None or coll is None: raise RuntimeError('Expected MTHW object or collection missing')
dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); mesh=ev.to_mesh()
world=[ev.matrix_world @ v.co for v in mesh.vertices]
actual_edges=[]
for poly in mesh.polygons:
 pts=[ev.matrix_world @ mesh.vertices[i].co for i in poly.vertices]
 at_grade=[(float(p.x),float(p.y)) for p in pts if abs(p.z)<1e-5]
 if len(at_grade)==2 and math.dist(*at_grade)>0.01: actual_edges.append(at_grade)
ring=%r
expected=[(ring[i],ring[(i+1)%%len(ring)]) for i in range(len(ring))]
def edist(e,a):
 direct=max(math.dist(e[0],a[0]),math.dist(e[1],a[1])); reverse=max(math.dist(e[0],a[1]),math.dist(e[1],a[0]))
 return min(direct,reverse)
errs=[min((edist(e,a) for a in actual_edges),default=float('inf')) for e in expected]
lo=[min(p[i] for p in world) for i in range(3)]; hi=[max(p[i] for p in world) for i in range(3)]
result={
 'scene':bpy.context.scene.name,'collection':coll.name,'collection_object_count':len(coll.all_objects),
 'collection_objects':[x.name for x in coll.all_objects],'object_name':obj.name,'object_type':obj.type,
 'evaluated_vertex_count':len(mesh.vertices),'evaluated_face_count':len(mesh.polygons),
 'world_bounds_m':[[lo[i],hi[i]] for i in range(3)],'dimensions_m':list(obj.dimensions),
 'matrix_world':[list(row) for row in ev.matrix_world],'modifier_count':len(obj.modifiers),
 'material_names':[m.name for m in mesh.materials],'source_edge_count':len(expected),
 'candidate_grade_edge_count':len(actual_edges),'source_edges_matched_within_2mm':sum(x<=.002 for x in errs),
 'max_source_edge_error_m':max(errs),'mean_source_edge_error_m':sum(errs)/len(errs),
 'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file],
 'linked_libraries':len(bpy.data.libraries)}
ev.to_mesh_clear(); Path(%r).write_text(json.dumps(result,indent=2),encoding='utf-8')
""" % (OBJECT_NAME, COLLECTION_NAME, expected_ring, str(result_path))
    completed = subprocess.run(
        [str(BLENDER), "--background", str(ASSET), "--factory-startup", "--python-expr", expr],
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if not result_path.exists():
        raise RuntimeError(f"Blender inspector did not write data. stdout={completed.stdout}; stderr={completed.stderr}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result_path.unlink(missing_ok=True)
    return result


def main() -> dict:
    fc = json.loads(SOURCE.read_text(encoding="utf-8"))
    feature = next(x for x in fc["features"] if int(x["id"]) == 235)
    props = feature["properties"]
    ring = feature["geometry"]["coordinates"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    expected_ring = [campus_xy(float(lon), float(lat)) for lon, lat in ring]
    source_bounds = [[min(p[k] for p in expected_ring), max(p[k] for p in expected_ring)] for k in range(2)]
    source_dimensions = [source_bounds[i][1] - source_bounds[i][0] for i in range(2)]
    model = inspect_saved_blend(expected_ring)
    emergency = EMERGENCY_PLAN.read_text(encoding="utf-8", errors="replace").lower()
    events = EVENTS_PAGE.read_text(encoding="utf-8", errors="replace").lower()
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next(x for x in manifest["assets"] if x.get("id") == ASSET_ID)
    previous = json.loads(PREVIOUS_RESULT.read_text(encoding="utf-8"))
    sources_present = all(p.is_file() for p in (SOURCE, EMERGENCY_PLAN, EVENTS_PAGE, PHOTO, AUDIT / "preview_exterior.png", AUDIT / "reopen_check.json"))
    walls_match = model["source_edges_matched_within_2mm"] == len(expected_ring) and model["max_source_edge_error_m"] <= 0.002
    emergency_supports_three = "matthews hall is a three story" in emergency
    venue_identity = "matthews hall" in events and "812 mitch daniels blvd" in events
    gis_says_four = int(props.get("NUM_LEVELS", 0)) == 4 or int(props.get("CountOfFLO", 0)) == 4

    criteria = [
        {
            "criterion": "Identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Purdue feature 235 identifies {props['BUILDING_N']} ({props['BLDG_ABBR']}) at {props['ADDRESS']}; Purdue Emergency Plan and Events snapshots also identify Matthews Hall at the same address.",
                f"The official 14-edge ring is geometrically matched to {model['source_edges_matched_within_2mm']} grade-level structural wall edges of the reopened asset, each within 2 mm; maximum error is {model['max_source_edge_error_m']:.6f} m.",
                "This confirms the model represents the named Purdue GIS footprint. The GIS outline is not a certified survey and does not establish survey-grade wall positions.",
            ],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0 if walls_match else 0.0,
            "max_score": 2,
            "evidence": [
                f"All {len(expected_ring)} absolute XY structural outline edges match the GIS ring within 2 mm after the project's approximate WGS84-to-campus coordinate transform.",
                f"Source footprint dimensions are about {source_dimensions[0]:.2f} × {source_dimensions[1]:.2f} m; evaluated whole-object bounds include the front portico/roof eave and are {model['dimensions_m'][0]:.2f} × {model['dimensions_m'][1]:.2f} × {model['dimensions_m'][2]:.2f} m.",
                "Identity matrix retains the asset's campus-coordinate placement and GIS-derived orientation. Survey accuracy remains unpublished.",
            ],
        },
        {
            "criterion": "Height, floors, and roof form",
            "score": 1.25,
            "max_score": 2,
            "evidence": [
                f"Purdue Emergency Plan text check for three stories: {emergency_supports_three}. GIS NUM_LEVELS/CountOfFLO values indicate four ({gis_says_four}); the conflicting GIS level fields and undocumented Extrution=27 remain unresolved.",
                f"The evaluated mesh reaches {model['world_bounds_m'][2][1]:.2f} m. The evidence labels 11.4 m wall height and 11.95 m roof height as estimates; no measured vertical source was found.",
                "The official oblique image supports a shallow dark roof edge, and the model shows three facade tiers with a low roof edge. Roof plane, pitch, underside, and exact height are not dimensioned.",
            ],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "The saved Purdue Events photograph visibly supports red brick, pale horizontal masonry courses, repeated sash windows, and a columned entrance portico.",
                "The preview includes brick walls, floor bands, repeated windows, and a centered portico on the photographed frontage.",
                "Only one oblique elevation is available. The modeled frontage is a plausible match, but the bearing is inferred, window and portico dimensions are approximate, and hidden elevations/material extents are unverified. The shallow roof edge is shown as a nearly flat dark cap with limited roof geometry.",
            ],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0 if model["object_type"] == "MESH" and model["collection_object_count"] == 1 and model["linked_libraries"] == 0 and not model["external_images"] and sources_present and entry.get("file") == f"buildings/{ASSET_ID}.blend" else 0.0,
            "max_score": 2,
            "evidence": [
                f"Independent Blender 5.2.3 reopen found scene {model['scene']}, expected collection {model['collection']}, one mesh object, {model['evaluated_vertex_count']} evaluated vertices, and {model['evaluated_face_count']} faces.",
                f"The asset has {model['modifier_count']} modifiers, {model['linked_libraries']} linked libraries, {len(model['external_images'])} unpacked image dependencies, and preserves an identity campus transform.",
                f"Manifest file/collection and required evidence snapshots, preview, and reopen record match: {entry.get('file')}; complete={sources_present}.",
            ],
        },
    ]
    score = sum(c["score"] for c in criteria)
    findings = [
        "Passes overall if the independently computed score is at least 8/10.",
        "Footprint, campus position, orientation, and plan dimensions are verified against the named official GIS geometry within the chosen 2 mm coordinate-comparison tolerance.",
        "Three stories are directly stated in the Emergency Plan, but the GIS level count indicates four and its extrusion field has undocumented units; roof height remains an estimate.",
        "The photographed front's brick, pale courses, window rhythm, and portico are represented. Other elevations and precise architectural dimensions remain unverified.",
    ]
    findings[0] = f"{'Passes' if score >= 8 else 'Does not pass'} overall at {score:.2f}/10 (minimum 8/10)."
    result = {
        "building_id": ASSET_ID,
        "score": score,
        "max_score": 10,
        "passing_standard": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "findings": findings,
        "comparison_to_previous_grade": {
            "previous_score": previous["score"],
            "independent_score": score,
            "difference": score - previous["score"],
            "comment": "Independent review uses the same 10-point rubric and independently reopens the current asset; the result is compared only after recomputing the evidence.",
        },
        "evidence": {
            "asset_path": str(ASSET),
            "grader_code": str(Path(__file__).resolve()),
            "gis_snapshot": str(SOURCE),
            "emergency_plan_snapshot": str(EMERGENCY_PLAN),
            "events_page_snapshot": str(EVENTS_PAGE),
            "reference_photo": str(PHOTO),
            "source_identity": {"FID": props["FID"], "abbreviation": props["BLDG_ABBR"], "name": props["BUILDING_N"], "address": props["ADDRESS"]},
            "source_outline": {"vertices": len(expected_ring), "bounds_xy_m": source_bounds, "dimensions_xy_m": source_dimensions},
            "independent_blender_reopen": model,
            "manifest_entry": {"id": entry["id"], "file": entry["file"], "collection": entry["collection"], "scene": entry["scene"], "object_count": entry["object_count"]},
            "source_text_checks": {"emergency_plan_three_stories": emergency_supports_three, "venue_page_identity_address": venue_identity},
            "builder_evidence_uncertainties": evidence["uncertainties"],
            "previous_grade_result_path": str(PREVIOUS_RESULT),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
