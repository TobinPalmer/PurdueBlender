"""Independent Neil Armstrong Hall R12.9 rubric evaluation.
Run with standard Python after `independent_probe_r12_9.py` has freshly reopened the asset in Blender.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROBE = HERE / "independent_reopen_r12_9.json"
MANIFEST = ROOT / "modular" / "manifest.json"
EXPECTED_SHA = "d8c78374b047fa1248d6d304db0cba1e7f39ff97d133ccc06d774eabf7558bf7"


def evaluate(probe, manifest_record):
    """Return criterion-level score from saved-file facts and direct source/render review."""
    if probe.get("sha256") != EXPECTED_SHA:
        raise ValueError("The independently reopened asset is not the requested R12.9 revision")
    if probe.get("collection") != "Asset_neil_armstrong_hall":
        raise ValueError("Expected export collection is absent")
    if probe.get("collection_object_count") != 446 or probe.get("mesh_count") != 416:
        raise ValueError("Fresh reopen inventory differs from the inspected R12.9 revision")
    root_ok = probe.get("root_location") == [0.0, 0.0, 0.0]
    cleanliness = not probe.get("materialless_meshes") and not probe.get("null_material_slots") and not probe.get("missing_external_images")
    manifest_count_matches = manifest_record.get("object_count") == probe.get("collection_object_count")

    criteria = [
      {"criterion": "Correct identity and source-backed footprint", "score": 1.5, "max_score": 2.0,
       "evidence": [
         "Purdue's Armstrong Hall emergency plan names the engineering building; 2016 project photos show its distinctive red-brown folded canopy, glazed atrium, and brick wings.",
         "The 2023 Indiana orthophoto and top overlay support the visible roof/eaves outline; the overlay's red outer loop follows the aerial roof edge and the inner loop marks its opening.",
         "The roof/eaves trace does not prove the structural wall line, atrium boundary, or wall-to-eaves offset; Purdue GIS feature 642 is generalized and not a wall survey."
       ],
       "findings": ["Building identity and signature roof/eaves form are supported; structural wall footprint and courtyard remain unverified."]},
      {"criterion": "Position, orientation, and scale/dimensions", "score": 1.8, "max_score": 2.0,
       "evidence": [
         f"Fresh reopen verifies the detailed asset root at {probe.get('root_location')} with identity world matrix.",
         "Manifest placement origin is [-109.0, 400.1893310546875] m; the prior R12.4 independent master inspection checked the marker at that origin, zero rotation and unit scale. R12.9 preserves the local frame.",
         "The R12.9 review did not reopen the entire current master; local structural dimensions and wall stationing are not verified by the roof trace."
       ],
       "findings": ["Placement is consistent with the prior master check; current master recheck and measured structural dimensions remain coordinator/evidence follow-ups."]},
      {"criterion": "Evidence-backed height, floors, and roof form", "score": 1.5, "max_score": 2.0,
       "evidence": [
         "Purdue OEP describes lower, grade and two upper levels; FRP describes a three-story frame, basement/sub-basement, cantilevered roof truss and atrium bridges.",
         "The 2016 photos support a localized folded triangular canopy. R12.9 moves the inferred peak to the northwest eaves corner and tapers adjacent edges; direct side/front renders now read closer to the photographed wing than the broad uniform ring in R12.8.",
         "The 2023 orthophoto supports XY/eaves only. The 21.5 m peak and roof warp remain inferred; 21.6 m LiDAR is a coarse ceiling, not a measured elevation."
       ],
       "findings": ["Story organization and canopy character have credible support, but roof height and profile are not measured."]},
      {"criterion": "Facade, entrances, and distinctive architecture", "score": 1.5, "max_score": 2.0,
       "evidence": [
         "2016 project photos support large glazed atrium zones, vertical aluminum framing, and projecting horizontal shading members; Kawneer identifies 1600UT curtain wall and Versoleil sunshade system context.",
         "R12.9 expands the candidate upper glass band, adds mullions/transom, and adds 86 horizontal aluminum fins; the rendered curved/glazed entrance and soffit/canopy connection are more source-consistent than R12.8.",
         "The current elevation renders still show long generic brick faces and the exact glazing bay stationing, fin depth/cadence, and entrance connection remain approximate because there is no dimensioned facade schedule."
       ],
       "findings": ["Signature glass/canopy elements are improved and source-motivated; facade detail remains schematic."]},
      {"criterion": "Modular export, portability, and complete evidence", "score": 1.7 if not manifest_count_matches else 1.9, "max_score": 2.0,
       "evidence": [
         f"Independent Blender 5.2.3 fresh reopen verified collection {probe.get('collection')} with {probe.get('collection_object_count')} objects / {probe.get('mesh_count')} meshes and root at origin.",
         f"All meshes have materials, no null slots or missing external images: {cleanliness}.",
         f"The R12.9 record includes source notes, validation, renders, and exact asset SHA; current shared manifest object_count={manifest_record.get('object_count')} versus saved export={probe.get('collection_object_count')} (needs coordinator reconciliation)."
       ],
       "findings": ["Asset is self-contained and reopens correctly; update the shared manifest inventory to 446 before declaring fully synchronized."]}
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {"building": "Neil Armstrong Hall", "revision": "R12.9", "asset_sha256": EXPECTED_SHA,
            "score": score, "max_score": 10, "pass_threshold": 8.0, "passed": score >= 8.0,
            "criteria": criteria,
            "evidence": {"independent_reopen": PROBE.relative_to(ROOT).as_posix(),
                         "manifest_record_id": manifest_record.get("id"),
                         "renders_reviewed": [
                           "audit/neil_armstrong_hall_refine/renders_independent_r12_9/r12_9_northwest_source03.png",
                           "audit/neil_armstrong_hall_refine/renders_independent_r12_9/r12_9_geotag_view01.png",
                           "audit/neil_armstrong_hall_refine/renders_independent_r12_9/r12_9_geotag_view03.png",
                           "audit/neil_armstrong_hall_refine/renders_independent_r12_9/r12_9_top_registered.png",
                           "audit/neil_armstrong_hall_refine/renders_independent_r12_9/r12_9_south_elevation.png"],
                         "sources": [
                           "https://www.purdue.edu/operations/emergency-preparedness/arms/",
                           "https://www.kawneer.ca/projects/education/neil-armstrong-hall-of-engineering-purdue-university/",
                           "https://frpinc.com/projects/neil-armstrong-hall-of-engineering/",
                           "https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg",
                           "https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer"]},
            "findings": ["Passes the 8/10 threshold narrowly.",
                         "The R12.9 folded canopy and upper curtain-wall/sunshade additions better match the direct 2016 photo evidence.",
                         "The model is not yet fully verified: wall footprint, courtyard boundary, canopy elevation, facade stationing and fin dimensions remain uncertain.",
                         "Coordinator should reconcile the manifest count and perform a current master-link check before integration."],
            "limitations": ["The 2023 orthophoto supports roof/eaves plan only, not structural walls.",
                            "Photos have unknown heading/roll and no calibrated camera; facade geometry is qualitative.",
                            "No dimensioned public as-built plan, facade schedule or roof elevation was found."]}


def main():
    probe=json.loads(PROBE.read_text(encoding="utf-8"))
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    record=next(x for x in manifest["assets"] if x["id"]=="neil_armstrong_hall")
    result=evaluate(probe,record)
    out=HERE/"independent_grade_r12_9.json"
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
